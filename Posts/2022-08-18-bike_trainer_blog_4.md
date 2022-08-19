# Developing a cycling control program for my indoor trainer (TrainerRoad clone) Part 4 - Device control, send and receive commands and bit twiddling
At this point I was able to connect to the device and read from specific characteristics. I also knew which characteristics were used to control the device during normal function and how the device reported its status.
In this post I will explain how I was able to send my own custom commands to adjust the bike trainer resistance (target power). 
This turned out to be more complicated than I thought and involved deciphering the packets being sent from the device. Fortunately for me, the Bluetooth specification documents are available and easy to understand (sort of).
The code for this post is Code files\Python code\send_commands_receive_callbacks.py

### Set up the callback and test the resitance control commands
First I declared the characteristic handle integers as constants.
```
# define the characteristic handles
FIT_MACHINE_CONTROL_POINT_HANDLE = 49
FIT_MACHINE_STATUS_HANDLE = 46
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

The code below show how I set up the notification/indication subscriptions and how I sent the control request command to the Fitness Machine Control Point. I also added a sleep command to give some time for the trainer to send back some data. (the trainer sends a Indoof Bike Data notification once every second) 

```
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
The next three lines of output are the Indoor Bike Data fields. Armed with the GATT Specification Supplement (https://www.bluetooth.com/specifications/specs/gatt-specification-supplement-5/), I tried to decode the data...

### Decoding the data from the trainer
The Indoor Bike Data characteristic can return a lot of different fields. As shown in the image below, the first 2 bytes contain the flags which indicate which values make up the remainder of the packet.
![indoor bike data flags](https://user-images.githubusercontent.com/102377660/185514407-6f192e40-9bbb-4aa7-9ad9-cfa506ce40c2.PNG)

I had a bit of trouble decoding the flags, but after some searching and a few helpful commentors on stackoverflow I figured it out. 
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
Ok, so the flag bytes were 84 and 8. In binary 84 is 01010100 and 8 is 00001000. Little Endian is used in this case, so the bytes needed to be reversed. Then, an index value was assigned to each bit. I illustrated the process below.
![flag decoding](https://user-images.githubusercontent.com/102377660/185516472-27255cd3-6c37-45fd-a469-b033d2af2453.png)
After decoding, I found that bits 2, 4, 6, and 11 were set to 1. 
The Indoor Bike Data documentation lists each possible field and the corresponding bit flag. Here is a sample.
![bit flag meaning indoor bike data](https://user-images.githubusercontent.com/102377660/185516903-4bbb45ba-c6ef-4a6f-ad95-2306e11fe51d.PNG)

After consulting the Indoor Bike Data documentation, the following fields are included in the data. 
Instantaneous speed (bit 0 was set to 0), instantaneous cadence (bit 2 was set to 1), total distance (bit 4 was set to 1), instantaneous power (bit 6 was set to 1) and elapsed time (bit 11 was set to 1).
The documentation also lists the size of each data field. I added up the data fields to see if they matched the 13 byte output that I received in the previous test. 
The number of bytes matched. I illustrated the decoded data here.
![decoded packet](https://user-images.githubusercontent.com/102377660/185517818-94a233e9-38be-4773-a2e0-e9111cd01f22.png)

Now it was a matter of converting the correct sections of the byte array to useful values. I wanted to get the instantaneous cadence and instantaneous power. The code below shows how I used the Struct library to unpack the byte array. Note that accodring to the Bluetooth documentation the cadence units are in 1/2 revolutions per minute (no, I don't know why either). So the value needed to be halved to get revolutions per minute. 
```
def bike_data_callback(sender: int, data: bytearray):
    print(f"Bike data {sender}: {data}")
    # unpack the 2 bytes corresponding to cadence using < for little endian and H for unsigned short
    print(f"Cadence (rpm) : {unpack('<H',data[4:6])[0] / 2}")
    # unpack the 2 bytes corresponding to power using < for little endian and h for signed short
    print(f"Power (Watts) : {unpack('<h',data[9:11])[0]}")
```
After running the code and hopping on the bike (to generate some non-zero outpus) I got the following output
```
Bike data 36: bytearray(b'T\x08\xf9\x06\x90\x00a\x00\x00{\x00\x1c\x00')
Cadence (rpm) : 72.0
Power (Watts) : 123
```
The power and cadence values seemed correct compared to how fast and how hard I was pedaling, but just to make sure the byte conversion was correct I did a short, steady workout on trainer road and recorded the packet traffic. Then, taking the Indoor Bike Data directly from the packet and converting it using the method shown above, I was able to replicate the cadence and power values that TrainerRoad was displaying. Success!

### Updating the trainer resistance and decoding the confirmation
After sending the request to control the trainer, I could then send a new target power. From observing the packet traffic I knew that there should be a response echoing the newly set target power. I updated the Fitness Machine Status callback function to display the confirmation of the newly set target power.
```
def status_callback(sender: int, data: bytearray):
    print(f"Status {sender}: {data}")
    # print the echoed new target power
    print(f"New target power (Watts) : {unpack('<h',data[1:])[0]}")
```
Now to send a new target power request. When I previously requested permission, I had to send a 1 byte command (00). But to change the target power, I needed to send 3 bytes. First the command code '05', then the new target power in signed int16 format. I tried to use the pack() method from the Struct library but I was unable to get the correct format and Fitness Machine Control Point callback was giving error responses (b'\x80\x05\x03'). In the end I opted for a slightly more cumbersom approach that worked for me. First I converted the desired target power to bytes using int.to_bytes(), then I used a byte array to combine the target power with the command code. The code looked like this
```
# Send the command code and new target power to update device resistance
new_target_power = 158
new_target_power_bytes = new_target_power.to_bytes(2, "little")
await client.write_gatt_char(
    FIT_MACHINE_CONTROL_POINT_HANDLE,
    bytearray([5, new_target_power_bytes[0], new_target_power_bytes[1]]),
    response=True,
)
```
Like I said, a bit cumbersom, but it gets the job done.
Then, after commenting out the Indoor Bike Data callback and running the code I got the following output. 
```
Control 49: bytearray(b'\x80\x00\x01')
Control 49: bytearray(b'\x80\x05\x01')
Status 46: bytearray(b'\x08\x9e\x00')
New target power (Watts) : 158 
```
The first line is the response from the Fitness Machine Control Point notification indicating that the request for control ('00') was successful ('01'). Next, is another notification from the Control Point indicating that the attempt to update the target power ('05') was successful ('01'). Then there is the printout from the Fitness Machine Status callback which shows the raw mesasge in bytes, followed by the unpacked value. The final line in the output (the unpacked value) confirms that the new target power is 158 W, exactly as intended. :)

### Wrap up
This post showed how I was able to send commands to the bike trainer to update the resistance (target power) and receive confirmation notifications. The post also showed how I decoded the Indoor Bike Data packet and extracted the instantaneous cadence and instantaneous power. 
At this point in the project I had tested all the individual commands and communication functions that I needed. Next, it was time to break out the class diagrams and start to design a useable program. 
