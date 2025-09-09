import gc
import keyword
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import tables
import joblib
from joblib import Parallel, delayed
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg, store
from tqdm import tqdm

from .base_ingestor import BaseIngester
from .ros2_msg_parser.parser import ROS2MessageParser

logger = logging.getLogger(__name__)


def _initialize_typestore_worker(ros_distro: str, custom_msg_folders: List[str]) -> store.Typestore:
    """Initialize a rosbags typestore in a worker process.

    This helper function creates a typestore for a given ROS distribution and
    registers any custom message definitions found in the specified folders.

    :param ros_distro: The ROS distribution name (e.g., 'humble').
    :param custom_msg_folders: A list of paths to directories containing custom message definitions.
    :return: An initialized and configured rosbags Typestore instance.
    """
    typestore = get_typestore(
        getattr(Stores, f"ROS2_{ros_distro.upper()}", Stores.ROS2_HUMBLE)
    )
    if not custom_msg_folders:
        return typestore
    for folder in custom_msg_folders:
        for path in Path(folder).rglob("*.msg"):
            if path.parent.name == "msg":
                try:
                    typestore.register(
                        get_types_from_msg(
                            path.read_text(), f"{path.parent.parent.name}/msg/{path.stem}"
                        )
                    )
                except Exception as e:
                    logger.error(f"Worker failed to register message {path}: {e}")
    return typestore


def _process_time_chunk(
    folder_path: str,
    ros_distro: str,
    custom_msg_folders: List[str],
    topic_map: Dict[str, str],
    field_definitions: Dict[str, Dict],
    time_slice: tuple[int, int],
) -> Dict[str, Dict[str, list]]:
    """Process a time-based chunk of a rosbag in a worker process.

    This function reads all messages within a specific time interval from a
    rosbag, extracts data for simple (non-complex) fields, and returns the
    data in local buffers. It is designed to be executed in parallel.

    :param folder_path: Path to the rosbag directory.
    :param ros_distro: The ROS distribution name.
    :param custom_msg_folders: List of paths to custom message definitions.
    :param topic_map: Mapping from ROS topic to HDF5 group path.
    :param field_definitions: A dictionary describing the fields for each topic,
                              used to structure the output buffers.
    :param time_slice: A tuple (start_ns, end_ns) defining the time range to process.
    :return: A dictionary of populated data buffers, keyed by HDF5 topic path.
    """
    # 1. Initialize resources within the worker
    typestore = _initialize_typestore_worker(ros_distro, custom_msg_folders)
    local_buffers = {}

    # 2. Initialize local buffers based on field definitions
    for topic_path, fields in field_definitions.items():
        local_buffers[topic_path] = {"timestamp_s": []}
        for field_info in fields.values():
            if not field_info["is_complex"]:
                for flat_name, _, _, _ in field_info["flat_fields"]:
                    local_buffers[topic_path][flat_name] = []

    # 3. Open the bag and process the assigned time slice
    with AnyReader([Path(folder_path)], default_typestore=typestore) as reader:
        connections = [c for c in reader.connections if c.topic in topic_map]
        start_ns, end_ns = time_slice

        for conn, ts, raw in reader.messages(
            connections=connections, start=start_ns, stop=end_ns
        ):
            topic_path = topic_map[conn.topic]
            msg = reader.deserialize(raw, conn.msgtype)

            # Append data to the appropriate local buffer
            local_buffers[topic_path]["timestamp_s"].append(ts / 1e9)
            topic_fields = field_definitions[topic_path]

            for field_name, field_info in topic_fields.items():
                if field_info["is_complex"]:
                    # Complex data is handled differently and written serially later
                    pass
                else:
                    for flat_name, path, _, _ in field_info["flat_fields"]:
                        value = _get_value_recursive_worker(msg, path)
                        local_buffers[topic_path][flat_name].append(value)

    return local_buffers


def _get_value_recursive_worker(obj: Any, parts: List[str]) -> Any:
    """Retrieve a nested attribute from an object.

    This standalone helper function safely traverses a nested object structure
    based on a list of attribute names. It also handles the special case of
    ROS time objects, converting them to a float timestamp.

    :param obj: The root object to start traversal from.
    :param parts: A list of attribute names representing the path to the desired value.
    :return: The retrieved value, or None if any attribute in the path does not exist.
    """
    val = obj
    for part in parts:
        try:
            val = getattr(val, part)
        except AttributeError:
            return None
    if hasattr(val, "sec") and hasattr(val, "nanosec"):
        return val.sec + val.nanosec * 1e-9
    return val


class RosbagIngester(BaseIngester):
    """Ingests ROS 2 bag files into HDF5 using a hybrid parallel/serial approach."""

    def __init__(
        self,
        input_folder: str,
        output_folder: str,
        state_manager: Any,
        layout_yaml_path: str,
        ros_distro: str = "humble",
        custom_msg_folders: List[str] = None,
        chunk_size: int = 1000,
        n_jobs_messages: int = -1,
    ):
        """Initialize the RosbagIngester.

        :param input_folder: The directory containing rosbag folders to process.
        :param output_folder: The directory where HDF5 files will be saved.
        :param state_manager: An object to manage processing state (e.g., tracking completed files).
        :param layout_yaml_path: Path to the YAML file that defines the HDF5 layout and topic mapping.
        :param ros_distro: The ROS distribution of the bags (e.g., 'humble', 'galactic').
        :param custom_msg_folders: A list of paths to folders with custom .msg definitions.
        :param chunk_size: The chunk size for writing data to HDF5 tables (deprecated).
        :param n_jobs_messages: The number of parallel jobs to use for processing messages within a single bag.
                               -1 means using all available cores.
        """
        super().__init__(input_folder, output_folder, state_manager, layout_yaml_path)
        self.ros_distro = ros_distro
        self.custom_msg_folders = custom_msg_folders or []
        self.chunk_size = chunk_size  # For HDF5 writing
        self.n_jobs_messages = n_jobs_messages if n_jobs_messages != 0 else -1
        self.typestore = self._initialize_typestore()
        self.topic_map = self._create_topic_map_from_layout()
        self.parser = ROS2MessageParser()

    def __getstate__(self) -> dict:
        """Prepare the object's state for pickling.

        Removes unpickleable attributes like the 'typestore' and 'parser'
        so the object can be sent to worker processes.

        :return: A dictionary of the object's pickleable state.
        """
        state = self.__dict__.copy()
        # Remove the unpickleable attributes.
        del state['typestore']
        del state['parser']
        return state

    def __setstate__(self, state: dict):
        """Restore the object's state after unpickling.

        Restores the state and re-initializes the unpickleable attributes
        that were removed by __getstate__. This is called in the new process.

        :param state: The dictionary of the object's state.
        """
        self.__dict__.update(state)
        # Re-initialize the unpickleable attributes in the new process.
        self.typestore = self._initialize_typestore()
        self.parser = ROS2MessageParser()

    def _create_topic_map_from_layout(self) -> Dict[str, str]:
        """Parse the layout YAML to create a mapping from ROS topic to HDF5 path.

        :raises ValueError: If the layout specification is missing or invalid.
        :return: A dictionary mapping the original ROS topic name to the target HDF5 group path.
        """
        if not self.layout_spec or "mapping" not in self.layout_spec:
            raise ValueError("Layout spec missing or invalid.")
        return {
            m["original_name"]: m["target_name"]
            for m in self.layout_spec["mapping"]
            if m.get("source") == "ros2bag"
        }

    def discover_files(self) -> List[str]:
        """Discover valid rosbag folders within the input directory.

        A folder is considered a valid rosbag if it contains a 'metadata.yaml' file.

        :return: A list of full paths to the discovered rosbag folders.
        """
        if not os.path.isdir(self.input_folder):
            return []
        potential = [
            os.path.join(self.input_folder, d)
            for d in os.listdir(self.input_folder)
            if os.path.isdir(os.path.join(self.input_folder, d))
        ]
        return [
            d for d in potential if os.path.isfile(os.path.join(d, "metadata.yaml"))
        ]

    def process_file(self, folder_path: str) -> Optional[str]:
        """Process a single rosbag folder and convert it to an HDF5 file.

        This method orchestrates the entire conversion process for one rosbag,
        including file handling, error management, and cleanup.

        :param folder_path: The full path to the rosbag folder.
        :return: The folder_path if processing was successful, otherwise None.
        """
        folder_name = os.path.basename(folder_path)
        safe_name = self._sanitize_hdf5_identifier(folder_name)
        output_path = os.path.join(self.output_folder, f"{safe_name}.h5")
        h5file = None
        success = False
        try:
            h5file = tables.open_file(
                output_path, mode="w", title=f"Data from {folder_name}"
            )
            self._stream_and_write_hybrid(folder_path, h5file)
            final_size = os.path.getsize(output_path) / (1024 * 1024)
            logger.info(
                f"Successfully created HDF5 file '{output_path}' with a size of {final_size:.2f} MB."
            )
            success = True
            return folder_path
        except Exception as e:
            logger.error(f"Failed to process rosbag {folder_name}: {e}", exc_info=True)
            return None
        finally:
            if h5file and h5file.isopen:
                h5file.close()
            
            # Only remove the file if the process did NOT succeed.
            if not success and os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except OSError as err:
                    logger.error(f"Error removing failed HDF5 file {output_path}: {err}")
            gc.collect()

    def _get_element_type_name(self, field_type_tuple: tuple) -> Optional[str]:
        """Extract the base type name from a rosbags field type tuple.

        The rosbags library represents types in a complex tuple format. This helper
        unpacks it to get the simple string name (e.g., 'std_msgs/msg/Header').

        :param field_type_tuple: The type tuple from a message definition.
        :return: The string name of the element type, or None if not applicable.
        """
        node_type, details = field_type_tuple
        if node_type == 1:  # (NODE_TYPE.BASE, ('<typename>', <size>))
            return details[0]
        if node_type == 2:  # (NODE_TYPE.MESSAGE, '<typename>')
            return details
        if node_type in (3, 4):  # (NODE_TYPE.SEQUENCE | ARRAY, (<element_tuple>, <size>))
            sub_node_type, sub_details = details[0]
            if sub_node_type == 1:
                return sub_details[0]
            if sub_node_type == 2:
                return sub_details
        return None

    def _stream_and_write_hybrid(self, folder_path: str, h5file: tables.File):
        """Orchestrate parallel message processing and serial HDF5 writing.

        This method implements a hybrid strategy:
        1. Serially creates the HDF5 file structure (groups and datasets).
        2. Divides the rosbag into time-based chunks.
        3. Processes simple data types in parallel across these chunks.
        4. Aggregates results and writes them serially to HDF5.
        5. Processes and writes complex data types serially in a final pass.

        :param folder_path: The path to the rosbag folder.
        :param h5file: An open PyTables File object to write to.
        """
        with AnyReader([Path(folder_path)], default_typestore=self.typestore) as reader:
            connections = [c for c in reader.connections if c.topic in self.topic_map]
            if not connections:
                logger.warning(f"No topics to process in {folder_path}. Skipping.")
                return

            # Step 1: Create the HDF5 structure and blueprints serially
            topic_blueprints = {}
            for conn in connections:
                topic_path = self.topic_map[conn.topic]
                if topic_path not in topic_blueprints:
                    topic_blueprints[topic_path] = self._create_topic_blueprint(
                        h5file, conn.msgtype, topic_path
                    )

            # Create a pickleable version of field definitions for the workers.
            worker_field_definitions = {}
            for path, bp in topic_blueprints.items():
                worker_field_definitions[path] = {}
                for field_name, field_info in bp['fields'].items():
                    # Copy all info EXCEPT the 'group' object
                    worker_field_definitions[path][field_name] = {
                        k: v for k, v in field_info.items() if k != 'group'
                    }

            # Step 2: Divide work into time-based chunks for parallel processing
            duration_ns = reader.duration
            n_jobs = joblib.cpu_count() if self.n_jobs_messages == -1 else self.n_jobs_messages
            if n_jobs > 1 and duration_ns > 0: # Only parallelize if beneficial
                chunk_duration = duration_ns // n_jobs
                time_slices = [
                    (reader.start_time + i * chunk_duration, reader.start_time + (i + 1) * chunk_duration)
                    for i in range(n_jobs)
                ]
                # Ensure the last chunk goes to the end time
                time_slices[-1] = (time_slices[-1][0], reader.end_time)
            else: # Run serially if n_jobs is 1 or duration is 0
                n_jobs = 1
                time_slices = [(reader.start_time, reader.end_time)]

            logger.info(f"Starting processing of {folder_path} with {n_jobs} worker(s).")

            # Step 3: Run workers in parallel (or serially if n_jobs=1)
            worker_results = Parallel(n_jobs=n_jobs)(
                delayed(_process_time_chunk)(
                    folder_path,
                    self.ros_distro,
                    self.custom_msg_folders,
                    self.topic_map,
                    worker_field_definitions, # Pass the clean, pickleable version
                    ts,
                )
                for ts in time_slices
            )

            logger.info("Processing finished. Aggregating and writing results.")

            # Step 4: Aggregate results and write to HDF5 serially
            for result_buffers in tqdm(worker_results, desc="-> Writing Chunks"):
                for topic_path, buffers in result_buffers.items():
                    if buffers and topic_blueprints.get(topic_path):
                        self._flush_buffers_to_hdf5(
                            topic_blueprints[topic_path]["datasets"], buffers
                        )

            # Step 5: Handle complex types serially
            logger.info("Processing and writing complex message types.")
            for conn, ts, raw in tqdm(reader.messages(connections=connections), desc="-> Complex Types"):
                topic_path = self.topic_map[conn.topic]
                blueprint = topic_blueprints[topic_path]
                for field_name, field_info in blueprint["fields"].items():
                    if field_info["is_complex"]:
                        msg = reader.deserialize(raw, conn.msgtype)
                        field_value = getattr(msg, field_name)
                        parsed_data = self.parser.parse(field_value, field_info["type"])
                        if parsed_data:
                            self._write_dict_to_hdf5(field_info["group"], parsed_data)

    def _create_topic_blueprint(
        self, h5file: tables.File, msgtype_name: str, topic_path: str
    ) -> Dict[str, Any]:
        """Create the HDF5 structure for a topic and return its blueprint.

        This function inspects a ROS message type and creates the corresponding
        HDF5 groups and datasets (EArrays for simple types, VLArrays for strings).
        It also builds and returns a dictionary ("blueprint") that describes this
        structure, which is used by other methods for writing data.

        :param h5file: The open PyTables File object.
        :param msgtype_name: The full name of the ROS message type (e.g., 'std_msgs/msg/String').
        :param topic_path: The target HDF5 group path for this topic.
        :return: A dictionary describing the created HDF5 datasets and field properties.
        """
        blueprint = {"datasets": {}, "fields": {}}
        parts = topic_path.strip("/").split("/")
        parent_group = h5file.root
        for part in parts:
            parent_group = getattr(parent_group, part, None) or h5file.create_group(
                parent_group, part
            )

        blueprint["datasets"]["timestamp_s"] = h5file.create_earray(
            parent_group, "timestamp_s", tables.Float64Atom(), (0,)
        )

        msg_def = self.typestore.get_msgdef(msgtype_name)
        for field_name, field_type_tuple in msg_def.fields:
            sane_name = self._sanitize_hdf5_identifier(field_name)
            element_type = self._get_element_type_name(field_type_tuple)
            is_complex = self.parser.can_parse_type(element_type)

            blueprint["fields"][sane_name] = {
                "is_complex": is_complex,
                "type": element_type,
            }

            if is_complex:
                blueprint["fields"][sane_name]["group"] = h5file.create_group(
                    parent_group, sane_name
                )
            else:
                flat_fields = self._get_all_fields(
                    element_type, prefix=f"{sane_name}_", path=[field_name]
                )
                blueprint["fields"][sane_name]["flat_fields"] = flat_fields
                for flat_name, _, ros_type, _ in flat_fields:
                    try:
                        if ros_type == "string":
                            atom = tables.VLStringAtom()
                            ds = h5file.create_vlarray(parent_group, flat_name, atom)
                        else:
                            atom = tables.Atom.from_dtype(np.dtype(ros_type))
                            ds = h5file.create_earray(parent_group, flat_name, atom, (0,))
                        blueprint["datasets"][flat_name] = ds
                    except (TypeError, ValueError):
                        atom = tables.VLStringAtom()
                        ds = h5file.create_vlarray(parent_group, flat_name, atom)
                        blueprint["datasets"][flat_name] = ds
        return blueprint

    def _get_all_fields(
        self,
        typename: str,
        prefix: str = "",
        path: Optional[List[str]] = None,
        visited: Optional[set] = None,
    ) -> List[tuple]:
        """Recursively flatten a nested ROS message type into a list of primitive fields.

        This function traverses a message definition, including nested messages,
        to produce a flat list of all terminal fields. This is used to create
        columns in the HDF5 table for simple message types.

        :param typename: The name of the ROS message type to start from.
        :param prefix: A string prefix to prepend to the flattened field names.
        :param path: A list of strings tracking the current attribute path from the root message.
        :param visited: A set to track visited typenames to prevent infinite recursion.
        :return: A list of tuples, where each tuple is (flat_name, path, ros_type, is_array).
        """
        if visited is None:
            visited = set()
        if path is None:
            path = []
        if typename in visited or self.parser.can_parse_type(typename):
            return []

        visited.add(typename)
        fields_list = []
        try:
            msg_def = self.typestore.get_msgdef(typename)
            for field_name, field_type_tuple in msg_def.fields:
                flat_name = f"{prefix}{field_name}"
                new_path = path + [field_name]
                element_type_name = self._get_element_type_name(field_type_tuple)
                is_array = field_type_tuple[0] in (3, 4)
                nested_fields = self._get_all_fields(
                    element_type_name, f"{flat_name}_", new_path, visited.copy()
                )
                if not nested_fields:
                    fields_list.append(
                        (flat_name, new_path, element_type_name, is_array)
                    )
                else:
                    fields_list.extend(nested_fields)
            return fields_list
        except KeyError:
            # Type is a primitive (e.g., 'uint8', 'float64')
            return [(prefix.strip("_"), path, typename, False)]

    def _get_value_recursive(self, obj: Any, parts: List[str]) -> Any:
        """Retrieve a nested attribute from an object.

        Class method wrapper for the standalone `_get_value_recursive_worker` function.

        :param obj: The root object to start traversal from.
        :param parts: A list of attribute names representing the path to the desired value.
        :return: The retrieved value.
        """
        return _get_value_recursive_worker(obj, parts)

    def _write_dict_to_hdf5(self, parent_group: tables.Group, data_dict: Dict[str, Any]):
        """Recursively write a dictionary to an HDF5 group.

        This method is used to store data from complex ROS messages (e.g., Image, PointCloud2)
        that have been parsed into a dictionary format. It creates new groups for nested
        dictionaries and appends data to existing datasets.

        :param parent_group: The PyTables Group to write into.
        :param data_dict: The dictionary containing the data to be written.
        """
        for key, value in data_dict.items():
            sane_key = self._sanitize_hdf5_identifier(key)
            h5file = parent_group._v_file

            if isinstance(value, dict):
                child_group = getattr(parent_group, sane_key, None) or h5file.create_group(parent_group, sane_key)
                self._write_dict_to_hdf5(child_group, value)
            else:
                if value is None:
                    continue
                if not hasattr(parent_group, sane_key):
                    try:
                        if isinstance(value, str):
                                atom = tables.VLStringAtom()
                                h5file.create_vlarray(parent_group, sane_key, atom, "String data")
                        else:
                            np_value = np.array(value)
                            if np_value.dtype.names: # Structured array
                                h5file.create_table(
                                    parent_group, sane_key, description=np_value.dtype
                                )
                            else: # Regular array
                                atom = tables.Atom.from_dtype(np_value.dtype)
                                shape = (0,) + np_value.shape
                                h5file.create_earray(
                                    parent_group, sane_key, atom, shape
                                )
                    except Exception as e:
                        logger.error(f"Could not create dataset '{sane_key}': {e}")
                        continue
                try:
                    dataset = getattr(parent_group, sane_key)
                    if isinstance(dataset, tables.Table):
                        dataset.append(value)
                    elif isinstance(dataset, tables.VLArray):
                        encoded_value = str(value if value is not None else "").encode("utf-8")
                        dataset.append(encoded_value)
                    else: # EArray
                        dataset.append(np.array(value)[np.newaxis, ...])
                except Exception as e:
                    logger.error(f"Failed to append data to dataset '{sane_key}': {e}")

    def _flush_buffers_to_hdf5(
        self, datasets: Dict[str, tables.Array], buffers: Dict[str, list]
    ):
        """Append data from in-memory buffers to HDF5 datasets.

        This function takes the aggregated data collected by the parallel workers
        and writes it in bulk to the corresponding PyTables EArrays and VLArrays.

        :param datasets: A dictionary mapping field names to PyTables Array objects.
        :param buffers: A dictionary mapping field names to lists of data (the buffers).
        """
        for field, data_buffer in buffers.items():
            if data_buffer and field in datasets:
                dataset = datasets[field]
                try:
                    if isinstance(dataset, tables.VLArray):
                        # VLArrays must be appended one item at a time
                        encoded_items = [
                            str(item if item is not None else "").encode("utf-8")
                            for item in data_buffer
                        ]
                        for item in encoded_items:
                            dataset.append(item)
                    else: # EArray can append a list directly
                        dataset.append(data_buffer)
                except Exception as e:
                    logger.error(f"Failed to flush buffer for field '{field}': {e}", exc_info=True)
        # No need to clear buffers as they are temporary and local to the call

    def _initialize_typestore(self) -> store.Typestore:
        """Initialize the rosbags typestore for the main process.

        This is a wrapper around the worker initialization function, using the
        instance's configuration.

        :return: An initialized rosbags Typestore instance.
        """
        return _initialize_typestore_worker(self.ros_distro, self.custom_msg_folders)

    def _sanitize_hdf5_identifier(self, name: str) -> str:
        """Clean a string to make it a valid HDF5/PyTables identifier.

        HDF5 identifiers must be valid Python identifiers. This function replaces
        invalid characters with underscores, ensures the name does not start with a
        digit, and appends an underscore if it's a Python keyword.

        :param name: The input string to sanitize.
        :return: A sanitized string suitable for use as a group or dataset name.
        """
        # Replace non-alphanumeric characters (and non-underscores) with an underscore
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # If the name starts with a digit, prepend an underscore
        if name and name[0].isdigit():
            name = '_' + name
        # If the name is a Python keyword, append an underscore
        if keyword.iskeyword(name):
            name += '_'
        return name or "unnamed"


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s",
    )

    class MockStateManager:
        """A mock state manager for demonstration purposes."""
        def get_unprocessed_items(self, items: List[str]) -> List[str]:
            return items

        def update_state(self, processed_items: List[str]):
            logger.info(f"StateManager would save state for: {processed_items}")

    # --- Configuration for the test run ---
    TEST_INPUT_DIR = "/mnt/sambashare/ugglf/2025-07-25/bags"
    TEST_OUTPUT_DIR = "/mnt/sambashare/ugglf/output/latest"
    YAML_PATH = "data-pipeline/configs/h5_layout_specification.yaml"
    CUSTOM_MESSAGES_FOLDER = ["data-pipeline/aivp-ros2-custom-messages"]
    # Set to 1 for serial processing, -1 to use all available CPU cores
    N_JOBS_FOR_FILES = 2
    N_JOBS_FOR_MESSAGES = -1
    # -----------------------------------------

    os.makedirs(TEST_INPUT_DIR, exist_ok=True)
    os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)

    if not os.path.exists(TEST_INPUT_DIR) or not os.listdir(TEST_INPUT_DIR):
        logger.warning(
            f"ACTION REQUIRED: Place a sample rosbag folder in: {os.path.abspath(TEST_INPUT_DIR)}"
        )
    else:
        ingester = RosbagIngester(
            input_folder=TEST_INPUT_DIR,
            output_folder=TEST_OUTPUT_DIR,
            custom_msg_folders=CUSTOM_MESSAGES_FOLDER,
            state_manager=MockStateManager(),
            layout_yaml_path=YAML_PATH,
            n_jobs_messages=N_JOBS_FOR_MESSAGES,
        )
        # The 'run' method in BaseIngester now controls parallelism for files
        ingester.run(n_jobs=N_JOBS_FOR_FILES)