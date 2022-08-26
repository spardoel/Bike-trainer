# Developing a cycling control program for my indoor trainer (TrainerRoad clone) Part 12 - Checking edge cases and error handling  

With the main code finished, I next wanted to test some of the possible issues the program might encounter. For example, what if the program cannot establish a connection to the trainer? Or what if the connection to the database is lost?
Let's start with the trainer. 

## Possible connection issues with the trainer
To test the traienr side of things I looked at 2 possibilities. First, what if the connection cannot be established, and second, what if the connection is lost during use. 

### Cannot connect to trainer
To test this, I ran the code while the trainer was unplugged. Here was the result.
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
Enter the workout id number to select it.
 To exit, press 'E'
1
Device with address F3:DB:2B:F4:47:0C was not found.

```
It looks like the bleak library has this nicely handled already. The user sees the message that the connection cannot be established, and the program exits. Ok, good. Moving on.

### Cannot connect to the database

To see what happens when the program can't connect to the database I turned off the computer hosting the Postgres database. Then I ran the code.
The connection attempt timed out, but the rest of the program attempted to run which caused a crash. So, after seeing that, I wanted to implement a check to see if the database connection was successfully established before running the rest of the code. 
I already had a try:, except: statement in the DatabaseHandler init method, so for this I simply added the exit() command. Like this.
```

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
            exit()
```
Now when the connection cannot be established, the program exits. 

## Future features and improvements
At this point I had accomplished what I set out to do. The main body of the code worked and I was satisfied with most things. But that doesn't mean there was no room for improvement.
Far from it, there were many places that I would like to improve. But for me these were past the point of diminishing returns. 
For instance, the UI could be improved and made to be much more interactive. I could use a library such as PyGame to make it more colourful and fun.
I also thought the main loop in the start_workout() method was cluttered and could use some refactoring. 
Expanding the databasae of available workouts would be good. 
The other feature that would be good to have is a pause function. Something that allows the user to stop the workout then resume it. This could be coupled with an autopause if the trainer connection is lost. 
For me, the pause and resume functionality would really benefit from a better UI, and controlling these features through the terminal would be awkward. Since I didn't plan on building a better UI, I also didn't implement the pause/resume functionality. 

## Wrap up
I think that's it. 
Thank you for checking out the project. I hope you found it somewhat interesting. 
