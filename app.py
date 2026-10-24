
import os
import re
import streamlit as st
from dotenv import load_dotenv
from neo4j import GraphDatabase
from google import genai

# -------------------- CONFIGURATION --------------------

load_dotenv()

st.set_page_config(
    page_title="CineGraph AI",
    page_icon="🎬",
    layout="wide"
)

# -------------------- CUSTOM CSS --------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

.stApp {
    background: radial-gradient(ellipse at top, #202044 0%, #0b1020 60%);
    color: #edf0ff;
    font-family: 'DM Sans', sans-serif;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1200px;
    width: 94%;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

section[data-testid="stSidebar"] {
    background: #0d1426;
    border-right: 1px solid #28334b;
}

.brand {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 30px;
    font-weight: 700;
    color: white;
}

.brand span {
    color: #a99aff;
}

.muted {
    color: #9caaca;
    font-size: 13px;
}

.hero {
    padding: 25px 0 20px;
}

.hero h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(28px, 4vw, 40px);
    letter-spacing: -1px;
    color: white;
    margin-bottom: 8px;
}

.pill {
    display: inline-block;
    padding: 6px 11px;
    border-radius: 30px;
    background: #252343;
    border: 1px solid #4b447e;
    color: #c8beff;
    font-size: 11px;
    letter-spacing: 1px;
    margin-bottom: 12px;
}

div[data-testid="stChatMessage"] {
    background: #141c30;
    border: 1px solid #2a3651;
    border-radius: 18px;
    padding: 16px 18px;
    margin-bottom: 14px;
}

div[data-testid="stChatMessage"]:has(
    [data-testid="chatAvatarIcon-user"]
) {
    background: #252044;
    border-color: #514681;
}

div[data-testid="stChatMessageContent"] {
    color: #edf0ff;
    line-height: 1.7;
}

div[data-testid="stChatInput"] {
    background: #141c30;
    border: 1px solid #514681;
    border-radius: 18px;
}

div[data-testid="stChatInput"] textarea {
    color: white !important;
}

.stButton > button {
    min-height: 44px;
    border-radius: 12px;
    border: 1px solid #374363;
    background: #171f35;
    color: #edf0ff;
}

.stButton > button:hover {
    background: #29254b;
    border-color: #a99aff;
    color: white;
}

[data-testid="stExpander"] {
    border: 1px solid #303c57;
    border-radius: 12px;
    background: #11182a;
}

hr {
    border-color: #27334b;
}

.footer {
    text-align: center;
    color: #7583a2;
    font-size: 12px;
    padding: 18px 0;
}
</style>
""", unsafe_allow_html=True)


# -------------------- CONNECTIONS --------------------

@st.cache_resource
def get_connections():
    required = [
        "NEO4J_URI",
        "NEO4J_USERNAME",
        "NEO4J_PASSWORD",
        "NEO4J_DATABASE",
        "GEMINI_API_KEY"
    ]

    missing = [key for key in required if not os.getenv(key)]

    if missing:
        raise ValueError(
            "Missing settings in .env: " + ", ".join(missing)
        )

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

    return driver, os.getenv("NEO4J_DATABASE"), client


# -------------------- QUESTION CLASSIFICATION --------------------

def get_intent(question):
    q = question.lower()

    if any(x in q for x in [
        "recommend", "similar to", "movies like",
        "movie like", "suggest movies"
    ]):
        return "recommend"

    if any(x in q for x in [
        "which movies did", "what movies did",
        "which films did", "what films did",
        "filmography of"
    ]):
        return "actor_movies"

    if any(x in q for x in [
        "who directed", "director of", "directed by"
    ]):
        return "director"

    if any(x in q for x in [
        "who acted in", "who starred in",
        "who stars in", "cast of", "actors in",
        "who is in"
    ]):
        return "movie_actors"

    return "movie_search"


# -------------------- EXTRACT SEARCH TERM --------------------

def extract_search_term(question, intent):
    q = question.strip().rstrip("?!.,'\"")

    patterns = {
        "recommend": [
            r"^(?:please\s+)?recommend\s+(?:me\s+)?movies?\s+similar\s+to\s+",
            r"^(?:please\s+)?recommend\s+(?:me\s+)?movies?\s+like\s+",
            r"^(?:please\s+)?suggest\s+(?:some\s+)?movies?\s+(?:similar\s+to|like)\s+",
            r"^(?:please\s+)?recommend\s+",
        ],
        "actor_movies": [
            r"^(?:please\s+)?which movies did\s+",
            r"^(?:please\s+)?what movies did\s+",
            r"^(?:please\s+)?which films did\s+",
            r"^(?:please\s+)?what films did\s+",
            r"^filmography of\s+",
        ],
        "director": [
            r"^who directed\s+",
            r"^director of\s+",
            r"^who is the director of\s+",
        ],
        "movie_actors": [
            r"^who acted in\s+",
            r"^who starred in\s+",
            r"^who stars in\s+",
            r"^actors in\s+",
            r"^cast of\s+",
            r"^who is in\s+",
        ],
        "movie_search": [
            r"^tell me about\s+",
            r"^show me\s+",
            r"^find\s+",
            r"^search for\s+",
        ]
    }

    for pattern in patterns.get(intent, []):
        q = re.sub(pattern, "", q, flags=re.IGNORECASE)

    suffixes = [
        r"\s+act(?:ed)?\s+in$",
        r"\s+star(?:red)?\s+in$",
        r"\s+movies?$",
        r"\s+films?$",
        r"\s+please$",
    ]

    for suffix in suffixes:
        q = re.sub(suffix, "", q, flags=re.IGNORECASE)

    return q.strip(" \t?!.,'\"")


# -------------------- NEO4J RETRIEVAL --------------------

def retrieve(question, driver, database):
    intent = get_intent(question)
    term = extract_search_term(question, intent)

    if not term:
        return intent, [], term

    queries = {
        "recommend": """
            MATCH (p:Person)-[:ACTED_IN]->(liked:Movie)
                  <-[:ACTED_IN]-(other:Person)
                  -[:ACTED_IN]->(rec:Movie)
            WHERE toLower(liked.title) CONTAINS toLower($term)
              AND rec <> liked
            RETURN rec.title AS movie,
                   count(DISTINCT other) AS shared_actors
            ORDER BY shared_actors DESC, movie
            LIMIT 5
        """,

        "actor_movies": """
            MATCH (p:Person)-[:ACTED_IN]->(m:Movie)
            WHERE toLower(p.name) CONTAINS toLower($term)
            RETURN p.name AS actor,
                   collect(DISTINCT m.title) AS movies
            LIMIT 10
        """,

        "director": """
            MATCH (p:Person)-[:DIRECTED]->(m:Movie)
            WHERE toLower(m.title) CONTAINS toLower($term)
            RETURN m.title AS movie,
                   collect(DISTINCT p.name) AS directors
            LIMIT 10
        """,

        "movie_actors": """
            MATCH (p:Person)-[:ACTED_IN]->(m:Movie)
            WHERE toLower(m.title) CONTAINS toLower($term)
            RETURN m.title AS movie,
                   collect(DISTINCT p.name) AS actors
            LIMIT 10
        """,

        "movie_search": """
            MATCH (m:Movie)
            WHERE toLower(m.title) CONTAINS toLower($term)
            OPTIONAL MATCH (p:Person)-[:ACTED_IN]->(m)
            RETURN m.title AS movie,
                   collect(DISTINCT p.name) AS actors
            LIMIT 10
        """
    }

    with driver.session(database=database) as session:
        result = session.run(queries[intent], term=term)
        data = [record.data() for record in result]

        # Fallback: search for a person if no movie was found.
        if not data and intent == "movie_search":
            result = session.run("""
                MATCH (p:Person)-[:ACTED_IN]->(m:Movie)
                WHERE toLower(p.name) CONTAINS toLower($term)
                RETURN p.name AS actor,
                       collect(DISTINCT m.title) AS movies
                LIMIT 10
            """, term=term)

            data = [record.data() for record in result]

    return intent, data, term


# -------------------- GEMINI ANSWER GENERATION --------------------

def generate_answer(question, intent, data, client):
    prompt = f"""
You are CineGraph, a friendly movie chatbot.

Answer the user's question using only the Neo4j data below.
Do not invent movie, actor or director information.
If the retrieved data is insufficient, say so.

For recommendations, explain that results are based on
shared actors and do not necessarily mean similar plots.

Question: {question}
Question category: {intent}
Retrieved Neo4j data: {data}

Give a clear, natural answer. Use bullet points when useful.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    return response.text or "Sorry, I couldn't generate an answer."


def answer_question(question):
    driver, database, client = get_connections()

    intent, data, term = retrieve(question, driver, database)

    if not data:
        return (
            "I couldn't find matching information in the movie "
            "knowledge graph. Try checking the movie or person's "
            "name, or ask about another movie.",
            [],
            intent
        )

    answer = generate_answer(question, intent, data, client)

    return answer, data, intent


# -------------------- SESSION STATE --------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


# -------------------- SIDEBAR --------------------

with st.sidebar:
    st.markdown(
        '<div class="brand">🎬 Cine<span>Graph</span></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<p class="muted">Your AI movie companion</p>',
        unsafe_allow_html=True
    )

    st.divider()

    if st.button("＋ New conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_question = None
        st.rerun()

    st.markdown("### ✨ Suggested questions")

    suggestions = [
        "Who acted in The Matrix?",
        "Who directed The Matrix?",
        "Which movies did Tom Hanks act in?",
        "Recommend movies similar to The Matrix"
    ]

    for suggestion in suggestions:
        if st.button(suggestion, use_container_width=True):
            st.session_state.pending_question = suggestion
            st.rerun()

    st.divider()

    st.markdown("### 🧠 How it works")
    st.markdown(
        '<p class="muted">'
        'Neo4j retrieves facts from your movie graph. '
        'Gemini turns those facts into conversational answers.'
        '</p>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="footer">Neo4j · Cypher · Gemini · Streamlit</div>',
        unsafe_allow_html=True
    )


# -------------------- MAIN CHAT --------------------

st.markdown("""
<div class="hero">
    <div class="pill">AI MOVIE ASSISTANT</div>
    <h1>Let's talk movies. 🎬</h1>
    <p class="muted">
        Ask about movie casts, actors, directors and recommendations.
    </p>
</div>
""", unsafe_allow_html=True)


# Show welcome message only when the chat is empty.
if not st.session_state.messages:
    with st.chat_message("assistant", avatar="🎬"):
        st.markdown(
            "Hi! I'm **CineGraph**, your movie assistant. "
            "Ask me a question about movies, actors or directors, "
            "and I'll search the knowledge graph for an answer."
        )


# Display all previous messages on every rerun.
for message in st.session_state.messages:
    with st.chat_message(
        message["role"],
        avatar="🎬" if message["role"] == "assistant" else "🧑"
    ):
        st.markdown(message["content"])

        if message["role"] == "assistant" and message.get("data"):
            with st.expander("🔎 See facts retrieved from Neo4j"):
                st.json(message["data"])


# -------------------- CHAT INPUT --------------------
# This input remains available after every answer.

typed_question = st.chat_input(
    "Ask another movie question and press Enter..."
)

question = typed_question

# Allow suggested questions to use the same chat flow.
if st.session_state.pending_question:
    question = st.session_state.pending_question
    st.session_state.pending_question = None


# -------------------- PROCESS QUESTION --------------------

if question:
    # Add the user question to history.
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    # Retrieve facts and generate an answer.
    try:
        with st.spinner("Searching Neo4j and asking Gemini..."):
            answer, data, intent = answer_question(question)

    except Exception as error:
        answer = "Sorry, something went wrong. Please try again."
        data = []
        intent = "error"
        st.error(f"Technical details: {error}")

    # Save the assistant answer to history.
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "data": data,
        "intent": intent
    })

    # Rerender the full chat, preserving previous messages.
    st.rerun()
