from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.models import User
from app.database import get_db
from app.schemas import UserCreate, UserOut, Token
from app.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=UserOut,
    summary="Register a new user",
    description="""
    Registers a new user account. The user must provide a unique username, password, name, and surname.
    \n- If the username is already registered, it returns an error.
    \n- The password is securely hashed before saving to the database.
    """,
)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        hashed_password=hashed_password,
        name=user.name,
        surname=user.surname,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post(
    "/login",
    response_model=Token,
    summary="Login a user",
    description="""
    Authenticates a user with username and password and returns an access token and a refresh token.
    \n- Supports both form-encoded and JSON login requests.
    \n- If the login credentials are incorrect, an error is returned.
    """,
)
def login_user(
    request: Request,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    if request.headers.get("content-type") == "application/json":
        body = request.json()  # No need to await this anymore
        user_data = UserCreate(**body)
        username = user_data.username
        password = user_data.password
    else:
        username = form_data.username
        password = form_data.password

    db_user = db.query(User).filter(User.username == username).first()
    if not db_user or not verify_password(password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": db_user.username})
    refresh_token = create_refresh_token(data={"sub": db_user.username})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh access token",
    description="""
    Refreshes the access token using a valid refresh token. 
    \n- Returns a new access token and the same refresh token.
    \n- If the refresh token is invalid or the user is not found, an error is returned.
    """,
)
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    username = verify_refresh_token(refresh_token)
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")

    access_token = create_access_token(data={"sub": db_user.username})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
