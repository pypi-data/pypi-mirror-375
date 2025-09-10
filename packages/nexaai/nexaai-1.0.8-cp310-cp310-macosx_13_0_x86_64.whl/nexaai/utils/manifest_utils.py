"""
Manifest and metadata utilities for handling nexa.manifest files and model metadata.

This module provides utilities to:
- Load and save nexa.manifest files
- Create GGUF and MLX manifests
- Process manifest metadata (handle null fields, fetch avatars, etc.)
- Manage backward compatibility with old download_metadata.json files
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

from .quantization_utils import (
    extract_quantization_from_filename, 
    detect_quantization_for_mlx
)
from .model_types import (
    PIPELINE_TO_MODEL_TYPE,
    MODEL_TYPE_TO_PIPELINE
)


def process_manifest_metadata(manifest: Dict[str, Any], repo_id: str) -> Dict[str, Any]:
    """Process manifest metadata to handle null/missing fields."""
    # Handle pipeline_tag
    pipeline_tag = manifest.get('pipeline_tag')
    if not pipeline_tag:
        # Reverse map from ModelType if available
        model_type = manifest.get('ModelType')
        pipeline_tag = MODEL_TYPE_TO_PIPELINE.get(model_type) if model_type else None
    
    # Handle download_time - keep as null if missing
    download_time = manifest.get('download_time')
    
    # Handle avatar_url - fetch on-the-fly if missing/null
    avatar_url = manifest.get('avatar_url')
    if not avatar_url:
        try:
            from .avatar_fetcher import get_avatar_url_for_repo
            avatar_url = get_avatar_url_for_repo(repo_id)
        except Exception:
            # If fetching fails, leave as None
            avatar_url = None
    
    # Return processed metadata
    processed_manifest = manifest.copy()
    processed_manifest.update({
        'pipeline_tag': pipeline_tag,
        'download_time': download_time,
        'avatar_url': avatar_url
    })
    
    return processed_manifest


def load_nexa_manifest(directory_path: str) -> Dict[str, Any]:
    """Load manifest from nexa.manifest if it exists."""
    manifest_path = os.path.join(directory_path, 'nexa.manifest')
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def load_download_metadata(directory_path: str, repo_id: Optional[str] = None) -> Dict[str, Any]:
    """Load download metadata from nexa.manifest if it exists, fallback to old format."""
    # First try to load from new manifest format
    manifest = load_nexa_manifest(directory_path)
    if manifest and repo_id:
        # Process the manifest to handle null/missing fields
        return process_manifest_metadata(manifest, repo_id)
    elif manifest:
        # Return manifest as-is if no repo_id provided (for backward compatibility)
        return manifest
    
    # Fallback to old format for backward compatibility
    old_metadata_path = os.path.join(directory_path, 'download_metadata.json')
    if os.path.exists(old_metadata_path):
        try:
            with open(old_metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def save_download_metadata(directory_path: str, metadata: Dict[str, Any]) -> None:
    """Save download metadata to nexa.manifest in the new format."""
    manifest_path = os.path.join(directory_path, 'nexa.manifest')
    try:
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
    except IOError:
        # If we can't save metadata, don't fail the download
        pass


def create_gguf_manifest(repo_id: str, files: List[str], directory_path: str, old_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Create GGUF format manifest."""
    
    # Load existing manifest to merge GGUF files if it exists
    existing_manifest = load_nexa_manifest(directory_path)
    
    model_files = {}
    if existing_manifest and "ModelFile" in existing_manifest:
        model_files = existing_manifest["ModelFile"].copy()
    
    # Process GGUF files
    for file_name in files:
        if file_name.endswith('.gguf'):
            # Use the new enum-based quantization extraction
            quantization_type = extract_quantization_from_filename(file_name)
            quant_level = quantization_type.value if quantization_type else "UNKNOWN"
            
            file_path = os.path.join(directory_path, file_name)
            file_size = 0
            if os.path.exists(file_path):
                try:
                    file_size = os.path.getsize(file_path)
                except (OSError, IOError):
                    pass
            
            model_files[quant_level] = {
                "Name": file_name,
                "Downloaded": True,
                "Size": file_size
            }
    
    manifest = {
        "Name": repo_id,
        "ModelType": PIPELINE_TO_MODEL_TYPE.get(old_metadata.get('pipeline_tag'), "other"),
        "PluginId": "llama_cpp",
        "ModelFile": model_files,
        "MMProjFile": {
            "Name": "",
            "Downloaded": False,
            "Size": 0
        },
        "TokenizerFile": {
            "Name": "",
            "Downloaded": False,
            "Size": 0
        },
        "ExtraFiles": None,
        # Preserve old metadata fields
        "pipeline_tag": old_metadata.get('pipeline_tag'),
        "download_time": old_metadata.get('download_time'),
        "avatar_url": old_metadata.get('avatar_url')
    }
    
    return manifest


def create_mlx_manifest(repo_id: str, files: List[str], directory_path: str, old_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Create MLX format manifest."""
    
    model_files = {}
    extra_files = []
    
    # Try different methods to extract quantization for MLX models
    quantization_type = detect_quantization_for_mlx(repo_id, directory_path)
    
    # Use the detected quantization or default to "DEFAULT"
    quant_level = quantization_type.value if quantization_type else "DEFAULT"
    
    for file_name in files:
        file_path = os.path.join(directory_path, file_name)
        file_size = 0
        if os.path.exists(file_path):
            try:
                file_size = os.path.getsize(file_path)
            except (OSError, IOError):
                pass
        
        # Check if this is a main model file (safetensors but not index files)
        if (file_name.endswith('.safetensors') and not file_name.endswith('.index.json')):
            model_files[quant_level] = {
                "Name": file_name,
                "Downloaded": True,
                "Size": file_size
            }
        else:
            # Add to extra files
            extra_files.append({
                "Name": file_name,
                "Downloaded": True,
                "Size": file_size
            })
    
    manifest = {
        "Name": repo_id,
        "ModelType": PIPELINE_TO_MODEL_TYPE.get(old_metadata.get('pipeline_tag'), "other"),
        "PluginId": "mlx",
        "ModelFile": model_files,
        "MMProjFile": {
            "Name": "",
            "Downloaded": False,
            "Size": 0
        },
        "TokenizerFile": {
            "Name": "",
            "Downloaded": False,
            "Size": 0
        },
        "ExtraFiles": extra_files if extra_files else None,
        # Preserve old metadata fields
        "pipeline_tag": old_metadata.get('pipeline_tag'),
        "download_time": old_metadata.get('download_time'),
        "avatar_url": old_metadata.get('avatar_url')
    }
    
    return manifest


def detect_model_type(files: List[str]) -> str:
    """Detect if this is a GGUF or MLX model based on file extensions."""
    has_gguf = any(f.endswith('.gguf') for f in files)
    has_safetensors = any(f.endswith('.safetensors') or 'safetensors' in f for f in files)
    
    if has_gguf:
        return "gguf"
    elif has_safetensors:
        return "mlx"
    else:
        # Default to mlx for other types
        return "mlx"


def create_manifest_from_files(repo_id: str, files: List[str], directory_path: str, old_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create appropriate manifest format based on detected model type.
    
    Args:
        repo_id: Repository ID
        files: List of files in the model directory
        directory_path: Path to the model directory
        old_metadata: Existing metadata (pipeline_tag, download_time, avatar_url)
        
    Returns:
        Dict containing the appropriate manifest format
    """
    model_type = detect_model_type(files)
    
    if model_type == "gguf":
        return create_gguf_manifest(repo_id, files, directory_path, old_metadata)
    else:  # mlx or other
        return create_mlx_manifest(repo_id, files, directory_path, old_metadata)


def save_manifest_with_files_metadata(repo_id: str, local_dir: str, old_metadata: Dict[str, Any]) -> None:
    """
    Create and save manifest based on files found in the directory.
    
    Args:
        repo_id: Repository ID
        local_dir: Local directory containing the model files
        old_metadata: Existing metadata to preserve
    """
    # Get list of files in the directory
    files = []
    try:
        for root, dirs, filenames in os.walk(local_dir):
            for filename in filenames:
                # Store relative path from the directory
                rel_path = os.path.relpath(os.path.join(root, filename), local_dir)
                files.append(rel_path)
    except (OSError, IOError):
        pass
    
    # Create appropriate manifest
    manifest = create_manifest_from_files(repo_id, files, local_dir, old_metadata)
    
    # Save manifest
    save_download_metadata(local_dir, manifest)
