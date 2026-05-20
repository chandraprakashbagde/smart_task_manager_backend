from passlib.context import CryptContext

pwd_cntxt = CryptContext(
    schemes=["bcrypt","argon2"],
    default="argon2",
    bcrypt__rounds=12,
    deprecated="auto"
)