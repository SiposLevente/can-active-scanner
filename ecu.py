from utils.can_actions import is_valid_response, send_and_receive
from utils.iso14229_1 import Constants, Iso14229_1, NegativeResponseCodes, Services
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
            resp = send_and_receive(
                tp, session_control_data, self.client_id, timeout=0.1)
            if resp and is_valid_response(resp):
                print("Entered Default Session (0x01) successfully.")

            for session in range(0x02, 0x0F):  # Check sessions from 0x02 to 0x0F
                print(f"Requesting Session {hex(session)}")

                resp = send_and_receive(
                    tp, [diagnostic_session_control.service_id, session], self.client_id, timeout=0.1)

                if resp and is_valid_response(resp):
                    print(f"Session {hex(session)} is supported.")
                    self.sessions.append(session)

            resp = send_and_receive(
                tp, session_control_data, self.client_id, timeout=0.1)

    def discover_services(self, timeout: int = 0.1):
        with IsoTp(arb_id_request=self.client_id, arb_id_response=self.server_id) as tp:
            tp.set_filter_single_arbitration_id(self.server_id)
            for service_id in range(0, 0xff):
                tp.send_request([service_id])

                # Get response
                msg = tp.bus.recv(timeout)
                if msg is None:
                    # No response received
                    continue
                # Parse response
                if len(msg.data) > 3:
                    # Since service ID is included in the response, mapping is correct even if response is delayed
                    response_id = msg.data[1]
                    response_service_id = msg.data[2]
                    status = msg.data[3]
                    if response_id != Constants.NR_SI:
                        request_id = Iso14229_1.get_service_request_id(
                            response_id)
                        self.services.append(request_id)
                    elif status != NegativeResponseCodes.SERVICE_NOT_SUPPORTED:
                        # Any other response than "service not supported" counts
                        self.services.append(response_service_id)

    def get_data_from_ecu(self, did: int):
        if 0x22 in self.services:
            # Read Data by Identifier (DID) service is supported

            # Send request to ECU
            request = [0x22, did]
            with IsoTp(arb_id_request=self.client_id, arb_id_response=self.server_id) as tp:
                tp.send_request(request)

                # Get response
                msg = tp.bus.recv(0.1)
                if msg is None:
                    return None

                # Parse response
                if len(msg.data) > 3:
                    response_did = msg.data[1]
                    data_length = msg.data[2]
                    data = msg.data[3:3 + data_length]
                    print(
                        f"DID {hex(response_did)}: {data}")
                    return data

    def get_sessions(self):
        return self.sessions

    def get_services(self):
        return self.services
