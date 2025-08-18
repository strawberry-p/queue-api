from fastapi import FastAPI
import sqlite3 as sq3
import time
#app = FastAPI()
database = sq3.connect("queue.db")
def queue_create_new(name="queue"):
    return(f'''
    create table if not exists {name} (
          ID integer primary key not null,
          content text,
          rel_pos float,
          timestamp integer)
''')

def DB_INSERT(name="queue"):
    return f"insert into {name} (ID, content, rel_pos, timestamp) values"

MNG_INSERT = "insert into queue_manager (ID, len, name, delete_secret, write_secret, read_secret, timestamp) values"

#is this lua or something
#why am i making functions that return text
c = database.cursor()
c.execute('''
    create table if not exists queue (
          ID integer primary key not null,
          content text,
          rel_pos float,
          timestamp integer)
''')
c.execute('''
    create table if not exists queue_manager (
          ID integer primary key not null,
          len integer not null,
          name text not null,
          delete_secret text,
          write_secret text,
          read_secret text,
          timestamp integer)
''')
c.execute("select * from queue_manager")
managerLen = len(c.fetchall())
if managerLen == 0:
    c.execute(f"{MNG_INSERT} (0, 0, 'queue', '', '', '', {round(time.time())})")
    managerLen += 1
c.execute(queue_create_new("info_queue"))
c.execute("select * from queue_manager where name = 'info_queue'")
if len(c.fetchall()) == 0:
    c.execute(f"{MNG_INSERT} ({managerLen}, 0, 'info_queue', '', '', '', {round(time.time())})")
    managerLen += 1
c.execute(queue_create_new("info_events"))
c.execute("select * from queue_manager where name = 'info_events'")
if len(c.fetchmany(1)) == 0:
    c.execute(f"{MNG_INSERT} ({managerLen}, 0, 'info_events', '', '', '', {round(time.time())})")
    managerLen += 1
c.execute("select * from queue_manager")
print(c.fetchall())
database.commit()
c.close()
#ts pmo fr

c = database.cursor()
c.execute("select * from queue")
queueLen = len(c.fetchall())
print(c.fetchall())
c.execute(f"update queue_manager set len = {queueLen} where name = 'queue'")
database.commit()
c.close()
def length_update(name="queue"):
    c = database.cursor()
    c.execute(f"select * from {name}")
    res = len(c.fetchall())
    c.execute(f"update queue_manager set len = {res} where name = '{name}'")
    database.commit()
    c.close()
    return res

def length_get(name="queue"):
    c = database.cursor()
    c.execute(f"select * from queue_manager where name = '{name}'")
    res = c.fetchone()[1]
    database.commit() #idk if i need to do this for read-only queries, but better safe than sorry?
    c.close()
    return res
def queue_write(content,name="queue"):
    global queueLen
    c = database.cursor()
    c.execute(f"{DB_INSERT()} {(length_get(name), str(content), 1, round(time.time()))}")
    #tuple to string formatting looks like this should work?
    database.commit()
    c.close()
    length_update(name) #should increase len

def queue_pop(pos, name="queue"):
    global queueLen
    c = database.cursor()
    qLen = length_get(name)
    if qLen > 0:
        c.execute(f"select * from {name} where ID = {pos}")
        res = str(c.fetchone()[1])
        c.execute(f"delete from {name} where ID = {pos}")
        for i in range(qLen-pos):
            c.execute(f"update {name} set ID = {pos+i} where ID = {pos+i+1}")
            #shift all entries above pos down by 1
        length_update(name) #should decrease len
    else:
        res = ""
        print(f"empty return for pos {pos}")
    database.commit()
    c.close()
    return res