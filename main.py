from fastapi import FastAPI
from auth_routes import router as auth_router
from user_routes import router as user_router

app = FastAPI()

app.include_router(auth_router)   # /register, /login
app.include_router(user_router)   # /users, /analyze (protected)