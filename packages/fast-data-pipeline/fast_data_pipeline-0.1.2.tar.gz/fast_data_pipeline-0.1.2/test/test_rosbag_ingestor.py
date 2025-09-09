"""
Unit tests for the RosbagIngester._get_all_fields method.
"""

import pytest
from unittest.mock import MagicMock, PropertyMock

# Assuming the RosbagIngester class is in a file named 'rosbag_ingestor.py'
# Adjust the import path as necessary for your project structure.
from data_pipeline.ingestion.rosbag_ingestor import RosbagIngester


@pytest.fixture
def ingester_instance(tmpdir):
    """
    Provides a RosbagIngester instance with a mocked typestore
    for isolated testing of the _get_all_fields method.
    """
    # Create a mock state manager and dummy folders/files
    mock_state_manager = MagicMock()
    input_dir = tmpdir.mkdir("input")
    output_dir = tmpdir.mkdir("output")
    layout_yaml = tmpdir.join("layout.yaml")
    layout_yaml.write('mapping: []')

    # Instantiate the ingester
    ingester = RosbagIngester(
        input_folder=str(input_dir),
        output_folder=str(output_dir),
        state_manager=mock_state_manager,
        layout_yaml_path=str(layout_yaml),
    )

    # --- Central Part: Mock the typestore ---
    mock_typestore = MagicMock()

    # Define the structures of our fake ROS messages
    # The format (node_type, details) mimics the rosbags internal representation.
    # Node Type 2 = Basic Type
    # Node Type 4 = Fixed-size array: ((element_type_tuple), size)
    fake_msg_defs = {
        # 1. A simple, primitive message
        "test_msgs/msg/Point": {
            "fields": [
                ("x", (2, "float64")),
                ("y", (2, "float64")),
                ("z", (2, "float64")),
            ]
        },
        # 2. A message that nests the Point message
        "test_msgs/msg/Pose": {
            "fields": [
                ("position", (2, "test_msgs/msg/Point")),
                ("orientation", (2, "test_msgs/msg/Quaternion")), # Assume Quaternion is primitive for this test
            ]
        },
        "test_msgs/msg/Quaternion": {
            "fields": [("w", (2, "float64"))]
        },
        # 3. A message with an array field
        "test_msgs/msg/PoseWithCovariance": {
             "fields": [
                ("pose", (2, "test_msgs/msg/Pose")),
                # FIX: Corrected the array definition by removing one layer of incorrect tuple wrapping.
                # This resolves the ValueError: not enough values to unpack.
                ("covariance", (4, ((2, "float64"), 36))), # Array of 36 float64s
            ]
        },
        # 4. A message containing a "complex" type that should not be recursed into
        "test_msgs/msg/SensorFrame": {
            "fields": [
                ("header", (2, "std_msgs/msg/Header")),
                ("image", (2, "sensor_msgs/msg/Image")), # This is a registered complex type
            ]
        },
        "std_msgs/msg/Header": {
            "fields": [("stamp", (2, "builtin_interfaces/msg/Time"))]
        },
        "builtin_interfaces/msg/Time": {
            "fields": [("sec", (2, "int32"))]
        },
        # 5. Messages with a circular dependency to test loop prevention
        "test_msgs/msg/NodeA": {
            "fields": [
                ("id", (2, "int32")),
                ("child", (2, "test_msgs/msg/NodeB")),
            ]
        },
        "test_msgs/msg/NodeB": {
             "fields": [
                ("id", (2, "int32")),
                ("parent", (2, "test_msgs/msg/NodeA")), # Points back to NodeA
            ]
        }
    }

    # Configure the mock to return the correct definition
    def get_msgdef_side_effect(typename):
        # Create a mock object that has a .fields attribute
        mock_def = MagicMock()
        definition = fake_msg_defs.get(typename)
        if definition:
            # Use PropertyMock to attach .fields as a property
            type(mock_def).fields = PropertyMock(return_value=definition["fields"])
            return mock_def
        raise KeyError(f"Typename '{typename}' not found in mock definitions.")

    mock_typestore.get_msgdef.side_effect = get_msgdef_side_effect
    ingester.typestore = mock_typestore

    # Ensure the complex parsers are set as they would be in production
    ingester.complex_msg_parsers = {
        "sensor_msgs/msg/Image": MagicMock(),
        "sensor_msgs/msg/PointCloud2": MagicMock(),
    }

    return ingester


def test_get_all_fields_primitive_message(ingester_instance):
    """
    Tests that a simple message with only primitive types is parsed correctly.
    """
    fields = ingester_instance._get_all_fields("test_msgs/msg/Point")
    expected = [
        ("x", ["x"], "float64", False),
        ("y", ["y"], "float64", False),
        ("z", ["z"], "float64", False),
    ]
    assert fields == expected


def test_get_all_fields_nested_message(ingester_instance):
    """
    Tests that nested messages are flattened with correct prefixes.
    """
    fields = ingester_instance._get_all_fields("test_msgs/msg/Pose")
    expected = [
        ("position_x", ["position", "x"], "float64", False),
        ("position_y", ["position", "y"], "float64", False),
        ("position_z", ["position", "z"], "float64", False),
        ("orientation_w", ["orientation", "w"], "float64", False),
    ]
    # Sort for comparison to ignore order differences
    assert sorted(fields) == sorted(expected)


def test_get_all_fields_stops_at_array(ingester_instance):
    """
    Tests that the recursion stops when it encounters an array,
    treating the array as a single field.
    """
    fields = ingester_instance._get_all_fields("test_msgs/msg/PoseWithCovariance")

    # Check that the nested fields are present
    assert ("pose_position_x", ["pose", "position", "x"], "float64", False) in fields

    # Check that the array field is present as a single item
    assert ("covariance", ["covariance"], "float64", True) in fields

    # Ensure it didn't try to expand the array
    assert len(fields) == 5 # 4 from Pose + 1 for covariance array


def test_get_all_fields_stops_at_complex_message(ingester_instance):
    """
    Tests that recursion stops when a field's type is in `complex_msg_parsers`.
    """
    fields = ingester_instance._get_all_fields("test_msgs/msg/SensorFrame")

    # It should recurse into the header, as it's not complex
    assert ("header_stamp_sec", ["header", "stamp", "sec"], "int32", False) in fields

    # It should NOT recurse into Image, but list it as a single field
    assert ("image", ["image"], "sensor_msgs/msg/Image", False) in fields

    # Check that no fields like 'image_data' or 'image_height' were generated
    image_subfields = [f for f in fields if f[0].startswith("image_")]
    assert not image_subfields

    assert len(fields) == 2


def test_get_all_fields_handles_circular_dependency(ingester_instance):
    """
    Tests that the `visited` set correctly prevents an infinite recursion loop.
    This test will FAIL until the bug in the source code is fixed.
    """
    fields = ingester_instance._get_all_fields("test_msgs/msg/NodeA")

    # This is the CORRECT expected output. The function should not add
    # 'child_parent' when it detects the circular reference.
    expected = [
        ("id", ["id"], "int32", False),
        ("child_id", ["child", "id"], "int32", False),
    ]

    # The recursion should stop when it sees NodeA for the second time.
    # NodeA -> child (NodeB) -> parent (NodeA) <- STOP
    assert sorted(fields) == sorted(expected)

