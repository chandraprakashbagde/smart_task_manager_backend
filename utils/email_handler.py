"""
Email Handler for sending OTP emails.
Uses aiosmtplib for async SMTP operations.
"""

import secrets
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.config import setting
import logging

logger = logging.getLogger(__name__)

def generate_otp_code() -> str:
    """
    Generate a secure 6-digit numeric OTP code.
    
    Returns:
        A string containing 6 random digits
    """
    otp_number = secrets.randbelow(1000000)
    return str(otp_number).zfill(6)

def get_otp_email_template(recipient_email: str, otp_code: str, purpose: str) -> tuple:
    """
    Generate email subject and HTML body for OTP verification.
    
    Args:
        recipient_email: Recipient's email address
        otp_code: Generated OTP code
        purpose: Purpose of OTP (REGISTRATION, FORGOT_PASSWORD, LOGIN_VERIFICATION)
    
    Returns:
        Tuple of (subject, html_body)
    """
    
    purpose_messages = {
        "REGISTRATION": "verify your email and complete your registration",
        "FORGOT_PASSWORD": "reset your password",
        "LOGIN_VERIFICATION": "verify your login attempt"
    }
    
    purpose_message = purpose_messages.get(purpose, "verify your identity")
    
    subject = f"Your OTP for {purpose}"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .header h1 {{
                color: #333;
                margin: 0;
                font-size: 28px;
            }}
            .content {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .content p {{
                color: #666;
                line-height: 1.6;
                margin: 15px 0;
            }}
            .otp-box {{
                background-color: #f9f9f9;
                border: 2px solid #007bff;
                border-radius: 8px;
                padding: 20px;
                margin: 30px 0;
            }}
            .otp-code {{
                font-size: 36px;
                font-weight: bold;
                color: #007bff;
                letter-spacing: 8px;
                margin: 0;
            }}
            .footer {{
                text-align: center;
                color: #999;
                font-size: 12px;
                margin-top: 30px;
                border-top: 1px solid #eee;
                padding-top: 20px;
            }}
            .warning {{
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                color: #856404;
                padding: 10px;
                border-radius: 4px;
                margin-top: 20px;
                font-size: 13px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Verification Code</h1>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>You have requested to {purpose_message}.</p>
                <p>Please use the following One-Time Password (OTP) to proceed:</p>
                
                <div class="otp-box">
                    <p class="otp-code">{otp_code}</p>
                </div>
                
                <p><strong>This OTP will expire in 5 minutes.</strong></p>
                
                <div class="warning">
                    <strong>⚠️ Security Notice:</strong> Never share this OTP with anyone. Our team will never ask you for this code.
                </div>
                
                <p>If you didn't request this code, please ignore this email.</p>
            </div>
            <div class="footer">
                <p>&copy; 2026 Smart Task Manager. All rights reserved.</p>
                <p>This is an automated email. Please do not reply to this message.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return subject, html_body

async def send_otp_email(recipient_email: str, otp_code: str, purpose: str) -> bool:
    """
    Send OTP email to the user asynchronously.
    
    Args:
        recipient_email: Recipient's email address
        otp_code: Generated OTP code
        purpose: Purpose of OTP
    
    Returns:
        True if email sent successfully, False otherwise
    """
    
    try:
        # Get email credentials from environment
        smtp_host = setting.SMTP_HOST
        smtp_port = setting.SMTP_PORT
        smtp_user = setting.SMTP_USER
        smtp_password = setting.SMTP_PASSWORD
        sender_email = setting.SENDER_EMAIL
        
        # Validate that SMTP settings are configured
        if not all([smtp_host, smtp_port, smtp_user, smtp_password, sender_email]):
            logger.error("SMTP settings not configured in environment variables")
            return False
        
        # Get email template
        subject, html_body = get_otp_email_template(recipient_email, otp_code, purpose)
        
        # Create email message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = recipient_email
        
        # Add HTML content
        html_part = MIMEText(html_body, "html")
        message.attach(html_part)
        
        # Send email via SMTP
        async with aiosmtplib.SMTP(hostname=smtp_host, port=int(smtp_port)) as smtp:
            await smtp.login(smtp_user, smtp_password)
            await smtp.send_message(message)
        
        logger.info(f"OTP email sent successfully to {recipient_email} for {purpose}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send OTP email to {recipient_email}: {str(e)}")
        return False

async def send_otp_email_sync_fallback(recipient_email: str, otp_code: str, purpose: str) -> bool:
    """
    Fallback synchronous email sending (if async fails).
    This can be used in background tasks.
    
    Args:
        recipient_email: Recipient's email address
        otp_code: Generated OTP code
        purpose: Purpose of OTP
    
    Returns:
        True if email sent successfully, False otherwise
    """
    # This is a placeholder for fallback implementation
    # In production, you might use a service like SendGrid, AWS SES, or other
    logger.warning(f"Using fallback email method for {recipient_email}")
    return await send_otp_email(recipient_email, otp_code, purpose)
