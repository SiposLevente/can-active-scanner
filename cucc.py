CAR_TYPE_MAPPING = {
    '5WA': 'Volkswagen AG (Volkswagen, Audi, Skoda, SEAT)',
    '5FA': 'Volkswagen AG (Volkswagen, Audi, Skoda, SEAT)',
    '1EA': 'Volkswagen AG (Volkswagen, Audi, Skoda, SEAT)',
    '2Q0': 'Continental AG (likely for ECUs like Engine Control Modules, Transmission Control Modules)',
    '3Q0': 'Continental AG (likely for ECUs like Engine Control Modules, Transmission Control Modules)',
    '5Q0': 'Continental AG (likely for ECUs like Engine Control Modules, Transmission Control Modules)',
    '5WA-series': 'Engine Control Modules (ECMs) or Transmission Control Modules (TCMs) used in Volkswagen AG vehicles',
    '5FA-series': 'Body Control Modules (BCMs) or Gateway Modules',
    '1EA-series': 'Powertrain Control Modules (PCMs) or Engine Management Systems',
    '2Q0-series': 'ECUs produced by Continental, including engine management, ABS, airbag systems',
    '3Q0-series': 'ECUs produced by Continental, including engine management, ABS, airbag systems',
    '5Q0-series': 'ECUs produced by Continental, including engine management, ABS, airbag systems'
}


def get_part_type(identifier: bytearray) -> str:
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
