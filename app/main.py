import uvicorn
from fastapi import FastAPI, APIRouter
from demo_jwt_auth import router as login_roter
app = FastAPI()

app.include_router(login_roter)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8000)