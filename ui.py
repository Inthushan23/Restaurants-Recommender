import requests

payload = {
    "user_id": "E9kcWJdJUHuTKfQurPljwA",
    "user_input": "I want a calm french restaurant to eat with my family (we are 5 including 3 kids) this evening. My son is in a wheelchair.",
    "top_k": 10
}

r = requests.post("http://localhost:8000/recommender/get_rec", json=payload)
if r:
    print(r.json())
else: 
    print("Erreur")
