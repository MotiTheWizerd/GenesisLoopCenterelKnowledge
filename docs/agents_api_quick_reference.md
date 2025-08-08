# Agents API Quick Reference

## Endpoints Overview

| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| POST | `/agents/message` | Send single message to agent | No |
| POST | `/agents/batch` | Send multiple messages | No |
| GET | `/agents/session/{user_id}/{session_id}` | Get session info | No |
| GET | `/agents/sessions` | List active sessions | No |
| DELETE | `/agents/session/{user_id}/{session_id}` | Close session | No |
| GET | `/agents/health` | System health status | No |

## Quick Start Examples

### JavaScript/Fetch

```javascript
// Send a message
const response = await fetch('http://localhost:8000/agents/message', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        message: "Hello!",
        user_id: "user-123",
        session_id: "session-456"
    })
});
const data = await response.json();
console.log(data.response); // Agent's reply
```

### Python/Requests

```python
import requests

response = requests.post('http://localhost:8000/agents/message', json={
    'message': 'Hello!',
    'user_id': 'user-123',
    'session_id': 'session-456'
})
data = response.json()
print(data['response'])  # Agent's reply
```

### cURL

```bash
curl -X POST http://localhost:8000/agents/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello!",
    "user_id": "user-123",
    "session_id": "session-456"
  }'
```

## Request/Response Formats

### Single Message Request

```json
{
  "message": "Hello! Can you help me?",
  "user_id": "user-123",
  "session_id": "session-456",
  "context": {},
  "assigned_by": "user"
}
```

### Single Message Response

```json
{
  "message_id": "uuid-here",
  "status": "completed",
  "response": "I'm here to help! What do you need assistance with?",
  "user_id": "user-123",
  "session_id": "session-456",
  "processing_time_ms": 1500,
  "timestamp": "2025-01-28T10:30:00Z",
  "error_message": null,
  "context": {
    "session_state": {
      "message_count": 1
    },
    "assigned_by": "user"
  }
}
```

### Batch Request

```json
{
  "messages": [
    {
      "message": "What is 2+2?",
      "user_id": "user-123",
      "session_id": "session-456"
    },
    {
      "message": "What is the capital of France?",
      "user_id": "user-123",
      "session_id": "session-456"
    }
  ],
  "process_parallel": false
}
```

## Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process response |
| 400 | Bad Request | Check request format |
| 404 | Not Found | Check endpoint URL |
| 500 | Server Error | Retry or contact support |

## Common Response Statuses

| Status | Meaning | Next Steps |
|--------|---------|------------|
| `completed` | Message processed successfully | Use `response` field |
| `error` | Processing failed | Check `error_message` field |
| `processing` | Still processing (rare) | Poll or wait |

## Error Handling

```javascript
try {
    const response = await fetch('/agents/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(messageData)
    });
    
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }
    
    const data = await response.json();
    
    if (data.status === 'error') {
        throw new Error(data.error_message);
    }
    
    return data.response;
} catch (error) {
    console.error('Agent request failed:', error);
    // Handle error appropriately
}
```

## Session Management

### Generate Session ID

```javascript
const generateSessionId = () => {
    return 'session-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
};
```

### Session Persistence

Sessions persist automatically. Use the same `session_id` across requests to maintain conversation context.

## Rate Limiting

- No built-in rate limiting currently
- Implement client-side throttling for production use
- Recommended: Max 60 requests per minute per session

## Best Practices

1. **Always handle errors** - Network and API errors can occur
2. **Use unique session IDs** - For proper conversation tracking
3. **Implement timeouts** - Prevent hanging requests
4. **Cache responses** - For repeated identical queries
5. **Sanitize inputs** - Clean user input before sending
6. **Monitor health** - Use `/agents/health` endpoint

## Testing

```javascript
// Test basic functionality
const testMessage = async () => {
    const response = await fetch('http://localhost:8000/agents/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            message: 'Test message',
            user_id: 'test-user',
            session_id: 'test-session-' + Date.now()
        })
    });
    
    const data = await response.json();
    console.log('Status:', data.status);
    console.log('Response:', data.response);
    console.log('Processing time:', data.processing_time_ms + 'ms');
};

testMessage();
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Check if server is running on port 8000 |
| 404 errors | Verify endpoint URLs are correct |
| Timeout errors | Increase timeout or check server load |
| Empty responses | Check `status` field for errors |
| Session not found | Use consistent session IDs |

## Environment Setup

### Development
```
API_BASE_URL=http://localhost:8000
```

### Production
```
API_BASE_URL=https://your-domain.com
```

## Integration Checklist

- [ ] Server running on correct port
- [ ] CORS configured for your domain
- [ ] Error handling implemented
- [ ] Session management in place
- [ ] Input validation added
- [ ] Timeout handling configured
- [ ] Health monitoring setup
- [ ] Rate limiting considered