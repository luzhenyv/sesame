Here's a summary of the v1 API endpoints:

1. Authentication Endpoints (`/v1/auth`):
   - `POST /v1/auth/register` - Register a new user
   - `POST /v1/auth/token` - Login to get access token
   - `POST /v1/auth/logout` - Logout the current user

2. Family Member Endpoints (`/v1/family-members`):
   - `POST /v1/family-members/` - Create a new family member
   - `GET /v1/family-members/` - List all family members for the current user
   - `GET /v1/family-members/{family_member_id}` - Get a specific family member
   - `PUT /v1/family-members/{family_member_id}` - Update a family member
   - `DELETE /v1/family-members/{family_member_id}` - Delete a family member

3. Health Events Endpoints (`/v1/health-events`):
   - `POST /v1/health-events/` - Create a new health event
   - `GET /v1/health-events/` - List health events with filtering
   - `GET /v1/health-events/{event_id}` - Get a specific health event
   - `PUT /v1/health-events/{event_id}` - Update a health event
   - `DELETE /v1/health-events/{event_id}` - Delete a health event

4. Files Endpoints (`/v1/files`):
   - `POST /v1/files/upload` - Upload a file
   - `GET /v1/files/{file_id}` - Get a specific file
   - `DELETE /v1/files/{file_id}` - Delete a file

Key features implemented:
1. JWT-based authentication with token expiration
2. Password hashing using bcrypt
3. Role-based access control (only the manager can access their family members' data)
4. Pagination for list endpoints
5. Proper error handling and validation
6. File upload support for health events

To use these endpoints:

1. First, register a new user:
```http
POST /v1/auth/register
{
    "email": "user@example.com",
    "password": "securepassword",
    "full_name": "John Doe"
}
```

2. Login to get an access token:
```http
POST /v1/auth/token
Form data:
username=user@example.com
password=securepassword
```

3. Use the access token in subsequent requests:
```http
Authorization: Bearer <access_token>
```

4. Create a family member:
```http
POST /v1/family-members/
{
    "name": "Jane Doe",
    "relationship": "child",
    "date_of_birth": "2020-01-01",
    "gender": "female"
}
```

5. Create health events for family members:
```http
POST /v1/health-events/
Form data:
title=Checkup
event_type=CHECKUP
description=Regular checkup
family_member_id=<family_member_id>
date_time=2024-03-28T10:00:00
```

6. Upload a file:
```http
POST /v1/files/upload
Form data:
file=<file>
```

All endpoints are protected except for registration and login. The system ensures that users can only access and modify their own family members' data and health events.
