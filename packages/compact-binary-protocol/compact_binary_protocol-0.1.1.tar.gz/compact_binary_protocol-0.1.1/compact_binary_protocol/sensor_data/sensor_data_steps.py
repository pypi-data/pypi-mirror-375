import struct

class SensorDataSteps:
    def __init__(self, battery: int, rssi: int, steps: int, sensor_version: int = 1):
        self.sensor_type = 3
        self.sensor_version = int(sensor_version)
        self.battery = int(battery)
        self.rssi = int(rssi)
        self.steps = int(steps)

    def to_bytes(self):
        payload = struct.pack('>BBi', self.battery, self.rssi, self.steps)
        header = struct.pack('>BBB', self.sensor_type, self.sensor_version, len(payload))
        return header + payload

    def describe(self):
        return (
            f"SensorSteps(type={self.sensor_type}, ver={self.sensor_version}, "
            f"batt={self.battery}%, rssi={self.rssi}, steps={self.steps})"
        )
