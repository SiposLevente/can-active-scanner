from utils.constants import CAR_TYPE_MAPPING


def convert_to_byte_list(did_identifier):
    return [(did_identifier & 0xFF00) >> 8, did_identifier & 0xFF]


def get_car_type(identifier: bytearray) -> str:
    try:
        # decode ignoring non-UTF-8 bytes
        identifier_str = identifier.decode('utf-8', errors='ignore')
    except Exception:
        return "Unknown"

    # First try to find an exact match for any known 3-character identifier
    for key in CAR_TYPE_MAPPING:
        if not key.endswith('-series') and key in identifier_str:
            return CAR_TYPE_MAPPING[key]

    # If not found, try prefix matches for -series
    for key in CAR_TYPE_MAPPING:
        if key.endswith('-series'):
            prefix = key.replace('-series', '')
            if prefix in identifier_str:
                return CAR_TYPE_MAPPING[key]
    return "Unknown"
