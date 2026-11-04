from fastapi import FastAPI
from router import users

app = FastAPI(title="FleetPulse Engine")

app.include_router(users.router)

@app.post("/")
def home():
    return {"Message" : "Welcome to FleetPulse Engine"}