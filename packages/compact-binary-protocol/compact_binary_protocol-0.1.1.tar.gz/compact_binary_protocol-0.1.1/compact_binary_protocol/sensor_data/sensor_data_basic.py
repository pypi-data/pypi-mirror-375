import struct

class SensorDataBasic:
    def __init__(self, sensor_type, temperature, battery, rssi, sensor_version=1):
        self.sensor_type = int(sensor_type)
        self.sensor_version = int(sensor_version)
        self.temperature = float(temperature)
        self.battery = int(battery)
        self.rssi = int(rssi)

    def to_bytes(self):
        payload = struct.pack('>HBB', int(self.temperature * 10), self.battery, self.rssi)
        header = struct.pack('>BBB', self.sensor_type, self.sensor_version, len(payload))
        return header + payload

    def describe(self):
        return f"SensorBasic(type={self.sensor_type}, ver={self.sensor_version}, temp={self.temperature}°C, batt={self.battery}%, rssi={self.rssi})"