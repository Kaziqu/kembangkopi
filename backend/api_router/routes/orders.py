# orders.py ORDER CRUD
import os
from fastapi import APIRouter, HTTPException
from gotrue import datetime
from supabase import create_client, Client
from typing import List, Optional
from pydantic import BaseModel
from config.config import Config
from recaptcha.recaptcha import Recaptcha
from dotenv import load_dotenv
from connection_manager import manager
import json

load_dotenv()

class OrderResponse(BaseModel):
    orders: List[dict]

Config = Config()

SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

recaptcha = Recaptcha()

router = APIRouter()

@router.post("/orders")
async def create_order(order_data: dict):
    """Create a new order."""
    recaptcha_token = order_data.get("recaptcha_token")

    if not recaptcha_token or not recaptcha.verify_recaptcha(recaptcha_token):
        raise HTTPException(status_code=400, detail="Invalid reCAPTCHA token")
    try:
        # insert the order into the database
        order_result  = supabase.table("orders").insert({
            "order_id": order_data["order_id"],
            "customer_name": order_data["customer_name"],
            "total": order_data["total"],
            "timestamp": order_data["timestamp"],
            "status": order_data["status"]
        }).execute()
    
        # Insert order items after order creation
        for item in order_data["items"]:
            item["order_id"] = order_data["order_id"]
            item["total"] = item["price"] * item["quantity"]
            try:
                supabase.table("items").insert(item).execute()
            except Exception as e:
                print("Error inserting item:", e)
                continue
            
        # Fetch the complete order data with items for WebSocket broadcast
        items_result = supabase.table("items").select("*").eq("order_id", order_data["order_id"]).execute()
        
        # Broadcast the new order with complete data to all connected WebSocket clients
        complete_order_data = {
            "order": {
                "order_id": order_data["order_id"],
                "customer_name": order_data["customer_name"],
                "total": order_data["total"],
                "timestamp": order_data["timestamp"],
                "status": order_data["status"]
            },
            "items": items_result.data if items_result.data else []
        }
        
        broadcast_message = json.dumps({
            "type": "new_order",
            "data": complete_order_data
        })
        
        print(f"Broadcasting new order: {order_data['order_id']} to {len(manager.active_connections)} connections")
        await manager.broadcast(broadcast_message)

        print("Order created successfully:", order_result)
        return {
            "message": "Order created successfully",
            "order_id": order_data["order_id"]
        }
    except Exception as e:
        print(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders", response_model=OrderResponse)
async def get_orders():
    """Get all orders."""
    try:
        result = supabase.table("orders").select("*").eq("status", "pending").order("timestamp").execute()
        
        orders = []
        for order in result.data:
            # Fetch items for this specific order
            items_result = supabase.table("items").select("*").eq("order_id", order["order_id"]).execute()
            
            order_data = {
                "order": {
                    "order_id": order["order_id"],
                    "customer_name": order["customer_name"],
                    "total": order["total"],
                    "timestamp": order["timestamp"],
                    "status": order["status"]
                },
                "items": items_result.data if items_result.data else []
            }
            orders.append(order_data)
            
        return {"orders": orders}
    except Exception as e:
        print(f"Error fetching orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/orders/{order_id}/complete")
async def complete_order(order_id: str):
    """Mark an order as complete."""
    try:
        result = supabase.table("orders").update(
            {
                "status": "completed",
                "completed_at": datetime.now().isoformat()
            }
        ).eq("order_id", order_id).execute()
        
        if result.data and len(result.data) > 0:
            # Broadcast order completion to all connected WebSocket clients
            broadcast_message = json.dumps({
                "type": "order_completed",
                "order_id": order_id
            })
            
            print(f"Broadcasting order completed: {order_id} to {len(manager.active_connections)} connections")
            await manager.broadcast(broadcast_message)
            
            return {"message": "Order marked as complete", "order_id": order_id}
        else:
            raise HTTPException(status_code=404, detail="Order not found")
    except Exception as e:
        print(f"Error completing order: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
