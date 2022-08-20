import logging


class WorkoutPlayer:
    def __init__(self, trainer, rider_ftp, name, database):

        self.trainer = trainer
        self.ftp = rider_ftp
        self.workout_name = name

        # get the power profile from the database
        self.power_profile = database.get_power_profile(workout_name=self.workout_name)
        logging.info(f"Workout {self.workout_name} was loaded.")
        print(f"Workout: {self.workout_name} was loaded. Ready to start.")

    def start_workout(self):
        logging.info("Starting workout")
        print("here we go")
