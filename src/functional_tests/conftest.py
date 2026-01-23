import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture
def page(request):
    headed = request.config.getoption("--headed")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=not headed)
        page = browser.new_page()
        yield page
        browser.close()


# @pytest.fixture
