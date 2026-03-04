import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()  # .env file load karo

DATABASE_FILE = "database.json"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable set nahi hai!")  # server start hi nahi hoga