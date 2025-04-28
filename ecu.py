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
        diagnostic_session_control = Services.DiagnosticSessionControl
        service_id = diagnostic_session_control.service_id
        sub_function = diagnostic_session_control.DiagnosticSessionType.DEFAULT_SESSION
        session_control_data = [service_id, sub_function]

        with IsoTp(None, None) as tp:
            default_session_msg = tp.get_frames_from_message(
                session_control_data)

            resp = send_and_receive(
                tp, default_session_msg, self.client_id, timeout=0.1)
            if resp and is_valid_response(resp):
                print("Entered Default Session (0x01) successfully.")

            for session in range(0x02, 0x0F):  # Check sessions from 0x02 to 0x0F

                msg = tp.get_frames_from_message(
                    [diagnostic_session_control.service_id, session])
                print(f"Requesting Session {hex(session)}")

                resp = send_and_receive(tp, msg, self.client_id, timeout=0.1)
                print(f"Response: {hex(resp)}")

                if resp and is_valid_response(resp):
                    print(f"Session {hex(session)} is supported.")
                    self.sessions.append(session)

            resp = send_and_receive(
                tp, default_session_msg, self.client_id, timeout=0.1)

    def discover_services(self):
        with IsoTp(None, None) as tp:
            for ecu, sessions in self.sessions.items():
                print(f"Discovering services for ECU {hex(ecu)}...")
                for session in sessions:
                    print(
                        f"  - Checking services for Session {hex(session)}...")
                    services_to_check = [0x19, 0x22, 0x31]
                    for service_id in services_to_check:
                        msg = tp.get_frames_from_message([service_id])
                        resp = send_and_receive(tp, msg, ecu, timeout=0.1)
                        if resp and resp.data[0] == 0x50 and is_valid_response(resp):
                            print(
                                f"    Service {hex(service_id)} is supported in Session {hex(session)}")
                            if ecu not in self.services:
                                self.services[ecu] = {}
                            if session not in self.services[ecu]:
                                self.services[ecu][session] = []
                            self.services[ecu][session].append(service_id)

    def get_sessions(self):
        return self.sessions

    def get_services(self):
        return self.services
