import struct
from ..encodings import encode_var_string

class LocationData:
    TYPE_GNSS = 1
    TYPE_CELL = 2

    def __init__(self, loc_type, *, latitude=None, longitude=None, mcc=None, mnc=None, lac=None, cell_id=None, rssi=None):
        self.loc_type = int(loc_type)
        self.latitude = latitude
        self.longitude = longitude
        self.mcc = mcc
        self.mnc = mnc
        self.lac = lac
        self.cell_id = cell_id
        self.rssi = rssi

    @staticmethod
    def gnss(latitude, longitude):
        return LocationData(LocationData.TYPE_GNSS, latitude=float(latitude), longitude=float(longitude))

    @staticmethod
    def cell(mcc, mnc, lac, cell_id, rssi):
        return LocationData(LocationData.TYPE_CELL, mcc=str(mcc), mnc=str(mnc), lac=str(lac), cell_id=str(cell_id), rssi=int(rssi))

    def to_bytes(self):
        if self.loc_type == LocationData.TYPE_GNSS:
            if self.latitude is None or self.longitude is None:
                raise ValueError("GNSS LocationData requires latitude and longitude")
            return struct.pack('>Bff', self.loc_type, float(self.latitude), float(self.longitude))
        elif self.loc_type == LocationData.TYPE_CELL:
            if None in (self.mcc, self.mnc, self.lac, self.cell_id) or self.rssi is None:
                raise ValueError("CELL LocationData requires mcc, mnc, lac, cell_id, and rssi")
            from_bytes = struct.pack('>B', self.loc_type)
            return (
                    from_bytes
                    + encode_var_string(self.mcc)
                    + encode_var_string(self.mnc)
                    + encode_var_string(self.lac)
                    + encode_var_string(self.cell_id)
                    + struct.pack('>b', int(self.rssi))
            )
        else:
            raise ValueError(f"Unknown LocationData type: {self.loc_type}")

    def describe(self):
        if self.loc_type == LocationData.TYPE_GNSS:
            return f"GNSS(lat={self.latitude}, lon={self.longitude})"
        elif self.loc_type == LocationData.TYPE_CELL:
            return f"CELL(mcc={self.mcc}, mnc={self.mnc}, lac={self.lac}, cell_id={self.cell_id}, rssi={self.rssi})"
        return f"UNKNOWN(type={self.loc_type})"