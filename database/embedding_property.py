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
from config import GOOGLE_API_KEY, EMBEDDING, NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD


@print_time
def main():
    """Main Function to add embedding properties to Neo4j Database."""
    # Add embedding property
    vector_index = Neo4jVector.from_existing_graph(
                                                    GoogleGenerativeAIEmbeddings(model=EMBEDDING, api_key=GOOGLE_API_KEY),
                                                    search_type="hybrid",
                                                    node_label="Document",
                                                    text_node_properties=["text"],
                                                    embedding_node_property="embedding",
                                                    url=NEO4J_URI,
                                                    username=NEO4J_USERNAME,
                                                    password=NEO4J_PASSWORD,
                                                )


if __name__ == "__main__":
    main()