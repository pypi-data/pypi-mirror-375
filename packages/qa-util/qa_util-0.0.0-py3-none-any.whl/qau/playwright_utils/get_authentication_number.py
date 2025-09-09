
import os
import random
import string
import time

from playwright.sync_api import Page, expect
from playwright.sync_api import Error as PlaywrightError
from qau.logging_utils import log


def _make_new_id() -> str:
    random_string = string.ascii_letters + string.digits
    char6 =  ''.join(random.choices(random_string,k=6))
    new_id = "it.test+"+char6+"@wonderwall.kr"
    os.environ["STORE_ID"] = new_id
    return new_id

# Email 인증
def get_gmail_auth_number(page:Page,store):
    new_id = _make_new_id()
    base_id = os.getenv("MOTHER_ID")
    base_pw = os.getenv("MOTHER_PW")
    if not all([new_id,base_id,base_pw]):
        raise RuntimeError("환경변수 부족: MOTHER_ID / MOTHER_PW 를 확인하세요.")

    gmail_tab=page.context.new_page()
    try:
        gmail_tab.goto("https://workspace.google.com/intl/ko/gmail/",wait_until="domcontentloaded")
        expect(gmail_tab.locator('div.header__aside > a[aria-label="Open Link Gmail에 로그인 Page New tab"]')).to_be_visible(timeout=10000)

        login_btn = gmail_tab.locator('div.header__aside > a[aria-label="Open Link Gmail에 로그인 Page New tab"]')
        if login_btn.is_visible():
            login_btn.click()


        if gmail_tab.locator('#identifierId').is_visible():
            id_input = gmail_tab.locator('#identifierId')
            id_input.type(os.getenv("MOTHER_ID"))

            next_btn = gmail_tab.get_by_role("button", name="다음")
            next_btn.click()

            expect(gmail_tab.locator('input[name="Passwd"]')).to_be_visible(timeout=10000)

            pw_input = gmail_tab.locator('input[name="Passwd"]')
            pw_input.type(os.getenv("MOTHER_PW"))
            next_btn.click()

            gmail_tab.wait_for_load_state("load")

            mail_row = gmail_tab.locator('div[gh="tl"] tbody > tr')
            expect(mail_row.first).to_be_visible(timeout=20000)

            mail_row.click()
            time.sleep(3)

            mail_box = gmail_tab.locator('a',has_text="받은편지함")

            timeout_sec = 30

            deadline = time.monotonic() + timeout_sec

            while time.monotonic() < deadline:
                if gmail_tab.locator(f'span[email="{new_id}"]').is_visible():
                    break
                mail_box.click()
                mail_row.click()
                time.sleep(1)
            else:
                raise TimeoutError("30초 내에 메일이 오지 않았습니다.")

            style="margin-top:24px;background-color:#f3f3f3;color:#fb4866;padding:16px;line-height:29px;font-size:24px;font-weight:700"
            auth_number = gmail_tab.locator(f'div[{style}]')

            count = auth_number.count()
            last_auth_number = auth_number.nth(count-1)
            store["authNumber"]=last_auth_number.text_content()

    except PlaywrightError as e:
        log.error("Gmail 자동화 중 PlaywrightError: %s", e)
        raise
    finally:
        gmail_tab.close()

