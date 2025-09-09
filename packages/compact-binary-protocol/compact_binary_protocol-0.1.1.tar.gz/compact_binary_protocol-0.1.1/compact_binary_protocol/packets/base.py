import struct

class Packet:
    def __init__(self, command, imei, transaction_id=0, version=1):
        # Ensure command is exactly 2 characters (pad or truncate)
        if len(command) == 1:
            self.command = command + '\0'
        elif len(command) >= 2:
            self.command = command[:2]
        else:
            self.command = '\0\0'
        self.imei = imei
        self.transaction_id = transaction_id
        self.version = version

    @staticmethod
    def _encode_imei_bcd(imei_str: str) -> bytes:
        digits = ''.join(ch for ch in imei_str if ch.isdigit())
        if len(digits) == 0:
            return b"\x00" * 8
        if len(digits) % 2 == 1:
            digits = '0' + digits
        b = bytearray()
        for i in range(0, len(digits), 2):
            low = int(digits[i+1])
            high = int(digits[i])
            b.append((high << 4) | low)
        if len(b) < 8:
            b.extend(b"\x00" * (8 - len(b)))
        elif len(b) > 8:
            b = b[:8]
        return bytes(b)

    def build_header(self):
        imei_bytes = Packet._encode_imei_bcd(self.imei)
        header = struct.pack('>BBBH',
                             self.version,
                             ord(self.command[0]),
                             ord(self.command[1]),
                             self.transaction_id) + imei_bytes
        return header

    def to_bytes(self):
        raise NotImplementedError()

    def print(self, packet_type):
        packet_bytes = self.to_bytes()
        print("v" * 50)
        print(f"  Type: {packet_type}")
        print(f"  Transaction ID: {self.transaction_id}")
        print(f"  Packet: {packet_bytes.hex()}")
        print(f"  Packet size: {len(packet_bytes)} bytes")
        print("^" * 50)
