#!/usr/bin/python

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


def create_new_workout(table_name, power_profile, conn):
    """Connect to the PostgreSQL database server"""

    try:
        # create a cursor
        cur = conn.cursor()

        # execute a statement
        cur.execute(
            f"CREATE TABLE {table_name} (timestamp SERIAL PRIMARY KEY, power DECIMAL(3,2) not null);"
        )

        # pass the data one line at a time to fill the table
        for inst_power in power_profile:
            cur.execute(f"INSERT INTO {table_name} (power) VALUES({inst_power});")

        # comit the changes to the database
        # conn.commit()

        # close the connection with the PostgreSQL
        # cur.close()
    except (Exception, psycopg2.DatabaseError) as Error:
        print(Error)


def add_new_workout(name, duration, difficulty, power_profile):

    # Connect to the database and update the workout templates table to include the new workout

    conn = None
    try:
        # read connection parameters
        params = Config1()

        # connect to the PostgreSQL server
        print("Connecting to the PostgtreSQL database...")
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # Insert the new table row
        cur.execute(
            f"INSERT INTO workout_templates (name,duration_min,difficulty) VALUES ('{name}',{duration},'{difficulty}');"
        )
        # log something?

        # Get the id number of the newly created table
        cur.execute(f"SELECT template_id from workout_templates WHERE name = '{name}';")

        # Get the id number and convert to string
        workout_id = str(cur.fetchone()[0])
        print(workout_id)

        # generate workout table name using workout id
        new_table_name = "workout" + workout_id.zfill(3)
        print(new_table_name)

        # call function to generate the corresponding workout table
        create_new_workout(new_table_name, power_profile, conn)

        # comit the changes to the database
        conn.commit()

        # close the connection with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as Error:
        print(Error)
    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed")


power_profile = [0.8] * (30 * 60)
name = "workout001"

# add_new_workout("Fast and steady", 30, "Medium", power_profile)

connect()
