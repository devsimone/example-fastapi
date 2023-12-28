from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run
from app.routers import post, user, auth, vote


from app import models
from database import engine

# we no longer need the below line as alembic is going take care to create the DB tables from our models
models.Base.metadata.create_all(bind=engine)  # It creates all of our SQLAlchemy models

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get("/")
def root():
    return {"message": "Hello world!"}


if __name__ == '__main__':
    run("app.main:app", host="0.0.0.0", port=8000, reload=True)
