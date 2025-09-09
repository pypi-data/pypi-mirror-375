import struct
from .base import Packet
from ..encodings import encode_var_string

class PowerOnPacket(Packet):
    def __init__(self, imei, transaction_id, customer_id, software_version, modem_version, mcc, mnc, rat):
        super().__init__('P+', imei, transaction_id, 1)
        self.customer_id = customer_id
        self.software_version = software_version
        self.modem_version = modem_version
        self.mcc = mcc
        self.mnc = mnc
        self.rat = rat

    def to_bytes(self):
        header = self.build_header()
        cid_bytes = b""
        try:
            if isinstance(self.customer_id, str):
                hex_str = self.customer_id.strip().lower()
                if hex_str.startswith('0x'):
                    hex_str = hex_str[2:]
                if len(hex_str) % 2 != 0:
                    raise ValueError("customer_id hex must have even length")
                cid_bytes = bytes.fromhex(hex_str) if hex_str else b""
            elif isinstance(self.customer_id, (bytes, bytearray)):
                cid_bytes = bytes(self.customer_id)
        except Exception as e:
            print(f"Warning: invalid customer_id '{self.customer_id}': {e}. Using zero-length.")
            cid_bytes = b""
        if len(cid_bytes) > 255:
            print(f"Warning: customer_id too long ({len(cid_bytes)} bytes). Truncating to 255 bytes.")
            cid_bytes = cid_bytes[:255]
        customer_id_with_length = struct.pack('>B', len(cid_bytes)) + cid_bytes
        software_version_with_length = encode_var_string(self.software_version)
        modem_version_with_length = encode_var_string(self.modem_version)
        mcc_with_length = encode_var_string(self.mcc)
        mnc_with_length = encode_var_string(self.mnc)
        rat_with_length = encode_var_string(self.rat)
        data = customer_id_with_length + software_version_with_length + modem_version_with_length + mcc_with_length + mnc_with_length + rat_with_length
        return header + data

    def print(self, packet_type):
        packet_bytes = self.to_bytes()
        print("v" * 50)
        print(f"  Type: {packet_type}")
        print(f"  Transaction ID: {self.transaction_id}")
        print(f"  Software Version: {self.software_version}")
        print(f"  Modem Version: {self.modem_version}")
        print(f"  Network: MCC:{self.mcc}, MNC:{self.mnc}, RAT:{self.rat}")
        print(f"  Packet: {packet_bytes.hex()}")
        print(f"  Packet size: {len(packet_bytes)} bytes")
        print("^" * 50)
