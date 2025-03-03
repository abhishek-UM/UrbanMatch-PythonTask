import json
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models, schemas

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
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = models.User(
        **user.model_dump(exclude={"interests"}),  # Use model_dump() instead of dict()
        interests=json.dumps(user.interests)  # Convert list to JSON
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db_user.interests = json.loads(db_user.interests)  # Convert back to list for response
    return db_user

@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(models.User).filter(models.User.is_deleted == False).offset(skip).limit(limit).all()
    
    # Ensure JSON deserialization for interests field
    for user in users:
        user.interests = json.loads(user.interests) if user.interests else []
    
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id, models.User.is_deleted == False).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Ensure JSON deserialization for interests field
    user.interests = json.loads(user.interests) if user.interests else []
    
    return user

@app.get("/users/{user_id}/matches", response_model=list[schemas.User])
def find_matches(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id, models.User.is_deleted == False).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_interests = json.loads(db_user.interests) if db_user.interests else []
    all_users = db.query(models.User).filter(models.User.is_deleted == False, models.User.id != user_id).all()

    matches = [
        user for user in all_users
        if set(json.loads(user.interests) if user.interests else []).intersection(user_interests)
    ]

    for match in matches:
        match.interests = json.loads(match.interests) if match.interests else []

    return matches

@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id, models.User.is_deleted == False).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.model_dump(exclude_unset=True)  # Ensure correct Pydantic usage

    if "email" in update_data and not schemas.validate_email(update_data["email"]):
        raise HTTPException(status_code=400, detail="Invalid email format")

    if "interests" in update_data:
        update_data["interests"] = json.dumps(update_data["interests"])  # Convert list to JSON

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    db_user.interests = json.loads(db_user.interests) if db_user.interests else []
    return db_user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.is_deleted = True  # Soft delete
    db.commit()
    return {"message": "User marked as deleted (soft delete)."}
