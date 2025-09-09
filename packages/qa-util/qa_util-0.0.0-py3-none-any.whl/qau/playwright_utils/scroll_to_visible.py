import pytest
from playwright.sync_api import Page, Locator
from playwright.sync_api import Error as PlaywrightError
from qau.logging_utils import log


def scroll_to_visible(page:Page,
                                container:Locator,
                                target:Locator,
                                steps:int = 100,
                                max_steps:int = 50,
                                min_scroll_px: int = 900,
                                timeout:int = 200
                                ):
    page.wait_for_load_state('domcontentloaded')
    container_handler = container.element_handle()
    if not container_handler:
        pytest.fail("container를 찾을 수 없습니다.")
        return False

    prev_scroll = 0
    try:
        for i in range(max_steps):
            try:
                if target.is_visible():
                    return True
            except PlaywrightError:
                pass
            scroll_height = page.evaluate("(el) => el.scrollHeight",container_handler)
            scroll_height = max(scroll_height, min_scroll_px)

            if prev_scroll >= scroll_height+100:
                pytest.fail("페이지 끝까지 내렸지만 요소가 없음")
                return False

            else:
                page.mouse.wheel(0, steps)
                page.wait_for_timeout(timeout)
                prev_scroll += steps
                log.debug("scroll step=%d, prev=%d, scroll_height=%d", i, prev_scroll, scroll_height)

    except PlaywrightError as e:
        log.error("스크롤 중 PlaywrightError: %s", e)
        pytest.fail(f"스크롤 중 오류: {e}")
        return False