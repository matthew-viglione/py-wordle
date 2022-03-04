"""Use pymongo do generate some stats"""
import json
from timeit import default_timer as timer
from pymongo import MongoClient
from wordle_game import WordleGame, get_words, position_level_score, word_level_score


def list_all_collections_and_sizes():
    """Print the name of every collection in the database, along with
    the number of documents in the collection.
    """
    dbs = client.list_database_names()
    for db in dbs:
        for c in client[db].list_collection_names():
            print(json.dumps({f"{db}.{c}": client[db][c].count_documents({})}, indent=4))


def print_all_documents(db, collection):
    """Print all the documents in the collection."""
    for document in client[db][collection].find({}):
        print(" " * 5, document)


def evaluate_solution_methods(collection, *args):
    """Solve all possible puzzles using the provided scoring methods.

    A dictionary representing each resulting attempt to solve the puzzle
    is stored in the specified mongo collection.

    Blacklist includes puzzles that generated exceptions. This means the
    scoring algorithm has bugs and sometimes fails.
    """
    for method in [*args]:
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
            except Exception as e:
                blacklist.append((w, e))
            document = {
                "solution": w,
                "method": method.__name__,
                "guesses": result,
                "score": len(result),
                "solved": solved,
            }
            collection[method.__name__].insert_one(document)
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


def print_average_score(collection):
    """Print the average score for the provided collection."""
    pipeline = [
        {"$match": {"solved": True}},
        {"$group": {"_id": None, "average": {"$avg": "$score"}}},
    ]
    avg = list(collection.aggregate(pipeline))[0]["average"]
    print("Score distribution:")
    print(f"   Average  : {avg}")


def print_score_distribution(collection):
    """Print the distribution of scores for the provided collection."""
    pipeline = [
        {"$match": {"solved": True}},
        {
            "$group": {
                "_id": "$score",
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"_id": 1}},
    ]
    for r in collection.aggregate(pipeline):
        print(f"   {r['_id']} guesses: {r['count']}")


def print_failed_solutions(collection):
    """Print the number of unsolved puzzles and the target solution."""
    pipeline = [
        {"$match": {"solved": False}},
        {"$group": {"_id": None, "count": {"$sum": 1}}},
    ]
    print(f"Failed to solve {list(collection.aggregate(pipeline))[0]['count']} puzzles:")
    pipeline = [
        {"$match": {"solved": False}},
        {"$group": {"_id": "$solution"}},
    ]
    print([r["_id"] for r in collection.aggregate(pipeline)])


if __name__ == "__main__":
    client = MongoClient(port=27017)
    wordle_db = client.wordle
    # evaluate_solution_methods(wordle_db, word_level_score, position_level_score)
    collections = wordle_db.list_collection_names()
    for col in collections:
        print("\n", "-" * 10, f"{col}", "-" * 10)
        col = client.wordle[col]
        print_average_score(col)
        print_score_distribution(col)
        print_failed_solutions(col)
