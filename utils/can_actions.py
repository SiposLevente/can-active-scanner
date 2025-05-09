import time

import can
import utils.constants as constants

from sys import stdout
from utils.iso15765_2 import IsoTp


def send_request(bus, arbitration_id, data):
    msg = can.Message(arbitration_id=arbitration_id,
                      data=data,
                      is_extended_id=False)
    try:
        bus.send(msg)
    except can.CanError:
        print("[-] CAN send error")


def listen_for_response(bus, expected_ids, timeout=0.1):
    start = time.time()
    while time.time() - start < timeout:
        msg = bus.recv(timeout)
        if msg and msg.arbitration_id in expected_ids:
            print(
                f"[<] Response from {hex(msg.arbitration_id)}: {msg.data.hex()}")
            return msg
    return None


def sniff_can(bus, duration=5):
    print(f"[~] Sniffing traffic for {duration} seconds...")
    iso_tp_detected = False
    diagnostic_ids_seen = set()
    seen_ids = set()

    start = time.time()
    while time.time() - start < duration:
        msg = bus.recv(timeout=1)
        if msg:
            aid = msg.arbitration_id
            seen_ids.add(aid)
            data = msg.data

            if aid >= 0x700 or aid in range(0x000, 0x800):
                diagnostic_ids_seen.add(aid)

            if len(data) > 0:
                first_byte = data[0]
                if first_byte & 0xF0 == 0x10:
                    print("[!] ISO-TP First Frame")
                    iso_tp_detected = True
                elif first_byte & 0xF0 == 0x20:
                    print("[!] ISO-TP Consecutive Frame")
                    iso_tp_detected = True
                elif first_byte == 0x30:
                    print("[!] ISO-TP Flow Control")
                    iso_tp_detected = True

    return iso_tp_detected, diagnostic_ids_seen


def is_valid_response(message):
    return (len(message.data) >= 2 and message.data[1] in constants.VALID_SESSION_CONTROL_RESPONSES)


def send_and_receive(tp: IsoTp, msg: list, send_arb_id: int, timeout: float = 0.1):
    msg = tp.get_frames_from_message(msg)
    tp.transmit(msg, send_arb_id, None)
    end_time = time.time() + timeout
    while time.time() < end_time:
        msg = tp.bus.recv(0)
        if msg is None:
            continue
        if is_valid_response(msg):
            return msg
    return None
