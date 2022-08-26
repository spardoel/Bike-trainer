#!/usr/bin/env python3

import logging
import asyncio
from user import User
from workout_player import WorkoutPlayer
from database_interface import DatabaseHandler
from trainer_interface import TrainerInterface
from user_interface import UserInterface

# configure logger
logging.basicConfig(filename="log.txt", level=logging.DEBUG)

# connect to the database
CURENT_USER_ID = 1  # this will be replaced with a login in the future
database = DatabaseHandler()


# lauch the user interface
user_interface = UserInterface(database)
selected_workout = user_interface.display_welcome_message()

# Create a user profile
current_user = User(database.get_athlete_power(CURENT_USER_ID))

# create the trainer interface
SUITO_ADDRESS = "F3:DB:2B:F4:47:0C"
trainer = TrainerInterface(SUITO_ADDRESS)


asyncio.run(trainer.trainer_connect())


# ***** asyncio.run() opens and closes an event loop.
# confirm that the device is connected.
if not trainer.check_connection():
    # if the trainer is not connected stop the program
    logging.error("Cannot connect to trainer. Program terminated")
    exit()


# create the workout player isntance
ride = WorkoutPlayer(
    trainer, current_user.rider_ftp, selected_workout, CURENT_USER_ID, database
)


asyncio.run(ride.start_workout())
