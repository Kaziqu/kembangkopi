# config
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    RECAPTCHA_URL = os.getenv("RECAPTCHA_URL")
    RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    BARISTA_PASSWORD = os.getenv("BARISTA_PASSWORD")

    # Optional: Environment variable for the environment (development, production, etc.)
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


def setup_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://order.kembangkopi.my.id",
                       "https://dashboard.kembangkopi.my.id"],  # For production, specify allowed origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app