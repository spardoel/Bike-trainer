import asyncio
from sys import byteorder
import time
from struct import pack, unpack
from bleak import BleakScanner, BleakClient


SUITO_ADDRESS = "F3:DB:2B:F4:47:0C"
# define the characteristic handles
FIT_MACHINE_CONTROL_POINT_HANDLE = 49
FIT_MACHINE_STATUS_HANDLE = 46
INDOOR_BIKE_DATA_HANDLE = 36


async def main(address):
    client = BleakClient(address)

    try:
        await client.connect()

        # Subscribe to the Indoor Bike Data characteristic
        await client.start_notify(INDOOR_BIKE_DATA_HANDLE, bike_data_callback)

        # Subscribe to the Fitness Machine Status characteristic
        await client.start_notify(FIT_MACHINE_STATUS_HANDLE, status_callback)

        # Subscribe to the Fitness Machine Controll Point characteristic
        await client.start_notify(FIT_MACHINE_CONTROL_POINT_HANDLE, control_callback)

        # Send the command to request control of the device. (convert to bytes first)
        await client.write_gatt_char(
            FIT_MACHINE_CONTROL_POINT_HANDLE, bytes([00]), response=True
        )

        # Send the command code and new target power to update device resistance
        new_target_power = 158
        new_target_power_bytes = new_target_power.to_bytes(2, "little")
        await client.write_gatt_char(
            FIT_MACHINE_CONTROL_POINT_HANDLE,
            bytearray([5, new_target_power_bytes[0], new_target_power_bytes[1]]),
            response=True,
        )

        time.sleep(5)

    except Exception as e:
        print(e)
    finally:
        await client.disconnect()


def control_callback(sender: int, data: bytearray):
    print(f"Control {sender}: {data}")


def status_callback(sender: int, data: bytearray):
    print(f"Status {sender}: {data}")
    # print the echoed new target power
    print(f"New target power (Watts) : {unpack('<h',data[1:])[0]}")


def bike_data_callback(sender: int, data: bytearray):

    print(f"Bike data {sender}: {data}")
    # unpack the 2 bytes corresponding to cadence using < for little endian and H for unsigned short
    print(f"Cadence (rpm) : {unpack('<H',data[4:6])[0] / 2}")
    # unpack the 2 bytes corresponding to power using < for little endian and h for signed short
    print(f"Power (Watts) : {unpack('<h',data[9:11])[0]}")


asyncio.run(main(SUITO_ADDRESS))
