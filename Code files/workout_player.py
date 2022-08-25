import logging
import time
import keyboard
import asyncio


NO_NEW_DATA_TIMEOUT = 10  # seconds


class WorkoutPlayer:
    def __init__(self, trainer, rider_ftp, name, rider_id, database):

        self.trainer = trainer
        self.ftp = rider_ftp
        self.workout_name = name
        self.rider_id = rider_id
        self.database = database

        # get the power profile from the database
        self.power_profile = self.database.get_power_profile(
            workout_name=self.workout_name
        )
        logging.info(f"Workout {self.workout_name} was loaded.")
        print(f"Workout: {self.workout_name} was loaded. Ready to start.")

    def set_callbacks(self, trainer_callbacks):
        self.trainer_callbacks = trainer_callbacks

    async def start_workout(self):  # add async
        logging.info("Starting workout")
        print("here we go... ")

        # self.ride_log_id = self.database.add_new_ride_log(
        #   self.rider_id, self.workout_name
        # )

        # Subscribe to the BLE characteristics to start getting data from the trainer
        await self.trainer.sub_to_trainer_characteristics()
        # await asyncio.create_task(self.trainer.sub_to_trainer_characteristics())

        # request trainer resistance control
        await self.trainer.request_trainer_control()

        # set the initial timestamp / index and timeout timer
        self.time_of_last_update = 0
        self.timeout_timer = []

        # Start the main loop that runs during the ride
        while True:
            await asyncio.sleep(0.1)
            # check if new data has arrived

            await self.trainer.set_trainer_resistance(50)

            # print(self.trainer.elapsed_time_sec)

            if self.trainer.elapsed_time_sec > self.time_of_last_update:
                # if the trainer has a larger number then new data has been received.
                # update the time_stamp and reset the timeout timer
                self.time_of_last_update = self.trainer.elapsed_time_sec
                self.timeout_timer = []

                # Do a bunch of cool things..
                # more cool things...

            elif not self.timeout_timer:
                # if the timer is not running, start it
                self.timeout_timer = time.time()

            elif (time.time() - self.timeout_timer) > NO_NEW_DATA_TIMEOUT:
                # if the timer has been running longer than the timeout duration, break the loop
                logging.debug(
                    f"The no new data timeout of {NO_NEW_DATA_TIMEOUT} seconds was reached."
                )
                print("Timeout reached")
                break

            # end the loop with the possible exit conditions
            if keyboard.is_pressed("Esc"):
                break
