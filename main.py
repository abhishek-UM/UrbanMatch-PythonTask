from typing import List
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models, schemas

import logging

logging.basicConfig(
    level=logging.INFO,  # Adjust level as needed (DEBUG, INFO, etc.)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/create-user", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        logger.info("Creating new user with email: %s", user.email)
        db_user = models.User(
            name=user.name,
            age=user.age,
            gender=user.gender,
            email=user.email,
            city=user.city,
            interests=user.interests
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info("User created successfully with id: %s", db_user.id)
        return db_user
    except IntegrityError as he:
        db.rollback()
        logger.warning("IntegrityError: %s", str(he))
        raise HTTPException(status_code=409, detail="User with this email already exists")
    except Exception as e:
        logger.error("Error occurred while creating user: %s", str(e))
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error while creating user ")


@app.get("/find-all-users", response_model=List[schemas.User])
def read_users(db: Session = Depends(get_db)):
    try:
        logger.info("Fetching all users")
        users = db.query(models.User).all()
        logger.info("Fetched %d users", len(users))
        return users
    except Exception as e:
        logger.error("Error occurred while fetching users: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error while fetching users")


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    try:
        logger.info("Fetching user with id: %s", user_id)
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user is None:
            logger.warning("User with id %s not found", user_id)
            raise HTTPException(status_code=404, detail="User not found")
        logger.info("User with id %s fetched successfully", user_id)
        return user
    except Exception as e:
        logger.error("Error occurred while fetching user with id %s: %s", user_id, str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error while fetching user "+str(e))

# ssss
@app.get("/match", response_model=List[schemas.CandidateSuggestion])
def calculate_match(user_identifier: schemas.UserIdentifier, db: Session = Depends(get_db)):
    try:
        logger.info("Calculating match for user: %s", user_identifier.email)
        # Retrieve the full user profile from the database using name and email
        user = db.query(models.User).filter(
            models.User.email == user_identifier.email,
            models.User.name == user_identifier.name
        ).first()
        if not user:
            logger.warning("User not found with email: %s and name: %s", user_identifier.email, user_identifier.name)
            raise HTTPException(status_code=404, detail="User not found")

        # Get candidates of the opposite gender
        candidates = db.query(models.User).filter(models.User.gender != user.gender).all()
        if not candidates:
            logger.warning("No matches found for user with email: %s", user_identifier.email)
            raise HTTPException(status_code=404, detail="No matches found Dont worry you are unique in your own way")

        suggestions = []
        user_interests = set(user.interests)

        for candidate in candidates:
            candidate_interests = set(candidate.interests)
            # Calculate interests similarity using Jaccard similarity
            common_interests = user_interests.intersection(candidate_interests)
            union_interests = user_interests.union(candidate_interests)
            interest_score = len(common_interests) / len(union_interests) if union_interests else 0

            # Calculate age compatibility: score decreases linearly with age difference (threshold 10 years)
            age_diff = abs(candidate.age - user.age)
            max_age_diff = 5
            age_score = max(0, 1 - (age_diff / max_age_diff))

            # City match: bonus if same city (score 1 if same, 0 otherwise)
            city_score = 1 if candidate.city.lower() == user.city.lower() else 0

            # Weight factors for composite match_percentage
            weight_interest = 0.5
            weight_age = 0.3
            weight_city = 0.2

            total_score = (interest_score * weight_interest) + (age_score * weight_age) + (city_score * weight_city)
            match_percentage = round(total_score * 100, 2)  # Convert to percentage

            candidate_suggestion = schemas.CandidateSuggestion(
                id=candidate.id,
                name=candidate.name,
                email=candidate.email,
                age=candidate.age,
                gender=candidate.gender,
                city=candidate.city,
                interests=candidate.interests,
                match_percentage=match_percentage
            )
            suggestions.append(candidate_suggestion)

        # Sort suggestions by match_percentage in descending order and return the top 3
        suggestions.sort(key=lambda x: x.match_percentage, reverse=True)
        top_suggestions = suggestions[:3]
        logger.info("Match calculation successful for user %s. Found %d suggestions.", user_identifier.email,
                    len(top_suggestions))
        return top_suggestions

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error("Error occurred during match calculation: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error during match calculation")
