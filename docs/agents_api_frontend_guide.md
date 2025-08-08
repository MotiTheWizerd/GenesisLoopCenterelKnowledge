# Agents API Documentation

## Overview

The Agents API provides a complete interface for AI agent message processing and session management. This system replicates the functionality from agents_test.py as HTTP endpoints.

## Endpoints

### 1. Process Single Message

**POST** `/agents/message`

Send a single message to the AI agent and receive a response.

#### Request Format

```json
{
  "message": "Hello! Can you help me?",
  "user_id": "user-123",
  "session_id": "session-456",
  "context": {
    "timestamp": "2025-01-28T10:30:00Z",
    "source": "web_frontend"
  },
  "assigned_by": "user"
}
```

#### Response Format

```json
{
  "message_id": "uuid-here",
  "status": "completed",
  "response": "I am an AI assistant designed to help users with various tasks and provide information. I can generate text, translate languages, answer questions, and engage in conversations. I'm here to assist you!",
  "user_id": "user-123",
  "session_id": "session-456",
  "processing_time_ms": 1500,
  "timestamp": "2025-01-28T10:30:00Z",
  "error_message": null,
  "context": {
    "session_state": {
      "message_count": 5
    },
    "assigned_by": "user"
  }
}
```

### 2. Batch Message Processing

**POST** `/agents/batch`

Process multiple messages in a single request.

#### Request Format

```json
{
  "messages": [
    {
      "message": "What is 2+2?",
      "user_id": "user-123",
      "session_id": "session-456",
      "assigned_by": "user"
    },
    {
      "message": "What is the capital of France?",
      "user_id": "user-123",
      "session_id": "session-456",
      "assigned_by": "user"
    }
  ],
  "batch_id": "batch-uuid-here",
  "process_parallel": false
}
```

#### Response Format

```json
{
  "batch_id": "batch-uuid-here",
  "total_messages": 2,
  "successful_responses": [
    {
      "message_id": "uuid-1",
      "status": "completed",
      "response": "2+2 equals 4.",
      "user_id": "user-123",
      "session_id": "session-456",
      "processing_time_ms": 800,
      "timestamp": "2025-01-28T10:30:00Z"
    },
    {
      "message_id": "uuid-2",
      "status": "completed",
      "response": "The capital of France is Paris.",
      "user_id": "user-123",
      "session_id": "session-456",
      "processing_time_ms": 900,
      "timestamp": "2025-01-28T10:30:01Z"
    }
  ],
  "failed_responses": [],
  "processing_time_ms": 1800,
  "timestamp": "2025-01-28T10:30:01Z",
  "status": "completed"
}
```

### 3. Session Information

**GET** `/agents/session/{user_id}/{session_id}`

Get information about a specific session.

#### Response Format

```json
{
  "status": "success",
  "session_info": {
    "session_id": "session-456",
    "user_id": "user-123",
    "created_at": "2025-01-28T10:00:00Z",
    "last_activity": "2025-01-28T10:30:00Z",
    "message_count": 5,
    "status": "active"
  },
  "timestamp": "2025-01-28T10:30:00Z"
}
```

### 4. List Active Sessions

**GET** `/agents/sessions`

List all active sessions.

#### Response Format

```json
{
  "status": "success",
  "active_session_count": 2,
  "active_sessions": [
    {
      "session_id": "session-456",
      "user_id": "user-123",
      "created_at": "2025-01-28T10:00:00Z",
      "last_activity": "2025-01-28T10:30:00Z",
      "message_count": 5,
      "status": "active"
    },
    {
      "session_id": "session-789",
      "user_id": "user-456",
      "created_at": "2025-01-28T09:45:00Z",
      "last_activity": "2025-01-28T10:25:00Z",
      "message_count": 3,
      "status": "active"
    }
  ],
  "timestamp": "2025-01-28T10:30:00Z"
}
```

### 5. Close Session

**DELETE** `/agents/session/{user_id}/{session_id}`

Close a specific session.

#### Response Format

```json
{
  "status": "success",
  "message": "Session session-456 for user user-123 has been closed",
  "timestamp": "2025-01-28T10:30:00Z"
}
```

### 6. Health Status

**GET** `/agents/health`

Get system health status.

#### Response Format

```json
{
  "status": "success",
  "health": {
    "status": "healthy",
    "active_sessions": 2,
    "total_messages_processed": 150,
    "average_response_time_ms": 1200.5,
    "last_health_check": "2025-01-28T10:30:00Z",
    "agent_info": {
      "agent_type": "GetHelperAgent",
      "app_name": "ray-consciousness-agent",
      "session_service": "InMemorySessionService"
    }
  },
  "timestamp": "2025-01-28T10:30:00Z"
}
```

## Status Codes

| Code | Status       | Meaning                                           |
| ---- | ------------ | ------------------------------------------------- |
| 200  | Success      | Request processed successfully                    |
| 400  | Bad Request  | Invalid request format or missing required fields |
| 404  | Not Found    | Session or endpoint not found                     |
| 500  | Server Error | Internal server error during processing           |

## Response Status Values

| Status       | Meaning                        | Action                      |
| ------------ | ------------------------------ | --------------------------- |
| `completed`  | Message processed successfully | Use `response` field        |
| `error`      | Processing failed              | Check `error_message` field |
| `processing` | Still processing (rare)        | Wait or poll                |

## Error Response Format

```json
{
  "message_id": "uuid-here",
  "status": "error",
  "response": null,
  "user_id": "user-123",
  "session_id": "session-456",
  "processing_time_ms": 100,
  "timestamp": "2025-01-28T10:30:00Z",
  "error_message": "Error processing message: Invalid input format",
  "context": {}
}
```

## Basic Usage Examples

### JavaScript/Fetch

```javascript
// Send a message
const response = await fetch("http://localhost:8000/agents/message", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    message: "Hello!",
    user_id: "user-123",
    session_id: "session-456",
  }),
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

## Session Management

Sessions persist automatically across requests. Use the same `session_id` to maintain conversation context.

### Generate Session ID

```javascript
const generateSessionId = () => {
  return (
    "session-" + Date.now() + "-" + Math.random().toString(36).substr(2, 9)
  );
};
```

## Best Practices

1. **Always handle errors** - Check response status and error_message
2. **Use unique session IDs** - For proper conversation tracking
3. **Implement timeouts** - Prevent hanging requests
4. **Validate inputs** - Sanitize user input before sending
5. **Monitor health** - Use `/agents/health` endpoint periodically

## Testing

Test basic functionality:

```javascript
const testMessage = async () => {
  const response = await fetch("http://localhost:8000/agents/message", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: "Test message",
      user_id: "test-user",
      session_id: "test-session-" + Date.now(),
    }),
  });

  const data = await response.json();
  console.log("Status:", data.status);
  console.log("Response:", data.response);
  console.log("Processing time:", data.processing_time_ms + "ms");
};
```
