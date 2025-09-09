import struct
from .base import Packet

class TelemetryPacket(Packet):
    def __init__(self, imei, timestamp, transaction_id, location_data, sensor_data):
        super().__init__('T', imei, transaction_id, 1)
        self.timestamp = int(timestamp)
        self.location_data = location_data
        # normalize sensor_data to a list
        if sensor_data is None:
            self.sensors = []
        elif isinstance(sensor_data, (list, tuple)):
            self.sensors = list(sensor_data)
        else:
            self.sensors = [sensor_data]

    def to_bytes(self):
        header = self.build_header()
        loc_bytes = self.location_data.to_bytes()
        sensor_count_val = len(self.sensors)
        sensor_count = struct.pack('>B', sensor_count_val)
        sensor_bytes = b''.join(sd.to_bytes() for sd in self.sensors)
        data = struct.pack('>I', int(self.timestamp)) + loc_bytes + sensor_count + sensor_bytes
        return header + data

    def print(self, packet_type):
        packet_bytes = self.to_bytes()
        print("v" * 50)
        print(f"  Type: {packet_type}")
        print(f"  Transaction ID: {self.transaction_id}")
        print(f"  Location: {self.location_data.describe()}")
        descs = []
        for sd in self.sensors:
            try:
                descs.append(sd.describe())
            except Exception:
                descs.append(str(sd))
        sensor_str = '[' + ', '.join(descs) + ']'
        print(f"  Sensor count: {len(self.sensors)}")
        print(f"  Sensors: {sensor_str}")
        print(f"  Packet: {packet_bytes.hex()}")
        print(f"  Packet size: {len(packet_bytes)} bytes")
        print("^" * 50)
