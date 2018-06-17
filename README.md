# ORM
**Project for learning ORM**

(without logging, test modules and others right things)

**From command line:**

```
$ python3 main.py
```

Requirements
--
- at least python 3.5 only

Installation
--

just clone the project:

```
$ git clone https://github.com/PyExplorer/ORM.git
$ cd ORM
```

Docs
--
Example of using and output: 


```
    conn = sqlite3.connect('orm.db')
    conn.execute('PRAGMA foreign_keys = 1;')

    position = Position(conn)
    user = User(conn)

    user.delete_table()
    position.delete_table()

    position.create_fake_table()
    user.create_fake_table()
    print('1 ', user.select_all())
```
```
    1  [(1, 'doe', 'doe@gm.com', 1, 'senior'), (2, 'joe', 'joe@gm.com', 2, 'middle'), (3, 'mike', 'mike@gm.com', 3, 'junior'), (4, 'john', 'john@gm.com', 1, 'senior')]
```
```
    user.create_fake_table()
    user.update(username='john bro', email='john@gm.com')
    print('2 ', user.select_all())
```
```
    2  [(1, 'john bro', 'john@gm.com', 1, 'senior'), (2, 'john bro', 'john@gm.com', 2, 'middle'), (3, 'john bro', 'john@gm.com', 3, 'junior'), (4, 'john bro', 'john@gm.com', 1, 'senior')]
```

```
    user.create_fake_table()
    print('3 ', user.select_columns('email', 'position'))
    print('4 ', user.select_columns('id', 'email'))
    print('5 ', user.select_columns('id', 'email', limit=2))

    print('6 ', user.select_columns('email', id=1))
    print('7 ', user.select_columns('id', 'email', id=1, username='doe'))
    print('8 ', user.select_columns('id', 'email', id=2))

```
```
    No such field: position
    3  [('doe@gm.com',), ('joe@gm.com',), ('mike@gm.com',), ('john@gm.com',)]
    4  [(1, 'doe@gm.com'), (2, 'joe@gm.com'), (3, 'mike@gm.com'), (4, 'john@gm.com')]
    5  [(1, 'doe@gm.com'), (2, 'joe@gm.com')]
    6  [('doe@gm.com',)]
    7  [(1, 'doe@gm.com')]
    8  [(2, 'joe@gm.com')]
```
```
    user.delete_table()
    # no such table: user
    user.add(id_p=1, name='senior')
    print('9 ', user.select_all())
```
```
    Finished with error: no such table: user
    9  ()
```
```
    # "no such columns"
    user.create_fake_table()
    print('10 ', user.select_columns('email_11', id=1))
```
```
    No such field: email_11
    10  No columns are selected
```
```
    # NOT NULL constraint failed
    user.delete_table()
    user.create_table()
    user.add(id=1, username='vasya')
    print('11 ', user.select_all())
```
```
    Finished with error: NOT NULL constraint failed: user.position_fk
    11  []
```
    conn.close()
```
