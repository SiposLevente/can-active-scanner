from enum import Enum
from errno import ETIMEDOUT

from utils import constants
from utils.can_actions import listen_for_response, send_request


class PossibleProtocol(Enum):
    UDS = "UDS over ISO-TP"
    LIKELY_ISOTP = "Likely ISO-TP (Possibly UDS or proprietary)"
    PROPRIETARY_ISOTP = "Proprietary ISO-TP"
    UNKNOWN = "Unknown or non-diagnostic protocol"


def probe_uds_functional(bus):
    print("\n[+] Probing UDS functional broadcast...")
    request = [0x02, 0x10, 0x01] + [0x00] * 5
    send_request(bus, constants.UDS_BROADCAST_ID, request)
    return listen_for_response(bus, constants.RESPONSE_ID_RANGE, timeout=ETIMEDOUT) is not None


def probe_uds_physical(bus):
    print("\n[+] Probing UDS physical addressing (0x500–0x73F)...")
    request = [0x02, 0x10, 0x01] + [0x00] * 5
    for aid in constants.PHYSICAL_ID_RANGE:
        send_request(bus, aid, request)
        if listen_for_response(bus, [aid], timeout=0.3):
            print(f"[+] Response from {hex(aid)}")
            return True
    return False


def conclude_protocol(iso_tp, uds_func_resp, uds_phys_resp, diag_ids):
    print("\n--- Final Protocol Inference ---")
    if uds_func_resp or uds_phys_resp:
        print("[✓] Detected diagnostic responses → Most likely **UDS over ISO-TP**")
        return PossibleProtocol.UDS
    elif iso_tp and diag_ids:
        print(
            "[~] ISO-TP traffic + high diagnostic ID range → Likely **UDS or OEM over ISO-TP**")
        return PossibleProtocol.LIKELY_ISOTP
    elif iso_tp:
        print(
            "[~] ISO-TP detected, but no known diag responses → Likely **OEM proprietary protocol over ISO-TP**")
        return PossibleProtocol.PROPRIETARY_ISOTP
    else:
        print("[✗] No diagnostic pattern or transport protocol detected")
        return PossibleProtocol.UNKNOWN
