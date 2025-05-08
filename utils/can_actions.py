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
        print(f"[>] Sent to {hex(arbitration_id)}: {msg.data.hex()}")
    except can.CanError:
        print("[-] CAN send error")


def listen_for_response(bus, expected_ids, timeout=1.0):
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

            print(f"Sniffed: ID {hex(aid)} DL:{msg.dlc} Data: {data.hex()}")

            if aid >= 0x700 or aid in range(0x500, 0x700):
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


def auto_blacklist(bus, duration, classifier_function, print_results):
    """Listens for false positives on the CAN bus and generates an arbitration ID blacklist.

    Finds all can.Message <msg> on 'bus' where 'classifier_function(msg)' evaluates to True.
    Terminates after 'duration' seconds and returns a set of all matching arbitration IDs.
    Prints progress, time countdown and list of results if 'print_results' is True.

    :param bus: CAN bus instance
    :param duration: duration in seconds
    :param classifier_function: function which, when called upon a can.Message instance,
                                returns a bool indicating if it should be blacklisted
    :param print_results: whether progress and results should be printed to stdout
    :type bus: can.Bus
    :type duration: float
    :type classifier_function: function
    :type print_results: bool
    :return set of matching arbitration IDs to blacklist
    :rtype set(int)
    """
    if print_results:
        print("Scanning for arbitration IDs to blacklist")
    blacklist = set()
    start_time = time.time()
    end_time = start_time + duration
    while time.time() < end_time:
        if print_results:
            time_left = end_time - time.time()
            num_matches = len(blacklist)
            print("\r{0:> 5.1f} seconds left, {1} found".format(
                time_left, num_matches), end="")
            stdout.flush()
        # Receive message
        msg = bus.recv(0.1)
        if msg is None:
            continue
        # Classify
        if classifier_function(msg):
            # Add to blacklist
            blacklist.add(msg.arbitration_id)
    if print_results:
        num_matches = len(blacklist)
        print("\r  0.0 seconds left, {0} found".format(num_matches), end="")
        if len(blacklist) > 0:
            print("\n  Detected IDs: {0}".format(
                " ".join(sorted(list(map(hex, blacklist))))))
        else:
            print()
    return blacklist
