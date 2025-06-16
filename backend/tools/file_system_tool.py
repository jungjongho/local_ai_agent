"""
File system tool for safe file operations.
Provides comprehensive file management capabilities with security controls.
"""
import os
import shutil
import stat
import hashlib
import mimetypes
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

import aiofiles
import aiofiles.os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .base_tool import BaseTool, ToolError, ToolConfig
from utils.logger import logger


class FileSystemConfig(ToolConfig):
    """Configuration specific to file system operations."""
    allowed_extensions: List[str] = [
        '.txt', '.md', '.json', '.csv', '.xml', '.yml', '.yaml',
        '.py', '.js', '.html', '.css', '.sql', '.log'
    ]
    blocked_extensions: List[str] = [
        '.exe', '.bat', '.cmd', '.com', '.scr', '.vbs', '.dll'
    ]
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    max_directory_depth: int = 10
    enable_backup: bool = True
    backup_directory: str = "data/backups"


class FileWatcher(FileSystemEventHandler):
    """File system event handler for monitoring changes."""
    
    def __init__(self, callback=None):
        self.callback = callback
        self.changes = []
    
    def on_modified(self, event):
        if not event.is_directory:
            change = {
                "type": "modified",
                "path": event.src_path,
                "timestamp": datetime.now().isoformat()
            }
            self.changes.append(change)
            if self.callback:
                self.callback(change)
    
    def on_created(self, event):
        if not event.is_directory:
            change = {
                "type": "created", 
                "path": event.src_path,
                "timestamp": datetime.now().isoformat()
            }
            self.changes.append(change)
            if self.callback:
                self.callback(change)
    
    def on_deleted(self, event):
        if not event.is_directory:
            change = {
                "type": "deleted",
                "path": event.src_path, 
                "timestamp": datetime.now().isoformat()
            }
            self.changes.append(change)
            if self.callback:
                self.callback(change)


class FileSystemTool(BaseTool):
    """
    Comprehensive file system tool with safety controls.
    
    Provides secure file operations including read, write, copy, move,
    delete, search, and monitoring capabilities.
    """
    
    def __init__(self, config: Optional[FileSystemConfig] = None):
        self.fs_config = config or FileSystemConfig()
        super().__init__(self.fs_config)
        
        # Initialize backup directory
        self.backup_path = Path(self.fs_config.backup_directory)
        self.backup_path.mkdir(parents=True, exist_ok=True)
        
        # File watcher for monitoring
        self.observer = None
        self.file_watcher = None
        
        logger.info("FileSystemTool initialized with safety controls")
    
    @property
    def name(self) -> str:
        return "file_system"
    
    @property
    def description(self) -> str:
        return """Comprehensive file system operations tool. Can read, write, copy, move, delete, 
        search files and directories. Includes safety controls and monitoring capabilities."""
    
    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": [
                        "read", "write", "copy", "move", "delete", "list", 
                        "search", "info", "mkdir", "watch", "stop_watch",
                        "backup", "restore", "hash", "permissions"
                    ],
                    "description": "File system operation to perform"
                },
                "path": {
                    "type": "string",
                    "description": "File or directory path"
                },
                "content": {
                    "type": "string", 
                    "description": "Content to write (for write operations)"
                },
                "destination": {
                    "type": "string",
                    "description": "Destination path (for copy/move operations)"
                },
                "pattern": {
                    "type": "string",
                    "description": "Search pattern (for search operations)"
                },
                "recursive": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to operate recursively"
                },
                "encoding": {
                    "type": "string",
                    "default": "utf-8",
                    "description": "File encoding for text operations"
                }
            },
            "required": ["operation", "path"]
        }
    
    async def _execute(self, **kwargs) -> Any:
        """Execute file system operation."""
        operation = kwargs.get("operation")
        path = kwargs.get("path")
        
        # Dispatch to specific operation method
        operation_methods = {
            "read": self._read_file,
            "write": self._write_file,
            "copy": self._copy_item,
            "move": self._move_item,
            "delete": self._delete_item,
            "list": self._list_directory,
            "search": self._search_files,
            "info": self._get_file_info,
            "mkdir": self._create_directory,
            "watch": self._start_watching,
            "stop_watch": self._stop_watching,
            "backup": self._backup_file,
            "restore": self._restore_file,
            "hash": self._calculate_hash,
            "permissions": self._manage_permissions
        }
        
        if operation not in operation_methods:
            raise ToolError(f"Unsupported operation: {operation}", self.name)
        
        return await operation_methods[operation](**kwargs)
    
    def _security_check(self, kwargs: Dict[str, Any]) -> None:
        """Enhanced security checks for file operations."""
        super()._security_check(kwargs)
        
        operation = kwargs.get("operation")
        path = kwargs.get("path")
        
        if not path:
            raise ToolError("Path is required", self.name)
        
        # Normalize and resolve path
        try:
            resolved_path = Path(path).resolve()
        except Exception as e:
            raise ToolError(f"Invalid path: {path}", self.name, {"error": str(e)})
        
        # Check if path is allowed
        if self.fs_config.allowed_paths:
            allowed = False
            for allowed_path in self.fs_config.allowed_paths:
                try:
                    allowed_path_resolved = Path(allowed_path).resolve()
                    # Check if the resolved path is within any allowed directory
                    if (
                        resolved_path == allowed_path_resolved or 
                        str(resolved_path).startswith(str(allowed_path_resolved) + os.sep) or
                        str(resolved_path).startswith(str(allowed_path_resolved) + "/")
                    ):
                        allowed = True
                        break
                except (ValueError, OSError) as e:
                    logger.debug(f"Error checking allowed path {allowed_path}: {e}")
                    continue
            
            if not allowed:
                # More helpful error message
                logger.warning(f"Path access denied: {resolved_path}")
                logger.info(f"Allowed paths: {self.fs_config.allowed_paths}")
                raise ToolError(
                    f"Path not in allowed directories: {path}\nAllowed directories: {', '.join(self.fs_config.allowed_paths[:3])}{'...' if len(self.fs_config.allowed_paths) > 3 else ''}",
                    self.name,
                    {"allowed_paths": self.fs_config.allowed_paths}
                )
        
        # Check file extension for read/write operations
        if operation in ["read", "write"] and resolved_path.suffix:
            if (resolved_path.suffix.lower() in self.fs_config.blocked_extensions or
                (self.fs_config.allowed_extensions and 
                 resolved_path.suffix.lower() not in self.fs_config.allowed_extensions)):
                raise ToolError(
                    f"File extension not allowed: {resolved_path.suffix}",
                    self.name
                )
        
        # Check for blocked patterns
        for pattern in self.fs_config.blocked_patterns:
            if pattern in str(resolved_path):
                raise ToolError(
                    f"Path contains blocked pattern: {pattern}",
                    self.name
                )
        
        # Prevent directory traversal attacks
        if ".." in str(resolved_path) or str(resolved_path).startswith("/"):
            if not any(str(resolved_path).startswith(allowed) 
                      for allowed in (self.fs_config.allowed_paths or [])):
                raise ToolError(
                    "Directory traversal detected",
                    self.name
                )
    
    async def _read_file(self, path: str, encoding: str = "utf-8", **kwargs) -> Dict[str, Any]:
        """Read file content."""
        file_path = Path(path)
        
        if not file_path.exists():
            raise ToolError(f"File not found: {path}", self.name)
        
        if not file_path.is_file():
            raise ToolError(f"Path is not a file: {path}", self.name)
        
        # Check file size
        file_size = file_path.stat().st_size
        if file_size > self.fs_config.max_file_size:
            raise ToolError(
                f"File too large: {file_size} bytes > {self.fs_config.max_file_size}",
                self.name
            )
        
        try:
            async with aiofiles.open(file_path, mode='r', encoding=encoding) as f:
                content = await f.read()
            
            return {
                "content": content,
                "size": file_size,
                "encoding": encoding,
                "mime_type": mimetypes.guess_type(str(file_path))[0],
                "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
            
        except UnicodeDecodeError:
            # Try binary read for non-text files
            async with aiofiles.open(file_path, mode='rb') as f:
                content = await f.read()
            
            return {
                "content": content.hex(),
                "size": file_size,
                "encoding": "binary",
                "mime_type": mimetypes.guess_type(str(file_path))[0],
                "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                "note": "Binary content returned as hex string"
            }
    
    async def _write_file(
        self, 
        path: str, 
        content: str, 
        encoding: str = "utf-8",
        **kwargs
    ) -> Dict[str, Any]:
        """Write content to file."""
        file_path = Path(path)
        
        # Create backup if file exists
        if file_path.exists() and self.fs_config.enable_backup:
            await self._backup_file(path=path)
        
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            async with aiofiles.open(file_path, mode='w', encoding=encoding) as f:
                await f.write(content)
            
            file_size = file_path.stat().st_size
            
            return {
                "path": str(file_path),
                "size": file_size,
                "encoding": encoding,
                "created": not file_path.existed_before if hasattr(file_path, 'existed_before') else None,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise ToolError(f"Failed to write file: {str(e)}", self.name)
    
    async def _copy_item(
        self, 
        path: str, 
        destination: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """Copy file or directory."""
        src_path = Path(path)
        dst_path = Path(destination)
        
        if not src_path.exists():
            raise ToolError(f"Source not found: {path}", self.name)
        
        try:
            if src_path.is_file():
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, dst_path)
                operation = "file_copy"
            else:
                shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
                operation = "directory_copy"
            
            return {
                "operation": operation,
                "source": str(src_path),
                "destination": str(dst_path),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise ToolError(f"Failed to copy: {str(e)}", self.name)
    
    async def _move_item(
        self, 
        path: str, 
        destination: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """Move file or directory."""
        src_path = Path(path)
        dst_path = Path(destination)
        
        if not src_path.exists():
            raise ToolError(f"Source not found: {path}", self.name)
        
        try:
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(src_path, dst_path)
            
            return {
                "operation": "move",
                "source": str(src_path),
                "destination": str(dst_path),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise ToolError(f"Failed to move: {str(e)}", self.name)
    
    async def _delete_item(self, path: str, **kwargs) -> Dict[str, Any]:
        """Delete file or directory."""
        item_path = Path(path)
        
        if not item_path.exists():
            raise ToolError(f"Item not found: {path}", self.name)
        
        # Create backup before deletion
        if self.fs_config.enable_backup:
            await self._backup_file(path=path)
        
        try:
            if item_path.is_file():
                item_path.unlink()
                operation = "file_delete"
            else:
                shutil.rmtree(item_path)
                operation = "directory_delete"
            
            return {
                "operation": operation,
                "path": str(item_path),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise ToolError(f"Failed to delete: {str(e)}", self.name)
    
    async def _list_directory(
        self, 
        path: str, 
        recursive: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """List directory contents."""
        dir_path = Path(path)
        
        if not dir_path.exists():
            raise ToolError(f"Directory not found: {path}", self.name)
        
        if not dir_path.is_dir():
            raise ToolError(f"Path is not a directory: {path}", self.name)
        
        try:
            items = []
            
            if recursive:
                for item in dir_path.rglob("*"):
                    stat_info = item.stat()
                    items.append({
                        "name": item.name,
                        "path": str(item),
                        "type": "file" if item.is_file() else "directory",
                        "size": stat_info.st_size if item.is_file() else None,
                        "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                        "permissions": oct(stat_info.st_mode)[-3:]
                    })
            else:
                for item in dir_path.iterdir():
                    stat_info = item.stat()
                    items.append({
                        "name": item.name,
                        "path": str(item),
                        "type": "file" if item.is_file() else "directory",
                        "size": stat_info.st_size if item.is_file() else None,
                        "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                        "permissions": oct(stat_info.st_mode)[-3:]
                    })
            
            return {
                "directory": str(dir_path),
                "items": items,
                "count": len(items),
                "recursive": recursive
            }
            
        except Exception as e:
            raise ToolError(f"Failed to list directory: {str(e)}", self.name)
    
    async def _search_files(
        self, 
        path: str, 
        pattern: str,
        recursive: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Search for files matching pattern."""
        search_path = Path(path)
        
        if not search_path.exists():
            raise ToolError(f"Search path not found: {path}", self.name)
        
        try:
            matches = []
            
            if recursive:
                for item in search_path.rglob(pattern):
                    if item.is_file():
                        stat_info = item.stat()
                        matches.append({
                            "path": str(item),
                            "name": item.name,
                            "size": stat_info.st_size,
                            "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat()
                        })
            else:
                for item in search_path.glob(pattern):
                    if item.is_file():
                        stat_info = item.stat()
                        matches.append({
                            "path": str(item),
                            "name": item.name,
                            "size": stat_info.st_size,
                            "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat()
                        })
            
            return {
                "search_path": str(search_path),
                "pattern": pattern,
                "matches": matches,
                "count": len(matches),
                "recursive": recursive
            }
            
        except Exception as e:
            raise ToolError(f"Search failed: {str(e)}", self.name)
    
    async def _get_file_info(self, path: str, **kwargs) -> Dict[str, Any]:
        """Get detailed file/directory information."""
        item_path = Path(path)
        
        if not item_path.exists():
            raise ToolError(f"Item not found: {path}", self.name)
        
        try:
            stat_info = item_path.stat()
            
            info = {
                "path": str(item_path),
                "name": item_path.name,
                "type": "file" if item_path.is_file() else "directory",
                "size": stat_info.st_size,
                "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat_info.st_atime).isoformat(),
                "permissions": oct(stat_info.st_mode)[-3:],
                "owner_readable": bool(stat_info.st_mode & stat.S_IRUSR),
                "owner_writable": bool(stat_info.st_mode & stat.S_IWUSR),
                "owner_executable": bool(stat_info.st_mode & stat.S_IXUSR)
            }
            
            if item_path.is_file():
                info["mime_type"] = mimetypes.guess_type(str(item_path))[0]
                info["extension"] = item_path.suffix
            
            return info
            
        except Exception as e:
            raise ToolError(f"Failed to get file info: {str(e)}", self.name)
    
    async def _create_directory(self, path: str, **kwargs) -> Dict[str, Any]:
        """Create directory and parent directories."""
        dir_path = Path(path)
        
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            
            return {
                "operation": "mkdir",
                "path": str(dir_path),
                "created": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise ToolError(f"Failed to create directory: {str(e)}", self.name)
    
    async def _start_watching(self, path: str, **kwargs) -> Dict[str, Any]:
        """Start watching directory for changes."""
        watch_path = Path(path)
        
        if not watch_path.exists() or not watch_path.is_dir():
            raise ToolError(f"Watch path must be an existing directory: {path}", self.name)
        
        try:
            if self.observer and self.observer.is_alive():
                self.observer.stop()
                self.observer.join()
            
            self.file_watcher = FileWatcher()
            self.observer = Observer()
            self.observer.schedule(self.file_watcher, str(watch_path), recursive=True)
            self.observer.start()
            
            return {
                "operation": "start_watch",
                "path": str(watch_path),
                "status": "watching",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise ToolError(f"Failed to start watching: {str(e)}", self.name)
    
    async def _stop_watching(self, **kwargs) -> Dict[str, Any]:
        """Stop file system watching."""
        try:
            if self.observer and self.observer.is_alive():
                self.observer.stop()
                self.observer.join()
                
                changes = self.file_watcher.changes if self.file_watcher else []
                
                return {
                    "operation": "stop_watch",
                    "status": "stopped",
                    "changes_detected": len(changes),
                    "changes": changes,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "operation": "stop_watch",
                    "status": "not_watching",
                    "message": "File watcher was not active"
                }
                
        except Exception as e:
            raise ToolError(f"Failed to stop watching: {str(e)}", self.name)
    
    async def _backup_file(self, path: str, **kwargs) -> Dict[str, Any]:
        """Create backup of file or directory."""
        source_path = Path(path)
        
        if not source_path.exists():
            raise ToolError(f"Backup source not found: {path}", self.name)
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{source_path.name}_{timestamp}"
            backup_file_path = self.backup_path / backup_name
            
            if source_path.is_file():
                shutil.copy2(source_path, backup_file_path)
                operation = "file_backup"
            else:
                shutil.copytree(source_path, backup_file_path)
                operation = "directory_backup"
            
            return {
                "operation": operation,
                "source": str(source_path),
                "backup_path": str(backup_file_path),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise ToolError(f"Failed to create backup: {str(e)}", self.name)
    
    async def _restore_file(self, path: str, backup_name: str = None, **kwargs) -> Dict[str, Any]:
        """Restore file from backup."""
        restore_path = Path(path)
        
        try:
            if backup_name:
                backup_file_path = self.backup_path / backup_name
            else:
                # Find most recent backup
                pattern = f"{restore_path.name}_*"
                backups = list(self.backup_path.glob(pattern))
                if not backups:
                    raise ToolError(f"No backups found for: {path}", self.name)
                backup_file_path = max(backups, key=lambda p: p.stat().st_mtime)
            
            if not backup_file_path.exists():
                raise ToolError(f"Backup file not found: {backup_file_path}", self.name)
            
            if backup_file_path.is_file():
                shutil.copy2(backup_file_path, restore_path)
                operation = "file_restore"
            else:
                if restore_path.exists():
                    shutil.rmtree(restore_path)
                shutil.copytree(backup_file_path, restore_path)
                operation = "directory_restore"
            
            return {
                "operation": operation,
                "restored_path": str(restore_path),
                "backup_used": str(backup_file_path),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise ToolError(f"Failed to restore: {str(e)}", self.name)
    
    async def _calculate_hash(
        self, 
        path: str, 
        algorithm: str = "sha256",
        **kwargs
    ) -> Dict[str, Any]:
        """Calculate file hash."""
        file_path = Path(path)
        
        if not file_path.exists():
            raise ToolError(f"File not found: {path}", self.name)
        
        if not file_path.is_file():
            raise ToolError(f"Path is not a file: {path}", self.name)
        
        try:
            hash_func = getattr(hashlib, algorithm)()
            
            async with aiofiles.open(file_path, mode='rb') as f:
                while chunk := await f.read(8192):
                    hash_func.update(chunk)
            
            return {
                "path": str(file_path),
                "algorithm": algorithm,
                "hash": hash_func.hexdigest(),
                "file_size": file_path.stat().st_size,
                "timestamp": datetime.now().isoformat()
            }
            
        except AttributeError:
            raise ToolError(f"Unsupported hash algorithm: {algorithm}", self.name)
        except Exception as e:
            raise ToolError(f"Failed to calculate hash: {str(e)}", self.name)
    
    async def _manage_permissions(
        self, 
        path: str, 
        permissions: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Get or set file permissions."""
        item_path = Path(path)
        
        if not item_path.exists():
            raise ToolError(f"Item not found: {path}", self.name)
        
        try:
            current_mode = item_path.stat().st_mode
            current_permissions = oct(current_mode)[-3:]
            
            result = {
                "path": str(item_path),
                "current_permissions": current_permissions,
                "readable": bool(current_mode & stat.S_IRUSR),
                "writable": bool(current_mode & stat.S_IWUSR),
                "executable": bool(current_mode & stat.S_IXUSR)
            }
            
            if permissions:
                # Set new permissions
                new_mode = int(permissions, 8)
                item_path.chmod(new_mode)
                result["operation"] = "permissions_changed"
                result["new_permissions"] = permissions
            else:
                result["operation"] = "permissions_read"
            
            return result
            
        except Exception as e:
            raise ToolError(f"Failed to manage permissions: {str(e)}", self.name)
    
    def cleanup(self):
        """Cleanup resources."""
        if self.observer and self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
        
        logger.info("FileSystemTool cleanup completed")
