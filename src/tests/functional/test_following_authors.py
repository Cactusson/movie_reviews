import re

from django.core import mail
from playwright.sync_api import expect

from .pages.home_page import HomePage


def test_following_authors(
    live_server,
    page,
    close_db_connections,
    king_of_color,
    sound_of_falling,
    night_patrol,
):
    home_page = HomePage(page)
    home_page.navigate(live_server)

    # Alice has heard of a new feature: now you can follow authors and see
    # only the reviews of those authors you're following.
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

    # Now she needs to navigate to the `Authors` page
    authors_link = page.get_by_role("navigation").get_by_text("Authors")
    expect(authors_link).to_be_visible()
    authors_link.click()

    # She sees a couple of authors and clicks on the one called `Matt Zoller Seitz`
    mzs_link = page.get_by_text("Matt Zoller Seitz")
    expect(mzs_link).to_be_visible()
    mzs_link.click()

    # Alice sees the `Follow` button
    follow_button = page.get_by_text("Follow", exact=True)
    expect(follow_button).to_be_visible()
    follow_button.click()

    # `Follow` button has changed: Now it says `Unfollow`
    expect(page.get_by_text("Follow", exact=True)).not_to_be_visible()
    expect(page.get_by_text("Unfollow", exact=True)).to_be_visible()

    # Alice goes back to the home page
    home_link = page.get_by_role("navigation").get_by_text("Home")
    expect(home_link).to_be_visible()
    home_link.click()

    # Now she sees only reviews by Matt Zoller Seitz and not by other authors
    expect(page.locator("div.review")).to_have_count(2)
    reviews = page.locator("div.review").all()
    for review in reviews:
        expect(review).to_contain_text("Matt Zoller Seitz")
