#! /usr/bin/env python3


"""
COMP3311
24T1
Assignment 2
Pokemon Database

Written by: <YOUR NAME HERE> <YOUR STUDENT ID HERE>
Written on: <DATE HERE>

File Name: Q4

Description: Print the best move a given pokemon can use against a given type in a given game for each level from 1 to 100
"""


import sys
import psycopg2
import helpers


### Constants
USAGE = f"Usage: {sys.argv[0]} <Game> <Attacking Pokemon> <Defending Pokemon>"


def main(db):
    ### Command-line args
    if len(sys.argv) != 4:
        print(USAGE)
        return 1
    game_name = sys.argv[1]
    attacking_pokemon_name = sys.argv[2]
    defending_pokemon_name = sys.argv[3]

    # TODO: your code here
    cur = db.cursor()
    sql_moves = "select m.name, m.power, t.name, t.id, string_agg(DISTINCT r.assertion, ' OR ') from moves m join learnable_moves lm on lm.learns = m.id join pokemon p on p.id = lm.learnt_by join requirements r on r.id = lm.learnt_when join games g on g.id = lm.learnt_in join types t on t.id = m.of_type where p.name = %s and m.power is not null and g.name = %s group by m.name, m.power, t.name, t.id"
    sql_types_id = "select first_type, second_type from pokemon where name = %s"
    sql_type = "select t.name from types t where id = %s or id = %s;"
    sql_eff = "select * from type_effectiveness te join types t on t.id = te.attacking where t.name = %s;"
    cur.execute(sql_moves, (attacking_pokemon_name, game_name))
    moves = cur.fetchall()

    cur.execute(sql_types_id, (attacking_pokemon_name,))
    type_ids_att = cur.fetchall()

    cur.execute(sql_types_id, (defending_pokemon_name,))
    type_ids_def = cur.fetchall()

    res = {}
    
    for move in moves:
        power_res = move[1]
        move_id = move[3]
        if move_id in type_ids_att[0]:
            power_res = power_res * 1.5
        
        cur.execute(sql_eff, (move[2],))
        effects = cur.fetchall()
        for effect in effects:
            if effect[1] in type_ids_def[0]:
                power_res = (power_res * effect[2]) / 100
        res[move[0]] = {'power_res': int(power_res), 'require': move[4], 'move_name':move[0]}

    sorted_res = sorted(res.items(), key=lambda x: (-x[1]['power_res'], x[0]))

    print(f"If \"{attacking_pokemon_name}\" attacks \"{defending_pokemon_name}\" in \"{game_name}\" it\'s available moves are:")
    for move_name, move_info in sorted_res:
         print(f"\t{move_name}")
         print(f"\t\twould have a relative power of {move_info['power_res']}")
         print(f"\t\tand can be learnt from {move_info['require']}")

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
 