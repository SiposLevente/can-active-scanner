import can
import sys


class CANCommunication:
    def __init__(self, channel='vcan0', bitrate=500000):
        """Initializes the CAN communication interface."""
        self.channel = channel
        self.bitrate = bitrate
        self.bus = None

    def setup_bus(self):
        """Set up the CAN bus interface."""
        try:
            self.bus = can.interface.Bus(
                channel=self.channel, bustype='socketcan', bitrate=self.bitrate)
            print(f"CAN bus {self.channel} initialized at {self.bitrate} bps.")
        except can.CanError as e:
            print(f"Failed to initialize CAN bus: {e}")
            sys.exit(1)

    def send_message(self, message_id, data):
        """Send a CAN message."""
        if not self.bus:
            print("CAN bus is not initialized.")
            return

        message = can.Message(arbitration_id=message_id,
                              data=data, is_extended_id=False)
        try:
            self.bus.send(message)
            print(f"Message sent: ID={message_id} Data={data}")
        except can.CanError as e:
            print(f"Failed to send message: {e}")

    def receive_message(self):
        """Receive a CAN message."""
        if not self.bus:
            print("CAN bus is not initialized.")
            return None

        try:
            message = self.bus.recv()
            print(
                f"Message received: ID={message.arbitration_id} Data={message.data}")
            return message
        except can.CanError as e:
            print(f"Failed to receive message: {e}")
            return None

    def close(self):
        """Close the CAN bus."""
        if self.bus:
            self.bus.shutdown()
            print("CAN bus closed.")
