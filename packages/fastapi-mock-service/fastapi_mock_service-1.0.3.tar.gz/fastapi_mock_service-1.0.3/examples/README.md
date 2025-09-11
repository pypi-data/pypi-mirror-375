# FastAPI Mock Service Examples

This directory contains example usage patterns for the FastAPI Mock Service library.

## 📂 Available Examples

### 🟢 [basic_example.py](basic_example.py)

**Simple REST API mock with standard responses**

Features:

- Standard HTTP responses
- Basic CRUD operations
- Query parameters
- Path parameters
- Perfect for getting started

```bash
# Run the basic example
python basic_example.py

# Or using CLI
fastapi-mock run basic_example.py
```

**Endpoints:**

- `GET /api/users/{user_id}` - Get user by ID
- `GET /api/users?limit=10&page=1&active=true` - Get users with pagination
- `POST /api/users` - Create new user
- `PUT /api/users/{user_id}` - Update user
- `DELETE /api/users/{user_id}` - Delete user
- `GET /health` - Health check

---

### 🔴 [advanced_example.py](advanced_example.py)

**Advanced mock with custom error codes and complex scenarios**

Features:

- Custom error codes and messages
- Advanced validation handlers
- Business logic simulation
- Realistic error scenarios
- Load testing integration
- Conditional response data

```bash
# Run the advanced example
python advanced_example.py

# Or using CLI
fastapi-mock run advanced_example.py
```

**Special Test Scenarios:**

- `GET /api/v1/users/500` → Server error simulation
- `GET /api/v1/users/503` → Timeout error simulation
- `GET /api/v1/users/1001` → Not found error
- `POST /api/v1/users` with `name="test"` → Forbidden operation
- `POST /api/v1/users` with `email="admin@..."` → Conflict error

---

## 🚀 Quick Start

### Generate New Examples

```bash
# Create basic example
fastapi-mock init my_basic_mock.py

# Create advanced example with custom error codes
fastapi-mock init my_advanced_mock.py --advanced
```

### Run Examples

```bash
# Method 1: Direct Python execution
python basic_example.py
python advanced_example.py

# Method 2: Using CLI tool
fastapi-mock run basic_example.py
fastapi-mock run advanced_example.py --port 9000

# Method 3: With auto-reload for development
fastapi-mock run basic_example.py --reload
```

## 📊 Dashboard & Monitoring

After starting any example, access:

- **📊 Dashboard**: http://localhost:8000
- **📈 Metrics**: http://localhost:8000/metrics
- **📚 API Docs**: http://localhost:8000/docs

## 🧪 Load Testing

### Using Dashboard

1. Open dashboard at http://localhost:8000
2. Click "Старт теста" to activate endpoints
3. Run your load testing tools
4. Monitor real-time metrics and charts
5. Click "Стоп теста" to generate report

### Using Command Line Tools

```bash
# curl - Simple testing
curl "http://localhost:8000/api/users/123"

# Apache Bench - Load testing
ab -n 1000 -c 10 http://localhost:8000/api/users/123

# wrk - Modern load testing
wrk -t4 -c100 -d30s http://localhost:8000/api/users/123
```

## 🎯 Customization Guide

### Adding Custom Error Codes

```python
# Define your error dictionary
MY_API_ERRORS = {
    "validation": {"code": "MY_API.01000", "message": "Validation failed"},
    "not_found": {"code": "MY_API.01001", "message": "Resource not found"},
    "rate_limit": {"code": "MY_API.01002", "message": "Too many requests"},
}

# Create responses dynamically
def create_responses_from_errors(error_dict, success_code):
    responses = [{"code": success_code, "description": "Success"}]
    for key, info in error_dict.items():
        responses.append({"code": info["code"], "description": info["message"]})
    return responses

MY_RESPONSES = create_responses_from_errors(MY_API_ERRORS, "MY_API.00000")

# Use in decorators
@mock.get("/my/endpoint", responses=MY_RESPONSES, tags=["my-api"])
def my_endpoint():
    # Your logic here
    pass
```

### Custom Validation Handlers

```python
def create_my_validation_handler(error_code, response_class):
    def handler(missing_params, endpoint_path, service_name):
        # Your custom validation logic
        result = StandardResult(
            timestamp=datetime.now().isoformat(),
            status=200,
            code=error_code,
            message=f"Custom validation: {', '.join(missing_params)}"
        )
        return response_class(result=result, data=None)
    return handler
```

## 📚 Learn More

- **Main Documentation**: [README.md](../README.md)
- **API Reference**: See docstrings in source code
- **Load Testing Guide**: Dashboard → "Возможности для НТ" section