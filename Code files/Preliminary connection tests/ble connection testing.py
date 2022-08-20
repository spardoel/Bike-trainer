import asyncio
from bleak import BleakScanner, BleakClient


SUITO_ADDRESS = "F3:DB:2B:F4:47:0C"


async def scan_for_devices():
    devices = await BleakScanner.discover()
    for d in devices:
        if d.name == "SUITO":
            print(f"{d.name},{d.address}")


async def connect_and_display_characteristics(address):
    client = BleakClient(address)  #

    try:
        await client.connect()
        # Read the characteristic and print the result
        manufacturer = await client.read_gatt_char(75)
        print(f"The Suito was made by:{manufacturer}")

        # use decode to convert from byte array
        manufacturer_string = manufacturer.decode("UTF-8")
        print(f"The Suito was made by:{manufacturer_string}")

    except Exception as e:
        print(e)
    finally:
        await client.disconnect()


# asyncio.run(scan_for_devices())
asyncio.run(connect_and_display_characteristics(SUITO_ADDRESS))
