from datetime import datetime, timedelta
import random
from typing import List
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.family_member import FamilyMember, MemberType
from app.models.health_event import HealthEvent
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


def create_fake_health_events(
    db: Session, members: List[FamilyMember], users: List[User]
) -> List[HealthEvent]:
    events = []

    for member in members:
        # Find the corresponding user (manager) for this member
        manager = next(user for user in users if user.id == member.manager_id)

        # Create 2-3 events for each member
        num_events = random.randint(2, 3)

        for _ in range(num_events):
            # Randomly select event type
            event_type = random.choice(["CHECKUP", "MEDICATION", "SYMPTOM"])

            # Generate random date within last 6 months
            days_ago = random.randint(0, 180)
            event_date = datetime.utcnow() - timedelta(days=days_ago)

            # Create event with appropriate details based on type
            if event_type == "CHECKUP":
                title = f"Regular Health Checkup"
                description = f"Routine health checkup for {member.name}"
            elif event_type == "MEDICATION":
                title = f"Medication Update"
                description = f"Updated medication schedule for {member.name}"
            else:  # SYMPTOM
                title = f"Health Symptom Report"
                description = f"Reported health symptoms for {member.name}"

            event = HealthEvent(
                title=title,
                event_type=event_type,
                description=description,
                date_time=event_date,
                family_member_id=member.id,
                created_by_id=manager.id,
                file_paths=[],
                file_types=[],
            )
            events.append(event)

    for event in events:
        db.add(event)
    db.commit()
    return events


def seed_database(db: Session, if_append: bool = False):
    """Seed the database with fake data"""
    if not if_append:
        print("Clearing existing data...")
        # Delete in correct order to respect foreign key constraints
        db.query(HealthEvent).delete()
        db.query(FamilyMember).delete()
        db.query(User).delete()
        db.commit()

    print("Creating fake users...")
    users = create_fake_users(db)

    print("Creating fake family members...")
    members = create_fake_family_members(db, users)

    print("Creating fake health events...")
    events = create_fake_health_events(db, members, users)

    print("Database seeding completed successfully!")
