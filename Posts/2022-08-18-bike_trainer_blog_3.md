# Developing a cycling control program for my indoor trainer (TrainerRoad clone) Part 3 - Use bleak library to establish BLE connection in python

After installing the bleak library, I followed the examples in the documentation for device scanning and connection (https://bleak.readthedocs.io/en/latest/scanning.html#bleakscanner). I then read a characteristic to confirm that the connection was working as intended. 
It is worth noting that the asycnio library was needed to allow the asynchronous bluetooth commumication. 

### Scanning for devices
```
import asyncio
from bleak import BleakScanner

async def scan_for_devices():
    devices = await BleakScanner.discover()
    for d in devices:
        print(f"{d.name},{d.metadata}")
asyncio.run(scan_for_devices())
```
Which returned the folowing list of available devices.
```
None,{'uuids': [], 'manufacturer_data': {76: b'\x10\x05>\x18\xd2)\x1e'}}
S9f1b4589198ad67cC,{'uuids': ['00001122-0000-1000-8000-00805f9b34fb'], 'manufacturer_data': {76: b"\x02\x15t'\x8b\xda\xb6DE \x8f\x0cr\x0e\xaf\x05\x995\x00\x00\x97}\xc5"}}
None,{'uuids': [], 'manufacturer_data': {117: b'B\x04\x01\x80f\\\xc1\xd7\xe9\xec\xb7^\xc1\xd7\xe9\xec\xb6\x01\\=\x00\x00\x00\x00'}}
Venus_2C4CC63CF269,{'uuids': ['06aa1910-f22a-11e3-9daa-0002a5d5c51b'], 'manufacturer_data': {9474: b'@\x0c\x00\x00G\x10'}}
None,{'uuids': [], 'manufacturer_data': {6: b'\x01\t \x02\x96\x93\xee\xdf\xdd5T<X\x9d\x97\x97\x0ey)\xb4\xbd\xae&\xca\x99\x191'}}
SUITO,{'uuids': ['00001826-0000-1000-8000-00805f9b34fb', '00001818-0000-1000-8000-00805f9b34fb'], 'manufacturer_data': {}}
None,{'uuids': [], 'manufacturer_data': {76: b'\t\x06\x03\x11\xc0\xa8\x02\x0e\x15\x05\x01&{p<'}}
None,{'uuids': ['0000fe9f-0000-1000-8000-00805f9b34fb'], 'manufacturer_data': {224: b'\x02\x10\xca\x965g'}}
None,{'uuids': [], 'manufacturer_data': {76: b'\x10\x06N\x1d\x9b\x8c\x9fx'}}
None,{'uuids': [], 'manufacturer_data': {76: b'\x10\x05\x0c\x18\xc1\x1c\x81'}}
None,{'uuids': [], 'manufacturer_data': {}}
```

I used an if statement to only select the desired device, and changed the print statement to include the address, as follows
```
import asyncio
from bleak import BleakScanner

async def scan_for_devices():
    devices = await BleakScanner.discover()
    for d in devices:
        if d.name == 'SUITO':
            print(f"{d.name},{d.metadata}")
asyncio.run(scan_for_devices())
```
Which gave the SUITO device name and address.
```
SUITO,F3:DB:2B:F4:47:0C
```

I already knew the address from the MATLAB preliminary testing and from observing the packet traffic. This confirms that we found the correct device. 

### Establish a connection and show the characteristics
Again, starting from the bleak documentation, I ran the following code to connect to the device and print out the available characteristics. 

```
from bleak import BleakClient

SUITO_ADDRESS = 'F3:DB:2B:F4:47:0C'

async def connect_and_display_characteristics(address):
    client = BleakClient(address)

    try:
        await client.connect()
        device_services = await client.get_services()
        device_characteristics =device_services.characteristics
        
        for c in device_characteristics:
            print(device_services.get_characteristic(c))
            
    except Exception as e:
        print(e)
    finally:
        await client.disconnect()
        
asyncio.run(connect_and_display_characteristics(SUITO_ADDRESS))
```
As expected, I got the list of characteristics.
```
00002a00-0000-1000-8000-00805f9b34fb (Handle: 2): Device Name
00002a01-0000-1000-8000-00805f9b34fb (Handle: 4): Appearance
00002a04-0000-1000-8000-00805f9b34fb (Handle: 6): Peripheral Preferred Connection Parameters
00002aa6-0000-1000-8000-00805f9b34fb (Handle: 8): Central Address Resolution
00002a05-0000-1000-8000-00805f9b34fb (Handle: 11): Service Changed
00002a5b-0000-1000-8000-00805f9b34fb (Handle: 15): CSC Measurement
00002a5c-0000-1000-8000-00805f9b34fb (Handle: 18): CSC Feature
00002a5d-0000-1000-8000-00805f9b34fb (Handle: 20): Sensor Location
00002a63-0000-1000-8000-00805f9b34fb (Handle: 23): Cycling Power Measurement
00002a65-0000-1000-8000-00805f9b34fb (Handle: 26): Cycling Power Feature
00002a5d-0000-1000-8000-00805f9b34fb (Handle: 28): Sensor Location
00002a66-0000-1000-8000-00805f9b34fb (Handle: 30): Cycling Power Control Point
00002acc-0000-1000-8000-00805f9b34fb (Handle: 34): Fitness Machine Feature
00002ad2-0000-1000-8000-00805f9b34fb (Handle: 36): Indoor Bike Data
00002ad3-0000-1000-8000-00805f9b34fb (Handle: 39): Training Status
00002ad6-0000-1000-8000-00805f9b34fb (Handle: 42): Supported Resistance Level Range
00002ad8-0000-1000-8000-00805f9b34fb (Handle: 44): Supported Power Range
00002ada-0000-1000-8000-00805f9b34fb (Handle: 46): Fitness Machine Status
00002ad9-0000-1000-8000-00805f9b34fb (Handle: 49): Fitness Machine Control Point
347b0010-7635-408b-8918-8ff3949ce592 (Handle: 53): Unknown
347b0011-7635-408b-8918-8ff3949ce592 (Handle: 55): Unknown
347b0018-7635-408b-8918-8ff3949ce592 (Handle: 58): Unknown
347b0012-7635-408b-8918-8ff3949ce592 (Handle: 60): Unknown
347b0013-7635-408b-8918-8ff3949ce592 (Handle: 62): Unknown
347b0014-7635-408b-8918-8ff3949ce592 (Handle: 64): Unknown
347b0016-7635-408b-8918-8ff3949ce592 (Handle: 67): Unknown
347b0017-7635-408b-8918-8ff3949ce592 (Handle: 69): Unknown
347b0019-7635-408b-8918-8ff3949ce592 (Handle: 72): Unknown
00002a29-0000-1000-8000-00805f9b34fb (Handle: 75): Manufacturer Name String
00002a25-0000-1000-8000-00805f9b34fb (Handle: 77): Serial Number String
00002a27-0000-1000-8000-00805f9b34fb (Handle: 79): Hardware Revision String
00002a26-0000-1000-8000-00805f9b34fb (Handle: 81): Firmware Revision String
00002a28-0000-1000-8000-00805f9b34fb (Handle: 83): Software Revision String
8e400001-f315-4f60-9fb8-838830daea50 (Handle: 86): Experimental Buttonless DFU Service
```

### Read from a characteristics to test the connection
To ensure that everything was working I wanted to read a characteristic from the Suito device. 
I chose the Manufacturer Name String. The handle for the Manufacturer Name String is 75. This handle is passed into .read_gatt_char to identify the characteristic to be read. I printed the manufacturer name twice. Once to show the bytearray output and a second time after converting to a string. Modifying the previous code:

```
async def connect_and_display_characteristics(address):
    client = BleakClient(address) # 

    try:
        await client.connect()
        # Read the characteristic and print the result
        manufacturer = await client.read_gatt_char(75) 
        print(f"The Suito was made by:{manufacturer}")

        # use decode to convert from byte array to string
        manufacturer_string = manufacturer.decode("UTF-8")
        print(f"The Suito was made by:{manufacturer_string}")
            

    except Exception as e:
        print(e)
    finally:
        await client.disconnect()
        
asyncio.run(connect_and_display_characteristics(SUITO_ADDRESS))
```
Gave the output:
```
The Suito was made by:bytearray(b'Elite')
The Suito was made by:Elite
```

### Wrap up
Good. I was able to connect to the device and show the available characteristics. Then I read a specific value to test the connection.
Importantly, I also tool note of the integer handles used to access each characteristic namely:
(Handle: 36): Indoor Bike Data, (Handle: 46): Fitness Machine Status, and (Handle: 49): Fitness Machine Control Point.
