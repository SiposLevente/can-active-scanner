import time
from typing import List


class NegativeResponseCodes(object):
    """
    ISO-14229-1 negative response codes
    """
    POSITIVE_RESPONSE = 0x00
    # 0x01-0x0F ISO SAE Reserved
    GENERAL_REJECT = 0x10
    SERVICE_NOT_SUPPORTED = 0x11
    SUB_FUNCTION_NOT_SUPPORTED = 0x12
    INCORRECT_MESSAGE_LENGTH_OR_INVALID_FORMAT = 0x13
    RESPONSE_TOO_LONG = 0x14
    # 0x15-0x20 ISO SAE Reserved
    BUSY_REPEAT_REQUEST = 0x21
    CONDITIONS_NOT_CORRECT = 0x22
    # 0x23 ISO SAE Reserved
    REQUEST_SEQUENCE_ERROR = 0x24
    NO_RESPONSE_FROM_SUBNET_COMPONENT = 0x25
    FAILURE_PREVENTS_EXECUTION_OF_REQUESTED_ACTION = 0x26
    # 0x27-0x30 ISO SAE Reserved
    REQUEST_OUT_OF_RANGE = 0x31
    # 0x32 ISO SAE Reserved
    SECURITY_ACCESS_DENIED = 0x33
    # 0x34 ISO SAE Reserved
    INVALID_KEY = 0x35
    EXCEEDED_NUMBER_OF_ATTEMPTS = 0x36
    REQUIRED_TIME_DELAY_NOT_EXPIRED = 0x37
    # 0x38-0x4F Reserved by extended data link security document
    # 0x50-0x6F ISO SAE Reserved
    UPLOAD_DOWNLOAD_NOT_ACCEPTED = 0x70
    TRANSFER_DATA_SUSPENDED = 0x71
    GENERAL_PROGRAMMING_FAILURE = 0x72
    WRONG_BLOCK_SEQUENCE_COUNTER = 0x73
    # 0x74-0x77 ISO SAE Reserved
    REQUEST_CORRECTLY_RECEIVED_RESPONSE_PENDING = 0x78
    # 0x79-0x7D ISO SAE Reserved
    SUB_FUNCTION_NOT_SUPPORTED_IN_ACTIVE_SESSION = 0x7E
    SERVICE_NOT_SUPPORTED_IN_ACTIVE_SESSION = 0x7F
    # 0x80 ISO SAE Reserved
    RPM_TOO_HIGH = 0x81
    RPM_TOO_LOW = 0x82
    ENGINE_IS_RUNNING = 0x83
    ENGINE_IS_NOT_RUNNING = 0x84
    ENGINE_RUN_TIME_TOO_LOW = 0x85
    TEMPERATURE_TOO_HIGH = 0x86
    TEMPERATURE_TOO_LOW = 0x87
    VEHICLE_SPEED_TOO_HIGH = 0x88
    VEHICLE_SPEED_TOO_LOW = 0x89
    THROTTLE_PEDAL_TOO_HIGH = 0x8A
    THROTTLE_PEDAL_TOO_LOW = 0x8B
    TRANSMISSION_RANGE_NOT_IN_NEUTRAL = 0x8C
    TRANSMISSION_RANGE_NOT_IN_GEAR = 0x8D
    # 0x8E ISO SAE Reserved
    BRAKE_SWITCHES_NOT_CLOSED = 0x8F
    SHIFT_LEVER_NOT_IN_PARK = 0x90
    TORQUE_CONVERTER_CLUTCH_LOCKED = 0x91
    VOLTAGE_TOO_HIGH = 0x92
    VOLTAGE_TOO_LOW = 0x93
    # 0x94-0xEF Reserved for specific conditions not correct
    # 0xF0-0xFE Vehicle manufacturer specific conditions not correct
    # 0xFF ISO SAE Reserved


class ServiceID(object):
    """
    ISO-14229-1 service ID definitions
    """
    DIAGNOSTIC_SESSION_CONTROL = 0x10
    ECU_RESET = 0x11
    CLEAR_DIAGNOSTIC_INFORMATION = 0x14
    READ_DTC_INFORMATION = 0x19
    READ_DATA_BY_IDENTIFIER = 0x22
    READ_MEMORY_BY_ADDRESS = 0x23
    READ_SCALING_DATA_BY_IDENTIFIER = 0x24
    SECURITY_ACCESS = 0x27
    COMMUNICATION_CONTROL = 0x28
    READ_DATA_BY_PERIODIC_IDENTIFIER = 0x2A
    DYNAMICALLY_DEFINE_DATA_IDENTIFIER = 0x2C
    WRITE_DATA_BY_IDENTIFIER = 0x2E
    INPUT_OUTPUT_CONTROL_BY_IDENTIFIER = 0x2F
    ROUTINE_CONTROL = 0x31
    REQUEST_DOWNLOAD = 0x34
    REQUEST_UPLOAD = 0x35
    TRANSFER_DATA = 0x36
    REQUEST_TRANSFER_EXIT = 0x37
    REQUEST_FILE_TRANSFER = 0x38
    WRITE_MEMORY_BY_ADDRESS = 0x3D
    TESTER_PRESENT = 0x3E
    ACCESS_TIMING_PARAMETER = 0x83
    SECURED_DATA_TRANSMISSION = 0x84
    CONTROL_DTC_SETTING = 0x85
    RESPONSE_ON_EVENT = 0x86
    LINK_CONTROL = 0x87


class BaseService(object):
    """Base class for services"""
    service_id = None


class Services(object):
    """Class structure containing service specific constants, sub-function
       parameters and functions"""

    class DiagnosticSessionControl(BaseService):

        service_id = ServiceID.DIAGNOSTIC_SESSION_CONTROL

        class DiagnosticSessionType(object):
            # 0x00 ISO SAE Reserved
            DEFAULT_SESSION = 0x01
            PROGRAMMING_SESSION = 0x02
            EXTENDED_DIAGNOSTIC_SESSION = 0x03
            SAFETY_SYSTEM_DIAGNOSTIC_SESSION = 0x04
            # 0x05-0x3F ISO SAE Reserved
            # 0x40-0x5F Vehicle manufacturer specific
            VEHICLE_MANUFACTURER_SESSION_MIN = 0x40
            VEHICLE_MANUFACTURER_SESSION_MAX = 0x5F
            # 0x60-0x7E System supplier specific
            SYSTEM_SUPPLIER_SESSION_MIN = 0x60
            SYSTEM_SUPPLIER_SESSION_MAX = 0x7E
            # 0x7F ISO SAE Reserved

    class EcuReset(BaseService):

        service_id = ServiceID.ECU_RESET

        class ResetType(object):
            # 0x00 ISO SAE Reserved
            HARD_RESET = 0x01
            KEY_OFF_ON_RESET = 0x02
            SOFT_RESET = 0x03
            ENABLE_RAPID_POWER_SHUTDOWN = 0x04
            DISABLE_RAPID_POWER_SHUTDOWN = 0x05
            # 0x06-0x3F ISO SAE Reserved
            # 0x40-0x5F Vehicle manufacturer specific
            # 0x60-0x7E System supplier specific
            # 0x7F ISO SAE Reserved

    class SecurityAccess(BaseService):

        service_id = ServiceID.SECURITY_ACCESS

        class RequestSeedOrSendKey(object):
            """
            These are lined up so that value X "request seed level N" has
            a matching "send key level N" at value X+1.

            0x01 is Request seed level 0x01
            0x02 is Send key level 0x01
            0x03 is Request seed level 0x02
            0x04 is Send key level 0x02
            (...)
            0x41 is Request seed level 0x21
            0x42 is Send key level 0x21

            The security levels numbering is arbitrary and does not imply
            any relationship between the levels.
            """

            # 0x00 ISO SAE Reserved
            # 0x01-0x42 Vehicle manufacturer specific request
            #           seed/send key pairs
            # 0x43-0X5E ISO SAE Reserved
            ISO_26021_2_VALUES = 0x5F
            ISO_26021_2_SEND_KEY = 0x60
            # 0x61-0x7E System supplier specific
            # 0x7F ISO SAE Reserved

            __REQUEST_SEED_MIN = 0x01
            __REQUEST_SEED_MAX = 0x41
            __SEND_KEY_MIN = 0x02
            __SEND_KEY_MAX = 0x42

            def is_valid_request_seed_level(self, sub_function):
                """Returns True if 'sub_function' is a valid request seed
                   value and False otherwise"""
                value = sub_function & 0x7F
                valid_interval = (self.__REQUEST_SEED_MIN
                                  <= value <= self.__REQUEST_SEED_MAX)
                is_odd = value % 2 == 1
                return valid_interval and is_odd

            def is_valid_send_key_level(self, sub_function):
                """Returns True if 'sub_function' is a valid send key value
                   and False otherwise"""
                value = sub_function & 0x7F
                valid_interval = (self.__SEND_KEY_MIN
                                  <= value <= self.__SEND_KEY_MAX)
                is_even = value % 2 == 0
                return valid_interval and is_even

            @staticmethod
            def get_send_key_for_request_seed(seed):
                return seed + 1


class Iso14229_1(object):
    P3_CLIENT = 5

    def __init__(self, tp):
        self.tp = tp

    def __enter__(self):
        return self

    @staticmethod
    def get_service_response_id(request_id):
        """
        Returns the service response ID for the given request ID

        :param request_id: Request service ID
        :return: Corresponding response service ID
        """
        return request_id + 0x40

    @staticmethod
    def get_service_request_id(response_id):
        """
        Returns the service request ID for the given response ID

        :param response_id: Response service ID
        :return: Corresponding request service ID
        """
        return response_id - 0x40
