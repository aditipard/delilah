"""Read-only health check of every servo on one controller board.

Usage: python check_servos.py <port>

It pings servo IDs 1 to 9 and prints each one's supply voltage and temperature.
It never switches a motor on, so nothing moves.
"""
import sys

import scservo_sdk as scs

BAUDRATE = 1_000_000
ADDR_VOLTAGE = 62      # Present_Voltage, in units of 0.1 V
ADDR_TEMPERATURE = 63  # Present_Temperature, in degrees Celsius
PINGS = 20


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    port = scs.PortHandler(sys.argv[1])
    if not port.openPort():
        sys.exit(f"Could not open {sys.argv[1]}")
    port.setBaudRate(BAUDRATE)
    packet = scs.PacketHandler(0)

    print(" ID  replies  voltage  temperature")
    found = 0
    for servo_id in range(1, 10):
        replies = sum(packet.ping(port, servo_id)[1] == scs.COMM_SUCCESS for _ in range(PINGS))
        if replies == 0:
            print(f"{servo_id:3d}  no reply")
            continue
        found += 1
        volts = packet.read1ByteTxRx(port, servo_id, ADDR_VOLTAGE)[0] / 10
        temp = packet.read1ByteTxRx(port, servo_id, ADDR_TEMPERATURE)[0]
        print(f"{servo_id:3d}  {replies:2d}/{PINGS}    {volts:4.1f} V   {temp:3d} C")
    port.closePort()
    print(f"{found} servos found")


if __name__ == "__main__":
    main()
