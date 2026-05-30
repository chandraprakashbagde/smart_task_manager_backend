from dotenv import load_dotenv
import os

load_dotenv()

class Setting:
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = int(os.getenv("DB_PORT"))
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")

    SECRET_KEY = os.getenv("SECRET_KEY")
    TOKEN_EXPIRATION = os.getenv("TOKEN_EXPIRATION")

    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

    FAST2SMS_API_KEY = os.getenv("FAST2SMS_API_KEY")
    FAST2SMS_API_URL = os.getenv("FAST2SMS_API_URL")
    OTP_EXPIRY_SECONDS = int(os.getenv("OTP_EXPIRY_SECONDS", 300))  # 5 minutes default
    OTP_LENGTH = int(os.getenv("OTP_LENGTH", 6))  # 6-digit OTP
    OTP_RESEND_WAIT_SECONDS = int(os.getenv("OTP_RESEND_WAIT_SECONDS", 60))  # 60 seconds resend throttle
    REDIS_URL = os.getenv("REDIS_URL")
  
    TEMPLATE_DIR = os.getenv("TEMPLATE_DIR")
    
    # Email/SMTP Configuration
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USERNAME") or os.getenv("SMTP_USER")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    SENDER_EMAIL = os.getenv("FROM_EMAIL") or os.getenv("SENDER_EMAIL")

setting = Setting()