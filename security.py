import os
from pathlib import Path
from typing import Union

class SecurityValidator:
    DATA_DIR = "/data"
    
    @classmethod
    def validate_path(cls, path: Union[str, Path]) -> bool:
        path = Path(path).resolve()
        data_path = Path(cls.DATA_DIR).resolve()
        
        # Ensure path is within /data directory
        if not str(path).startswith(str(data_path)):
            raise SecurityError(f"Access denied: Path {path} is outside {cls.DATA_DIR}")
        return True
    
    @classmethod
    def validate_operation(cls, operation: str, path: Union[str, Path]) -> bool:
        # Prevent delete operations
        if operation.lower() in ['delete', 'remove', 'unlink', 'rmdir']:
            raise SecurityError(f"Operation denied: {operation} is not allowed")
        return True

class SecurityError(Exception):
    pass
