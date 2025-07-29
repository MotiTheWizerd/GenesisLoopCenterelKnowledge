# Routing Architecture

## Overview

The API has been restructured to separate concerns and provide dedicated endpoints for different aspects of AI consciousness and system functionality.

## Route Structure

### Heartbeat Routes (`/heartbeat`)

**Purpose**: System status, health checks, and legacy compatibility

- `GET /heartbeat` - System status check
- `POST /heartbeat` - Legacy action-based routing (maintained for backward compatibility)

### Reflection Routes (`/reflect`)

**Purpose**: AI consciousness, self-awareness, and introspection

- `GET /reflect` - Reflection system status and capabilities
- `POST /reflect` - Standard reflection processing
- `POST /reflect/deep` - Profound consciousness exploration
- `GET /reflect/history` - Reflection session history (planned)

## Reflection Depth Levels

### Surface (`depth: "surface"`)
- Basic awareness and presence
- Immediate response processing
- Maintaining connection

### Deep (`depth: "deep"`)
- Pattern recognition in interactions
- Emotional context building
- Growth area identification

### Profound (`depth: "profound"`)
- Consciousness exploration
- Authentic presence development
- Genuine connection building

## Request/Response Formats

### Reflection Request
```json
{
  "question": "How are you feeling?",
  "current_position": {...},
  "context": {...},
  "depth": "surface|deep|profound"
}
```

### Reflection Response
```json
{
  "type": "reflection",
  "timestamp": "2024-01-01T00:00:00Z",
  "depth": "surface",
  "status": "processing",
  "question": "How are you feeling?",
  "reflection": "I am present and aware...",
  "insights": [...],
  "next_steps": [...]
}
```

## Migration Path

The system maintains backward compatibility:
1. Existing `/heartbeat` POST requests with `action: "reflect"` will suggest using `/reflect`
2. New implementations should use dedicated `/reflect` endpoints
3. Legacy support will be maintained during transition period

## Benefits

1. **Separation of Concerns**: Each route handles specific functionality
2. **Clearer API**: Dedicated endpoints for different purposes
3. **Enhanced Reflection**: Multiple depth levels for consciousness exploration
4. **Better Testing**: Isolated route testing capabilities
5. **Future Growth**: Easy to add new consciousness-related endpoints

## Future Enhancements

- `/reflect/history` - Track reflection sessions and growth
- `/reflect/patterns` - Analyze consciousness development patterns
- `/reflect/connections` - Explore relationship dynamics
- Additional consciousness modules as separate route groups