import struct

class SensorDataNull:
    def __init__(self):
        self.sensor_type = 0
        self.sensor_version = 0

    def to_bytes(self):
        return struct.pack('>BBB', self.sensor_type, self.sensor_version, 0)

    def describe(self):
        return f"SensorNull(type={self.sensor_type}, ver={self.sensor_version})"
