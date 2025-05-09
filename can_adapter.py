
import time
from typing import List

import can
import cantools

from ecu import ECU
from utils import constants
from utils.can_actions import is_valid_response, send_and_receive, sniff_can
from utils.iso14229_1 import ServiceID, Services
from utils.iso15765_2 import IsoTp

from utils.protocol_types import conclude_protocol, probe_uds_functional, probe_uds_physical


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

    def collect_ecus(self, min_id=constants.ARBITRATION_ID_MIN, max_id=constants.ARBITRATION_ID_MAX, delay=0.1, verify=True, print_results=True):
        diagnostic_session_control = Services.DiagnosticSessionControl
        service_id = diagnostic_session_control.service_id  # 0x10
        sub_function = diagnostic_session_control.DiagnosticSessionType.DEFAULT_SESSION  # 0x01
        session_control_data = [service_id, sub_function]

        with IsoTp(None, None, channel=self.channel) as tp:
            # Prepare session control frame
            send_arb_id = min_id - 1
            total_ids = max_id - min_id + 1
            scanned_ids = 0

            if print_results:
                print(
                    f"Scanning for ECUs from 0x{(send_arb_id+1):04X} to 0x{max_id:04X}...")

            while send_arb_id < max_id:
                send_arb_id += 1
                scanned_ids += 1

                # Print progress
                progress = (scanned_ids / total_ids) * 100
                print(
                    f"\rProgress: {progress:.2f}% ({scanned_ids}/{total_ids})", end="")

                response_msg = send_and_receive(
                    tp, session_control_data, send_arb_id, timeout=delay)

                if response_msg is None:
                    continue
                if is_valid_response(response_msg, service_id):
                    if print_results:
                        print(
                            f"\rSending Diagnostic Session Control to 0x{send_arb_id:04x}")
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
                                    f"Resending 0x{verify_arb_id:04x}...", end="")
                            verification_msg = send_and_receive(
                                tp, session_control_data, verify_arb_id, timeout=delay + 0.1)
                            if verification_msg and is_valid_response(verification_msg, service_id):
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
            print("Discovering sessions...", end="", flush=True)
            ecu.discover_sessions(channel=self.channel)
            print("done!")

            print("Discovering services...", end="", flush=True)
            ecu.discover_services(channel=self.channel)
            print("done!")
            print("-" * 20)
        print("=" * 20)

    def print_ecu_info(self):
        for ecu in self.ECUs:
            print(
                f"ECU ID: 0x{ecu.client_id:04X}, Server ID: 0x{ecu.server_id:04X}")
            for session in ecu.sessions:
                print(
                    f"\tSession ID: 0x{session.session_id:02X}\tServices: {[hex(service) for service in session.services]}")
            print("-" * 20)

    def print_data_from_ecus_by_identifer(self):
        for ecu in self.ECUs:
            print(
                f"ECU ID: 0x{ecu.client_id:04X}, Server ID: 0x{ecu.server_id:04X}")
            for session in ecu.sessions:
                if ServiceID.READ_DATA_BY_IDENTIFIER in session.services:
                    print(f"\tSession ID: 0x{session.session_id:02X}")
                    for did in constants.DID_IDENTIFIERS:
                        data = ecu.get_data_from_ecu_by_identifier(
                            did, self.channel, session.session_id)
                        if data is not None:
                            print(f"\t\tDID {hex(did)}: {data}")
                    break
            print("-" * 20)

    def get_data_from_ecus_by_identifer(self):
        ecu_data_list = []
        for ecu in self.ECUs:
            ecu_sessions_data = []
            for session in ecu.sessions:
                if ServiceID.READ_DATA_BY_IDENTIFIER in session.services:
                    session_data = []
                    for did in constants.DID_IDENTIFIERS:
                        data = ecu.get_data_from_ecu_by_identifier(
                            did, self.channel, session.session_id)
                        session_data.append((did, data))
                    ecu_sessions_data.append(
                        (session.session_id, session_data))
            ecu_data_list.append((ecu, ecu_sessions_data))
        return ecu_data_list

    def get_security_access(self, sec_level: int):
        if sec_level not in range(1, 8):
            print(f"Invalid security access level: {sec_level}")
            return None
        sec_level = sec_level*2-1

        data = None
        for ecu in self.ECUs:
            needed_session = ecu.find_session_with_service(
                ServiceID.SECURITY_ACCESS, channel=self.channel)
            if needed_session is None:
                continue
            data = ecu.request_seed_security_access(
                sec_level, channel=self.channel)

        return data

    def shutdown(self):
        if self.bus:
            self.bus.shutdown()
            print("CAN bus shutdown.")
        else:
            print("No CAN bus to shutdown.")

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

    def infer_protocol(self):
        print(f"Starting protocol detection on {self.channel}...")

        iso_tp, diag_ids = sniff_can(self.bus, duration=6)

        uds_func = probe_uds_functional(self.bus)
        uds_phys = probe_uds_physical(self.bus)

        result = conclude_protocol(iso_tp, uds_func, uds_phys, diag_ids)
        print(f"\n[RESULT] Most likely protocol: {result.value}")

        return result
