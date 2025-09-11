import os
from typing import List

from .utils import (
    get_current_username,
    validate_path_security,
    validate_boolean_env,
    apply_cap,
)
from .constants import (
    MAX_CACHE_SIZE_CAP_MB,
    MAX_CONCURRENT_SAVES_CAP,
    MIN_LOCAL_SPACE_MB,
    LOCK_TIMEOUT_CAP_SECONDS,
    INCOMPLETE_TIMEOUT_CAP_SECONDS,
    REQUIRED_TORCH_CACHE_DIR_PREFIX,
)


class Config:
    def _allowed_torch_cache_prefixes(self) -> List[str]:
        home_cache = os.path.expanduser("~/.cache")
        return ["/tmp/", "/cache/", f"{home_cache}"]

    # --------- dynamic properties ---------
    @property
    def TORCH_CACHE_DIR(self) -> str:
        """
        Validated torch compile cache directory.

        Env:
          - TORCHINDUCTOR_CACHE_DIR (optional)
            Defaults to /tmp/torchinductor_<username> if not set.
        """
        default_dir = f"/tmp/torchinductor_{get_current_username()}"
        chosen = os.getenv("TORCHINDUCTOR_CACHE_DIR", default_dir)
        return validate_path_security(
            chosen,
            self._allowed_torch_cache_prefixes(),
            "TORCHINDUCTOR_CACHE_DIR",
        )

    @property
    def B10FS_CACHE_DIR(self) -> str:
        """
        Validated B10FS cache directory.

        Env:
          - B10FS_CACHE_DIR (optional)
            Defaults to f"{REQUIRED_TORCH_CACHE_DIR_PREFIX}/compile_cache"
        """
        default_dir = f"{REQUIRED_TORCH_CACHE_DIR_PREFIX}/compile_cache"
        chosen = os.getenv("B10FS_CACHE_DIR", default_dir)
        return validate_path_security(
            chosen,
            [REQUIRED_TORCH_CACHE_DIR_PREFIX],
            "B10FS_CACHE_DIR",
        )

    @property
    def LOCAL_WORK_DIR(self) -> str:
        """
        Validated local work directory.

        Env:
          - LOCAL_WORK_DIR (optional, default: /app)
        """
        chosen = os.getenv("LOCAL_WORK_DIR", "/app")
        return validate_path_security(
            chosen,
            ["/app/", "/tmp/", "/cache/"],
            "LOCAL_WORK_DIR",
        )

    @property
    def MAX_CACHE_SIZE_MB(self) -> int:
        """
        Max size of a single cache archive (MB), capped for safety.

        Env:
          - MAX_CACHE_SIZE_MB (optional, default: 1024)
        Caps:
          - <= MAX_CACHE_SIZE_CAP_MB
        """
        requested = int(os.getenv("MAX_CACHE_SIZE_MB", 1024))
        return apply_cap(requested, MAX_CACHE_SIZE_CAP_MB, "MAX_CACHE_SIZE_MB")

    @property
    def MAX_CONCURRENT_SAVES(self) -> int:
        """
        Max concurrent save operations, capped for safety.

        Env:
          - MAX_CONCURRENT_SAVES (optional, default: 50)
        Caps:
          - <= MAX_CONCURRENT_SAVES_CAP
        """
        requested = int(os.getenv("MAX_CONCURRENT_SAVES", 50))
        return apply_cap(requested, MAX_CONCURRENT_SAVES_CAP, "MAX_CONCURRENT_SAVES")

    @property
    def REQUIRED_B10FS_SPACE_MB(self) -> int:
        """
        Estimated required space on B10FS (MB) based on concurrency and per-archive size.
        Lower-bounded to ensure a sane minimum.
        """
        return max(self.MAX_CONCURRENT_SAVES * self.MAX_CACHE_SIZE_MB, 100_000)

    @property
    def MIN_LOCAL_SPACE_MB(self) -> int:
        """Minimum required free space on local filesystem (MB)."""
        return MIN_LOCAL_SPACE_MB

    @property
    def BASETEN_FS_ENABLED(self) -> bool:
        """
        Whether Baseten FS features are enabled.

        Env:
          - BASETEN_FS_ENABLED (string "0" or "1", default "0")
        """
        raw = os.getenv("BASETEN_FS_ENABLED", "0")
        return validate_boolean_env(raw, "BASETEN_FS_ENABLED")

    @property
    def CLEANUP_LOCK_TIMEOUT_SECONDS(self) -> int:
        """
        Timeout for cleaning up lock files (seconds).

        Env:
          - CLEANUP_LOCK_TIMEOUT_SECONDS (optional, default: 30)
        Caps:
          - <= LOCK_TIMEOUT_CAP_SECONDS
        """
        requested = int(os.getenv("CLEANUP_LOCK_TIMEOUT_SECONDS", 30))
        return apply_cap(
            requested, LOCK_TIMEOUT_CAP_SECONDS, "CLEANUP_LOCK_TIMEOUT_SECONDS"
        )

    @property
    def CLEANUP_INCOMPLETE_TIMEOUT_SECONDS(self) -> int:
        """
        Timeout for cleaning up incomplete files (seconds).

        Env:
          - CLEANUP_INCOMPLETE_TIMEOUT_SECONDS (optional, default: 60)
        Caps:
          - <= INCOMPLETE_TIMEOUT_CAP_SECONDS
        """
        requested = int(os.getenv("CLEANUP_INCOMPLETE_TIMEOUT_SECONDS", 60))
        return apply_cap(
            requested,
            INCOMPLETE_TIMEOUT_CAP_SECONDS,
            "CLEANUP_INCOMPLETE_TIMEOUT_SECONDS",
        )


config = Config()
