import os
import time
import can
import cantools
import argparse

known_uds_services = {0x10, 0x11, 0x27, 0x28,
                      0x22, 0x2E, 0x2F, 0x31, 0x34, 0x36, 0x3E, 0x85}


class CANAdapter:
    def __init__(self, interface: str, channel: str, bitrate: int, dbc_file: str = None):
        self.interface = interface
        self.channel = channel
        self.bitrate = bitrate
        self.dbc_file = dbc_file
        self.messages = []

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
            bustype=self.interface, channel=self.channel, bitrate=self.bitrate)

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
        """
        Decode the collected CAN messages using the DBC file.
        """
        if not self.dbc:
            print("No DBC file provided. Skipping decoding.")
            return []

        decoded_messages = []
        for message in self.messages:
            try:
                decoded = self.dbc.decode_message(
                    message.arbitration_id, message.data)
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
        """
        Send a CAN message.

        :param arbitration_id: The arbitration ID of the CAN message
        :param data: The data payload of the CAN message (as bytes)
        """
        message = can.Message(arbitration_id=arbitration_id,
                              data=data, is_extended_id=False)
        try:
            self.bus.send(message)
            print(f"Sent message: ID={arbitration_id}, Data={data}")
        except can.CanError as e:
            print(f"Failed to send message: {e}")

    def find_uds_service_ids(self):
        """
        Search for UDS service IDs in the recorded messages.

        :return: A list of arbitration IDs that match known UDS services.
        """
        uds_service_ids = []
        for message in self.messages:
            if message.arbitration_id in known_uds_services:
                uds_service_ids.append(message.arbitration_id)
                print(f"Found UDS service ID: {message.arbitration_id}")
        return uds_service_ids


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CAN Adapter")
    parser.add_argument("--dbc-file",
                        help="Path to the DBC file")
    args = parser.parse_args()

    # Example usage
    adapter = CANAdapter(
        interface="socketcan",
        channel="vcan0",
        bitrate=500000,
        dbc_file=args.dbc_file
    )

    adapter.listen(duration=10)  # Listen for 10 seconds

    # Search for the ID of UDS services
    uds_service_ids = adapter.find_uds_service_ids()
    print(f"UDS Service IDs found: {uds_service_ids}")
