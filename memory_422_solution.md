# Memory Store 422 Error - Solution Summary

## Problem Identified
The `/memory/store` endpoint was receiving 422 "Unprocessable Entity" errors because clients were sending requests without the required `memories` field.

## Root Cause
The `StoreRequest` model requires a `memories` field (list of dictionaries), but some client was sending requests with only optional fields like `source` and `timestamp`.

## Solution Implemented

### 1. Enhanced Error Handling
- Added comprehensive request validation before Pydantic processing
- Detailed error logging with request IDs for tracking
- Clear error messages explaining what's missing and expected format

### 2. Debug Endpoints Added
- `GET /memory/debug/recent-errors` - Shows recent memory-related errors
- Enhanced logging in `logs/heartbeat_detailed.jsonl`

### 3. Request Validation Flow
```
1. Raw request received
2. Parse JSON body
3. Check if 'memories' field exists
4. Validate 'memories' is a list
5. Pass to Pydantic validation
6. Process valid request
```

## Error Details Logged
When a 422 error occurs, the system now logs:
- Request ID for tracking
- Missing or invalid fields
- Raw request data received
- Expected format example
- Timestamp and error type

## Valid Request Format
```json
{
  "memories": [
    {
      "content": "Memory content here",
      "type": "optional_type",
      "metadata": {}
    }
  ],
  "source": "optional_source",
  "timestamp": "optional_timestamp"
}
```

## Monitoring Commands

### Check Recent Errors
```bash
curl http://localhost:8000/memory/debug/recent-errors
```

### Monitor Logs in Real-time
```bash
tail -f logs/heartbeat_detailed.jsonl | grep -i error
```

### Test Endpoint
```bash
python test_422_fix.py
```

## Prevention
1. Ensure all clients sending to `/memory/store` include the `memories` field
2. Validate request format before sending
3. Monitor the debug endpoint for validation errors
4. Check logs regularly for error patterns

## Next Steps
1. Identify the client/agent making malformed requests
2. Fix the client to include required fields
3. Monitor logs to ensure no more 422 errors occur

The system now provides clear debugging information to identify and fix any future validation issues.