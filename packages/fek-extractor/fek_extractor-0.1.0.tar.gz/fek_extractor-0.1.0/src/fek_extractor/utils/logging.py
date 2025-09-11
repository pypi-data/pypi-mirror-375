from __future__ import annotations

import logging


def get_logger(name: str = "fek_extractor") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        # Default configuration if user didn't configure logging
        handler = logging.StreamHandler()
        fmt = logging.Formatter("%(levelname)s %(name)s: %(message)s")
        handler.setFormatter(fmt)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
