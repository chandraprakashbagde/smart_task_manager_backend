from repositories.user_repository import get_user_by_email, update_password
from repositories.otp_repository import (
    store_otp,
    get_latest_active_otp,
    mark_otp_as_used,
    get_last_otp_timestamp
)
from utils.response_handler import SuccessResp, FieldErrorResp
from utils.password_handler import pwd_cntxt
from utils.token import generate_token, generate_reset_token, verify_reset_token
from utils.email_handler import generate_otp_code, send_otp_email
from config.config import setting
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

async def userLogin(crendetials):
    
    user = await get_user_by_email(crendetials.email)

    if user == None:
        return FieldErrorResp(
            field="email",
            message="User not found with this email"
        )

    if pwd_cntxt.verify(crendetials.password, user["password"]) != True:
        return FieldErrorResp(
            field="password",
            message="Incorrect Password."
        )

    user['created_at'] = user["created_at"].isoformat()
    user['updated_at'] = user["updated_at"].isoformat()

    return SuccessResp(
            message="User logged in successfully.",
            data={ "token": generate_token(userid=user["user_id"], email=user["email"])}
        )


# ============================================================================
# OTP SERVICE FUNCTIONS
# ============================================================================

async def send_otp_service(send_otp_request):

    try:
        email = send_otp_request.email
        purpose = send_otp_request.purpose.value  # Convert enum to string
        
        # ===== RATE LIMITING: Check if user can request a new OTP =====
        last_otp_time = await get_last_otp_timestamp(email, purpose)

        if last_otp_time:
            # Calculate seconds since last OTP was created
            resendInfo = getResendTimeParames(last_otp_time, setting.OTP_RESEND_WAIT_SECONDS)
            # Check if user is trying to resend too quickly
            if resendInfo["minutes"] > 0 or resendInfo["seconds"] > 0:
                return FieldErrorResp(
                    field="email",
                    message=None,
                    data=resendInfo
                )
        
        # ===== GENERATE OTP =====
        otp_code = generate_otp_code()
        
        # ===== STORE OTP IN DATABASE =====
        otp_id = await store_otp(
            email=email,
            otp_code=otp_code,
            purpose=purpose,
            expiry_seconds=setting.OTP_EXPIRY_SECONDS
        )
        
        if not otp_id:
            return FieldErrorResp(
                field="email",
                message="Failed to generate OTP. Please try again."
            )
        
        # ===== SEND EMAIL =====
        email_sent = await send_otp_email(email, otp_code, purpose)
        
        if not email_sent:
            logger.warning(f"OTP generated but email failed to send for: {email}")
            return FieldErrorResp(
                field="email",
                message="OTP generated but failed to send email. Please try again."
            )
        
        # ===== SUCCESSFUL RESPONSE =====
        return SuccessResp(
            message=f"OTP sent successfully to {email}",
            data={
                "email": email,
                "purpose": purpose,
                "otp_id": otp_id
            }
        )
        
    except Exception as e:
        logger.error(f"Error in send_otp_service: {str(e)}")
        return FieldErrorResp(
            field="email",
            message="An error occurred while sending OTP. Please try again."
        )


async def verify_otp_service(verify_otp_request):
    """
    Service function to verify the OTP provided by the user.
    Checks for: validity, expiration, one-time use, and purpose match.
    
    Args:
        verify_otp_request: VerifyOTPRequest schema with email, otp, and purpose
    
    Returns:
        JSONResponse with verification result
    """
    try:
        email = verify_otp_request.email
        provided_otp = verify_otp_request.otp
        purpose = verify_otp_request.purpose.value  # Convert enum to string
        
        # ===== FETCH LATEST ACTIVE OTP =====
        otp_record = await get_latest_active_otp(email, purpose)
        
        # Check if any valid OTP exists
        if not otp_record:
            return FieldErrorResp(
                field="otp",
                message="No valid OTP found. Please request a new OTP."
            )
        
        # ===== CHECK IF OTP IS ALREADY USED =====
        if otp_record.get('is_used'):
            return FieldErrorResp(
                field="otp",
                message="This OTP has already been used."
            )
        
        # ===== CHECK OTP EXPIRATION =====
        expires_at = otp_record.get('expires_at')
        if expires_at < datetime.utcnow():
            return FieldErrorResp(
                field="otp",
                message="OTP has expired. Please request a new OTP."
            )
        
        # ===== VERIFY OTP CODE =====
        stored_otp = otp_record.get('otp_code')
        if provided_otp != stored_otp:
            return FieldErrorResp(
                field="otp",
                message="Invalid OTP. Please try again."
            )
        
        # ===== MARK OTP AS USED =====
        otp_id = otp_record.get('otp_id')
        marked = await mark_otp_as_used(otp_id)
        
        if not marked:
            logger.error(f"Failed to mark OTP as used for otp_id: {otp_id}")
            return FieldErrorResp(
                field="otp",
                message="Failed to verify OTP. Please try again."
            )
        
        # ===== SUCCESSFUL VERIFICATION =====
        logger.info(f"OTP verified successfully for email: {email}, purpose: {purpose}")
        return SuccessResp(
            message="OTP verified successfully",
            data={
                "email": email,
                "purpose": purpose,
                "verified": True
            }
        )
        
    except Exception as e:
        logger.error(f"Error in verify_otp_service: {str(e)}")
        return FieldErrorResp(
            field="otp",
            message="An error occurred while verifying OTP. Please try again."
        )
    


# ============================================================================
# FORGOT PASSWORD SERVICE FUNCTIONS
# ============================================================================

async def forgot_password_service(request):
    try:
        email = request.email

        user = await get_user_by_email(email)
        if not user:
            return FieldErrorResp(
                field="email",
                message="No account found with this email"
            )

        purpose = "FORGOT_PASSWORD"

        last_otp_time = await get_last_otp_timestamp(email, purpose)

        resendRemainingSeconds = setting.OTP_RESEND_WAIT_SECONDS

        if last_otp_time:
            resendInfo = getResendTimeParames(last_otp_time, setting.OTP_RESEND_WAIT_SECONDS)
            if resendInfo["minutes"] > 0 or resendInfo["seconds"] > 0:
                return FieldErrorResp(
                    field="email",
                    message=f"We've already sent an OTP to your email. \nPlease wait {resendInfo["text"]} before requesting a new OTP.",
                )

        otp_code = generate_otp_code()

        otp_id = await store_otp(
            email=email,
            otp_code=otp_code,
            purpose=purpose,
            expiry_seconds=setting.OTP_EXPIRY_SECONDS
        )

        if not otp_id:
            return FieldErrorResp(
                field="email",
                message="Failed to generate OTP. Please try again."
            )

        email_sent = await send_otp_email(email, otp_code, purpose)

        if not email_sent:
            logger.warning(f"Forgot password OTP generated but email failed for: {email}")
            return FieldErrorResp(
                field="email",
                message="OTP generated but failed to send email. Please try again."
            )

        return SuccessResp(
            message=f"OTP sent successfully to {email}",
            data={
                "email": email,
                "purpose": purpose,
                "otp_id": otp_id,
                "resendRemainingSeconds":resendRemainingSeconds
            }
        )

    except Exception as e:
        logger.error(f"Error in forgot_password_service: {str(e)}")
        return FieldErrorResp(
            field="email",
            message="An error occurred. Please try again."
        )


async def verify_forgot_password_otp_service(request):
    try:
        email = request.email
        provided_otp = request.otp
        purpose = "FORGOT_PASSWORD"

        otp_record = await get_latest_active_otp(email, purpose)

        if not otp_record:
            return FieldErrorResp(
                field="otp",
                message="No valid OTP found. Please request a new OTP."
            )

        if otp_record.get('is_used'):
            return FieldErrorResp(
                field="otp",
                message="This OTP has already been used."
            )

        expires_at = otp_record.get('expires_at')
        if expires_at < datetime.utcnow():
            return FieldErrorResp(
                field="otp",
                message="OTP has expired. Please request a new OTP."
            )

        stored_otp = otp_record.get('otp_code')
        if provided_otp != stored_otp:
            return FieldErrorResp(
                field="otp",
                message="Invalid OTP. Please try again."
            )

        otp_id = otp_record.get('otp_id')
        marked = await mark_otp_as_used(otp_id)

        if not marked:
            logger.error(f"Failed to mark OTP as used for otp_id: {otp_id}")
            return FieldErrorResp(
                field="otp",
                message="Failed to verify OTP. Please try again."
            )

        reset_token = generate_reset_token(email)

        logger.info(f"Forgot password OTP verified successfully for email: {email}")
        return SuccessResp(
            message="OTP verified successfully",
            data={
                "email": email,
                "verified": True,
                "reset_token": reset_token
            }
        )

    except Exception as e:
        logger.error(f"Error in verify_forgot_password_otp_service: {str(e)}")
        return FieldErrorResp(
            field="otp",
            message="An error occurred while verifying OTP. Please try again."
        )


async def reset_password_service(request):
    try:
        token = request.token
        new_password = request.new_password
        confirm_password = request.confirm_password

        if new_password != confirm_password:
            return FieldErrorResp(
                field="confirm_password",
                message="Passwords do not match."
            )

        email = verify_reset_token(token)
        if not email:
            return FieldErrorResp(
                field="token",
                message="Invalid or expired reset token. Please verify OTP again."
            )

        user = await get_user_by_email(email)
        if not user:
            return FieldErrorResp(
                field="email",
                message="No account found with this email."
            )

        hashed_password = pwd_cntxt.hash(new_password)
        updated = await update_password(email, hashed_password)

        if not updated:
            return FieldErrorResp(
                field="password",
                message="Failed to reset password. Please try again."
            )

        logger.info(f"Password reset successfully for email: {email}")
        return SuccessResp(
            message="Password reset successfully.",
            data={
                "email": email
            }
        )

    except Exception as e:
        logger.error(f"Error in reset_password_service: {str(e)}")
        return FieldErrorResp(
            field="password",
            message="An error occurred while resetting password. Please try again."
        )


## Helper functions

def getResendTimeParames(createtime, expiry_time):
    # Check if createtime is already a datetime object
    if isinstance(createtime, str):
        created_at = datetime.strptime(createtime, "%Y-%m-%d %H:%M:%S")
    else:
        created_at = createtime  # It's already a datetime object
    

    # Calculate expiry datetime
    expiry_datetime = created_at + timedelta(seconds=expiry_time)

    # Get current time
    now = datetime.now()

    # Calculate remaining time
    remaining = expiry_datetime - now
    remainingSeconds = int(remaining.total_seconds())

    # Extract minutes and seconds
    if remainingSeconds > 0:
        minutes = remainingSeconds // 60
        seconds = remainingSeconds % 60

        return {
            "minutes": minutes,
            "seconds": seconds,
            "remainingSeconds": remainingSeconds,
            "text": get_text(minutes, seconds)
        }
    else:
        return {
            "minutes": 0,
            "seconds": 0,
            "remainingSeconds": 0,
            "text": "now"
        }
    
def get_text(minutes: int, seconds: int) -> str:
    parts = []

    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")

    if seconds > 0:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")

    if not parts:
        return "0 seconds"

    return " and ".join(parts)