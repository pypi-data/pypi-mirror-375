"""
MIME type detection and processing utilities.

This module provides comprehensive functionality for:
- Detecting MIME types from binary data, file streams, and file names
- Creating MIME-typed data containers (MIMEBlob)
- Normalizing MIME types using configurable aliases
- Multi-stage detection using content analysis and extension mapping

Key Features:
    - **Content-based detection**: Uses puremagic to analyze file headers and magic bytes
    - **Extension-based detection**: Supports complex multi-part extensions (.tar.gz, .tar.gz.gpg)
    - **MIME type normalization**: Applies configurable aliases for consistency
    - **Data container**: MIMEBlob class for handling MIME-typed binary data

Detection Strategy:
    1. Content analysis using puremagic (most reliable)
    2. Custom dictionary lookup for complex extensions
    3. Standard library mimetypes fallback
    4. Automatic MIME type alias normalization

Examples:
    >>> import kiarina.utils.mime as km
    >>>
    >>> # Detect MIME type from binary data
    >>> mime_type = km.detect_mime_type(raw_data=jpeg_bytes)
    >>> print(mime_type)  # "image/jpeg"
    >>>
    >>> # Detect from file name
    >>> mime_type = km.detect_mime_type(file_name_hint="document.tar.gz")
    >>> print(mime_type)  # "application/gzip"
    >>>
    >>> # Create MIMEBlob from data
    >>> blob = km.create_mime_blob(jpeg_bytes)
    >>> print(blob.mime_type)  # "image/jpeg"
    >>> print(blob.ext)        # ".jpg"
    >>>
    >>> # Create MIMEBlob from text
    >>> blob = km.MIMEBlob("text/plain", raw_text="Hello World")
    >>> print(blob.raw_base64_url)  # "data:text/plain;base64,SGVsbG8gV29ybGQ="

Configuration:
    MIME type detection behavior can be customized through environment variables:
    - KIARINA_UTILS_MIME_CUSTOM_MIME_TYPES: Custom extension to MIME type mapping
    - KIARINA_UTILS_MIME_MIME_ALIASES: MIME type aliases for normalization
    - KIARINA_UTILS_MIME_HASH_ALGORITHM: Hash algorithm for MIMEBlob (default: sha256)

Note:
    For optimal content-based detection, install the optional puremagic dependency.
    Without it, detection falls back to extension-based methods only.
"""

# pip install kiarina-utils-mime
import logging
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.apply_mime_alias import apply_mime_alias
    from ._helpers.create_mime_blob import create_mime_blob
    from ._helpers.detect_mime_type import detect_mime_type
    from ._models.mime_blob import MIMEBlob
    from .settings import settings_manager

__version__ = "1.0.0"

__all__ = [
    # .helpers
    "apply_mime_alias",
    "create_mime_blob",
    "detect_mime_type",
    # .model
    "MIMEBlob",
    # .settings
    "settings_manager",
]

logging.getLogger(__name__).addHandler(logging.NullHandler())


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

    module_map = {
        # .helpers
        "apply_mime_alias": "._helpers.apply_mime_alias",
        "create_mime_blob": "._helpers.create_mime_blob",
        "detect_mime_type": "._helpers.detect_mime_type",
        # .model
        "MIMEBlob": "._models.mime_blob",
        # .settings
        "settings_manager": ".settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
