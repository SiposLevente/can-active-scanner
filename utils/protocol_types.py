from enum import Enum
from typing import Counter


def is_probably_uds(frame):
    # UDS typically uses IDs in 0x7E0–0x7EF and has a SID in the first byte
    return 0x7E0 <= frame.arbitration_id <= 0x7EF and len(frame.data) > 1 and 0x10 <= frame.data[0] <= 0x3E


def is_probably_isotp(frame):
    # ISO-TP PCI types in first nibble: 0x0 (SF), 0x1 (FF), 0x2 (CF), 0x3 (FC)
    return len(frame.data) > 1 and ((frame.data[0] >> 4) in [0x0, 0x1, 0x2, 0x3])


def is_probably_j1939(frame):
    # J1939 uses 29-bit extended IDs and PGN typically in 0xF000–0xFFFF
    if frame.is_extended_id:
        pgn = (frame.arbitration_id >> 8) & 0xFFFF
        return 0xF000 <= pgn <= 0xFFFF
    return False


class Protocol(Enum):
    J1939 = "J1939"
    UDS_OVER_ISOTP = "UDS over ISO-TP"
    ISOTP_GENERIC = "ISO-TP (generic)"
    UNCLEAR = "Unclear or custom/non-standard"


def infer_protocol(messages):
    uds_count = 0
    isotp_count = 0
    j1939_count = 0
    id_counter = Counter()

    for msg in messages:
        id_counter[msg.arbitration_id] += 1
        if is_probably_uds(msg):
            uds_count += 1
        if is_probably_isotp(msg):
            isotp_count += 1
        if is_probably_j1939(msg):
            j1939_count += 1

    print("\n--- Heuristic Summary ---")
    print(f"Total messages: {len(messages)}")
    print(f"UDS-like frames: {uds_count}")
    print(f"ISO-TP-like frames: {isotp_count}")
    print(f"J1939-like frames: {j1939_count}")
    if id_counter:
        most_common_id, freq = id_counter.most_common(1)[0]
        print(f"Most common CAN ID: {hex(most_common_id)} (seen {freq} times)")
    else:
        print("No messages received.")

    if j1939_count > uds_count and j1939_count > isotp_count:
        return Protocol.J1939
    elif uds_count > 5 and isotp_count > 5:
        return Protocol.UDS_OVER_ISOTP
    elif isotp_count > 10:
        return Protocol.ISOTP_GENERIC
    else:
        return Protocol.UNCLEAR
