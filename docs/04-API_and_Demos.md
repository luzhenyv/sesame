# API and Demos

This document provides comprehensive API documentation and demo guidelines for the User Health Data Management Platform.

## API Overview

The platform exposes a RESTful API that follows standard HTTP methods and status codes. All API endpoints are prefixed with `/api/v1`.

### Authentication

- API authentication uses JWT tokens
- Tokens are obtained via the `/api/v1/auth/login` endpoint
- Include the token in the `Authorization` header as `Bearer {token}`
- Tokens expire after 24 hours

### API Versioning

- Current API version: v1
- Versions are included in the URL path: `/api/v1/...`
- Deprecated endpoints will be maintained for at least 6 months

### Rate Limiting

- 100 requests per minute per API key
- 429 Too Many Requests response when limit is exceeded
- `X-RateLimit-Remaining` header shows remaining requests

## Core API Endpoints

### User Management

#### User Registration

```
POST /api/v1/users/register
```

Creates a new user account with a randomly generated ID.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "age": 35,
  "gender": "female"
}
```

**Response:**
```json
{
  "user_id": "usr_7f4b2c1a9e8d",
  "email": "user@example.com",
  "created_at": "2023-03-15T10:30:45Z"
}
```

**Status Codes:**
- 201: User created successfully
- 400: Invalid request body
- 409: Email already exists

#### User Authentication

```
POST /api/v1/auth/login
```

Authenticates a user and returns a JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Status Codes:**
- 200: Successful authentication
- 401: Invalid credentials

### Health Records

#### Upload Health Report

```
POST /api/v1/health/reports
```

Uploads a health examination report for OCR processing.

**Request Body:**
```
Content-Type: multipart/form-data

file: [PDF or image file]
report_type: "blood_test"
report_date: "2023-02-15"
```

**Response:**
```json
{
  "report_id": "rep_3e5f2a1b8c7d",
  "file_name": "blood_test_2023-02-15.pdf",
  "processing_status": "pending",
  "upload_date": "2023-03-16T14:25:10Z"
}
```

**Status Codes:**
- 202: Report accepted for processing
- 400: Invalid request
- 413: File too large (max 10MB)

#### Retrieve Health Reports

```
GET /api/v1/health/reports
```

Retrieves a list of user's health reports.

**Query Parameters:**
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20)
- `report_type`: Filter by report type
- `start_date`: Filter by date range start
- `end_date`: Filter by date range end

**Response:**
```json
{
  "total": 42,
  "page": 1,
  "per_page": 20,
  "reports": [
    {
      "report_id": "rep_3e5f2a1b8c7d",
      "report_type": "blood_test",
      "report_date": "2023-02-15",
      "processing_status": "completed",
      "upload_date": "2023-03-16T14:25:10Z"
    },
    // More reports...
  ]
}
```

**Status Codes:**
- 200: Successful retrieval
- 401: Unauthorized

#### Get Report Details

```
GET /api/v1/health/reports/{report_id}
```

Retrieves detailed information from a processed health report.

**Response:**
```json
{
  "report_id": "rep_3e5f2a1b8c7d",
  "report_type": "blood_test",
  "report_date": "2023-02-15",
  "processing_status": "completed",
  "upload_date": "2023-03-16T14:25:10Z",
  "extracted_data": {
    "hemoglobin": {
      "value": 14.2,
      "unit": "g/dL",
      "reference_range": "12.0-16.0",
      "status": "normal"
    },
    "white_blood_cells": {
      "value": 7.5,
      "unit": "K/uL",
      "reference_range": "4.5-11.0",
      "status": "normal"
    },
    // More test results...
  }
}
```

**Status Codes:**
- 200: Successful retrieval
- 401: Unauthorized
- 404: Report not found

### Health Logs

#### Create Health Log

```
POST /api/v1/health/logs
```

Creates a new health log entry.

**Request Body:**
```json
{
  "log_type": "blood_pressure",
  "log_date": "2023-03-17T08:30:00Z",
  "values": {
    "systolic": 120,
    "diastolic": 80,
    "pulse": 72
  },
  "notes": "Morning reading before breakfast"
}
```

**Response:**
```json
{
  "log_id": "log_2d9e7f3b5a6c",
  "log_type": "blood_pressure",
  "log_date": "2023-03-17T08:30:00Z",
  "created_at": "2023-03-17T08:32:15Z"
}
```

**Status Codes:**
- 201: Log created successfully
- 400: Invalid request body
- 401: Unauthorized

### Family Management

#### Add Family Member

```
POST /api/v1/family/members
```

Adds a new family member.

**Request Body:**
```json
{
  "name": "John Smith",
  "relationship": "father",
  "age": 65,
  "email": "john@example.com"  // Optional
}
```

**Response:**
```json
{
  "member_id": "mem_8c5d2e1f9a3b",
  "name": "John Smith",
  "relationship": "father",
  "created_at": "2023-03-18T09:45:20Z"
}
```

**Status Codes:**
- 201: Member added successfully
- 400: Invalid request body

### Health Assessments

#### Get Available Assessments

```
GET /api/v1/assessments
```

Retrieves available health assessment surveys.

**Response:**
```json
{
  "assessments": [
    {
      "assessment_id": "ast_1a2b3c4d5e6f",
      "title": "Heart Health Risk Assessment",
      "description": "Evaluates your cardiovascular health risk factors",
      "estimated_time": 5,  // minutes
      "question_count": 12
    },
    // More assessments...
  ]
}
```

**Status Codes:**
- 200: Successful retrieval

#### Start Assessment

```
POST /api/v1/assessments/{assessment_id}/start
```

Starts a new assessment session.

**Response:**
```json
{
  "session_id": "ses_5e4d3c2b1a9f",
  "assessment_id": "ast_1a2b3c4d5e6f",
  "expires_at": "2023-03-19T11:30:00Z",  // 1 hour from now
  "first_question": {
    "question_id": "q1",
    "text": "Do you smoke?",
    "type": "single_choice",
    "options": [
      {"id": "q1a", "text": "Yes, regularly"},
      {"id": "q1b", "text": "Occasionally"},
      {"id": "q1c", "text": "No, never"}
    ]
  }
}
```

**Status Codes:**
- 200: Assessment started successfully
- 404: Assessment not found

#### Submit Assessment Answer

```
POST /api/v1/assessments/sessions/{session_id}/answers
```

Submits an answer and retrieves the next question.

**Request Body:**
```json
{
  "question_id": "q1",
  "answer": "q1c"
}
```

**Response:**
```json
{
  "next_question": {
    "question_id": "q2",
    "text": "Do you have a family history of heart disease?",
    "type": "single_choice",
    "options": [
      {"id": "q2a", "text": "Yes, immediate family"},
      {"id": "q2b", "text": "Yes, extended family"},
      {"id": "q2c", "text": "No, none that I'm aware of"}
    ]
  },
  "progress": {
    "completed": 1,
    "total": 12,
    "percentage": 8
  }
}
```

**Status Codes:**
- 200: Answer accepted, next question provided
- 201: Assessment completed (final answer)
- 400: Invalid answer
- 404: Session not found or expired

#### Get Assessment Results

```
GET /api/v1/assessments/sessions/{session_id}/results
```

Retrieves the results of a completed assessment.

**Response:**
```json
{
  "assessment_id": "ast_1a2b3c4d5e6f",
  "completed_at": "2023-03-19T11:15:30Z",
  "score": 78,
  "risk_level": "moderate",
  "summary": "Your heart health assessment indicates a moderate risk level...",
  "recommendations": [
    "Consider regular cardiovascular exercise",
    "Maintain a healthy diet low in saturated fats",
    "Schedule a follow-up with your physician"
  ],
  "detailed_factors": [
    {
      "factor": "Smoking Status",
      "value": "Non-smoker",
      "impact": "positive"
    },
    // More factors...
  ]
}
```

**Status Codes:**
- 200: Results retrieved successfully
- 400: Assessment not completed
- 404: Session not found

## Demo Scenarios

### Demo 1: Personal Health Record Management

This demo showcases the core functionality of uploading and managing health records.

**Steps:**

1. **Register a New User**
   - Use the registration API endpoint
   - Demonstrate the random ID generation
   - Show how minimal personal data is collected

2. **Upload Health Reports**
   - Upload a sample blood test report PDF
   - Show the OCR processing in action
   - Demonstrate data extraction accuracy

3. **View Health Dashboard**
   - Display the aggregated health data
   - Show visualizations of key health indicators
   - Demonstrate timeline view of historical data

4. **Create Health Logs**
   - Add manual health log entries
   - Show voice input functionality
   - Demonstrate how logs integrate with report data

### Demo 2: Family Health Management

This demo focuses on managing health data across a family unit.

**Steps:**

1. **Create Family Members**
   - Add multiple family members with relationships
   - Demonstrate permission settings

2. **Upload Health Data for Family**
   - Process medical reports for different family members
   - Show how data is organized by family member

3. **Family Health Overview**
   - Demonstrate the family mode dashboard
   - Show health trends across family members
   - Highlight relationship-based insights

### Demo 3: Health Assessment and Recommendations

This demo showcases the assessment and recommendation capabilities.

**Steps:**

1. **Browse Available Assessments**
   - Show the variety of health assessments
   - Explain the purpose and methodology

2. **Complete a Health Risk Assessment**
   - Walk through the assessment flow
   - Demonstrate dynamic questioning logic

3. **Review Assessment Results**
   - Show the generated risk score and explanation
   - Present personalized recommendations
   - Demonstrate how results integrate with existing health data

4. **Schedule Follow-ups**
   - Set reminders for recommended actions
   - Show integration with calendar

## API Testing Tools

- **Swagger UI**: Available at `http://localhost:5000/docs` in development mode
- **Postman Collection**: Available in the repository at `/docs/assets/health-platform-api.postman_collection.json`
- **Authentication Token**: For testing, use `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0X3VzZXIifQ.1234567890`

## Demo Data

For demonstration purposes, the following test accounts and sample data are available:

- **Test User**: Email: `demo@healthplatform.com`, Password: `demo1234`
- **Sample Reports**: Available in `/docs/assets/sample_reports/`
- **Sample Voice Logs**: Available in `/docs/assets/sample_voice_logs/`

## Integration Instructions

To integrate with the platform API in your application:

1. Register for an API key in the developer portal
2. Set up authentication using JWT
3. Follow rate limiting guidelines
4. Handle error responses appropriately
5. Use webhook endpoints for long-running processes 