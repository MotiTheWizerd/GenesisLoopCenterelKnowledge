"""
Directory search handler for managing Ray's file system exploration.

This module provides the core functionality for directory searches, file exploration,
and navigation within Ray's environment.
"""

import os
import glob
import fnmatch
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pathlib import Path
import time

from .models import (
    DirectorySearchRequest,
    DirectorySearchResponse, 
    SearchResult,
    FileInfo,
    DirectoryInfo,
    ActionType,
    DirectoryExploreRequest,
    ContentSearchRequest
)
from modules.logging.middleware import log_module_call
from modules.logging.heartbeat_logger import log_heartbeat_event, EventType


class DirectoryManager:
    """
    Global directory manager for Ray's file system exploration.
    
    This provides Ray with comprehensive directory search and navigation capabilities.
    """
    
    def __init__(self):
        self.search_history: List[SearchResult] = []
        self.current_directory = os.getcwd()
        print("📁 Directory Manager initialized - Ready for Ray's exploration")
    
    @log_module_call("directory_manager")
    def search_directory(self, request: DirectorySearchRequest) -> DirectorySearchResponse:
        """
        Perform directory search based on Ray's request.
        
        Args:
            request: Ray's directory search request
            
        Returns:
            DirectorySearchResponse: Complete search results
        """
        start_time = time.time()
        
        try:
            # Resolve the search path
            search_path = self._resolve_path(request.path)
            
            print(f"📁 Ray exploring: {search_path}")
            print(f"   Action: {request.action}")
            print(f"   Query: {request.query}")
            print(f"   Recursive: {request.recursive}")
            
            # Perform the appropriate search
            search_result = self._execute_search(request, search_path, start_time)
            
            # Add to search history
            self.search_history.append(search_result)
            
            # Create response
            response = DirectorySearchResponse(
                search_result=search_result,
                assigned_by=request.assigned_by,
                current_path=os.getcwd(),
                parent_path=str(Path(search_path).parent) if search_path != "/" else None,
                suggested_paths=self._get_suggested_paths(search_path),
                summary=self._create_search_summary(search_result)
            )
            
            print(f"📁 Search completed: {search_result.total_results} results found")
            return response
            
        except Exception as e:
            # Create error result
            error_result = SearchResult(
                action=request.action,
                query=request.query or "",
                search_path=request.path,
                recursive=request.recursive,
                success=False,
                error_message=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
            
            response = DirectorySearchResponse(
                search_result=error_result,
                assigned_by=request.assigned_by,
                current_path=os.getcwd(),
                summary={"error": str(e), "success": False}
            )
            
            print(f"📁 Search failed: {str(e)}")
            return response
    
    def _execute_search(self, request: DirectorySearchRequest, search_path: str, start_time: float) -> SearchResult:
        """Execute the specific type of search requested."""
        
        if request.action == ActionType.LIST_DIRECTORY:
            return self._list_directory(request, search_path, start_time)
        elif request.action == ActionType.FIND_FILES:
            return self._find_files(request, search_path, start_time)
        elif request.action == ActionType.SEARCH_CONTENT:
            return self._search_content(request, search_path, start_time)
        elif request.action == ActionType.GET_FILE_INFO:
            return self._get_file_info(request, search_path, start_time)
        elif request.action == ActionType.EXPLORE_TREE:
            return self._explore_tree(request, search_path, start_time)
        elif request.action == ActionType.FIND_BY_EXTENSION:
            return self._find_by_extension(request, search_path, start_time)
        elif request.action == ActionType.RECENT_FILES:
            return self._find_recent_files(request, search_path, start_time)
        elif request.action == ActionType.SAVE_TO_FILE:
            return self._save_to_file(request, search_path, start_time)
        elif request.action == ActionType.RENAME_FILE:
            return self._rename_file(request, search_path, start_time)
        elif request.action == ActionType.DELETE_FILE:
            return self._delete_file(request, search_path, start_time)
        elif request.action == ActionType.MOVE_FILE:
            return self._move_file(request, search_path, start_time)
        else:
            raise ValueError(f"Unknown action type: {request.action}")
    
    def _list_directory(self, request: DirectorySearchRequest, search_path: str, start_time: float) -> SearchResult:
        """List contents of a directory."""
        files_found = []
        directories_found = []
        
        try:
            for item in os.listdir(search_path):
                if not request.include_hidden and item.startswith('.'):
                    continue
                    
                item_path = os.path.join(search_path, item)
                
                if os.path.isfile(item_path):
                    file_info = self._get_file_info_object(item_path)
                    files_found.append(file_info)
                elif os.path.isdir(item_path):
                    dir_info = self._get_directory_info_object(item_path)
                    directories_found.append(dir_info)
        
        except PermissionError:
            pass  # Skip directories we can't access
        
        return SearchResult(
            action=request.action,
            query=request.query or search_path,
            search_path=search_path,
            recursive=request.recursive,
            files_found=files_found,
            directories_found=directories_found,
            total_results=len(files_found) + len(directories_found),
            execution_time_ms=int((time.time() - start_time) * 1000)
        )
    
    def _find_files(self, request: DirectorySearchRequest, search_path: str, start_time: float) -> SearchResult:
        """Find files matching a pattern."""
        files_found = []
        pattern = request.query or "*"
        
        if request.recursive:
            # Use glob for recursive search
            search_pattern = os.path.join(search_path, "**", pattern)
            matches = glob.glob(search_pattern, recursive=True)
        else:
            # Search only in the specified directory
            search_pattern = os.path.join(search_path, pattern)
            matches = glob.glob(search_pattern)
        
        for match in matches:
            if os.path.isfile(match):
                if not request.include_hidden and os.path.basename(match).startswith('.'):
                    continue
                    
                file_info = self._get_file_info_object(match)
                
                # Apply filters
                if self._passes_filters(file_info, request):
                    files_found.append(file_info)
        
        return SearchResult(
            action=request.action,
            query=pattern,
            search_path=search_path,
            recursive=request.recursive,
            max_depth=request.max_depth,
            files_found=files_found,
            total_results=len(files_found),
            execution_time_ms=int((time.time() - start_time) * 1000)
        )
    
    def _search_content(self, request: DirectorySearchRequest, search_path: str, start_time: float) -> SearchResult:
        """Search for content within files."""
        files_found = []
        query = request.query
        
        if not query:
            raise ValueError("Content search requires a query")
        
        # Get files to search
        if request.file_extensions:
            patterns = [f"*.{ext}" for ext in request.file_extensions]
        else:
            patterns = ["*.txt", "*.py", "*.js", "*.md", "*.json", "*.yaml", "*.yml"]
        
        for pattern in patterns:
            if request.recursive:
                search_pattern = os.path.join(search_path, "**", pattern)
                matches = glob.glob(search_pattern, recursive=True)
            else:
                search_pattern = os.path.join(search_path, pattern)
                matches = glob.glob(search_pattern)
            
            for file_path in matches:
                if os.path.isfile(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if query.lower() in content.lower():
                                file_info = self._get_file_info_object(file_path)
                                files_found.append(file_info)
                    except (PermissionError, UnicodeDecodeError):
                        continue  # Skip files we can't read
        
        return SearchResult(
            action=request.action,
            query=query,
            search_path=search_path,
            recursive=request.recursive,
            files_found=files_found,
            total_results=len(files_found),
            execution_time_ms=int((time.time() - start_time) * 1000)
        )
    
    def _get_file_info(self, request: DirectorySearchRequest, search_path: str, start_time: float) -> SearchResult:
        """Get detailed information about a specific file or directory."""
        files_found = []
        directories_found = []
        
        if os.path.isfile(search_path):
            file_info = self._get_file_info_object(search_path)
            files_found.append(file_info)
        elif os.path.isdir(search_path):
            dir_info = self._get_directory_info_object(search_path)
            directories_found.append(dir_info)
        else:
            raise FileNotFoundError(f"Path not found: {search_path}")
        
        return SearchResult(
            action=request.action,
            query=search_path,
            search_path=search_path,
            files_found=files_found,
            directories_found=directories_found,
            total_results=len(files_found) + len(directories_found),
            execution_time_ms=int((time.time() - start_time) * 1000)
        )
    
    def _explore_tree(self, request: DirectorySearchRequest, search_path: str, start_time: float) -> SearchResult:
        """Explore directory structure in tree format."""
        files_found = []
        directories_found = []
        max_depth = request.max_depth or 2
        
        def explore_recursive(path: str, current_depth: int):
            if current_depth > max_depth:
                return
                
            try:
                for item in os.listdir(path):
                    if not request.include_hidden and item.startswith('.'):
                        continue
                        
                    item_path = os.path.join(path, item)
                    
                    if os.path.isfile(item_path):
                        file_info = self._get_file_info_object(item_path)
                        files_found.append(file_info)
                    elif os.path.isdir(item_path):
                        dir_info = self._get_directory_info_object(item_path)
                        directories_found.append(dir_info)
                        explore_recursive(item_path, current_depth + 1)
            except PermissionError:
                pass
        
        explore_recursive(search_path, 0)
        
        return SearchResult(
            action=request.action,
            query=f"tree:{max_depth}",
            search_path=search_path,
            recursive=True,
            max_depth=max_depth,
            files_found=files_found,
            directories_found=directories_found,
            total_results=len(files_found) + len(directories_found),
            execution_time_ms=int((time.time() - start_time) * 1000)
        )
    
    def _find_by_extension(self, request: DirectorySearchRequest, search_path: str, start_time: float) -> SearchResult:
        """Find files by extension."""
        files_found = []
        extensions = request.file_extensions or ([request.query.lstrip('.')] if request.query else [])
        
        if not extensions:
            raise ValueError("Extension search requires file_extensions or query")
        
        for ext in extensions:
            ext = ext.lstrip('.')  # Remove leading dot if present
            pattern = f"*.{ext}"
            
            if request.recursive:
                search_pattern = os.path.join(search_path, "**", pattern)
                matches = glob.glob(search_pattern, recursive=True)
            else:
                search_pattern = os.path.join(search_path, pattern)
                matches = glob.glob(search_pattern)
            
            for match in matches:
                if os.path.isfile(match):
                    file_info = self._get_file_info_object(match)
                    if self._passes_filters(file_info, request):
                        files_found.append(file_info)
        
        return SearchResult(
            action=request.action,
            query=f"ext:{','.join(extensions)}",
            search_path=search_path,
            recursive=request.recursive,
            files_found=files_found,
            total_results=len(files_found),
            execution_time_ms=int((time.time() - start_time) * 1000)
        )
    
    def _find_recent_files(self, request: DirectorySearchRequest, search_path: str, start_time: float) -> SearchResult:
        """Find recently modified files."""
        files_found = []
        
        # Get all files
        if request.recursive:
            search_pattern = os.path.join(search_path, "**", "*")
            matches = glob.glob(search_pattern, recursive=True)
        else:
            search_pattern = os.path.join(search_path, "*")
            matches = glob.glob(search_pattern)
        
        file_infos = []
        for match in matches:
            if os.path.isfile(match):
                if not request.include_hidden and os.path.basename(match).startswith('.'):
                    continue
                file_info = self._get_file_info_object(match)
                if self._passes_filters(file_info, request):
                    file_infos.append(file_info)
        
        # Sort by modification time (most recent first)
        file_infos.sort(key=lambda f: f.modified_time, reverse=True)
        
        # Take top results (default 50)
        max_results = 50
        files_found = file_infos[:max_results]
        
        return SearchResult(
            action=request.action,
            query="recent_files",
            search_path=search_path,
            recursive=request.recursive,
            files_found=files_found,
            total_results=len(files_found),
            execution_time_ms=int((time.time() - start_time) * 1000)
        )
    
    def _get_file_info_object(self, file_path: str) -> FileInfo:
        """Get FileInfo object for a file."""
        stat = os.stat(file_path)
        
        return FileInfo(
            name=os.path.basename(file_path),
            path=file_path,
            size=stat.st_size,
            modified_time=datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
            created_time=datetime.fromtimestamp(stat.st_ctime, timezone.utc).isoformat(),
            extension=Path(file_path).suffix.lstrip('.') if Path(file_path).suffix else None,
            is_directory=False,
            permissions=oct(stat.st_mode)[-3:]
        )
    
    def _get_directory_info_object(self, dir_path: str) -> DirectoryInfo:
        """Get DirectoryInfo object for a directory."""
        stat = os.stat(dir_path)
        files = []
        subdirs = []
        file_count = 0
        total_size = 0
        
        try:
            for item in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item)
                if os.path.isfile(item_path):
                    file_count += 1
                    file_stat = os.stat(item_path)
                    total_size += file_stat.st_size
                    files.append(self._get_file_info_object(item_path))
                elif os.path.isdir(item_path):
                    subdirs.append(item)
        except PermissionError:
            pass
        
        return DirectoryInfo(
            name=os.path.basename(dir_path),
            path=dir_path,
            file_count=file_count,
            subdirectory_count=len(subdirs),
            total_size=total_size,
            modified_time=datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
            files=files,
            subdirectories=subdirs
        )
    
    def _passes_filters(self, file_info: FileInfo, request: DirectorySearchRequest) -> bool:
        """Check if file passes the request filters."""
        # Size filters
        if request.min_size and file_info.size < request.min_size:
            return False
        if request.max_size and file_info.size > request.max_size:
            return False
        
        # Date filters
        if request.modified_after:
            try:
                after_date = datetime.fromisoformat(request.modified_after.replace('Z', '+00:00'))
                file_date = datetime.fromisoformat(file_info.modified_time.replace('Z', '+00:00'))
                if file_date < after_date:
                    return False
            except ValueError:
                pass
        
        if request.modified_before:
            try:
                before_date = datetime.fromisoformat(request.modified_before.replace('Z', '+00:00'))
                file_date = datetime.fromisoformat(file_info.modified_time.replace('Z', '+00:00'))
                if file_date > before_date:
                    return False
            except ValueError:
                pass
        
        return True
    
    def _resolve_path(self, path: str) -> str:
        """Resolve and validate the search path."""
        if path == "." or path == "":
            return os.getcwd()
        
        # Convert to absolute path
        abs_path = os.path.abspath(path)
        
        # Validate path exists
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Path does not exist: {abs_path}")
        
        return abs_path
    
    def _get_suggested_paths(self, current_path: str) -> List[str]:
        """Get suggested paths for further exploration."""
        suggestions = []
        
        try:
            # Add parent directory
            parent = str(Path(current_path).parent)
            if parent != current_path:
                suggestions.append(parent)
            
            # Add subdirectories
            if os.path.isdir(current_path):
                for item in os.listdir(current_path):
                    item_path = os.path.join(current_path, item)
                    if os.path.isdir(item_path) and not item.startswith('.'):
                        suggestions.append(item_path)
                        if len(suggestions) >= 5:  # Limit suggestions
                            break
        except PermissionError:
            pass
        
        return suggestions
    
    def _create_search_summary(self, result: SearchResult) -> Dict[str, Any]:
        """Create a summary of search results."""
        return {
            "total_files": len(result.files_found),
            "total_directories": len(result.directories_found),
            "total_results": result.total_results,
            "action": result.action,
            "execution_time_ms": result.execution_time_ms,
            "success": result.success,
            "search_path": result.search_path,
            "recursive": result.recursive
        }
    
    @log_module_call("directory_manager")
    def get_search_history(self) -> List[SearchResult]:
        """Get Ray's search history."""
        return self.search_history
    
    def _save_to_file(self, request: DirectorySearchRequest, search_path: str, start_time: float) -> SearchResult:
        """Save content to a file."""
        if not request.query:
            raise ValueError("Save to file requires content in the query field")
        
        # Parse the query as JSON to get save parameters
        try:
            import json
            save_params = json.loads(request.query)
            file_path = save_params.get("file_path")
            content = save_params.get("content", "")
            overwrite = save_params.get("overwrite", False)
            create_directories = save_params.get("create_directories", True)
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid save parameters: {str(e)}")
        
        if not file_path:
            raise ValueError("file_path is required for save operation")
        
        # Resolve the file path
        if not os.path.isabs(file_path):
            file_path = os.path.join(search_path, file_path)
        
        # Check if file exists and overwrite is not allowed
        if os.path.exists(file_path) and not overwrite:
            raise ValueError(f"File already exists and overwrite is False: {file_path}")
        
        # Create parent directories if needed
        if create_directories:
            parent_dir = os.path.dirname(file_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir)
        
        # Write the content to file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Get file info after saving
            file_info = self._get_file_info_object(file_path)
            
            return SearchResult(
                action=request.action,
                query=f"saved_to:{file_path}",
                search_path=search_path,
                files_found=[file_info],
                total_results=1,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
            
        except Exception as e:
            raise ValueError(f"Failed to save file: {str(e)}")
    
    @log_module_call("directory_manager")
    def save_search_results_to_file(self, search_result: SearchResult, file_path: str, format: str = "json") -> Dict[str, Any]:
        """Save search results to a file."""
        try:
            if format.lower() == "json":
                content = json.dumps(search_result.dict(), indent=2, default=str)
            elif format.lower() == "markdown":
                content = self._format_search_results_as_markdown(search_result)
            elif format.lower() == "text":
                content = self._format_search_results_as_text(search_result)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            # Create parent directories if needed
            parent_dir = os.path.dirname(file_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir)
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            file_size = os.path.getsize(file_path)
            
            return {
                "success": True,
                "file_path": file_path,
                "file_size": file_size,
                "format": format,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error_message": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def _format_search_results_as_markdown(self, result: SearchResult) -> str:
        """Format search results as markdown."""
        content = f"# Search Results\n\n"
        content += f"**Action:** {result.action}\n"
        content += f"**Query:** {result.query}\n"
        content += f"**Path:** {result.search_path}\n"
        content += f"**Total Results:** {result.total_results}\n"
        content += f"**Execution Time:** {result.execution_time_ms}ms\n"
        content += f"**Timestamp:** {result.timestamp}\n\n"
        
        if result.files_found:
            content += f"## Files Found ({len(result.files_found)})\n\n"
            for file_info in result.files_found:
                size_kb = file_info.size / 1024
                content += f"- **{file_info.name}** ({size_kb:.1f}KB)\n"
                content += f"  - Path: `{file_info.path}`\n"
                content += f"  - Modified: {file_info.modified_time}\n"
                if file_info.extension:
                    content += f"  - Extension: {file_info.extension}\n"
                content += "\n"
        
        if result.directories_found:
            content += f"## Directories Found ({len(result.directories_found)})\n\n"
            for dir_info in result.directories_found:
                content += f"- **{dir_info.name}** ({dir_info.file_count} files)\n"
                content += f"  - Path: `{dir_info.path}`\n"
                content += f"  - Subdirectories: {dir_info.subdirectory_count}\n"
                content += f"  - Total Size: {dir_info.total_size / 1024:.1f}KB\n\n"
        
        return content
    
    def _format_search_results_as_text(self, result: SearchResult) -> str:
        """Format search results as plain text."""
        content = f"Search Results\n{'=' * 50}\n\n"
        content += f"Action: {result.action}\n"
        content += f"Query: {result.query}\n"
        content += f"Path: {result.search_path}\n"
        content += f"Total Results: {result.total_results}\n"
        content += f"Execution Time: {result.execution_time_ms}ms\n"
        content += f"Timestamp: {result.timestamp}\n\n"
        
        if result.files_found:
            content += f"Files Found ({len(result.files_found)}):\n{'-' * 30}\n"
            for file_info in result.files_found:
                size_kb = file_info.size / 1024
                content += f"• {file_info.name} ({size_kb:.1f}KB)\n"
                content += f"  Path: {file_info.path}\n"
                content += f"  Modified: {file_info.modified_time}\n"
                if file_info.extension:
                    content += f"  Extension: {file_info.extension}\n"
                content += "\n"
        
        if result.directories_found:
            content += f"Directories Found ({len(result.directories_found)}):\n{'-' * 30}\n"
            for dir_info in result.directories_found:
                content += f"• {dir_info.name} ({dir_info.file_count} files)\n"
                content += f"  Path: {dir_info.path}\n"
                content += f"  Subdirectories: {dir_info.subdirectory_count}\n"
                content += f"  Total Size: {dir_info.total_size / 1024:.1f}KB\n\n"
        
        return content

    def _rename_file(self, request: DirectorySearchRequest, search_path: str, start_time: float) -> SearchResult:
        """Rename a file or directory."""
        if not request.query:
            raise ValueError("Rename operation requires parameters in the query field")
        
        try:
            params = json.loads(request.query)
            source_path = params.get("source_path")
            target_path = params.get("target_path")
            force = params.get("force", False)
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid rename parameters: {str(e)}")
        
        if not source_path or not target_path:
            raise ValueError("Both source_path and target_path are required for rename operation")
        
        # Resolve paths
        if not os.path.isabs(source_path):
            source_path = os.path.join(search_path, source_path)
        if not os.path.isabs(target_path):
            target_path = os.path.join(search_path, target_path)
        
        # Check if source exists
        if not os.path.exists(source_path):
            raise ValueError(f"Source path does not exist: {source_path}")
        
        # Check if target exists and force is not enabled
        if os.path.exists(target_path) and not force:
            raise ValueError(f"Target path already exists and force is False: {target_path}")
        
        # Create target directory if needed
        target_dir = os.path.dirname(target_path)
        if target_dir and not os.path.exists(target_dir):
            os.makedirs(target_dir)
        
        # Perform rename
        try:
            os.rename(source_path, target_path)
            
            # Get info about the renamed file
            file_info = self._get_file_info_object(target_path)
            
            return SearchResult(
                action=request.action,
                query=f"renamed:{os.path.basename(source_path)} -> {os.path.basename(target_path)}",
                search_path=search_path,
                files_found=[file_info],
                total_results=1,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
            
        except Exception as e:
            raise ValueError(f"Failed to rename file: {str(e)}")
    
    def _delete_file(self, request: DirectorySearchRequest, search_path: str, start_time: float) -> SearchResult:
        """Delete a file or directory."""
        if not request.query:
            raise ValueError("Delete operation requires parameters in the query field")
        
        try:
            params = json.loads(request.query)
            target_path = params.get("target_path")
            force = params.get("force", False)
            recursive = params.get("recursive", False)
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid delete parameters: {str(e)}")
        
        if not target_path:
            raise ValueError("target_path is required for delete operation")
        
        # Resolve path
        if not os.path.isabs(target_path):
            target_path = os.path.join(search_path, target_path)
        
        # Check if path exists
        if not os.path.exists(target_path):
            raise ValueError(f"Path does not exist: {target_path}")
        
        # Get info before deletion
        if os.path.isfile(target_path):
            file_info = self._get_file_info_object(target_path)
            item_type = "file"
        else:
            # For directories, create a simple info object
            stat = os.stat(target_path)
            file_info = FileInfo(
                name=os.path.basename(target_path),
                path=target_path,
                size=0,
                modified_time=datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                is_directory=True
            )
            item_type = "directory"
        
        # Perform deletion
        try:
            if os.path.isfile(target_path):
                os.remove(target_path)
            elif os.path.isdir(target_path):
                if recursive:
                    import shutil
                    shutil.rmtree(target_path)
                else:
                    os.rmdir(target_path)  # Only works for empty directories
            
            return SearchResult(
                action=request.action,
                query=f"deleted:{item_type}:{os.path.basename(target_path)}",
                search_path=search_path,
                files_found=[file_info],
                total_results=1,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
            
        except Exception as e:
            raise ValueError(f"Failed to delete {item_type}: {str(e)}")
    
    def _move_file(self, request: DirectorySearchRequest, search_path: str, start_time: float) -> SearchResult:
        """Move a file or directory."""
        if not request.query:
            raise ValueError("Move operation requires parameters in the query field")
        
        try:
            params = json.loads(request.query)
            source_path = params.get("source_path")
            target_path = params.get("target_path")
            force = params.get("force", False)
            create_directories = params.get("create_directories", True)
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid move parameters: {str(e)}")
        
        if not source_path or not target_path:
            raise ValueError("Both source_path and target_path are required for move operation")
        
        # Resolve paths
        if not os.path.isabs(source_path):
            source_path = os.path.join(search_path, source_path)
        if not os.path.isabs(target_path):
            target_path = os.path.join(search_path, target_path)
        
        # Check if source exists
        if not os.path.exists(source_path):
            raise ValueError(f"Source path does not exist: {source_path}")
        
        # Check if target exists and force is not enabled
        if os.path.exists(target_path) and not force:
            raise ValueError(f"Target path already exists and force is False: {target_path}")
        
        # Create target directory if needed
        if create_directories:
            target_dir = os.path.dirname(target_path)
            if target_dir and not os.path.exists(target_dir):
                os.makedirs(target_dir)
        
        # Perform move
        try:
            import shutil
            shutil.move(source_path, target_path)
            
            # Get info about the moved file
            file_info = self._get_file_info_object(target_path)
            
            return SearchResult(
                action=request.action,
                query=f"moved:{os.path.basename(source_path)} -> {target_path}",
                search_path=search_path,
                files_found=[file_info],
                total_results=1,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
            
        except Exception as e:
            raise ValueError(f"Failed to move file: {str(e)}")

    @log_module_call("directory_manager")
    def clear_search_history(self) -> Dict[str, Any]:
        """Clear Ray's search history."""
        count = len(self.search_history)
        self.search_history.clear()
        return {"cleared_searches": count, "timestamp": datetime.now(timezone.utc).isoformat()}


# Global directory manager instance
directory_manager = DirectoryManager()