import inspect
import logging

from rich.logging import RichHandler

from rich.traceback import install as RTI

# setup_logging("DEBUG") conftest.py 에 명시 필요
def setup_logging(level: str = "INFO", name: str = "QAU") -> logging.Logger:
    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)
    
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[RichHandler(rich_tracebacks=True, show_time=False, show_path=False)],
    )

    RTI(width=120, show_locals=False)
    return logging.getLogger(name)