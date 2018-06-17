from collections import OrderedDict
import sqlite3


class Field:
    def __init__(self, ftype='', unique=False, not_null=False, pk=False,
                 ref_table='', ref_field='', map_field=''):
        self.ftype = ftype
        self.unique = unique
        self.not_null = not_null
        self.pk = pk
        self.ref_table = ref_table
        self.ref_field = ref_field
        self.map_field = map_field

    def get_value_for_query(self, raw_value):
        digit_types = ['int', 'float']
        str_types = ['text', 'char']
        if raw_value is None:
            return 'NULL'
        for st in str_types:
            if st in self.ftype:
                return '"' + raw_value + '"'
        for dt in digit_types:
            if dt in self.ftype:
                return str(raw_value)

    def get_query_for_create_table(self, field):
        keywords = ''
        if self.pk:
            keywords += ' PRIMARY KEY'
        if self.unique:
            keywords += ' UNIQUE'
        if self.not_null:
            keywords += ' NOT NULL'

        query_for_create_table = '{} {} {}'.format(
            field, self.ftype, keywords
        )

        if self.ref_table:
            query_for_create_table = """
            {}, FOREIGN KEY({}) REFERENCES {}({}) 
            ON DELETE CASCADE ON UPDATE CASCADE
            """.format(
                query_for_create_table, field, self.ref_table, self.ref_field
            )

        return query_for_create_table


class Meta(type):
    @classmethod
    def __prepare__(cls, *args, **kwargs):
        return OrderedDict()

    def __new__(cls, name, bases, namespace):
        new_class = super().__new__(cls, name, bases, namespace)
        fields = [
            (name, value) for name, value in namespace.items()
            if isinstance(value, Field)
        ]
        new_class.base_fields = OrderedDict(fields)
        return new_class


class Base(metaclass=Meta):
    def __init__(self, connection):
        self.conn = connection
        self.c = self.conn.cursor()

        self.fields = self.__class__.base_fields
        self.table_name = self.__class__.__dict__.get('__tablename__')

    def save_to_db(self, query):
        try:
            self.c.execute(query)
            self.conn.commit()
        except (sqlite3.OperationalError, sqlite3.IntegrityError) as e:
            print("Finished with error: {}".format(e))

    def execute(self, query):
        try:
            self.c.execute(query)
            return True
        except sqlite3.OperationalError as e:
            return False


    @property
    def str_field_names(self):
        return ", ".join([field[0] for field in self.fields.items()])

    def create_table(self):
        query_template = "CREATE TABLE IF NOT EXISTS {} ({}) "

        fields_queries = []
        for field in self.fields.items():
            field_query = field[1].get_query_for_create_table(field[0])
            fields_queries.append(field_query)

        self.save_to_db(
            query_template.format(self.table_name, ', '.join(fields_queries))
        )

    def delete_table(self):
        query_template = "DROP TABLE IF EXISTS {} "
        self.c.execute(
            query_template.format(self.table_name)
        )
        self.conn.commit()

    def add(self, **kwargs):
        """
        Add record to db
        :param kwargs: columns=value
        """
        query_template = "INSERT INTO {}({}) VALUES({})"

        fields_queries = []
        for field in self.fields.items():
            field_name = field[0]
            raw_field_value = kwargs.get(field[0])
            field_value = field[1].get_value_for_query(raw_field_value)
            fields_queries.append((field_name, field_value))

        self.save_to_db(
            query_template.format(
                self.table_name,
                ", ".join([field[0] for field in fields_queries]),
                ", ".join([field[1] for field in fields_queries]),
                )
        )

    def update(self, **kwargs):
        """
        Update table with new values for all columns
        :param kwargs: columns=value
        """
        query_template = "UPDATE {} SET {}"

        set_queries = []
        for kwarg in kwargs.items():
            if self.is_field(kwarg[0]):
                field = self.fields.get(kwarg[0])
                set_queries.append(
                    "{} = {}".format(
                        kwarg[0],
                        field.get_value_for_query(kwarg[1])
                    )
                )

        self.save_to_db(
            query_template.format(
                self.table_name,
                ", ".join([query for query in set_queries]),
                )
        )

    def is_field(self, field):
        return field in self.fields

    def select_all(self):
        """
        Select all columns for the table (self.table_name)
        and join relation table (ref_table) with their field (map_field)
        """

        query_template = "SELECT {} FROM {}"
        str_field_names = self.str_field_names
        join_fields = []
        # try to find relation fields for join
        for field in self.fields.items():
            if field[1].ref_table:
                join_fields.append((field[0], field[1].ref_table, field[1].ref_field))
                str_field_names = '{}, {}.{}'.format(
                    str_field_names,
                    field[1].ref_table,
                    field[1].map_field
                )
                # only for one relation
                break

        # have relations
        if join_fields:
            query_template = '{} JOIN ({}) WHERE {}'.format(
                query_template, ', '.join([f[1] for f in join_fields]),
                '{}=={}.{}'.format(join_fields[0][0], join_fields[0][1],
                                   join_fields[0][2]))

        if self.execute(
                query_template.format(str_field_names, self.table_name)
        ):
            return self.c.fetchall()
        else:
            return ()

    def select_columns(self, *args, **kwargs):
        """
        Select columns (args) with filter (kwargs) and with limit (kwargs)
        :param args: columns
        :param kwargs: conditions, limit
        """
        query_template = "SELECT {} FROM {}"
        where_template = "SELECT {} FROM {} WHERE {}"

        select_queries = []
        for arg in args:
            if self.is_field(arg):
                select_queries.append(arg)
            else:
                print("No such field: {}".format(arg))

        where_queries = []
        for kwarg in kwargs.items():
            if self.is_field(kwarg[0]):
                field = self.fields.get(kwarg[0])
                where_queries.append(
                    "{} = {}".format(
                        kwarg[0],
                        field.get_value_for_query(kwarg[1])
                    )
                )

        if select_queries and where_queries:
            query = where_template.format(
                ', '.join(select_queries),
                self.table_name, ' AND '.join(where_queries)

            )
        elif select_queries:
            query = query_template.format(
                ', '.join(select_queries), self.table_name
            )
        else:
            return 'No columns are selected'

        limit = kwargs.get('limit', '')
        if limit:
            query += ' LIMIT {}'.format(kwargs.get('limit'))

        if self.execute(query):
            return self.c.fetchall()
        else:
            return ()


