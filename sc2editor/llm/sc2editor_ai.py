"""
Integrated module related to LLM

This module integrates several other modules to provide LLM services.

Note that after finishing the LLM answer, you must initialize the graph state with the delete_thread_id method of the SC2EditorLLM class.
"""

# Python Standard Library imports
from math import floor
from typing import Annotated, Literal, TypedDict, AsyncIterator, Any

# Third-party Library imports
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langchain_neo4j import Neo4jGraph, Neo4jVector

# Custom Library imports
from config import *
from sc2editor.llm.system_prompts import *


class Router(BaseModel):
    """A model that determines whether to allow or disallow prompts."""
    prompt_status: Literal['allow', 'disallow'] = Field(
                                                        description="Status indicating whether the prompt is allowed or not allowed."
                                                        )


class Entities(BaseModel):
    """A model that extracts named entities and key concepts from text."""
    keywords: list[str] = Field(
                                default_factory=list,
                                description="A list of key concepts or keywords mentioned in the text."
                                )


class AnswerJudgment(BaseModel):
    "This is a model that determines whether an answer is possible based on the conversation history up to this point and the given context."
    answer_status: Literal['yes', 'no'] = Field(
                                                    description="Status to check whether or not an answer can be given with the given information."
                                                )


class State(TypedDict):
    messages: Annotated[list[BaseMessage], "The conversation history up to this point, including the current prompt."]
    prompt_status: Literal['allow', 'disallow']
    keywords: Annotated[list[str], "A list of key concepts or keywords mentioned in the prompt."]
    graph_context: Annotated[str, "Graph Data retrieved from graph retriever"]
    vector_context: Annotated[str, "Vector Data retrieved from vector retriever"]
    context: Annotated[str, "Reference to use in answer"]
    retriever_attempt_count: Annotated[int, "The number of retriever attempts."]
    retriever_query: Annotated[str, "Query information needed for answering"]
    answer_allow_status: Literal['yes', 'no']
    answer: Annotated[str, "Answers to prompt"]


class SC2EditorLLM:
    """SC2 Editor LLM system that handles database connections, retrieval, and conversation processing."""
    
    def __init__(self, neo4j_uri: str = NEO4J_URI, neo4j_username: str = NEO4J_USERNAME, 
                 neo4j_password: str = NEO4J_PASSWORD, google_api_key: str = GOOGLE_API_KEY,
                 model: str = MODEL, embedding_model: str = EMBEDDING,
                 maximum_information_acquisition_rate: int | float = MAXIMUM_INFORMATION_ACQUISITION_RATE, maximum_retriever_attempts: int = MAXIMUM_RETRIEVER_ATTEMPTS):
        """
        Initialize the SC2EditorLLM with database connections and models.
        
        Args:
            neo4j_uri: Neo4j database URI
            neo4j_username: Neo4j username
            neo4j_password: Neo4j password
            google_api_key: Google API key for LLM and embeddings
            model: Google Generative AI model name
            embedding_model: Embedding model name
            maximum_information_acquisition_rate: Maximum information rate obtained from retriever (Values ​​from 0 to 1)
            maximum_retriever_attempts: Maximum of retriever attempts
        """
        self.neo4j_uri = neo4j_uri
        self.neo4j_username = neo4j_username
        self.neo4j_password = neo4j_password
        self.google_api_key = google_api_key
        self.model = model
        self.embedding_model = embedding_model
        self.maximum_information_acquisition_rate = maximum_information_acquisition_rate
        self.maximum_retriever_attempts = maximum_retriever_attempts
        
        # Initialize connections
        self.neo4j_graph = None
        self.vector_retriever = None
        self.graph = None
        self._is_initialized = False

        self.initialize()
    
    def __enter__(self):
        """Context manager entry"""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        return None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        self.close()
        return None
    
    def initialize(self):
        """Initialize database connections and build the graph"""
        if self._is_initialized:
            return None
        
        # Initialize Neo4j graph connection
        self.neo4j_graph = Neo4jGraph(self.neo4j_uri, self.neo4j_username, self.neo4j_password)

        # Retrieving statistics from a Neo4j database
        self._neo4j_statistics()

        # Initialize vector retriever
        # Since embedding_text is small in size, add a ratio
        additional_ratio = 0
        k = floor(self.embedding_text_count * (self.maximum_information_acquisition_rate + additional_ratio))
        self.vector_retriever = Neo4jVector.from_existing_graph(
                                                                GoogleGenerativeAIEmbeddings(model=self.embedding_model, api_key=self.google_api_key),
                                                                search_type="hybrid",
                                                                node_label="Document",
                                                                text_node_properties=["text"],
                                                                embedding_node_property="embedding",
                                                                url=self.neo4j_uri,
                                                                username=self.neo4j_username,
                                                                password=self.neo4j_password,
                                                                ).as_retriever(
                                                                                search_kwargs={'k': k}
                                                                                )
        
        # Build the state graph
        self.builder = self._create_graph()
        self.graph = self.builder.compile(checkpointer=self.checkpointer)
        self._is_initialized = True
    
    def close(self):
        """Close database connections and cleanup resources"""
        if self.neo4j_graph:
            self.neo4j_graph.close()
            self.neo4j_graph = None
        
        self.vector_retriever = None
        self.graph = None
        self._is_initialized = False
    
    def _ensure_initialized(self):
        """Ensure the system is initialized before use"""
        if not self._is_initialized:
            raise RuntimeError("SC2EditorLLM must be initialized before use. Call initialize() or use as context manager.")
    
    def save_graph_visualization(self, output_path: str = './graph.png'):
        """
        Save a visualization of the state graph.
        
        Args:
            output_path: Path where to save the graph image
        """
        self._ensure_initialized()
        self.graph.get_graph().draw_mermaid_png(output_file_path=output_path)
    
    def _neo4j_statistics(self):
        """Method to get statistics such as total number of nodes, total number of relationships, number of embedded texts, etc. in Neo4j database"""
        # Query total number of nodes
        node_count_query = """
        MATCH (n)
        RETURN count(n) AS TotalNodes;
        """
        node_result = self.neo4j_graph.query(node_count_query)[0]
        self.node_count = node_result['TotalNodes']

        # Query the total number of relationships
        relationship_count_query = """
        MATCH ()-[r]->()
        RETURN count(r) AS TotalRelationships;
        """
        relationship_result = self.neo4j_graph.query(relationship_count_query)[0]
        self.relationship_count = relationship_result['TotalRelationships']

        # Query the total number of embedding texts
        embedding_text_count_query = """
        MATCH (d:Document)
        WHERE d.embedding IS NOT NULL
        RETURN count(d) AS EmbeddingText;
        """
        embedding_text_result = self.neo4j_graph.query(embedding_text_count_query)[0]
        self.embedding_text_count = embedding_text_result['EmbeddingText']
    
    def _create_chains(self):
        """Configures and creates all the chains to be used in the graph"""
        # router_node
        router_model = ChatGoogleGenerativeAI(model=MODEL, temperature=0, api_key=self.google_api_key)
        router_prompt = ChatPromptTemplate.from_messages(
                                                        [
                                                            (
                                                                'system',
                                                                ROUTER_SYSTEM_PROMPT
                                                            ),
                                                            (
                                                                'human',
                                                                "Please decide whether to allow prompts based on the conversation history including the current prompt.\n\n"
                                                                "Conversation History:\n{messages}"
                                                            )
                                                            
                                                        ]
                                                    )
        self._router_node_chain = router_prompt | router_model.with_structured_output(Router)

        # disallow_node
        self._disallow_node_chain = ChatGoogleGenerativeAI(model=MODEL, temperature=0.3, api_key=self.google_api_key)

        # entity_extract_node
        entity_extract_model = ChatGoogleGenerativeAI(model=MODEL, temperature=0, api_key=self.google_api_key)
        entity_extract_prompt = ChatPromptTemplate.from_messages(
                                                    [
                                                        (
                                                            'system',
                                                            ENTITY_EXTRACTION_SYSTEM_PROMPT
                                                        ),
                                                        (
                                                            'human',
                                                            "{message}"
                                                        )
                                                    ]
                                                )
        self._entity_extract_node_chain = entity_extract_prompt | entity_extract_model.with_structured_output(Entities)

        # retriever_query_node
        retriever_query_model = ChatGoogleGenerativeAI(model=MODEL, temperature=0.3, api_key=self.google_api_key)
        retriever_query_prompt = ChatPromptTemplate.from_messages(
                                                        [
                                                            (
                                                                'system',
                                                                RETRIEVER_QUERY_SYSTEM_PROMPT
                                                            ),
                                                            (
                                                                'human',
                                                                "Please write a natural language query necessary for the answer based on the context and the conversation history so far.\n\n"
                                                                "Context:\n{context}\n\n"
                                                                "Conversation History:\n{messages}"
                                                            )
                                                            
                                                        ]
                                                    )
        self._retriever_query_node_chain = retriever_query_prompt | retriever_query_model

        # context_cleanup_node
        context_cleanup_model = ChatGoogleGenerativeAI(model=MODEL, temperature=0, api_key=self.google_api_key)
        context_cleanup_prompt = ChatPromptTemplate.from_messages(
                                                        [
                                                            (
                                                                'system',
                                                                CONTEXT_CLEANUP_SYSTEM_PROMPT
                                                            ),
                                                            (
                                                                'human',
                                                                "Please refer to the conversation history so far and organize unnecessary context in your answer.\n\n"
                                                                "Conversation History:\n{messages}\n\n"
                                                                "Context:\n{context}"
                                                            )
                                                            
                                                        ]
                                                    )
        self._context_cleanup_node_chain = context_cleanup_prompt | context_cleanup_model

        # answer_judgment_node
        answer_judgment_model = ChatGoogleGenerativeAI(model=MODEL, temperature=0, api_key=self.google_api_key)
        answer_judgment_prompt = ChatPromptTemplate.from_messages(
                                                        [
                                                            (
                                                                'system',
                                                                ANSWER_JUDGMENT_SYSTEM_PROMPT
                                                            ),
                                                            (
                                                                'human',
                                                                "Please decide whether or not you can answer based on the given context and the conversation history so far.\n\n"
                                                                "Context:\n{context}\n\n"
                                                                "Conversation History:\n{messages}"
                                                            )
                                                            
                                                        ]
                                                    )
        self._answer_judgment_node_chain = answer_judgment_prompt | answer_judgment_model.with_structured_output(AnswerJudgment)

        # answer_node
        answer_model = ChatGoogleGenerativeAI(model=MODEL, temperature=0.3, api_key=self.google_api_key)
        answer_prompt = ChatPromptTemplate.from_messages(
                                                    [
                                                        SystemMessage(
                                                                        (
                                                                            f"{SC2_EDITOR_AI_SYSTEM_PROMPT}"
                                                                            "\n\n"
                                                                            "Additional Context:"
                                                                            "\n"
                                                                            "{context}"
                                                                        )
                                                                    ),
                                                        MessagesPlaceholder('messages'),
                                                    ]
                                                )
        self._answer_node_chain = answer_prompt | answer_model
    
    def _create_graph(self) -> StateGraph:
        """Configures and creates the StateGraph with all nodes and edges"""
        # Create chains
        self._create_chains()

        # Create StateGraph
        builder = StateGraph(State)
        
        # Add nodes
        builder.add_node('router_node', self._router_node)
        builder.add_node('disallow_node', self._disallow_node)
        builder.add_node('entity_extract_node', self._entity_extract_node)
        builder.add_node('retriever_attempt_node', self._retriever_attempt_node)
        builder.add_node('retriever_query_node', self._retriever_query_node)
        builder.add_node('retriever_node', self._retriever_node)
        builder.add_node('context_cleanup_node', self._context_cleanup_node)
        builder.add_node('answer_judgment_node', self._answer_judgment_node)
        builder.add_node('answer_node', self._answer_node)
        
        # Add edges
        builder.add_edge(START, 'router_node')
        builder.add_conditional_edges('router_node', self._check_progress)
        builder.add_edge('disallow_node', END)
        builder.add_edge('entity_extract_node', 'retriever_attempt_node')
        builder.add_conditional_edges('retriever_attempt_node', self._check_retriever_attempt)
        builder.add_edge('retriever_query_node', 'retriever_node')
        builder.add_edge('retriever_node', 'context_cleanup_node')
        builder.add_edge('context_cleanup_node', 'answer_judgment_node')
        builder.add_conditional_edges('answer_judgment_node', self._check_answer_judgment)
        builder.add_edge('answer_node', END)

        # Create checkpointer
        self.checkpointer = InMemorySaver()
        
        return builder
    
    def _format_messages(self, messages: list[BaseMessage]) -> str:
        """
        Format messages for prompt templates
        
        Args:
            messages: Conversation history list. Consists of 'SystemMessage', 'HumanMessage', 'AIMessage', etc.
        
        Returns:
            Conversation history converted to text
        """
        formatted_messages = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                formatted_messages.append(f"- Human: {msg.content}")
            elif isinstance(msg, AIMessage):
                formatted_messages.append(f"- AI: {msg.content}")
            elif isinstance(msg, SystemMessage):
                formatted_messages.append(f"- System: {msg.content}")
            else:
                formatted_messages.append(f"- Unknown: {msg.content}")

        return "\n".join(formatted_messages)
    
    # Node implementations
    async def _router_node(self, state: State) -> State:
        messages_text = self._format_messages(state['messages'])
        res = await self._router_node_chain.ainvoke({'messages': messages_text})

        return {'prompt_status': res.prompt_status}
    
    async def _check_progress(self, state: State) -> Literal['entity_extract_node', 'disallow_node']:
            if state['prompt_status'] == 'allow':
                return 'entity_extract_node'
            else:
                return 'disallow_node'
    
    async def _disallow_node(self, state: State) -> State:
        messages = [SystemMessage(DISALLOW_PROMPT)] + state['messages']
        res = await self._disallow_node_chain.ainvoke(messages)

        return {'answer': res.content}
    
    async def _entity_extract_node(self, state: State) -> State:
        res = await self._entity_extract_node_chain.ainvoke({'message': state['messages'][-1].content})

        return {'keywords': res.keywords}
    
    async def _retriever_attempt_node(self, state: State) -> State:
        attempt = state.get('retriever_attempt_count', 0) + 1
        return {'retriever_attempt_count': attempt}
    
    async def _check_retriever_attempt(self, state: State) -> Literal['retriever_query_node', 'answer_node']:
            if state['retriever_attempt_count'] <= self.maximum_retriever_attempts:
                return 'retriever_query_node'
            else:
                return 'answer_node'
    
    async def _retriever_query_node(self, state: State) -> State:
        context = state.get('context', "")
        messages_text = self._format_messages(state['messages'])
        res = await self._retriever_query_node_chain.ainvoke({'context': context, 'messages': messages_text})

        return {'retriever_query': res.content}
    
    async def _retriever_node(self, state: State) -> State:
        # Determine graph data limit based on attempt count
        graph_data_limit = floor((((self.node_count + self.relationship_count) * self.maximum_information_acquisition_rate) / self.maximum_retriever_attempts) * state['retriever_attempt_count'])
        
        # Import Graph Data
        # Based on whether each entity is included in the node id or text property of the graph, when a matching node is found, adjacent nodes and relationships are collected around that node.
        graph_data = ""

        for text_keyword in state['keywords']:
            response = self.neo4j_graph.query(
                    f"""
                    MATCH (node)
                    WHERE toLower(node.id) CONTAINS toLower($query) OR toLower(node.text) CONTAINS toLower($query)
                    MATCH (node)-[r]-(neighbor)
                    WHERE type(r) <> 'MENTIONS'
                    RETURN CASE
                        WHEN startNode(r) = node
                        THEN node.id + ' - ' + type(r) + ' -> ' + neighbor.id
                        ELSE neighbor.id + ' - ' + type(r) + ' -> ' + node.id
                    END AS output
                    LIMIT {graph_data_limit};
                    """,
                    {"query": text_keyword.lower()},
                )
            graph_data += "\n".join([el['output'] for el in response])
            if graph_data:
                graph_data += "\n"

        graph_data = f"""{graph_data.strip() if graph_data else "There is no associated graph data."}"""
        
        # Import Vector Data
        # Vector search based on embedding properties embedded in text properties of nodes with document labels
        vector_retriever_result = await self.vector_retriever.ainvoke(state['retriever_query'])

        if vector_retriever_result:
            vector_data_list = [''] * len(vector_retriever_result)
            for idx, langchain_doc in enumerate(vector_retriever_result):
                # Delete metadatas that doesn't help much
                del langchain_doc.metadata['source']
                del langchain_doc.metadata['languages']
                del langchain_doc.metadata['filetype']

                doc_trans_text_list = [f"{metadata_key}: \n{langchain_doc.metadata[metadata_key]}" for metadata_key in sorted(langchain_doc.metadata, key=lambda meta_key: meta_key.lower())]
                doc_text = f"""# Document\n{'\n'.join(doc_trans_text_list)}\n{langchain_doc.page_content.strip()}""".strip()
                vector_data_list[idx] = doc_text
                
            vector_data = '\n\n'.join(vector_data_list)
        else:
            vector_data = "There is no associated vector data."

        # Combining Graph Data and Vector Data
        final_data = (f"--- Search results ---"
                        "\n\n"
                        "[Graph Data]"
                        "\n\n"
                        f"{graph_data}"
                        "\n\n"
                        "[Vector Data]"
                        "\n\n"
                        f"{vector_data}"
                        )
        
        if 'context' not in state:
            context = final_data.strip()
        else:
            context = f"{state['context']}\n\n{final_data.strip()}".strip()
        
        return {'graph_context': graph_data, 'vector_context': vector_data, 'context': context}
    
    async def _context_cleanup_node(self, state: State) -> State:
        messages_text = self._format_messages(state['messages'])
        res = await self._context_cleanup_node_chain.ainvoke({'context': state['context'], 'messages': messages_text})

        return {'context': res.content}
    
    async def _answer_judgment_node(self, state: State) -> State:
        messages_text = self._format_messages(state['messages'])
        res = await self._answer_judgment_node_chain.ainvoke({'context': state['context'], 'messages': messages_text})

        return {'answer_allow_status': res.answer_status}
    
    async def _check_answer_judgment(self, state: State) -> Literal['retriever_attempt_node', 'answer_node']:
            if state['answer_allow_status'] == 'yes':
                return 'answer_node'
            else:
                return 'retriever_attempt_node'
    
    async def _answer_node(self, state: State) -> State:
        res = await self._answer_node_chain.ainvoke({'context': state['context'], 'messages': state['messages']})

        return {'answer': res.content}
    
    def astream(self, messages: dict[str, list[BaseMessage]], thread_id: str, stream_mode: str = 'messages') -> AsyncIterator[dict[str, Any] | Any]:
        """
        Method that asynchronously streams token-by-token output.

        Once the answer is finished, you should delete the corresponding thread_id.
        
        Args:
            messages: This is the conversation history so far, including the current prompt. The dictionary must have only one key: 'messages'.
            thread_id: It is an identifier. It uses a value using uuid4.
            stream_mode: The mode to stream output, defaults to 'messages'.
                Options are:

                - `"values"`: Emit all values in the state after each step, including interrupts.
                    When used with functional API, values are emitted once at the end of the workflow.
                - `"updates"`: Emit only the node or task names and updates returned by the nodes or tasks after each step.
                    If multiple updates are made in the same step (e.g. multiple nodes are run) then those updates are emitted separately.
                - `"custom"`: Emit custom data from inside nodes or tasks using `StreamWriter`.
                - `"messages"`: Emit LLM messages token-by-token together with metadata for any LLM invocations inside nodes or tasks.
                    Will be emitted as 2-tuples `(LLM token, metadata)`.
                - `"debug"`: Emit debug events with as much information as possible for each step.

                You can pass a list as the `stream_mode` parameter to stream multiple modes at once.
                The streamed outputs will be tuples of `(mode, data)`.
        
        Returns:
            If stream_mode is 'messages', which is the default, an asynchronous Iterator consisting of (message_chunk, metadata) is returned.
            'message_chunk', 'metadata' are as follows:

            - message_chunk: the token or message segment from the LLM.
            - metadata: a dictionary containing details about the graph node and LLM invocation.
        
        Examples:
        >>> async def streaming():
        ...     async with SC2EditorLLM() as llm:
        ...         thread_id = "sc2"
        ...         async for msg, metadata in llm.astream({'messages': [HumanMessage('When a unit is selected, how can I output the text "Unit selected!"')]}, thread_id=thread_id):
        ...             if metadata['langgraph_node'] in ('answer_node', 'disallow_node'):
        ...                 print(msg.content, end="", flush=True)
        ...         llm.delete_thread_id(thread_id=thread_id)
        >>> asyncio.run(streaming())
        """
        return self.graph.astream(messages, {'configurable': {'thread_id': thread_id}}, stream_mode=stream_mode)
    
    def delete_thread_id(self, thread_id: str):
        """
        Method to delete the corresponding thread_id from InMemorySaver.
        
        Args:
            thread_id: It is an identifier. It uses a value using uuid4.
        """
        self.checkpointer.delete_thread(thread_id)