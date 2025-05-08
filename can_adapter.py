
import time
from typing import Counter, List, Protocol

import can
import cantools

from ecu import ECU
from utils import constants
from utils.can_actions import auto_blacklist, is_valid_response, send_and_receive
from utils.iso14229_1 import Services
from utils.iso15765_2 import IsoTp

from utils.protocol_types import infer_protocol


class CANAdapter:
    def __init__(self, interface: str, channel: str, bitrate: int, dbc_file: str = None):
        self.interface = interface
        self.channel = channel
        self.bitrate = bitrate
        self.dbc_file = dbc_file
        self.dbc = None
        self.ECUs: List[ECU] = []

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

    def collect_ecus(self, min_id=constants.ARBITRATION_ID_MIN, max_id=constants.ARBITRATION_ID_MAX, blacklist_args=[],
                     auto_blacklist_duration=0, delay=0.1, verify=True, print_results=True):
        diagnostic_session_control = Services.DiagnosticSessionControl
        service_id = diagnostic_session_control.service_id
        sub_function = diagnostic_session_control.DiagnosticSessionType.DEFAULT_SESSION
        session_control_data = [service_id, sub_function]

        # Example IsoTp instance
        with IsoTp(None, None) as tp:
            blacklist = set(blacklist_args)
            # Perform automatic blacklist scan
            if auto_blacklist_duration > 0:
                auto_bl_arb_ids = auto_blacklist(tp.bus,
                                                 auto_blacklist_duration,
                                                 is_valid_response,
                                                 print_results)
                blacklist |= auto_bl_arb_ids

            # Prepare session control frame
            send_arb_id = min_id - 1
            if print_results:
                print(
                    f"Scanning for ECUs from 0x{send_arb_id:04X} to 0x{max_id:04X}...")

            while send_arb_id < max_id:
                send_arb_id += 1
                # Send Diagnostic Session Control
                response_msg = send_and_receive(
                    tp, session_control_data, send_arb_id, timeout=delay)

                if response_msg is None:
                    continue
                if response_msg.arbitration_id in blacklist:
                    continue
                if is_valid_response(response_msg):
                    if print_results:
                        print(
                            f"Sending Diagnostic Session Control to 0x{send_arb_id:04x}")
                    if verify:
                        # Verification logic
                        verified = False
                        tp.set_filter_single_arbitration_id(
                            response_msg.arbitration_id)
                        if print_results:
                            print(
                                f"Verifying response from 0x{send_arb_id:04x}")
                        for verify_arb_id in range(send_arb_id, send_arb_id - 10, -1):
                            if print_results:
                                print(
                                    f"Resending 0x{verify_arb_id:04x}... ", end="")
                            verification_msg = send_and_receive(
                                tp, session_control_data, verify_arb_id, timeout=delay + 0.1)
                            if verification_msg and is_valid_response(verification_msg):
                                verified = True
                                send_arb_id = verify_arb_id
                                break
                        tp.clear_filters()
                        if not verified:
                            if print_results:
                                print("False match - skipping")
                            continue

                    if print_results:
                        print(
                            f"Found diagnostics server at 0x{send_arb_id:04x}, response at 0x{response_msg.arbitration_id:04x}")
                    self.ECUs.append(
                        ECU(send_arb_id, response_msg.arbitration_id))
        if print_results:
            print()

    def gather_ecu_info(self):
        for ecu in self.ECUs:
            print(
                f"ECU ID: 0x{ecu.client_id:04X}, Server ID: 0x{ecu.server_id:04X}")
            print("Discovering sessions...", end=" ")
            ecu.discover_sessions()
            print("done!")

            print("Discovering services...", end=" ")
            ecu.discover_services()
            print("done!")
            print("-" * 20)
        print("=" * 20)

    def print_ecu_info(self):
        for ecu in self.ECUs:
            print(
                f"ECU ID: 0x{ecu.client_id:04X}, Server ID: 0x{ecu.server_id:04X}")
            print(
                f"Sessions: {[hex(session) for session in ecu.get_sessions()]}")
            print(
                f"Services: {[hex(service) for service in ecu.get_services()]}")
            print("-" * 20)

    def print_data_from_ecus(self):
        for ecu in self.ECUs:
            print(
                f"ECU ID: 0x{ecu.client_id:04X}, Server ID: 0x{ecu.server_id:04X}")
            if 0x22 in ecu.services:
                for did in constants.DID_IDENTIFIERS:
                    data = ecu.get_data_from_ecu(did)
                    if data is not None:
                        print(f"DID {hex(did)}: {data}")
            else:
                print("Read Data by Identifier (DID) service is not supported.")

            print("-" * 20)

    def get_data_from_ecus(self):
        ecu_data_list = []
        for ecu in self.ECUs:
            if 0x22 in ecu.services:
                dids_data = []
                for did in constants.DID_IDENTIFIERS:
                    data = ecu.get_data_from_ecu(did)
                    dids_data.append((did, data))

                ecu_data = (ecu, dids_data)
                ecu_data_list.append(ecu_data)
        return ecu_data_list

    # ==========
    # ==========

    def print_ecus(self):
        if not self.ECUs:
            print("No ECUs found.")
            return
        print("Found ECUs:")
        for ecu in self.ECUs:
            print(ecu)

    def decode_messages(self, messages=[]):
        if not self.dbc:
            print("No DBC file provided. Skipping decoding.")
            return []
        decoded_messages = []
        for message in messages:
            try:
                decoded = self.dbc.decode_message(
                    message.arbitration_id, message.data)
                decoded_messages.append((message.arbitration_id, decoded))
            except Exception:
                continue
        return decoded_messages

    def save_messages(self, output_file: str, decoded: bool = True, duration=10):
        messages = self.listen(duration, False)
        with open(output_file, 'w') as f:
            if decoded and self.dbc:
                decoded_messages = self.decode_messages()
                for arbitration_id, data in decoded_messages:
                    f.write(f"ID={arbitration_id}, Data={data}\n")
            else:
                for message in messages:
                    f.write(f"{message}\n")
        print(f"Messages saved to {output_file}")

    def listen(self, duration: int, print_messages: bool = False):
        messages = []
        print(f"Listening on {self.channel} for {duration} seconds...")
        start_time = time.time()
        while time.time() - start_time < duration:
            message = self.bus.recv(timeout=1)
            if message:
                messages.append(message)
                if print_messages:
                    print(f"Received message: {message}")
        return messages

    def infer_protocol(self, duration: int = 10):
        messages = self.listen(duration, False)
        """Infers the protocol used by the ECU based on the messages received."""
        if not messages:
            print("No messages received. Cannot infer protocol.")
            return Protocol.UNCLEAR
        return infer_protocol(messages)
