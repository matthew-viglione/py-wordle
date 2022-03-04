"""A Cassandra integration for the py-wordle game."""

from cassandra.cluster import Cluster
from cassandra.query import dict_factory


class Cassandra:
    """A helper class to make working with Cassandra DB easier."""

    cluster = None
    session = None
    schema = None

    def __init__(self):
        self.cluster = Cluster()
        self.session = self.cluster.connect()
        self.session.row_factory = dict_factory

        self.create_keyspace("wordle")
        self.list_keyspaces()

        self.session.set_keyspace("wordle")

    def create_keyspace(self, name):
        """Create a Cassandra keyspace. This is simillar to a collection
        in Mongo.
        """
        command = f"CREATE KEYSPACE IF NOT EXISTS {name} WITH REPLICATION"
        command += " = { 'class' : 'SimpleStrategy', 'replication_factor' : 3 }"
        print(command)
        self.session.execute(command)

    def create_table(self, table, fields, primary="solution"):
        """Create a table with the specified name and datatyped. The
        primary key can also be chosen.
        """
        key_list = "".join([f"{k} {v}, " for k, v in fields.items()])
        command = (
            f"CREATE TABLE IF NOT EXISTS {table} ({key_list}PRIMARY KEY ({primary}))"
        )
        print(command)
        self.session.execute(command)

    def insert(self, table, data):
        """Insert into the specified table."""
        keys = ", ".join(data.keys())
        values = ", ".join([f"'{v}'" for v in data.values()])
        command = f"INSERT INTO {table} ({keys}) VALUES ({values})"
        print(command)
        self.session.execute(command)

    def select(self, table, columns):
        """Select data from the specified table."""
        keys = ", ".join(columns)
        command = f"SELECT {keys} FROM {table}"
        print(command)
        return list(self.session.execute(command))

    def list_keyspaces(self):
        """Print a list of all availble keyspaces."""
        print("Keyspaces:")
        for r in list(self.session.execute("DESCRIBE keyspaces")):
            print(" ", r["keyspace_name"])

    def list_tables(self):
        """Print a list of available tables."""
        print("Tables: ")
        for r in list(self.session.execute("DESCRIBE tables")):
            print(" ", r["name"])


table_name = "test"

schema = {
    "solution": "text",
    "method": "text",
    "guesses": "text",
    "score": "text",
    "solved": "text",
}

game_data = {
    "solution": "raise",
    "method": "word_level_score",
    "guesses": "something",
    "score": str(3),
    "solved": str(True),
}

db = Cassandra()
db.create_table(table_name, schema)
db.list_tables()
db.insert(table_name, game_data)
print(db.select(table_name, schema.keys()))


# https://github.com/dkoepke/cassandra-python-driver/blob/master/example.py
# https://docs.datastax.com/en/developer/python-driver/3.25/api/
