import struct
from .base import Packet
from ..encodings import encode_var_string
from ..decoders import DataReader

class UpdateRequestPacket(Packet):
    """
    Update request sent from server to device.
    Command code: 'U+'
    Fields (as var_strings in body): component, url, arguments
    """
    def __init__(self, imei, transaction_id, component: str, url: str, arguments: str):
        super().__init__('U+', imei, transaction_id, 1)
        self.component = component or ''
        self.url = url or ''
        self.arguments = arguments or ''

    def to_bytes(self):
        header = self.build_header()
        body = (
            encode_var_string(self.component) +
            encode_var_string(self.url) +
            encode_var_string(self.arguments)
        )
        return header + body

    @staticmethod
    def decode(imei: str, transaction_id: int, data: bytes):
        """
        Parse incoming payload bytes into an UpdateRequestPacket using DataReader.
        imei/transaction_id come from the header decoded by PacketDecoder.
        """
        reader = DataReader(data)
        component = reader.read_var_string()
        url = reader.read_var_string()
        arguments = reader.read_var_string()
        return UpdateRequestPacket(imei, transaction_id, component, url, arguments)

    def print(self, packet_type):
        packet_bytes = self.to_bytes()
        print("v" * 50)
        print(f"  Type: {packet_type}")
        print(f"  Transaction ID: {self.transaction_id}")
        print(f"  Component: {self.component}")
        print(f"  URL: {self.url}")
        print(f"  Arguments: {self.arguments}")
        print(f"  Packet: {packet_bytes.hex()}")
        print(f"  Packet size: {len(packet_bytes)} bytes")
        print("^" * 50)


class UpdateStatusPacket(Packet):
    """
    Update status sent from device to server.
    Command code: 'U-'
    Fields (as var_strings in body): component, status, result
    Status values: "waiting", "started", "success", "failed"
    """
    def __init__(self, imei, transaction_id, component: str, status: str, result: str = ""):
        super().__init__('U-', imei, transaction_id, 1)
        self.component = component or ''
        self.status = (status or '').lower()
        if self.status not in ("waiting", "started", "success", "failed"):
            # keep as-is but warn via fallback to allow forward compat; still encode provided string
            pass
        self.result = result or ''

    def to_bytes(self):
        header = self.build_header()
        body = (
            encode_var_string(self.component) +
            encode_var_string(self.status) +
            encode_var_string(self.result)
        )
        return header + body

    def print(self, packet_type):
        packet_bytes = self.to_bytes()
        print("v" * 50)
        print(f"  Type: {packet_type}")
        print(f"  Transaction ID: {self.transaction_id}")
        print(f"  Component: {self.component}")
        print(f"  Status: {self.status}")
        print(f"  Result: {self.result}")
        print(f"  Packet: {packet_bytes.hex()}")
        print(f"  Packet size: {len(packet_bytes)} bytes")
        print("^" * 50)
