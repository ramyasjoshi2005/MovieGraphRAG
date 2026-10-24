
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from google import genai

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(
        os.getenv("NEO4J_USERNAME"),
        os.getenv("NEO4J_PASSWORD")
    )
)

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
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
        LIMIT 10
    """, title=title)

    movies = [record.data() for record in result]

driver.close()

if not movies:
    print("No matching movies found.")
else:
    prompt = f"""
    You are a movie question-answering assistant.

    Answer the question using ONLY the database results.
    Do not invent information.

    Question: Who acted in {title}?

    Database results: {movies}
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
        
    )

    print("\nAnswer:")
    print(response.text)
