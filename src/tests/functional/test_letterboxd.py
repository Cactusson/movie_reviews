import re

from django.core import mail
from playwright.sync_api import expect

from .pages.home_page import HomePage


def test_letterboxd(
    live_server,
    page,
    close_db_connections,
    king_of_color,
    sound_of_falling,
    night_patrol,
    mocked_letterboxd_feed,
):
    home_page = HomePage(page)
    home_page.navigate(live_server)

    # Alice has heard of a new feature: now you can connect your Letterboxd account
    # and see the reviews of the movies you have recently watched.
    # She wants to try it out

    # She needs to log in first
    navbar = page.get_by_role("navigation")
    email_field = navbar.get_by_placeholder("Enter your email to log in")
    email_field.fill("test@example.com")
    email_field.press("Enter")
    email = mail.outbox.pop()
    url_search = re.search(r"http:\/\/.+?\/.+", email.body)
    url = url_search.group(0)
    page.goto(url)

    # Alice goes to her profile page
    navbar.get_by_text("Profile").click()

    # There is an input field for the Letterboxd account
    letterboxd_field = page.get_by_label("Your Letterboxd account")
    expect(letterboxd_field).to_be_visible()

    # She fills in her Letterboxd username
    letterboxd_field.fill("alice")

    # And clicks on the `Save` button
    save_button = page.get_by_role("button", name="Save")
    expect(save_button).to_be_visible()
    save_button.click()

    # Alice goes back to the home page
    home_page.navigate(live_server)

    # There is a new section titled `Letterboxd`
    letterboxd_section = page.get_by_text("Letterboxd")
    expect(letterboxd_section).to_be_visible()

    # She clicks on it
    letterboxd_section.click()

    # One of the movies Alice has seen recently is called `Night Patrol`
    # Sure enough, it is listed on the page
    first_review = page.locator("div.review").first
    expect(first_review).to_be_visible()
    expect(first_review).to_contain_text("Night Patrol")
