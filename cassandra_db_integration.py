"""A Cassandra integration for the py-wordle game."""
import json
from collections import Counter
from timeit import default_timer as timer

from cassandra.cluster import Cluster
from cassandra.query import dict_factory
from wordle_game import WordleGame, get_words, position_level_score, word_level_score


def _insert_helper(values):
    r = ""
    for v in values:
        if isinstance(v, (bool, int)):
            r += "," + str(v)
        else:
            r += ",'" + v + "'"
    return r[1:]


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
        # values = ", ".join([f"'{v}'" for v in data.values()])
        values = _insert_helper(data.values())
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

    def drop_table(self, table):
        """Drop the specified table."""
        command = f"DROP TABLE IF EXISTS {table};"
        print(command)
        self.session.execute(command)


def evaluate_solution_methods(db, *args):
    """Solve all possible puzzles using the provided scoring methods.

    A dictionary representing each resulting attempt to solve the puzzle
    is stored in the specified Cassandra table.

    Blacklist includes puzzles that generated exceptions. This means the
    scoring algorithm has bugs and sometimes fails.
    """
    for method in [*args]:
        print(method)
        all_solutions = get_words("wordlist_solutions.txt")
        blacklist = []
        unsolved = []
        num_guesses = []
        start = timer()
        for w in all_solutions:
            try:
                game = WordleGame(enable_solver=True, solution=w)
                result, solved = game.solve(method=method)
                if not solved:
                    unsolved.append(w)
                else:
                    num_guesses.append(len(result))
                document = {
                    "solution": w,
                    # "method": method.__name__,
                    # "guesses": result,
                    "score": len(result),
                    "solved": solved,
                }
                db.insert(method.__name__, document)
            except Exception as e:
                print(e)
                blacklist.append(w)
        end = timer()
        print(
            json.dumps(
                {
                    "method": method.__name__,
                    "blacklist": blacklist,
                    "blacklist count": len(blacklist),
                    "unsolved": unsolved,
                    "unsolved count": len(unsolved),
                    "average score": sum(num_guesses) / len(num_guesses),
                    "elapsed time": end - start,
                },
                indent=4,
            )
        )


def print_average_score(db, table):
    """Print the average score for the provided method."""
    db.session.execute(f"CREATE INDEX IF NOT EXISTS ON {table}(method);")
    # query = f"SELECT AVG(score) FROM {table};"
    query = f"SELECT score FROM {table};"
    avg = [i["score"] for i in list(db.session.execute(query))]
    avg = sum(avg) / len(avg)
    print(f"   Average  : {avg}")


def print_score_distribution(db, table):
    """Print the distribution of scores for the provided method."""
    db.session.execute(f"CREATE INDEX IF NOT EXISTS ON {table}(method);")
    query = f"SELECT score FROM {table};"
    avg = [i["score"] for i in list(db.session.execute(query))]
    for k, v in sorted(dict(Counter(avg)).items()):
        print(f"   {k} guesses: {v}")


def print_failed_solutions(db, table):
    """Print the number of unsolved puzzles and the target solution."""
    db.session.execute(f"CREATE INDEX IF NOT EXISTS ON {table}(solved);")
    query = f"SELECT solution FROM {table} WHERE solved = false ALLOW FILTERING;"
    words = [i["solution"] for i in list(db.session.execute(query))]
    print(f"Failed to solve {len(words)} puzzles:")
    print(words)


if __name__ == "__main__":

    schema = {
        "solution": "text",
        "method": "text",
        "guesses": "text",
        "score": "int",
        "solved": "boolean",
    }
    cassandra_db = Cassandra()
    # cassandra_db.list_tables()

    for m in (word_level_score, position_level_score):
        m_name = m.__name__
        # cassandra_db.drop_table(m_name)
        # cassandra_db.create_table(m_name, schema)
        # evaluate_solution_methods(cassandra_db, m)
        print("\n", "-" * 10, f"{m_name}", "-" * 10)
        print_average_score(cassandra_db, m_name)
        print_score_distribution(cassandra_db, m_name)
        print_failed_solutions(cassandra_db, m_name)
