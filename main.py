import argparse
from can_adapter import CANAdapter
from utils.can_actions import DEFAULT_INTERFACE


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CAN UDS Prober")
    parser.add_argument("--dbc-file", help="Path to the DBC file (optional)")
    parser.add_argument("--duration", type=int, default=5,
                        help="Time to listen to CAN traffic")
    args = parser.parse_args()

    adapter = CANAdapter(
        interface="socketcan",
        channel=DEFAULT_INTERFACE,
        bitrate=500000,
        dbc_file=args.dbc_file
    )

    result = adapter.infer_protocol()
    print(f"Inferred Protocol: {result}")

    adapter.collect_ecus()
    adapter.gather_ecu_info()
    adapter.print_ecu_info()
    adapter.print_data_from_ecus()
