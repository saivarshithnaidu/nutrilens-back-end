from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models.sql_models import User, PasswordReset
from models.auth_schemas import UserCreate, UserLogin, Token, UserResponse, ForgotPasswordRequest, ResetPasswordRequest
from core.security import verify_password, get_password_hash, create_access_token, decode_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import datetime, timedelta
import uuid

router = APIRouter()

@router.post("/signup", response_model=Token)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Check existing user
        db_user = db.query(User).filter(or_(User.email == user.email, User.phone == user.phone)).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email or Phone already registered")
        
        # Create User
        hashed_pw = get_password_hash(user.password)
        new_user = User(
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            hashed_password=hashed_pw
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Generate Token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": new_user.email, "user_id": new_user.id},
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        print(f"Signup Error: {e}") 
        # Check if it is a DB connection error (generic catch for now)
        if "OperationalError" in str(e) or "database" in str(e).lower():
             raise HTTPException(status_code=503, detail="Database temporarily unavailable")
        raise e

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    try:
        # Find by email OR phone
        user = db.query(User).filter(
            or_(User.email == login_data.username, User.phone == login_data.username)
        ).first()
        
        if not user:
            raise HTTPException(status_code=400, detail="Incorrect email/phone or password")
        
        if not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Incorrect email/phone or password")
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        print(f"Login Error: {e}")
        if "OperationalError" in str(e) or "database" in str(e).lower():
             raise HTTPException(status_code=503, detail="Database temporarily unavailable")
        raise e

@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        or_(User.email == request.email_or_phone, User.phone == request.email_or_phone)
    ).first()
    
    if not user:
        # Don't reveal user existence
        return {"message": "If account exists, reset instructions have been sent."}
    
    # Generate Token
    reset_token = str(uuid.uuid4())
    expires = datetime.utcnow() + timedelta(minutes=15)
    
    reset_entry = PasswordReset(
        user_id=user.id,
        reset_token=reset_token,
        expires_at=expires
    )
    db.add(reset_entry)
    db.commit()
    
    # SIMULATE SENDING EMAIL
    print(f"\n[SIMULATION] PASSWORD RESET LINK FOR {user.email}:")
    print(f"Token: {reset_token}")
    print(f"Link: http://localhost:3000/auth/reset-password?token={reset_token}\n")
    
    return {"message": "Password reset instructions sent (check server console)."}

@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    reset_entry = db.query(PasswordReset).filter(PasswordReset.reset_token == request.token).first()
    
    if not reset_entry:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    if reset_entry.used:
        raise HTTPException(status_code=400, detail="Token already used")
        
    if reset_entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token expired")
    
    # Update Password
    user = db.query(User).filter(User.id == reset_entry.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.hashed_password = get_password_hash(request.new_password)
    reset_entry.used = True
    
    db.commit()
    return {"message": "Password updated successfully"}

from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.get("/me", response_model=UserResponse)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if not payload:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
