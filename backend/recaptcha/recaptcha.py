# recaptcha.py
import os
from fastapi import HTTPException
import requests
from dotenv import load_dotenv
from config.config import Config

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv()

recaptcha_secret_key = os.getenv("RECAPTCHA_SECRET_KEY")

class Recaptcha:
    def __init__(self):
        # Load the reCAPTCHA secret key from environment variables
        self.secret_key = recaptcha_secret_key
        if not self.secret_key:
            raise ValueError("RECAPTCHA_SECRET_KEY environment variable must be set")

    def verify_recaptcha(self, token: str) -> bool:
        url = Config.RECAPTCHA_URL
        if not url:
            raise ValueError("RECAPTCHA_URL must be set in the configuration")
        
        data = {
            "secret": self.secret_key,
            "response": token
        }
        
        try:
            response = requests.post(url, data=data, timeout=5)
            result = response.json()
            return result.get("success", False)
        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Error verifying reCAPTCHA: {str(e)}")
        except ValueError as e:
            raise HTTPException(status_code=500, detail=f"Invalid response from reCAPTCHA: {str(e)}")