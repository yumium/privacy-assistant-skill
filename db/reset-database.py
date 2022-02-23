import os
import sys
import databaseBursts

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db"))
FILE_PATH = os.path.dirname(os.path.abspath(__file__))
DB_MANAGER = databaseBursts.dbManager()

schema = open(os.path.join(os.path.dirname(FILE_PATH), "db", "schema.sql"), "rb").read()
DB_MANAGER.execute(schema, None)

schema = open(os.path.join(os.path.dirname(FILE_PATH), "db", "schema_populate.sql"), "rb").read()
DB_MANAGER.execute(schema, None)

print("Database sucessfully reset")
