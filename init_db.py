from database import Base, engine

# Drop all existing tables
Base.metadata.drop_all(bind=engine)

# Create all tables fresh
Base.metadata.create_all(bind=engine)

print("Database initialized successfully!") 