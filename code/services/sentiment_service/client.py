import requests
import time
import random

# Replace this with your actual service URL
BASE_URL = "http://localhost:8000/sentiment"

# Sample texts for random sentiment testing
texts = [
    "I love this product!",
    "This is the worst experience I've had.",
    "It's okay, not great.",
    "Absolutely fantastic!",
    "Terrible, would not recommend.",
    "I'm feeling neutral about this.",
    "What a beautiful day!",
    "I’m so frustrated with this issue.",
]

def send_request():
    text = random.choice(texts)
    try:
        response = requests.get(BASE_URL, params={"text": text})
        print(f"[{time.strftime('%H:%M:%S')}] Sent: '{text}' | Response: {response.json()}")
    except Exception as e:
        print(f"Error sending request: {e}")

if __name__ == "__main__":
    while True:
        send_request()
        time.sleep(2)  # send a request every 2 seconds (adjust as needed)
