import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

uri = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")
database = os.getenv("NEO4J_DATABASE")

driver = GraphDatabase.driver(
    uri,
    auth=(username, password)
)

try:
    driver.verify_connectivity()
    print("Connected to Neo4j successfully!")

    with driver.session(database=database) as session:
        result = session.run("RETURN 'Hello MovieGraph!' AS message")
        print(result.single()["message"])

except Exception as e:
    print("Connection failed:", e)

finally:
    driver.close()
