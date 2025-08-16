from fastapi import FastAPI
import sqlite3 as sq3
import time
#app = FastAPI()
database = sq3.connect("queue.db")
c = database.cursor()
c.execute('''
    create table if not exists queue (
          ID integer primary key not null,
          content text,
          rel_pos float,
          timestamp integer)
''')
database.commit()
c.close()
DB_INSERT = "insert into queue (ID, content, rel_pos, timestamp) values"
c = database.cursor()
c.execute("select * from queue")
queueLen = len(c.fetchall())
database.commit()
c.close()
def queue_write(content):
    global queueLen
    c = database.cursor()
    c.execute(f"{DB_INSERT} {(queueLen, str(content), 1, round(time.time()))}")
    #tuple to string formatting looks like this should work?
    database.commit()
    c.close()
    queueLen += 1

def queue_pop(pos):
    global queueLen
    c = database.cursor()
    if queueLen > 0:
        c.execute(f"select * from queue where ID = {pos}")
        res = str(c.fetchone()[1])
        c.execute(f"delete from queue where ID = {pos}")
        for i in range(queueLen-pos):
            c.execute(f"update queue set ID = {pos+i} where ID = {pos+i+1}")
            #shift all entries above pos down by 1
        queueLen -= 1
    else:
        res = ""
        print(f"empty return for pos {pos}")
    database.commit()
    c.close()
    return res