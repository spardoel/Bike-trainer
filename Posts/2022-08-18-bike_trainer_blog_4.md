#Developing a cycling control program for my indoor trainer (TrainerRoad clone) Part 4 - Device control, send and receive commands and bit twiddling
At this point I was able to connect to the device and read from specific characteristics. I also knew which characteristics were used to control the device during normal function and how the device reported its status.
In this post I will explain how I was able to send my own custom commands to adjust the bike trainer resistance (target power). 
This turned out to be more complicated than I thought and involved deciphering the packets being sent from the device. Fortunately for me the Bluetooth specification documents are available and easy to understand (mostly)

### Set up the callback and test the resitance control commands
First I declared the characteristic handle integers as constants.
```
# define the characteristic handles
FIT_MACHINE_CONTROL_POINT_HANDLE = 49
FIT_MACHIBE_STATUS_HANDLE = 46
INDOOR_BIKE_DATA_HANDLE = 36
```

Then I created the basic callbacks. For these first tests, simply print the received message. 

```
def control_callback(sender: int, data: bytearray):
    print(f"Control {sender}: {data}")
    
def status_callback(sender: int, data: bytearray):
    print(f"Status {sender}: {data}")

def bike_data_callback(sender: int, data: bytearray):
    print(f"Bike data {sender}: {data}")

```

Sending the command to change the resistance (target power) first requires permission to change the device settings.
I observed this in the packet traffic, and learned the details from the Fitness Machine Service Bluetooth Service Supplement (https://www.bluetooth.com/specifications/specs/fitness-machine-service-1-0/).
According to the documentation, to change the trainer resistance I first needed to send the '00' operation code to request permission.
![fit machine control point docs initiate](https://user-images.githubusercontent.com/102377660/185512466-a56b7392-a31e-4bc0-97b2-b845f12dd129.PNG)
(the M requirement indicates that a notification subscription must be set up prior to commands being sent).
Then, to change the trainer resistance the code is '05' followed by the new target power. 
![fit machine send command doc](https://user-images.githubusercontent.com/102377660/185513023-60261403-56ff-415a-bda4-0a3db659564a.PNG)

Setting up the notification/indication subscriptions and sending the control request command to the Fitness Machine Control Point. I also added a  sleep command to give some time for the trainer to send back some data (it sends a notification once per second)
```
async def main(address):
    client = BleakClient(address)
    
    try:
        await client.connect()

        # Subscribe to the Indoor Bike Data characteristic
        await client.start_notify(INDOOR_BIKE_DATA_HANDLE, bike_data_callback)
        
         # Subscribe to the Fitness Machine Status characteristic
        await client.start_notify(FIT_MACHIBE_STATUS_HANDLE, status_callback)

         # Subscribe to the Fitness Machine Controll Point characteristic
        await client.start_notify(FIT_MACHINE_CONTROL_POINT_HANDLE, control_callback) 
        
        # Send the command to request control of the device. (convert to bytes first)
        await client.write_gatt_char(FIT_MACHINE_CONTROL_POINT_HANDLE,bytes([00]),response=True)
        
        time.sleep(3)
        
    except Exception as e:
        print(e)
    finally:
        await client.disconnect()

asyncio.run(main(SUITO_ADDRESS))
```
After running this code, I got the following output:
```
Control 49: bytearray(b'\x80\x00\x01')
Bike data 36: bytearray(b'T\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\xb6\x00')
Bike data 36: bytearray(b'T\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\xb7\x00')
Bike data 36: bytearray(b'T\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\xb8\x00')
```
The Control message contains the '80' response I was looking for followed by '01' indicating success, i.e., control was granted and now commands to change the resistance can be sent.
The next three lines of output are the Indoor Bike Data fields. From the GATT Specification Supplement (https://www.bluetooth.com/specifications/specs/gatt-specification-supplement-5/), I tried to decode the data...

### Decoding the data from the trainer
The Indoor Bike Data characteristic can return a lot of different fields. As shown in the image below, the first 2 bytes contain the flags which indicate which values make up the remainder of the packet.
![indoor bike data flags](https://user-images.githubusercontent.com/102377660/185514407-6f192e40-9bbb-4aa7-9ad9-cfa506ce40c2.PNG)

I had a bit of trouble decoding the flags, but after some searching and a few helpful commentors on stackexchange I figured it out. 
The first step is to get the two flag bytes and convert them to binary. 
I updated the Indoor Bike Data callback to unpack the first 2 bytes using the struct library. 
```
def bike_data_callback(sender: int, data: bytearray):
    print(f"Bike data {sender}: {data}")
    print(unpack('bb',data[0:2]))
```
Which returned the following
```
Bike data 36: bytearray(b'T\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc1\x04')
(84, 8)
```
Ok, so the flag bytes are 84 and 8. In binary 84 is 01010100 and 8 is 00001000. Little Endian is used in this case, so the bytes need to be reversed. Then assign an index value fo each bit. I ilustrated the process below.
![flag decoding](https://user-images.githubusercontent.com/102377660/185516472-27255cd3-6c37-45fd-a469-b033d2af2453.png)
After decoding, bits 2, 4, 6, and 11 are set to 1. 
The Indoor Bike DAta documentation lists each possible field and the corresponding bit flag. Here is a sample.
![bit flag meaning indoor bike data](https://user-images.githubusercontent.com/102377660/185516903-4bbb45ba-c6ef-4a6f-ad95-2306e11fe51d.PNG)

After consulting the Indoor Bike Data documentation, the following fields are included in the data. 
Instantaneous speed (bit 0 was set to 0), instantaneous cadence (bit 2 was set to 1), total distance (bit 4 was set to 1), instantaneous power (bit 6 was set to 1) and elapsed time (bit 11 was set to 1).
The documentation also lists the size of each data field. I added up the data fields to see if they matched the 13 byte output that I received in the previous test. 
The number of bytes matched. I illustrated the decoded data here.
![decoded packet](https://user-images.githubusercontent.com/102377660/185517818-94a233e9-38be-4773-a2e0-e9111cd01f22.png)


