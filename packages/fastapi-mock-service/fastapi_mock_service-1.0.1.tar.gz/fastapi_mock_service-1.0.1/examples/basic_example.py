#!/usr/bin/env python3
"""
Basic FastAPI Mock Service Example

Simple REST API mock with standard HTTP responses.
Perfect for basic API development and testing.
"""

from fastapi_mock_service import MockService
from pydantic import BaseModel
from typing import List, Optional

# Create mock service
mock = MockService()


# Define data models
class User(BaseModel):
    id: int
    name: str
    email: str
    active: bool = True


class UserListResponse(BaseModel):
    users: List[User]
    total: int
    page: int = 1
    limit: int = 10


class CreateUserRequest(BaseModel):
    name: str
    email: str
    active: bool = True


# Simple GET endpoint
@mock.get("/api/users/{user_id}")
def get_user(user_id: int):
    """Get user by ID"""
    return User(
        id=user_id,
        name=f"User {user_id}",
        email=f"user{user_id}@example.com",
        active=user_id % 2 == 1  # Odd IDs are active
    )


# GET endpoint with query parameters
@mock.get("/api/users")
def get_users(limit: int = 10, page: int = 1, active: Optional[bool] = None):
    """Get paginated list of users"""

    # Calculate offset
    offset = (page - 1) * limit

    # Generate users based on filters
    users = []
    for i in range(offset + 1, offset + limit + 1):
        user_active = i % 2 == 1

        # Apply active filter if provided
        if active is None or active == user_active:
            users.append(User(
                id=i,
                name=f"User {i}",
                email=f"user{i}@example.com",
                active=user_active
            ))

    return UserListResponse(
        users=users,
        total=len(users),
        page=page,
        limit=limit
    )


# POST endpoint
@mock.post("/api/users")
def create_user(user_data: CreateUserRequest):
    """Create new user"""

    # Simulate user creation
    new_user = User(
        id=999,  # Mock ID
        name=user_data.name,
        email=user_data.email,
        active=user_data.active
    )

    return {
        "message": "User created successfully",
        "user": new_user
    }


# PUT endpoint
@mock.put("/api/users/{user_id}")
def update_user(user_id: int, user_data: CreateUserRequest):
    """Update existing user"""

    updated_user = User(
        id=user_id,
        name=user_data.name,
        email=user_data.email,
        active=user_data.active
    )

    return {
        "message": "User updated successfully",
        "user": updated_user
    }


# DELETE endpoint
@mock.delete("/api/users/{user_id}")
def delete_user(user_id: int):
    """Delete user"""
    return {
        "message": f"User {user_id} deleted successfully"
    }


# Health check endpoint
@mock.get("/health")
def health_check():
    """Service health check"""
    return {
        "status": "healthy",
        "service": "User API Mock",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    print("🚀 Starting Basic Mock Service...")
    print("📊 Dashboard: http://localhost:8000")
    print("📈 Metrics: http://localhost:8000/metrics")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\n📋 Available endpoints:")
    print("  GET    /api/users/{user_id}")
    print("  GET    /api/users?limit=10&page=1&active=true")
    print("  POST   /api/users")
    print("  PUT    /api/users/{user_id}")
    print("  DELETE /api/users/{user_id}")
    print("  GET    /health")

    mock.run()
