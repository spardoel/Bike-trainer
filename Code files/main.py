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
