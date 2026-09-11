import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask configuration
    HOST = "127.0.0.1"
    PORT = 5000
    DEBUG = True

    # Google Safe Browsing API Key
    SAFE_BROWSING_API_KEY = os.getenv("SAFE_BROWSING_API_KEY")

    # VirusTotal API Key
    VT_API_KEY = os.getenv("VT_API_KEY")
