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
        if isinstance(name, int):
            self.workout_name = self.database.get_workout_name_from_id(name)

        self.power_profile = self.database.get_power_profile(
            workout_name=self.workout_name
        )
        logging.info(f"Workout {self.workout_name} was loaded.")
        print(f"Workout: {self.workout_name} was loaded. Ready to start.")

    async def start_workout(self):
        logging.info("Starting workout")
        print("here we go... ")

        # Add a new row to the ride_logs table and create a new ride table
        self.ride_log_table_name = self.database.add_new_ride_log(
            self.rider_id, self.workout_name
        )

        # Subscribe to the BLE characteristics to start getting data from the trainer
        await self.trainer.sub_to_trainer_characteristics()

        # request trainer resistance control
        await self.trainer.request_trainer_control()
        await asyncio.sleep(0.5)

        # set the initial timestamp / index and timeout timer
        self.time_of_last_update = 0
        self.timeout_timer = []
        self.workout_index = 0
        self.current_target_power = []

        # Start the main loop that runs during the ride
        while True:

            if not self.trainer.client.is_connected():
                break

            await asyncio.sleep(0.1)
            # check if new data has arrived
            if self.trainer.elapsed_time_sec > self.time_of_last_update:
                # if the trainer has a larger number, then new data has been received.
                # update the time_stamp and reset the timeout timer
                self.time_of_last_update = self.trainer.elapsed_time_sec
                self.timeout_timer = []

                # new data is available.
                # Check if new target power needs to be set
                self.next_target_power = int(
                    self.power_profile[self.workout_index] * self.ftp
                )

                if self.next_target_power != self.current_target_power:
                    await self.trainer.set_trainer_resistance(self.next_target_power)
                    # update the current power
                    self.current_target_power = self.next_target_power

                print(
                    f"Elapsed time: {self.time_of_last_update}, target power: {self.current_target_power }, rider power: {self.trainer.inst_power_watts}"
                )

                # Log the user power to the database
                self.database.log_ride_power(
                    self.ride_log_table_name,
                    self.trainer.inst_power_watts,
                    self.trainer.inst_cadence_rpm,
                )

                await asyncio.sleep(0.1)

                # increment the counter
                self.workout_index = self.workout_index + 1

                # end the loop if the workout is finished
                if self.workout_index >= len(self.power_profile):
                    print("The workout has finished normally")
                    break

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

        # after the main loop ends, display ride values to the user
        print(
            f"Workout done! The ride was {round(self.database.get_ride_duration_from_ride_log_table(self.ride_log_table_name),2)}  minutes long with and average power of {int(self.database.get_avg_power_from_ride_log_table(self.ride_log_table_name))} Watts and average cadence of {int(self.database.get_avg_cadence_from_ride_log_table(self.ride_log_table_name))} rpm"
        )
