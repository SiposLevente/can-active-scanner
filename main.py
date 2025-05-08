import argparse
from can_adapter import CANAdapter
from utils.common import get_car_type


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CAN UDS Prober")
    parser.add_argument("--dbc-file", help="Path to the DBC file (optional)")
    parser.add_argument("--duration", type=int, default=5,
                        help="Time to listen to CAN traffic")
    parser.add_argument("--channel", default="can0",
                        help="CAN interface channel (default: vcan0)")
    args = parser.parse_args()

    adapter = CANAdapter(
        interface="socketcan",
        channel=args.channel,
        bitrate=500000,
        dbc_file=args.dbc_file
    )

    # result = adapter.infer_protocol()
    # print(f"Inferred Protocol: {result}")

    adapter.collect_ecus()
    adapter.gather_ecu_info()
    adapter.print_ecu_info()

    adapter.print_data_from_ecus()

    # data = adapter.get_data_from_ecus()
    # # find serial number did in data
    # for ecu_data in data:
    #     print(f"Client ID: {ecu_data[0].client_id}, Server ID: {ecu_data[0].server_id}")
    #     for did_data in ecu_data[1]:
    #         if did_data[0] == 0xF18C:
    #             print(f"Serial Number: {did_data[1]}")
    #             car_type = get_car_type(did_data[1])
    #             print(f"Car Type: {car_type}")
    #             break
