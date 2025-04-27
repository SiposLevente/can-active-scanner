import time
import can
import cantools
import argparse
# Make sure to replace this with actual module imports
from utils.can_actions import auto_blacklist
from utils.iso14229_1 import Services
from utils.iso15765_2 import IsoTp
import utils.constants as constants


class CANAdapter:
    def __init__(self, interface: str, channel: str, bitrate: int, dbc_file: str = None):
        self.interface = interface
        self.channel = channel
        self.bitrate = bitrate
        self.dbc_file = dbc_file
        self.dbc = None
        self.messages = []
        self.uds_ids = set()
        self.sessions = {}

        if dbc_file:
            try:
                self.dbc = cantools.database.load_file(dbc_file)
                print(f"Loaded DBC file: {dbc_file}")
            except Exception as e:
                print(f"Failed to load DBC file: {e}")

        self.bus = can.interface.Bus(
            bustype=self.interface,
            channel=self.channel,
            bitrate=self.bitrate
        )

    def listen(self, duration: int, print_messages: bool = False):
        print(f"Listening on {self.channel} for {duration} seconds...")
        start_time = time.time()
        while time.time() - start_time < duration:
            message = self.bus.recv(timeout=1)
            if message:
                self.messages.append(message)
                if print_messages:
                    print(f"Received message: {message}")

    def send_and_receive(self, arbitration_id: int, data: bytes, timeout: float = 1.0):
        """ Sends a CAN message and waits for a response. """
        try:
            message = can.Message(
                arbitration_id=arbitration_id, data=data, is_extended_id=False)
            self.bus.send(message)
            print(
                f"Sent message: {hex(arbitration_id)} with data {data.hex()}")

            # Wait for response within timeout period
            response = self.bus.recv(timeout=timeout)
            if response:
                print(
                    f"Received response: {response.data.hex()} from {hex(response.arbitration_id)}")
                return response
            else:
                print(f"No response received within {timeout} seconds.")
                return None
        except can.CanError as e:
            print(f"Error sending message: {e}")
            return None

    def is_valid_response(message):
        return (len(message.data) >= 2 and
                message.data[1] in constants.valid_session_control_responses)

    def find_uds_service_ids(self, min_id=constants.ARBITRATION_ID_MIN, max_id=constants.ARBITRATION_ID_MAX, blacklist_args=[],
                             auto_blacklist_duration=0, delay=0.5, verify=True, print_results=True):
        """
        Scans for diagnostics support by brute-forcing session control
        messages to different arbitration IDs.

        Returns a list of all (client_arb_id, server_arb_id) pairs found.
        """

        diagnostic_session_control = Services.DiagnosticSessionControl
        service_id = diagnostic_session_control.service_id
        sub_function = diagnostic_session_control.DiagnosticSessionType.DEFAULT_SESSION
        session_control_data = [service_id, sub_function]

        found_arbitration_ids = []

        # Example IsoTp instance
        with IsoTp(None, None) as tp:
            blacklist = set(blacklist_args)
            # Perform automatic blacklist scan
            if auto_blacklist_duration > 0:
                auto_bl_arb_ids = auto_blacklist(tp.bus,
                                                 auto_blacklist_duration,
                                                 self.is_valid_response,
                                                 print_results)
                blacklist |= auto_bl_arb_ids

            # Prepare session control frame
            sess_ctrl_frm = tp.get_frames_from_message(session_control_data)
            send_arb_id = min_id - 1
            while send_arb_id < max_id:
                send_arb_id += 1
                if print_results:
                    print(
                        f"\rSending Diagnostic Session Control to 0x{send_arb_id:04x}", end="")
                # Send Diagnostic Session Control
                tp.transmit(sess_ctrl_frm, send_arb_id, None)
                end_time = time.time() + delay
                # Listen for response
                while time.time() < end_time:
                    msg = tp.bus.recv(0)
                    if msg is None:
                        continue
                    if msg.arbitration_id in blacklist:
                        continue
                    if self.is_valid_response(msg):
                        if verify:
                            # Verification logic
                            verified = False
                            tp.set_filter_single_arbitration_id(
                                msg.arbitration_id)
                            if print_results:
                                print(
                                    f"\nVerifying response from 0x{send_arb_id:04x}")
                            for verify_arb_id in range(send_arb_id, send_arb_id - 10, -1):
                                if print_results:
                                    print(
                                        f"Resending 0x{verify_arb_id:04x}... ", end="")
                                tp.transmit(sess_ctrl_frm, verify_arb_id, None)
                                verification_end_time = time.time() + delay + 0.1
                                while time.time() < verification_end_time:
                                    verification_msg = tp.bus.recv(0)
                                    if verification_msg is None:
                                        continue
                                    if self.is_valid_response(verification_msg):
                                        verified = True
                                        send_arb_id = verify_arb_id
                                        break
                                if verified:
                                    print("Success")
                                    break
                            tp.clear_filters()
                            if not verified:
                                print("False match - skipping")
                                continue

                        if print_results:
                            print(
                                f"Found diagnostics server at 0x{send_arb_id:04x}, response at 0x{msg.arbitration_id:04x}")
                        found_arbitration_ids.append(
                            (send_arb_id, msg.arbitration_id))
        return found_arbitration_ids

    def decode_messages(self):
        if not self.dbc:
            print("No DBC file provided. Skipping decoding.")
            return []

        decoded_messages = []
        for message in self.messages:
            try:
                decoded = self.dbc.decode_message(
                    message.arbitration_id, message.data)
                decoded_messages.append((message.arbitration_id, decoded))
            except Exception:
                continue
        return decoded_messages

    def save_messages(self, output_file: str, decoded: bool = True):
        with open(output_file, 'w') as f:
            if decoded and self.dbc:
                decoded_messages = self.decode_messages()
                for arbitration_id, data in decoded_messages:
                    f.write(f"ID={arbitration_id}, Data={data}\n")
            else:
                for message in self.messages:
                    f.write(f"{message}\n")
        print(f"Messages saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CAN UDS Prober")
    parser.add_argument("--dbc-file", help="Path to the DBC file (optional)")
    parser.add_argument("--duration", type=int, default=5,
                        help="Time to listen to CAN traffic")
    args = parser.parse_args()

    adapter = CANAdapter(
        interface="socketcan",
        channel="vcan0",
        bitrate=500000,
        dbc_file=args.dbc_file
    )

    arbitration_ids = adapter.find_uds_service_ids(print_results=False)
    for arb_id, server_id in arbitration_ids:
        print(f"Found UDS server at {hex(server_id)} for client {hex(arb_id)}")
