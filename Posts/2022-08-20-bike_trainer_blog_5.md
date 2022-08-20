# Developing a cycling control program for my indoor trainer (TrainerRoad clone) Part 4 - Integrating PostgreSQL
From the very beginning of the project I knew I wanted to use a SQL database to manage the workout data. The main reason for this was scalability. I could easily keep track of a few workout templates and trainning logs but in a real setting with many users, a large catalogue of workouts and years of training data local file storage was not a good solutions. 
So I started to think about the database I wanted and how to organize the tables. 

### Database tables, the basics
Right away there were a few tables I needed. First, a table to store user information such as a unique id, a name, weight and functional threshold power (FTP). FTP is a measurement of the maximum power (in Watts) you can hold for an hour. The number is used as a fitness metric and often gets thrown around when bragging to your bros on group rides.
FTP is often normalized by rider weight to produce a 'Watts per Kilo' metric. So the table also included rider weight in kilograms. The athletes table looked like this. 

```
bike_workouts=# SELECT * FROM athletes;
 athlete_id | name  | weight_kg | ftp
------------+-------+-----------+-----
          1 | Scott |        70 | 237
```

Next I wanted to have a table holding the catalogue of available workouts. The workouts would each have an id, name, difficulty rating, and duration.
The table looked like this.
```
 template_id |      name       | duration_min |   difficulty
-------------+-----------------+--------------+-----------------
          10 | Fast and steady |           30 | Medium
           1 | Slow and steady |           15 | Easy
```
You may notice that the template id numbers skip from 1 to 10. I created a separate python script to insert new workouts into the database and it took me a few (or 8) tries to get it right.

Next there came the problem of how to store the workout templates themselves. If you think of a workout as a changing power level over time, then a given workout template can be stored as two lists. One with the timestamps (or indexes) and the other with the power values.
That's great, but to identify the workout? I could have another column with the template_id repeated in every row but that is a waste of space. Instead I chose to create a simple 2 column table for each workout. 
The first column holds the timestamps. The second column holds the power at each timestamp. Since the workout will run on 1 second intervals, I used the Serial type to automatically increment each new row.
The resulting table looked like this
```
timestamp | power
-----------+-------
         1 |  0.50
         2 |  0.50
         3 |  0.50
         4 |  0.50
         5 |  0.50
         6 |  0.50
         7 |  0.50
         8 |  0.50
         9 |  0.50
        10 |  0.50
        11 |  0.50
        12 |  0.50
        13 |  0.50
        14 |  0.50
        15 |  0.50
        16 |  0.50
        17 |  0.50
        18 |  0.50
        ...|...
  ```
  To identify the tables I wanted to use the template ids from the workout_templates table, but naming tables using integers seemed like a recipe for confusion down the line. 
  Instead I padded the template id with zeros and added the word 'workout'. So for example the workout named 'Slow and steady' was stored in table 'workout001'. 
  You might have noticed that the power values are decimals. This is so that the workouts can be generic and scaled for each rider according to their current fitness level (using their FTP).
  That is where the basic database set up stopped. I knew I would need more tables for storing completed workout data and tracking athlete progression over time, but first I wanted to setup the python methods I would use to work with the database. 
  
  ### Connecting to PostgreSQL using the psycopg2 library
  To connect to the Postgres databse I had created I used the psycopg2 library. The library documentation and examples were very helpful. Just like in the documentation example I created a configuration file so store the host address and login credentials. 
  For some extra complexity (who doesn't love unnecessary complexity) I wanted to store the database on a separate computer. After updating the Postgres configuration files and allowing port 5432 through the Windows firewall, I was able to connect to the database from all the way across the room.
  The connectin commands were pretty straighforward and looked like this:
  ```
import psycopg2
from SQL_config.config import Config1

def connect():
    """Connect to the PostgreSQL database server"""
    conn = None
    try:
        # read connection parameters
        params = Config1()

        # connect to the PostgreSQL server
        print("Connecting to the PostgtreSQL database...")
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        print("PostgreSQL database version:")
        cur.execute("SELECT version()")

        db_version = cur.fetchone()
        print(db_version)

        # execute a statement
        cur.execute("SELECT * from athletes;")

        result = cur.fetchone()
        print(result)

        # close the connection with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as Error:
        print(Error)
    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed")
  ```
  Running this code returned the following
  ```
Connecting to the PostgtreSQL database...
PostgreSQL database version:
('PostgreSQL 14.4, compiled by Visual C++ build 1914, 64-bit',)
(1, 'Scott', 70, 237)
Database connection closed
  ```
This basic test shows how I connected to the database running on another computer and interact with it using SQL commands. 

### Wrap up
This post introduced the database I used for the project and the basic tables I created. It also shows a simplified example of how the psycopg2 library can be used to connect to SQL databases.
  
