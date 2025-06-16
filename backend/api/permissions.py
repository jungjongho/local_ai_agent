"""
Path permission management API endpoints
"""
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from pathlib import Path
import os

from services.agent_service import agent_service
from utils.logger import logger

router = APIRouter(prefix="/api/permissions", tags=["permissions"])


class PathPermissionRequest(BaseModel):
    """Request model for path permission operations."""
    path: str = Field(..., description="File or directory path")
    permission_type: str = Field(default="read_write", description="Permission type: read, write, read_write")
    reason: Optional[str] = Field(None, description="Reason for requesting permission")


class PathPermissionResponse(BaseModel):
    """Response model for path permissions."""
    path: str
    allowed: bool
    permission_type: str
    reason: Optional[str] = None
    added_timestamp: Optional[str] = None


class BulkPathPermissionRequest(BaseModel):
    """Request model for bulk path permission operations."""
    paths: List[PathPermissionRequest] = Field(..., description="List of path permission requests")


@router.get("/allowed-paths")
async def get_allowed_paths() -> Dict[str, Any]:
    """
    Get currently allowed paths.
    
    Returns:
        List of currently allowed paths with metadata
    """
    logger.info("Getting allowed paths")
    
    try:
        # Get file system tool config
        fs_tool = agent_service.tools.get("file_system")
        if not fs_tool:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="File system tool not available"
            )
        
        allowed_paths = fs_tool.fs_config.allowed_paths or []
        
        # Add metadata for each path
        paths_info = []
        for path_str in allowed_paths:
            try:
                path_obj = Path(path_str)
                paths_info.append({
                    "path": path_str,
                    "exists": path_obj.exists(),
                    "is_directory": path_obj.is_dir() if path_obj.exists() else None,
                    "absolute_path": str(path_obj.resolve()) if path_obj.exists() else path_str,
                    "permission_type": "read_write",  # Default for existing paths
                    "is_user_added": path_str not in agent_service._get_safe_allowed_paths()  # Check if user added
                })
            except Exception as e:
                logger.warning(f"Error processing path {path_str}: {e}")
                paths_info.append({
                    "path": path_str,
                    "exists": False,
                    "error": str(e),
                    "permission_type": "read_write"
                })
        
        return {
            "allowed_paths": paths_info,
            "total_count": len(paths_info),
            "default_paths_count": len(agent_service._get_safe_allowed_paths()),
            "user_added_count": len(paths_info) - len(agent_service._get_safe_allowed_paths())
        }
        
    except Exception as e:
        logger.error(f"Error getting allowed paths: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving allowed paths: {str(e)}"
        )


@router.post("/add-path")
async def add_allowed_path(request: PathPermissionRequest) -> Dict[str, Any]:
    """
    Add a new path to allowed paths.
    
    Args:
        request: Path permission request
        
    Returns:
        Result of path addition
    """
    logger.info(f"Adding path permission: {request.path}")
    
    try:
        # Validate path
        try:
            path_obj = Path(request.path).resolve()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid path: {request.path} - {str(e)}"
            )
        
        # Security check - prevent adding dangerous paths
        dangerous_patterns = [
            "/System", "/usr/bin", "/bin", "/sbin", "/etc/passwd", "/etc/shadow",
            "C:\\Windows\\System32", "C:\\Program Files", "/root", "/.ssh"
        ]
        
        path_str = str(path_obj)
        for pattern in dangerous_patterns:
            if pattern in path_str:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Cannot add system path: {request.path}"
                )
        
        # Get file system tool
        fs_tool = agent_service.tools.get("file_system")
        if not fs_tool:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="File system tool not available"
            )
        
        # Check if path already allowed
        current_paths = fs_tool.fs_config.allowed_paths or []
        if str(path_obj) in current_paths or request.path in current_paths:
            return {
                "success": True,
                "message": f"Path already allowed: {request.path}",
                "path": str(path_obj),
                "already_exists": True
            }
        
        # Add path to allowed paths
        new_paths = current_paths + [str(path_obj)]
        fs_tool.fs_config.allowed_paths = new_paths
        
        logger.info(f"Added path to allowed list: {path_obj}")
        
        return {
            "success": True,
            "message": f"Path added successfully: {request.path}",
            "path": str(path_obj),
            "permission_type": request.permission_type,
            "reason": request.reason,
            "total_allowed_paths": len(new_paths),
            "already_exists": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding path permission: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding path: {str(e)}"
        )


@router.post("/add-paths")
async def add_multiple_paths(request: BulkPathPermissionRequest) -> Dict[str, Any]:
    """
    Add multiple paths to allowed paths.
    
    Args:
        request: Bulk path permission request
        
    Returns:
        Results of bulk path addition
    """
    logger.info(f"Adding multiple path permissions: {len(request.paths)} paths")
    
    results = []
    successful = 0
    failed = 0
    
    for path_request in request.paths:
        try:
            # Use the single path addition logic
            result = await add_allowed_path(path_request)
            results.append({
                "path": path_request.path,
                "success": True,
                "result": result
            })
            successful += 1
            
        except HTTPException as e:
            results.append({
                "path": path_request.path,
                "success": False,
                "error": e.detail,
                "status_code": e.status_code
            })
            failed += 1
        except Exception as e:
            results.append({
                "path": path_request.path,
                "success": False,
                "error": str(e)
            })
            failed += 1
    
    return {
        "total_processed": len(request.paths),
        "successful": successful,
        "failed": failed,
        "results": results
    }


@router.delete("/remove-path")
async def remove_allowed_path(path: str) -> Dict[str, Any]:
    """
    Remove a path from allowed paths.
    
    Args:
        path: Path to remove
        
    Returns:
        Result of path removal
    """
    logger.info(f"Removing path permission: {path}")
    
    try:
        # Get file system tool
        fs_tool = agent_service.tools.get("file_system")
        if not fs_tool:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="File system tool not available"
            )
        
        current_paths = fs_tool.fs_config.allowed_paths or []
        
        # Resolve path for comparison
        try:
            path_obj = Path(path).resolve()
            path_str = str(path_obj)
        except Exception:
            path_str = path
        
        # Check if it's a default path (prevent removal of core paths)
        default_paths = agent_service._get_safe_allowed_paths()
        if path in default_paths or path_str in default_paths:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Cannot remove default system path: {path}"
            )
        
        # Remove path
        new_paths = []
        removed = False
        
        for existing_path in current_paths:
            if existing_path != path and existing_path != path_str:
                new_paths.append(existing_path)
            else:
                removed = True
        
        if not removed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Path not found in allowed paths: {path}"
            )
        
        fs_tool.fs_config.allowed_paths = new_paths
        
        logger.info(f"Removed path from allowed list: {path}")
        
        return {
            "success": True,
            "message": f"Path removed successfully: {path}",
            "removed_path": path,
            "remaining_paths": len(new_paths)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing path permission: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing path: {str(e)}"
        )


@router.post("/validate-path")
async def validate_path_access(path: str) -> Dict[str, Any]:
    """
    Validate if a path can be accessed with current permissions.
    
    Args:
        path: Path to validate
        
    Returns:
        Validation result
    """
    logger.info(f"Validating path access: {path}")
    
    try:
        # Test file operation to check access
        result = await agent_service.simple_file_operation(
            operation="info",
            path=path
        )
        
        return {
            "path": path,
            "accessible": result.success,
            "error": result.error if not result.success else None,
            "details": result.result if result.success else None
        }
        
    except Exception as e:
        logger.error(f"Error validating path: {e}")
        return {
            "path": path,
            "accessible": False,
            "error": str(e)
        }


@router.get("/suggested-paths")
async def get_suggested_paths() -> Dict[str, Any]:
    """
    Get suggested paths that users might want to add.
    
    Returns:
        List of suggested paths
    """
    logger.info("Getting suggested paths")
    
    try:
        home_dir = Path.home()
        
        suggested_paths = []
        
        # Common user directories
        common_dirs = [
            home_dir / "Desktop",
            home_dir / "Documents", 
            home_dir / "Downloads",
            home_dir / "workspace",
            home_dir / "projects",
            home_dir / "dev",
            home_dir / "code",
            Path.cwd(),  # Current working directory
        ]
        
        for dir_path in common_dirs:
            if dir_path.exists() and dir_path.is_dir():
                suggested_paths.append({
                    "path": str(dir_path),
                    "display_name": dir_path.name,
                    "description": f"Your {dir_path.name} directory",
                    "exists": True,
                    "type": "directory"
                })
        
        # Add some common project locations
        project_locations = [
            home_dir / "GitHub",
            home_dir / "git",
            home_dir / "repos",
            Path("/opt/homebrew"),  # Common on macOS
            Path("/usr/local"),
        ]
        
        for project_path in project_locations:
            if project_path.exists():
                suggested_paths.append({
                    "path": str(project_path),
                    "display_name": project_path.name,
                    "description": f"Common development directory: {project_path.name}",
                    "exists": True,
                    "type": "directory"
                })
        
        return {
            "suggested_paths": suggested_paths,
            "total_suggestions": len(suggested_paths)
        }
        
    except Exception as e:
        logger.error(f"Error getting suggested paths: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting suggestions: {str(e)}"
        )


@router.post("/reset-to-defaults")
async def reset_to_default_paths() -> Dict[str, Any]:
    """
    Reset allowed paths to default safe paths.
    
    Returns:
        Result of reset operation
    """
    logger.info("Resetting paths to defaults")
    
    try:
        # Get file system tool
        fs_tool = agent_service.tools.get("file_system")
        if not fs_tool:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="File system tool not available"
            )
        
        # Reset to default paths
        default_paths = agent_service._get_safe_allowed_paths()
        fs_tool.fs_config.allowed_paths = default_paths
        
        logger.info(f"Reset to {len(default_paths)} default paths")
        
        return {
            "success": True,
            "message": "Paths reset to defaults successfully",
            "default_paths": default_paths,
            "total_paths": len(default_paths)
        }
        
    except Exception as e:
        logger.error(f"Error resetting paths: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting paths: {str(e)}"
        )
