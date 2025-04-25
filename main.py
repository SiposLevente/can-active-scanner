import os
import time
import can
import cantools
import argparse


class CANAdapter:
    def __init__(self, interface: str, channel: str, bitrate: int, dbc_file: str = None):
        self.interface = interface
        self.channel = channel
        self.bitrate = bitrate
        self.dbc_file = dbc_file
        self.messages = []
        self.uds_ids = set()
        self.sessions = {}

        # Load the DBC file if provided
        self.dbc = None
        if self.dbc_file:
            try:
                self.dbc = cantools.database.load_file(dbc_file)
                print(f"Loaded DBC file: {dbc_file}")
            except Exception as e:
                print(f"Failed to load DBC file: {e}")

        # Initialize CAN bus
        self.bus = can.interface.Bus(
            bustype=self.interface, channel=self.channel, bitrate=self.bitrate
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

    def decode_messages(self):
        if not self.dbc:
            print("No DBC file provided. Skipping decoding.")
            return []

        decoded_messages = []
        for message in self.messages:
            try:
                decoded = self.dbc.decode_message(
                    message.arbitration_id, message.data
                )
                decoded_messages.append((message.arbitration_id, decoded))
                print(
                    f"Decoded message: ID={message.arbitration_id}, Data={decoded}")
            except Exception as e:
                print(
                    f"Failed to decode message ID={message.arbitration_id}: {e}")
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

    def send_message(self, arbitration_id: int, data: bytes):
        message = can.Message(arbitration_id=arbitration_id,
                              data=data, is_extended_id=False)
        try:
            self.bus.send(message)
            print(f"Sent message: ID={arbitration_id:#04x}, Data={data.hex()}")
        except can.CanError as e:
            print(f"Failed to send message: {e}")

    def find_uds_service_ids(self):
        for msg in self.messages:
            if 0x10 <= msg.data[0] <= 0x3F:
                self.uds_ids.add(msg.arbitration_id)
        print(f"UDS service IDs found: {[hex(i) for i in self.uds_ids]}")
        return list(self.uds_ids)

    def discover_sessions(self):
        for uds_id in self.uds_ids:
            sessions = []
            for session_type in [0x01, 0x02, 0x03]:  # Default, Programming, Extended
                data = bytes([0x10, session_type])
                self.send_message(uds_id, data)
                response = self.bus.recv(timeout=1)
                if response and response.arbitration_id != uds_id:
                    sessions.append(session_type)
                    print(
                        f"Session {session_type:#02x} accepted by ID {uds_id:#04x}")
            if sessions:
                self.sessions[uds_id] = sessions
        print(f"Discovered sessions: {self.sessions}")
        return self.sessions

    def probe_services_in_sessions(self):
        for uds_id, sessions in self.sessions.items():
            for session in sessions:
                # First, switch to session
                session_request = bytes([0x10, session])
                self.send_message(uds_id, session_request)
                time.sleep(0.1)  # slight delay to allow session switch

                for service in range(0x00, 0xff):  # typical range for UDS
                    request = bytes([service])
                    self.send_message(uds_id, request)
                    response = self.bus.recv(timeout=0.5)
                    if response and response.arbitration_id != uds_id:
                        print(
                            f"Service {service:#04x} responded in session {session:#02x} from ID {uds_id:#04x}")
                    else:
                        print(
                            f"No response for service {service:#04x} in session {session:#02x} (ID {uds_id:#04x})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CAN Adapter")
    parser.add_argument("--dbc-file", help="Path to the DBC file")
    args = parser.parse_args()

    adapter = CANAdapter(
        interface="socketcan",
        channel="vcan0",
        bitrate=500000,
        dbc_file=args.dbc_file
    )

    adapter.listen(duration=10)

    adapter.find_uds_service_ids()
    adapter.discover_sessions()
    adapter.probe_services_in_sessions()
