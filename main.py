from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="NUTRILENS AI Backend",
    description="AI-Powered Diet & Calorie Intelligence System",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "NUTRILENS AI Backend is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

from api.analyze import router as analyze_router
from api.auth import router as auth_router
from database import engine, Base

# Create Tables
# Create Tables Safely
try:
    if engine:
        Base.metadata.create_all(bind=engine)
        print("DATABASE: Connected and tables verified.")
    else:
        print("WARNING: Database engine is None. Running in offline mode.")
except Exception as e:
    print(f"WARNING: Database connection failed. Running in offline mode.\nError: {e}")

app.include_router(analyze_router, prefix="/api")
app.include_router(auth_router, prefix="/auth")
from api.foods import router as foods_router
app.include_router(foods_router, prefix="/api")

from api.lifestyle import router as life_router
app.include_router(life_router, prefix="/api")

from api.safety import router as safety_router
app.include_router(safety_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    # Use 0.0.0.0 to allow external access if needed, or 127.0.0.1 for local only
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
