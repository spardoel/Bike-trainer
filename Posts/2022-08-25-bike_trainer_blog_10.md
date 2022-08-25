# Developing a cycling control program for my indoor trainer (TrainerRoad clone) Part 10 - Testing and debugging

In the last post I implemented the start_workout() method but hadn't tested it. 
Well after running the code I am pleased to annouce that there were zero bugs or unintented behaviours and everything was perfect. Obviously I am joking, there were some bugs... There were a few typos and very minor bugs that I won't mention. But two bugs were worth noting. 

## Bug 1, forgetting to scale target power and convert to integer before sending to trainer
As the title says, when I first implemented the code I was sending new target power values to the trainer in the decimal format used in the database. I had forgotten to multiply the fractional power number by the rider's ftp. After doing that I cast the value to int before sending to the trainer characteristic. 
The fix looked like this.
```
# Before
await self.trainer.set_trainer_resistance(
  self.power_profile[self.workout_index]
 )
# After
await self.trainer.set_trainer_resistance(
  int(self.power_profile[self.workout_index] * self.ftp)
 )
```
This allowed the trainer resistance to be updated as intended. 

## Bug 2, searching the ride_log table by date
This bug was obvious once pointed out but for some reason I didn't see it coming. That is just how it goes with bugs I suppose. 
When updating the ride_logs table to add a new row, I would then use the current date to search the ride logs and retreive the most recent log (the one from today). However I overlooked the fact that there could be several rides logged in a single day. For example by someone testing the code and running it multiple times... 
Since I defined the ride_id using the Serial command, the newest entry should have the highest id value. So to solve this bug, I added 'ORDER BY ride_id DESC' to the SQL query that retrives the ID. Now the query will return the most recently created row on a given day.
```
# Before
cur.execute(f"SELECT ride_id FROM ride_logs WHERE ride_date = '{todays_date}';")

# Get the id number and convert to string
ride_id = str(cur.fetchone()[0])

# After
cur.execute(f"SELECT ride_id FROM ride_logs WHERE ride_date = '{todays_date}' ORDER BY ride_id DESC;")

# Get the id number and convert to string
ride_id = str(cur.fetchone()[0])
```

## Running the debugged code
After I finished debugging, I added a print statement to show the rider the elepased time, the target power and the current power. Then I hopped on the bike to give it a try. This was the output.
```
Trainer connected.
The Suito was made by:Elite
Workout: Fast and steady was loaded. Ready to start.
here we go...
Trainer control requested
Elapsed time: 2623, target power: 189, rider power: 0
Elapsed time: 2624, target power: 189, rider power: 0
Elapsed time: 2625, target power: 189, rider power: 17
Elapsed time: 2626, target power: 189, rider power: 17
Elapsed time: 2627, target power: 189, rider power: 117
Elapsed time: 2628, target power: 189, rider power: 117
Elapsed time: 2629, target power: 189, rider power: 153
Elapsed time: 2630, target power: 189, rider power: 153
```
Hey, alright! It worked. Well... maybe not. As I was attempting to pedal I noticed that the actual trainer resistance was MUCH higher than 189 Watts. At that point I had 2 ideas about what might be causing it. 1. Maybe there is another bug in the code that results in the incorrect resistance being sent to the trainer (or there is a disconnect between the difficulty sent to the trainer and the one displayed to the user). or, 2. The trainer resistance was being updated too often and it's internal contorl systems never got a chanceo to react. I have noticed this when using the trainer normally, i.e., when controlled by a real cycling app. After a change in resistance, the resistance felt by the user will fluctuate a bit before settling around the correct value.
Alright, with those ideas in mind, I tried to track down my problem. Once again, I looked to the packet sniffer. 
### Wireshark output
I a Wireshark and ran the program. Here is a screenshot of the output.
![sniffer screen grab 3](https://user-images.githubusercontent.com/102377660/186744090-dfe9b877-9c2d-4a2e-9e70-4131ebf7dedc.PNG)

To me the problem was immediately obvious. The workout profile I selected was just a steady difficulty. Yet the sniffer output showed a lot of traffic using the Control Point characteristic... To investigate further I selected one of the Fitness Machine Status notifications. This confirmed that the trainer resistance was set to 189 W. Ok, so my 2nd guess was probably the problem. The program is sending commands to update the resistance too often and the trainer doesn't have time to zero in on the correct resistance. With that in mind, I went to the section of code that updated the trainer resistance. 
Here is the code. 
```
 # new data is available.
                # Check if new target power needs to be set
                if self.power_profile[self.workout_index] != self.current_target_power:
                    await self.trainer.set_trainer_resistance(
                        int(self.power_profile[self.workout_index] * self.ftp)
                    )
                    # update the current power
                    self.current_target_power = int(
                        self.power_profile[self.workout_index] * self.ftp
                    )
```
Do you see the problem? This one is a bit embarassing. It is my old friend Bug # 1 from above... the if statement used to check if the resistance needed to be updated was comparing the fractional value to the power after being multiplied by the rider's ftp and cast to an integer. Of course the condition would always be true because target_power is never equal to target_power * ftp. 
To stop this sort of thing from happening again, I created a variable to store the converted power value and used this in the other method calls. 
```
                self.next_target_power = int(self.power_profile[self.workout_index] * self.ftp)

                if self.next_target_power != self.current_target_power:
                    await self.trainer.set_trainer_resistance(self.next_target_power)
                    # update the current power
                    self.current_target_power = self.next_target_power
```
After running this code things were better. The trainer resistance still felt much to hard, but it settled after a few seconds and then felt about right. 

### check the database
To make sure that the data was being logged correctly I checked the database. First the ride_logs table. 
```
bike_workouts=# SELECT * FROM ride_logs;
 ride_id | template_id | athlete_id | ride_date
---------+-------------+------------+------------
      21 |          10 |          1 | 2022-08-25
      22 |          10 |          1 | 2022-08-25
      23 |          10 |          1 | 2022-08-25
      24 |          10 |          1 | 2022-08-25
      25 |          10 |          1 | 2022-08-25
      26 |          10 |          1 | 2022-08-25
      27 |          10 |          1 | 2022-08-25
      28 |          10 |          1 | 2022-08-25
```
As you can see the entries are being logged correctly. Now, what about the ride log tables? 
Using the most recent rider_id, value, we are looking for a table names ride028. Here is what I got when I querried.
```

bike_workouts=# SELECT * FROM ride028;
 timestamp | power | cadence
-----------+-------+---------
         1 |    52 |      10
         2 |    52 |      10
         3 |   118 |      20
         4 |   118 |      20
         5 |   118 |      20
         6 |   107 |      18
         7 |   107 |      18
         8 |   107 |      18
         9 |   107 |      18
        10 |   107 |      18
        11 |   112 |      22
        12 |   112 |      22
        13 |   147 |      21
        14 |   147 |      21
        15 |   224 |      30
        16 |   231 |      41
        17 |   230 |      46
        18 |   203 |      48
        19 |   203 |      48
        20 |   148 |      48
        21 |   203 |      47
        22 |   248 |      49
        23 |   249 |      52
        24 |   224 |      58
        25 |   205 |      60
        26 |   200 |      62
        27 |   189 |      63
        28 |   199 |      64
        29 |   192 |      65
        30 |   172 |      65
        31 |   177 |      66
        32 |   199 |      66
        33 |   167 |      66
        34 |   155 |      64
        35 |   155 |      64
        36 |   155 |      64
        37 |   155 |      64
        38 |   155 |      64
        39 |     0 |       0
        40 |     0 |       0
        41 |     0 |       0
        42 |     0 |       0
        43 |     0 |       0
        44 |     0 |       0
        45 |     0 |       0
        46 |     0 |       0
        47 |     0 |       0
        48 |     0 |       0
        49 |     0 |       0
        50 |     0 |       0
```
Great! You can see that the results were logged. I took a minute to see if the data made sense. The first column is the timestamp and increases by 1 every row. Looks good. Next is the power that I produced. The power started lower than the target of 189 then qucikly shot up past the target before coming back down. This makes sense considering how the trainer modulates the resistance above and below the target value before settling. Finally, there is the cadence which sarted slow before increasing to around 65 rpm. This makes sense. At time 39 both the cadence and power drop to zero and about 10 seconds later the log stops, this matches me climbing off the bike and stopping the program manually. 
Ok, so great, it's working!

## Wrap up
This short post describes some of the bugs I encountered when trying to run the start_workout() method. It also verified that the rides are being logged correctly. 

