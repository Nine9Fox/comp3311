#! /usr/bin/env python3


"""
COMP3311
24T1
Assignment 2
Pokemon Database

Written by: <YOUR NAME HERE> <YOUR STUDENT ID HERE>
Written on: <DATE HERE>

File Name: Q1.py

Description: List the number of pokemon and the number of locations in each game
"""


import sys
import psycopg2
import helpers


### Constants
USAGE = f"Usage: {sys.argv[0]}"

def main(db):
    if len(sys.argv) != 1:
        print(USAGE)
        return 1

    # TODO: your code here
    cur = db.cursor()
    cur.execute("select g.region as Region, g.name as Game, count(DISTINCT p.national_id) as pokemon_count, count(DISTINCT l.id) as location_count from games g \
                join pokedex p ON p.game = g.id \
                left join locations l on g.id = l.appears_in \
                group by g.region, g.name \
                order by g.region, g.name, count(DISTINCT p.national_id), count(DISTINCT l.id)")
    rows = cur.fetchall()
    print("Region Game              #Pokemon #Locations")
    for row in rows:
        RegionName, GameName, Pokemon, Locations = row
        print(f"{RegionName:<6} {GameName:<17} {Pokemon:<8} {Locations}")

if __name__ == '__main__':
    exit_code = 0
    db = None
    try:
        db = psycopg2.connect(dbname="pkmon")
        exit_code = main(db)
    except psycopg2.Error as err:
        print("DB error: ", err)
        exit_code = 1
    except Exception as err:
        print("Internal Error: ", err)
        raise err
    finally:
        if db is not None:
            db.close()
    sys.exit(exit_code)
