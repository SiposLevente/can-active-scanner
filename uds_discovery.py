import can
import sys
from utils.iso14229_1 import Services, ReadDataByIdentifier
from can_communication.can_comm import CANCommunication


class UDSDiscovery(CANCommunication):
    def __init__(self, channel='vcan0', bitrate=500000):
        super().__init__(channel=channel, bitrate=bitrate)

    def send_uds_request(self, request):
        """Send a UDS request and receive the response."""
        if not self.bus:
            print("CAN bus is not initialized.")
            return None

        # Create the UDS message
        message = can.Message(arbitration_id=0x7E0,
                              data=request, is_extended_id=False)
        try:
            # Send the message
            self.bus.send(message)
            print(f"Sent UDS request: {request}")
        except can.CanError as e:
            print(f"Failed to send UDS request: {e}")
            return None

        # Wait for a response
        try:
            response = self.bus.recv(5.0)  # Timeout of 5 seconds
            if response:
                print(f"Received response: {response.data}")
                return response
            else:
                print("No response received within the timeout period.")
                return None
        except can.CanError as e:
            print(f"Failed to receive response: {e}")
            return None

    def uds_discovery(self):
        """Perform UDS discovery by querying ECUs."""
        # Prepare the UDS request (Diagnostic Session Control)
        diagnostic_session_request = Services.Services.DiagnosticSessionControl(
            0x01)  # 0x01 for default session

        # Send the diagnostic session request
        print("Sending Diagnostic Session Control request...")
        response = self.send_uds_request(diagnostic_session_request.encode())
        if response:
            print(f"Diagnostic session established with ECU: {response.data}")

        # Additional discovery logic can be added here
        # For example, querying ReadDataByIdentifier or other UDS services
        read_data_request = ReadDataByIdentifier(
            0xF190)  # Example identifier for vehicle info
        print("Sending Read Data By Identifier request...")
        response = self.send_uds_request(read_data_request.encode())
        if response:
            print(f"Data received from ECU: {response.data}")

        # Further service discovery logic can be added here
        print("UDS discovery complete.")


if __name__ == "__main__":
    uds_discovery = UDSDiscovery(channel='vcan0')
    uds_discovery.setup_bus()
    uds_discovery.uds_discovery()
    uds_discovery.close()
