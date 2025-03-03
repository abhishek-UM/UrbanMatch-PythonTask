from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends,Query
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
    db_email = db.query(models.User).filter(models.User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
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

@app.delete("/users/{user_id}",response_model=schemas.DeleteResponse)
def delete_user(user_id:int,db:Session=Depends(get_db)):
    db_user=db.query(models.User).filter(models.User.id==user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()

    return  schemas.DeleteResponse(
        status_code=200,
        detail=f"Successfully deleted user { db_user.name}"
    )



@app.put("/users/{user_id}", response_model=schemas.UpdateResponse)
def update_user(user_id: int, user: schemas.UserBase, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    
    if user.email and user.email != db_user.email:
        email_exists = db.query(models.User).filter(models.User.email == user.email).first()
        if email_exists:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    
    update_data = user.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)

    
    return schemas.UpdateResponse(
        status_code=200,
        content={"message": f"Successfully updated user {db_user.name}"}
    )


@app.get("/matches", response_model=List[schemas.User])
def find_matches(
    city: str = Query(..., description="City to match within"),
    user_age: int = Query(..., ge=18, description="User's age to determine age range"),

    age_range: int = Query(18, ge=0, description="Age range around user's age"),
    preferred_gender: Optional[str] = Query(None, description="Preferred gender to filter by"),
    interests: List[str] = Query(..., description="List of interests to match"),
    db: Session = Depends(get_db)
) -> List[schemas.User]:
    
    min_age = max(user_age - age_range, 18)
    max_age = user_age + age_range

    
    query = db.query(models.User).filter(
        models.User.city == city,
        models.User.age >= min_age,
        models.User.age <= max_age
    )

   
    if preferred_gender:
        query = query.filter(models.User.gender == preferred_gender)

    potential_matches = query.all()

   
    user_interests = set(interests)
    matches = []
    for person in potential_matches:
        person_interests = set(person.interests or [])
        if user_interests & person_interests:  
            matches.append(person)

    
    return matches  


