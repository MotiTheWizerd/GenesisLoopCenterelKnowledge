# Poetry Commands Reference

## 🚀 Quick Start Commands

### Start the API Server
```bash
# Option 1: Using uvicorn directly
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using the start script (recommended)
poetry run python start_api_server.py
```

### Start the Dashboard
```bash
# Main dashboard with AI features
poetry run streamlit run ui/streamlit/main_menu.py --server.port 8501
```

### Start Log Dashboard
```bash
# Separate log analysis dashboard
poetry run streamlit run launch_log_dashboard.py --server.port 8502
```

## 🤖 AI Features Commands

### Install AI Dependencies
```bash
poetry run python install_ai_deps.py
```

### Fix Encoding Issues
```bash
poetry run python fix_metadata_encoding.py
```

### Test AI Features
```bash
poetry run python test_embedding_features.py
```

## 🧪 Testing Commands

### Test Dashboard Components
```bash
# Test button keys and imports
poetry run python test_dashboard_buttons.py

# Test Streamlit pages
poetry run python test_streamlit_pages.py

# Test AI features
poetry run python test_embedding_features.py
```

### Run All Tests
```bash
# Run all test scripts
poetry run python test_dashboard_buttons.py && poetry run python test_streamlit_pages.py && poetry run python test_embedding_features.py
```

## 📦 Dependency Management

### Add New Dependencies
```bash
# Add production dependency
poetry add package-name

# Add development dependency
poetry add --group dev package-name

# Add with version constraint
poetry add "package-name>=1.0.0,<2.0.0"
```

### Update Dependencies
```bash
# Update all dependencies
poetry update

# Update specific package
poetry update package-name

# Show outdated packages
poetry show --outdated
```

### View Dependencies
```bash
# Show all dependencies
poetry show

# Show dependency tree
poetry show --tree

# Show specific package info
poetry show package-name
```

## 🔧 Environment Management

### Virtual Environment
```bash
# Activate shell
poetry shell

# Show environment info
poetry env info

# List environments
poetry env list

# Remove environment
poetry env remove python
```

### Install Project
```bash
# Install all dependencies
poetry install

# Install without dev dependencies
poetry install --only main

# Install only dev dependencies
poetry install --only dev
```

## 🌐 Service URLs

When running the services, they'll be available at:

- **API Server**: http://localhost:8000
  - Swagger docs: http://localhost:8000/docs
  - ReDoc: http://localhost:8000/redoc

- **Main Dashboard**: http://localhost:8501
  - AI Intelligence features
  - Memory management
  - System health monitoring

- **Log Dashboard**: http://localhost:8502
  - Log analysis and visualization
  - Timeline views
  - Statistics

## 🔄 Development Workflow

### Typical Development Session
```bash
# 1. Start API server (in terminal 1)
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 2. Start dashboard (in terminal 2)
poetry run streamlit run ui/streamlit/main_menu.py --server.port 8501

# 3. Test changes (in terminal 3)
poetry run python test_embedding_features.py

# 4. Fix any encoding issues if needed
poetry run python fix_metadata_encoding.py
```

### Before Committing Changes
```bash
# Run all tests
poetry run python test_dashboard_buttons.py && poetry run python test_streamlit_pages.py && poetry run python test_embedding_features.py

# Format code (if black is configured)
poetry run black .

# Check types (if mypy is configured)
poetry run mypy .
```

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. "No module named uvicorn"
```bash
# Add missing dependencies
poetry add fastapi uvicorn
```

#### 2. "Port already in use"
```bash
# Kill processes on ports
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use different ports
poetry run uvicorn main:app --port 8001
poetry run streamlit run ui/streamlit/main_menu.py --server.port 8502
```

#### 3. "Encoding errors"
```bash
# Fix metadata encoding
poetry run fix-encoding
```

#### 4. "Import errors"
```bash
# Reinstall dependencies
poetry install --sync
```

#### 5. "Virtual environment issues"
```bash
# Recreate environment
poetry env remove python
poetry install
```

## 📊 Monitoring Commands

### Check Service Status
```bash
# Test API server
curl http://localhost:8000/health/status

# Test dashboard (check browser)
# http://localhost:8501

# Check processes
# Windows:
netstat -ano | findstr :8000
netstat -ano | findstr :8501
```

### View Logs
```bash
# API server logs (in terminal where it's running)
# Dashboard logs (in terminal where it's running)

# Or check log files if configured
poetry run python -c "from pathlib import Path; print('Logs:', list(Path('logs').glob('*.log')))"
```

## 🎯 Production Commands

### Build and Deploy
```bash
# Export requirements.txt (if needed)
poetry export -f requirements.txt --output requirements.txt

# Build package
poetry build

# Publish (if configured)
poetry publish
```

### Environment Variables
```bash
# Set environment variables for production
export ENVIRONMENT=production
export API_HOST=0.0.0.0
export API_PORT=8000

# Or use .env file (already exists in project)
```

## 📚 Help and Documentation

### Get Help
```bash
# Poetry help
poetry --help

# Command-specific help
poetry add --help
poetry run --help

# Show project info
poetry show --tree
poetry env info
```

### Useful Resources
- Poetry docs: https://python-poetry.org/docs/
- FastAPI docs: https://fastapi.tiangolo.com/
- Streamlit docs: https://docs.streamlit.io/

---

**Quick Reference Card:**
```bash
# Start everything
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000    # Terminal 1
poetry run streamlit run ui/streamlit/main_menu.py --server.port 8501     # Terminal 2

# Test everything
poetry run python test_embedding_features.py

# Fix issues
poetry run python fix_metadata_encoding.py
```