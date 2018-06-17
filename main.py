from orm import Base, Field
import sqlite3


class User(Base):
    __tablename__ = 'user'
    id = Field(ftype='int', pk=True)
    username = Field(ftype='text')
    email = Field(ftype='text')
    position_fk = Field(
        ftype='int',
        ref_table='position',
        ref_field='id_p',
        map_field='name',
        not_null=True
    )

    def create_fake_table(self):
        self.delete_table()
        self.create_table()
        self.add(id=1, username='doe', email='doe@gm.com', position_fk=1)
        self.add(id=2, username='joe', email='joe@gm.com', position_fk=2)
        self.add(id=3, username='mike', email='mike@gm.com', position_fk=3)
        self.add(id=4, username='john', email='john@gm.com', position_fk=1)


class Position(Base):
    __tablename__ = 'position'
    id_p = Field(ftype='int', pk=True)
    name = Field(ftype='text')

    def create_fake_table(self):
        self.delete_table()
        self.create_table()
        self.add(id_p=1, name='senior')
        self.add(id_p=2, name='middle')
        self.add(id_p=3, name='junior')


if __name__ == '__main__':
    conn = sqlite3.connect('orm.db')
    conn.execute('PRAGMA foreign_keys = 1;')

    position = Position(conn)
    user = User(conn)

    user.delete_table()
    position.delete_table()

    position.create_fake_table()
    user.create_fake_table()
    print('1 ', user.select_all())

    user.create_fake_table()
    user.update(username='john bro', email='john@gm.com')
    print('2 ', user.select_all())

    user.create_fake_table()
    print('3 ', user.select_columns('email', 'position'))
    print('4 ', user.select_columns('id', 'email'))
    print('5 ', user.select_columns('id', 'email', limit=2))

    print('6 ', user.select_columns('email', id=1))
    print('7 ', user.select_columns('id', 'email', id=1, username='doe'))
    print('8 ', user.select_columns('id', 'email', id=2))

    user.delete_table()
    # no such table: user
    user.add(id_p=1, name='senior')
    print('9 ', user.select_all())
    # "no such columns"
    user.create_fake_table()
    print('10 ', user.select_columns('email_11', id=1))
    # NOT NULL constraint failed
    user.delete_table()
    user.create_table()
    user.add(id=1, username='vasya')
    print('11 ', user.select_all())

    conn.close()
