import re

from playwright.sync_api import expect

from .pages.home_page import HomePage


def test_navigating_between_reviews(
    live_server, page, night_patrol, king_of_color, sound_of_falling
):
    home_page = HomePage(page)

    # Alice wants to check out the new website which aggregates movie reviews
    # She goes to the home page
    home_page.navigate(live_server)

    # Alice sees that the title says something about `reviews`
    expect(page).to_have_title(re.compile(r"reviews", re.IGNORECASE))

    # There are currently three reviews published
    reviews = page.locator("div.review").all()
    assert len(reviews) == 3

    # The most recent one (the first on the page) has title `Night Patrol`
    first_review = reviews[0]
    expect(first_review).to_contain_text("Night Patrol")

    # The review's author appears to be `Matt Zoller Seitz`
    expect(first_review).to_contain_text("Matt Zoller Seitz")
