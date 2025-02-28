from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from database import get_db, UserModel, Base, engine
from sqlalchemy.orm import Session
from pydantic import BaseModel

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request validation
class UserLogin(BaseModel):
    email: str
    password: str

class UserSignup(BaseModel):
    name: str
    email: str
    password: str

# Constants
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Create tables
Base.metadata.create_all(bind=engine)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.get("/")
async def root():
    return FileResponse('templates/login.html')

@app.get("/profile")
async def profile_page():
    return FileResponse('templates/profile.html')

@app.get("/app")
async def app_page():
    return FileResponse('templates/index.html')

@app.post("/signup")
async def signup(user: UserSignup, db: Session = Depends(get_db)):
    try:
        print(f"Signup attempt for email: {user.email}")
        
        # Check if user exists
        existing_user = db.query(UserModel).filter(UserModel.email == user.email).first()
        if existing_user:
            return JSONResponse(
                status_code=400,
                content={"message": "Email already registered"}
            )
        
        # Hash password
        hashed_password = bcrypt.hashpw(
            user.password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # Create new user
        new_user = UserModel(
            name=user.name,
            email=user.email,
            hashed_password=hashed_password
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create access token
        access_token = create_access_token(
            data={"sub": new_user.email},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        print(f"User created successfully: {new_user.email}")
        return JSONResponse(
            status_code=200,
            content={
                "access_token": access_token,
                "token_type": "bearer",
                "user_id": new_user.id
            }
        )
        
    except Exception as e:
        print(f"Signup error: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"message": str(e)}
        )

@app.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    try:
        print(f"Login attempt for email: {user.email}")
        
        # Find user
        db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
        if not db_user:
            return JSONResponse(
                status_code=401,
                content={"message": "Invalid email or password"}
            )
        
        # Verify password
        if not bcrypt.checkpw(
            user.password.encode('utf-8'),
            db_user.hashed_password.encode('utf-8')
        ):
            return JSONResponse(
                status_code=401,
                content={"message": "Invalid email or password"}
            )
        
        # Create access token
        access_token = create_access_token(
            data={"sub": db_user.email},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        print(f"Login successful for: {db_user.email}")
        return JSONResponse(
            status_code=200,
            content={
                "access_token": access_token,
                "token_type": "bearer",
                "user_id": db_user.id
            }
        )
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"message": str(e)}
        )

@app.post("/api/update-profile")
async def update_profile(request: Request, db: Session = Depends(get_db)):
    try:
        # Get request body
        profile_data = await request.json()
        
        # Get current user from token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JSONResponse(
                status_code=401,
                content={"message": "Not authenticated"}
            )
        
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        
        # Update user profile
        user = db.query(UserModel).filter(UserModel.email == email).first()
        if not user:
            return JSONResponse(
                status_code=404,
                content={"message": "User not found"}
            )
        
        # Update user fields
        user.age = profile_data.get('age')
        user.location = profile_data.get('location')
        user.bio = profile_data.get('bio')
        user.interests = ','.join(profile_data.get('interests', []))
        
        db.commit()
        
        return JSONResponse(
            status_code=200,
            content={"message": "Profile updated successfully"}
        )
        
    except Exception as e:
        print(f"Error updating profile: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"message": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 