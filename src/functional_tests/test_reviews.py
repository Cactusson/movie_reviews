from playwright.sync_api import expect

from functional_tests.pages.home_page import HomePage


def test_navigating_between_reviews(live_server, page):
    home_page = HomePage(page)

    # Alice wants to check out the new website which aggregates movie reviews
    # She goes to the home page
    home_page.navigate(live_server)

    # Alice sees that the title says something about `reviews``
    expect(page).to_have_title("reviews")
