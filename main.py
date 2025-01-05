from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas
from models import Base
from typing import List
import re
from geopy.distance import geodesic
from typing import List

app = FastAPI()

Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint to create a new user

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Regular expression for validating an email address
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    
    if not re.match(email_regex, user.email):
        raise HTTPException(status_code=400, detail="Invalid email address")
    
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Endpoint to get all users (with pagination support)

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    # Query the database for users with pagination
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users



# Endpoint to get a specific user by their ID


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Endpoint to update user details (partial update)

@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, updated_user: schemas.UserUpdate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in updated_user.dict(exclude_unset=True).items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user

# Endpoint to delete a user by ID

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}


# Endpoint to find matches for a user based on shared interests and city

@app.get("/users/{user_id}/matches", response_model=List[schemas.UserWithScore])
def find_matches(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Filter potential matches by age difference ±3
    potential_matches = db.query(models.User).filter(
        models.User.id != user_id,
        abs(models.User.age - user.age) <= 3  # Only matches with age difference within ±3
    ).all()

    def calculate_match_score(other_user: models.User) -> float:
        # intrest similarity
        shared_interests = len(set(user.interests) & set(other_user.interests))
        total_interests = len(set(user.interests) | set(other_user.interests))
        interest_similarity = shared_interests / total_interests if total_interests > 0 else 0

        # city score
        user_coords = (user.latitude, user.longitude)
        other_coords = (other_user.latitude, other_user.longitude)
        city_proximity_score = max(1 - geodesic(user_coords, other_coords).km / 100, 0)  # close city score higher
        
        #age difference calculation
        age_score = 1 
        
        score = (
            50 * interest_similarity +  # Interest similarity (max 50)
            30 * city_proximity_score +  # City proximity (max 30)
            20 * age_score  # Age similarity (max 20)
        )
        return score

    # score calculation
    matches_with_scores = [
        {"user": match, "score": calculate_match_score(match)}
        for match in potential_matches
    ]
    matches_with_scores.sort(key=lambda x: x["score"], reverse=True)

    #response
    result = [
        schemas.UserWithScore(
            id=match["user"].id,
            email=match["user"].email,
            city=match["user"].city,
            interests=match["user"].interests,
            latitude=match["user"].latitude,
            longitude=match["user"].longitude,
            score=match["score"]
        )
        for match in matches_with_scores
    ]

    return result


