import time
import os
import uuid
import glob
from loguru import logger
from typing import Optional

def get_image_lifetime() -> int:
    lifetime_hours = os.getenv("IMAGE_LIFETIME_HOURS", "24")
    try:
        return int(lifetime_hours) * 3600
    except ValueError:
        logger.warning(
            f"Invalid IMAGE_LIFETIME_HOURS value: {lifetime_hours}, using default 24 hours"
        )
        return 24 * 3600

def cleanup_expired_files(
    data_dir: str = "data", lifetime_seconds: Optional[int] = None
) -> int:
    if lifetime_seconds is None:
        lifetime_seconds = get_image_lifetime()

    if not os.path.exists(data_dir):
        return 0

    current_time = time.time()
    cleanup_count = 0

    pattern = os.path.join(data_dir, "*")
    files = glob.glob(pattern)

    for file_path in files:
        if os.path.isfile(file_path):
            file_mtime = os.path.getmtime(file_path)

            if current_time - file_mtime > lifetime_seconds:
                try:
                    os.remove(file_path)
                    cleanup_count += 1
                    logger.info(f"Cleaned up expired file: {file_path}")
                except OSError as e:
                    logger.error(f"Failed to remove file {file_path}: {e}")

    if cleanup_count > 0:
        logger.info(f"Cleaned up {cleanup_count} expired files")

    return cleanup_count

def generate_data_path(suffix: str = "html", namespace: str = "default") -> tuple[str, str]:
    os.makedirs("data", exist_ok=True)
    filename = f"{namespace}_{int(time.time())}_{uuid.uuid4().hex[:8]}.{suffix}"
    return os.path.join("data", filename), os.path.abspath(
        os.path.join("data", filename)
    )
