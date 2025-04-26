import argparse
from can_adapter import CANAdapter


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="CAN UDS Service ID Discovery")
    parser.add_argument("--interface", type=str, default="socketcan",
                        help="CAN interface type (e.g., socketcan)")
    parser.add_argument("--channel", type=str, default="vcan0",
                        help="CAN interface channel (e.g., vcan0)")
    parser.add_argument("--bitrate", type=int,
                        default=500000, help="CAN bus bitrate")
    parser.add_argument("--duration", type=int, default=5,
                        help="Time duration to listen to CAN traffic")
    args = parser.parse_args()

    # Initialize the CAN adapter
    adapter = CANAdapter(interface=args.interface,
                         channel=args.channel, bitrate=args.bitrate)

    # Run UDS discovery
    adapter.find_uds_service_ids()


if __name__ == "__main__":
    main()
