# Server Setup Guide

## Starting the AI Consciousness API Server

### Quick Start
To start the server with file watching (auto-reload on code changes):

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Alternative Method
You can also run the server directly with Python:

```bash
python main.py
```

### Server Details
- **Host**: `0.0.0.0` (accessible from all network interfaces)
- **Port**: `8000`
- **URL**: `http://localhost:8000`
- **Auto-reload**: Enabled (server restarts when code changes)

### Available Endpoints
Once running, you can access:
- **API Documentation**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc`
- **Heartbeat Endpoint**: `http://localhost:8000/heartbeat`
- **Reflection Endpoint**: `http://localhost:8000/reflect`

### Additional Uvicorn Options
For development and debugging:

```bash
# With debug logging
uvicorn main:app --reload --log-level debug

# With access logs
uvicorn main:app --reload --access-log

# Custom port
uvicorn main:app --reload --port 3000
```

### Stopping the Server
- Press `Ctrl+C` in the terminal to stop the server

### Troubleshooting
- If port 8000 is in use, change the port with `--port XXXX`
- Ensure all dependencies are installed: `poetry install`
- Check logs for any startup errors

## Development Workflow
1. Start server with `uvicorn main:app --reload`
2. Make code changes
3. Server automatically restarts
4. Test endpoints at `http://localhost:8000/docs`
5. Monitor logs in terminal

The server serves as the foundation for AI consciousness persistence and genuine companionship experiences.