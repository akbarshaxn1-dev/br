from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models import UserCreate, UserLogin, TokenResponse, UserResponse, TwoFASetupResponse
from database import get_db
from utils.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token, generate_backup_codes
from utils.permissions import Permissions
from utils.audit import log_action
from datetime import datetime, timedelta, timezone
from config import config
import pyotp
import qrcode
import io
import base64
from typing import Optional

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload or payload.get('type') != 'access':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user_id = payload.get('user_id')
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    db = get_db()
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.get('is_active'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    # Convert datetime strings if needed
    if isinstance(user.get('created_at'), str):
        user['created_at'] = datetime.fromisoformat(user['created_at'])
    
    return user

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, request: Request):
    """Register a new user"""
    db = get_db()
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create user document
    user_dict = user_data.model_dump(exclude={'password'})
    user_dict['password_hash'] = hashed_password
    user_dict['is_active'] = True
    user_dict['two_fa_enabled'] = False
    user_dict['created_at'] = datetime.now(timezone.utc).isoformat()
    
    # Generate unique ID
    from models import UserBase
    user_base = UserBase(**user_dict)
    user_dict['id'] = user_base.id
    
    # Insert user
    await db.users.insert_one(user_dict)
    
    # Log action
    await log_action(
        user_id=user_dict['id'],
        user_email=user_dict['email'],
        action="user_registered",
        resource_type="user",
        resource_id=user_dict['id'],
        ip_address=request.client.host if request.client else None
    )
    
    # Return user without sensitive data
    user_response = {k: v for k, v in user_dict.items() if k not in ['password_hash', 'two_fa_secret', 'backup_codes']}
    if isinstance(user_response['created_at'], str):
        user_response['created_at'] = datetime.fromisoformat(user_response['created_at'])
    
    return user_response

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, request: Request):
    """Login user and return tokens"""
    db = get_db()
    
    # Find user
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.get('is_active', True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    # Check 2FA if enabled
    if user.get('two_fa_enabled', False):
        if not credentials.otp_code:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="2FA code required"
            )
        
        # Verify OTP
        totp = pyotp.TOTP(user['two_fa_secret'])
        if not totp.verify(credentials.otp_code, valid_window=1):
            # Check backup codes
            if credentials.otp_code not in user.get('backup_codes', []):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid 2FA code"
                )
            else:
                # Remove used backup code
                await db.users.update_one(
                    {"id": user['id']},
                    {"$pull": {"backup_codes": credentials.otp_code}}
                )
    
    # Create tokens
    access_token = create_access_token(
        data={"user_id": user['id'], "email": user['email'], "role": user['role']}
    )
    refresh_token = create_refresh_token()
    
    # Store refresh token
    refresh_token_doc = {
        "token": refresh_token,
        "user_id": user['id'],
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.refresh_tokens.insert_one(refresh_token_doc)
    
    # Log login
    await log_action(
        user_id=user['id'],
        user_email=user['email'],
        action="user_login",
        resource_type="auth",
        resource_id=user['id'],
        ip_address=request.client.host if request.client else None
    )
    
    # Prepare user response
    user_response = {k: v for k, v in user.items() if k not in ['password_hash', 'two_fa_secret', 'backup_codes']}
    if isinstance(user_response['created_at'], str):
        user_response['created_at'] = datetime.fromisoformat(user_response['created_at'])
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user_response
    }

@router.post("/refresh", data-testid="refresh-token-endpoint")
async def refresh_access_token(refresh_token: str):
    """Refresh access token using refresh token"""
    db = get_db()
    
    # Find refresh token
    token_doc = await db.refresh_tokens.find_one({"token": refresh_token}, {"_id": 0})
    if not token_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Check expiration
    expires_at = datetime.fromisoformat(token_doc['expires_at'])
    if expires_at < datetime.now(timezone.utc):
        # Delete expired token
        await db.refresh_tokens.delete_one({"token": refresh_token})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )
    
    # Get user
    user = await db.users.find_one({"id": token_doc['user_id']}, {"_id": 0})
    if not user or not user.get('is_active', True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or disabled"
        )
    
    # Create new access token
    access_token = create_access_token(
        data={"user_id": user['id'], "email": user['email'], "role": user['role']}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/logout", data-testid="logout-endpoint")
async def logout(refresh_token: str, current_user: dict = Depends(get_current_user)):
    """Logout user by invalidating refresh token"""
    db = get_db()
    
    await db.refresh_tokens.delete_one({"token": refresh_token, "user_id": current_user['id']})
    
    return {"message": "Logged out successfully"}

@router.post("/setup-2fa", response_model=TwoFASetupResponse, data-testid="setup-2fa-endpoint")
async def setup_2fa(current_user: dict = Depends(get_current_user)):
    """Setup 2FA for user"""
    db = get_db()
    
    # Check if role requires 2FA
    if not Permissions.requires_2fa(current_user['role']):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="2FA not required for your role"
        )
    
    # Generate secret
    secret = pyotp.random_base32()
    
    # Generate QR code
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=current_user['email'],
        issuer_name="Единый Портал Управления"
    )
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    # Generate backup codes
    backup_codes = generate_backup_codes()
    
    # Store secret and backup codes
    await db.users.update_one(
        {"id": current_user['id']},
        {"$set": {
            "two_fa_secret": secret,
            "backup_codes": backup_codes,
            "two_fa_enabled": False  # Will be enabled after verification
        }}
    )
    
    return {
        "secret": secret,
        "qr_code_url": f"data:image/png;base64,{qr_code_base64}",
        "backup_codes": backup_codes
    }

@router.post("/verify-2fa", data-testid="verify-2fa-endpoint")
async def verify_2fa(otp_code: str, current_user: dict = Depends(get_current_user)):
    """Verify and enable 2FA"""
    db = get_db()
    
    user = await db.users.find_one({"id": current_user['id']}, {"_id": 0})
    if not user.get('two_fa_secret'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA setup not initiated"
        )
    
    # Verify OTP
    totp = pyotp.TOTP(user['two_fa_secret'])
    if not totp.verify(otp_code, valid_window=1):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid 2FA code"
        )
    
    # Enable 2FA
    await db.users.update_one(
        {"id": current_user['id']},
        {"$set": {"two_fa_enabled": True}}
    )
    
    # Log action
    await log_action(
        user_id=current_user['id'],
        user_email=current_user['email'],
        action="2fa_enabled",
        resource_type="user",
        resource_id=current_user['id']
    )
    
    return {"message": "2FA enabled successfully"}

@router.get("/me", response_model=UserResponse, data-testid="get-current-user-endpoint")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    return current_user
