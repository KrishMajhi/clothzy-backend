import logging

logger = logging.getLogger("auth_logger")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logging.info("TEST LOG")
logger.warning("TEST WARNING")