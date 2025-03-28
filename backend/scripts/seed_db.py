from datetime import datetime, timedelta
import random
from typing import List
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.family_member import FamilyMember, MemberType
from app.api.v1.endpoints.auth import get_password_hash


def create_fake_users(db: Session) -> List[User]:
    users = [
        User(
            email="demo@example.com",
            hashed_password=get_password_hash("demo123"),
            full_name="Demo User",
            is_active=True,
        ),
        User(
            email="john@example.com",
            hashed_password=get_password_hash("john123"),
            full_name="John Doe",
            is_active=True,
        ),
        User(
            email="jane@example.com",
            hashed_password=get_password_hash("jane123"),
            full_name="Jane Smith",
            is_active=True,
        ),
    ]

    for user in users:
        db.add(user)
    db.commit()
    return users


def create_fake_family_members(db: Session, users: List[User]) -> List[FamilyMember]:
    members = []

    # Demo User's family members
    members.extend(
        [
            FamilyMember(
                name="John Smith",
                member_type=MemberType.HUMAN,
                relation_type="Father",
                date_of_birth=datetime(1980, 1, 1),
                health_score=95,
                notes="Loves hiking",
                manager_id=users[0].id,
            ),
            FamilyMember(
                name="Sarah Smith",
                member_type=MemberType.HUMAN,
                relation_type="Mother",
                date_of_birth=datetime(1982, 3, 15),
                health_score=92,
                notes="Enjoys cooking",
                manager_id=users[0].id,
            ),
            FamilyMember(
                name="Max",
                member_type=MemberType.PET,
                relation_type="Dog",
                date_of_birth=datetime(2020, 5, 10),
                health_score=88,
                notes="Golden Retriever",
                manager_id=users[0].id,
            ),
        ]
    )

    # John Doe's family members
    members.extend(
        [
            FamilyMember(
                name="Jane Doe",
                member_type=MemberType.HUMAN,
                relation_type="Mother",
                date_of_birth=datetime(1985, 7, 20),
                health_score=90,
                notes="Works as a teacher",
                manager_id=users[1].id,
            ),
            FamilyMember(
                name="Luna",
                member_type=MemberType.PET,
                relation_type="Cat",
                date_of_birth=datetime(2021, 2, 28),
                health_score=95,
                notes="Persian cat",
                manager_id=users[1].id,
            ),
        ]
    )

    # Jane Smith's family members
    members.extend(
        [
            FamilyMember(
                name="Mike Johnson",
                member_type=MemberType.HUMAN,
                relation_type="Father",
                date_of_birth=datetime(1978, 11, 5),
                health_score=87,
                notes="Retired military",
                manager_id=users[2].id,
            ),
            FamilyMember(
                name="Emma Johnson",
                member_type=MemberType.HUMAN,
                relation_type="Daughter",
                date_of_birth=datetime(2010, 4, 12),
                health_score=98,
                notes="Loves soccer",
                manager_id=users[2].id,
            ),
        ]
    )

    for member in members:
        db.add(member)
    db.commit()
    return members


def seed_database(db: Session):
    """Seed the database with fake data"""
    print("Creating fake users...")
    users = create_fake_users(db)

    print("Creating fake family members...")
    members = create_fake_family_members(db, users)

    print("Database seeding completed successfully!")
