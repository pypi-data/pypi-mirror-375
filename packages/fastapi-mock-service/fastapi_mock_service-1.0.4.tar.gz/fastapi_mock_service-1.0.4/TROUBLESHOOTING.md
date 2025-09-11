# Troubleshooting Guide

## Common Issues and Solutions

### ❌ TemplateNotFound: 'dashboard.html'

**Error Message:**

```
jinja2.exceptions.TemplateNotFound: 'dashboard.html' not found in search path
```

**Cause:**
Template files were not properly included in older versions of the package.

**Solution:**
Update to version 1.0.3 or later:

```bash
pip install --upgrade fastapi-mock-service>=1.0.3
```

**Manual Fix for Development:**
If you're working with the source code directly, ensure the templates directory exists:

```python
from pathlib import Path

# Check if templates exist
template_path = Path("fastapi_mock_service/templates/dashboard.html")
if template_path.exists():
    print("✅ Templates found")
else:
    print("❌ Templates missing")
```

### ❌ TypeError: 'fastapi_mock_service.mock_service' is not a package

**Error Message:**

```
TypeError: 'fastapi_mock_service.mock_service' is not a package
```

**Cause:**
Incorrect usage of `importlib.resources` with module name instead of package name.

**Solution:**
This is fixed in version 1.0.3. Update your installation:

```bash
pip install --upgrade fastapi-mock-service>=1.0.3
```

### ❌ Import Errors

**Error Message:**

```
ImportError: No module named 'importlib_resources'
```

**Cause:**
Missing dependency for Python 3.8.

**Solution:**
Install the required dependency:

```bash
pip install importlib-resources>=5.0.0
```

Or update to the latest version which includes this dependency:

```bash
pip install --upgrade fastapi-mock-service>=1.0.3
```

### 🔧 Development Mode Issues

If you're developing or modifying the library:

1. **Ensure all files are in place:**
   ```bash
   ls -la fastapi_mock_service/templates/
   # Should show dashboard.html
   ```

2. **Rebuild the package:**
   ```bash
   pip install build
   python -m build
   ```

3. **Test the built package:**
   ```bash
   pip install dist/fastapi_mock_service-*.whl --force-reinstall
   ```

### 📝 Reporting Issues

If you encounter other issues:

1. **Check your version:**
   ```python
   import fastapi_mock_service
   print(fastapi_mock_service.__version__)
   ```

2. **Verify installation:**
   ```bash
   pip show fastapi-mock-service
   ```

3. **Create minimal reproduction:**
   ```python
   from fastapi_mock_service import MockService
   
   mock = MockService()
   
   @mock.get("/test")
   def test():
       return {"status": "ok"}
   
   if __name__ == "__main__":
       mock.run()
   ```

4. **Report the issue:** [GitHub Issues](https://github.com/yourusername/fastapi-mock-service/issues)

## Version Compatibility

| Version | Python | Status | Notes |
|---------|--------|--------|-------|
| 1.0.3+  | 3.8+   | ✅ Recommended | Templates issue fixed |
| 1.0.2   | 3.8+   | ⚠️ Has issues | Templates not included |
| 1.0.1   | 3.8+   | ⚠️ Has issues | Templates not included |
| 1.0.0   | 3.8+   | ⚠️ Has issues | Templates not included |