# Authentication & Authorization API Documentation

## Overview
This document provides comprehensive API documentation for the authentication system, role-based permissions, audit logging, and messaging features.

## Authentication Endpoints

### 1. User Registration
**Endpoint:** `POST /api/auth/register/`

**Request Body:**
```json
{
    "username": "johndoe",
    "email": "john.doe@example.com",
    "password": "securepassword123",
    "first_name": "John",
    "last_name": "Doe",
    "role": "doctor"
}
```

**Response:**
```json
{
    "message": "User registered successfully"
}
```

**Available Roles:**
- `admin`: Full system access
- `doctor`: Medical professional access
- `lab`: Lab technician access
- `viewer`: Read-only access

### 2. User Login
**Endpoint:** `POST /api/auth/login/`

**Request Body:**
```json
{
    "email": "john.doe@example.com",
    "password": "securepassword123"
}
```

**Response:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "username": "johndoe",
        "email": "john.doe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "doctor"
    }
}
```

### 3. User Logout
**Endpoint:** `POST /api/auth/logout/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
    "message": "Successfully logged out"
}
```

## User Management

### 4. List Users
**Endpoint:** `GET /api/users/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Permissions:** Admin only

**Response:**
```json
[
    {
        "id": 1,
        "username": "johndoe",
        "email": "john.doe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "doctor"
    }
]
```

### 5. Get User Details
**Endpoint:** `GET /api/users/{id}/`

**Permissions:** Admin only

### 6. Update User
**Endpoint:** `PUT /api/users/{id}/`

**Permissions:** Admin only

### 7. Delete User
**Endpoint:** `DELETE /api/users/{id}/`

**Permissions:** Admin only

## Messaging System

### 8. Send Message
**Endpoint:** `POST /api/messaging/messages/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "recipient": 2,
    "subject": "Data Analysis Request",
    "content": "Please analyze the latest antibiogram data."
}
```

**Response:**
```json
{
    "id": 1,
    "sender": 1,
    "sender_username": "johndoe",
    "recipient": 2,
    "recipient_username": "admin",
    "subject": "Data Analysis Request",
    "content": "Please analyze the latest antibiogram data.",
    "timestamp": "2024-01-15T10:30:00Z",
    "read_status": false
}
```

### 9. List Messages
**Endpoint:** `GET /api/messaging/messages/`

**Response:**
```json
[
    {
        "id": 1,
        "sender": 1,
        "sender_username": "johndoe",
        "recipient": 2,
        "recipient_username": "admin",
        "subject": "Data Analysis Request",
        "content": "Please analyze the latest antibiogram data.",
        "timestamp": "2024-01-15T10:30:00Z",
        "read_status": false
    }
]
```

### 10. Get Sent Messages
**Endpoint:** `GET /api/messaging/messages/sent/`

### 11. Get Received Messages
**Endpoint:** `GET /api/messaging/messages/received/`

### 12. Get Unread Messages
**Endpoint:** `GET /api/messaging/messages/unread/`

### 13. Mark Message as Read
**Endpoint:** `POST /api/messaging/messages/{id}/mark_read/`

**Response:**
```json
{
    "status": "message marked as read"
}
```

## Role-Based Permissions

### Admin Permissions
- ✅ Full system access
- ✅ Create/edit/delete users
- ✅ Upload/modify/delete all data
- ✅ Generate all reports
- ✅ Use all AI features
- ✅ Send messages to all users
- ✅ Approve/reject uploads

### Doctor Permissions
- ✅ Login and access dashboard
- ✅ View analytics and graphs
- ✅ Use filters for data analysis
- ✅ Generate and download reports
- ✅ Use AI antibiotic recommendations
- ✅ Send messages to admin
- ❌ Cannot modify raw data
- ❌ Cannot delete reports

### Lab Permissions
- ✅ Login to system
- ✅ Upload data files
- ✅ View uploaded data after approval
- ✅ Limited AI access
- ✅ Send messages to admin
- ❌ Cannot modify old results
- ❌ Cannot create official reports

### Viewer Permissions
- ✅ Login to system
- ✅ View dashboard and graphs
- ❌ Cannot upload data
- ❌ Cannot modify data
- ❌ Cannot create reports
- ❌ Cannot use AI features

## Audit Logging

### Audit Log Types

1. **Login Logs** - Track user login events
2. **Logout Logs** - Track user logout events
3. **Upload Logs** - Track file upload activities
4. **Modification Logs** - Track data changes
5. **Report Logs** - Track report generation
6. **AI Usage Logs** - Track AI feature usage

### Viewing Audit Logs
Audit logs are accessible through the Django admin interface at `/admin/`.

## Data Upload Workflow

### Upload Process
1. **Lab User** uploads file → Status: `pending`
2. **Admin** reviews upload
3. **Admin** approves/rejects → Status: `approved`/`rejected`
4. **Approved uploads** become available for analysis

### Upload Permissions
- **Lab**: Can upload files, cannot modify/delete after upload
- **Admin**: Can approve/reject uploads, can modify/delete all
- **Doctor**: Cannot upload files
- **Viewer**: Cannot upload files

## Error Responses

### Authentication Errors
```json
{
    "error": "Invalid credentials"
}
```

### Permission Errors
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### Validation Errors
```json
{
    "email": ["This field is required."],
    "password": ["This field may not be blank."]
}
```

## Testing Examples

### Python Test Script
```python
import requests

BASE_URL = "http://localhost:8000/api"

# Register a user
user_data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "role": "doctor"
}
response = requests.post(f"{BASE_URL}/auth/register/", json=user_data)

# Login
login_data = {"email": "test@example.com", "password": "testpass123"}
response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
token = response.json()["access"]

# Use authenticated endpoint
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/analytics/", headers=headers)
```

### cURL Examples
```bash
# Register user
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass123","role":"doctor"}'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# Get users (admin only)
curl -X GET http://localhost:8000/api/users/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Encryption**: Django's built-in password hashing
- **Role-Based Access Control**: Granular permissions per user role
- **Audit Logging**: Complete tracking of all user activities
- **IP Tracking**: Login/logout events include IP addresses
- **Session Management**: Secure session handling with logout capability

## Best Practices

1. **Always use HTTPS** in production
2. **Implement rate limiting** for authentication endpoints
3. **Regularly review audit logs** for security monitoring
4. **Use strong passwords** and implement password policies
5. **Keep user sessions short** for sensitive applications
6. **Regularly backup audit logs** for compliance

## Support

For API support or issues, please refer to the Django admin interface or contact the system administrator.
