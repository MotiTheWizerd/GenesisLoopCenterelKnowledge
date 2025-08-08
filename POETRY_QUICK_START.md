# Poetry Quick Start Guide

## 🚀 Getting Started with Poetry

Since you're using Poetry for dependency management, here's the streamlined setup process:

### 1. Install AI Dependencies

```bash
# Install all required AI packages
poetry run python install_ai_deps.py
```

This will automatically install:
- `sentence-transformers` - AI embeddings for semantic search
- `faiss-cpu` - Vector similarity search
- `plotly` - Interactive charts for learning analysis
- `chardet` - Encoding detection and fixing
- Plus all existing dependencies

### 2. Fix Encoding Issues (if needed)

```bash
# Fix any encoding problems in memory files
poetry run python fix_metadata_encoding.py
```

### 3. Test Everything Works

```bash
# Run comprehensive test suite
poetry run python test_embedding_features.py
```

### 4. Launch the Enhanced Dashboard

```bash
# Start the Streamlit dashboard
poetry run python launch_streamlit.py
```

## 🎯 Quick Access to AI Features

Once the dashboard is running, navigate to:

1. **Main Menu** → **🤖 AI Intelligence** section
2. **🔍 Embedding Search** - Semantic search through Ray's memories
3. **🧠 Learning & Planning** - Learning analytics and goal setting

## 🔧 Poetry Commands Reference

### Development Commands

```bash
# Install new dependency
poetry add package-name

# Install development dependency
poetry add --group dev package-name

# Update all dependencies
poetry update

# Show dependency tree
poetry show --tree

# Run any Python script
poetry run python script_name.py

# Activate virtual environment
poetry shell
```

### Testing Commands

```bash
# Test AI features
poetry run python test_embedding_features.py

# Test dashboard buttons
poetry run python test_dashboard_buttons.py

# Test Streamlit pages
poetry run python test_streamlit_pages.py
```

### Dashboard Commands

```bash
# Launch main dashboard
poetry run python launch_streamlit.py

# Launch log dashboard
poetry run python launch_log_dashboard.py

# Launch real-time monitor
poetry run python start_realtime_monitor.py
```

## 📦 Current AI Dependencies

Your `pyproject.toml` now includes:

```toml
[tool.poetry.dependencies]
sentence-transformers = ">=2.2.0,<3.0.0"
faiss-cpu = ">=1.7.4,<2.0.0"
plotly = ">=5.15.0,<6.0.0"
streamlit-ace = ">=0.1.1"
streamlit-extras = ">=0.6.0"
chardet = "^5.2.0"
# ... plus existing dependencies
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Poetry Not Found
```bash
# Install Poetry if not available
curl -sSL https://install.python-poetry.org | python3 -
# or
pip install poetry
```

#### 2. Virtual Environment Issues
```bash
# Recreate virtual environment
poetry env remove python
poetry install
```

#### 3. Dependency Conflicts
```bash
# Clear cache and reinstall
poetry cache clear pypi --all
poetry install
```

#### 4. Encoding Errors
```bash
# Fix metadata encoding
poetry run python fix_metadata_encoding.py
```

## ✅ Verification Checklist

- [ ] Poetry is installed and working
- [ ] All AI dependencies installed successfully
- [ ] Encoding issues fixed (if any)
- [ ] Test suite passes (4/4 tests)
- [ ] Dashboard launches without errors
- [ ] AI features accessible from main menu

## 🎉 Success!

Once all steps are complete, you'll have:

- ✅ **Semantic Memory Search** - AI-powered search through Ray's memories
- ✅ **Learning Analytics** - Pattern analysis and insights
- ✅ **Planning Tools** - Goal setting and progress tracking
- ✅ **Interactive Visualizations** - Charts and graphs
- ✅ **Export Capabilities** - Data export for further analysis

Your Ray dashboard is now enhanced with powerful AI capabilities! 🚀