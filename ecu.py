from utils.can_actions import is_valid_response, send_and_receive
from utils.common import convert_to_byte_list
from utils.iso14229_1 import Constants, Iso14229_1, NegativeResponseCodes, ServiceID, Services
from utils.iso15765_2 import IsoTp


class Session:
    def __init__(self, session_id):
        self.session_id = session_id
        self.services = []

    def add_service(self, service_id):
        if service_id not in self.services:
            self.services.append(service_id)


class ECU:
    def __init__(self, client_id, setver_id):
        self.client_id = client_id
        self.server_id = setver_id
        self.sessions: list[Session] = []

    def discover_sessions(self, channel=None):
        diagnostic_session_control = Services.DiagnosticSessionControl
        service_id = diagnostic_session_control.service_id

        with IsoTp(None, None, channel=channel) as tp:
            for session in range(0x01, 0x0F):  # Check sessions from 0x02 to 0x0F
                resp = self.switch_to_session(session, tp)

                # TODO: Check invalid response codes
                if resp:
                    if is_valid_response(resp, service_id):
                        self.sessions.append(Session(session))

            # Switch back to default session
            self.switch_to_session(
                Services.DiagnosticSessionControl.DiagnosticSessionType.DEFAULT_SESSION, tp)

    def discover_services(self, timeout: int = 0.1, channel=None):
        with IsoTp(arb_id_request=self.client_id, arb_id_response=self.server_id, channel=channel) as tp:
            tp.set_filter_single_arbitration_id(self.server_id)

            for session in self.sessions:
                # Iterate through all sessions
                self.switch_to_session(session.session_id, tp)

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
                            session.add_service(request_id)
                        elif status != NegativeResponseCodes.SERVICE_NOT_SUPPORTED:
                            # Any other response than "service not supported" counts
                            session.add_service(response_service_id)

            # Switch back to default session
            self.switch_to_session(
                Services.DiagnosticSessionControl.DiagnosticSessionType.DEFAULT_SESSION, tp)

    def get_data_from_ecu(self, did: int, channel=None):
        needed_session = None
        # find which session has the service 0x22
        for session in self.sessions:
            if ServiceID.READ_DATA_BY_IDENTIFIER in session.services:
                needed_session = session.session_id
                break
        if needed_session is None:
            print("No session with service 0x22 found")
            return None

        with IsoTp(None, None, channel=channel) as tp:
            self.switch_to_session(needed_session, tp)

        # Send request to ECU
        request = [ServiceID.READ_DATA_BY_IDENTIFIER]
        request.extend(convert_to_byte_list(did))

        with IsoTp(arb_id_request=self.client_id, arb_id_response=self.server_id) as tp:
            tp.send_request(request)
            # Get response
            msg = tp.bus.recv(0.1)
            if msg is None:
                return None
            # Parse response
            if len(msg.data) > 3:
                data_length = msg.data[2]
                data = msg.data[3:3 + data_length]
                return data

    def switch_to_session(self, session_id: int, tp: IsoTp):
        return send_and_receive(
            tp, [Services.DiagnosticSessionControl.service_id, session_id], self.client_id, timeout=0.1)

    def get_sessions(self):
        return self.sessions
