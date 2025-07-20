# config
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    # reCAPTCHA Configuration
    RECAPTCHA_URL = os.getenv("RECAPTCHA_URL", "https://www.google.com/recaptcha/api/siteverify")
    RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")
    
    # Supabase Configuration
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # Authentication
    BARISTA_PASSWORD = os.getenv("BARISTA_PASSWORD")
    
    # Environment Configuration
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Server Configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    
    @classmethod
    def validate_config(cls):
        """Validate that all required environment variables are set"""
        required_vars = [
            "SUPABASE_URL",
            "SUPABASE_KEY", 
            "BARISTA_PASSWORD",
            "RECAPTCHA_SECRET_KEY"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True


def setup_middleware(app):
    """Setup CORS middleware based on environment"""
    config = Config()
    
    if config.ENVIRONMENT == "production":
        # Production CORS - strict origins
        allowed_origins = [
            "https://order.kembangkopi.my.id",           # Order Interface
            "https://dashboard.kembangkopi.my.id"  # Dashboard Barista
        ]
        allowed_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        allowed_headers = ["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"]
    else:
        # Development CORS - more permissive
        allowed_origins = [
            "http://localhost:3000",
            "http://localhost:5173", 
            "http://127.0.0.1:5500",
            "http://localhost:8080",
            "https://order.kembangkopi.my.id",
            "https://dashboard.kembangkopi.my.id"
        ]
        allowed_methods = ["*"]
        allowed_headers = ["*"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=allowed_methods,
        allow_headers=allowed_headers,
    )
    return app