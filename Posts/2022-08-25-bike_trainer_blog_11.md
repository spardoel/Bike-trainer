# Developing a cycling control program for my indoor trainer (TrainerRoad clone) Part 11 - Adding a basic UI
With the 

## Adding a basic user interface
At this point the code worked. I could run a workout and log the results.Next I wanted to create a basic UI that would allow the user to view the available workouts and select one from the list. I also wanted to create a workout summary display to show duration and average power at the completion of a workout. I started with the workout summary to get it out of the way.

### Display workout summary
Basically I wanted to display a message to the user to show the duration of the workout, as well as the average power and cadence. These values are all available from the ride log table, so this method will invole writing a method to get all data from the database. 
On second thought, I wrote three separate methods one to get the timestamps, one to get the power and the other to get the cadence. Here is they are.
```
 def get_ride_duration_from_ride_log_table(self, table_name):

        cur = self.conn.cursor()

        # get list of possible workout ids
        cur.execute(f"SELECT timestamp FROM {table_name};")

        # Get the id numbers and convert to string
        results = cur.fetchall()
        # extract the list of tuples
        results_list = [x[0] for x in results]

        # return the length of the ride in minutes.
        return len(results_list) / 60

    def get_avg_power_from_ride_log_table(self, table_name):

        cur = self.conn.cursor()

        # get list of possible workout ids
        cur.execute(f"SELECT power FROM {table_name};")

        # Get the id numbers and convert to string
        results = cur.fetchall()
        # extract the list of tuples
        results_list = [x[0] for x in results]

        return mean(results_list)

    def get_avg_cadence_from_ride_log_table(self, table_name):

        cur = self.conn.cursor()

        # get list of possible workout ids
        cur.execute(f"SELECT cadence FROM {table_name};")

        # Get the id numbers and convert to string
        results = cur.fetchall()
        # extract the list of tuples
        results_list = [x[0] for x in results]

        return mean(results_list)
```
The methods are pretty basic, they query the watabase then unpack the results and return a numeric value. These methods are called within a print statement placed after the main loop in the start_workout() method.
```
# after the main loop ends, display ride values to the user
        print(
            f"Workout done! The ride was {round(self.database.get_ride_duration_from_ride_log_table(self.ride_log_table_name),2)}  minutes long with and average power of {int(self.database.get_avg_power_from_ride_log_table(self.ride_log_table_name))} Watts and average cadence of {int(self.database.get_avg_cadence_from_ride_log_table(self.ride_log_table_name))} rpm"
        )
```

### Welcome screen and workout selection
The UI interactions will need to run at the beginning of the main function. But to avoid cluttering the main I wanted to group the user interface methods together. For this purpose I created the UserInterface class.
