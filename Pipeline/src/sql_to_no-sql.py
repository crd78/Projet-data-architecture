from pathlib import Path
import sqlite3
from pymongo import MongoClient


def list_tables(conn):
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )
    return [r[0] for r in cur.fetchall()]


def migrate_table(conn, mongo_db, table):
    conn.row_factory = sqlite3.Row
    cur = conn.execute(f'SELECT * FROM "{table}"')

    coll = mongo_db[table]
    coll.delete_many({})
    batch = []
    total = 0

    while True:
        rows = cur.fetchmany(BATCH_SIZE)
        if not rows:
            break
        for row in rows:
            doc = dict(row)
            batch.append(doc)

        if batch:
            coll.insert_many(batch, ordered=False)
            total += len(batch)
            batch.clear()

    return total


if __name__ == "__main__":
    # Constants
    PIPELINE_DIR = Path(__file__).resolve().parent.parent
    BASE_DIR = PIPELINE_DIR / "datasets_finaux"
    DB_PATH = BASE_DIR / "paris_immobilier.db"
    MONGO_URI = "mongodb+srv://root:root@cluster0.x2olcfn.mongodb.net/?appName=Cluster0"
    DB_NAME = "paris_immobilier"
    BATCH_SIZE = 5000

    # Création des connexions
    conn = sqlite3.connect(DB_PATH)
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    mongo_db = client[DB_NAME]
    tables = list_tables(conn)

    for table in tables:
        inserted = migrate_table(conn, mongo_db, table)
        print(f"Table '{table}' migrée avec {inserted} documents insérés.")
