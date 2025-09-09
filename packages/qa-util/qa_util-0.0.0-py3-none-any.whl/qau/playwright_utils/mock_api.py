import json
from typing import Union

from exceptiongroup import suppress
from playwright.sync_api import Page


def create_mock_api(
        page:Page,
        url_pattern: str,
        status: int = 200,
        body: Union[dict,list,str,None] = None,
        once: bool = False
):
    payload = body

    # body가 dict || list 일 경우
    if isinstance(body,(dict,list)):
        payload = json.dumps(body)

    def _handler(route, _request):
        route.fulfill(
            status = status,
            body = payload,
        )
        if once:
            # 이미 unroute 가 되었을 수도 있어서 suppress 처리
            with suppress(Exception):
                page.unroute(url_pattern,_handler)
    page.route(url_pattern,_handler)

def remove_mock_api(
        page:Page,
        url_pattern: str,
):
    page.unroute(url_pattern)
