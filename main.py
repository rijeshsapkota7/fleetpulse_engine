from fastapi import FastAPI
from router import users, realtime, dispatch
from database.database import Base, engine

app = FastAPI(title="FleetPulse Engine")


Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(realtime.router)
app.include_router(dispatch.router)
@app.post("/")
def home():
    return {"Message" : "Welcome to FleetPulse Engine"}