from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.database.database import engine
from app.database.models import Base

from app.routers.auth import router as auth_router
from app.routers.files import router as files_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://127.0.0.1", 
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "null",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

app.include_router(auth_router)
app.include_router(files_router)

@app.on_event("startup")
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("База данных инициализирована")
    
@app.on_event("shutdown")
async def shutdown_database():
    await engine.dispose()
    print("База данных закрыта")
    
    
if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)