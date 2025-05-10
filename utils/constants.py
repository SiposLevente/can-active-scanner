
ARBITRATION_ID_MIN = 0x0
ARBITRATION_ID_MAX = 0x7FF
ARBITRATION_ID_MAX_EXTENDED = 0x1FFFFFFF

BYTE_MIN = 0x00
BYTE_MAX = 0xFF

VALUE_TO_ADD_FOR_SUCCESSFUL_RESPONSE = 0x40  # original + 0x40

NEGATIVE_RESPONSE_CODE = 0x7F

UDS_BROADCAST_ID = 0x7DF
PHYSICAL_ID_RANGE = range(0x500, 0x7ff)
RESPONSE_ID_RANGE = range(0x500, 0x7ff)

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

DID_IDENTIFIERS = {
    0xF180: "Boot software identification",
    0xF181: "Application software identification",
    0xF182: "Application data identification",
    0xF183: "Boot software fingerprint",
    0xF184: "Application software fingerprint",
    0xF185: "Application data fingerprint",
    0xF186: "Active diagnostic session",
    0xF187: "Manufacturer spare part number",
    0xF188: "Manufacturer ECU software number",
    0xF189: "Manufacturer ECU software version",
    0xF18A: "Identifier of system supplier",
    0xF18B: "ECU manufacturing date",
    0xF18C: "ECU serial number",
    0xF18D: "Supported functional units",
    0xF18E: "Manufacturer kit assembly part number",
    0xF190: "Vehicle Identification Number (VIN)",
    0xF192: "System supplier ECU hardware number",
    0xF193: "System supplier ECU hardware version number",
    0xF194: "System supplier ECU software number",
    0xF195: "System supplier ECU software version number",
    0xF196: "Exhaust regulation/type approval number",
    0xF197: "System name / engine type",
    0xF198: "Repair shop code / tester serial number",
    0xF199: "Programming date",
    0xF19D: "ECU installation date",
    0xF19E: "ODX file"
}

SECURITY_ACCESS_SUBFUNCTIONS = {
    0x01: "Request Seed - Level 1",
    0x02: "Send Key - Level 1",
    0x03: "Request Seed - Level 2",
    0x04: "Send Key - Level 2",
    0x05: "Request Seed - Level 3",
    0x06: "Send Key - Level 3",
    0x07: "Request Seed - Level 4",
    0x08: "Send Key - Level 4",
    0x09: "Request Seed - Level 5",
    0x0A: "Send Key - Level 5",
    0x0B: "Request Seed - Level 6",
    0x0C: "Send Key - Level 6",
    0x0D: "Request Seed - Level 7",
    0x0E: "Send Key - Level 7"
}

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

NRC_FOR_AVAILABLE_SERVICE = {
    # The ECU is currently busy and cannot process the request at this time
    0x21: "Busy-repeat request",
    # The requested action cannot be performed due to certain conditions not being met
    0x22: "Conditions not correct",
    # The ECU is available, but required components are not responding
    0x25: "No response from subnet component",
    # A time-based condition has not yet been met
    0x37: "Required time delay has not expired",
    # The maximum number of attempts to invoke the service has been exceeded
    0x36: "Exceeded number of attempts",
    # Some internal programming failure preventing the response
    0x72: "Programming failure",
    # Sequence error in multi-frame communication preventing response
    0x73: "Wrong block sequence counter",
    # ECU has received the request but response is still pending
    0x78: "Request received - response pending",
}
