from can_communication.can_comm import CANCommunication

def main():
    # Initialize CAN communication on vcan0 interface
    can_comm = CANCommunication(channel='vcan0')
    can_comm.setup_bus()

    # Send a message with ID 0x123 and data [0x01, 0x02, 0x03]
    can_comm.send_message(0x123, [0x01, 0x02, 0x03])

    # Receive a CAN message
    message = can_comm.receive_message()

    # Close the CAN bus when done
    can_comm.close()

if __name__ == "__main__":
    main()
