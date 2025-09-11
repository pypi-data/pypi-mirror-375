import asyncio
import os
import tempfile
from typing import Awaitable, Literal, overload

import aiofiles
from filelock import AsyncFileLock, FileLock

from .get_lock_file_path import get_lock_file_path


@overload
def write_binary(
    mode: Literal["sync"], file_path: str | os.PathLike[str], raw_data: bytes
) -> None: ...


@overload
def write_binary(
    mode: Literal["async"], file_path: str | os.PathLike[str], raw_data: bytes
) -> Awaitable[None]: ...


def write_binary(
    mode: Literal["sync", "async"], file_path: str | os.PathLike[str], raw_data: bytes
) -> None | Awaitable[None]:
    """
    Write binary data to a file

    Args:
        model (Literal["async", "sync"]): Execution mode, either "async" or "sync"
        file_path (str | os.PathLike[str]): Path to the file to write
        raw_data (bytes): Binary data to write
    """
    # Normalize the file path
    file_path = os.path.expanduser(os.path.expandvars(os.fspath(file_path)))

    # Ensure the directory exists
    if dirname := os.path.dirname(file_path):
        os.makedirs(dirname, exist_ok=True)

    # Define the lock file path
    lock_file_path = get_lock_file_path(file_path)

    # Create a temporary file in the same directory to achieve atomic operation
    fd, temp_file_path = tempfile.mkstemp(
        dir=dirname if dirname else None,
        prefix=".write_binary_",
        suffix=".tmp",
    )
    os.close(fd)

    # Function to clean up temporary file
    def _cleanup_temp_file() -> None:
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception:
                pass

    # Synchronous version of the function
    def _sync() -> None:
        lock = FileLock(lock_file_path)

        try:
            with lock:
                # Write to the temporary file
                with open(temp_file_path, "wb") as temp_file:
                    temp_file.write(raw_data)
                    temp_file.flush()
                    os.fsync(temp_file.fileno())

                # Atomic replace
                os.replace(temp_file_path, file_path)

        except Exception:
            _cleanup_temp_file()
            raise

    # Asynchronous version of the function
    async def _async() -> None:
        lock = AsyncFileLock(lock_file_path)

        try:
            async with lock:
                # Write to the temporary file
                async with aiofiles.open(temp_file_path, "wb") as temp_file:
                    await temp_file.write(raw_data)
                    await temp_file.flush()
                    await asyncio.to_thread(os.fsync, temp_file.fileno())

                # Atomic replace
                os.replace(temp_file_path, file_path)

        except Exception:
            _cleanup_temp_file()
            raise

    if mode == "sync":
        _sync()
        return None
    else:
        return _async()
