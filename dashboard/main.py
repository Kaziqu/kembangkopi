# Main .py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
import asyncio
import json
from datetime import datetime, timedelta, timezone
from supabase import create_client, Client
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import requests
from pydantic import BaseModel

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

#print("SUPABASE_URL:", os.getenv("SUPABASE_URL"))
#print("SUPABASE_KEY:", os.getenv("SUPABASE_KEY"))

app = FastAPI(title="Dashboard API", version="1.0")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ... background task ...
    yield

app = FastAPI(title="Dashboard API", version="1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://kembangkopi.my.id",
        "https://dashboard.kembangkopi.my.id",
        "https://order.kembangkopi.my.id"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Semua route, websocket, dsb, di bawah sini!
# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Client connected. Total active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"Client disconnected. Total active connections: {len(self.active_connections)}")

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
        print(f"Message sent to client: {message}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
                print(f"Broadcast message sent: {message}")
            except:
                self.active_connections.remove(connection)
                print("Failed to send message to a client, removing connection.")

manager = ConnectionManager()

# Database Models
class OrderItem:
    def __init__(self, name: str, price: int, quantity: int, milk: str = "-", sugar: str= "-"):
        self.name = name
        self.price = price
        self.quantity = quantity
        self.total = price * quantity
        self.milk = milk
        self.sugar = sugar

class Order:
    def __init__(self, customer_name: str, items: List[OrderItem]):
        self.order_id = datetime.now().strftime("%Y%m%d%H%M%S")
        self.customer_name = customer_name
        self.items = items
        self.total = sum(item.total for item in items)
        self.timestamp = datetime.now().isoformat()
        self.status = "pending"

# Login API
class LoginRequest(BaseModel):
    password: str

# Verify password
@app.post("/api/login")
async def login(request: LoginRequest):
    correct_password = os.getenv("BARISTA_PASSWORD")

    if not correct_password:
        raise HTTPException(status_code=500, detail="Password tidak ditemukan")

    if request.password == correct_password:
        return {"status": "success"}

    else:
        # Sleep for 1 second to prevent brute force attack
        await asyncio.sleep(2)
        await manager.broadcast(json.dumps({
            "type": "login_failed",
            "data": {
                "message": "Wrong password"
            }
        }))
        raise HTTPException(status_code=401, detail="Wrong password")

# API Routes
@app.get("/api/orders")
async def get_orders():
    """Get  all pending orders from the database."""
    try:
        result = supabase.table("orders").select("*").eq("status", "pending").order("timestamp").execute()
       
       # Transform the result into a list of Order objects
        orders = []
        for order in result.data:
            order_data = {
                "order": {
                    "order_id": order["order_id"],
                    "customer_name": order["customer_name"],
                    "total": order["total"],
                    "timestamp": order["timestamp"],
                    "status": order["status"]
                },
                "items": order["items"]
            }
            orders.append(order_data)
        
        return {"orders": orders}
    except Exception as e:
        print(f"Error fetching orders: {e}")
        return {"error": str(e)}
    
RECAPTCHA_SECRET = os.getenv("RECAPTCHA_SECRET")

def verify_recaptcha(token: str) -> bool:
    url = "https://www.google.com/recaptcha/api/siteverify"
    data = {
        "secret": RECAPTCHA_SECRET,
        "response": token
    }
    try:
        response = requests.post(url, data=data, timeout=5)
        result = response.json()
        return result.get("success", False)
    except Exception as e:
        print("reCAPTCHA validation error:", e)
        return False

@app.post("/api/orders")
async def get_order(order_data: dict):
    recaptcha_token = order_data.get("recaptcha_token")
    if not recaptcha_token or not verify_recaptcha(recaptcha_token):
        return {"error": "reCAPTCHA validation failed"}, 400
    try:
       # Insert the order into the database
        order_result = supabase.table("orders").insert({
            "order_id": order_data["order_id"],
            "customer_name": order_data["customer_name"],
            "total": order_data["total"],
            "timestamp": order_data["timestamp"],
            "status": order_data["status"]
        }).execute()

        # Insert the order items into the database
        for item in order_data["items"]:
            item["order_id"] = order_data["order_id"]
            item["total"] = item["price"] * item["quantity"]
            print("Insert item:", item) #debugging
            try:
                supabase.table("items").insert(item).execute()
            except Exception as e:
                print("Error inserting item:", e)

        # broadcast the new order to all connected clients
        await manager.broadcast(json.dumps({
            "type": "new_order",
            "data": {
                "order": {
                    "order_id": order_data["order_id"],
                    "customer_name": order_data["customer_name"],
                    "total": order_data["total"],
                    "timestamp": order_data["timestamp"],
                    "status": order_data["status"]
            },
            "items": order_data["items"]
        }
    }))
        
        return order_result
    except Exception as e:
        print(f"Error creating order: {e}")
        return {"error": str(e)}

@app.put("/api/orders/{order_id}/complete")
async def complete_order(order_id: str):
    """Mark an order as complete in the database."""
    try:
       # Update the order status to 'complete'
       result = supabase.table("orders").update({
           "status": "complete",
           "completed_at": datetime.now().isoformat()
       }).eq("order_id", order_id).execute()
       print("Order marked as complete:", result)

       # Broadcast the updated order status to all connected clients
       await manager.broadcast(json.dumps({
           "type": "order_completed",
           "order_id": order_id
       }))

       return {"message": "Order marked as complete", "order_id": order_id}
    except Exception as e:
        print(f"Error completing order: {e}")
        return {"error": str(e)}
    
@app.get("/api/stats")
async def get_stats():
    """Get statistics about orders."""
    try:
        # Use UTC for all date filters
        today_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        start_utc = f"{today_utc}T00:00:00+00:00"

        # Total orders today
        total_sales_today = supabase.table("orders").select("*").gte("timestamp", start_utc).execute()

        # Pending orders
        pending_orders = supabase.table("orders").select("*").eq("status", "pending").execute()

        # Completed orders Today
        completed_orders_today = supabase.table("orders").select("*").eq("status", "complete").gte("completed_at", start_utc).execute()

        # Total revenue today
        total_revenue_today = supabase.table("orders").select("total").gte("timestamp", start_utc).execute()
        total_revenue = sum(order["total"] for order in total_revenue_today.data)

        return {
            "total_sales_today": len(total_sales_today.data),
            "pending_orders": len(pending_orders.data),
            "completed_orders_today": len(completed_orders_today.data),
            "total_revenue_today": total_revenue
        }
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return {"error": str(e)}

# --- ORDER OPEN/CLOSE ENDPOINTS (SCALABLE) ---
@app.get("/api/isopen")
def is_open():
    result = supabase.table("settings").select("value").eq("key", "order_open").single().execute()
    if result.data:
        return {"open": result.data["value"] == "true"}
    raise HTTPException(status_code=500, detail="Setting not found")

@app.post("/api/setopen")
async def set_open(request: Request):
    data = await request.json()
    open_status = data.get("open")
    if open_status is None:
        raise HTTPException(status_code=400, detail="Missing 'open' in body")
    value = "true" if open_status else "false"
    supabase.table("settings").upsert({"key": "order_open", "value": value}).execute()
    return {"open": open_status}

@app.websocket("/ws-dashboard")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received data from client: {data}")
            # Here you can handle incoming messages from the client if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")

# Supabase Realtime Listeners (simulation)
async def supabase_listener():
    """Listen for database changes and broadcast them to connected clients."""
    last_seen_id = 0
    await asyncio.sleep(1)
    
    while True:
        try:
            response = supabase.table("orders").select("*").eq("status", "pending").order("timestamp", desc=True).execute()
            orders = response.data

            for order in orders:
                if order["id"] > last_seen_id:
                    last_seen_id = order["id"]
                    print(f"New order detected: {order['id']}")

                await asyncio.sleep(5)
  
        except Exception as e:
            print(f"Error in supabase listener: {e}")
            await asyncio.sleep(10)

# Test data creation
@app.post("/api/test/create-sample-order")
async def create_sample_order():
    """Create a sample order for testing."""
    import random

    customer_names = ["John Doe", "Jane Smith", "Alice Johnson", "Bob Brown", "Charlie Davis"]
    drinks = [
        {"name": "Cafe Latte", "price": 18000},
        {"name": "Cappuccino", "price": 20000},
        {"name": "Espresso", "price": 15000},
        {"name": "Americano", "price": 15000},
        {"name": "Mocha", "price": 22000}
    ]

    # Create random orders
    customer_name = random.choice(customer_names)
    order_items = []

    for _ in range(random.randint(1, 3)):
        drink = random.choice(drinks)
        quantity = random.randint(1, 3)
        milk = random.choice(["Full Cream", "Oat Milk", "Almond Milk", "-"])
        sugar = random.choice(["No Sugar", "1 Sugar", "2 Sugar", "-"])

        item = OrderItem(
            name=drink["name"],
            price=drink["price"],
            quantity=quantity,
            milk=milk,
            sugar=sugar
        )
        order_items.append(item)

    # Create the order
    order = Order(customer_name, order_items)
    order_data = {
        "order_id": order.order_id,
        "customer_name": order.customer_name,
        "total": order.total,
        "timestamp": order.timestamp,
        "status": order.status,
        "items": [{
            "name": item.name,
            "price": item.price,
            "quantity": item.quantity,
            "milk": item.milk,
            "sugar": item.sugar
        } for item in order_items
    ]
    }

    # Insert the order into the database
    result = await get_order(order_data)
    return result
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000);