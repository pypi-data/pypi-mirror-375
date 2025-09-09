from playwright.sync_api import Locator


def next_sibling(target,step:int=1) -> Locator:
    return target.locator(f"xpath=following-sibling::*[{step}]")

def prev_sibling(target, step: int = 1) -> Locator:
    return target.locator(f"xpath=preceding-sibling::*[{step}]")