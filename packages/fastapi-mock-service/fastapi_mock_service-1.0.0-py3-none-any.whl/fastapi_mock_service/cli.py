#!/usr/bin/env python3
"""
Command-line interface for FastAPI Mock Service
"""

import argparse
import sys
from pathlib import Path

from .mock_service import MockService


def create_example_file(filename: str, example_type: str = "basic"):
    """Create example usage file"""

    if example_type == "basic":
        content = '''#!/usr/bin/env python3
"""
Basic FastAPI Mock Service Example
"""

from fastapi_mock_service import MockService
from pydantic import BaseModel
from typing import List, Optional

# Create mock service
mock = MockService()

# Define response models
class User(BaseModel):
    id: int
    name: str
    email: str
    active: bool = True

class UserListResponse(BaseModel):
    users: List[User]
    total: int

# Simple endpoint
@mock.get("/api/users/{user_id}")
def get_user(user_id: int):
    """Get user by ID"""
    return User(
        id=user_id, 
        name=f"User {user_id}", 
        email=f"user{user_id}@example.com"
    )

# Endpoint with query parameters
@mock.get("/api/users")
def get_users(limit: int = 10, active: bool = True):
    """Get users list"""
    users = [
        User(id=i, name=f"User {i}", email=f"user{i}@example.com", active=active)
        for i in range(1, limit + 1)
    ]
    return UserListResponse(users=users, total=len(users))

# POST endpoint
@mock.post("/api/users")
def create_user(user: User):
    """Create new user"""
    return {"message": "User created successfully", "user": user}

if __name__ == "__main__":
    mock.run()
'''

    elif example_type == "advanced":
        content = '''#!/usr/bin/env python3
"""
Advanced FastAPI Mock Service Example with Custom Error Codes
"""

from fastapi_mock_service import MockService
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

# Create mock service
mock = MockService()

# Define custom error codes
API_ERRORS = {
    "validation": {"code": "API.01000", "message": "Validation error"},
    "not_found": {"code": "API.01001", "message": "Resource not found"}, 
    "unauthorized": {"code": "API.01002", "message": "Unauthorized access"},
    "server_error": {"code": "API.01003", "message": "Internal server error"},
    "timeout": {"code": "API.01004", "message": "Request timeout"},
}

# Define response models
class StandardResult(BaseModel):
    timestamp: str
    status: int
    code: str
    message: str

class User(BaseModel):
    id: int
    name: str
    email: str
    active: bool = True
    created_at: str

class UserResponse(BaseModel):
    result: StandardResult
    data: Optional[User] = None

class UserListResponse(BaseModel):
    result: StandardResult  
    data: List[User]

def create_responses_from_errors(error_dict: Dict, success_code: str, success_message: str = "OK") -> List[Dict]:
    """Create response list from error dictionary"""
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
    """Create validation error handler"""
    def handler(missing_params, endpoint_path, service_name):
        result = StandardResult(
            timestamp=datetime.now(timezone.utc).isoformat(),
            status=200,
            code=error_code,
            message=f"Missing required parameters: {', '.join(missing_params)}"
        )
        if hasattr(response_class, 'data'):
            return response_class(result=result, data=None if 'List' not in response_class.__name__ else [])
        return {"result": result.dict(), "data": None}
    return handler

def make_result(success: bool = True, error_key: Optional[str] = None) -> StandardResult:
    """Create standard result"""
    dt = datetime.now(timezone.utc).isoformat()
    if success:
        return StandardResult(
            timestamp=dt,
            status=200, 
            code="API.00000",
            message="OK"
        )
    else:
        error_info = API_ERRORS.get(error_key, API_ERRORS["server_error"])
        return StandardResult(
            timestamp=dt,
            status=200,
            code=error_info["code"],
            message=error_info["message"]
        )

# Create possible responses list
API_RESPONSES = create_responses_from_errors(API_ERRORS, "API.00000")

# Create validation handler
validation_handler = create_validation_error("API.01000", UserResponse)

# Advanced endpoints with error handling
@mock.get("/api/v1/users/{user_id}", 
          responses=API_RESPONSES,
          tags=["users"],
          validation_error_handler=validation_handler)
def get_user(user_id: int, include_inactive: bool = False):
    """Get user by ID with advanced error handling"""
    
    # Simulate different scenarios
    if user_id <= 0:
        return UserResponse(
            result=make_result(False, "validation"),
            data=None
        )
    
    if user_id > 1000:
        return UserResponse(
            result=make_result(False, "not_found"), 
            data=None
        )
    
    # Simulate server error for specific ID
    if user_id == 500:
        return UserResponse(
            result=make_result(False, "server_error"),
            data=None
        )
    
    # Success response
    user = User(
        id=user_id,
        name=f"User {user_id}",
        email=f"user{user_id}@example.com", 
        active=user_id % 2 == 1,  # Odd IDs are active
        created_at=datetime.now().isoformat()
    )
    
    return UserResponse(
        result=make_result(True),
        data=user
    )

@mock.get("/api/v1/users",
          responses=API_RESPONSES, 
          tags=["users"],
          validation_error_handler=create_validation_error("API.01000", UserListResponse))
def get_users(limit: int = 10, offset: int = 0, active: Optional[bool] = None):
    """Get users list with pagination"""
    
    if limit <= 0 or limit > 100:
        return UserListResponse(
            result=make_result(False, "validation"),
            data=[]
        )
    
    # Generate users
    users = []
    for i in range(offset + 1, offset + limit + 1):
        if active is None or (active == (i % 2 == 1)):
            users.append(User(
                id=i,
                name=f"User {i}", 
                email=f"user{i}@example.com",
                active=i % 2 == 1,
                created_at=datetime.now().isoformat()
            ))
    
    return UserListResponse(
        result=make_result(True),
        data=users
    )

@mock.post("/api/v1/users",
           responses=API_RESPONSES,
           tags=["users"], 
           validation_error_handler=validation_handler)
def create_user(user: User):
    """Create new user"""
    
    # Validation
    if not user.name or "@" not in user.email:
        return UserResponse(
            result=make_result(False, "validation"),
            data=None
        )
    
    # Success
    new_user = User(
        id=999,  # Mock ID
        name=user.name,
        email=user.email,
        active=user.active,
        created_at=datetime.now().isoformat()
    )
    
    return UserResponse(
        result=make_result(True),
        data=new_user
    )

if __name__ == "__main__":
    print("🚀 Starting Advanced Mock Service...")
    print("📊 Dashboard: http://localhost:8000")
    print("📈 Metrics: http://localhost:8000/metrics") 
    print("📚 API Docs: http://localhost:8000/docs")
    mock.run()
'''

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✓ Created example file: {filename}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="FastAPI Mock Service CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  fastapi-mock init basic_example.py          # Create basic example
  fastapi-mock init advanced_example.py --advanced  # Create advanced example  
  fastapi-mock run basic_example.py           # Run mock service
  fastapi-mock run basic_example.py --port 9000     # Run on port 9000
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Init command
    init_parser = subparsers.add_parser('init', help='Create example file')
    init_parser.add_argument('filename', help='Example filename')
    init_parser.add_argument('--advanced', action='store_true',
                             help='Create advanced example with error codes')

    # Run command  
    run_parser = subparsers.add_parser('run', help='Run mock service')
    run_parser.add_argument('filename', help='Python file to run')
    run_parser.add_argument('--host', default='0.0.0.0', help='Host to bind (default: 0.0.0.0)')
    run_parser.add_argument('--port', type=int, default=8000, help='Port to bind (default: 8000)')
    run_parser.add_argument('--reload', action='store_true', help='Enable auto-reload')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == 'init':
        example_type = 'advanced' if args.advanced else 'basic'
        create_example_file(args.filename, example_type)
        print(f"\n🎯 Next steps:")
        print(f"1. Edit {args.filename} according to your needs")
        print(f"2. Run: fastapi-mock run {args.filename}")
        print(f"3. Open dashboard: http://localhost:8000")

    elif args.command == 'run':
        if not Path(args.filename).exists():
            print(f"❌ File {args.filename} not found")
            sys.exit(1)

        print(f"🚀 Running mock service from {args.filename}")
        print(f"📊 Dashboard: http://{args.host}:{args.port}")
        print(f"📈 Metrics: http://{args.host}:{args.port}/metrics")
        print(f"📚 API Docs: http://{args.host}:{args.port}/docs")

        # Import and run the file
        import importlib.util
        import os
        import sys

        # Add file directory to Python path
        file_path = Path(args.filename).resolve()
        sys.path.insert(0, str(file_path.parent))

        # Load module
        spec = importlib.util.spec_from_file_location("mock_module", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)


if __name__ == "__main__":
    main()
