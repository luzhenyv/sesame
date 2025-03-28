import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from scripts.seed_db import seed_database


def run_seed():
    engine = create_engine(settings.get_database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()


if __name__ == "__main__":
# The seeding script will create:
#    3 users with different email addresses and passwords
#    7 family members (mix of humans and pets) distributed among the users
# The demo user credentials are:
#    demo@example.com / demo123
#    john@example.com / john123
#    jane@example.com / jane123

    run_seed()
