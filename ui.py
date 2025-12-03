import requests

payload = {
    "user_id": "qVc8ODYU5SZjKXVBgXdI7w",
    "user_input": "I want a calm french restaurant to eat with my family (we are 5 including 3 kids) this evening. My son is in a wheelchair.",
    "top_k": 10
}

r = requests.post("http://localhost:8000/recommender/", json=payload)
if r:
    print(r.json())
else: 
    print("Erreur")
