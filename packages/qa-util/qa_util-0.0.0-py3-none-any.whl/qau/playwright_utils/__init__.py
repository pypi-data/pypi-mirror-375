from .get_iframe_page import get_iframe_page
from .sibling_util import next_sibling, prev_sibling
from .get_api_response import get_api_response
from .get_authentication_number import get_gmail_auth_number
from .mock_api import create_mock_api, remove_mock_api
"""
qau.playwright_utils
--------------------
Playwright 유틸 모음:
- get_api_response: API 응답 캡처 & 저장
- get_iframe_page: iframe 접근 헬퍼
- next_sibling / prev_sibling: DOM 탐색 헬퍼
- get_gmail_auth_number: Gmail 인증 코드 헬퍼
"""

__version__ = "0.1.0"

__all__ = [
    "get_api_response",
    "next_sibling",
    "prev_sibling",
    "get_iframe_page",
    "get_gmail_auth_number",
    "create_mock_api",
    "remove_mock_api"
]