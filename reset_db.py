import os
import bcrypt
import time
from database import Base, engine, SessionLocal, UserModel

def reset_database():
    print("Starting database reset...")
    
    # Try to remove the database with retries
    for attempt in range(5):  # Try 5 times
        try:
            if os.path.exists("sql_app.db"):
                os.remove("sql_app.db")
                print("Removed existing database")
            break
        except PermissionError:
            print(f"Database is locked, attempt {attempt + 1} of 5...")
            time.sleep(1)  # Wait 1 second before retry
        except Exception as e:
            print(f"Error removing database: {e}")
            time.sleep(1)

    try:
        # Create new tables
        Base.metadata.create_all(bind=engine)
        print("Created new tables")

        # Create a session
        db = SessionLocal()

        try:
            # Create test user
            test_password = "test123"
            hashed_password = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt())
            
            test_user = UserModel(
                email="test@example.com",
                name="Test User",
                hashed_password=hashed_password.decode('utf-8'),
                age=25,
                location="New York",
                bio="Test user bio",
                interests="reading,music,travel"
            )
            
            db.add(test_user)
            db.commit()
            
            # Verify user creation
            user = db.query(UserModel).filter(UserModel.email == "test@example.com").first()
            if user:
                print(f"Test user created successfully: {user.email}")
            else:
                print("Failed to create test user!")
                
        except Exception as e:
            print(f"Error creating test user: {e}")
            db.rollback()
        finally:
            db.close()
            
    except Exception as e:
        print(f"Database error: {e}")
        return False

    return True

if __name__ == "__main__":
    print("Starting database initialization...")
    
    # Make sure no server is running
    input("Please make sure the FastAPI server is stopped (press Enter to continue)...")
    
    if reset_database():
        print("Database reset completed successfully!")
    else:
        print("Database reset failed!") 