from datetime import datetime, timedelta
import jwt
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from app.database import get_async_session
from app.models import Product, User
from app.schemas import ProductInfo
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.future import select

from config import SECRET_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(user_id: int, expires_delta: timedelta = None):
    to_encode = {"sub": str(user_id)}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(db: AsyncSession, username: str, password: str) -> User:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None


async def get_current_user(db: AsyncSession = Depends(get_async_session), token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user_id = int(user_id)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user ID format")

    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


async def create_new_product(db: AsyncSession, product_info: ProductInfo) -> int:
    """
    Creates a new product in the database if it doesn't exist.

    Args:
    db (AsyncSession): The database session.
    product_info (ProductInfo): The product data.

    Returns:
    int: The ID of the created or existing product.
    """
    # First check if the product already exists to avoid duplicates
    existing_product = await db.execute(select(Product).filter(Product.name == product_info.name))
    product = existing_product.scalars().first()

    if product:
        return product.id  # Return existing product ID if product is found

    # If not found, create a new product
    new_product = Product(
        name=product_info.name,
        price=product_info.price
    )
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)

    return new_product.id


def format_receipt(receipt):
    lines = []
    lines.append("ФОП Джонсонок Борис")
    lines.append("=======================")

    total = 0
    for item in receipt.items:
        item_total = item.product.price * item.quantity
        total += item_total
        lines.append(f"{item.product.name} {item.quantity} x {item.product.price:.2f} {item_total:.2f}")

    lines.append("-----------------------")
    lines.append(f"СУМА {total:.2f}")
    lines.append(f"Картка {receipt.payment_amount:.2f}")
    lines.append(f"Решта {max(0.0, receipt.payment_amount - total):.2f}")
    lines.append("=======================")
    lines.append(datetime.now().strftime("%d.%m.%Y %H:%M"))
    lines.append("Дякуємо за покупку!")

    return "\n".join(lines)
