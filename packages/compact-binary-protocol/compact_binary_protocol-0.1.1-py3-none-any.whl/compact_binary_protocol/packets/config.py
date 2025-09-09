import struct
from .base import Packet
from ..encodings import encode_var_string

class ConfigPacket(Packet):
    def __init__(self, imei, server_address, reporting_interval, reading_interval, transaction_id=0):
        super().__init__('C', imei, transaction_id)
        self.server_address = server_address
        self.reporting_interval = int(reporting_interval)
        self.reading_interval = int(reading_interval)

    def to_bytes(self):
        header = self.build_header()
        address_with_length = encode_var_string(self.server_address)
        data = address_with_length + struct.pack('>II', self.reporting_interval, self.reading_interval)
        return header + data

    @staticmethod
    def decode(imei: str, transaction_id: int, data: bytes):
        from ..decoders import DataReader
        reader = DataReader(data)
        server_address = reader.read_var_string()
        reporting_interval = reader.read_int4()
        reading_interval = reader.read_int4()
        return ConfigPacket(imei, server_address, reporting_interval, reading_interval, transaction_id)

    def print(self, packet_type):
        packet_bytes = self.to_bytes()
        print("v" * 50)
        print(f"  Type: {packet_type}")
        print(f"  Transaction ID: {self.transaction_id}")
        print(f"  Server: {self.server_address}")
        print(f"  Reporting Interval: {self.reporting_interval} seconds")
        print(f"  Reading Interval: {self.reading_interval} seconds")
        print(f"  Packet: {packet_bytes.hex()}")
        print(f"  Packet size: {len(packet_bytes)} bytes")
        print("^" * 50)