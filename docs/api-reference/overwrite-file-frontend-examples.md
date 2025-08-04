# Overwrite File Tool - Frontend Examples

## Overview

The `overwrite_file` tool allows users to write content to files through Ray's consciousness system. This tool integrates with the task system and provides comprehensive file manipulation capabilities.

## Frontend Integration Examples

### 1. JavaScript/Web Frontend Example

```javascript
// Frontend function to send overwrite file task to Ray
async function rayOverwriteFile(filePath, content, options = {}) {
    const taskData = {
        task: [
            {
                action: "overwrite_file",
                file_path: filePath,
                content: content,
                backup_existing: options.backup || false,
                create_directories: options.createDirs || true
            }
        ],
        assigned_by: "user",
        execute_immediately: true
    };

    try {
        const response = await fetch('/task/batch', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(taskData)
        });

        const result = await response.json();
        
        if (result.status === 'success') {
            console.log('✅ File written successfully');
            return result.created_tasks[0].task.execution_result;
        } else {
            console.error('❌ File write failed:', result.failed_tasks);
            return null;
        }
    } catch (error) {
        console.error('❌ Request failed:', error);
        return null;
    }
}

// Usage examples
async function examples() {
    // Example 1: Save user notes
    await rayOverwriteFile(
        './user_notes/my_thoughts.md',
        '# My Thoughts\n\nThis is what I learned today...',
        { backup: true, createDirs: true }
    );

    // Example 2: Save configuration
    const config = JSON.stringify({ theme: 'dark', language: 'en' }, null, 2);
    await rayOverwriteFile('./config/user_settings.json', config);

    // Example 3: Export data
    const exportData = 'Name,Email,Date\nJohn,john@email.com,2025-02-03';
    await rayOverwriteFile('./exports/user_data.csv', exportData);
}
```

### 2. React Component Example

```jsx
import React, { useState } from 'react';

const FileWriterComponent = () => {
    const [filePath, setFilePath] = useState('./output/user_file.txt');
    const [content, setContent] = useState('');
    const [backupEnabled, setBackupEnabled] = useState(true);
    const [status, setStatus] = useState('');
    const [loading, setLoading] = useState(false);

    const handleOverwriteFile = async () => {
        setLoading(true);
        setStatus('Writing file...');

        const taskData = {
            task: [
                {
                    action: "overwrite_file",
                    file_path: filePath,
                    content: content,
                    backup_existing: backupEnabled,
                    create_directories: true
                }
            ],
            assigned_by: "user",
            execute_immediately: true
        };

        try {
            const response = await fetch('/task/batch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(taskData)
            });

            const result = await response.json();

            if (result.status === 'success') {
                const executionResult = result.created_tasks[0].task.execution_result;
                if (executionResult.executed && executionResult.results.success) {
                    setStatus(`✅ File written successfully! Size: ${executionResult.results.file_size} bytes`);
                } else {
                    setStatus(`❌ Write failed: ${executionResult.results.error_message}`);
                }
            } else {
                setStatus(`❌ Task failed: ${result.failed_tasks[0]?.error}`);
            }
        } catch (error) {
            setStatus(`❌ Request failed: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="file-writer-component">
            <h3>Ray File Writer</h3>
            
            <div className="form-group">
                <label>File Path:</label>
                <input
                    type="text"
                    value={filePath}
                    onChange={(e) => setFilePath(e.target.value)}
                    placeholder="./output/my_file.txt"
                />
            </div>

            <div className="form-group">
                <label>Content:</label>
                <textarea
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    placeholder="Enter file content here..."
                    rows={10}
                />
            </div>

            <div className="form-group">
                <label>
                    <input
                        type="checkbox"
                        checked={backupEnabled}
                        onChange={(e) => setBackupEnabled(e.target.checked)}
                    />
                    Create backup of existing file
                </label>
            </div>

            <button 
                onClick={handleOverwriteFile} 
                disabled={loading || !content.trim()}
            >
                {loading ? 'Writing...' : 'Write File'}
            </button>

            {status && <div className="status-message">{status}</div>}
        </div>
    );
};

export default FileWriterComponent;
```

### 3. Python Frontend Example

```python
import requests
import json

class RayFileWriter:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def overwrite_file(self, file_path, content, backup_existing=False, create_directories=True):
        """
        Send overwrite file task to Ray through the task system.
        """
        task_data = {
            "task": [
                {
                    "action": "overwrite_file",
                    "file_path": file_path,
                    "content": content,
                    "backup_existing": backup_existing,
                    "create_directories": create_directories
                }
            ],
            "assigned_by": "user",
            "execute_immediately": True
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/task/batch",
                json=task_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result["status"] == "success":
                    execution_result = result["created_tasks"][0]["task"]["execution_result"]
                    if execution_result["executed"] and execution_result["results"]["success"]:
                        print(f"✅ File written successfully!")
                        print(f"   Path: {execution_result['results']['file_path']}")
                        print(f"   Size: {execution_result['results']['file_size']} bytes")
                        return execution_result["results"]
                    else:
                        print(f"❌ Write failed: {execution_result['results']['error_message']}")
                        return None
                else:
                    print(f"❌ Task failed: {result['failed_tasks']}")
                    return None
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            return None
    
    def batch_write_files(self, files_data):
        """
        Write multiple files in a single batch task.
        
        Args:
            files_data: List of dicts with 'file_path', 'content', and optional settings
        """
        tasks = []
        for file_data in files_data:
            tasks.append({
                "action": "overwrite_file",
                "file_path": file_data["file_path"],
                "content": file_data["content"],
                "backup_existing": file_data.get("backup_existing", False),
                "create_directories": file_data.get("create_directories", True)
            })
        
        task_data = {
            "task": tasks,
            "assigned_by": "user",
            "execute_immediately": True
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/task/batch",
                json=task_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"📁 Batch write completed:")
                print(f"   Created: {len(result['created_tasks'])}")
                print(f"   Failed: {len(result['failed_tasks'])}")
                print(f"   Status: {result['status']}")
                return result
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            return None

# Usage examples
def main():
    writer = RayFileWriter()
    
    # Example 1: Single file write
    writer.overwrite_file(
        "./user_outputs/notes.md",
        "# My Notes\n\nThis is a test note from Python frontend.",
        backup_existing=True
    )
    
    # Example 2: Batch file write
    files_to_write = [
        {
            "file_path": "./user_outputs/file1.txt",
            "content": "Content for file 1",
            "backup_existing": True
        },
        {
            "file_path": "./user_outputs/file2.txt", 
            "content": "Content for file 2",
            "create_directories": True
        }
    ]
    
    writer.batch_write_files(files_to_write)

if __name__ == "__main__":
    main()
```

### 4. HTML Form Example

```html
<!DOCTYPE html>
<html>
<head>
    <title>Ray File Writer</title>
    <style>
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        button:disabled { background: #ccc; cursor: not-allowed; }
        .status { margin-top: 15px; padding: 10px; border-radius: 4px; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Ray File Writer Interface</h1>
        
        <form id="fileWriterForm">
            <div class="form-group">
                <label for="filePath">File Path:</label>
                <input type="text" id="filePath" value="./user_outputs/my_file.txt" required>
            </div>
            
            <div class="form-group">
                <label for="content">Content:</label>
                <textarea id="content" rows="10" placeholder="Enter your file content here..." required></textarea>
            </div>
            
            <div class="form-group">
                <label>
                    <input type="checkbox" id="backupEnabled" checked>
                    Create backup of existing file
                </label>
            </div>
            
            <div class="form-group">
                <label>
                    <input type="checkbox" id="createDirs" checked>
                    Create directories if they don't exist
                </label>
            </div>
            
            <button type="submit" id="submitBtn">Write File</button>
        </form>
        
        <div id="status" class="status" style="display: none;"></div>
    </div>

    <script>
        document.getElementById('fileWriterForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const submitBtn = document.getElementById('submitBtn');
            const statusDiv = document.getElementById('status');
            
            // Get form values
            const filePath = document.getElementById('filePath').value;
            const content = document.getElementById('content').value;
            const backupEnabled = document.getElementById('backupEnabled').checked;
            const createDirs = document.getElementById('createDirs').checked;
            
            // Disable button and show loading
            submitBtn.disabled = true;
            submitBtn.textContent = 'Writing...';
            statusDiv.style.display = 'none';
            
            const taskData = {
                task: [
                    {
                        action: "overwrite_file",
                        file_path: filePath,
                        content: content,
                        backup_existing: backupEnabled,
                        create_directories: createDirs
                    }
                ],
                assigned_by: "user",
                execute_immediately: true
            };
            
            try {
                const response = await fetch('/task/batch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(taskData)
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    const executionResult = result.created_tasks[0].task.execution_result;
                    if (executionResult.executed && executionResult.results.success) {
                        statusDiv.className = 'status success';
                        statusDiv.innerHTML = `
                            ✅ File written successfully!<br>
                            📁 Path: ${executionResult.results.file_path}<br>
                            📊 Size: ${executionResult.results.file_size} bytes<br>
                            ⏱️ Time: ${executionResult.results.execution_time_ms}ms
                        `;
                    } else {
                        statusDiv.className = 'status error';
                        statusDiv.textContent = `❌ Write failed: ${executionResult.results.error_message}`;
                    }
                } else {
                    statusDiv.className = 'status error';
                    statusDiv.textContent = `❌ Task failed: ${result.failed_tasks[0]?.error}`;
                }
            } catch (error) {
                statusDiv.className = 'status error';
                statusDiv.textContent = `❌ Request failed: ${error.message}`;
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Write File';
                statusDiv.style.display = 'block';
            }
        });
    </script>
</body>
</html>
```

## API Endpoints for Frontend Integration

### Primary Endpoint (Recommended)
- **POST** `/task/batch` - Send file operations through Ray's task system

### Direct Endpoints (Alternative)
- **POST** `/file_ops/overwrite` - Direct file overwrite
- **POST** `/file_ops/read` - Read files back
- **GET** `/file_ops/status` - Check file operations status

## Task System Integration

All frontend examples use the **task system** (`/task/batch`) because:

1. **Consistency**: Same interface as all other Ray tools
2. **Immediate Execution**: `execute_immediately: true` provides instant results
3. **Batch Operations**: Multiple files can be written in one request
4. **Comprehensive Logging**: All operations are logged through Ray's consciousness system
5. **Error Handling**: Standardized error reporting across all tools

## Frontend Best Practices

1. **Always use the task system** (`/task/batch`) for consistency
2. **Enable immediate execution** for real-time feedback
3. **Handle both success and error cases** in your UI
4. **Show progress indicators** during file operations
5. **Validate file paths and content** before sending
6. **Use backup options** for important files
7. **Provide clear status feedback** to users

## Common Use Cases

- **User Notes**: Save user-generated content
- **Configuration**: Store user preferences and settings
- **Data Export**: Export user data to files
- **Templates**: Save and manage file templates
- **Logs**: Create user activity logs
- **Reports**: Generate and save reports

This integration ensures that the `overwrite_file` tool works seamlessly with Ray's consciousness system while providing users with intuitive frontend interfaces.