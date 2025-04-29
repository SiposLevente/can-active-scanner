import argparse
from can_adapter import CANAdapter


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CAN UDS Prober")
    parser.add_argument("--dbc-file", help="Path to the DBC file (optional)")
    parser.add_argument("--duration", type=int, default=5,
                        help="Time to listen to CAN traffic")
    args = parser.parse_args()

    adapter = CANAdapter(
        interface="socketcan",
        channel="vcan0",
        bitrate=500000,
        dbc_file=args.dbc_file
    )

    adapter.collect_ecus()
    adapter.gather_ecu_info()
    adapter.print_ecu_info()
    adapter.print_data_from_ecus()
