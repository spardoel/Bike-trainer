# Developing a cycling control program for my indoor trainer (TrainerRoad clone) Part 7 - Setting up bluetooth callbacks and the WorkoutPlayer class

Oh boy. This part was tricky. The bluetooth commands used to communicate with the trainer need to be done asynchronously, which took me a few tries to get right. I'll try to describe the issues I had and my thought process along the way. 
But to be honest, I mostly got it working through educated guesses and trial and error. Which as we all know, is the gold standard in coding. 

## The WorkoutPlayer class
At first my idea was to have a method within the workout player that would subscribe to the trainer's ble characteristics and update the trainer resistance and log table everytime new data was sent from the trainer. 
To do this, I create a sub_to_trainer_characteristics() method to subscribe to the ble characteristics and set up the callbacks. The method was inside the TrainerInterface class and looks like this:
```
    async def sub_to_trainer_characteristics(self):
        try:
            # Subscribe to the Indoor Bike Data characteristic
            # in odrer to send additiona input arguments to the callback, need to use partial.
            # bike_data_callback_class = BIkeDataCallbackClass
            await self.client.start_notify(INDOOR_BIKE_DATA_HANDLE, bike_data_callback)

            # Subscribe to the Fitness Machine Status characteristic
            await self.client.start_notify(FIT_MACHINE_STATUS_HANDLE, status_callback)

            # Subscribe to the Fitness Machine Controll Point characteristic
            await self.client.start_notify(
                FIT_MACHINE_CONTROL_POINT_HANDLE, control_callback
            )

        except:
            logging.warning("Could not start the trainer data stream.")
```
As in the initial tests, when subscribing to the characteristics 'await' needs to be used. This means that the function must be asynchronous, hence the async keyword before the method name in the definition. 
To run the sub_to_trainer_characteristics() method, I first tried to use the asyncio.run() command. Like this.

![run workout diagram 1](https://user-images.githubusercontent.com/102377660/186532220-50df9050-621e-406a-9277-5939024dae0f.png)

The above diagram is meant to show that the start_workout() method was called normally, and the sub_to_trainer_characteristics method was called using asyncio.run().
Once this was run I was greeted by an error message that kept running at approximately 1 second intervals. I know that the trainer updates its status every 1 second so it seems like there is something wrong with the callback. Here is the error message.
```
RuntimeError: Event loop is closed
Exception ignored in: <function bike_data_callback at 0x0000020B53FB12D0>
Traceback (most recent call last):
  File "c:\Users\scott\OneDrive\Desktop\Suito_ble\Bike_trainer_project\Code files\.venv\lib\site-packages\bleak\backends\winrt\client.py", line 822, in notification_parser
    return loop.call_soon_threadsafe(func, sender.attribute_handle, value)
  File "C:\Users\scott\AppData\Local\Programs\Python\Python310\lib\asyncio\base_events.py", line 795, in call_soon_threadsafe
    self._check_closed()
  File "C:\Users\scott\AppData\Local\Programs\Python\Python310\lib\asyncio\base_events.py", line 515, in _check_closed
    raise RuntimeError('Event loop is closed')
```
Right. So from the error message I could see that the bike_data_callback was encountering problems because the Event loop was closed. After some ready, I learned that the asyncio.run() command opens and closes an event loop. 
So my understanding of the situation is that the subscriptions were created inside the asynchronous loop which then closed after the method finished running. Then when the trainer send back data the subcription callbacks were not awaited properly. 
To be honest I don't fully grasp the intricacies of the problem, but I knew that the asyncio.run() command opened and closed a loop. So if I put the entire start_workout() method inside this loop then the subcriptions should remain valid.
So I called the start_workout() method using asyncio.run(), and made the method itself async so that the sub_to_trainer_characteristic() could be awaited.
Here is an updated diagram.
![run workout diagram 2](https://user-images.githubusercontent.com/102377660/186533645-44df2d62-1bd9-42d1-8d7d-08e552ed64de.png)

When I ran the code I got an error message indicating that the bluetooth device could not be found. Apparently I took to long between connection attempts and the trainer turned itself off. So after standing up, unplugging the trainer and pluggin it back in, I ran the code again.
And got nothing. The code ran, but the callback, which was supposed to print the bike data to the terminal did not work. At this point I thought maybe the subscription wasn't being sent to the trainer. So I opened the packet sniffer and ran the code again.

![sniffer screen grab 2](https://user-images.githubusercontent.com/102377660/186534758-6f4c583c-4258-4d00-8f38-eb023ab144f6.PNG)

As you can seen from the WireShark screen shot, the trainer was indeed sending a packet to the 'indoor bike data' characteristic every second.

## The sub_to_trainer_characteristics() method and callbacks
Ok, so the trainer side of things was working, but my callback wasn't. So I took a closer look at the subscription method and the callbacks.
Here is the code.
```
async def sub_to_trainer_characteristics(self):
        try:
            # Subscribe to the Indoor Bike Data characteristic
            # in odrer to send additiona input arguments to the callback, need to use partial.
            # bike_data_callback_class = BIkeDataCallbackClass
            await self.client.start_notify(
                INDOOR_BIKE_DATA_HANDLE, self.bike_data_callback
            )

            # Subscribe to the Fitness Machine Status characteristic
            await self.client.start_notify(
                FIT_MACHINE_STATUS_HANDLE, self.status_callback
            )

            # Subscribe to the Fitness Machine Controll Point characteristic
            await self.client.start_notify(
                FIT_MACHINE_CONTROL_POINT_HANDLE, self.control_callback
            )

        except:
            logging.warning("Could not start the trainer data stream.")

    def control_callback(sender: int, data: bytearray):
        # Unpack the message and log it if there is a problem (result code 1 is normal)
        result_code = unpack("<b", data[2:3])[0]
        if result_code != 1:
            logging.debug("Control point response received. {result_code}")

    def status_callback(sender: int, data: bytearray):
        # get the current resistance level of the trainer
        trainer_resistance_watts = unpack("<h", data[1:])[0]

    def bike_data_callback(sender: int, data: bytearray):
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
```
As you can see, the sub_to_trainer_characteristics() method subscribes to each of the three characteristics in turn. The callbacks are also methods of the TrainerInterface class. I thought that if the perhaps the callbacks themselves also needed to be asynchronous, so I added the async keyword to the callback definitions but that didn't help. My next idea was to move the callback outside the TrainerInterface class. This is how I had set up the callbacks in the initial tests and that had worked. So I moved the callbacks out of the class and defined them as separate functions. After running the code I got the following. 
```
bytearray(b'T\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
Elapsed time is: 0
bytearray(b'T\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
Elapsed time is: 0
bytearray(b'T\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
Elapsed time is: 0
bytearray(b'T\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
Elapsed time is: 0
bytearray(b'T\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
Elapsed time is: 0
bytearray(b'T\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
Elapsed time is: 0
```
Great! The callback is working and printing the packet bytes to the terminal once per second. I noticed that the elapsed time was not increasing... Maybe that was because no resistance was set on the trainer, so the trainer hadn't started counting? I don't know. I took not of that and left it for future me to deal with. 

Now the callback was getting called. Good. But I didn't like the idea of having three callback functions floating arround. I created a TrainerCallbacks class and made the callbacks methods, like this. 
```

class TrainerCallbacks:
    def control_callback(sender: int, data: bytearray):
        # Unpack the message and log it if there is a problem (result code 1 is normal)
        result_code = unpack("<b", data[2:3])[0]
        if result_code != 1:
            logging.debug("Control point response received. {result_code}")

    def status_callback(sender: int, data: bytearray):
        # get the current resistance level of the trainer
        trainer_resistance_watts = unpack("<h", data[1:])[0]

    def bike_data_callback(sender: int, data: bytearray):
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
```
Then I instantiated the TrainerCallbacks class within the sub_to_trainer_characteristics() method. I wanted to check a hunch. Sure enough, the callbacks didn't work. I then moved the TrainerCallbacks class instantiation to the TrainerInterface init method and set the instance of TrainerCallbacks as a property of TrainerInterface. That also didn't work. (not surprising). So it seemed to me that methods associated with the TrainerInterface class didn't work. Instead, what if I passed in the callbacks class as an input to the sub_to_trainer_characteristics() method? so I tried this.
```
    async def start_workout(self):  # add async
        logging.info("Starting workout")
        print("here we go... ")

        trainer_callbacks = TrainerCallbacks()
        
        # Subscribe to the BLE characteristics to start getting data from the trainer
        await self.trainer.sub_to_trainer_characteristics(trainer_callbacks)
```
This also didn't work. So perhaps the issue is that the callbacks are created within the asyncio.run() event loop. What if I instantiated the callbacks in the main function then passed them to the WorkoutPlayer, which passed them to the sub_to_trainer_characteristics() method. Aaaannnnddd nothing. Crap. Ok so moving the grouping the callbacks into a class and passing the class into the subscription function wasn't working. So I went back to the last function state and tried a different approach.
### Callbacks take two
The callbacks were working when they were defined as individual functions in the same file as the TrainerInterface. So I went back to that point. After running the code it still worked (phew). Once of the reasons I wanted to group the callbacks into classes was that to facilitate pulling data out of them. So instead of putting the callback in a class what if I passed a class in as an additional input argument and saved the data in the callback that way. 
According to the bleak documentaion the way to do this was using 'partial'. Like this
```
from functools import partial 

await self.client.start_notify(INDOOR_BIKE_DATA_HANDLE, partial(bike_data_callback, self))

def bike_data_callback(trainer_interface_instance: TrainerInterface, sender: int, data: bytearray):
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
    print(trainer_interface_instance.elapsed_time_sec)
```
The above code block shows the 'partial' import, the use of partial in the subscription call and the modified callback function that now accepts the instance of the TrainerInterface class as an input argument. 
After running this code I got the following 
```
bytearray(b'T\x08\x00\x00\x00\x00-\x00\x00\x00\x00\x00\x00')
Elapsed time is: 0
0
bytearray(b'T\x08\x00\x00\x00\x00-\x00\x00\x00\x00\x00\x00')
Elapsed time is: 0
0
```
Alright, so this was working. Good. The elapsed time was still 0 but that it a problem for later. 
Next I wanted to see access the elapsed_time_sec property from within the WorkoutPlayer. As it turns out, elapsed_time_sec is a property of trainer_interface which is a property of the workoutPlayer instance so accessing it from within the start_workout() method was no problem. 

```
async def start_workout(self):  # add async
        logging.info("Starting workout")
        print("here we go... ")


        # Subscribe to the BLE characteristics to start getting data from the trainer
        await self.trainer.sub_to_trainer_characteristics()

        # Start the main loop that runs during the ride
        while True:
            await asyncio.sleep(0.1)
            # check if new data has arrived
            print(self.trainer.elapsed_time_sec)
```
Running the above code produced the following. 
```
bytearray(b'T\x08\x00\x00\x00\x00-\x00\x00\x00\x00\x00\x00')
0
0
0
0
0
0
0
0
0
```
Perfect. This seems like a good place to stop for now. 

## Wrap up
In this post I grappled with the asyncio library. After some confusion and serveral rounds of trial and error, I got it working. 
I had the trainer data callback set up and feeding data (for now just the elapsed time) into the main loop of the start_workout() method. Time for a quick git commit to save this version of code before I break something... 
