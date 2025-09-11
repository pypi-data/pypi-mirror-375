from enum import Enum, auto

# ----- Hard caps & fixed thresholds (security / safety) -----
MAX_CACHE_SIZE_CAP_MB: int = 1 * 1024  # 1GB hard limit per cache archive
MAX_CONCURRENT_SAVES_CAP: int = 100  # Max concurrent save ops (estimate for space calc)

# Minimum required space on local disk
MIN_LOCAL_SPACE_MB: int = 50 * 1024  # 50GB

# Cleanup hard limits
LOCK_TIMEOUT_CAP_SECONDS: int = 3600  # 1 hour hard limit
INCOMPLETE_TIMEOUT_CAP_SECONDS: int = 7200  # 2 hours hard limit

# Allowed / required path patterns
REQUIRED_TORCH_CACHE_DIR_PREFIX: str = "/cache/model"  # For B10FS cache dir validation

# File naming patterns
CACHE_FILE_EXTENSION: str = ".tar.gz"
CACHE_LATEST_SUFFIX: str = ".latest"
CACHE_INCOMPLETE_SUFFIX: str = ".incomplete"
CACHE_PREFIX: str = "cache_"

# Monitoring cadence
SPACE_MONITOR_CHECK_INTERVAL_SECONDS: float = 0.5


# ----- Enums -----
class WorkerStatus(Enum):
    """Status values for worker process results."""

    SUCCESS = auto()
    ERROR = auto()
    CANCELLED = auto()


class OperationStatus(Enum):
    """Status values for all b10-transfer operations (load, save, transfer)."""

    SUCCESS = auto()
    ERROR = auto()
    DOES_NOT_EXIST = auto()  # Used by load operations when cache file not found
    SKIPPED = auto()  # Used by load/save ops when operation not needed
