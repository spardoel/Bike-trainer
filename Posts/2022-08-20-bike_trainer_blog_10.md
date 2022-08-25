# Developing a cycling control program for my indoor trainer (TrainerRoad clone) Part 10 - Testing and basic UI 

In the last post I implemented the start_workout() method but hadn't tested it. 
Well after running the code I am pleased to annouce that there were zero bugs or unintented behaviours and everything was perfect. Obviously I am joking, there were some bugs...

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


