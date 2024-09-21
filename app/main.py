from fastapi import FastAPI

from app.routers import users, receipts

app = FastAPI(
    title="Receipt API",
    description="This is an API for creating and viewing receipts with user registration and authentication.",
    version="1.0.0",
    contact={
        "name": "Oleksandr Chaban",
        "email": "toer1xe@gmail.com",
    },
)

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(receipts.router, prefix="/receipts", tags=["receipts"])


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
