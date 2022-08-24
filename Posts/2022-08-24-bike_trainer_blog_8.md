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
