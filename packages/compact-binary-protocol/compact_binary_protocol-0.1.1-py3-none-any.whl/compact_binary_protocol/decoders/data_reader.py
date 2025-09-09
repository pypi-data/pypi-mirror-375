class DataReader:
    """Sequential reader for bytes with big-endian decode helpers."""

    def __init__(self, data):
        self.data = data
        self.position = 0

    def read_var_string(self):
        if self.position >= len(self.data):
            raise IndexError("Not enough data to read string length")
        length = self.data[self.position]
        self.position += 1
        if self.position + length > len(self.data):
            raise IndexError(f"Not enough data to read string of length {length}")
        string_bytes = self.data[self.position:self.position + length]
        self.position += length
        return string_bytes.decode('ascii')

    def read_int4(self):
        if self.position + 4 > len(self.data):
            raise IndexError("Not enough data to read 4-byte integer")
        int_bytes = self.data[self.position:self.position + 4]
        self.position += 4
        return int.from_bytes(int_bytes, byteorder='big')
