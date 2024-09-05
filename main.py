from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models, schemas
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_,text

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def create_user():
    return {"message":"Welcome"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(**user.dict())
    try: 
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError as e:
        db.rollback() 
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
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

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id== user_id).first()
    if user is None:
        raise HTTPException(status_code =404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message":"User deleted successfully"}


@app.put("/users/{user_id}")
def update_user(user_id:int,user_data:schemas.UserBase,db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id== user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    updated_data = user_data.model_dump(exclude_unset=True)

    for key,value in updated_data.items():
        setattr(user,key,value)
    
    db.commit()
    db.refresh(user)
    return {"user_id":user_id,"updated_data":user}
    
def sort_key(t):
    _, interests,same_city,age_diff  = t
    return {-interests,not same_city,age_diff}

@app.get("/find-matches/{user_id}", response_model=list[schemas.User])
def find_matches(user_id: int,age_range:int = 5,db: Session = Depends(get_db)):
    current_user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    min_age,max_age = min(18,current_user.age-age_range),current_user.age+age_range
    filters = []
    filters.append(models.User.age>=min_age)
    filters.append(models.User.age<=max_age)
    filters.append(models.User.gender!=current_user.gender)
    query = db.query(models.User).filter(*filters).all()

    target_interests = set(current_user.interests)
    matches = []
    for user in query:
        print(user)
        print(user.interests)
        user_interests = set(user.interests)
        common_interests = len(target_interests.intersection(user_interests))
        print(common_interests)
        if common_interests>0:
            city = 0
            age_difference = 0
            if current_user.city == user.city:
                city = 1
            age_difference = abs(user.age-current_user.age)
            p = (user,common_interests,city,age_difference)
            matches.append(p)
    
    sorted_matches = sorted(matches,key = sort_key)
    result = [match[0] for match in sorted_matches]
    return result
