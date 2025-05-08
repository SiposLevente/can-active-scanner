import argparse
from can_adapter import CANAdapter
from utils.common import get_car_type


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CAN UDS Prober")
    parser.add_argument("--dbc-file", help="Path to the DBC file (optional)")
    parser.add_argument("--duration", type=int, default=5,
                        help="Time to listen to CAN traffic")
    parser.add_argument("--channel", default="can0",
                        help="CAN interface channel (default: can0)")
    args = parser.parse_args()

    adapter = CANAdapter(
        interface="socketcan",
        channel=args.channel,
        bitrate=500000,
        dbc_file=args.dbc_file
    )

    result = adapter.infer_protocol()
    print(f"Inferred Protocol: {result}")

    adapter.collect_ecus()
    print("=" * 20)
    adapter.gather_ecu_info()
    adapter.print_ecu_info()

    adapter.print_data_from_ecus()

    # type list of (ecu, (did, data))
    data = adapter.get_data_from_ecus()
    for ecu, ecu_data_list in data:
        for did, data in ecu_data_list:
            if did == 0xF187:
                print(
                    f"ECU ID: 0x{ecu.client_id:04X}, Server ID: 0x{ecu.server_id:04X}")
                print(f"DID: {hex(did)}, Data: {data.hex()}")
                car_type = get_car_type(data)
                print(f"Car Type: {car_type}")
