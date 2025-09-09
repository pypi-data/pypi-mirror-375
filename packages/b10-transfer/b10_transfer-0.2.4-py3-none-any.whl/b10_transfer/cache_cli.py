# src/b10_tcache/cli.py
import os

VLLM_CACHE_DIR = os.getenv("VLLM_CACHE_ROOT", "~/.cache/vllm")
os.environ["TORCHINDUCTOR_CACHE_DIR"] = VLLM_CACHE_DIR

from .cache import load_compile_cache, save_compile_cache

import logging
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True)
class WaitCfg:
    url: str
    timeout_s: float
    interval_s: float
    loglevel: str


DEFAULT_URL = os.getenv("B10_TRANSFER_VLLM_URL", "http://127.0.0.1:8000/v1/models")
DEFAULT_TIMEOUT_S = float(os.getenv("B10_TRANSFER_TIMEOUT_S", "1800"))  # 30m default
DEFAULT_INTERVAL_S = float(os.getenv("B10_TRANSFER_INTERVAL_S", "2"))
DEFAULT_LOGLEVEL = os.getenv("B10_TRANSFER_CLI_LOGLEVEL", "INFO").upper()


def _setup_logging(level: str) -> logging.Logger:
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    return logging.getLogger("b10_transfer.cli")


def _http_ok(url: str, logger: logging.Logger) -> bool:
    """
    Return True if vLLM readiness looks good.

    We consider it 'ready' if GET <url> returns 200.
    """
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status != 200:
                return False
            return True
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        logger.debug("Readiness probe failed: %s", e)
        return False
    except Exception as e:
        logger.debug("Unexpected readiness error: %s", e)
        return False


def _wait_for_ready(cfg: WaitCfg, logger: logging.Logger) -> bool:
    t0 = time.monotonic()
    logger.info(
        "Waiting for vLLM readiness at %s (timeout=%.0fs, interval=%.1fs)",
        cfg.url,
        cfg.timeout_s,
        cfg.interval_s,
    )

    while True:
        if _http_ok(cfg.url, logger):
            logger.info("vLLM reported ready at %s", cfg.url)
            return True
        if time.monotonic() - t0 > cfg.timeout_s:
            logger.error(
                "Timed out after %.0fs waiting for vLLM readiness.", cfg.timeout_s
            )
            return False

        time.sleep(cfg.interval_s)


def main() -> None:
    cfg = WaitCfg(
        url=DEFAULT_URL,
        timeout_s=DEFAULT_TIMEOUT_S,
        interval_s=DEFAULT_INTERVAL_S,
        loglevel=DEFAULT_LOGLEVEL,
    )

    logger = _setup_logging(cfg.loglevel)

    # 1) Preload any existing cache (non-fatal on error)
    try:
        logger.info("Calling load_compile_cache() …")
        load_compile_cache()
        logger.info("load_compile_cache() returned.")
    except Exception as e:
        logger.exception("load_compile_cache() failed: %s", e)

    # 2) Wait for vLLM HTTP to be ready
    try:
        ready = _wait_for_ready(cfg, logger)
    except Exception as e:
        logger.exception("Readiness wait crashed: %s", e)
        sys.exit(3)

    if not ready:
        # Loop timed out. Safe exit.
        sys.exit(4)

    # 3) Save compile cache
    try:
        logger.info("Calling save_compile_cache() …")
        save_compile_cache()
        logger.info("save_compile_cache() completed.")
    except Exception as e:
        logger.exception("save_compile_cache() failed: %s", e)
        sys.exit(5)

    logger.info("vLLM automatic torch compile cache done.")
