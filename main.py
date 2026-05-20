from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from config.database import init_db, close_db
from routes.user_routes import router as user_router
from routes.auth_routes import router as login_router
from utils.response_handler import validation_exception_handler
from services.admin_service import setup_admin_user

app = FastAPI()

# Define the allowed origins
origins = [
    "http://localhost:3000",   # Common for Create React App
    "http://localhost:5173",   # Common for Vite
    "http://127.0.0.1:3000",
    # Add your production frontend URL later
    # "https://yourdomain.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # Allows the origins in your list
    allow_credentials=True,       # Allows cookies and authorization headers
    allow_methods=["*"],          # Allows all HTTP methods (GET, POST, PUT, etc.)
    allow_headers=["*"],          # Allows all headers
)

@app.on_event("startup")
async def startup():
    await init_db()
    await setup_admin_user()

@app.on_event("shutdown")
async def shutdown():
    await close_db()

@app.exception_handler(RequestValidationError)
async def exceptionHandler(request: Request, exc: RequestValidationError):
    return await validation_exception_handler(exc)

app.include_router(login_router)
app.include_router(user_router)