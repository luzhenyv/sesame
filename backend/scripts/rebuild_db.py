import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from app.db.base_class import Base
from app.core.config import settings

def rebuild_database():
    engine = create_engine(settings.get_database_url)
    
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    
    print("Database rebuilt successfully!")

if __name__ == "__main__":
    response = input("This will delete all data in the database. Are you sure? (y/N): ")
    if response.lower() == "y":
        rebuild_database()
    else:
        print("Operation cancelled.")
