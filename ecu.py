from utils.can_actions import is_valid_response, send_and_receive
from utils.constants import DID_IDENTIFIERS
from utils.iso14229_1 import Services
from utils.iso15765_2 import IsoTp


class ECU:
    def __init__(self, client_id, setver_id):
        self.client_id = client_id
        self.server_id = setver_id
        self.sessions = []
        self.services = []
        self.dids = []

    def discover_sessions(self):
        diagnostic_session_control = Services.DiagnosticSessionControl
        service_id = diagnostic_session_control.service_id
        sub_function = diagnostic_session_control.DiagnosticSessionType.DEFAULT_SESSION
        session_control_data = [service_id, sub_function]

        with IsoTp(None, None) as tp:
            resp = send_and_receive(
                tp, session_control_data, self.client_id, timeout=0.1)
            if resp and is_valid_response(resp):
                print("Entered Default Session (0x01) successfully.")

            for session in range(0x02, 0x0F):  # Check sessions from 0x02 to 0x0F
                print(f"Requesting Session {hex(session)}")

                resp = send_and_receive(
                    tp, [diagnostic_session_control.service_id, session], self.client_id, timeout=0.1)
                print(f"Response: {resp}")

                if resp and is_valid_response(resp):
                    print(f"Session {hex(session)} is supported.")
                    self.sessions.append(session)

            resp = send_and_receive(
                tp, session_control_data, self.client_id, timeout=0.1)

    def discover_dids(self):
        for did in DID_IDENTIFIERS:
            # Create the Read Data by Identifier (0x22) request message
            # 0x22 is the service ID for Read Data by Identifier
            request_data = [0x22, did[0]]
            with IsoTp(None, None) as tp:
                request_msg = tp.get_frames_from_message(request_data)

                # Send the request and wait for the response
                resp = send_and_receive(
                    tp, request_msg, self.client_id, timeout=0.1)

                # If response is valid, store the DID and data
                if resp and is_valid_response(resp):
                    print(f"Discovered DID 0x{did:X} with data: {resp}")
                    self.dids.append(did[0])
                else:
                    print(f"Failed to discover DID 0x{did:X}")

    def get_sessions(self):
        return self.sessions

    def get_dids(self):
        return self.dids

    """


blága szabolcs

hétfő 14: 00

"""
