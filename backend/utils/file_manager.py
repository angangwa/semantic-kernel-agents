"""
File management utility for Contoso Agent Demo
Supports CSV, JSON, images, and other artifacts for frontend rendering
"""

import os
import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import mimetypes


class FileManager:
    """Simple file manager with direct filesystem operations - no metadata cache"""
    
    def __init__(self, artifacts_dir: str = "artifacts"):
        self.artifacts_dir = Path(artifacts_dir)
        self.artifacts_dir.mkdir(exist_ok=True)
    
    def generate_file_id(self, base_name: str, file_extension: str) -> str:
        """Generate unique file ID with timestamp and UUID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{base_name}_{timestamp}_{unique_id}.{file_extension}"
    
    def save_artifact(self, file_id: str, file_path: Union[str, Path], 
                     description: str = "", metadata: Dict[str, Any] = None) -> str:
        """
        Register an artifact file - simplified version that just confirms file exists
        
        Args:
            file_id: Unique file identifier  
            file_path: Path to the saved file
            description: Human-readable description (stored in memory only)
            metadata: Additional metadata (ignored in simple version)
            
        Returns:
            file_id: The registered file ID
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # File exists, that's all we need to verify
        return file_id
    
    def get_artifact_path(self, file_id: str) -> Path:
        """Get the full path for saving an artifact"""
        return self.artifacts_dir / file_id
    
    def get_file_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file metadata by checking filesystem directly"""
        file_path = self.artifacts_dir / file_id
        
        if not file_path.exists():
            return None
        
        # Extract info directly from filesystem
        file_extension = file_path.suffix.lower().lstrip('.')
        mime_type, _ = mimetypes.guess_type(str(file_path))
        
        # Get file stats
        stat_info = file_path.stat()
        
        # Generate description from filename
        base_name = file_path.stem.split('_')[0]  # Get part before timestamp
        description = self._generate_description(base_name, file_extension)
        
        return {
            "file_path": str(file_path),
            "file_type": file_extension,
            "mime_type": mime_type or f"application/{file_extension}",
            "description": description,
            "created_at": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
            "size_bytes": stat_info.st_size
        }
    
    def get_file_path(self, file_id: str) -> Optional[Path]:
        """Get full file path by file ID"""
        file_path = self.artifacts_dir / file_id
        return file_path if file_path.exists() else None
    
    def _generate_description(self, base_name: str, file_type: str) -> str:
        """Generate description from filename and type"""
        descriptions = {
            "monthly_bill_trend": "Monthly Bill Trend Chart",
            "bill_details": "Bill Line Items",
            "usage_analysis": "Usage Analysis Report"
        }
        
        for key, desc in descriptions.items():
            if key in base_name:
                return desc
        
        # Fallback description
        if file_type in ["png", "jpg", "jpeg"]:
            return "Chart/Image"
        elif file_type == "csv":
            return "Data Export"
        else:
            return f"{file_type.upper()} File"
    
    def format_file_reference(self, file_id: str, display_text: str = None) -> str:
        """
        Format file reference for agent responses using template syntax
        Frontend can parse [FILE:...] pattern for rendering
        
        Examples:
        - [FILE:bill_detail.csv:November Bill Details]
        - [FILE:usage_chart.png:Usage Analysis Chart]
        """
        if not file_id:
            return ""
            
        if display_text:
            return f"[FILE:{file_id}:{display_text}]"
        else:
            # Generate description from filename
            file_path = Path(file_id)
            base_name = file_path.stem.split('_')[0]
            file_extension = file_path.suffix.lower().lstrip('.')
            display = self._generate_description(base_name, file_extension)
            return f"[FILE:{file_id}:{display}]"
    
    def list_files(self, file_type: str = None, limit: int = None) -> List[Dict[str, Any]]:
        """List files by scanning filesystem directly"""
        files = []
        
        # Scan artifacts directory
        for file_path in self.artifacts_dir.glob("*"):
            if file_path.is_file():
                file_extension = file_path.suffix.lower().lstrip('.')
                
                # Filter by type if specified
                if file_type and file_extension != file_type:
                    continue
                
                file_info = self.get_file_info(file_path.name)
                if file_info:
                    files.append({
                        "file_id": file_path.name,
                        **file_info
                    })
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: x["created_at"], reverse=True)
        
        if limit:
            files = files[:limit]
            
        return files
    
    def cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """Clean up files older than specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        removed_count = 0
        
        # Scan directory for old files
        for file_path in self.artifacts_dir.glob("*"):
            if file_path.is_file():
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < cutoff_time:
                    file_path.unlink()
                    removed_count += 1
        
        return removed_count


# Global instance
file_manager = FileManager()