from functools import partial # needed to allow self to be passed to notiify callbacks

import asyncio
from sys import byteorder
import time
from bleak import BleakScanner, BleakClient


SUITO_address =  'F3:DB:2B:F4:47:0C'



async def scanfordevices():
    devices = await BleakScanner.discover()
    for d in devices:
        if d.name == 'SUITO':
            print(d.name)
            print(d.metadata)
            print(' ')


class Bike_data:
    cadence = []
    power = []

    def callback(self,sender: int, data: bytearray):

        #print(f"{sender}: {data}")

        self.cadence.append(int.from_bytes(data[4:5],"little"))
        print(f"Cadence: {self.cadence[-1]}")
        print("the cadence is not accurate!")
        
        self.power.append(int.from_bytes(data[9:10],"little"))
        print(f"Power: {self.power[-1]}")


class Suito_trainer:
    manufacturer =''
    



async def main(address):
    client = BleakClient(address)
    suito = Suito_trainer()
    try:
        await client.connect()

        suito.manufacturer = await client.read_gatt_char(75) 
        bike_data_class = Bike_data


        await client.start_notify(36, partial(bike_data_class.callback, bike_data_class)) # 36 is the indoor bike data characteristic

        
        # Fitness machine status is handle 46
        await client.start_notify(46, status_callback) # Activate indications on the fitness machine status

        # fitness machine control point is handle 49
        await client.start_notify(49, control_callback) # Activate indications on the fitness machine control point

        await client.write_gatt_char(49,bytes([00]),response=True)
       
        
    # update the target power
        d = (100).to_bytes(2,"little")
        array_1 = [5,d[0],d[1]]
        await client.write_gatt_char(49,bytearray(array_1),response=True)

    # wait for the process to run a bit
        for i in range(0,10):
            time.sleep(1)


    except Exception as e:
        print(e)
    finally:
        await client.disconnect()


def control_callback(sender: int, data: bytearray):
    
    print(f"Control {sender}: {data}")

def status_callback(sender: int, data: bytearray):
    
    print(f"Status {sender}: {data}")
    payload=data[1:2]
    #print(data[0])
    #print(data[1])
    #print(data[2])
    #print(payload)
    
    
    print(int.from_bytes(payload, byteorder = "little"))
    #print(len(data))
    #print(int.from_bytes(data[2:3],"little"))

asyncio.run(main(SUITO_address))



