from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta, datetime  # Add 'datetime' here
from app.database import engine, Base, get_db_session
from app.models import User, Product, Cart, CartItem, Order, OrderItem
from app.auth import create_access_token, get_current_user
from pydantic import BaseModel

app = FastAPI()
Base.metadata.create_all(bind=engine)


class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str


class UserResponse(BaseModel):
    username: str
    email: str
    full_name: str


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: float
    stock: int


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: float
    stock: int


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: ProductResponse


class OrderResponse(BaseModel):
    id: int
    total_amount: float
    status: str
    created_at: datetime  # Now works with the import


@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db_session)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    new_user = User(username=user.username, email=user.email, full_name=user.full_name)
    new_user.set_password(user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db_session)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=15))
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.post("/products/", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db_session),
                   current_user: User = Depends(get_current_user)):
    new_product = Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@app.get("/products/", response_model=List[ProductResponse])
def get_products(db: Session = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    products = db.query(Product).all()
    return products


@app.post("/carts/items/", response_model=CartItemResponse)
def add_to_cart(item: CartItemCreate, db: Session = Depends(get_db_session),
                current_user: User = Depends(get_current_user)):
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    cart_item = CartItem(cart_id=cart.id, product_id=item.product_id, quantity=item.quantity)
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item


@app.get("/carts/", response_model=List[CartItemResponse])
def get_cart(db: Session = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    cart_items = db.query(CartItem).filter(CartItem.cart_id == current_user.id).all()
    return cart_items


@app.post("/checkout/", response_model=OrderResponse)
def checkout(db: Session = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    cart_items = db.query(CartItem).filter(CartItem.cart_id == current_user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="No items in cart")
    total_amount = sum(item.quantity * item.product.price for item in cart_items)
    new_order = Order(user_id=current_user.id, total_amount=total_amount, status="pending")
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    for cart_item in cart_items:
        order_item = OrderItem(order_id=new_order.id, product_id=cart_item.product_id, quantity=cart_item.quantity,
                               price_at_time=cart_item.product.price)
        db.add(order_item)
        db.delete(cart_item)
    db.commit()
    return new_order
