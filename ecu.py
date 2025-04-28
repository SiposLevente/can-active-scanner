from utils.can_actions import is_valid_response, send_and_receive
from utils.iso14229_1 import Services
from utils.iso15765_2 import IsoTp


class ECU:
    def __init__(self, client_id, setver_id):
        self.client_id = client_id
        self.server_id = setver_id
        self.sessions = []
        self.services = []

    def discover_sessions(self):
        with IsoTp(None, None) as tp:
            default_session_msg = tp.get_frames_from_message([0x10, 0x01])

            resp = send_and_receive(
                tp, default_session_msg, self.client_id, timeout=0.1)
            if resp and resp.data[0] == 0x50 and is_valid_response(resp):
                print("Entered Default Session (0x01) successfully.")

            for session in range(0x02, 0x0F):  # Check sessions from 0x02 to 0x0F

                msg = tp.get_frames_from_message([0x10, session])
                print(f"Requesting Session {hex(session)}")

                resp = send_and_receive(tp, msg, self.client_id, timeout=0.1)
                print(f"Response: {resp}")

                if resp and resp.data[0] == 0x50 and is_valid_response(resp):
                    print(f"Session {hex(session)} is supported.")
                    self.sessions.append(session)

            resp = send_and_receive(
                tp, default_session_msg, self.client_id, timeout=0.1)

    def discover_services(self):
        # Common UDS services based on the extracted SID information
        services = {
            0x10: "Diagnostic Session Control",
            0x11: "ECU Reset",
            0x27: "Security Access",
            0x28: "Communication Control",
            0x29: "Authentication",
            0x3E: "Tester Present",
            0x83: "Access Timing Parameters",
            0x85: "Control DTC Settings",
            0x87: "Link Control"
        }

        with IsoTp(None, None) as tp:
            for sid, service_name in services.items():
                # Send the service request to the ECU
                msg = tp.get_frames_from_message([sid])
                resp = send_and_receive(
                    tp, msg, self.client_id, timeout=0.1)

                # Check for positive response (0x50) indicating the service is supported
                if resp and resp.data and resp.data[0] == 0x50:
                    print(
                        f"Service {service_name} (SID {hex(sid)}) is supported.")
                    self.services.append(service_name)

    def get_sessions(self):
        return self.sessions

    def get_services(self):
        return self.services
