# Developing a cycling control program for my indoor trainer (TrainerRoad clone) Part 11 - Adding a basic UI
With the basic functionality testing done, I next added a way for a user to interact with the program.

## Adding a basic user interface
At this point the code worked. I could run a workout and log the results. Next I wanted to create a basic UI that would allow the user to view the available workouts and select one from the list. I also wanted to create a workout summary display to show duration and average power at the completion of a workout. I started with the workout summary to get it out of the way.

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
## the UserInterface class

The UI interactions will need to run at the beginning of the main function. But to avoid cluttering the main I wanted to group the user interface methods together. For this purpose I created the UserInterface class.
The class had the following methods
display_welcome_message()
display_end_message()
display_available_workouts()

### Welcome screen and workout selection
The welcome method pretty much does what the title implies. It displays a welcome message to the user and invited them to choose one of the available options.
```
 def display_welcome_message(self):

        print(
            "Welcome to my TrainerRoad clone! \nPlease choose one of the following options: \n\nTo display the available workouts, press '1' \nTo exit, press '2'"
        )

        # then wait for the user's input
        user_input = input()

        if user_input == "1":
            self.display_available_workouts()
            return self.selected_workout

        elif user_input == "2":
            self.display_end_message()
            return
        else:
            print("Invalid input. Try again.\n")
            time.sleep(2)
            self.display_welcome_message()
```
This method dispalys a welcome message and promtps the user to pres either 1 or 2. The coe then checks the input and runs the appropriate methods, in this case either the display_available_workouts() method or the display_welcome_message() method.
```
    def display_end_message(self):
        print("Program terminated. See you next time!")
        exit()
```
The display_end_message() method simply displays a message to the user and terminates the program.
```
    def display_available_workouts(self):

        # get the available workouts from the database
        valid_ids = self.database.print_available_workouts()

        print("Enter the database id numer to select it.\n To exit, press 'E'")

        user_input = input()

        if user_input in valid_ids:
            self.selected_workout = user_input

        elif user_input == "e" or user_input == "E":
            self.display_end_message()

        else:
            print("Invalid input. Please try again.")
            self.display_available_workouts()
```
The display_available_workouts() method is a little more interesting. First it calls a DatabaseHandler method that prints the available workouts for the user and returns the list of available workout ids. Then the method accepts the user input and either selects the corresponding workout, asks the user to try again if the input is invalid, or exits the program. Next lets look at the DatabaseHandler.print_available_workouts() method. 

### The DatabaseHandler print_available_workouts() method
This method accesses the database and returns all the data from the workout_templates table. It prints the data to the user and then executes a second query to retrive the workout template ids which are then returned to the UserInterface intance. 
```
def print_available_workouts(self):
        # create a cursor
        cur = self.conn.cursor()
        # get the data from
        cur.execute(f"SELECT * FROM workout_templates ORDER BY template_id;")
        # retrieve the response
        available_workouts = cur.fetchall()

        # print the header
        print("Workout Id,  Workout name,   Duration (min),    Difficulty")

        for row in available_workouts:
            print(f"{row[0]}           {row[1]}       {row[2]}             {row[3]} ")

        # execute a statement
        cur.execute(f"SELECT template_id FROM workout_templates ORDER BY template_id;")
        # retrieve the response
        valid_ids = cur.fetchall()
        # return a list of valid ids
        return [str(x[0]) for x in valid_ids]
```

And really that's about it. 
Here is an example of the program being run. 
```
Welcome to my TrainerRoad clone! 
Please choose one of the following options:

To display the available workouts, press '1'
To exit, press '2'
1
Workout Id,  Workout name,   Duration (min),    Difficulty
1           Slow and steady       15             Easy
10           Fast and steady       30             Medium
12           test workout       1             Easy
Enter the database id numer to select it.
 To exit, press 'E'
12
Trainer connected.
The Suito was made by:Elite
Workout: test workout was loaded. Ready to start.
here we go...
Trainer control requested
Elapsed time: 204, target power: 94, rider power: 0
Elapsed time: 205, target power: 94, rider power: 0
Elapsed time: 206, target power: 94, rider power: 90
Elapsed time: 207, target power: 94, rider power: 90
Elapsed time: 208, target power: 94, rider power: 15
Elapsed time: 209, target power: 94, rider power: 15
Elapsed time: 210, target power: 94, rider power: 124
Elapsed time: 211, target power: 94, rider power: 124
Elapsed time: 212, target power: 94, rider power: 159
Elapsed time: 213, target power: 94, rider power: 149
Elapsed time: 214, target power: 94, rider power: 149
Elapsed time: 215, target power: 94, rider power: 130
Elapsed time: 216, target power: 94, rider power: 125
Elapsed time: 217, target power: 94, rider power: 113
Elapsed time: 218, target power: 94, rider power: 115
Elapsed time: 219, target power: 94, rider power: 115
Elapsed time: 220, target power: 94, rider power: 101
Elapsed time: 221, target power: 94, rider power: 102
Elapsed time: 222, target power: 94, rider power: 96
Elapsed time: 223, target power: 94, rider power: 99
Elapsed time: 224, target power: 94, rider power: 97
Elapsed time: 225, target power: 94, rider power: 98
Elapsed time: 226, target power: 94, rider power: 101
Elapsed time: 227, target power: 94, rider power: 96
Elapsed time: 228, target power: 94, rider power: 88
Elapsed time: 229, target power: 94, rider power: 85
Elapsed time: 230, target power: 94, rider power: 84
Elapsed time: 231, target power: 94, rider power: 89
Elapsed time: 232, target power: 94, rider power: 96
Elapsed time: 233, target power: 94, rider power: 99
Elapsed time: 234, target power: 94, rider power: 94
Elapsed time: 235, target power: 94, rider power: 96
Elapsed time: 236, target power: 94, rider power: 91
Elapsed time: 237, target power: 94, rider power: 88
Elapsed time: 238, target power: 94, rider power: 91
Elapsed time: 239, target power: 94, rider power: 86
Elapsed time: 240, target power: 94, rider power: 87
Elapsed time: 241, target power: 94, rider power: 91
Elapsed time: 242, target power: 94, rider power: 89
Elapsed time: 243, target power: 94, rider power: 92
Elapsed time: 244, target power: 94, rider power: 92
Elapsed time: 245, target power: 94, rider power: 88
Elapsed time: 246, target power: 94, rider power: 84
Elapsed time: 247, target power: 94, rider power: 84
Elapsed time: 248, target power: 94, rider power: 86
Elapsed time: 249, target power: 94, rider power: 84
Elapsed time: 250, target power: 94, rider power: 90
Elapsed time: 251, target power: 94, rider power: 85
Elapsed time: 252, target power: 94, rider power: 88
Elapsed time: 253, target power: 94, rider power: 82
Elapsed time: 254, target power: 94, rider power: 87
Elapsed time: 255, target power: 94, rider power: 96
Elapsed time: 256, target power: 94, rider power: 93
Elapsed time: 257, target power: 94, rider power: 85
Elapsed time: 258, target power: 94, rider power: 87
Elapsed time: 259, target power: 94, rider power: 96
Elapsed time: 260, target power: 94, rider power: 93
Elapsed time: 261, target power: 94, rider power: 90
Elapsed time: 262, target power: 94, rider power: 88
Elapsed time: 263, target power: 94, rider power: 86
The workout has finished normally
Workout done! The ride was 1.0  minutes long with and average power of 91 Watts and average cadence of 51 rpm
```
It works! 

## Wrap up
The bulk of the coding is finished! There is a _very_ simple user interface that allows the user to select a workout and monitor their power during the ride. 
There are a few minor tweaks to be made but for the most part it's done! Yay!
