import psycopg2
import os
import random


connection = False

random.seed()

try:
    connection = psycopg2.connect(user=os.environ['DBUSERNAME'],
                                  password=os.environ['DBPASSWORD'],
                                  host="127.0.0.1",
                                  port="5432",
                                  database=os.environ['DB'])

    print("PostgreSQL connection is open")

    print("Deleting unsolved murders")
    cursor = connection.cursor()
    cursor.execute("DELETE FROM frontend_murder WHERE NOT agreed_on")
    connection.commit()

    print("Reviving players")
    cursor = connection.cursor()
    cursor.execute("UPDATE frontend_player SET is_dead = FALSE WHERE frontend_player.is_dead")
    connection.commit()

    print("Producing new targets")
    cursor = connection.cursor()
    cursor.execute("SELECT user_id from frontend_player")

    players = cursor.fetchall()
    targets = list(map(lambda x: x[0], players))

    ret = []
    random.shuffle(targets)

    for i in range(0, len(targets)):
        if i != len(targets) - 1:
            ret.append((targets[i], targets[i+1]))
        else:
            ret.append((targets[i], targets[0]))

    print(ret)
    for combi in ret:
        cursor.execute(f"UPDATE frontend_player SET target_id = {combi[1]} WHERE user_id = {combi[0]}")
    connection.commit()


except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL Err:", error)
finally:
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
