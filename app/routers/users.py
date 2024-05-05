from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.future import select

from app import schemas
from app.database import get_async_session
from app.models import User
from app.services import authenticate_user, create_access_token, pwd_context

router = APIRouter()


@router.post("/users/", response_model=schemas.UserInDB, summary="Create a new user",
             description="Register a new user by providing a name, login,"
                         " and password. Returns the created user data with a hashed password.")
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_async_session)):
    """
        Create a new user in the database.

        - **name**: each user must have a name
        - **login**: a unique login which is used for user identification
        - **password**: a password that will be hashed before storage
    """
    async with db as session:
        result = await session.execute(select(User).where(User.login == user.login))
        user_exists = result.scalars().first()
        if user_exists:
            raise HTTPException(status_code=400, detail="Login already registered")
        hashed_password = pwd_context.hash(user.password)
        new_user = User(username=user.username, login=user.login, hashed_password=hashed_password)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user


@router.post("/token", response_model=schemas.Token, summary="Authenticate user and retrieve token",
             description="Authenticate a user by their login and password."
                         " Returns a JWT token for accessing protected endpoints.")
async def login_for_access_token(db: Session = Depends(get_async_session),
                                 form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate a user and issue a JWT token.

    This endpoint allows users to submit their login and password in exchange for a JWT token.
    This token can be used to authenticate subsequent requests to the API.

    - **username**: The login of the user. Must match the login used at registration.
    - **password**: The password of the user. Must match the password used at registration.

    If the username or password is incorrect, a 401 error is returned, indicating unauthorized access.

    On successful authentication, a JWT token is returned which expires in 30 minutes.
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(user_id=user.id, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
