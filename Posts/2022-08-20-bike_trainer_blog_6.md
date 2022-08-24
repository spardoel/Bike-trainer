# Developing a cycling control program for my indoor trainer (TrainerRoad clone) Part 6 - First attempts at program design 

At this point I had tested all the individual components. I could connect to the trainer via bluetooth, and I could access the database running on my other computer. The next step was to create the actual program. 
### Design
I started with a few class diagrams but I wasn't making much progress. I found it hard to visualize the whole finished system.
Eventually I gave up and just started working on the components I knew for sure I would need. My initial implementation (in sudo UML) looked like this.

![initial program class diagrams](https://user-images.githubusercontent.com/102377660/186519519-c6144003-d2ee-4754-9cb2-281d9a83065c.png)

As you can see I started with a main function that was associated with all the other classes. The User class just held the rider's ftp (for now). The TrainerInterface class was created in the main function then passed to the WorkoutPlayer for use. The DatabaseHandler class was used to interact with the database. 
At this point, my main function looked like this
```
import logging
import asyncio
from user import User
from workout_player import WorkoutPlayer
from database_interface import DatabaseHandler
from trainer_interface import TrainerInterface

# configure logger
logging.basicConfig(filename="log.txt", level=logging.DEBUG)

# connect to the database
CURENT_USER_ID = 1  # this will be replaced with a login in the future
database = DatabaseHandler()

# Create a user profile
current_user = User(database.get_athlete_power(CURENT_USER_ID))

# create the trainer interface
SUITO_ADDRESS = "F3:DB:2B:F4:47:0C"
trainer = TrainerInterface(SUITO_ADDRESS)
asyncio.run(trainer.trainer_connect())

# select a workout (this will later be an input from the user)
selected_workout = "Fast and steady"
# create the workout player isntance
ride = WorkoutPlayer(trainer, current_user.rider_ftp, selected_workout, database)
ride.start_workout()
```
After the imports, I set up a log file. Then declared the current user id as a constant and initialized the database handler. I then created the instance of the User class. The User class takes the rider ftp as an input paramater, so that value was retrived from the database using the database handler's get_athlete_power() method.
Next, I instantiated the TrainerInterface class which started the connection to the trainer. Once the trainer was connected and a workout was selected (in this case declared as a constant), a WorkoutPlayer instance was created.

### Wrap up 
This short post introduced the basic structure of the program. In the next posts I'll go into how the different classes were implemented and the challenges I encountered with the asyncio library... 

