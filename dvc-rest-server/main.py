from fastapi import FastAPI
from app.routes import router

app = FastAPI()

# Include the routes defined in routes.py
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)