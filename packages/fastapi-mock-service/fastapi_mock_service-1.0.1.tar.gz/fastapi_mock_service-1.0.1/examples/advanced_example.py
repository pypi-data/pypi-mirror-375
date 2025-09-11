#!/usr/bin/env python3
"""
Advanced FastAPI Mock Service Example

Demonstrates:
- Custom error codes and messages
- Advanced response formats  
- Validation error handlers
- Real-world API scenarios
- Load testing integration
"""

from fastapi_mock_service import MockService
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import random

# Create mock service
mock = MockService()

# Define custom error codes
API_ERRORS = {
    "validation": {"code": "API.01000", "message": "Request validation failed"},
    "not_found": {"code": "API.01001", "message": "Resource not found"},
    "unauthorized": {"code": "API.01002", "message": "Unauthorized access"},
    "forbidden": {"code": "API.01003", "message": "Access forbidden"},
    "server_error": {"code": "API.01004", "message": "Internal server error"},
    "timeout": {"code": "API.01005", "message": "Request timeout"},
    "rate_limit": {"code": "API.01006", "message": "Rate limit exceeded"},
    "conflict": {"code": "API.01007", "message": "Resource conflict"},
}


# Define response models
class StandardResult(BaseModel):
    timestamp: str
    status: int
    code: str
    message: str
    request_id: Optional[str] = None


class User(BaseModel):
    id: int
    name: str
    email: str
    active: bool = True
    created_at: str
    updated_at: str
    profile: Optional[Dict[str, Any]] = None


class UserResponse(BaseModel):
    result: StandardResult
    data: Optional[User] = None


class UserListResponse(BaseModel):
    result: StandardResult
    data: List[User] = []
    pagination: Optional[Dict[str, Any]] = None


class CreateUserRequest(BaseModel):
    name: str
    email: str
    active: bool = True
    profile: Optional[Dict[str, Any]] = None


def create_responses_from_errors(error_dict: Dict, success_code: str, success_message: str = "OK") -> List[Dict]:
    """
    Dynamically create response list from error dictionary
    This function demonstrates how to avoid hardcoding response codes in the library
    """
    responses = [
        {"code": success_code, "description": f"{success_message} - Successful response"}
    ]

    for error_key, error_info in error_dict.items():
        responses.append({
            "code": error_info["code"],
            "description": error_info["message"]
        })

    return responses


def create_validation_error(error_code: str, response_class):
    """
    Create validation error handler for missing parameters
    This demonstrates custom validation logic
    """

    def handler(missing_params, endpoint_path, service_name):
        result = StandardResult(
            timestamp=datetime.now(timezone.utc).isoformat(),
            status=200,  # Always HTTP 200, error is in result.code
            code=error_code,
            message=f"Missing required parameters: {', '.join(missing_params)}",
            request_id=f"req_{random.randint(100000, 999999)}"
        )

        if hasattr(response_class, '__annotations__') and 'data' in response_class.__annotations__:
            # Handle different response types
            if 'List' in str(response_class.__annotations__['data']):
                return response_class(result=result, data=[])
            else:
                return response_class(result=result, data=None)

        return {"result": result.dict(), "data": None}

    return handler


def make_result(success: bool = True, error_key: Optional[str] = None,
                custom_message: Optional[str] = None) -> StandardResult:
    """
    Create standard result object
    This demonstrates centralized result creation
    """
    dt = datetime.now(timezone.utc).isoformat()
    request_id = f"req_{random.randint(100000, 999999)}"

    if success:
        return StandardResult(
            timestamp=dt,
            status=200,
            code="API.00000",
            message="Operation successful",
            request_id=request_id
        )
    else:
        error_info = API_ERRORS.get(error_key, API_ERRORS["server_error"])
        return StandardResult(
            timestamp=dt,
            status=200,  # Always HTTP 200
            code=error_info["code"],
            message=custom_message or error_info["message"],
            request_id=request_id
        )


# Create possible responses list (for UI dashboard)
API_RESPONSES = create_responses_from_errors(API_ERRORS, "API.00000")

# Create validation handlers for different response types  
user_validation_handler = create_validation_error("API.01000", UserResponse)
user_list_validation_handler = create_validation_error("API.01000", UserListResponse)


# Advanced endpoints with comprehensive error handling
@mock.get("/api/v1/users/{user_id}",
          responses=API_RESPONSES,
          tags=["users"],
          validation_error_handler=user_validation_handler)
def get_user(user_id: int, include_profile: bool = False):
    """
    Get user by ID with advanced error handling
    
    Demonstrates:
    - Parameter validation
    - Different error scenarios
    - Conditional response data
    """

    # Validation scenarios
    if user_id <= 0:
        return UserResponse(
            result=make_result(False, "validation", "User ID must be positive"),
            data=None
        )

    if user_id > 1000:
        return UserResponse(
            result=make_result(False, "not_found", f"User {user_id} not found"),
            data=None
        )

    # Simulate server error for specific ID
    if user_id == 500:
        return UserResponse(
            result=make_result(False, "server_error", "Database connection failed"),
            data=None
        )

    # Simulate timeout for specific ID
    if user_id == 503:
        return UserResponse(
            result=make_result(False, "timeout", "Service timeout after 30 seconds"),
            data=None
        )

    # Success response
    now = datetime.now().isoformat()

    user_data = {
        "id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com",
        "active": user_id % 2 == 1,  # Odd IDs are active
        "created_at": now,
        "updated_at": now
    }

    # Conditionally include profile data
    if include_profile:
        user_data["profile"] = {
            "bio": f"Biography for user {user_id}",
            "avatar_url": f"https://api.example.com/avatars/{user_id}.jpg",
            "settings": {
                "theme": "dark" if user_id % 3 == 0 else "light",
                "notifications": user_id % 4 != 0
            }
        }

    user = User(**user_data)

    return UserResponse(
        result=make_result(True),
        data=user
    )


@mock.get("/api/v1/users",
          responses=API_RESPONSES,
          tags=["users"],
          validation_error_handler=user_list_validation_handler)
def get_users(limit: int = 10, offset: int = 0, active: Optional[bool] = None, search: Optional[str] = None):
    """
    Get paginated list of users with filtering
    
    Demonstrates:
    - Query parameter validation
    - Pagination logic
    - Filtering capabilities
    """

    # Validation
    if limit <= 0 or limit > 100:
        return UserListResponse(
            result=make_result(False, "validation", "Limit must be between 1 and 100"),
            data=[]
        )

    if offset < 0:
        return UserListResponse(
            result=make_result(False, "validation", "Offset must be non-negative"),
            data=[]
        )

    # Simulate rate limiting
    if limit > 50:
        return UserListResponse(
            result=make_result(False, "rate_limit", "Too many items requested. Max 50 per request."),
            data=[]
        )

    # Generate users based on parameters
    users = []
    now = datetime.now().isoformat()

    for i in range(offset + 1, offset + limit + 1):
        user_active = i % 2 == 1
        user_name = f"User {i}"

        # Apply filters
        if active is not None and active != user_active:
            continue

        if search and search.lower() not in user_name.lower():
            continue

        users.append(User(
            id=i,
            name=user_name,
            email=f"user{i}@example.com",
            active=user_active,
            created_at=now,
            updated_at=now
        ))

    # Pagination info
    pagination = {
        "offset": offset,
        "limit": limit,
        "total": len(users),
        "has_more": len(users) == limit  # Simplified logic
    }

    return UserListResponse(
        result=make_result(True),
        data=users,
        pagination=pagination
    )


@mock.post("/api/v1/users",
           responses=API_RESPONSES,
           tags=["users"],
           validation_error_handler=user_validation_handler)
def create_user(user_data: CreateUserRequest):
    """
    Create new user with validation
    
    Demonstrates:
    - Request body validation
    - Business logic validation
    - Conflict handling
    """

    # Business logic validation
    if not user_data.name.strip():
        return UserResponse(
            result=make_result(False, "validation", "Name cannot be empty"),
            data=None
        )

    if "@" not in user_data.email or "." not in user_data.email:
        return UserResponse(
            result=make_result(False, "validation", "Invalid email format"),
            data=None
        )

    # Simulate email conflict
    if "admin" in user_data.email.lower():
        return UserResponse(
            result=make_result(False, "conflict", "Email already exists"),
            data=None
        )

    # Simulate forbidden operation
    if "test" in user_data.name.lower():
        return UserResponse(
            result=make_result(False, "forbidden", "Test users cannot be created via API"),
            data=None
        )

    # Success - create user
    now = datetime.now().isoformat()
    new_user = User(
        id=random.randint(1001, 9999),  # Mock ID
        name=user_data.name,
        email=user_data.email,
        active=user_data.active,
        created_at=now,
        updated_at=now,
        profile=user_data.profile
    )

    return UserResponse(
        result=make_result(True),
        data=new_user
    )


@mock.delete("/api/v1/users/{user_id}",
             responses=API_RESPONSES,
             tags=["users"],
             validation_error_handler=user_validation_handler)
def delete_user(user_id: int, force: bool = False):
    """
    Delete user with protection logic
    
    Demonstrates:
    - Authorization simulation
    - Conditional deletion
    - Safety checks
    """

    # Validation
    if user_id <= 0:
        return UserResponse(
            result=make_result(False, "validation", "Invalid user ID"),
            data=None
        )

    # Simulate protected users
    if user_id <= 10 and not force:
        return UserResponse(
            result=make_result(False, "forbidden", "Cannot delete system user without force flag"),
            data=None
        )

    # Simulate not found
    if user_id > 1000:
        return UserResponse(
            result=make_result(False, "not_found", f"User {user_id} not found"),
            data=None
        )

    # Success
    return UserResponse(
        result=make_result(True),
        data=None
    )


# Health and status endpoints
@mock.get("/health", tags=["system"])
def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "service": "Advanced User API Mock",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@mock.get("/api/v1/status", responses=API_RESPONSES, tags=["system"])
def service_status():
    """Detailed service status"""
    return {
        "result": make_result(True).dict(),
        "data": {
            "service": "Advanced User API",
            "version": "1.0.0",
            "environment": "mock",
            "features": [
                "user_management",
                "validation",
                "error_handling",
                "pagination",
                "filtering"
            ],
            "uptime": "100%",
            "database": "connected"
        }
    }


if __name__ == "__main__":
    print("🚀 Starting Advanced Mock Service...")
    print("📊 Dashboard: http://localhost:8000")
    print("📈 Metrics: http://localhost:8000/metrics")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\n✨ Advanced features:")
    print("  ✓ Custom error codes and messages")
    print("  ✓ Advanced parameter validation")
    print("  ✓ Business logic simulation")
    print("  ✓ Realistic error scenarios")
    print("  ✓ Load testing integration")
    print("\n🎯 Test scenarios:")
    print("  • GET /api/v1/users/500 → Server error")
    print("  • GET /api/v1/users/503 → Timeout error")
    print("  • GET /api/v1/users/1001 → Not found")
    print("  • POST /api/v1/users (name='test') → Forbidden")
    print("  • POST /api/v1/users (email='admin@...') → Conflict")

    mock.run()
