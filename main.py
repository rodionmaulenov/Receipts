from fastapi import FastAPI

from app.routers import users
from app.routers import receipts

app = FastAPI()

app.include_router(users.router)
app.include_router(receipts.router)
