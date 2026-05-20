from ..repositories.user_repository import get_user_by_email, create_user
from ..config.config import setting
from ..schemas.user_schema import CreateUser
from ..utils.password_handler import pwd_cntxt

# Updated function in your service layer
async def setup_admin_user():
    # Subtle/Dim color for the check
    print("\033[90m[init] Checking admin status...\033[0m", end="\r") 

    user = await get_user_by_email(email=setting.ADMIN_EMAIL)

    if user is None:
        # Bold Yellow for progress
        print("\033[1;33m[!] Admin setup in progress...\033[0m")
        
        user_data = CreateUser(
            f_name="System",
            l_name="Admin",
            email=setting.ADMIN_EMAIL,
            password=setting.ADMIN_PASSWORD,
            cpassword=setting.ADMIN_PASSWORD,
            role="Admin",
        )

        user_data.password = pwd_cntxt.hash(user_data.password)

        await create_user(user_data)
        
        # Bold Green for completion
        print("\033[1;32m[✓] Admin user created successfully.\033[0m")
    else:
        # Clear the "Checking" line if nothing was done
        print(" " * 40, end="\r")
