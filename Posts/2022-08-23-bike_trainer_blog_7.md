# Developing a cycling control program for my indoor trainer (TrainerRoad clone) Part 7 - Setting up the DatabaseHandler class and its methods

In this post I will go over the creation of the DatabaseHandler class and its methods. This class handles the interactions with the Postgres database running on a separate computer.

## Previously...
Previously I talked a bit about how the database would be set up, so let's start there. In the post I described the tables being used. First there was the athlete table which holds the athlete id, name, weight and ftp.
```
bike_workouts=# SELECT * FROM athletes;
 athlete_id | name  | weight_kg | ftp
------------+-------+-----------+-----
          1 | Scott |        70 | 237
```
Pretty straightforward. In that post I also introduced the workout_templates table which acts as a sort of catalogue for the available workouts which each have their own table with the timestamp and power data.
I made a diagram to ilustrate the relationship.
![workout_templates_tables](https://user-images.githubusercontent.com/102377660/186248572-0a3f36d5-75f0-4660-8aea-653ebd7a9ca6.png)


As you can see, the workout templates table holds the information about each workout. The workouts themselves are represented in separated tables named according to the template_id. Note that in the 'power' column of the workout tables the power value is represented as a fraction of the rider's ftp. 
Also note that the power normally wouldn't change every second as depicted in the diagram since you'd normally want to stay at a certain intensity for a few minutes at a time. 

And that's about as far as the previous post went. Picking up where it left off let's tak about 'Rides'. 

## Ride tables

Having tables to store the workout templates is great, but I also wanted to store the completed workouts. To make things a bit clearer let's define some terms. 
I used 'Workout' to refer to templates and available activities and I used 'Ride' to refer to completed activities. With this in mind, I created additional tables that mirror the templates table but hold the power that the rider actually produced. Check out the diagram below.

![ride_logs table](https://user-images.githubusercontent.com/102377660/186247330-a904b5d9-1c47-451c-a5af-307ce4eeeec3.png)
Just like for the workouts, there is one table holding the information for each ride and other tables holding the rides themselves. In this case, the ride_logs table holds the ride id, the template id, the athlete id and the data of completion. Then, separate ride tables hold the power that the rider produced at each timestamp during the ride. 

## The DatabaseHandler class
As in the initial tests, I started the Postgres conection using the Config file. Here is the class declaration and the init method.
```
import logging
import psycopg2
from SQL_config.config import Config

class DatabaseHandler:
    def __init__(self):
        # open the connection to the database
        self.conn = None
        try:
            # read connection parameters
            params = Config()
            # create the connection
            self.conn = psycopg2.connect(**params)

            logging.info("Database connection established")

        except (Exception, psycopg2.DatabaseError) as Error:
            print(Error)
```
The connection is saved as a class property called conn. I did this so that I can easily access the connection from the other methods and I don't need to re-establish the connection. 
Next I created a destructor to close the connection. 
```
    def __del__(self):
        # desctructor
        if self.conn is not None:
            self.conn.close()
            logging.info("Database connection closed")
```

### get_athlete_power()
With those basics out of the way, let's look at the other methods. A mentioned earlier, all of the workouts are scaled according to the rider's functional threshold power (FTP). FTP is a number (in Watts) representing the rider's current fitness level. If you want to learn more I suggest you google it, or ask a cycling. Just like bros in the gym bragging about how much they can bench, when provoked a cyclist will enthusiastically tell you all about their FTP, what it means, and how their FTP is higher than their buddy. All this to say, I needed to create a method to get the rider's FTP from the 'athletes' database. Here is what I cam up with.
```
    def get_athlete_power(self, athlete_id):

        # create a cursor
        cur = self.conn.cursor()

        cur.execute(f"SELECT ftp FROM athletes WHERE athlete_id = {athlete_id};")

        # Get the id number and convert to string
        return cur.fetchone()[0]
```
This method accepts a athlete id and returns the athletes ftp. The method does the following. Using the connection that was created in the init method, the method creates a cursor. Then, using the cur.execute command it sends a SQL command to the database. The command selects the 'ftp' column from the 'athletes' table and returns the row where the 'athlete_id' matches the one provided. Then, using cur.fetchone, return the result of the SQL querry. 

### get_workout_id_from_name()
Similar to how the athlete's FTP value was retreived using the athlete_id, this method retrieves the workout_id number corresponding to a specific workout name. Here is the method definition.
```
    def get_workout_id_from_name(self, workout_name):
        # create a cursor
        cur = self.conn.cursor()

        cur.execute(f"SELECT template_id from workout_templates WHERE name = '{workout_name}';")

        # Get the id number and convert to string
        return cur.fetchone()[0]
```
As you can see, the method uses the same commands as the get_athlete_power() method, changing only the SQL query. In this case the query selects the template_id column from the workout_templates table and returns the row where the workout_name matches the name provided to the method. 

Next let's look at something a little more interesting.

### get_power_profile()
This method will return the power profile as a list. I wanted to make the method flexible enough to accept either the workout name or workout id as input parameters. A lot of the code in the method has to do with handling these two possible inputs. 
```
def get_power_profile(self, workout_name="", workout_id=[]):
        # if no values are entered, return an empty list
        if len(workout_name) == 0 and len(workout_id) == 0:
            return []
            
        try:
            # create a cursor
            cur = self.conn.cursor()

            # get list of possible workout ids
            cur.execute(f"SELECT template_id FROM workout_templates;")

            # Get the id numbers and convert to string
            available_workout_ids = cur.fetchall()
            # extract the list of tuples
            self.available_workout_ids = [x[0] for x in available_workout_ids]

            # get the workout id value using the workout name
            if len(workout_name) > 0 and len(workout_id) == 0:
                self.workout_id = self.get_workout_id_from_name(workout_name)
            else:
                self.workout_id = workout_id

            if self.workout_id not in self.available_workout_ids:
                logging.warning(f"Workout '{workout_name}' with ID {workout_id} not found")
                return -1

            # if the workout is available, generate the desired table name. Table name format is 'workout002'
            self.table_name = "workout" + str(self.workout_id).zfill(3)
            # execute a statement
            cur.execute(f"SELECT power FROM {self.table_name};")
            # retrieve the response
            power_profile = cur.fetchall()

            # close the connection with the PostgreSQL
            cur.close()

            # extract from the list of tuples format
            return [x[0] for x in power_profile]
 
        except (Exception, psycopg2.DatabaseError) as Error:
            print(Error)           
```
The get_power_profile method accepts workout_name and workout_id as optional inputs. The first block of code checks whether there were any actual inputs. It checks the length of the input parameters, and if both are length 0, then stop the method and return an empty list. Assuming the method had at least one non null input, then fetch data from the database. As with the previous 2 mthods, I created a cursor, and executed a SQL query. The query in this case selected all of the template_id rows from the workout_templates table. Then, uing the cur.fetchall command, I accepted the result of the query as a tuple. Next, using a list comprehension I extracted the workout_id values and stored them in a class property called available_workout_ids. At this point in the code, I had an input (either the workout name or id) and I had a list of available workout ids to search through. If the given input was the workout id, then this step is easy. But what if the workout name was provided? 
Let's take a closer look. I recoppied the section of code below for reference. 
```
            # get the workout id value using the workout name
            if len(workout_name) > 0 and len(workout_id) == 0:
                self.workout_id = self.get_workout_id_from_name(workout_name)
            else:
                self.workout_id = workout_id
```
The 'if' statement confirms that a workout name was provided and that the workout id number was not. In this case, use the get_workout_if_from_name() method to get the id. If the first statement fails, that means we have the workout_id, so simply copy it to the class property. The next block of code (coppied below) checks that the workout_id assigned to the class property is valid, i.e., is within the list of available workout ids. If it is not valid, then log the problem and return error code -1. 
```
            if self.workout_id not in self.available_workout_ids:
                logging.warning(
                    f"Workout '{workout_name}' with ID {workout_id} not found"
                )
                return -1
```

Great, at this point in the method I had the workout id value. Now all that was left was to get the power profile from the appropriate workout table. Recall that the workout templates were names using the word 'workout' plus the template id value. So the next line of code generated the name of the desired table by combining the string 'workout' with the zero padded template id. 
```
            self.table_name = "workout" + str(self.workout_id).zfill(3)
```
Then, simply execute the SQL query to get the power column from the table, and use the fetchall() command to save it as a tuple. Then close the cursor for good measure and use a list comprehension to return the power values in the form of a list. 
```
            # execute a statement
            cur.execute(f"SELECT power FROM {self.table_name};")
            # retrieve the response
            power_profile = cur.fetchall()

            # close the connection with the PostgreSQL
            cur.close()

            # extract from the list of tuples format
            return [x[0] for x in power_profile]
```

The final method I wanted to cover in this post is the method needed to add a new ride log.

### add_new_ride_log()
When a workout starts, the program needs to create a new entry in the ride_logs table and create a new ride table for that entry. The following method does just that. 
```
 def add_new_ride_log(self, rider_id, workout_name):
        # get the workout tempalte id
        workout_tempalte_id = self.get_workout_id_from_name(workout_name)

        # create the cursor
        cur = self.conn.cursor()
        date_to_add = date.today()
        print(date_to_add)
        cur.execute(
            f"INSERT INTO ride_logs (template_id,athlete_id,ride_date) VALUES({workout_tempalte_id},{rider_id},'{date.today()}');"
        )
        # commit the changes to the database
        self.conn.commit()

        # get the ride id from the newly created ride using the current data (assuming these two operations run on the same day)
        cur.execute(
            f"SELECT ride_id FROM ride_logs WHERE ride_date = '{date.today()}';"
        )
        # Get the id number and convert to string
        ride_id = str(cur.fetchone()[0])

        # generate the table name
        new_table_name = "ride" + ride_id.zfill(3)

        # execute a statement
        cur.execute(
            f"CREATE TABLE {new_table_name} (timestamp SERIAL PRIMARY KEY, power DECIMAL(3,2) not null);"
        )

        self.conn.commit()

        # return the ride table name so that the table can be updated during the ride
        return new_table_name
```
The method accepts the rider_id and workout_name and inputs, these are needed to add a new row to the ride_logs table. The first thing the method does is converts the workout_name to the workout_id. 
Then it generates a cursor and executes a SQL command. This command inserts a new row into the ride_logs table. Note that to generate the date, I used date.today() from datetime. The result from date.today() was not accepted as a valid date in the SQL database, so I had to send it as a string, which worked. 
After the command to add a row to the ride_logs table was sent, the conn.comit() command was used to commit the query to the database.
Once the row was added to the ride_logs table, and the corresponding ride_id value was generated, I needed to get that ride_id. I did that using another SQL query to select the ride_id where the ride_data wasa equal to today's date. I suppose this could create a problem if the row was created just before midnight and the next query was executed a the next day... But I don't think that's likely. But to avoid the possibility altogether I'll update the code so that the date is saved as a variable that is used in booth queries - ensuring that the dates match.
Then, once the ride_id was obtained, it was used to generate the name of the ride table in the form of 'ride001' where 001 is the ride_id.
Then, another SQL execute() command is used to create the table with the newly generate name. 
Finally, the changes are committed and the name of the table was returned. This name will be needed to update the table with the power data over the course of the workout.

## Wrap up
This post detailed the methods within the DatabaseHandler class. These methods were needed to fetch specific data from the database and to update and create tables. The methods will be used by the other classes in the program and may need to be updated or changed, but for now this class is done :) On to the next one.
