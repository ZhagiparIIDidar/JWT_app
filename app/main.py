import uvicorn
from fastapi import FastAPI, APIRouter
from app.demo_jwt_auth import router as login_roter
app = FastAPI()

app.include_router(login_roter)
