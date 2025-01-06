# Suggested code may be subject to a license. Learn more: ~LicenseLog:140021096.
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from db.config import get_db
import models
import schemas.UserSchema as UserSchemas
from utils.validation import email_validation

app = FastAPI()

@app.post("/users/", response_model=UserSchemas.User)
def create_user(user: UserSchemas.UserCreate, db: Session = Depends(get_db)):
    if not email_validation(user.email):
        raise HTTPException(status_code=400, detail="Invalid email address")
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=list[UserSchemas.User])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=UserSchemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.patch("/users/{user_id}", response_model=UserSchemas.User)
def update_user(user_id: int, user: UserSchemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    update_data = user.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user
    
@app.delete("/users/{user_id}", response_model=UserSchemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return user

@app.get("/recommendation/{user_id}", response_model=list[UserSchemas.User])
def recommendation(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    query = text("""
        SELECT 
            id, name, age, gender, email, city, interests,
            array_length(ARRAY(
                SELECT unnest(interests) 
                INTERSECT 
                SELECT unnest(ARRAY[:user_interests]::VARCHAR[])
            ), 1) AS intersection_size
        FROM users
        WHERE 
            id != :user_id AND
            city = :city AND
            age BETWEEN :min_age AND :max_age AND
            (
                (age >= 18 AND :user_age >= 18) OR 
                (age < 18 AND :user_age < 18)
            ) AND
            interests && ARRAY[:user_interests]::VARCHAR[]
        ORDER BY intersection_size DESC
    """)

    # Replace these with your actual variables
    params = {
        "user_id": user_id,
        "city": user.city,
        "min_age": user.age - 2,
        "max_age": user.age + 2,
        "user_age": user.age,
        "user_interests": user.interests,
    }

    recommendations = db.execute(query, params).fetchall()

    return recommendations

if __name__ == "__main__":
    app.run()