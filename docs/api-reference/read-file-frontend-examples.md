# Read File API - Frontend Usage Examples

**Version:** 2.0.0  
**Base URL:** `http://localhost:8000`  
**Content-Type:** `application/json`

This document provides complete frontend usage examples for Ray's read_file functionality with detailed JSON request/response examples and JavaScript integration code.

## ⚠️ Important: Current Implementation

Ray's read_file functionality is integrated with the **task-based system** and also available as direct directory endpoints.

### Available Endpoints

1. **Task-based (Recommended):** `POST /tasks`
2. **Direct Directory:** `POST /directory/read`

---

## 📋 Table of Contents

1. [Task-Based Read File (Recommended)](#task-based-read-file-recommended)
2. [Direct Directory Read](#direct-directory-read)
3. [JavaScript Integration Examples](#javascript-integration-examples)
4. [Response Format Details](#response-format-details)
5. [Error Handling](#error-handling)
6. [Advanced Usage Patterns](#advanced-usage-patterns)

---

## Task-Based Read File (Recommended)

### Basic File Reading

**Purpose:** Read entire file contents through Ray's task system

**Request Format:**

```json
{
  "task": [
    {
      "action": "read_file",
      "file_path": "./README.md",
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true,
  "self_destruct": true
}
```

**Endpoint:** `POST /tasks`

**JavaScript Example:**

```javascript
async function readFileViaTask(filePath) {
  const response = await fetch("http://localhost:8000/tasks", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      task: [
        {
          action: "read_file",
          file_path: filePath,
          assigned_by: "ray",
        },
      ],
      assigned_by: "ray",
      execute_immediately: true,
      self_destruct: true,
    }),
  });

  const result = await response.json();
  return result;
}

// Usage
readFileViaTask("./config/settings.json").then((result) => {
  console.log("File content:", result.task_results[0].content);
});
```

### Advanced File Reading with Parameters

**Purpose:** Read file with encoding, size limits, and line ranges

**Request Format:**

```json
{
  "task": [
    {
      "action": "read_file",
      "file_path": "./logs/application.log",
      "encoding": "utf-8",
      "max_size": 1048576,
      "start_line": 100,
      "end_line": 200,
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true,
  "self_destruct": true
}
```

**JavaScript Example:**

```javascript
async function readFileAdvanced(options) {
  const {
    filePath,
    encoding = "utf-8",
    maxSize = null,
    startLine = null,
    endLine = null,
  } = options;

  const taskData = {
    action: "read_file",
    file_path: filePath,
    encoding: encoding,
    assigned_by: "ray",
  };

  if (maxSize) taskData.max_size = maxSize;
  if (startLine) taskData.start_line = startLine;
  if (endLine) taskData.end_line = endLine;

  const response = await fetch("http://localhost:8000/tasks", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      task: [taskData],
      assigned_by: "ray",
      execute_immediately: true,
      self_destruct: true,
    }),
  });

  return await response.json();
}

// Usage
readFileAdvanced({
  filePath: "./logs/debug.log",
  startLine: 50,
  endLine: 100,
  maxSize: 512000,
}).then((result) => {
  const fileData = result.task_results[0];
  console.log(`Read ${fileData.lines_count} lines`);
  console.log("Content:", fileData.content);
});
```

---

## Direct Directory Read

### POST /directory/read

**Purpose:** Direct file reading through directory API

**Basic Request:**

```json
{
  "action": "read_file",
  "path": "./config/app.json",
  "assigned_by": "ray"
}
```

**Advanced Request with JSON Parameters:**

```json
{
  "action": "read_file",
  "path": ".",
  "query": "{\"file_path\": \"./logs/error.log\", \"encoding\": \"utf-8\", \"max_size\": 1048576, \"start_line\": 1, \"end_line\": 50}",
  "assigned_by": "ray"
}
```

**JavaScript Example:**

```javascript
async function readFileDirectly(filePath, options = {}) {
  const {
    encoding = "utf-8",
    maxSize = null,
    startLine = null,
    endLine = null,
  } = options;

  let requestBody;

  if (Object.keys(options).length === 0) {
    // Simple request
    requestBody = {
      action: "read_file",
      path: filePath,
      assigned_by: "ray",
    };
  } else {
    // Advanced request with parameters
    const queryParams = {
      file_path: filePath,
      encoding: encoding,
    };

    if (maxSize) queryParams.max_size = maxSize;
    if (startLine) queryParams.start_line = startLine;
    if (endLine) queryParams.end_line = endLine;

    requestBody = {
      action: "read_file",
      path: ".",
      query: JSON.stringify(queryParams),
      assigned_by: "ray",
    };
  }

  const response = await fetch("http://localhost:8000/directory/read", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(requestBody),
  });

  return await response.json();
}

// Usage Examples
readFileDirectly("./README.md").then((result) => {
  const fileInfo = result.search_result.files_found[0];
  console.log("File:", fileInfo.name);
  console.log("Size:", fileInfo.size);
  console.log("Content:", fileInfo.content);
});

readFileDirectly("./logs/app.log", {
  startLine: 100,
  endLine: 150,
  maxSize: 1024000,
}).then((result) => {
  const fileInfo = result.search_result.files_found[0];
  console.log(`Read ${fileInfo.lines_count} lines from ${fileInfo.name}`);
});
```

---

## JavaScript Integration Examples

### Complete File Reader Class

```javascript
class RayFileReader {
  constructor(baseUrl = "http://localhost:8000") {
    this.baseUrl = baseUrl;
  }

  /**
   * Read file using task system (recommended)
   * @param {string} filePath - Path to file
   * @param {Object} options - Reading options
   * @returns {Promise<Object>} File content and metadata
   */
  async readFileTask(filePath, options = {}) {
    const {
      encoding = "utf-8",
      maxSize = null,
      startLine = null,
      endLine = null,
    } = options;

    const taskData = {
      action: "read_file",
      file_path: filePath,
      encoding: encoding,
      assigned_by: "ray",
    };

    if (maxSize) taskData.max_size = maxSize;
    if (startLine) taskData.start_line = startLine;
    if (endLine) taskData.end_line = endLine;

    try {
      const response = await fetch(`${this.baseUrl}/tasks`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          task: [taskData],
          assigned_by: "ray",
          execute_immediately: true,
          self_destruct: true,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();

      if (result.task_results && result.task_results[0]) {
        return {
          success: true,
          content: result.task_results[0].content,
          metadata: {
            name: result.task_results[0].name,
            size: result.task_results[0].size,
            lines: result.task_results[0].lines_count,
            isBinary: result.task_results[0].is_binary,
            encoding: result.task_results[0].encoding_used,
          },
        };
      } else {
        throw new Error("No task results returned");
      }
    } catch (error) {
      return {
        success: false,
        error: error.message,
      };
    }
  }

  /**
   * Read file using direct directory API
   * @param {string} filePath - Path to file
   * @param {Object} options - Reading options
   * @returns {Promise<Object>} File content and metadata
   */
  async readFileDirect(filePath, options = {}) {
    const {
      encoding = "utf-8",
      maxSize = null,
      startLine = null,
      endLine = null,
    } = options;

    const queryParams = {
      file_path: filePath,
      encoding: encoding,
    };

    if (maxSize) queryParams.max_size = maxSize;
    if (startLine) queryParams.start_line = startLine;
    if (endLine) queryParams.end_line = endLine;

    const requestBody = {
      action: "read_file",
      path: ".",
      query: JSON.stringify(queryParams),
      assigned_by: "ray",
    };

    try {
      const response = await fetch(`${this.baseUrl}/directory/read`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();

      if (result.search_result.success && result.search_result.files_found[0]) {
        const fileInfo = result.search_result.files_found[0];
        return {
          success: true,
          content: fileInfo.content,
          metadata: {
            name: fileInfo.name,
            path: fileInfo.path,
            size: fileInfo.size,
            lines: fileInfo.lines_count,
            isBinary: fileInfo.is_binary,
            encoding: fileInfo.encoding_used,
            modified: fileInfo.modified_time,
          },
        };
      } else {
        throw new Error(result.search_result.error_message || "Read failed");
      }
    } catch (error) {
      return {
        success: false,
        error: error.message,
      };
    }
  }

  /**
   * Read file using simplified POST method
   * @param {string} filePath - Path to file
   * @param {Object} options - Reading options
   * @returns {Promise<Object>} File content and metadata
   */
  async readFileSimple(filePath, options = {}) {
    const {
      encoding = "utf-8",
      maxSize = null,
      startLine = null,
      endLine = null,
    } = options;

    const requestBody = {
      action: "read_file",
      path: filePath,
      assigned_by: "ray",
    };

    // If we have advanced options, use query format
    if (maxSize || startLine || endLine || encoding !== "utf-8") {
      const queryParams = {
        file_path: filePath,
        encoding: encoding,
      };

      if (maxSize) queryParams.max_size = maxSize;
      if (startLine) queryParams.start_line = startLine;
      if (endLine) queryParams.end_line = endLine;

      requestBody.path = ".";
      requestBody.query = JSON.stringify(queryParams);
    }

    try {
      const response = await fetch(`${this.baseUrl}/directory/read`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();

      if (result.search_result.success && result.search_result.files_found[0]) {
        const fileInfo = result.search_result.files_found[0];
        return {
          success: true,
          content: fileInfo.content,
          metadata: {
            name: fileInfo.name,
            path: fileInfo.path,
            size: fileInfo.size,
            lines: fileInfo.lines_count,
            isBinary: fileInfo.is_binary,
            encoding: fileInfo.encoding_used,
          },
        };
      } else {
        throw new Error(result.search_result.error_message || "Read failed");
      }
    } catch (error) {
      return {
        success: false,
        error: error.message,
      };
    }
  }
}

// Usage Examples
const fileReader = new RayFileReader();

// Read configuration file
fileReader.readFileTask("./config/app.json").then((result) => {
  if (result.success) {
    const config = JSON.parse(result.content);
    console.log("App config:", config);
    console.log("File size:", result.metadata.size, "bytes");
  } else {
    console.error("Failed to read config:", result.error);
  }
});

// Read log file with line limits
fileReader
  .readFileDirect("./logs/error.log", {
    startLine: 1,
    endLine: 50,
    maxSize: 1024000,
  })
  .then((result) => {
    if (result.success) {
      console.log("Recent errors:");
      console.log(result.content);
      console.log(`Read ${result.metadata.lines} lines`);
    }
  });

// Simple read of small file
fileReader.readFileSimple("./VERSION").then((result) => {
  if (result.success) {
    console.log("Version:", result.content.trim());
  }
});
```

### React Component Example

```javascript
import React, { useState, useCallback } from "react";

const FileReader = () => {
  const [filePath, setFilePath] = useState("./README.md");
  const [content, setContent] = useState("");
  const [metadata, setMetadata] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const readFile = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("http://localhost:8000/tasks", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          task: [
            {
              action: "read_file",
              file_path: filePath,
              assigned_by: "ray",
            },
          ],
          assigned_by: "ray",
          execute_immediately: true,
          self_destruct: true,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const result = await response.json();

      if (result.task_results && result.task_results[0]) {
        const fileData = result.task_results[0];
        setContent(fileData.content);
        setMetadata({
          name: fileData.name,
          size: fileData.size,
          lines: fileData.lines_count,
          isBinary: fileData.is_binary,
        });
      } else {
        throw new Error("No file data returned");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [filePath]);

  return (
    <div className="file-reader">
      <div className="controls">
        <input
          type="text"
          value={filePath}
          onChange={(e) => setFilePath(e.target.value)}
          placeholder="Enter file path..."
          className="file-path-input"
        />
        <button onClick={readFile} disabled={loading}>
          {loading ? "Reading..." : "Read File"}
        </button>
      </div>

      {error && <div className="error">Error: {error}</div>}

      {metadata && (
        <div className="metadata">
          <h3>File Info</h3>
          <p>
            <strong>Name:</strong> {metadata.name}
          </p>
          <p>
            <strong>Size:</strong> {metadata.size} bytes
          </p>
          <p>
            <strong>Lines:</strong> {metadata.lines}
          </p>
          <p>
            <strong>Binary:</strong> {metadata.isBinary ? "Yes" : "No"}
          </p>
        </div>
      )}

      {content && (
        <div className="content">
          <h3>File Content</h3>
          <pre className="file-content">{content}</pre>
        </div>
      )}
    </div>
  );
};

export default FileReader;
```

---

## Response Format Details

### Task-Based Response

```json
{
  "task_id": "uuid-here",
  "status": "completed",
  "task_results": [
    {
      "name": "config.json",
      "path": "/full/path/to/config.json",
      "size": 1024,
      "content": "{\n  \"version\": \"1.0\",\n  \"debug\": true\n}",
      "lines_count": 4,
      "is_binary": false,
      "encoding_used": "utf-8",
      "modified_time": "2025-07-30T10:30:00Z",
      "extension": "json"
    }
  ],
  "execution_time_ms": 15,
  "assigned_by": "ray",
  "timestamp": "2025-07-30T12:00:00Z"
}
```

### Directory API Response

```json
{
  "request_id": "uuid-here",
  "search_result": {
    "search_id": "uuid-here",
    "action": "read_file",
    "query": "read:config.json",
    "timestamp": "2025-07-30T12:00:00Z",
    "files_found": [
      {
        "name": "config.json",
        "path": "/full/path/to/config.json",
        "size": 1024,
        "modified_time": "2025-07-30T10:30:00Z",
        "created_time": "2025-07-29T14:00:00Z",
        "extension": "json",
        "is_directory": false,
        "permissions": "644",
        "content": "{\n  \"version\": \"1.0\",\n  \"debug\": true\n}",
        "lines_count": 4,
        "is_binary": false,
        "encoding_used": "utf-8"
      }
    ],
    "total_results": 1,
    "search_path": ".",
    "execution_time_ms": 15,
    "success": true
  },
  "assigned_by": "ray",
  "timestamp": "2025-07-30T12:00:00Z",
  "summary": {
    "total_files": 1,
    "total_results": 1,
    "action": "read_file",
    "success": true
  }
}
```

---

## Error Handling

### Common Error Responses

#### File Not Found

```json
{
  "search_result": {
    "success": false,
    "error_message": "File not found: /path/to/nonexistent.txt",
    "total_results": 0
  }
}
```

#### File Too Large

```json
{
  "search_result": {
    "success": false,
    "error_message": "File too large: 15728640 bytes (max: 10485760 bytes)",
    "total_results": 0
  }
}
```

#### Permission Denied

```json
{
  "search_result": {
    "success": false,
    "error_message": "Permission denied: /restricted/file.txt",
    "total_results": 0
  }
}
```

#### Binary File Warning

```json
{
  "search_result": {
    "success": true,
    "files_found": [
      {
        "name": "image.jpg",
        "content": "<Binary file - 2048576 bytes>",
        "is_binary": true,
        "lines_count": 0
      }
    ]
  }
}
```

### JavaScript Error Handling Pattern

```javascript
async function safeReadFile(filePath, options = {}) {
  try {
    const response = await fetch("http://localhost:8000/tasks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        task: [
          {
            action: "read_file",
            file_path: filePath,
            ...options,
            assigned_by: "ray",
          },
        ],
        assigned_by: "ray",
        execute_immediately: true,
        self_destruct: true,
      }),
    });

    if (!response.ok) {
      return {
        success: false,
        error: `HTTP ${response.status}: ${response.statusText}`,
        type: "network",
      };
    }

    const result = await response.json();

    if (result.task_results && result.task_results[0]) {
      const fileData = result.task_results[0];

      // Check if file is binary
      if (fileData.is_binary) {
        return {
          success: true,
          warning: "File is binary, content may not display correctly",
          content: fileData.content,
          metadata: fileData,
          type: "binary",
        };
      }

      return {
        success: true,
        content: fileData.content,
        metadata: fileData,
        type: "text",
      };
    } else {
      return {
        success: false,
        error: "No file data returned",
        type: "api",
      };
    }
  } catch (error) {
    return {
      success: false,
      error: error.message,
      type: "exception",
    };
  }
}

// Usage with comprehensive error handling
safeReadFile("./config.json").then((result) => {
  if (result.success) {
    if (result.type === "binary") {
      console.warn(result.warning);
      console.log("Binary file size:", result.metadata.size);
    } else {
      console.log("File content:", result.content);
      console.log("Lines:", result.metadata.lines_count);
    }
  } else {
    switch (result.type) {
      case "network":
        console.error("Network error:", result.error);
        break;
      case "api":
        console.error("API error:", result.error);
        break;
      case "exception":
        console.error("Unexpected error:", result.error);
        break;
    }
  }
});
```

---

## Advanced Usage Patterns

### Reading Multiple Files

```javascript
async function readMultipleFiles(filePaths) {
  const tasks = filePaths.map((filePath) => ({
    action: "read_file",
    file_path: filePath,
    assigned_by: "ray",
  }));

  const response = await fetch("http://localhost:8000/tasks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      task: tasks,
      assigned_by: "ray",
      execute_immediately: true,
      self_destruct: true,
    }),
  });

  const result = await response.json();
  return result.task_results || [];
}

// Usage
readMultipleFiles(["./config.json", "./package.json", "./README.md"]).then(
  (files) => {
    files.forEach((file) => {
      console.log(`${file.name}: ${file.size} bytes`);
    });
  }
);
```

### Reading Large Files in Chunks

```javascript
async function readFileInChunks(filePath, chunkSize = 100) {
  // First, get file info to determine total lines
  const infoResponse = await fetch("http://localhost:8000/directory/read", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      action: "get_file_info",
      path: filePath,
      assigned_by: "ray",
    }),
  });
  const info = await infoResponse.json();

  if (!info.search_result.success) {
    throw new Error("File not found");
  }

  // Read first chunk to get line count
  const firstChunk = await fetch("http://localhost:8000/tasks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      task: [
        {
          action: "read_file",
          file_path: filePath,
          end_line: chunkSize,
          assigned_by: "ray",
        },
      ],
      assigned_by: "ray",
      execute_immediately: true,
      self_destruct: true,
    }),
  });

  const firstResult = await firstChunk.json();
  const totalLines = firstResult.task_results[0].lines_count;

  const chunks = [];
  for (let start = 1; start <= totalLines; start += chunkSize) {
    const end = Math.min(start + chunkSize - 1, totalLines);

    const chunkResponse = await fetch("http://localhost:8000/tasks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        task: [
          {
            action: "read_file",
            file_path: filePath,
            start_line: start,
            end_line: end,
            assigned_by: "ray",
          },
        ],
        assigned_by: "ray",
        execute_immediately: true,
        self_destruct: true,
      }),
    });

    const chunkResult = await chunkResponse.json();
    chunks.push({
      start: start,
      end: end,
      content: chunkResult.task_results[0].content,
    });
  }

  return chunks;
}

// Usage
readFileInChunks("./logs/large_file.log", 50).then((chunks) => {
  console.log(`File read in ${chunks.length} chunks`);
  chunks.forEach((chunk, index) => {
    console.log(`Chunk ${index + 1}: lines ${chunk.start}-${chunk.end}`);
  });
});
```

### Configuration File Manager

```javascript
class ConfigManager {
  constructor(baseUrl = "http://localhost:8000") {
    this.baseUrl = baseUrl;
  }

  async readConfig(configPath) {
    const response = await fetch(`${this.baseUrl}/tasks`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        task: [
          {
            action: "read_file",
            file_path: configPath,
            assigned_by: "ray",
          },
        ],
        assigned_by: "ray",
        execute_immediately: true,
        self_destruct: true,
      }),
    });

    const result = await response.json();

    if (result.task_results && result.task_results[0]) {
      const fileData = result.task_results[0];

      try {
        // Try to parse as JSON
        const config = JSON.parse(fileData.content);
        return {
          success: true,
          config: config,
          metadata: {
            path: configPath,
            size: fileData.size,
            modified: fileData.modified_time,
          },
        };
      } catch (parseError) {
        return {
          success: false,
          error: "Invalid JSON format",
          rawContent: fileData.content,
        };
      }
    } else {
      return {
        success: false,
        error: "Failed to read config file",
      };
    }
  }

  async readMultipleConfigs(configPaths) {
    const results = {};

    for (const path of configPaths) {
      results[path] = await this.readConfig(path);
    }

    return results;
  }
}

// Usage
const configManager = new ConfigManager();

configManager.readConfig("./config/app.json").then((result) => {
  if (result.success) {
    console.log("App config:", result.config);
    console.log("Last modified:", result.metadata.modified);
  } else {
    console.error("Config error:", result.error);
  }
});

configManager
  .readMultipleConfigs([
    "./config/app.json",
    "./config/database.json",
    "./config/logging.json",
  ])
  .then((configs) => {
    Object.entries(configs).forEach(([path, result]) => {
      if (result.success) {
        console.log(`${path}: loaded successfully`);
      } else {
        console.error(`${path}: ${result.error}`);
      }
    });
  });
```

---

**This document provides complete frontend integration examples for Ray's read_file functionality with detailed JSON requests, JavaScript code, and error handling patterns.** 📖
