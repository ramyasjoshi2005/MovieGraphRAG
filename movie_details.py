
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
        MATCH (p:Person)-[:ACTED_IN]->(m:Movie)
        WHERE m.title = $title
        RETURN m.title AS movie,
               collect(p.name) AS actors
    """, title="The Matrix")

    for record in result:
        print("Movie:", record["movie"])
        print("Actors:", record["actors"])

driver.close()
