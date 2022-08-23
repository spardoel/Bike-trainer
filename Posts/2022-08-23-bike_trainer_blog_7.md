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
