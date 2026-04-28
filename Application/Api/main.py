from fastapi import FastAPI

from .database import create_mongo_client, get_mongo_db
from .routes import router

app = FastAPI(title="API ville de Paris")


@app.on_event("startup")
def startup():
    app.state.mongo_client = create_mongo_client()
    app.state.mongo_db = get_mongo_db(app.state.mongo_client)


@app.on_event("shutdown")
def shutdown():
    app.state.mongo_client.close()
    
app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {"message": "API ville de Paris - Utilisez /docs pour la documentation"}