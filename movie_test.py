
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(
        os.getenv("NEO4J_USERNAME"),
        os.getenv("NEO4J_PASSWORD")
    )
)

with driver.session(
    database=os.getenv("NEO4J_DATABASE")
) as session:

    result = session.run("""
        MATCH (m:Movie)
        RETURN m.title AS title
        LIMIT 10
    """)

    for record in result:
        print(record["title"])

driver.close()
