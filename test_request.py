import requests

response = requests.post(
    "http://127.0.0.1:5000/chat",
    json={"message": "What is AI?"},
    headers={"Content-Type": "application/json"}
)

print(response.json())
