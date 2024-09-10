#! /usr/bin/env python3


"""
COMP3311
24T1
Assignment 2
Pokemon Database

Written by: <YOUR NAME HERE> <YOUR STUDENT ID HERE>
Written on: <DATE HERE>

File Name: Q2

Description: List all locations where a specific pokemon can be found
"""


import sys
import psycopg2
import helpers


### Constants
USAGE = f"Usage: {sys.argv[0]} <pokemon_name>"


def main(db):
    if len(sys.argv) != 2:
        print(USAGE)
        return 1

    pokemon_name = sys.argv[1]

    # TODO: your code here
    cur = db.cursor()
    sql = "select \
            g.name, l.name, \
            case \
                when  e.rarity >= 21 then 'Common' \
                when  e.rarity >= 6 then 'Uncommon' \
                when  e.rarity >= 1 then 'Rare' \
                else 'Limited' \
            end as Rarity, \
            e.levels, \
            string_agg(DISTINCT \
                        case \
                            when er.inverted then 'Not ' || r.assertion \
                            else r.assertion \
                        end, ', ') \
            from encounters e \
            join locations l on l.id = e.occurs_at \
            join games g on g.id = l.appears_in \
            join pokemon p on p.id = e.occurs_with \
            join encounter_requirements er on er.encounter = e.id \
            join requirements r on er.requirement = r.id \
            where p.name = %s \
            group by \
                g.region, g.name, l.name, e.rarity, e.levels, r.assertion \
            order by \
                g.region, g.name, l.name, \
                case \
                    when  e.rarity >= 21 then 1 \
                    when  e.rarity >= 6 then 4 \
                    when  e.rarity >= 1 then 3 \
                    else 2 \
                end, \
                e.levels, r.assertion"

    cur.execute(sql, (pokemon_name,))
    rows = cur.fetchall()
    widths = [len("Game"), len("Location"), len("Rarity"), len("MinLevel"), len("MaxLevel"), len("Requirements")]
    for row in rows:
        for i, item in enumerate(row):
            widths[i] = max(widths[i], len(str(item)))

    print(f"Game{'':<{widths[0] - 4}} Location{'':<{widths[1] - 8}} Rarity{'':<{widths[2] - 6}} MinLevel{'':<{widths[3] - 8}} MaxLevel{'':<{widths[3] - 8}} Requirements")

    curInfo = []
    curRe = {}
    for row in rows:
        game_name, location, rarity, levels, requirments = row
        levels_tuple = tuple(map(int, levels.strip("()").split(",")))
        info = game_name + location + rarity + levels + requirments
        info_noRe = game_name + location + rarity + levels
        if info not in curInfo:
            curInfo.append(info)

            if info_noRe not in curRe:
                curRe[info_noRe] = {'re': requirments}
            else:
                curRe[info_noRe]['re'] += ', ' + requirments

            print(f"{game_name:<{widths[0]}} {location:<{widths[1]}} {rarity:<{widths[2]}} {levels_tuple[0]:<{widths[3]}} {levels_tuple[1]:<{widths[3]}} {curRe[info_noRe]['re']}")


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
