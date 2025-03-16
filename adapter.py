import time
import can
import json


class Adapter:
    def __init__(self, _channel: str, _bustype: str = 'socketcan', _bitrate: int = 500000):
        self.channel = _channel
        self.bustype = _bustype
        self.bitrate = _bitrate
        self.bus = None

    def connect(self):
        self.bus = can.interface.Bus(
            channel=self.channel, bustype=self.bustype, bitrate=self.bitrate)
        print(
            f"Connected to CAN bus on channel {self.channel} with bitrate {self.bitrate}")

    def disconnect(self):
        if self.bus:
            self.bus.shutdown()
            self.bus = None
            print(f"Disconnected from CAN bus on channel {self.channel}")

    def send(self, _data: bytes, _arbitration_id: int):
        if self.bus:
            message = can.Message(
                arbitration_id=_arbitration_id, data=_data, is_extended_id=False)
            self.bus.send(message)
            print(f"Sent data to CAN bus on channel {self.channel}: {_data}")
        else:
            print("Bus is not connected")

    def listen(self, listen_time: float, output_file: str):
        if self.bus:
            end_time = time.time() + listen_time
            messages = []
            while time.time() < end_time:
                message = self.bus.recv(timeout=1)
                if message:
                    print(
                        f"Received data from CAN bus on channel {self.channel}: {message.data}")
                    messages.append({
                        'timestamp': message.timestamp,
                        'arbitration_id': message.arbitration_id,
                        'data': list(message.data)
                    })
            with open(output_file, 'w') as f:
                json.dump(messages, f, indent=4)
            print(f"Recorded data saved to {output_file}")
        else:
            print("Bus is not connected")
