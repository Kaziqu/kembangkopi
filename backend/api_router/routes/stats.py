# stats.py - Statistics Endpoints
import os
from datetime import timezone
from fastapi import APIRouter, HTTPException
from datetime import datetime
from pydantic import BaseModel
from supabase import create_client, Client
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class StatsResponse(BaseModel):
    total_sales_today: int
    pending_orders: int
    completed_orders_today: int
    total_revenue_today: float

router = APIRouter()
SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
	raise RuntimeError("SUPABASE_URL and SUPABASE_KEY environment variables must be set.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@router.get("/stats", response_model=StatsResponse)
async def get_statistics():
    """Fetch statistics from the database."""

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
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")