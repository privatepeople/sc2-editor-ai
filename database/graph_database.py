"""
Module for building a graph database.

This module splits a Markdown document into text, converts it to a LangChain GraphDocument,
and then stores it in Neo4j Database. At this time, LLM is used to convert to Graph Document.

If you want to run this file, type the command below in the backend directory.

uv run python -m database.graph_database
"""

# Third-party Library imports
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_neo4j import Neo4jGraph

# Custom Library imports
from utils import print_time
from config import get_settings
from sc2editor.text_splitters import markdown_load_split


def setup_llm_and_transformer(model: str) -> tuple[ChatGoogleGenerativeAI, LLMGraphTransformer]:
    """
    Function to set up LLM and Graph Transformer objects.

    Args:
        model: Gemini LLM Model
    
    Returns:
        Returns a tuple of LLM and GraphTransformers that use the LLM.
    """
    llm = ChatGoogleGenerativeAI(model=model, temperature=0)
    llm_transformer = LLMGraphTransformer(llm=llm)
    
    return llm, llm_transformer


def query_database_stats(graph: Neo4jGraph) -> tuple[dict[str, int], dict[str, int]]:
    """
    A function that sends a query to a neo4j graph database and returns statistics.
    
    Args:
        graph: Neo4j Database
    
    Returns:
        Returns the number of total nodes and the number of total relationships as a tuple.
        The elements of a tuple are organized as follows:
        
        ({'TotalNodes': Total number of nodes}, {'TotalRelationships': Total number of relationships})
    """
    # Query total number of nodes
    node_count_query = """
    MATCH (n)
    RETURN count(n) AS TotalNodes;
    """
    node_result = graph.query(node_count_query)[0]

    # Query the total number of relationships
    relationship_count_query = """
    MATCH ()-[r]->()
    RETURN count(r) AS TotalRelationships;
    """
    relationship_result = graph.query(relationship_count_query)[0]
    
    return node_result, relationship_result


@print_time
def main(model: str, url: str, username: str, password: str):
    """
    Main Function to split text in Markdown document and add it to Neo4j Database.
    
    Args:
        model: Gemini LLM Model
        url: Neo4j Database URL
        username: The username of Neo4j Database account
        password: The password of Neo4j Database account
    """
    # Set up LLM and Graph Transformer
    llm, llm_transformer = setup_llm_and_transformer(model=model)
    
    # Load and preprocess documents
    documents = markdown_load_split()
    
    # Convert Langchain Documents to Graph Documents
    graph_documents = llm_transformer.convert_to_graph_documents(documents)
    
    # Get Neo4j credentials and create connection
    graph = Neo4jGraph(url, username, password)
    
    # Add Graph Documents to Graph Database
    graph.add_graph_documents(
                                graph_documents=graph_documents,
                                include_source=True,
                                baseEntityLabel=True
                            )
    
    # Query and display statistics
    node_result, relationship_result = query_database_stats(graph)
    
    print()
    print("Number of total nodes: ", node_result["TotalNodes"])
    print("Number of total relationships: ", relationship_result["TotalRelationships"])

    # Close the connection
    graph.close()


if __name__ == "__main__":
    settings = get_settings()
    main(model=settings.llm.model, url=settings.neo4j_uri, username=settings.neo4j_username, password=settings.neo4j_password)