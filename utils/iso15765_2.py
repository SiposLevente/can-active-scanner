from utils.constants import ARBITRATION_ID_MAX
import can
import time


class IsoTp:
    """
    Implementation of ISO-15765-2, also known as ISO-TP. This is a multi-frame messaging protocol
    over CAN, which allows message payloads of up to 4095 bytes.
    """

    MAX_SF_LENGTH = 7
    MAX_FF_LENGTH = 6
    MAX_CF_LENGTH = 7

    SF_PCI_LENGTH = 1
    CF_PCI_LENGTH = 1
    FF_PCI_LENGTH = 2
    FC_PCI_LENGTH = 3

    FC_FS_CTS = 0
    FC_FS_WAIT = 1
    FC_FS_OVFLW = 2

    SF_FRAME_ID = 0
    FF_FRAME_ID = 1
    CF_FRAME_ID = 2
    FC_FRAME_ID = 3

    N_BS_TIMEOUT = 1.5

    MAX_FRAME_LENGTH = 8
    MAX_MESSAGE_LENGTH = 4095

    def __init__(self, arb_id_request, arb_id_response, bus=None, padding_value=0x00):
        # Setting default bus to None rather than the actual bus prevents a CanError when
        # called with a virtual CAN bus, while the OS is lacking a working CAN interface
        if bus is None:
            from utils.constants import DEFAULT_INTERFACE
            self.bus = can.Bus(channel=DEFAULT_INTERFACE,
                               interface="socketcan")
        else:
            self.bus = bus
        self.arb_id_request = arb_id_request
        self.arb_id_response = arb_id_response
        # Controls optional padding of SF messages and the last CF frame in multi-frame messages
        # Disabled padding is _not_ part of ISO-15765-2, but might prove useful for testing against some targets
        self.padding_value = padding_value
        if padding_value is None:
            self.padding_enabled = False
        else:
            self.padding_enabled = True
            if not isinstance(padding_value, int):
                raise TypeError(
                    "IsoTp: padding must be an integer or None, received '{0}'".format(padding_value))
            if not 0x00 <= padding_value <= 0xFF:
                raise ValueError(
                    "IsoTp: padding must be in range 0x00-0xFF (0-255), got '{0}'".format(padding_value))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.bus.shutdown()

    def _set_filters(self, filters):
        """
        Sets filters for the CAN bus - description can be found at
        https://python-can.readthedocs.io/en/stable/bus.html#can.BusABC.set_filters

        :param filters: dict specifying "can_id", "can_mask" and (optional) "extended" flag
        :return: None
        """
        self.bus.set_filters(filters)

    def clear_filters(self):
        """Remove arbitration ID filters"""
        self._set_filters(None)

    def send_message(self, data, arbitration_id, force_extended=False):
        """
        Transmits a message using 'arbitration_id' and 'data' on 'self.bus'

        :param data: Data to send
        :param arbitration_id: Arbitration ID to use
        :param force_extended: Force extended arbitration ID
        :return: None
        """
        is_extended = force_extended or arbitration_id > ARBITRATION_ID_MAX
        msg = can.Message(
            arbitration_id=arbitration_id,
            data=data,
            is_extended_id=False
        )
        self.bus.send(msg)

    def decode_fc(self, frame):
        """
        Decodes a flow control (FC) frame

        :param frame: Frame to decode
        :return: Tuple of values flow status (FS), block size (BS) and separation time minimum (STmin) if valid,
                 Tuple of None, None, None otherwise
        """
        if len(frame) >= self.FC_PCI_LENGTH:
            fs = frame[0] & 0xF
            block_size = frame[1]
            st_min = frame[2]
            return fs, block_size, st_min
        else:
            return None, None, None

    def send_request(self, message):
        """
        Wrapper for sending 'message' as a request

        :param message: The message to send
        :return: None
        """
        frames = self.get_frames_from_message(
            message, padding_value=self.padding_value)
        self.transmit(frames, self.arb_id_request, self.arb_id_response)

    def transmit(self, frames, arbitration_id, arbitration_id_flow_control):
        """
        Transmits 'frames' in order on the bus, according to ISO-15765-2

        :param frames: List of frames (which are in turn lists of values) to send
        :param arbitration_id: The arbitration ID used for sending
        :param arbitration_id_flow_control: The arbitration ID used for receiving flow control (FC)
        :return: None
        """
        if len(frames) == 0:
            # No data to send
            return None
        elif len(frames) == 1:
            # Single frame
            self.send_message(frames[0], arbitration_id)
        elif len(frames) > 1:
            # Multiple frames
            frame_index = 0
            # Send first frame (FF)
            self.send_message(frames[frame_index], arbitration_id)
            number_of_frames_left_to_send = len(frames) - 1
            number_of_frames_left_to_send_in_block = 0
            frame_index += 1
            st_min = 0
            while number_of_frames_left_to_send > 0:
                receiver_is_ready = False
                while not receiver_is_ready:
                    # Wait for receiver to send flow control (FC)
                    msg = self.bus.recv(self.N_BS_TIMEOUT)
                    if msg is None:
                        # Quit on timeout
                        return None
                    # Verify that msg uses the expected arbitration ID
                    elif msg.arbitration_id != arbitration_id_flow_control:
                        continue
                    fc_frame = msg.data

                    # Decode Flow Status (FS) from FC message
                    fs, block_size, st_min = self.decode_fc(fc_frame)
                    if fs == self.FC_FS_WAIT:
                        # Flow status (FS) wait (WT)
                        continue
                    elif fs == self.FC_FS_CTS:
                        # Continue to send (CTS)
                        receiver_is_ready = True
                        number_of_frames_left_to_send_in_block = block_size

                        if number_of_frames_left_to_send < number_of_frames_left_to_send_in_block or block_size == 0:
                            number_of_frames_left_to_send_in_block = number_of_frames_left_to_send
                        # If STmin is specified in microseconds (0xF1-0xF9) or using reserved ranges (0x80-0xF0 and
                        # 0xFA-0xFF), round up to one millisecond
                        if st_min > 0x7F:
                            st_min = 1
                    elif fs == self.FC_FS_OVFLW:
                        # Overflow - abort transmission
                        return None
                    else:
                        # Timeout - did not receive a CTS message in time
                        return None
                while number_of_frames_left_to_send_in_block > 0:
                    # Send more frames, until it is time to wait for flow control (FC) again
                    self.send_message(frames[frame_index], arbitration_id)
                    frame_index += 1
                    number_of_frames_left_to_send_in_block -= 1
                    number_of_frames_left_to_send -= 1
                    if number_of_frames_left_to_send_in_block > 0:
                        time.sleep(st_min / 1000)

    @staticmethod
    def get_frames_from_message(message, padding_value=0x00):
        """
        Returns a copy of 'message' split into frames,
        :param message: Message to split
        :param padding_value: Integer value used to pad messages, or None to disable padding (not part of ISO-15765-3)
        :return: List of frames
        """
        if padding_value is None:
            padding_enabled = False
            padding_value = 0x00
        else:
            padding_enabled = True

        frame_list = []
        message_length = len(message)
        if message_length > IsoTp.MAX_MESSAGE_LENGTH:
            error_msg = "Message too long for ISO-TP. Max allowed length is {0} bytes, received {1} bytes".format(
                IsoTp.MAX_MESSAGE_LENGTH, message_length)
            raise ValueError(error_msg)
        if message_length <= IsoTp.MAX_SF_LENGTH:
            # Single frame (SF) message
            if padding_enabled:
                frame = [padding_value] * IsoTp.MAX_FRAME_LENGTH
            else:
                frame = [padding_value] * (message_length + 1)
            frame[0] = (IsoTp.SF_FRAME_ID << 4) | message_length
            for i in range(0, message_length):
                frame[1 + i] = message[i]
            frame_list.append(frame)
        else:
            # Multiple frame message
            bytes_left_to_copy = message_length
            # Create first frame (FF)
            frame = [padding_value] * IsoTp.MAX_FRAME_LENGTH
            frame[0] = (IsoTp.FF_FRAME_ID << 4) | (message_length >> 8)
            frame[1] = message_length & 0xFF
            for i in range(0, IsoTp.MAX_FF_LENGTH):
                frame[2 + i] = message[i]
            frame_list.append(frame)
            # Create consecutive frames (CF)
            bytes_copied = IsoTp.MAX_FF_LENGTH
            bytes_left_to_copy -= bytes_copied
            sn = 0
            while bytes_left_to_copy > 0:
                sn = (sn + 1) % 16
                if not padding_enabled and bytes_left_to_copy < 7:
                    # Skip padding on last CF
                    frame = [padding_value] * (bytes_left_to_copy + 1)
                else:
                    frame = [padding_value] * IsoTp.MAX_FRAME_LENGTH
                frame[0] = (IsoTp.CF_FRAME_ID << 4) | sn
                # Fill current CF
                bytes_to_copy_to_current_cf = min(
                    IsoTp.MAX_CF_LENGTH, bytes_left_to_copy)
                for i in range(bytes_to_copy_to_current_cf):
                    frame[1 + i] = message[bytes_copied]
                    bytes_left_to_copy = bytes_left_to_copy - 1
                    bytes_copied = bytes_copied + 1
                frame_list.append(frame)
        return frame_list
