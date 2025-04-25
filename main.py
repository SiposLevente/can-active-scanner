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
        message = can.Message(arbitration_id=arbitration_id,
                              data=data,
                              is_extended_id=False)
        try:
            self.bus.send(message)
            start = time.time()
            while time.time() - start < timeout:
                response = self.bus.recv(timeout=0.1)
                if response and response.arbitration_id == arbitration_id + 8:
                    return response
        except can.CanError as e:
            print(f"CAN send error on ID {hex(arbitration_id)}: {e}")
        return None

    def find_uds_service_ids(self, id_range=range(0x000, 0x7FF)):
        print("Probing for UDS responders...")
        for arb_id in id_range:
            response = self.send_and_receive(
                arb_id, b'\x10\x01')  # Default diagnostic session
            if response and response.data[0] == 0x50:
                print(f"UDS response from ID {hex(arb_id)}")
                self.uds_ids.add(arb_id)

    def discover_sessions(self):
        print("Discovering supported sessions...")
        for arb_id in self.uds_ids:
            response = self.send_and_receive(
                arb_id, b'\x10\x03')  # Extended session request
            if response and response.data[0] == 0x50:
                print(f"{hex(arb_id)} supports extended session")
                self.sessions[arb_id] = 'extended'
            else:
                print(f"{hex(arb_id)} remains in default session")
                self.sessions[arb_id] = 'default'

    def probe_services_in_sessions(self):
        print("Probing services (e.g., VIN)...")
        for arb_id in self.uds_ids:
            vin_request = b'\x22\xF1\x90'  # Read Data By Identifier (VIN)
            response = self.send_and_receive(arb_id, vin_request)
            print(response)
            if response and response.data[0] == 0x62:
                vin = ''.join(chr(b) for b in response.data[3:])
                print(f"VIN from {hex(arb_id)}: {vin}")
            else:
                print(f"VIN request failed or not supported on {hex(arb_id)}")

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

    adapter.listen(duration=args.duration)
    adapter.find_uds_service_ids()
    adapter.discover_sessions()
    adapter.probe_services_in_sessions()
