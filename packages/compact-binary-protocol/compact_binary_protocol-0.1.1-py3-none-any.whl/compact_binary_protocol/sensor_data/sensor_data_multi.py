import struct

class SensorDataMulti:
    def __init__(self, battery, rssi, first_timestamp, interval, records):
        self.sensor_type = int(2)
        self.sensor_version = int(1)
        self.battery = int(battery)
        self.rssi = int(rssi)
        self.first_timestamp = first_timestamp
        self.interval = interval
        self.records = records
        self.battery = int(battery)
        self.rssi = int(rssi)

    def to_bytes(self):
        payload_header = struct.pack(
            '>BBIHB',
            self.battery,
            self.rssi,
            int(self.first_timestamp),
            int(self.interval),
            len(self.records)
        )
        records_bytes = bytearray()
        for rec in self.records:
            temp = int(round(float(rec['temperature']) * 10))
            hum = int(round(float(rec['humidity']) * 10))
            records_bytes += struct.pack('>hh', temp, hum)
        payload = payload_header + bytes(records_bytes)
        header = struct.pack('>BBB', self.sensor_type, self.sensor_version, len(payload))
        return header + payload

    def describe(self):
        rec_cnt = len(self.records) if self.records is not None else 0
        return (
            f"SensorMulti(type={self.sensor_type}, ver={self.sensor_version}, "
            f"batt={self.battery}%, rssi={self.rssi}, first_ts={self.first_timestamp}, "
            f"interval={self.interval}s, records={rec_cnt})"
        )