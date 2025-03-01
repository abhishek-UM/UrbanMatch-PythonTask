from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models, schemas
import json
from sqlalchemy import text
app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# this is a update user endpoint
@app.patch("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user_data: schemas.UserUpdate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user


# this is a delete user endpoint
@app.delete("/users/{user_id}", response_model=dict)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted"}

# this is a find matches for a user endpoint
@app.get("/users/{user_id}/matches", response_model=list[schemas.User])
def find_matches(user_id: int, db: Session = Depends(get_db)):
    # Retrieve the given user's profile
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
         raise HTTPException(status_code=404, detail="User not found")
    matches = []
    # Retrieve all other users
    all_users = db.query(models.User).filter(models.User.id != user_id).all()
    for other in all_users:
         # If there's at least one common interest, consider it a match
         if set(user.interests).intersection(set(other.interests)):
              matches.append(other)
    return matches

# this is a upgraded matchmaking endpoint that returns a match score 😅
@app.get("/users/{user_id}/matches_score", response_model=list[schemas.UserMatch])
def find_matches_score(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    matches = []
    all_users = db.query(models.User).filter(models.User.id != user_id).all()
    for other in all_users:
        # here we are calculating common interests score
        common_interests = set(user.interests).intersection(set(other.interests))
        score = len(common_interests)
        # here we are adding bonus if both users are in the same city
        if user.city.lower() == other.city.lower():
            score += 1
        
        # Only consider matches with a score greater than 0
        if score > 0:
            matches.append({"user": other, "match_score": score})
    
    # Sort matches by score in descending order
    matches.sort(key=lambda x: x["match_score"], reverse=True)
    return matches
