from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from typing import List
from database import SessionLocal, engine, Base
import models, schemas

# Import the utility function
from utils import calculate_interest_similarity  # Import from utils.py

app = FastAPI()

# Database initialization
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create a new user endpoint
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        schemas.UserCreate.validate(user)  # Validation
        db_user = models.User(**user.dict())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    # Handle exceptions
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

# Get all users with pagination (skip and limit) endpoint
@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        users = db.query(models.User).offset(skip).limit(limit).all()
        return users
    
    # Handle exceptions
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

# Get a specific user by their ID endpoint
@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
    # Handle exceptions
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

# Update a user's details endpoint
@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    try:
        db_user = db.query(models.User).filter(models.User.id == user_id).first()
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.email:
            schemas.UserUpdate.validate(user)  # Validate email if being updated
        
        user_data = user.dict(exclude_unset=True)
        for key, value in user_data.items():
            setattr(db_user, key, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    
    # Handle exceptions
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

# Delete a user by their ID endpoint
@app.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    try:
        db_user = db.query(models.User).filter(models.User.id == user_id).first()
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        db.delete(db_user)
        db.commit()
        return db_user
    
    # Handle exceptions
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

# Get user's potential matches endpoint
@app.get("/users/{user_id}/matches", response_model=List[schemas.UserMatch])
def find_matches(user_id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        age_range = (user.age - 3, user.age + 3)
        
        # Case-insensitive gender comparison using ilike
        potential_matches = db.query(models.User).filter(
            models.User.id != user_id,
            models.User.age.between(*age_range),
            func.lower(models.User.gender) != func.lower(user.gender)  # Case-insensitive comparison
        ).all()
        
        # Split interests and convert to lowercase for case-insensitive comparison
        user_interests = [interest.lower() for interest in user.interests.split(',')]
        matches = []
        
        for match in potential_matches:
            match_interests = [interest.lower() for interest in match.interests.split(',')]
            
            # Call the external function to calculate similarity
            interest_similarity = calculate_interest_similarity(user_interests, match_interests)
            
            # Composite score calculation
            composite_score = (
                0.6 * interest_similarity +
                0.3 * (1 if match.city == user.city else 0) +
                0.1 * (1 - abs(user.age - match.age) / 10)
            )
            
            if composite_score > 0:
                match_dict = match.__dict__
                match_dict['interests'] = match_interests
                matches.append((match_dict, composite_score))
        
        sorted_matches = sorted(matches, key=lambda x: x[1], reverse=True)
        return [match for match, _ in sorted_matches[:5]]
    
    # Error Handling
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
