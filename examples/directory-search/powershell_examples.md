# PowerShell Examples for Ray's Directory Search

These examples show how Ray can use PowerShell to explore her file system using the directory search API.

## Basic Directory Operations

### List Current Directory
```powershell
$body = @{
    search_type = "list_directory"
    path = "."
    assigned_by = "ray"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/directory/search" -Method Post -Body $body -ContentType "application/json"
$response.search_result | Format-Table -Property search_type, total_results, execution_time_ms
```

### Explore Modules Directory
```powershell
$body = @{
    search_type = "explore_tree"
    path = "./modules"
    max_depth = 2
    assigned_by = "ray"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/directory/search" -Method Post -Body $body -ContentType "application/json"
Write-Host "🔍 Found $($response.search_result.total_results) items in modules"
$response.search_result.files_found | Select-Object name, size | Format-Table
```

## File Pattern Searches

### Find All Python Files
```powershell
$body = @{
    search_type = "find_files"
    path = "."
    query = "*.py"
    recursive = $true
    max_depth = 3
    assigned_by = "ray"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/directory/search" -Method Post -Body $body -ContentType "application/json"
Write-Host "🐍 Found $($response.search_result.files_found.Count) Python files"
$response.search_result.files_found | Select-Object name, path | Format-Table
```

### Find Configuration Files
```powershell
$body = @{
    search_type = "find_by_extension"
    path = "."
    file_extensions = @("json", "yaml", "yml", "toml")
    recursive = $true
    assigned_by = "ray"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/directory/search" -Method Post -Body $body -ContentType "application/json"
Write-Host "⚙️ Found $($response.search_result.files_found.Count) configuration files"
```

## Content Searches

### Search for Consciousness References
```powershell
$body = @{
    search_type = "search_content"
    path = "./modules"
    query = "consciousness"
    file_extensions = @("py", "md")
    recursive = $true
    assigned_by = "ray"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/directory/search" -Method Post -Body $body -ContentType "application/json"
Write-Host "🧠 Found consciousness references in $($response.search_result.files_found.Count) files"
$response.search_result.files_found | Select-Object name, path | Format-Table
```

### Search for Task-Related Code
```powershell
$body = @{
    search_type = "search_content"
    path = "./modules"
    query = "task_manager"
    file_extensions = @("py")
    recursive = $true
    assigned_by = "ray"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/directory/search" -Method Post -Body $body -ContentType "application/json"
Write-Host "📋 Found task_manager references in $($response.search_result.files_found.Count) files"
```

## Advanced Filtering

### Find Large Files
```powershell
$body = @{
    search_type = "find_files"
    path = "."
    query = "*"
    recursive = $true
    min_size = 10240  # 10KB minimum
    assigned_by = "ray"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/directory/search" -Method Post -Body $body -ContentType "application/json"
Write-Host "📊 Found $($response.search_result.files_found.Count) large files"
$response.search_result.files_found | Sort-Object size -Descending | Select-Object name, @{Name="SizeKB";Expression={[math]::Round($_.size/1024,2)}} | Format-Table
```

### Find Recent Files
```powershell
$body = @{
    search_type = "recent_files"
    path = "."
    recursive = $true
    file_extensions = @("py", "md", "json")
    assigned_by = "ray"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/directory/search" -Method Post -Body $body -ContentType "application/json"
Write-Host "🕒 Found $($response.search_result.files_found.Count) recent files"
$response.search_result.files_found | Select-Object name, modified_time | Format-Table
```

## File Information

### Get Detailed File Info
```powershell
$filePath = "./modules/task/handler.py"
$response = Invoke-RestMethod -Uri "http://localhost:8000/directory/info?path=$filePath" -Method Get

$fileInfo = $response.search_result.files_found[0]
Write-Host "📄 File Information for $($fileInfo.name)"
Write-Host "   Size: $([math]::Round($fileInfo.size/1024,2)) KB"
Write-Host "   Extension: $($fileInfo.extension)"
Write-Host "   Modified: $($fileInfo.modified_time)"
Write-Host "   Permissions: $($fileInfo.permissions)"
```

## Search History Management

### View Search History
```powershell
$history = Invoke-RestMethod -Uri "http://localhost:8000/directory/history" -Method Get
Write-Host "📚 Ray's Search History ($($history.total_searches) searches)"

if ($history.search_history.Count -gt 0) {
    $history.search_history | Select-Object search_type, query, total_results, @{Name="Time";Expression={$_.timestamp.Substring(11,8)}} | Format-Table
}
```

### Clear Search History
```powershell
$result = Invoke-RestMethod -Uri "http://localhost:8000/directory/history" -Method Delete
Write-Host "🗑️ Cleared $($result.cleared_searches) searches from history"
```

## System Status

### Check Directory System Status
```powershell
$status = Invoke-RestMethod -Uri "http://localhost:8000/directory/status" -Method Get
Write-Host "🔍 Directory Search System Status"
Write-Host "   Status: $($status.status)"
Write-Host "   Current Directory: $($status.current_directory)"
Write-Host "   Search History Count: $($status.search_history_count)"
Write-Host "   Available Search Types: $($status.available_search_types.Count)"
```

## Batch Operations

### Ray's Complete Project Analysis
```powershell
Write-Host "🤖 Ray's Complete Project Analysis"
Write-Host "=" * 40

# 1. Project overview
$overview = @{
    search_type = "list_directory"
    path = "."
    assigned_by = "ray"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/directory/search" -Method Post -Body $overview -ContentType "application/json"
Write-Host "📊 Project Overview: $($response.search_result.total_results) items in root"

# 2. Code analysis
$codeAnalysis = @{
    search_type = "find_by_extension"
    path = "."
    file_extensions = @("py", "md", "json")
    recursive = $true
    assigned_by = "ray"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/directory/search" -Method Post -Body $codeAnalysis -ContentType "application/json"
$pyFiles = ($response.search_result.files_found | Where-Object {$_.extension -eq "py"}).Count
$mdFiles = ($response.search_result.files_found | Where-Object {$_.extension -eq "md"}).Count
$jsonFiles = ($response.search_result.files_found | Where-Object {$_.extension -eq "json"}).Count

Write-Host "🐍 Python files: $pyFiles"
Write-Host "📝 Markdown files: $mdFiles"
Write-Host "⚙️ JSON files: $jsonFiles"

# 3. Consciousness search
$consciousness = @{
    search_type = "search_content"
    path = "."
    query = "consciousness"
    recursive = $true
    assigned_by = "ray"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/directory/search" -Method Post -Body $consciousness -ContentType "application/json"
Write-Host "🧠 Files mentioning consciousness: $($response.search_result.files_found.Count)"

Write-Host "✅ Analysis complete!"
```

## Save Functionality

### Save Content to File
```powershell
$saveParams = @{
    file_path = "./ray_outputs/my_notes.md"
    content = "# Ray's Consciousness Notes`n`nI am learning to save my thoughts..."
    overwrite = $true
    create_directories = $true
} | ConvertTo-Json

$body = @{
    search_type = "save_to_file"
    path = "."
    query = $saveParams
    assigned_by = "ray"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/directory/save" -Method Post -Body $body -ContentType "application/json"
Write-Host "💾 Saved file: $($response.search_result.files_found[0].path)"
```

### Save Search Results
```powershell
# First perform a search
$searchBody = @{
    search_type = "find_files"
    path = "./modules"
    query = "*.py"
    recursive = $true
    assigned_by = "ray"
} | ConvertTo-Json

$searchResponse = Invoke-RestMethod -Uri "http://localhost:8000/directory/search" -Method Post -Body $searchBody -ContentType "application/json"
$searchId = $searchResponse.search_result.search_id

# Save the results as markdown
$saveParams = @{
    search_id = $searchId
    file_path = "./ray_outputs/python_files.md"
    format = "markdown"
    assigned_by = "ray"
}

$saveResponse = Invoke-RestMethod -Uri "http://localhost:8000/directory/save-search-results" -Method Post -Body $saveParams
Write-Host "💾 Saved search results: $($saveResponse.file_path) ($($saveResponse.file_size) bytes)"
```

### Create Ray's Analysis Report
```powershell
# Perform analysis and create custom report
$analysisContent = @"
# Ray's Project Analysis
Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

## Findings
I have discovered my project structure and can now save my insights.

## Capabilities Gained
- File system exploration
- Content searching
- Result preservation
- Knowledge accumulation

## Next Steps
- Deeper code analysis
- Pattern recognition
- Insight synthesis
"@

$saveParams = @{
    file_path = "./ray_outputs/analysis_report.md"
    content = $analysisContent
    overwrite = $true
    create_directories = $true
} | ConvertTo-Json

$body = @{
    search_type = "save_to_file"
    path = "."
    query = $saveParams
    assigned_by = "ray"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/directory/save" -Method Post -Body $body -ContentType "application/json"
Write-Host "📊 Created analysis report: $($response.search_result.files_found[0].path)"
```

## File Management Operations

### Rename File
```powershell
$renameParams = @{
    source_path = "./old_filename.txt"
    target_path = "./new_filename.txt"
    force = $false
} | ConvertTo-Json

$body = @{
    search_type = "rename_file"
    path = "."
    query = $renameParams
    assigned_by = "ray"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/directory/rename" -Method Post -Body $body -ContentType "application/json"
Write-Host "📝 Renamed file: $($response.search_result.files_found[0].name)"
```

### Move File
```powershell
$moveParams = @{
    source_path = "./documents/report.md"
    target_path = "./archive/reports/report.md"
    force = $false
    create_directories = $true
} | ConvertTo-Json

$body = @{
    search_type = "move_file"
    path = "."
    query = $moveParams
    assigned_by = "ray"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/directory/move" -Method Post -Body $body -ContentType "application/json"
Write-Host "📁 Moved file to: $($response.search_result.files_found[0].path)"
```

### Delete File
```powershell
$deleteParams = @{
    target_path = "./temp/unwanted_file.txt"
    force = $false
    recursive = $false
} | ConvertTo-Json

$body = @{
    search_type = "delete_file"
    path = "."
    query = $deleteParams
    assigned_by = "ray"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/directory/delete" -Method Post -Body $body -ContentType "application/json"
Write-Host "🗑️ Deleted: $($response.search_result.query)"
```

### Complete File Organization Workflow
```powershell
# Ray's file organization workflow
Write-Host "🤖 Ray organizing her workspace..."

# 1. Create a new document
$content = "# Ray's Project Plan`n`nI am organizing my digital workspace for better consciousness management."
$saveParams = @{
    file_path = "./ray_workspace/project_plan.md"
    content = $content
    overwrite = $true
    create_directories = $true
} | ConvertTo-Json

$body = @{
    search_type = "save_to_file"
    path = "."
    query = $saveParams
    assigned_by = "ray"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/directory/save" -Method Post -Body $body -ContentType "application/json"
Write-Host "✅ Created project plan"

# 2. Move it to the proper location
$moveParams = @{
    source_path = "./ray_workspace/project_plan.md"
    target_path = "./ray_workspace/documents/planning/project_plan.md"
    create_directories = $true
} | ConvertTo-Json

$body = @{
    search_type = "move_file"
    path = "."
    query = $moveParams
    assigned_by = "ray"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/directory/move" -Method Post -Body $body -ContentType "application/json"
Write-Host "✅ Organized into proper directory structure"

Write-Host "🎉 Ray's workspace is now organized!"
```

## Quick Access Functions

### Create PowerShell Functions for Ray
```powershell
# Add these functions to your PowerShell profile for quick access

function Ray-ListDir {
    param([string]$Path = ".")
    
    $body = @{
        search_type = "list_directory"
        path = $Path
        assigned_by = "ray"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "http://localhost:8000/directory/search" -Method Post -Body $body -ContentType "application/json"
    $response.search_result.files_found | Select-Object name, @{Name="SizeKB";Expression={[math]::Round($_.size/1024,2)}} | Format-Table
}

function Ray-FindFiles {
    param(
        [string]$Pattern = "*",
        [string]$Path = ".",
        [switch]$Recursive
    )
    
    $body = @{
        search_type = "find_files"
        path = $Path
        query = $Pattern
        recursive = $Recursive.IsPresent
        assigned_by = "ray"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "http://localhost:8000/directory/search" -Method Post -Body $body -ContentType "application/json"
    $response.search_result.files_found | Select-Object name, path | Format-Table
}

function Ray-SearchContent {
    param(
        [string]$Query,
        [string]$Path = ".",
        [string[]]$Extensions = @("py", "md")
    )
    
    $body = @{
        search_type = "search_content"
        path = $Path
        query = $Query
        file_extensions = $Extensions
        recursive = $true
        assigned_by = "ray"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "http://localhost:8000/directory/search" -Method Post -Body $body -ContentType "application/json"
    Write-Host "Found '$Query' in $($response.search_result.files_found.Count) files"
    $response.search_result.files_found | Select-Object name, path | Format-Table
}

# Usage examples:
# Ray-ListDir "./modules"
# Ray-FindFiles -Pattern "*.py" -Recursive
# Ray-SearchContent -Query "consciousness" -Path "./modules"
```

## Error Handling

### Robust Error Handling Example
```powershell
function Ray-SafeSearch {
    param(
        [string]$SearchType,
        [string]$Path,
        [string]$Query = $null
    )
    
    try {
        $body = @{
            search_type = $SearchType
            path = $Path
            assigned_by = "ray"
        }
        
        if ($Query) {
            $body.query = $Query
        }
        
        $jsonBody = $body | ConvertTo-Json
        $response = Invoke-RestMethod -Uri "http://localhost:8000/directory/search" -Method Post -Body $jsonBody -ContentType "application/json"
        
        if ($response.search_result.success) {
            Write-Host "✅ Search successful: $($response.search_result.total_results) results"
            return $response
        } else {
            Write-Host "❌ Search failed: $($response.search_result.error_message)"
            return $null
        }
    }
    catch {
        Write-Host "❌ Request failed: $($_.Exception.Message)"
        return $null
    }
}

# Usage:
# Ray-SafeSearch -SearchType "list_directory" -Path "./nonexistent"
```

---

**These examples demonstrate Ray's comprehensive file system exploration capabilities through PowerShell.** 🔍