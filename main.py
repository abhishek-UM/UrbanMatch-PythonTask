from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models, schemas
from typing import List
from pydantic import EmailStr

app = FastAPI()

Base.metadata.create_all(bind=engine)


class MatchingAlgorithm:
    WEIGHTS = {"age": 0.3, "location": 0.3, "interests": 0.4}

    MAX_AGE_DIFF = 10

    @staticmethod
    def calculate_age_score(user_age: int, match_age: int) -> float:
        """Calculate age compatibility (0 to 1)"""
        age_diff = abs(user_age - match_age)
        if age_diff > MatchingAlgorithm.MAX_AGE_DIFF:
            return 0
        return 1 - (age_diff / MatchingAlgorithm.MAX_AGE_DIFF)

    @staticmethod
    def calculate_location_score(user_city: str, match_city: str) -> float:
        """Calculate location compatibility (0 or 1)"""
        return 1.0 if user_city.lower() == match_city.lower() else 0.0

    @staticmethod
    def calculate_interests_score(
        user_interests: List[str], match_interests: List[str]
    ) -> float:
        """Calculate interests compatibility (0 to 1)"""
        user_interests_set = set(interest.lower() for interest in user_interests)
        match_interests_set = set(interest.lower() for interest in match_interests)

        if not user_interests_set or not match_interests_set:
            return 0.0

        common_interests = len(user_interests_set.intersection(match_interests_set))
        total_interests = len(user_interests_set)

        return common_interests / total_interests


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = (
        db.query(models.User).filter(models.User.email == user.email).first()
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_data = user.dict()
    db_user = models.User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.email and user_update.email != db_user.email:
        existing_user = (
            db.query(models.User).filter(models.User.email == user_update.email).first()
        )
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}


@app.get("/users/{user_id}/matches", response_model=List[schemas.UserMatch])
def find_matches(
    user_id: int,
    db: Session = Depends(get_db),
    min_age: int = None,
    max_age: int = None,
):
    """Find matches for a user"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    matches_query = db.query(models.User).filter(
        models.User.id != user_id,
        models.User.gender != user.gender,
    )

    if min_age:
        matches_query = matches_query.filter(models.User.age >= min_age)
    if max_age:
        matches_query = matches_query.filter(models.User.age <= max_age)

    potential_matches = matches_query.all()
    scored_matches = []

    for match in potential_matches:
        age_score = MatchingAlgorithm.calculate_age_score(user.age, match.age)
        location_score = MatchingAlgorithm.calculate_location_score(
            user.city, match.city
        )
        interests_score = MatchingAlgorithm.calculate_interests_score(
            user.interests, match.interests
        )

        total_score = (
            age_score * MatchingAlgorithm.WEIGHTS["age"]
            + location_score * MatchingAlgorithm.WEIGHTS["location"]
            + interests_score * MatchingAlgorithm.WEIGHTS["interests"]
        )

        if total_score > 0.5:
            scored_matches.append(
                {
                    "user": match,
                    "compatibility_score": round(total_score, 2),
                    "match_details": {
                        "age_compatibility": round(age_score, 2),
                        "location_compatibility": round(location_score, 2),
                        "interests_compatibility": round(interests_score, 2),
                    },
                }
            )

    scored_matches.sort(key=lambda x: x["compatibility_score"], reverse=True)

    return scored_matches
