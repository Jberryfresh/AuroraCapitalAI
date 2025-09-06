"""Reset database tables."""
from aurora.database import Base, engine

def main():
    """Drop and recreate all tables."""
    print("Dropping all tables...")
    Base.metadata.drop_all(engine)
    
    print("Creating all tables...")
    Base.metadata.create_all(engine)
    
    print("Database reset complete!")

if __name__ == "__main__":
    main()
