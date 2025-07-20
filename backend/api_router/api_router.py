# api-client.py
import os
from fastapi import APIRouter
from dotenv import load_dotenv
from .routes import stats, orders, websocket, auth, settings

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')

load_dotenv()

class APIRouterManager:
    def __init__(self):
        self.router = APIRouter()
        self.setup_routes()

    def setup_routes(self):
        """Setup all API routes."""
        self.router.include_router(stats.router, prefix="/api", tags=["stats"])
        self.router.include_router(orders.router, prefix="/api", tags=["orders"])
        self.router.include_router(auth.router, prefix="/api", tags=["auth"])
        self.router.include_router(settings.router, prefix="/api", tags=["settings"])

        # WebSocket routes no need prefix
        self.router.include_router(websocket.router, tags=["websocket"])