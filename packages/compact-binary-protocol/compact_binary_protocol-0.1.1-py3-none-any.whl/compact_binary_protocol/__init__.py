"""
compact_binary_protocol

A small, self-contained Python library that defines the compact binary protocol
used by Tartabit client components. It provides:
- Encoding helpers
- Data model classes for location and sensor data
- Packet classes for telemetry/configuration/power/motion events
- Decoding helpers for responses and header parsing

All multi-byte values are encoded using big-endian format.
"""

from .encodings import encode_var_string
from .decoders import PacketDecoder, DataReader
from .sensor_data import (
    LocationData,
    SensorDataBasic,
    SensorDataMulti,
    SensorDataNull,
    SensorDataSteps,
)
from .packets import Packet, TelemetryPacket, ConfigPacket, PowerOnPacket, MotionStartPacket, MotionStopPacket, UpdateRequestPacket, UpdateStatusPacket

__all__ = [
    'encode_var_string',
    'PacketDecoder', 'DataReader',
    'LocationData', 'SensorDataBasic', 'SensorDataMulti', 'SensorDataNull', 'SensorDataSteps',
    'Packet', 'TelemetryPacket', 'ConfigPacket', 'PowerOnPacket', 'MotionStartPacket', 'MotionStopPacket',
    'UpdateRequestPacket', 'UpdateStatusPacket',
]
