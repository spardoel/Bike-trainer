import logging
import psycopg2
from SQL_config.config import Config1


class DatabaseHandler:
    def __init__(self):
        # open the connection to the database
        self.conn = None
        try:
            # read connection parameters
            params = Config1()
            # create the connection
            self.conn = psycopg2.connect(**params)

            logging.info("Database connection established")

        except (Exception, psycopg2.DatabaseError) as Error:
            print(Error)

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

    def get_athlete_power(self, athlete_id):

        # create a cursor
        cur = self.conn.cursor()

        cur.execute(f"SELECT ftp FROM athletes WHERE athlete_id = {athlete_id};")

        # Get the id number and convert to string
        return cur.fetchone()[0]
