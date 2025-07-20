from fastapi import FastAPI
import uvicorn
from api_router.api_router import APIRouterManager
from config.config import setup_middleware, Config

# Validate configuration on startup
Config.validate_config()

app = FastAPI(
    title="Kembang Kopi API", 
    version="1.0.0",
    description="Real-time Order Management System for Kembang Kopi",
    debug=Config.DEBUG
)

# Setup middleware
setup_middleware(app)

# Initialize API router manager
api_router_manager = APIRouterManager()
app.include_router(api_router_manager.router)

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host=Config.HOST, 
        port=Config.PORT,
        reload=Config.DEBUG
    )
