from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from jose import JWTError, jwt

from app.core import security
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, User as UserSchema
from app.schemas.auth import Token, TokenData
from app.utils.serializer import serialize_dict

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user():
    """
    Bypassing authentication for now. 
    Always returns a mock admin user.
    """
    try:
        # Try to find an existing admin
        user = await User.find_one(User.role == "admin")
        if user:
            return user
    except Exception:
        # Database might not be initialized yet
        pass
        
    from beanie import PydanticObjectId
    return User.model_construct(
        id=PydanticObjectId("65f1a2b3c4d5e6f7a8b9c0d1"), # Mock ID
        email="admin@example.com",
        name="Admin User",
        hashed_password="mock_password",
        role="admin"
    )

async def get_admin_user(current_user: User = Depends(get_current_user)):
    """
    Bypassing admin check.
    """
    return current_user

@router.post("/register", response_model=UserSchema)
async def register(user_in: UserCreate):
    """
    Create a new user account.
    Requires email, name, password, and optionally a role (default: student).
    """
    user = await User.find_one(User.email == user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = security.get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        name=user_in.name,
        hashed_password=hashed_password,
        role=user_in.role
    )
    await db_user.insert()
    return serialize_dict(db_user)

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate a user and return a JWT access token.
    Uses standard OAuth2 password flow (username/password).
    """
    user = await User.find_one(User.email == form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
