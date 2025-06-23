"""
This is an example of asynchronous streaming output.

Be careful, if you don't initialize the state by deleting the corresponding thread id at the end, the output may become strange.
"""

# Python Standard Library imports
import asyncio

# Third-party Library imports
from langchain_core.messages import HumanMessage

# Custom Library imports
from sc2editor.llm import SC2EditorLLM


if __name__ == '__main__':
    async def streaming():
        async with SC2EditorLLM() as llm:
            thread_id = "sc2"
            prompt = 'When a unit is selected, how can I output the text "Unit selected!"'

            async for msg, metadata in llm.astream({'messages': [HumanMessage(prompt)]}, thread_id=thread_id):
                if metadata['langgraph_node'] in ('answer_node', 'disallow_node'):
                    print(msg.content, end="", flush=True)
            llm.delete_thread_id(thread_id=thread_id)

    asyncio.run(streaming())