import logging
import os
from typing import BinaryIO, overload

from .._operations.detect_with_dictionary import detect_with_dictionary
from .._operations.detect_with_mimetypes import detect_with_mimetypes
from .._operations.detect_with_puremagic import detect_with_puremagic
from .apply_mime_alias import apply_mime_alias

logger = logging.getLogger(__name__)


@overload
def detect_mime_type(
    *,
    raw_data: bytes | None = None,
    stream: BinaryIO | None = None,
    file_name_hint: str | os.PathLike[str] | None = None,
    # normalize_mime_alias options
    mime_aliases: dict[str, str] | None = None,
    # detect_with_dictionary options
    custom_mime_types: dict[str, str] | None = None,
    multi_extensions: set[str] | None = None,
    archive_extensions: set[str] | None = None,
    compression_extensions: set[str] | None = None,
    encryption_extensions: set[str] | None = None,
) -> str | None: ...


@overload
def detect_mime_type(
    *,
    raw_data: bytes | None = None,
    stream: BinaryIO | None = None,
    file_name_hint: str | os.PathLike[str] | None = None,
    # normalize_mime_alias options
    mime_aliases: dict[str, str] | None = None,
    # detect_with_dictionary options
    custom_mime_types: dict[str, str] | None = None,
    multi_extensions: set[str] | None = None,
    archive_extensions: set[str] | None = None,
    compression_extensions: set[str] | None = None,
    encryption_extensions: set[str] | None = None,
    default: str,
) -> str: ...


def detect_mime_type(
    *,
    raw_data: bytes | None = None,
    stream: BinaryIO | None = None,
    file_name_hint: str | os.PathLike[str] | None = None,
    # normalize_mime_alias options
    mime_aliases: dict[str, str] | None = None,
    # detect_with_dictionary options
    custom_mime_types: dict[str, str] | None = None,
    multi_extensions: set[str] | None = None,
    archive_extensions: set[str] | None = None,
    compression_extensions: set[str] | None = None,
    encryption_extensions: set[str] | None = None,
    default: str | None = None,
) -> str | None:
    """
    Detect the MIME type of a file or data stream using multiple detection methods.

    This function employs a multi-stage approach to determine the MIME type with high accuracy:

    Detection Strategy:
        1. **Content-based detection**: Uses `puremagic` to analyze raw data or file streams
           by examining file headers and magic bytes for precise identification.
        2. **Custom dictionary lookup**: Matches file extensions against a configurable
           mapping that handles complex cases like multi-part extensions (.tar.gz).
        3. **Standard library fallback**: Uses Python's built-in `mimetypes` module
           for standard file extension to MIME type mapping.

    All detected MIME types are automatically normalized using configurable aliases
    to ensure consistency with modern standards (e.g., "application/x-yaml" → "application/yaml").

    Args:
        raw_data (bytes | None): Raw binary data to analyze. Takes precedence over stream
            if both are provided.
        stream (BinaryIO | None): Binary file stream to analyze. Used when raw_data is None.
        file_name_hint (str | os.PathLike[str] | None): File name or path used as a hint
            for extension-based detection. Required when raw_data and stream are None.

        mime_aliases (dict[str, str] | None): Custom MIME type aliases for normalization.
            Merged with default settings, with custom values taking precedence.
            Example: {"application/x-yaml": "application/yaml"}

        custom_mime_types (dict[str, str] | None): Custom extension to MIME type mapping.
            Example: {".myext": "application/x-custom"}
        multi_extensions (set[str] | None): Multi-part extensions to recognize.
            See `kiarina.utils.ext.extract_extension` for details.
        archive_extensions (set[str] | None): Archive-related extensions.
            See `kiarina.utils.ext.extract_extension` for details.
        compression_extensions (set[str] | None): Compression-related extensions.
            See `kiarina.utils.ext.extract_extension` for details.
        encryption_extensions (set[str] | None): Encryption-related extensions.
            See `kiarina.utils.ext.extract_extension` for details.

        default (str | None): Default MIME type to return if detection fails. Default is None.

    Returns:
        (str | None): The detected and normalized MIME type, or default if detection fails.

    Note:
        At least one of raw_data, stream, or file_name_hint must be provided.
        Content-based detection (raw_data/stream) is more reliable than extension-based detection.
    """
    # Try to detect MIME type using puremagic
    if raw_data is not None or stream is not None:
        if mime_type := detect_with_puremagic(
            raw_data=raw_data, stream=stream, file_name_hint=file_name_hint
        ):
            return apply_mime_alias(mime_type, mime_aliases=mime_aliases)

    # Try to detect MIME type using a dictionary based on file name hint
    if file_name_hint is not None:
        if mime_type := detect_with_dictionary(
            file_name_hint,
            custom_mime_types=custom_mime_types,
            multi_extensions=multi_extensions,
            archive_extensions=archive_extensions,
            compression_extensions=compression_extensions,
            encryption_extensions=encryption_extensions,
        ):
            return apply_mime_alias(mime_type, mime_aliases=mime_aliases)

    # Try to detect MIME type using the mimetypes module
    if file_name_hint is not None:
        if mime_type := detect_with_mimetypes(file_name_hint):
            return apply_mime_alias(mime_type, mime_aliases=mime_aliases)

    # If no MIME type is found, return default
    logger.debug(f"No MIME type found for file: {file_name_hint}")
    return default
