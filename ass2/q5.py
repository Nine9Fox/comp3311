#! /usr/bin/env python3


"""
COMP3311
24T1
Assignment 2
Pokemon Database

Written by: <YOUR NAME HERE> <YOUR STUDENT ID HERE>
Written on: <DATE HERE>

File Name: Q5

Description: Print a formatted (recursive) evolution chain for a given pokemon
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

    sql_post = " \
        WITH RECURSIVE evolution_chain as ( \
        select \
            e.id, \
            pre.name as pre_name, \
            post.name as post_name, \
            e.pre_evolution as pre_evolution, \
            e.post_evolution as post_evolution, \
            r.assertion, \
            er.inverted \
        from evolutions e \
        join pokemon pre on e.pre_evolution = pre.id \
        join pokemon post on e.post_evolution = post.id \
        join evolution_requirements er on er.evolution = e.id\
        join requirements r on r.id = er.requirement \
        where pre.name = %s \
        union \
        select \
            e.id, \
            pre.name as pre_name, \
            post.name as post_name, \
            e.pre_evolution, \
            e.post_evolution, \
            r.assertion, \
            er.inverted \
        from evolution_chain ec \
        join evolutions e on e.pre_evolution = ec.post_evolution \
        join evolution_requirements er on er.evolution = e.id\
        join requirements r on r.id = er.requirement \
        join pokemon pre on e.pre_evolution = pre.id \
        join pokemon post on e.post_evolution = post.id \
        ) \
        select * from evolution_chain"

    sql_pre = " \
        WITH RECURSIVE evolution_chain as ( \
        select \
            e.id, \
            pre.name as pre_name, \
            post.name as post_name, \
            e.pre_evolution as pre_evolution, \
            e.post_evolution as post_evolution, \
            r.assertion, \
            er.inverted \
        from evolutions e \
        join pokemon pre on e.pre_evolution = pre.id \
        join pokemon post on e.post_evolution = post.id \
        join evolution_requirements er on er.evolution = e.id\
        join requirements r on r.id = er.requirement \
        where post.name = %s \
        union \
        select \
            e.id, \
            pre.name as pre_name, \
            post.name as post_name, \
            e.pre_evolution, \
            e.post_evolution, \
            r.assertion, \
            er.inverted \
        from evolution_chain ec \
        join evolutions e on e.post_evolution = ec.pre_evolution \
        join evolution_requirements er on er.evolution = e.id\
        join requirements r on r.id = er.requirement \
        join pokemon pre on e.pre_evolution = pre.id \
        join pokemon post on e.post_evolution = post.id \
        ) \
        select * from evolution_chain"

    sql_findname = "select p.id, p.name from pokemon p where p.id = %s"

    cur.execute(sql_pre, (pokemon_name,))
    pres = cur.fetchall()

    cur.execute(sql_post, (pokemon_name,))
    posts = cur.fetchall()

    evolution_dict_pre = {}
    evolution_dict_post = {}

    for data in pres:
        eid, pre_evolution, post_evolution, _, _, requirement, inverted = data
        if eid not in evolution_dict_pre:
            evolution_dict_pre[eid] = [pre_evolution, post_evolution]
        evolution_dict_pre[eid].append((requirement, inverted))

    for data in posts:
        eid, pre_evolution, post_evolution, _, _, requirement, inverted = data
        if eid not in evolution_dict_post:
            evolution_dict_post[eid] = [pre_evolution, post_evolution]
        evolution_dict_post[eid].append((requirement, inverted))

    print('')
    if not evolution_dict_pre:   
        pre = pokemon_name
        print(f"\'{pre}\' doesn't have any pre-evolutions.") 
        print('')

    isEvo = []
    for key, value in evolution_dict_pre.items():
        pre, post, *requirements = value
        if (pre, post) not in isEvo:
            isEvo.append((pre, post))
            count_or = 0
            for key_j, value_j in evolution_dict_pre.items():
                pre_j, post_j, *requirements_j = value_j
                if pre == pre_j and post == post_j:
                    count_or += 1
            #print(count_or)
            if count_or == 1:
                if len(requirements) == 1:
                    print(f"\'{post}\' can evolve from \'{pre}\' when the following requirements are satisfied:")
                    if requirements[0][1] == False:
                        print(f"\t{requirements[0][0]}")
                    else:
                        print(f"\tNOT {requirements[0][0]}")

                if len(requirements) > 1:
                    print(f"\'{post}\' can evolve from \'{pre}\' when the following requirements are satisfied:")
                    if requirements[0][1] == False:
                        print(f"\t\t{requirements[0][0]}")
                    else:
                        print(f"\t\tNOT {requirements[0][0]}")

                    for re in requirements[1:]:
                        print("\tAND")
                        if re[1] == False:
                            print(f"\t\t{re[0]}")
                        else:
                            print(f"\t\tNOT {re[0]}")

            if count_or > 1:
                if len(requirements) == 1:
                    print(f"\'{post}\' can evolve from \'{pre}\' when the following requirements are satisfied:")
                    if requirements[0][1] == False:
                        print(f"\t\t{requirements[0][0]}")
                    else:
                        print(f"\t\tNOT {requirements[0][0]}")

                    for key_j, value_j in evolution_dict_pre.items():
                        pre_j, post_j, *requirements_j = value_j
                        if pre == pre_j and post == post_j:
                            print("\tOR")
                            if requirements_j[0][1] == False:
                                print(f"\t\t{requirements_j[0][0]}")
                            else:
                                print(f"\t\tNOT {requirements_j[0][0]}")
                
                if len(requirements) > 1:
                    print(f"\'{post}\' can evolve from \'{pre}\' when the following requirements are satisfied:")
                    if requirements[0][1] == False:
                        print(f"\t\t\t{requirements[0][0]}")
                    else:
                        print(f"\t\t\tNOT {requirements[0][0]}")

                    for re in requirements[1:]:
                        print("\t\tAND")
                        if re[1] == False:
                            print(f"\t\t\t{re[0]}")
                        else:
                            print(f"\t\t\tNOT {re[0]}")  

                    for key_j, value_j in evolution_dict_pre.items():
                        pre_j, post_j, *requirements_j = value_j
                        if pre == pre_j and post == post_j and requirements != requirements_j:
                            print("\tOR")
                            if len(requirements_j) == 1:
                                if requirements_j[0][1] == False:
                                    print(f"\t\t\t{requirements_j[0][0]}")
                                else:
                                    print(f"\t\t\tNOT {requirements_j[0][0]}")
                            if len(requirements_j) > 1:   
                                if requirements_j[0][1] == False:
                                    print(f"\t\t\t{requirements_j[0][0]}")
                                else:
                                    print(f"\t\t\tNOT {requirements_j[0][0]}")

                                for re in requirements_j[1:]:
                                    print("\t\tAND")
                                    if re[1] == False:
                                        print(f"\t\t\t{re[0]}")
                                    else:
                                        print(f"\t\t\tNOT {re[0]}")
            print('')
            noPre = 1
            for key_k, value_k in evolution_dict_pre.items():
                pre_k, post_k, *requirements_k = value_k
                if pre == post_k:
                    noPre = 0
            if noPre == 1:
                print(f"\'{pre}\' doesn't have any pre-evolutions.") 
                print('') 


    if not evolution_dict_post:
        post = pokemon_name
        print(f"\'{post}\' doesn't have any post-evolutions.")
        print('')

    
    cur_index = 0
    dict_length = len(evolution_dict_post)
    isEvo = []

    for key, value in evolution_dict_post.items():
        pre, post, *requirements = value
        count_or = 0
        if (pre, post) not in isEvo:
            isEvo.append((pre, post))
            for key_j, value_j in evolution_dict_post.items():
                pre_j, post_j, *requirements_j = value_j
                if pre == pre_j and post == post_j:
                    count_or += 1
            #print(count_or)
            if count_or == 1:
                if len(requirements) == 1:
                    print(f"\'{pre}\' can evolve into \'{post}\' when the following requirements are satisfied:")
                    if requirements[0][1] == False:
                        print(f"\t{requirements[0][0]}")
                    else:
                        print(f"\tNOT {requirements[0][0]}")

                if len(requirements) > 1:
                    print(f"\'{pre}\' can evolve into \'{post}\' when the following requirements are satisfied:")
                    if requirements[0][1] == False:
                        print(f"\t\t{requirements[0][0]}")
                    else:
                        print(f"\t\tNOT {requirements[0][0]}")

                    for re in requirements[1:]:
                        print("\tAND")
                        if re[1] == False:
                            print(f"\t\t{re[0]}")
                        else:
                            print(f"\t\tNOT {re[0]}")

            if count_or > 1:
                if len(requirements) == 1:
                    print(f"\'{pre}\' can evolve into \'{post}\' when the following requirements are satisfied:")
                    if requirements[0][1] == False:
                        print(f"\t\t{requirements[0][0]}")
                    else:
                        print(f"\t\tNOT {requirements[0][0]}")

                    for key_j, value_j in evolution_dict_pre.items():
                        pre_j, post_j, *requirements_j = value_j
                        if pre == pre_j and post == post_j:
                            print("\tOR")
                            if requirements_j[0][1] == False:
                                print(f"\t\t{requirements_j[0][0]}")
                            else:
                                print(f"\t\tNOT {requirements_j[0][0]}")
                
                if len(requirements) > 1:
                    print(f"\'{pre}\' can evolve into \'{post}\' when the following requirements are satisfied:")
                    print(f"\t\t\t{requirements[0]}")
                    if requirements[0][1] == False:
                        print(f"\t\t\t{requirements[0][0]}")
                    else:
                        print(f"\t\t\tNOT {requirements[0][0]}")

                    for re in requirements[1:]:
                        print("\t\tAND")
                        print(f"\t\t\t{re}")
                        if re[1] == False:
                            print(f"\t\t\t{re[0]}")
                        else:
                            print(f"\t\t\tNOT {re[0]}")

                    for key_j, value_j in evolution_dict_pre.items():
                        pre_j, post_j, *requirements_j = value_j
                        if pre == pre_j and post == post_j and requirements != requirements_j:
                            print("\tOR")
                            if len(requirements_j) == 1:
                                if requirements_j[0][1] == False:
                                    print(f"\t\t{requirements_j[0][0]}")
                                else:
                                    print(f"\t\tNOT {requirements_j[0][0]}")

                            if len(requirements_j) > 1:   
                                if requirements_j[0][1] == False:
                                    print(f"\t\t\t{requirements_j[0][0]}")
                                else:
                                    print(f"\t\t\tNOT {requirements_j[0][0]}")
                                for re in requirements_j[1:]:
                                    print("\t\tAND")
                                    if re[1] == False:
                                        print(f"\t\t\t{re[0]}")
                                    else:
                                        print(f"\t\t\tNOT {re[0]}")
            print('')
            noPost = 1

            if cur_index == dict_length - 1:
                print(f"\'{post}\' doesn't have any post-evolutions.")
                print('')            
            else:
                for key_k, value_k in evolution_dict_post.items():
                    pre_k, post_k, *requirements_k = value_k
                    if post == pre_k:
                        noPost = 0
                if noPost == 1: 
                    print(f"\'{post}\' doesn't have any post-evolutions.")
                    print('') 
                    print('')
            cur_index += 1

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
