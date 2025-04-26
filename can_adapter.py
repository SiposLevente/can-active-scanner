import time
import can


class CANAdapter:
    def __init__(self, interface: str, channel: str, bitrate: int):
        self.interface = interface
        self.channel = channel
        self.bitrate = bitrate
        self.bus = can.interface.Bus(
            bustype=self.interface,
            channel=self.channel,
            bitrate=self.bitrate
        )

    def send_and_receive(self, arbitration_id: int, data: bytes, timeout: float = 2.0):
        """
        Sends a CAN message and waits for a response.
        """
        message = can.Message(arbitration_id=arbitration_id,
                              data=data,
                              is_extended_id=False)
        try:
            self.bus.send(message)
            start = time.time()
            while time.time() - start < timeout:
                response = self.bus.recv(timeout=0.1)
                if response:
                    print(
                        f"Received response from {hex(response.arbitration_id)}: {response.data}")
                    if response.arbitration_id == arbitration_id + 8:
                        return response
        except can.CanError as e:
            print(f"CAN send error on ID {hex(arbitration_id)}: {e}")
        return None

    def find_uds_service_ids(self, id_range=range(0x000, 0x7FF)):
        """
        Probes the CAN bus for UDS service responders.
        """
        print("Probing for UDS responders...")
        discovered_clients = []

        for arb_id in id_range:
            # Send the Diagnostic Session Control request (0x10)
            response = self.send_and_receive(arb_id, b'\x10\x01')

            # 0x50 is the expected response for a successful Diagnostic Session Control
            if response and response.data[0] == 0x50:
                server_id = response.arbitration_id
                print(
                    f"Found diagnostics server at {hex(arb_id)}, response at {hex(server_id)}")
                # Add to discovered clients
                discovered_clients.append((arb_id, server_id))

        # Output the discovered client-server pairs
        print("\nIdentified diagnostics:")
        print("+------------+------------+")
        print("| CLIENT ID  | SERVER ID  |")
        print("+------------+------------+")
        for client_id, server_id in discovered_clients:
            print(f"| {hex(client_id):<10} | {hex(server_id):<10} |")
        print("+------------+------------+")
