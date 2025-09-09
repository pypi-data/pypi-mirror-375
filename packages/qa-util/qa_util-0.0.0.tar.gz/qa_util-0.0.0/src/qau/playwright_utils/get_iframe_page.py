from typing import Optional

from playwright.sync_api import Page, Frame
from playwright.sync_api import Error as PlaywrightError
from qau.logging_utils import log


def get_iframe_page(page:Page,value:str,by:str="id") -> Optional[Frame]:
    frame = None
    try:
        if by == 'id':
            frame = page.wait_for_selector(f"iframe#{value}").content_frame()
        elif by == 'title':
            frame = page.wait_for_selector(f"iframe[title='{value}']").content_frame()
        elif by == 'class':
            frame = page.wait_for_selector(value).content_frame()
        else:
            raise ValueError(f"Unsupported '{by}'")

        if frame is None:
            log.warning("iframe not found (by=%s, value=%s)", by, value)
        else:
            log.info("iframe found (by=%s, value=%s, url=%s)", by, value, frame.url)
        return frame
    except PlaywrightError as e:
        log.exception("iframe search error (by=%s, value=%s): %s", by, value, e)
        log.exception("iframe search error (by=%s, value=%s): %s", by, value, e)
        return frame

