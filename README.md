# StarCraft 2 Editor AI

This project is an **LLM-powered assistant for the StarCraft 2 Editor**, built using [Google Gemini API Free Tier](https://ai.google.dev/gemini-api/docs).

---

## LLM Architecture

A detailed graph of a **single-agent architecture** using LangGraph is shown in the image below.

![LLM Architecture](./graph.png)

---

## Tech Stack

* **Package/Project Management**: uv
* **Linting/Formatting**: Ruff
* **Configuration**: PyYAML, Pydantic Settings
* **Dependency Injection**: Dependency Injector
* **Security**: bcrypt, PyJWT
* **Backend**: FastAPI, Uvicorn, SlowApi
* **LLM**: LangChain, LangGraph
* **Graph Database**: Neo4j AuraDB

---

## Features

* **logging**: Process tracking based on logging
* **API access control via login**: APIs that clients should not access can only be used by logging in.
* **Asynchronous Streaming**: When multiple requests occur at the same time, the response is not delayed asynchronously, and the client's request is responded to through streaming.
* **Global API limits**: Control the total usage per minute of specific APIs based on the value of api_limit set in config.yaml.
* **Conversation history background task**: A background task that deletes conversation history from memory that is older than the conversation_timeout set in config.yaml.

---

## Requirements

* **Python**: 3.12 or higher  
  It is recommended to use `uv` for package and project management.
* **Google Gemini API KEY**
* **Neo4j AuraDB Instance**

Refer to each service's official documentation for installation and setup instructions.

---

## Environment Variables Configuration

Create a `.env` file in the **root directory** with the following structure:

```env
GOOGLE_API_KEY=

NEO4J_URI=
NEO4J_USERNAME=
NEO4J_PASSWORD=
AURA_INSTANCEID=
AURA_INSTANCENAME=

ADMIN_USERNAME=
ADMIN_PASSWORD=

JWT_SECRET_KEY=
ALGORITHM=

UVICORN_HOST=
UVICORN_PORT=

# Optional
LANGSMITH_TRACING=
LANGSMITH_ENDPOINT=
LANGSMITH_PROJECT=
LANGCHAIN_API_KEY=
```

---

## Database Initialization

1. Create a Neo4j AuraDB instance.
2. Ensure your `.env` file contains the correct Neo4j credentials.
3. Run the following scripts to build the graph database:

```bash
python -m database/graph_database.py
python -m database/embedding_property.py
```

**※ Warning**: <ins>Building a Neo4j graph database this way costs real money because it uses Gemini API. I used about 890k tokens based on gemini-2.0-flash and text-embedding-004.</ins>

---

## How to Run

From the root directory:

```bash
python main.py
```

When the host is 127.0.0.1 and the port is 8000, if you enter the URL as 127.0.0.1:8000, the webpage will appear.
If you need to log in as an administrator, add the path as \admin.

The locations of the data used in this project are as follows. When adding data later, you can use the same locations.
At this time, the extension must be .md, which is a Markdown extension.

```
sc2editor/datas/new_tutorials/
```

---

## Data Sources

The sources of data used in this project are as follows:

🔗 [StarCraft 2 Editor Guides](https://s2editor-guides.readthedocs.io/)

---