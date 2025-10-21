# E-Commerce API

A secure E-Commerce API built with FastAPI, SQLAlchemy, and PostgreSQL. Features user authentication, product management, shopping cart, and checkout. Deployed on AWS EC2.

## Features
- User registration/login with JWT tokens.
- CRUD for products (create/list).
- Shopping cart (add/view items).
- Checkout to create orders.

## Tech Stack
- FastAPI for async APIs.
- SQLAlchemy ORM with PostgreSQL.
- Pydantic for validation.
- JWT for authentication.
- Swagger UI for testing.

## Quick Start
1. Clone the repo: `git clone https://github.com/Ezaz-555/ecommerce2.git`
2. Install dependencies: `pip install fastapi uvicorn sqlalchemy python-jose[cryptography] passlib[bcrypt] python-dotenv`
3. Copy `.env.example` to `.env` and add your `SECRET_KEY`.
4. Run: `uvicorn app.main:app --port 8000 --reload`
5. Test at `http://127.0.0.1:8000/docs`.

## API Endpoints
- POST /users/ - Create user.
- POST /login - Get token.
- POST /products/ - Create product.
- GET /products/ - List products.
- POST /carts/items/ - Add to cart.
- GET /carts/ - View cart.
- POST /checkout/ - Process checkout.

## Lessons Learned
- Handled relationships (user-cart-product).
- Debugged bcrypt/auth issues.
- Secured endpoints with dependencies.

## Future Improvements
- Stripe payments.
- Email notifications.

Built as a beginner project for backend skills. Feedback welcome!

#FastAPI #Python #Ecommerce #Backend #JobSearch
