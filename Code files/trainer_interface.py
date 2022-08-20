# import asyncio
import logging
from bleak import BleakScanner, BleakClient


class TrainerInterface:
    def __init__(self, address):
        self.suito_address = address
        logging.info("Trainer interface created")

    async def trainer_connect(self):
        self.client = BleakClient(self.suito_address)
        try:
            await self.client.connect()
            print("Trainer connected.")
            # Read the characteristic and print the result
            manufacturer = await self.client.read_gatt_char(75)
            # use decode to convert from byte array
            self.manufacturer_string = manufacturer.decode("UTF-8")
            print(f"The Suito was made by:{self.manufacturer_string}")

        except Exception as e:
            print(e)

    async def scan_for_devices():
        devices = await BleakScanner.discover()
        for d in devices:
            print(f"{d.name},{d.address}")

    async def trainer_disconnect(self):
        try:
            await self.client.disconnect()
            print("trainer disconnected")
            logging.info("Trainer device disconnected")
        except Exception as e:
            print(e)
            logging.warning(e)
