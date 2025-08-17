import sqlite3 as sq3
db = sq3.connect("queue.db")
c = db.cursor()
c.execute("drop table queue_manager")
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
db.commit()
c.close()