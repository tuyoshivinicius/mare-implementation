"""
MARE CLI - Helper utilities
Common utility functions used throughout the MARE CLI application
"""

import os
import json
import yaml
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import hashlib

def generate_uuid() -> str:
    """Generate a unique identifier."""
    return str(uuid.uuid4())

def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now().isoformat()

def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if necessary.
    
    Args:
        path: Directory path to ensure
    
    Returns:
        Path object for the directory
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj

def read_json_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Read and parse JSON file.
    
    Args:
        file_path: Path to JSON file
    
    Returns:
        Parsed JSON data
    
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json_file(
    file_path: Union[str, Path], 
    data: Dict[str, Any], 
    indent: int = 2
) -> None:
    """
    Write data to JSON file.
    
    Args:
        file_path: Path to output file
        data: Data to write
        indent: JSON indentation level
    """
    ensure_directory(Path(file_path).parent)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)

def read_yaml_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Read and parse YAML file.
    
    Args:
        file_path: Path to YAML file
    
    Returns:
        Parsed YAML data
    
    Raises:
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If file is not valid YAML
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def write_yaml_file(
    file_path: Union[str, Path], 
    data: Dict[str, Any]
) -> None:
    """
    Write data to YAML file.
    
    Args:
        file_path: Path to output file
        data: Data to write
    """
    ensure_directory(Path(file_path).parent)
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

def read_text_file(file_path: Union[str, Path]) -> str:
    """
    Read text file content.
    
    Args:
        file_path: Path to text file
    
    Returns:
        File content as string
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def write_text_file(file_path: Union[str, Path], content: str) -> None:
    """
    Write content to text file.
    
    Args:
        file_path: Path to output file
        content: Content to write
    """
    ensure_directory(Path(file_path).parent)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def calculate_file_hash(file_path: Union[str, Path]) -> str:
    """
    Calculate SHA-256 hash of file content.
    
    Args:
        file_path: Path to file
    
    Returns:
        Hexadecimal hash string
    """
    hash_sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def calculate_string_hash(content: str) -> str:
    """
    Calculate SHA-256 hash of string content.
    
    Args:
        content: String content to hash
    
    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def find_project_root(start_path: Optional[Union[str, Path]] = None) -> Optional[Path]:
    """
    Find MARE project root directory by looking for .mare directory.
    
    Args:
        start_path: Starting path for search (defaults to current directory)
    
    Returns:
        Path to project root or None if not found
    """
    if start_path is None:
        start_path = Path.cwd()
    else:
        start_path = Path(start_path)
    
    current = start_path.resolve()
    
    while current != current.parent:
        if (current / '.mare').exists():
            return current
        current = current.parent
    
    return None

def validate_project_structure(project_path: Union[str, Path]) -> bool:
    """
    Validate that directory contains a valid MARE project structure.
    
    Args:
        project_path: Path to project directory
    
    Returns:
        True if valid project structure, False otherwise
    """
    project_path = Path(project_path)
    
    required_items = [
        '.mare',
        '.mare/config.yaml',
        '.mare/workspace'
    ]
    
    return all((project_path / item).exists() for item in required_items)

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing/replacing invalid characters.
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing whitespace and dots
    filename = filename.strip(' .')
    
    # Ensure filename is not empty
    if not filename:
        filename = 'untitled'
    
    return filename

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to maximum length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncating
    
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)
    
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result

