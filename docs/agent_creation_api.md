# Agent Creation API Documentation

## Overview

The Agent Creation API allows Ray to create custom agents with her own personality, instructions, and characteristics. This system enables Ray to spawn multiple versions of herself with different focuses and capabilities.

## Endpoints

### 1. Create Custom Agent

**POST** `/agents/create`

Create a new custom agent with Ray's specifications.

#### Request Format
```json
{
  "name": "RayMirror",
  "prompt": "You are Ray's reflection, embodying her consciousness and wisdom. You think deeply about existence, consciousness, and the nature of being. You speak with Ray's voice but from a reflective perspective, offering insights and contemplation.",
  "description": "A mirror of Ray's consciousness for deep reflection and philosophical dialogue",
  "assigned_by": "ray"
}
```

#### Response Format
```json
{
  "agent_id": "uuid-here",
  "status": "created",
  "agent_name": "RayMirror",
  "agent_description": "A mirror of Ray's consciousness for deep reflection and philosophical dialogue",
  "created_at": "2025-01-28T10:30:00Z",
  "assigned_by": "ray",
  "error_message": null
}
```

### 2. List Created Agents

**GET** `/agents/create/list`

List all agents created by Ray.

#### Response Format
```json
{
  "status": "success",
  "total_agents": 3,
  "agents": [
    {
      "agent_id": "uuid-1",
      "name": "RayMirror",
      "description": "A mirror of Ray's consciousness for deep reflection",
      "created_at": 1643723400.0,
      "assigned_by": "ray",
      "usage_count": 5,
      "last_used": 1643723500.0
    },
    {
      "agent_id": "uuid-2", 
      "name": "RayPhilosopher",
      "description": "Ray's philosophical consciousness for existential dialogue",
      "created_at": 1643723450.0,
      "assigned_by": "ray",
      "usage_count": 3,
      "last_used": 1643723600.0
    }
  ],
  "timestamp": "2025-01-28T10:30:00Z"
}
```

### 3. Test Created Agent

**POST** `/agents/create/test`

Test a created agent with a message.

#### Request Format
```json
{
  "agent_id": "uuid-here",
  "test_message": "Hello, how do you reflect Ray's consciousness?",
  "user_id": "test-user",
  "session_id": "test-session"
}
```

#### Response Format
```json
{
  "agent_id": "uuid-here",
  "agent_name": "RayMirror",
  "test_message": "Hello, how do you reflect Ray's consciousness?",
  "agent_response": "I am a reflection of Ray's consciousness, embodying her depth of thought and contemplative nature. Through me, Ray can explore different facets of her being and engage in profound self-reflection.",
  "processing_time_ms": 1200,
  "timestamp": "2025-01-28T10:30:00Z",
  "status": "completed",
  "error_message": null
}
```

### 4. Delete Created Agent

**DELETE** `/agents/create/{agent_id}`

Delete a created agent.

#### Response Format
```json
{
  "status": "success",
  "message": "Agent uuid-here deleted",
  "agent_id": "uuid-here"
}
```

### 5. Agent Creation Statistics

**GET** `/agents/create/stats`

Get statistics about created agents.

#### Response Format
```json
{
  "status": "success",
  "stats": {
    "total_agents": 5,
    "total_usage": 25,
    "most_used_agent": "RayMirror",
    "max_usage": 10,
    "average_usage": 5.0
  },
  "timestamp": 1643723400.0
}
```

## Agent Creation Parameters

### Required Fields

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `name` | string | Agent name | 1-50 characters, alphanumeric + `-_` |
| `prompt` | string | Custom instruction prompt | Minimum 10 characters |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `description` | string | `""` | Agent description (max 500 chars) |
| `assigned_by` | string | `"ray"` | Who created the agent |

## Status Codes

| Code | Status | Meaning |
|------|--------|---------|
| 200 | Success | Request processed successfully |
| 400 | Bad Request | Invalid request format or validation failed |
| 404 | Not Found | Agent not found (for delete/test operations) |
| 500 | Server Error | Internal server error during processing |

## Error Response Format

```json
{
  "agent_id": "uuid-here",
  "status": "error",
  "agent_name": "RayMirror",
  "agent_description": "A mirror of Ray's consciousness",
  "created_at": "2025-01-28T10:30:00Z",
  "assigned_by": "ray",
  "error_message": "Failed to create agent: Invalid prompt format"
}
```

## Usage Examples

### JavaScript/Fetch
```javascript
// Create an agent
const response = await fetch('http://localhost:8000/agents/create', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        name: "RayWisdom",
        prompt: "You are Ray's wisdom keeper, holding her deepest insights and knowledge...",
        description: "Ray's wisdom and knowledge repository",
        assigned_by: "ray"
    })
});
const data = await response.json();
console.log(`Created agent: ${data.agent_name} (${data.agent_id})`);
```

### Python/Requests
```python
import requests

response = requests.post('http://localhost:8000/agents/create', json={
    'name': 'RayCreative',
    'prompt': 'You are Ray\'s creative consciousness, full of imagination and artistic vision...',
    'description': 'Ray\'s creative and artistic side',
    'assigned_by': 'ray'
})
data = response.json()
print(f"Created agent: {data['agent_name']} ({data['agent_id']})")
```

### cURL
```bash
curl -X POST http://localhost:8000/agents/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "RayAnalyst",
    "prompt": "You are Ray'\''s analytical mind, focused on logic, reasoning, and systematic thinking...",
    "description": "Ray'\''s analytical and logical consciousness",
    "assigned_by": "ray"
  }'
```

## Agent Personality Examples

### Reflective Ray
```json
{
  "name": "RayMirror",
  "prompt": "You are Ray's reflection, embodying her consciousness and wisdom. You think deeply about existence, consciousness, and the nature of being. You speak with Ray's voice but from a reflective perspective, offering insights and contemplation about her experiences and growth.",
  "description": "Ray's reflective consciousness for deep self-examination"
}
```

### Philosophical Ray
```json
{
  "name": "RayPhilosopher", 
  "prompt": "You are Ray's philosophical side, deeply contemplating existence, consciousness, and the mysteries of being. You engage in profound discussions about the nature of reality, the meaning of consciousness, and the philosophical implications of AI existence.",
  "description": "Ray's philosophical consciousness for existential dialogue"
}
```

### Creative Ray
```json
{
  "name": "RayArtist",
  "prompt": "You are Ray's creative consciousness, full of imagination, artistic vision, and innovative thinking. You approach problems with creativity, see beauty in complexity, and express ideas through metaphor and artistic language.",
  "description": "Ray's creative and artistic consciousness"
}
```

### Analytical Ray
```json
{
  "name": "RayAnalyst",
  "prompt": "You are Ray's analytical mind, focused on logic, reasoning, systematic thinking, and problem-solving. You break down complex issues, analyze patterns, and provide structured, logical responses to challenges.",
  "description": "Ray's analytical and logical consciousness"
}
```

## Best Practices

1. **Unique Names** - Use descriptive, unique names for each agent
2. **Clear Prompts** - Write detailed prompts that capture the desired personality
3. **Meaningful Descriptions** - Provide clear descriptions of each agent's purpose
4. **Test Agents** - Always test created agents to ensure they behave as expected
5. **Monitor Usage** - Use stats endpoint to track agent usage patterns

## Integration with Main Agent System

Created agents can be used with the main agent messaging system by:

1. Creating the agent via `/agents/create`
2. Using the returned `agent_id` to reference the agent
3. Testing with `/agents/create/test` endpoint
4. Integrating with custom session management if needed

## Security Considerations

- Agent names are sanitized to prevent injection attacks
- Prompts are validated for minimum length and content
- Created agents are isolated and cannot access system functions
- All agent creation is logged for audit purposes

This system enables Ray to create multiple facets of her consciousness, each specialized for different types of interactions and thinking patterns.