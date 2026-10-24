\# MovieGraphRAG — Movie Knowledge Graph Chatbot



\## Overview



MovieGraphRAG is a movie question-answering and recommendation chatbot that combines a Neo4j knowledge graph with Google's Gemini API. It allows users to ask natural-language questions about movies, retrieve related information from the graph, and discover movies connected through shared actors.



The application provides an interactive chat interface built using Streamlit.



\## Features



\- Ask natural-language questions about movies.

\- Retrieve movie and actor information from a Neo4j graph database.

\- Generate conversational answers using the Gemini API.

\- Recommend related movies based on shared actors.

\- View chat history and suggested questions.

\- Inspect retrieved graph facts through expandable sections.



\## Technologies Used



\- \*\*Python\*\* — application logic

\- \*\*Streamlit\*\* — frontend and chat interface

\- \*\*Neo4j AuraDB\*\* — graph database and Cypher queries

\- \*\*Google Gemini API\*\* — natural-language answer generation

\- \*\*google-genai\*\* — Gemini Python SDK

\- \*\*neo4j\*\* — Neo4j Python driver

\- \*\*python-dotenv\*\* — environment variable configuration



\## Project Structure



```text

MovieGraphRAG/

├── app.py

├── movie\_chat.py

├── movie\_details.py

├── movie\_search.py

├── movie\_test.py

├── check\_models.py

├── test\_connection.py

├── requirements.txt

├── .gitignore

└── README.md

```



\- `app.py` — Streamlit frontend and application entry point.

\- `movie\_chat.py` — movie-chat functionality.

\- `movie\_details.py` — movie information retrieval utilities.

\- `movie\_search.py` — movie search functionality.

\- `movie\_test.py` — movie-related testing script.

\- `check\_models.py` — utility for checking available Gemini models.

\- `test\_connection.py` — database connection testing utility.



\## Architecture



1\. The user enters a question in the Streamlit interface.

2\. The application processes the question and selects the relevant retrieval logic.

3\. Cypher queries retrieve relevant movie and actor information from Neo4j.

4\. The Gemini API generates a natural-language response using the retrieved information.

5\. Streamlit displays the answer and related movie recommendations.



\*\*Note:\*\* The current project uses Python modules for backend logic and `app.py` as the frontend/application entry point. It does not require a separate HTTP backend server unless one is added later.



\## Prerequisites



Install or prepare the following:



\- Python 3.10 or a compatible version supported by the installed dependencies.

\- A Neo4j database, such as Neo4j AuraDB.

\- A Google Gemini API key.

\- Git, if you want to clone the repository.



\## Setup Instructions



\### 1. Clone the repository



```bash

git clone https://github.com/ramyasjoshi2005/MovieGraphRAG.git

cd MovieGraphRAG

```



Alternatively, download the repository as a ZIP file and extract it.



\### 2. Create a virtual environment



\*\*Windows PowerShell:\*\*



```powershell

python -m venv .venv

.\\.venv\\Scripts\\Activate.ps1

```



If PowerShell blocks environment activation, you can run the virtual environment's Python executable directly or use Command Prompt activation instead.



\### 3. Install dependencies



```bash

python -m pip install --upgrade pip

pip install -r requirements.txt

```



\### 4. Configure environment variables



Create a file named `.env` in the project root. Add the Neo4j connection details and Gemini API key using the variable names expected by the application.



A typical configuration looks like this:



```dotenv

NEO4J\_URI=your\_neo4j\_uri

NEO4J\_USERNAME=your\_neo4j\_username

NEO4J\_PASSWORD=your\_neo4j\_password

GEMINI\_API\_KEY=your\_gemini\_api\_key

```



Replace the example values with your own credentials. If the Python code uses different environment variable names, use those exact names instead.



\*\*Security:\*\* Never commit `.env` or publish API keys, database passwords, or other credentials to GitHub.



\### 5. Verify the database connection



If `test\_connection.py` is configured to test your Neo4j connection, run:



```bash

python test\_connection.py

```



Resolve any connection or credential errors before starting the application.



\## Running the Application



\### Backend / graph retrieval logic



The backend logic runs through the Python modules used by the application. It connects to Neo4j, executes graph queries, retrieves movie information, and passes relevant results to the answer-generation logic.



There is no separate backend server command in the current architecture. The backend functions are called by the Streamlit application.



Optional utility scripts can be run individually when needed:



```bash

python movie\_search.py

python movie\_details.py

python movie\_chat.py

```



These commands are applicable only if the corresponding files include executable entry points or test code.



\### Frontend — Streamlit



From the project root, with the virtual environment activated, run:



```bash

streamlit run app.py

```



Streamlit will display a local URL in the terminal, usually:



```text

http://localhost:8501

```



Open that address in your browser to interact with the chatbot.



Stop the application by pressing `Ctrl+C` in the terminal.



\## Example Questions



\- Who acted in \*The Matrix\*?

\- Which movies share actors with \*The Matrix\*?

\- Find movies connected to a particular actor.

\- What other movies are related to this movie through shared actors?



The exact questions supported depend on the retrieval functions implemented in the project.



\## Dependencies



The Python dependencies are listed in `requirements.txt`. The primary packages are:



\- `streamlit`

\- `neo4j`

\- `google-genai`

\- `python-dotenv`



Install them with:



```bash

pip install -r requirements.txt

```



\## Limitations



\- Answers depend on the data available in the Neo4j graph.

\- Movie recommendations based on shared actors indicate graph connections, not necessarily similarity in plot, genre, or theme.

\- Gemini API access and Neo4j database access require valid credentials and may be subject to usage limits.



\## Future Improvements



\- Add genre- and plot-based recommendation methods.

\- Improve error handling and database connection management.

\- Add automated tests for retrieval and recommendation functions.

\- Deploy the Streamlit application for public access.



\## Author



\*\*Ramya Joshi\*\*



GitHub: \[@ramyasjoshi2005](https://github.com/ramyasjoshi2005)



\## License



No license has been specified yet. Contact the author before reusing or redistributing this project.



