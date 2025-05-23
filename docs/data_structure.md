# System Data Structure

## Overview
This document describes the core data structure of the Sesame Health Management System. The system is designed to help family health managers track and manage health events for their family members, including both humans and pets.

## Core Models

### User
The primary user who manages family health information.
- `id`: UUID (Primary Key, auto-generated)
- `email`: String(255) (Unique, Indexed)
- `hashed_password`: String(255)
- `full_name`: String(255)
- `is_active`: Boolean (Default: True)
- `created_at`: DateTime (UTC, auto-generated)
- `updated_at`: DateTime (UTC, auto-updated)

### FamilyMember
Represents a family member (human or pet) whose health is being tracked.
- `id`: UUID (Primary Key, auto-generated)
- `name`: String(255)
- `member_type`: Enum (HUMAN/PET)
- `relation_type`: String(50)
- `date_of_birth`: DateTime (Optional)
- `health_score`: Integer (Optional)
- `notes`: Text (Optional)
- `created_at`: DateTime (UTC, auto-generated)
- `updated_at`: DateTime (UTC, auto-updated)
- `manager_id`: UUID (Foreign Key to User)

### HealthEvent
Represents a health-related event for a family member.
- `id`: UUID (Primary Key, auto-generated)
- `title`: String(255)
- `event_type`: String(255) (Enum: CHECKUP/MEDICATION/SYMPTOM)
- `description`: Text (Optional)
- `date_time`: DateTime
- `family_member_id`: UUID (Foreign Key to FamilyMember)
- `created_by_id`: UUID (Foreign Key to User)
- `created_at`: DateTime (UTC, auto-generated)
- `updated_at`: DateTime (UTC, auto-updated)
- `file_paths`: String[] (Optional)
- `file_types`: String[] (Optional)

## Model Relationships

```mermaid
erDiagram
    User ||--o{ FamilyMember : manages
    User ||--o{ HealthEvent : creates
    FamilyMember ||--o{ HealthEvent : has

    User {
        UUID id PK
        string email UK
        string hashed_password
        string full_name
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    FamilyMember {
        UUID id PK
        string name
        enum member_type
        string relation_type
        datetime date_of_birth
        integer health_score
        text notes
        datetime created_at
        datetime updated_at
        UUID manager_id FK
    }

    HealthEvent {
        UUID id PK
        string title
        string event_type
        text description
        datetime date_time
        UUID family_member_id FK
        UUID created_by_id FK
        datetime created_at
        datetime updated_at
        string[] file_paths
        string[] file_types
    }
```

## Relationships Explained

1. User to FamilyMember:
   - One-to-Many relationship
   - A user can manage multiple family members
   - Each family member belongs to one user (manager)
   - Relationship is lazy-loaded with selectin strategy
   - Implemented using SQLAlchemy's relationship with back_populates

2. User to HealthEvent:
   - One-to-Many relationship
   - A user can create multiple health events
   - Each health event is created by one user
   - Relationship is implemented using backref
   - Allows easy access to created events from user object

3. FamilyMember to HealthEvent:
   - One-to-Many relationship
   - A family member can have multiple health events
   - Each health event belongs to one family member
   - Relationship is lazy-loaded with selectin strategy
   - Implemented using SQLAlchemy's relationship with back_populates

## Technical Details

1. All timestamps are stored in UTC
2. UUIDs are used for all primary and foreign keys
3. String fields have specific length constraints
4. Relationships use SQLAlchemy's modern typing system with Mapped types
5. File attachments are stored as arrays of strings for paths and types

## Future Extensibility

The current data structure is designed to be extensible for future features:

1. Community Doctor Support:
   - Can add DoctorPatient relationship table
   - Can extend User model with doctor-specific fields
   - Can add doctor-related fields to HealthEvent

2. Patient Self-Service:
   - Can extend User model with patient-specific fields
   - Can add patient authentication and authorization
   - Can add patient-specific health event creation

3. Additional Features:
   - Can add more event types
   - Can extend file attachment support
   - Can add more health metrics and tracking