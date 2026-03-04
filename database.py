import json
import os
from config import DATABASE_FILE

def load_data():
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r") as file:
            content = file.read().strip()
            if not content:
                return {"users": [], "analyses": []}
            data = json.loads(content)
            if isinstance(data, dict):
                return data
    return {"users": [], "analyses": []}

def save_data(data):
    with open(DATABASE_FILE, "w") as file:
        json.dump(data, file, indent=2)