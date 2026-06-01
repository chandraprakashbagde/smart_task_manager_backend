import base64       # for encoding/decoding data safely in URLs
import hmac         # for creating secure signatures
import hashlib      # for hashing (SHA256)
import time         # for handling expiry


from config.config import setting

# 🔐 SECRET key (very important)
# This must be kept private. If leaked, anyone can generate valid tokens.
SECRET = setting.SECRET_KEY
EXPIRYTIME = setting.TOKEN_EXPIRATION
RESET_TOKEN_EXPIRY = setting.PASSWORD_RESET_TOKEN_EXPIRATION  # 5 minutes for reset token

def generate_token(userid: int, email: str):
    # ⏱ Step 1: Create expiry time (current time + 60 seconds)
    exp_time = int(time.time()) + int(EXPIRYTIME)

    # 🧠 Step 2: Create payload → "userid:expiry"
    payload = f"{userid}:{email}:{exp_time}".encode()

    # 🔄 Step 3: Encode payload using base64 (safe to send in URLs)
    payload_b64 = base64.urlsafe_b64encode(payload)

    # 🔐 Step 4: Create signature using HMAC + SECRET
    signature = hmac.new(
        SECRET.encode(),     # secret key
        payload_b64,         # data to sign
        hashlib.sha256       # hashing algorithm
    ).digest()

    # 🔄 Step 5: Encode signature also in base64
    signature_b64 = base64.urlsafe_b64encode(signature)

    # 🧩 Step 6: Combine payload + signature → token
    token = payload_b64 + b"." + signature_b64

    # Convert bytes → string (important for API usage)
    return token.decode()

def verify_token(token: str):
    try:
        # Convert string token back to bytes
        print(token.encode())

        # 🧩 Step 1: Split token into payload and signature
        parts = token.encode().split(b".")

        # If token format is wrong → reject
        if len(parts) != 2:
            return None

        payload_b64, signature_b64 = parts

        # 🔐 Step 2: Recreate signature from payload
        expected_signature = hmac.new(
            SECRET.encode(),
            payload_b64,
            hashlib.sha256
        ).digest()

        expected_signature_b64 = base64.urlsafe_b64encode(expected_signature)

        # ❌ Step 3: Compare signatures (if mismatch → token is fake)
        if(expected_signature_b64 != signature_b64):
            print("signature not matching !")
            return None
        
        # 🔄 Step 4: Decode payload back to string
        decoded = base64.urlsafe_b64decode(payload_b64).decode()

        # 🧠 Step 5: Extract userid and expiry
        userid, email, exp = decoded.split(":")
        exp = int(exp)

        # ⛔ Step 6: Check expiry
        if exp < int(time.time()):
            print("Token expired ❌")
            return None

        # ✅ Token is valid → return user userid and email
        return {
            "userid":userid,
            "email": email
        }

    except Exception as e:
        print(f"Error during verification: {e}")
        return None

def generate_reset_token(email: str):
    exp_time = int(time.time()) + RESET_TOKEN_EXPIRY
    payload = f"reset:{email}:{exp_time}".encode()
    payload_b64 = base64.urlsafe_b64encode(payload)
    signature = hmac.new(SECRET.encode(), payload_b64, hashlib.sha256).digest()
    signature_b64 = base64.urlsafe_b64encode(signature)
    token = payload_b64 + b"." + signature_b64
    return token.decode()

def verify_reset_token(token: str):
    try:
        parts = token.encode().split(b".")
        if len(parts) != 2:
            return None

        payload_b64, signature_b64 = parts

        expected_signature = hmac.new(SECRET.encode(), payload_b64, hashlib.sha256).digest()
        expected_signature_b64 = base64.urlsafe_b64encode(expected_signature)

        if expected_signature_b64 != signature_b64:
            return None

        decoded = base64.urlsafe_b64decode(payload_b64).decode()
        prefix, email, exp = decoded.split(":")
        if prefix != "reset":
            return None
        exp = int(exp)

        if exp < int(time.time()):
            return None

        return email

    except Exception as e:
        print(f"Error during reset token verification: {e}")
        return None
