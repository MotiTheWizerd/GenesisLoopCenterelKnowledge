# React Integration Guide for Agents API

## Overview

This guide shows how to integrate the Agents API into React applications with hooks, components, and best practices.

## Custom Hook: useAgentsAPI

```jsx
// hooks/useAgentsAPI.js
import { useState, useCallback, useRef, useEffect } from 'react';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export const useAgentsAPI = (userId) => {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [sessionId] = useState(() => generateSessionId());
    const [messageHistory, setMessageHistory] = useState([]);
    const [stats, setStats] = useState({
        messageCount: 0,
        totalResponseTime: 0,
        averageResponseTime: 0
    });

    const abortControllerRef = useRef(null);

    const generateSessionId = () => {
        return 'session-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    };

    const sendMessage = useCallback(async (message, context = {}) => {
        if (!message.trim()) {
            setError('Message cannot be empty');
            return null;
        }

        // Cancel any ongoing request
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
        }

        abortControllerRef.current = new AbortController();
        setIsLoading(true);
        setError(null);

        try {
            const requestBody = {
                message: message.trim(),
                user_id: userId,
                session_id: sessionId,
                context: {
                    timestamp: new Date().toISOString(),
                    source: 'react_frontend',
                    ...context
                },
                assigned_by: 'user'
            };

            const response = await fetch(`${API_BASE_URL}/agents/message`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(requestBody),
                signal: abortControllerRef.current.signal
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.status === 'completed') {
                // Add to message history
                const newMessage = {
                    id: data.message_id,
                    userMessage: message,
                    agentResponse: data.response,
                    timestamp: data.timestamp,
                    processingTime: data.processing_time_ms
                };

                setMessageHistory(prev => [...prev, newMessage]);

                // Update stats
                setStats(prev => {
                    const newCount = prev.messageCount + 1;
                    const newTotal = prev.totalResponseTime + data.processing_time_ms;
                    return {
                        messageCount: newCount,
                        totalResponseTime: newTotal,
                        averageResponseTime: Math.round(newTotal / newCount)
                    };
                });

                return data;
            } else {
                throw new Error(data.error_message || 'Unknown error occurred');
            }

        } catch (error) {
            if (error.name === 'AbortError') {
                return null; // Request was cancelled
            }
            setError(error.message);
            throw error;
        } finally {
            setIsLoading(false);
            abortControllerRef.current = null;
        }
    }, [userId, sessionId]);

    const sendBatchMessages = useCallback(async (messages, processParallel = false) => {
        setIsLoading(true);
        setError(null);

        try {
            const requestBody = {
                messages: messages.map(msg => ({
                    message: msg.message,
                    user_id: userId,
                    session_id: sessionId,
                    context: msg.context || {},
                    assigned_by: 'user'
                })),
                process_parallel: processParallel
            };

            const response = await fetch(`${API_BASE_URL}/agents/batch`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            return data;

        } catch (error) {
            setError(error.message);
            throw error;
        } finally {
            setIsLoading(false);
        }
    }, [userId, sessionId]);

    const clearHistory = useCallback(() => {
        setMessageHistory([]);
        setStats({
            messageCount: 0,
            totalResponseTime: 0,
            averageResponseTime: 0
        });
    }, []);

    const cancelRequest = useCallback(() => {
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
        }
    }, []);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (abortControllerRef.current) {
                abortControllerRef.current.abort();
            }
        };
    }, []);

    return {
        sendMessage,
        sendBatchMessages,
        clearHistory,
        cancelRequest,
        isLoading,
        error,
        sessionId,
        messageHistory,
        stats
    };
};
```

## Chat Component

```jsx
// components/AgentChat.jsx
import React, { useState, useRef, useEffect } from 'react';
import { useAgentsAPI } from '../hooks/useAgentsAPI';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import LoadingIndicator from './LoadingIndicator';
import ErrorMessage from './ErrorMessage';
import ChatStats from './ChatStats';

const AgentChat = ({ userId, className = '' }) => {
    const {
        sendMessage,
        clearHistory,
        cancelRequest,
        isLoading,
        error,
        sessionId,
        messageHistory,
        stats
    } = useAgentsAPI(userId);

    const [inputValue, setInputValue] = useState('');
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messageHistory]);

    const handleSendMessage = async (message) => {
        if (!message.trim() || isLoading) return;

        setInputValue('');
        
        try {
            await sendMessage(message);
        } catch (error) {
            console.error('Failed to send message:', error);
        }
    };

    const handleClearChat = () => {
        if (window.confirm('Are you sure you want to clear the chat history?')) {
            clearHistory();
        }
    };

    return (
        <div className={`agent-chat ${className}`}>
            <div className="chat-header">
                <h3>AI Agent Chat</h3>
                <div className="chat-controls">
                    <button 
                        onClick={handleClearChat}
                        disabled={isLoading || messageHistory.length === 0}
                        className="btn btn-secondary"
                    >
                        Clear Chat
                    </button>
                    {isLoading && (
                        <button 
                            onClick={cancelRequest}
                            className="btn btn-warning"
                        >
                            Cancel
                        </button>
                    )}
                </div>
            </div>

            <div className="chat-messages">
                <MessageList messages={messageHistory} />
                {isLoading && <LoadingIndicator />}
                <div ref={messagesEndRef} />
            </div>

            {error && <ErrorMessage message={error} />}

            <MessageInput
                value={inputValue}
                onChange={setInputValue}
                onSend={handleSendMessage}
                disabled={isLoading}
                placeholder="Type your message..."
            />

            <ChatStats 
                stats={stats}
                sessionId={sessionId}
            />
        </div>
    );
};

export default AgentChat;
```

## Message Components

```jsx
// components/MessageList.jsx
import React from 'react';
import Message from './Message';

const MessageList = ({ messages }) => {
    if (messages.length === 0) {
        return (
            <div className="empty-messages">
                <p>Start a conversation with the AI agent!</p>
            </div>
        );
    }

    return (
        <div className="message-list">
            {messages.map((message) => (
                <div key={message.id} className="message-pair">
                    <Message
                        type="user"
                        content={message.userMessage}
                        timestamp={message.timestamp}
                    />
                    <Message
                        type="agent"
                        content={message.agentResponse}
                        timestamp={message.timestamp}
                        processingTime={message.processingTime}
                    />
                </div>
            ))}
        </div>
    );
};

export default MessageList;
```

```jsx
// components/Message.jsx
import React from 'react';

const Message = ({ type, content, timestamp, processingTime }) => {
    const formatTime = (isoString) => {
        return new Date(isoString).toLocaleTimeString();
    };

    return (
        <div className={`message message-${type}`}>
            <div className="message-content">
                {content}
            </div>
            <div className="message-meta">
                <span className="message-time">
                    {formatTime(timestamp)}
                </span>
                {processingTime && (
                    <span className="processing-time">
                        ({processingTime}ms)
                    </span>
                )}
            </div>
        </div>
    );
};

export default Message;
```

```jsx
// components/MessageInput.jsx
import React, { useState, useRef } from 'react';

const MessageInput = ({ value, onChange, onSend, disabled, placeholder }) => {
    const [isComposing, setIsComposing] = useState(false);
    const textareaRef = useRef(null);

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey && !isComposing) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleSend = () => {
        if (value.trim() && !disabled) {
            onSend(value);
        }
    };

    const adjustTextareaHeight = () => {
        const textarea = textareaRef.current;
        if (textarea) {
            textarea.style.height = 'auto';
            textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
        }
    };

    React.useEffect(() => {
        adjustTextareaHeight();
    }, [value]);

    return (
        <div className="message-input">
            <div className="input-container">
                <textarea
                    ref={textareaRef}
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    onKeyDown={handleKeyDown}
                    onCompositionStart={() => setIsComposing(true)}
                    onCompositionEnd={() => setIsComposing(false)}
                    placeholder={placeholder}
                    disabled={disabled}
                    rows={1}
                    className="message-textarea"
                />
                <button
                    onClick={handleSend}
                    disabled={disabled || !value.trim()}
                    className="send-button"
                >
                    {disabled ? '...' : 'Send'}
                </button>
            </div>
        </div>
    );
};

export default MessageInput;
```

## Utility Components

```jsx
// components/LoadingIndicator.jsx
import React from 'react';

const LoadingIndicator = () => {
    return (
        <div className="loading-indicator">
            <div className="typing-animation">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <span className="loading-text">Agent is thinking...</span>
        </div>
    );
};

export default LoadingIndicator;
```

```jsx
// components/ErrorMessage.jsx
import React from 'react';

const ErrorMessage = ({ message, onDismiss }) => {
    return (
        <div className="error-message">
            <span className="error-icon">⚠️</span>
            <span className="error-text">{message}</span>
            {onDismiss && (
                <button onClick={onDismiss} className="error-dismiss">
                    ×
                </button>
            )}
        </div>
    );
};

export default ErrorMessage;
```

```jsx
// components/ChatStats.jsx
import React from 'react';

const ChatStats = ({ stats, sessionId }) => {
    return (
        <div className="chat-stats">
            <div className="stats-grid">
                <div className="stat-item">
                    <label>Session ID:</label>
                    <span title={sessionId}>
                        {sessionId.substring(0, 12)}...
                    </span>
                </div>
                <div className="stat-item">
                    <label>Messages:</label>
                    <span>{stats.messageCount}</span>
                </div>
                <div className="stat-item">
                    <label>Avg Response:</label>
                    <span>{stats.averageResponseTime}ms</span>
                </div>
            </div>
        </div>
    );
};

export default ChatStats;
```

## CSS Styles

```css
/* styles/AgentChat.css */
.agent-chat {
    display: flex;
    flex-direction: column;
    height: 600px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background: white;
}

.chat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border-bottom: 1px solid #eee;
    background: #f8f9fa;
}

.chat-header h3 {
    margin: 0;
    color: #333;
}

.chat-controls {
    display: flex;
    gap: 0.5rem;
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
}

.message-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.message-pair {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.message {
    max-width: 80%;
    padding: 0.75rem 1rem;
    border-radius: 18px;
    word-wrap: break-word;
}

.message-user {
    align-self: flex-end;
    background: #007bff;
    color: white;
}

.message-agent {
    align-self: flex-start;
    background: #f1f3f4;
    color: #333;
}

.message-meta {
    font-size: 0.75rem;
    color: #666;
    margin-top: 0.25rem;
}

.processing-time {
    margin-left: 0.5rem;
    font-style: italic;
}

.message-input {
    border-top: 1px solid #eee;
    padding: 1rem;
}

.input-container {
    display: flex;
    gap: 0.5rem;
    align-items: flex-end;
}

.message-textarea {
    flex: 1;
    min-height: 40px;
    max-height: 120px;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 20px;
    resize: none;
    font-family: inherit;
    font-size: 14px;
    line-height: 1.4;
}

.message-textarea:focus {
    outline: none;
    border-color: #007bff;
}

.send-button {
    padding: 0.75rem 1.5rem;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 20px;
    cursor: pointer;
    font-weight: 500;
}

.send-button:disabled {
    background: #ccc;
    cursor: not-allowed;
}

.loading-indicator {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem;
    color: #666;
}

.typing-animation {
    display: flex;
    gap: 2px;
}

.typing-animation span {
    width: 6px;
    height: 6px;
    background: #666;
    border-radius: 50%;
    animation: typing 1.4s infinite ease-in-out;
}

.typing-animation span:nth-child(2) {
    animation-delay: 0.2s;
}

.typing-animation span:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes typing {
    0%, 80%, 100% {
        transform: scale(0.8);
        opacity: 0.5;
    }
    40% {
        transform: scale(1);
        opacity: 1;
    }
}

.error-message {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    background: #ffe6e6;
    color: #d63384;
    border-left: 4px solid #d63384;
    margin: 0.5rem 1rem;
}

.chat-stats {
    border-top: 1px solid #eee;
    padding: 0.5rem 1rem;
    background: #f8f9fa;
    font-size: 0.75rem;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
}

.stat-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.stat-item label {
    font-weight: 500;
    color: #666;
}

.empty-messages {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #666;
    font-style: italic;
}

.btn {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.875rem;
}

.btn-secondary {
    background: #6c757d;
    color: white;
}

.btn-warning {
    background: #ffc107;
    color: #212529;
}

.btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}
```

## Usage Example

```jsx
// App.jsx
import React from 'react';
import AgentChat from './components/AgentChat';
import './styles/AgentChat.css';

function App() {
    const userId = 'user-' + Date.now(); // In real app, get from auth

    return (
        <div className="App">
            <header className="App-header">
                <h1>AI Agent Chat Demo</h1>
            </header>
            <main>
                <AgentChat 
                    userId={userId}
                    className="main-chat"
                />
            </main>
        </div>
    );
}

export default App;
```

## Environment Configuration

```bash
# .env
REACT_APP_API_BASE_URL=http://localhost:8000
```

## Advanced Features

### Context Provider for Global State

```jsx
// contexts/AgentsContext.jsx
import React, { createContext, useContext, useReducer } from 'react';

const AgentsContext = createContext();

const agentsReducer = (state, action) => {
    switch (action.type) {
        case 'SET_GLOBAL_CONTEXT':
            return { ...state, globalContext: action.payload };
        case 'ADD_SESSION':
            return { 
                ...state, 
                sessions: { ...state.sessions, [action.payload.id]: action.payload }
            };
        default:
            return state;
    }
};

export const AgentsProvider = ({ children }) => {
    const [state, dispatch] = useReducer(agentsReducer, {
        globalContext: {},
        sessions: {}
    });

    return (
        <AgentsContext.Provider value={{ state, dispatch }}>
            {children}
        </AgentsContext.Provider>
    );
};

export const useAgentsContext = () => {
    const context = useContext(AgentsContext);
    if (!context) {
        throw new Error('useAgentsContext must be used within AgentsProvider');
    }
    return context;
};
```

This React integration provides a complete, production-ready chat interface with proper state management, error handling, and user experience considerations.