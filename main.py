import argparse
from can_adapter import CANAdapter
from utils.common import get_car_type


def get_part_type(data):
    for ecu, ecu_data_list in data:
        for did, data in ecu_data_list:
            if did == 0xF187:
                print(
                    f"ECU ID: 0x{ecu.client_id:04X}, Server ID: 0x{ecu.server_id:04X}")
                print(f"DID: {hex(did)}, Data: {data.hex()}")
                car_type = get_car_type(data)
                print(
                    f"Part Type: {'Unknown' if car_type is None else car_type}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CAN UDS Prober")
    parser.add_argument("--dbc-file", help="Path to the DBC file (optional)")
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
    print("=" * 20)

    adapter.print_data_from_ecus_by_identifer()
    print("=" * 20)

    # type list of List[(ecu, List(did, data))]
    data_by_identifier = adapter.get_data_from_ecus_by_identifer()
    get_part_type(data_by_identifier)

    sec_seed = adapter.get_security_access(sec_level=1)
    print(f"Level 1 Security Seed: {sec_seed}")

    adapter.shutdown()
