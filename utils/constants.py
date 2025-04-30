
ARBITRATION_ID_MIN = 0x0
ARBITRATION_ID_MAX = 0x7FF
ARBITRATION_ID_MAX_EXTENDED = 0x1FFFFFFF

BYTE_MIN = 0x00
BYTE_MAX = 0xFF

MAX_MESSAGE_LENGTH = 0x8

MESSAGE_DELAY = 0.1
DELAY_STEP = 0.02
NOTIFIER_STOP_DURATION = 0.5

# Global CAN interface setting, which can be set through the -i flag to caringcaribou.py
# The value None corresponds to the default CAN interface (typically can0)
DEFAULT_INTERFACE = "vcan0"

VALID_SESSION_CONTROL_RESPONSES = [0x50, 0x7F]

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

DID_IDENTIFIERS = [
    (0xF180, "Boot software identification"),
    (0xF181, "Application software identification"),
    (0xF182, "Application data identification"),
    (0xF183, "Boot software fingerprint"),
    (0xF184, "Application software fingerprint"),
    (0xF185, "Application data fingerprint"),
    (0xF186, "Active diagnostic session"),
    (0xF187, "Manufacturer spare part number"),
    (0xF188, "Manufacturer ECU software number"),
    (0xF189, "Manufacturer ECU software version"),
    (0xF18A, "Identifier of system supplier"),
    (0xF18B, "ECU manufacturing date"),
    (0xF18C, "ECU serial number"),
    (0xF18D, "Supported functional units"),
    (0xF18E, "Manufacturer kit assembly part number"),
    (0xF190, "Vehicle Identification Number (VIN)"),
    (0xF192, "System supplier ECU hardware number"),
    (0xF193, "System supplier ECU hardware version number"),
    (0xF194, "System supplier ECU software number"),
    (0xF195, "System supplier ECU software version number"),
    (0xF196, "Exhaust regulation/type approval number"),
    (0xF197, "System name / engine type"),
    (0xF198, "Repair shop code / tester serial number"),
    (0xF199, "Programming date"),
    (0xF19D, "ECU installation date"),
    (0xF19E, "ODX file")
]


UDS_SERVICE_NAMES = {
    0x10: "DIAGNOSTIC_SESSION_CONTROL",
    0x11: "ECU_RESET",
    0x14: "CLEAR_DIAGNOSTIC_INFORMATION",
    0x19: "READ_DTC_INFORMATION",
    0x20: "RETURN_TO_NORMAL",
    0x22: "READ_DATA_BY_IDENTIFIER",
    0x23: "READ_MEMORY_BY_ADDRESS",
    0x24: "READ_SCALING_DATA_BY_IDENTIFIER",
    0x27: "SECURITY_ACCESS",
    0x28: "COMMUNICATION_CONTROL",
    0x29: "AUTHENTICATION",
    0x2A: "READ_DATA_BY_PERIODIC_IDENTIFIER",
    0x2C: "DYNAMICALLY_DEFINE_DATA_IDENTIFIER",
    0x2D: "DEFINE_PID_BY_MEMORY_ADDRESS",
    0x2E: "WRITE_DATA_BY_IDENTIFIER",
    0x2F: "INPUT_OUTPUT_CONTROL_BY_IDENTIFIER",
    0x31: "ROUTINE_CONTROL",
    0x34: "REQUEST_DOWNLOAD",
    0x35: "REQUEST_UPLOAD",
    0x36: "TRANSFER_DATA",
    0x37: "REQUEST_TRANSFER_EXIT",
    0x38: "REQUEST_FILE_TRANSFER",
    0x3D: "WRITE_MEMORY_BY_ADDRESS",
    0x3E: "TESTER_PRESENT",
    0x7F: "NEGATIVE_RESPONSE",
    0x83: "ACCESS_TIMING_PARAMETER",
    0x84: "SECURED_DATA_TRANSMISSION",
    0x85: "CONTROL_DTC_SETTING",
    0x86: "RESPONSE_ON_EVENT",
    0x87: "LINK_CONTROL"
}

NRC_NAMES = {
    0x00: "POSITIVE_RESPONSE",
    0x10: "GENERAL_REJECT",
    0x11: "SERVICE_NOT_SUPPORTED",
    0x12: "SUB_FUNCTION_NOT_SUPPORTED",
    0x13: "INCORRECT_MESSAGE_LENGTH_OR_INVALID_FORMAT",
    0x14: "RESPONSE_TOO_LONG",
    0x21: "BUSY_REPEAT_REQUEST",
    0x22: "CONDITIONS_NOT_CORRECT",
    0x24: "REQUEST_SEQUENCE_ERROR",
    0x25: "NO_RESPONSE_FROM_SUBNET_COMPONENT",
    0x26: "FAILURE_PREVENTS_EXECUTION_OF_REQUESTED_ACTION",
    0x31: "REQUEST_OUT_OF_RANGE",
    0x33: "SECURITY_ACCESS_DENIED",
    0x34: "AUTHENTICATION_REQUIRED",
    0x35: "INVALID_KEY",
    0x36: "EXCEEDED_NUMBER_OF_ATTEMPTS",
    0x37: "REQUIRED_TIME_DELAY_NOT_EXPIRED",
    0x70: "UPLOAD_DOWNLOAD_NOT_ACCEPTED",
    0x71: "TRANSFER_DATA_SUSPENDED",
    0x72: "GENERAL_PROGRAMMING_FAILURE",
    0x73: "WRONG_BLOCK_SEQUENCE_COUNTER",
    0x78: "REQUEST_CORRECTLY_RECEIVED_RESPONSE_PENDING",
    0x7E: "SUB_FUNCTION_NOT_SUPPORTED_IN_ACTIVE_SESSION",
    0x7F: "SERVICE_NOT_SUPPORTED_IN_ACTIVE_SESSION",
    0x81: "RPM_TOO_HIGH",
    0x82: "RPM_TOO_LOW",
    0x83: "ENGINE_IS_RUNNING",
    0x84: "ENGINE_IS_NOT_RUNNING",
    0x85: "ENGINE_RUN_TIME_TOO_LOW",
    0x86: "TEMPERATURE_TOO_HIGH",
    0x87: "TEMPERATURE_TOO_LOW",
    0x88: "VEHICLE_SPEED_TOO_HIGH",
    0x89: "VEHICLE_SPEED_TOO_LOW",
    0x8A: "THROTTLE_PEDAL_TOO_HIGH",
    0x8B: "THROTTLE_PEDAL_TOO_LOW",
    0x8C: "TRANSMISSION_RANGE_NOT_IN_NEUTRAL",
    0x8D: "TRANSMISSION_RANGE_NOT_IN_GEAR",
    0x8F: "BRAKE_SWITCHES_NOT_CLOSED",
    0x90: "SHIFT_LEVER_NOT_IN_PARK",
    0x91: "TORQUE_CONVERTER_CLUTCH_LOCKED",
    0x92: "VOLTAGE_TOO_HIGH",
    0x93: "VOLTAGE_TOO_LOW"
}

DELAY_DISCOVERY = 0.01
DELAY_TESTER_PRESENT = 0.5
DELAY_SECSEED_RESET = 0.01
TIMEOUT_SERVICES = 0.2
TIMEOUT_SUBSERVICES = 0.02

# Max number of arbitration IDs to backtrack during verification
VERIFICATION_BACKTRACK = 5
# Extra time in seconds to wait for responses during verification
VERIFICATION_EXTRA_DELAY = 0.5

BYTE_MIN = 0x00
BYTE_MAX = 0xFF

DUMP_DID_MIN = 0x0000
DUMP_DID_MAX = 0xFFFF
DUMP_DID_TIMEOUT = 0.2

MEM_START_ADDR = 0
MEM_LEN = 0x100
MEM_SIZE = 0x10
ADDR_BYTE_SIZE = 4
MEM_LEN_BYTE_SIZE = 2
