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
            for session in range(0x01, 0x0F):
                msg = tp.get_frames_from_message([0x10, session])
                resp = send_and_receive(
                    tp, msg, self.client_id, 0.1)
                if resp.data[1] == 0x50 and is_valid_response(resp):
                    self.sessions.append(session)

    def discover_services(self):
        pass

    def get_sessions(self):
        return self.sessions

    def get_services(self):
        return self.services
