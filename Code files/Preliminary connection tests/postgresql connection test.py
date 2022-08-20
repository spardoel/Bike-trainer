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
        # print("PostgreSQL database version:")
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


if __name__ == "__main__":
    connect()
