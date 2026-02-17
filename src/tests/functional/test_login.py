import re

from django.core import mail
from playwright.sync_api import expect


TEST_EMAIL = "test@example.com"
SUBJECT = "Your Login Link for Movie Reviews"


def test_login_using_magic_link(live_server, page):
    page.goto(live_server.url)

    # Alice notices a `Log In` section in the navbar
    # It's telling her to enter her email address and she does
    navbar = page.get_by_role("navigation")
    email_field = navbar.get_by_label("Enter your email to log in")
    expect(email_field).to_be_visible()
    email_field.fill(TEST_EMAIL)
    email_field.press("Enter")

    # A message appears telling her an email has been sent
    expect(page.locator("body")).to_contain_text(
        "Check your email",
    )

    # She checks her email and finds a message
    email = mail.outbox.pop()
    assert TEST_EMAIL in email.to
    assert email.subject == SUBJECT

    # It has a URL link in it
    assert "Use this link to log in" in email.body
    url_search = re.search(r"http:\/\/.+?\/.+", email.body)
    assert url_search is not None, f"Could not find url in email body:\n{email.body}"
    url = url_search.group(0)
    assert live_server.url in url

    # she clicks it
    page.goto(url)

    # she is logged in!
    expect(page.locator("nav")).to_contain_text(TEST_EMAIL)

    # Now she logs out
    page.locator("nav").get_by_text("Log Out").click()

    # She is logged out
    expect(page.locator("nav")).not_to_contain_text(TEST_EMAIL)
