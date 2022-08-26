import logging
import psycopg2
from SQL_config.config import Config
from datetime import date
from statistics import mean


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

    def __del__(self):
        # desctructor
        if self.conn is not None:
            self.conn.close()
            logging.info("Database connection closed")

    def get_power_profile(self, workout_name="", workout_id=[]):
        """Connect to the PostgreSQL database server"""
        # if no values are entered, return an empty list
        if len(workout_name) == 0 and len(workout_id) == 0:
            return []

        try:
            # create a cursor
            cur = self.conn.cursor()

            # get list of possible workout ids
            cur.execute(f"SELECT template_id from workout_templates;")

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
                logging.warning(
                    f"Workout '{workout_name}' with ID {workout_id} not found"
                )
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

    def get_workout_id_from_name(self, workout_name):
        # create a cursor
        cur = self.conn.cursor()

        cur.execute(
            f"SELECT template_id from workout_templates WHERE name = '{workout_name}';"
        )

        # Get the id number and convert to string
        return cur.fetchone()[0]

    def get_workout_name_from_id(self, workout_id):
        # create a cursor
        cur = self.conn.cursor()

        cur.execute(
            f"SELECT name from workout_templates WHERE template_id = '{workout_id}';"
        )

        # Get the id number and convert to string
        return cur.fetchone()[0]

    def get_athlete_power(self, athlete_id):

        # create a cursor
        cur = self.conn.cursor()

        cur.execute(f"SELECT ftp FROM athletes WHERE athlete_id = {athlete_id};")

        # Get the id number and convert to string
        return cur.fetchone()[0]

    def add_new_ride_log(self, rider_id, workout_name):
        # get the workout tempalte id
        workout_tempalte_id = self.get_workout_id_from_name(workout_name)

        # create the cursor
        cur = self.conn.cursor()
        todays_date = date.today()
        cur.execute(
            f"INSERT INTO ride_logs (template_id,athlete_id,ride_date) VALUES({workout_tempalte_id},{rider_id},'{todays_date}');"
        )
        # commit the changes to the database
        self.conn.commit()

        # get the ride id from the newly created ride using the current data (assuming these two operations run on the same day)
        cur.execute(
            f"SELECT ride_id FROM ride_logs WHERE ride_date = '{todays_date}' ORDER BY ride_id DESC;"
        )

        # Get the id number and convert to string
        ride_id = str(cur.fetchone()[0])

        # generate the table name
        new_table_name = "ride" + ride_id.zfill(3)

        # execute a statement
        cur.execute(
            f"CREATE TABLE {new_table_name} (timestamp SERIAL PRIMARY KEY, power int not null, cadence int not null);"
        )

        self.conn.commit()

        # return the ride table name so that the table can be updated during the ride
        return new_table_name

    def log_ride_power(self, table_name, power_to_log, cadence_to_log):

        # create the cursor
        cur = self.conn.cursor()
        # Query the database
        cur.execute(
            f"INSERT INTO {table_name} (power, cadence) VALUES({power_to_log},{cadence_to_log});"
        )
        # commit the changes to the database
        self.conn.commit()

    def get_ride_duration_from_ride_log_table(self, table_name):

        cur = self.conn.cursor()

        # Query the database
        cur.execute(f"SELECT timestamp FROM {table_name};")

        results = cur.fetchall()
        # extract the list of tuples
        results_list = [x[0] for x in results]

        # return the length of the ride in minutes.
        return len(results_list) / 60

    def get_avg_power_from_ride_log_table(self, table_name):

        cur = self.conn.cursor()

        # Query the database
        cur.execute(f"SELECT power FROM {table_name};")

        results = cur.fetchall()
        # extract the list of tuples
        results_list = [x[0] for x in results]

        # return the average
        return mean(results_list)

    def get_avg_cadence_from_ride_log_table(self, table_name):

        cur = self.conn.cursor()

        # Query the database
        cur.execute(f"SELECT cadence FROM {table_name};")

        results = cur.fetchall()
        # extract the list of tuples
        results_list = [x[0] for x in results]

        # return the average
        return mean(results_list)

    def print_available_workouts(self):
        # create a cursor
        cur = self.conn.cursor()
        # Query the database
        cur.execute(f"SELECT * FROM workout_templates ORDER BY template_id;")
        # retrieve the response
        available_workouts = cur.fetchall()

        # print the header
        print("Workout Id,  Workout name,   Duration (min),    Difficulty")

        # Print the workout information
        for row in available_workouts:
            print(f"{row[0]}           {row[1]}       {row[2]}             {row[3]} ")

        # Query the database
        cur.execute(f"SELECT template_id FROM workout_templates ORDER BY template_id;")
        # retrieve the response
        valid_ids = cur.fetchall()
        # return a list of valid ids
        return [str(x[0]) for x in valid_ids]
