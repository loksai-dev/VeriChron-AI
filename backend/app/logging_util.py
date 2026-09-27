import logging

log = logging.getLogger("verichron")


def configure_logging() -> None:
    if log.handlers:
        return
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def agent_log(section: str, message: str) -> None:
    log.info("[%s] %s", section.upper(), message)
