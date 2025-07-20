from fastapi import FastAPI
import uvicorn
from api_router.api_router import APIRouterManager
from config.config import setup_middleware

app = FastAPI(title="Kembang Kopi API", version="1.0.0")

# Setup middleware
setup_middleware(app)

# Initialize API router manager
api_router_manager = APIRouterManager()
app.include_router(api_router_manager.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)