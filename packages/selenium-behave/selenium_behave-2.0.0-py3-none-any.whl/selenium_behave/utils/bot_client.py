import uuid, requests

def get_bot_response(utterance):
    url = "https://endpoint-frontier.cognigy.cloud/e955fa33b9211e4eeb8929779662f78c856852c2412d45c8158a222311eb795f"
    headers = {"Content-Type": "application/json"}
    session_id = str(uuid.uuid4())
    payload = {"userId": "12345", "sessionId": session_id, "text": utterance, "data": {}}
    resp = requests.post(url, headers=headers, json=payload, timeout=10)
    data = resp.json()
    return data.get("text", ""), session_id
