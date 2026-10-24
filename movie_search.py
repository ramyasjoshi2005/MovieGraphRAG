
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"),
          os.getenv("NEO4J_PASSWORD"))
)

title = input("Enter a movie name: ")

with driver.session(
    database=os.getenv("NEO4J_DATABASE")
) as session:

    result = session.run("""
        MATCH (p:Person)-[:ACTED_IN]->(m:Movie)
        WHERE toLower(m.title) CONTAINS toLower($title)
        RETURN m.title AS movie,
               collect(p.name) AS actors
    """, title=title)

    found = False

    for record in result:
        found = True
        print("\nMovie:", record["movie"])
        print("Actors:", ", ".join(record["actors"]))

    if not found:
        print("No matching movie found.")

driver.close()
