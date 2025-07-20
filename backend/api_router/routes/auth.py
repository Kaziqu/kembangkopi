# api-barista.py
import os
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
import asyncio
import json
from connection_manager import manager
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv()

router = APIRouter()

class LoginRequest(BaseModel):
    password: str
   
# verify password
@router.post("/auth")
async def login(request: LoginRequest):
    correct_password = os.getenv("BARISTA_PASSWORD")
    try: 
        if not correct_password:
            await asyncio.sleep(1)
            raise HTTPException(status_code=401, detail="Invalid password")
        if request.password == correct_password:
            return {"message": "Login successful"}
        else:
            await asyncio.sleep(2)
            
            # Safely broadcast login failure without causing 500 error
            try:
                await manager.broadcast(json.dumps({
                    "type": "login_failed",
                    "message": "Invalid password attempt"
                }))
                print("Broadcasted login failure notification")
            except Exception as broadcast_error:
                print(f"Failed to broadcast login failure: {broadcast_error}")
                # Don't let broadcast error affect the main response
            
            raise HTTPException(status_code=401, detail="Invalid password")
    except HTTPException:
        # Re-raise HTTP exceptions (401, etc.) without wrapping in 500
        raise
    except Exception as e:
        print(f"Unexpected error in login: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")