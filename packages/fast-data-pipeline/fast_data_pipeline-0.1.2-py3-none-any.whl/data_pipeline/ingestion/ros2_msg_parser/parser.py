import importlib
import logging
from typing import Any, Dict, Optional, TypeVar

import numpy as np

# To use this we need to convert to the native msg type, which takes too long
# from ros2_utils.msg_conversions.sensor_msgs.image import image_to_numpy

from .rosbags_image import image_to_numpy_rosbags
from .rosbags_pointcloud import read_points_rosbags

logger = logging.getLogger(__name__)

T = TypeVar('T')

NATIVE_CLASSES: dict[str, type] = {}

def to_native(msg: object) -> object:
    """Convert rosbags message to native message.
    Is extremely inefficient

    Args:
        msg: Rosbags message.

    Returns:
        Native message.

    """
    # Check if the object has __msgtype__ attribute (i.e., it's a ROS message)
    if not hasattr(msg, '__msgtype__'):
        # If it's not a message object, return it as-is
        return msg
        
    msgtype: str = msg.__msgtype__  
    if msgtype not in NATIVE_CLASSES:
        pkg, name = msgtype.rsplit('/', 1)
        NATIVE_CLASSES[msgtype] = getattr(importlib.import_module(pkg.replace('/', '.')), name)

    fields = {}
    for name, field in msg.__dataclass_fields__.items():  
        if 'ClassVar' in field.type:
            continue
        value = getattr(msg, name)
        
        # Handle nested message objects
        if hasattr(value, '__msgtype__'):
            value = to_native(value)
        elif isinstance(value, list):
            # Process each element in the list
            converted_list = []
            for x in value:
                if hasattr(x, '__msgtype__'):
                    # It's a message object, convert it
                    converted_list.append(to_native(x))
                else:
                    # It's a primitive type, keep it as-is
                    converted_list.append(x)
            value = converted_list
        elif isinstance(value, np.ndarray):
            value = value.tolist()
        
        fields[name] = value

    return NATIVE_CLASSES[msgtype](**fields)

class ROS2MessageParser:
    """A library for converting specific ROS2 messages to other formats."""

    def __init__(self):
        # The dispatch map defines which ROS types this parser can handle.
        self.parsing_map = {
            "sensor_msgs/msg/Image": self._parse_sensor_msgs_image,
            "sensor_msgs/msg/PointCloud2": self._parse_sensor_msgs_pointcloud2,
        }

    def can_parse_type(self, typename: str) -> bool:
        """Checks if a given type name has a registered parser."""
        return typename in self.parsing_map

    def parse(self, msg: Any, msg_type_str: str) -> Optional[Dict[str, Any]]:
        """
        Parses a message by looking up its type in the dispatch dictionary.
        """
        parser_func = self.parsing_map.get(msg_type_str)
        if parser_func:
            # Pass the message and its type string to the appropriate parser function
            return parser_func(msg, msg_type_str)
        return None


    def _parse_sensor_msgs_image(self, msg: Any, type_str: str) -> Dict[str, Any]:
        """Parses a sensor_msgs/msg/Image into a dictionary using direct rosbags parsing."""
        return {
            "data": image_to_numpy_rosbags(msg),
            "timestamp": {
                "timestamp_s": msg.header.stamp.sec,
                "timestamp_ns": msg.header.stamp.nanosec,
            },
            "metadata": {
                "encoding": msg.encoding,
                "frame_id": msg.header.frame_id,
            },
        }

    def _parse_sensor_msgs_pointcloud2(self, msg: Any, type_str: str) -> Dict[str, Any]:
        """
        Parse PointCloud2 message using direct rosbags parsing
        """
        points_generator = read_points_rosbags(msg, skip_nans=True)
        
        points_list = list(points_generator)
        
        if points_list:
            first_point = points_list[0]
            dtype = [(f'field_{i}', np.float32) for i in range(len(first_point))]
            
            structured_array = np.array(points_list, dtype=dtype)
        else:
            structured_array = np.array([], dtype=[('field_0', np.float32)])
        
        return {
            "data": structured_array, 
            "timestamp": {
                "timestamp_s": msg.header.stamp.sec,
                "timestamp_ns": msg.header.stamp.nanosec,
            },
            "metadata": {
                "is_dense": msg.is_dense,
                "frame_id": msg.header.frame_id,
            },
        }
