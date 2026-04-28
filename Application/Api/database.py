from pymongo import MongoClient
from contextlib import contextmanager
import os

MONGO_URI = "mongodb+srv://root:root@cluster0.x2olcfn.mongodb.net/?appName=Cluster0"
DB_NAME = "paris_immobilier"
        
        

def create_mongo_client():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

    # Test connexion (fail fast si IP/user/password pas OK)
    client.admin.command("ping")
    return client


def get_mongo_db(client: MongoClient):
    db_name = DB_NAME
    return client[db_name]