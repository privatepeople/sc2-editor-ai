# Python Standard Library imports
import asyncio
from random import choice

# Third-party Library imports
from langchain_core.messages import HumanMessage

# Custom Library imports
from sc2editor.llm import SC2EditorLLM


if __name__ == '__main__':
    async def test():
        async with SC2EditorLLM() as llm:
            thread_id = "sc2"
            prompts = [
                'When a unit is selected, how can I output the text "Unit selected!"',
                "Please tell me how to make it so that every time I press the 1 key on my keyboard, it outputs 'low' by default, but every 10th time, it outputs 'High Reset'.",
                "Please tell me how to output the number of dead marines as text every time a marine dies in the game.",
                "Please tell me how to increase the health of a marine by 5 when it enters a certain area.",
                "Please tell me how to reduce a Marine's health by 5 when entering a specific area.",
                """Please tell me how to add the text "I am a marine!" above the marine's head.""",
                "Please tell me how to attach the damage dealt by Dehaka as text on top of Dehaka's head.",
                "Please tell me how to create a Debug Cheat.",
                "Please tell me how to make a marine spawn on the map every second, and separately print out the total number of marines on the map as text every 5 seconds.",
                "Please tell me how to kill a mutalisk by clicking on it 5 times using data editor in the game.",
                "Please tell me how to add an aura to marine that increases the movement speed of surrounding units.",
                "Please tell me how to control units with the wasd keys on the keyboard."
            ]
            prompt = choice(prompts)

            async for msg, metadata in llm.astream({'messages': [HumanMessage(prompt)]}, thread_id=thread_id):
                if metadata['langgraph_node'] in ('answer_node', 'disallow_node'):
                    print(msg.content, end="", flush=True)
            llm.delete_thread_id(thread_id=thread_id)

    asyncio.run(test())