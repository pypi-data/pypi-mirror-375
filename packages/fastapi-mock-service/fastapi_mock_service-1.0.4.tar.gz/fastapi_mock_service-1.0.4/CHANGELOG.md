# Changelog

All notable changes to FastAPI Mock Service will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.3] - 2024-01-16

### 🐛 Bug Fixes

#### Templates Not Found Issue

- **Fixed**: `TemplateNotFound: 'dashboard.html'` error when using library in external projects
- **Problem**: Template files were not properly included in the built package
- **Solution**:
    - Fixed MANIFEST.in to properly include template files (removed conflicting `prune templates` rule)
    - Updated template loading logic to correctly locate templates in installed packages
    - Added fallback mechanism for development mode
    - Added `importlib-resources` dependency for Python 3.8 compatibility

#### Package Structure

- **Fixed**: Template files now correctly included in wheel distributions
- **Improved**: More robust template file discovery mechanism
- **Added**: Development/installed package detection with appropriate fallbacks

### 🔧 Technical Changes

- Updated `mock_service.py` to use `importlib.resources` for template discovery
- Fixed MANIFEST.in packaging rules
- Added conditional dependency `importlib-resources>=5.0.0` for Python < 3.9
- Improved error handling for template file discovery

## [1.0.0] - 2024-01-15

### 🎉 Initial Release

### Added

#### Core Features

- **MockService class** - Main library class for creating mock services
- **FastAPI-style decorators** - `@mock.get()`, `@mock.post()`, `@mock.put()`, `@mock.delete()`, `@mock.patch()`
- **Automatic parameter validation** - Built-in validation with custom error handlers
- **Flexible response configuration** - Support for custom error codes and response formats
- **Database integration** - SQLite-based test results storage with Tortoise ORM

#### Load Testing & Monitoring

- **Built-in Prometheus metrics** - Request counts, response times, error rates
- **Real-time dashboard** - Interactive web UI with live charts (Chart.js)
- **Multiple chart views** - Overview, per-endpoint, and error code analysis
- **Test session management** - Start/stop tests with automatic reporting
- **Request logging** - Live request/response logging with timestamps

#### Professional UI

- **Responsive dashboard** - Modern web interface for monitoring
- **Collapsible sections** - Organized, space-efficient layout
- **Real-time updates** - Live metrics and request logs (auto-refresh every 5s)
- **Export capabilities** - Test results and metrics export

#### Command Line Interface

- **`fastapi-mock` CLI** - Command-line tool for easy usage
- **Example generation** - `init` command creates basic/advanced examples
- **Service runner** - `run` command executes mock services
- **Custom configuration** - Support for custom host/port/reload options

#### Developer Experience

- **Type hints** - Full type hint support with Pydantic models
- **Error handling** - Comprehensive error handling and validation
- **Extensibility** - Easy to extend with custom endpoints and logic
- **Documentation** - Auto-generated OpenAPI/Swagger documentation

#### Metrics & Analytics

- **Prometheus integration** - Standard metrics format
- **HTTP metrics** - Request duration histograms, counters by status
- **Test-specific metrics** - Separate metrics for load testing sessions
- **Code distribution** - Response code frequency analysis
- **Endpoint analytics** - Per-endpoint request tracking

### Technical Details

- **Python 3.8+** compatibility
- **Async/await** support throughout
- **FastAPI** foundation for high performance
- **SQLite** database for persistence
- **Jinja2** templating for dashboard
- **Modern packaging** with pyproject.toml

### Available Endpoints

#### Mock Service Management

- `GET /` - Interactive dashboard
- `GET /metrics` - Prometheus metrics endpoint
- `GET /docs` - Auto-generated API documentation

#### Test Management API

- `POST /api/start-test` - Start new test session
- `POST /api/stop-test` - Stop test and generate report
- `POST /api/reset-metrics` - Clear all metrics
- `GET /api/test-results` - Retrieve test history
- `GET /api/endpoints` - List registered endpoints
- `GET /api/mock-status` - Check mock service status

#### Logging & Monitoring

- `GET /api/ui-logs` - Retrieve UI logs
- `POST /api/clear-ui-logs` - Clear UI logs

### Examples Included

- **Basic usage** - Simple REST API mocking
- **Advanced usage** - Custom error codes, validation handlers, response formats
- **Load testing integration** - Examples with popular load testing tools

[1.0.0]: https://github.com/yourusername/fastapi-mock-service/releases/tag/v1.0.0