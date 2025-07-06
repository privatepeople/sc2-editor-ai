"""
Module for adding embedding property to Neo4j Database.

This module extracts text from the text property of the Document label,
creates an embedding, and stores it in the embedding property.

If you want to run this file, type the command below in the backend directory.

uv run python -m database.embedding_property
"""

# Third-party Library imports
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_neo4j import Neo4jVector

# Custom Library imports
from utils import print_time
from config import get_settings


@print_time
def main(embedding: str, url: str, username: str, password: str):
    """
    Main Function to add embedding properties to Neo4j Database.

    Args:
        embedding: Gemini Embedding Model
        url: Neo4j Database URL
        username: The username of Neo4j Database account
        password: The password of Neo4j Database account
    """
    # Add embedding property
    Neo4jVector.from_existing_graph(
        GoogleGenerativeAIEmbeddings(model=embedding),
        search_type="hybrid",
        node_label="Document",
        text_node_properties=["text"],
        embedding_node_property="embedding",
        url=url,
        username=username,
        password=password,
    )


if __name__ == "__main__":
    settings = get_settings()
    main(
        embedding=settings.llm.embedding,
        url=settings.neo4j_uri,
        username=settings.neo4j_username,
        password=settings.neo4j_password,
    )
