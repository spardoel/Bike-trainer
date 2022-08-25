# Developing a cycling control program for my indoor trainer (TrainerRoad clone) Part 9 - Setting up the start_workout() method 
In this post I want to talk about the main loop that runs within the start_workout() method of the WorloutpPlayer class. In the last post I set up the data callback to feed data into the loop as it becomes available. So let's jump into the loop. 

## The start_workout() method
The start workout method has a lot going on. It needs to get data from the trainer, update the ride_log table, tell the trainer to change the resistance when necessary, and keep track of a multiple possible break conditions.
Since this loop will run indefinitely, the first thing I set up were stopping conditions. 

### Stopping conditions 1
The first stopping condition is the Escape key. I wanted to be able to break the loop by pressing escape. This was mainly a developpment and debugging tool for myself. 
Here is the start_workout() method with the basic loop and the first exit condition. 
```
async def start_workout(self):
        logging.info("Starting workout")
        print("here we go... ")

        # Subscribe to the BLE characteristics to start getting data from the trainer
        await self.trainer.sub_to_trainer_characteristics()

        # Start the main loop that runs during the ride
        while True:
            await asyncio.sleep(0.1)
            # check if new data has arrived

            print(self.trainer.elapsed_time_sec)

            # end the loop with the possible exit conditions
            if keyboard.is_pressed("Esc"):
                break
```
After the call to trainer.sub_to_trainer_characteristics() (explained in the previous post), I started and infinite loop. The if statement at the bottom of the loop checks to see if the user has pressed the escape key. If they have, the loop breaks. Easy. 

### Stopping condition 2
I also wanted a timeout. If the trainer stopped sending data for some reason (say if it were accidentally unpplugged while rushing back to the bike after grabbing a snack), I wanted the code to notice the absence of new data and stop the loop. 
For this, I used the elapsed time data sent by the trainer and a pre-determined maximum timeout (NO_NEW_DATA_TIMEOUT = 10 seconds). Basically, everytime the loop runs it checks the value of the trainer_interface.elapsed_time_sec property. If a new data packet has been received since the last time the loop ran, this value will have changed. To keep track of the previous time I used a variable called time_of_last_update and a simple if statement. Like this
```
 while True:
            await asyncio.sleep(0.1)
            
            # check if new data has arrived
            print(self.trainer.elapsed_time_sec)
            if self.trainer.elapsed_time_sec > self.time_of_last_update:
                # if the trainer has a larger number, then new data has been received.
                # update the time_stamp and reset the timeout timer
                self.time_of_last_update = self.trainer.elapsed_time_sec
                self.timeout_timer = []

```
As you can see, if the trainer_elapsed_time_sec value is higher than time_of_last_update, then a new data packet has been received. In this case, time_of_last_update is set to the most recent elapsed time value and the timeout_timer is set to an empty list. 
Speaking of the timeout timer... 
If the elapsed_timed_sec is NOT larger than time_of_last_update, then no new data has been recieved. 
In this case, check to see if the timeout_timer has a value. If not, then start the timer by using time.time(). I did this using an else if statement. Like this. 
```
            if self.trainer.elapsed_time_sec > self.time_of_last_update:
                # if the trainer has a larger number then new data has been received.
                # update the time_stamp and reset the timeout timer
                self.time_of_last_update = self.trainer.elapsed_time_sec
                self.timeout_timer = []

                # Do a bunch of cool things..

            elif not self.timeout_timer:
                # if the timer is not running, start it
                self.timeout_timer = time.time()

```
Now, what if there has been no new data since the last loop but the timer has already been started? Well, in this case, check to see how long ago the timer was started. If the timer was started more that the allowable time ago, log the timeout event and break the loop. I did this using a second else if statement. 
```
NO_NEW_DATA_TIMEOUT = 10

 if self.trainer.elapsed_time_sec > self.time_of_last_update:
                # if the trainer has a larger number then new data has been received.
                # update the time_stamp and reset the timeout timer
                self.time_of_last_update = self.trainer.elapsed_time_sec
                self.timeout_timer = []

                # Do a bunch of cool things..

            elif not self.timeout_timer:
                # if the timer is not running, start it
                self.timeout_timer = time.time()

            elif (time.time() - self.timeout_timer) > NO_NEW_DATA_TIMEOUT:
                # if the timer has been running longer than the timeout duration, break the loop
                logging.debug(
                    f"The no new data timeout of {NO_NEW_DATA_TIMEOUT} seconds was reached."
                )
                print("Timeout reached")
                break
```
Alright, so I had 2 ways of exiting the infinite loop. Either the user pressed escape, or the trainer timed out without sending new data. There will also be a third way the loop exits (when the workout is completed normally) but that will be added later. 
Next, let's look at what happens when there is new data from the trainer. As alluded to by the very helpful comments in the code, 'a bunch of cool things' happen. 

## Setting the trainer resistance 
During the initial testing, I learned that in order to change the resistance level of the trainer, I first needed to request control. So I coded that next. 

### Request trainer control
To request control of the trainer resistance, I needed to send the command '00' to the Fitness Machine Control Point characteristic. To do this, I created the confusingly named request_trainer_control() method in the TrainerInterface class.
The method looked like this.
```
    async def request_trainer_control(self):

        # Send the command to request control of the device. (convert to bytes first)
        await self.client.write_gatt_char(
            FIT_MACHINE_CONTROL_POINT_HANDLE, bytes([00]), response=True
        )

```
As you can see, the method is pretty simple. It converts '00' to bytes then writes the result to the control point characteristic.
Next I added the call to this new method to the start_workout() method before the main loop.
```
 await self.trainer.request_trainer_control()
 
  while True:
            await asyncio.sleep(0.1)
            # check if new data has arrived

            print(self.trainer.elapsed_time_sec)

    ...
    ...
    ...
    
            # end the loop with the possible exit conditions
            if keyboard.is_pressed("Esc"):
                break

```
When this code was run I got the following output.
```
bytearray(b'T\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
0
0
0
0
0
0
0
0
bytearray(b'T\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00')
1
1
1
1
1
1
1
1
1
bytearray(b'T\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00')
2
2
2
2
```
As you can see, the output is the Indoor Bike Data printed by the callback. Between the byte array outputs is the elapsed time value printed from within the main start_workout() loop. I was pleased to see the elapsed time incrementing by one second every time the trainer sent new data. As I suspected, requesting control of the resistance started the 'elepased_time' counter on the trainer. Don't you just love it when problems solve themselves?

### Update trainer resistance
Similar to the request_trainer_control() method, the set_trainer_resistance() method also used the control point characteristic on the trainer. Howerver, this method accepts the new desired power value as an input parameter and converts the value to a byte array before sending. Like this. 
```
    async def set_trainer_resistance(self,new_power):

        new_target_power_bytes = new_power.to_bytes(2, "little")
        await self.client.write_gatt_char(
            FIT_MACHINE_CONTROL_POINT_HANDLE,
            bytearray([5, new_target_power_bytes[0], new_target_power_bytes[1]]),
            response=True,
        )
```
Now, converting the new power to bytes then using indexes to access the first and second bytes probably isn't the most optimal solution. But to be honest, I was having issues generating the byte array format the trainer was looking for when using pack() from the struct library. I think the solution shown in the code above is reliable and easy to read so I am happy to leave it and move on.  

### A few housekeeping changes 
Just in case something goes wrong down the line, I added some log file entries to request_trainer_control() and set_trainer_resistance() methods. The automatic responses from the control point characteristic are already always logged through the control_callback() method. Now, the request to change the resistance will be logged as well. This might be helpful down the line if things go wrong... (I hope it won't be necessary)

## Checking the power profile and adjusting the trainer difficulty
During the creation of the WorkoutPlayer class object, the init method calls the DatabaseHandler.get_power_profile() method. This means that the workout template power profile is already available as a property within the start_workout() method. At 1 second intervals the 





