# settings.py
# OPEN ORDER/CLOSE 
import os
from fastapi import APIRouter, HTTPException
from supabase import create_client, Client
from typing import Optional
from config.config import Config
from pydantic import BaseModel

Config = Config()

SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

class OrderStatusResponse(BaseModel):
    open: bool
    message: Optional[str] = None

class SetOrderStatusRequest(BaseModel):
    open: bool

router = APIRouter()

@router.get("/isopen", response_model=OrderStatusResponse)
async def is_open():
    """Check if the order system is open."""
    try:
        result = supabase.table("settings").select("value").eq("key", "order_open").execute()
        
        # Handle empty result or no data
        if not result.data or len(result.data) == 0:
            # Default to closed if no setting exists
            return {"open": False, "message": "Order system is closed (no setting found)"}
        
        # Get the first (and should be only) result
        setting_value = result.data[0].get("value", "false")
        is_open = setting_value.lower() == "true"
        
        return {
            "open": is_open, 
            "message": "Order system is open" if is_open else "Order system is closed"
        }
    except Exception as e:
        print(f"Error in is_open endpoint: {str(e)}")  # Add logging
        raise HTTPException(status_code=500, detail=f"Error checking order status: {str(e)}")

@router.post("/setopen", response_model=OrderStatusResponse)
async def set_open(request: SetOrderStatusRequest):
    """Set the order system open/close status."""
    try:
        value = "true" if request.open else "false"
        result = supabase.table("settings").upsert({"key": "order_open", "value": value}).execute()
        
        print(f"Updated order status to: {value}")  # Add logging
        return {"open": request.open, "message": "Order status updated successfully"}
    except Exception as e:
        print(f"Error in set_open endpoint: {str(e)}")  # Add logging
        raise HTTPException(status_code=500, detail=f"Error updating order status: {str(e)}")