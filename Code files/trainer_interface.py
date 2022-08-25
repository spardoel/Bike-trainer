# import asyncio
import logging
from bleak import BleakScanner, BleakClient
from functools import partial  # needed to allow self to be passed to notiify callbacks
from struct import unpack

FIT_MACHINE_CONTROL_POINT_HANDLE = 49
FIT_MACHINE_STATUS_HANDLE = 46
INDOOR_BIKE_DATA_HANDLE = 36


class TrainerInterface:
    def __init__(self, address):
        self.elapsed_time_sec = 0

        self.suito_address = address
        logging.info("Trainer interface created")

    def check_connection(self):

        if self.client.is_connected:
            logging.debug("Trainer is connected")
            return True
        else:
            logging.debug("Trainer is not connected")
            return False

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

    async def sub_to_trainer_characteristics(self):
        try:

            # Subscribe to the Indoor Bike Data characteristic
            # in odrer to send additiona input arguments to the callback, need to use partial.
            # bike_data_callback_class = BIkeDataCallbackClass
            await self.client.start_notify(
                INDOOR_BIKE_DATA_HANDLE, partial(bike_data_callback, self)
            )

            # Subscribe to the Fitness Machine Status characteristic
            await self.client.start_notify(FIT_MACHINE_STATUS_HANDLE, status_callback)

            # Subscribe to the Fitness Machine Controll Point characteristic
            await self.client.start_notify(
                FIT_MACHINE_CONTROL_POINT_HANDLE,
                control_callback,
            )

        except:
            logging.warning("Could not start the trainer data stream.")

    async def request_trainer_control(self):

        # Send the command to request control of the device. (convert to bytes first)
        await self.client.write_gatt_char(
            FIT_MACHINE_CONTROL_POINT_HANDLE, bytes([00]), response=True
        )

    async def set_trainer_resistance(self, new_power):

        new_target_power_bytes = new_power.to_bytes(2, "little")
        await self.client.write_gatt_char(
            FIT_MACHINE_CONTROL_POINT_HANDLE,
            bytearray([5, new_target_power_bytes[0], new_target_power_bytes[1]]),
            response=True,
        )


def control_callback(sender: int, data: bytearray):
    # Unpack the message and log it if there is a problem (result code 1 is normal)
    print(data)
    result_code = unpack("<b", data[2:3])[0]
    if result_code != 1:
        logging.debug("Control point response received. {result_code}")


def status_callback(sender: int, data: bytearray):
    # get the current resistance level of the trainer
    trainer_resistance_watts = unpack("<h", data[1:])[0]


def bike_data_callback(
    trainer_interface_instance: TrainerInterface, sender: int, data: bytearray
):
    # Unpack the data from the trainer to get the instantaneous cadence, instantaneous power and the total time
    # incomming data format is 2 bytes for flags, 2 for inst speed, 2 inst cadence, 3 total distance, 2 inst power, 2 elepsed time
    print(data)
    # Get the cadence in rpm
    inst_cadence_rpm = unpack("<H", data[4:6])[0] / 2
    # get the power in watts
    inst_power_watts = unpack("<h", data[9:11])[0]
    # get the elapsed time in seconds
    elapsed_time_sec = unpack("<H", data[11:14])[0]
    print(f"Elapsed time is: {elapsed_time_sec}")
    trainer_interface_instance.elapsed_time_sec = elapsed_time_sec
