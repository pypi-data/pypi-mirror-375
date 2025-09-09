import inspect
import logging

from .setup import setup_logging
class _ContextLogger:
    def __getattr__(self, name):
        """
            inspect.stack()은 호출 스택을 list로 반환
            [0] getattr
            [1] log.blah(...)
            [2] log.blah(...)를 호출한 모듈의 func
            [2]__name__으로 모듈명 가져오기
        """
        caller = inspect.stack()[2].frame.f_globals.get("__name__","qau")
        return getattr(logging.getLogger(caller),name)


log = _ContextLogger()

"""
qau.logging_utils
--------------------
logging 유틸 모음:
- setup_logging: log 출력 레벨/형태
- log: logging 헬퍼
"""

__version__ = "0.1.0"

__all__ = [
    "setup_logging",
    "log",
]