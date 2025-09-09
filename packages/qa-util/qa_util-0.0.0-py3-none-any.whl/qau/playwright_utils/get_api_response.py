from typing import Callable, MutableMapping, Any
from playwright.sync_api import Page, Response
from playwright.sync_api import Error as PlaywrightError
from qau.logging_utils import log
def get_api_response(driver:Page,
                     action:Callable[[], None],
                     url:str,
                     key:str,
                     store:MutableMapping[str,Any]
                     ):

    log.debug("Waiting for API response: url=%s", url)

    # 응답 기다리면서 액션 실행
    with driver.expect_response(
            lambda res: res.url.split("?")[0].endswith(url)
                        and res.request.method.upper() != "HEAD"
    ) as r:
        action()

    response:Response = r.value

    if response.ok:
        try:
            res_body = response.body()
            if not res_body:
                store[key] = {}
                log.info("API response empty body → stored {} at key=%s", key)
            else:
                store[key] = response.json()
                log.info("API JSON stored under key=%s", key)
        except PlaywrightError as e:
            log.exception("key:%s %s",key,e)

    else:
        log.error("API request failed: %s %s [status=%s]",
                     response.request.method, response.url, response.status)