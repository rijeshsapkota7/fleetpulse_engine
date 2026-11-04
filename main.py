from fastapi import FastAPI

app = FastAPI(title="FleetPulse Engine")

# app.include_router()

@app.post("/")
def home():
    return {"Message" : "Welcome to FleetPulse Engine"}