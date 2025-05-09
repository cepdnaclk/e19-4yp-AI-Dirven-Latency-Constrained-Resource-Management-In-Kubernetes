import requests
import random
import time

TEXT_SAMPLES = [
    "I absolutely love this product!",
    "It's okay, not great.",
    "Terrible experience, would not recommend.",
    "I'm feeling neutral about this.",
    "What a fantastic service!",
    "This is the worst I've ever had.",
    "Could be better.",
    "I'm so happy with the results!",
    "I wouldn't use this again.",
    "Pretty decent overall.",
    "Absolutely horrible.",
    "Highly recommended!",
    "I'm extremely disappointed.",
    "Good quality and fast service.",
    "It didn’t meet my expectations.",
    "Very satisfied!",
    "Regret buying it.",
    "Nothing special, but okay.",
    "Exceeded my expectations!",
    "Total waste of money."
]

SERVICE_URL = "http://sentiment-service/sentiment"

while True:
    text = random.choice(TEXT_SAMPLES)
    try:
        res = requests.get(SERVICE_URL, params={"text": text})
        print(f"Sent: {text} | Status: {res.status_code} | Response: {res.json()}")
    except Exception as e:
        print(f"Request failed: {e}")
    time.sleep(random.uniform(0.5, 2.0))  # Random delay between requests
