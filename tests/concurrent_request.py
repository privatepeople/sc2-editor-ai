import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


def send_request(conversation_id: str):
    prompt = "Can you tell me what kind of AI you are?"
    response = requests.post("http://127.0.0.1:8080/chat/stream", json={
                                                                            "message": prompt,
                                                                            "conversation_id": conversation_id,
                                                                            "history": [
                                                                                {
                                                                                "role": "user",
                                                                                "content": prompt
                                                                                }
                                                                            ]
                                                                        },
                                                                        stream=True)
    return response


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(send_request, str(i)) for i in range(10)]
        success = fail = 0

    for future in as_completed(futures):
        result = future.result()
        if result.ok:
            success += 1
            for line in result.iter_lines():
                if line:
                    print(line.decode('utf-8'))
        else:
            fail += 1
        result.close()
    
    print(f"Success: {success}, Fail: {fail}")