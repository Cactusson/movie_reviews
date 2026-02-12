import re

from playwright.sync_api import expect

from .pages.home_page import HomePage


def test_navigating_between_reviews(
    live_server,
    page,
    close_db_connections,
    king_of_color,
    sound_of_falling,
    night_patrol,
):
    home_page = HomePage(page)

    # Alice wants to check out the new website which aggregates movie reviews
    # She goes to the home page
    home_page.navigate(live_server)

    # Alice sees that the title says something about `reviews`
    expect(page).to_have_title(re.compile(r"reviews", re.IGNORECASE))

    # There are currently three reviews published
    expect(page.locator("div.review")).to_have_count(3)
    reviews = page.locator("div.review").all()

    # The most recent one (the first on the page) has title `Night Patrol`
    first_review = reviews[0]
    expect(first_review).to_contain_text("Night Patrol")

    # The review's author appears to be `Matt Zoller Seitz`
    expect(first_review).to_contain_text("Matt Zoller Seitz")

    # Alice clicks on the title and is redirected to this review's page
    first_review.get_by_text("Night Patrol", exact=True).click()
    expect(page).to_have_title("Night Patrol")

    # Here she sees the full review
    expect(page.locator("div.review-content")).to_be_visible()

    # She notices that the author's name is a link and clicks on it
    page.get_by_text("Matt Zoller Seitz", exact=True).click()

    # She is redirected to the page containing all the reviews by this author
    expect(page).to_have_title("Matt Zoller Seitz")
    for review in page.locator("div.review").all():
        expect(review.get_by_text("Matt Zoller Seitz")).to_be_visible()

    # Alice notices there is a navigation menu at the top of the page
    expect(page.get_by_role("navigation")).to_be_visible()

    # There is a link to the home page
    expect(
        page.get_by_role("navigation").get_by_role("link", name="Home")
    ).to_be_visible()

    # And a link which says `Authors`
    expect(
        page.get_by_role("navigation").get_by_role("link", name="Authors")
    ).to_be_visible()

    # Alice clicks on the `Authors`
    page.get_by_role("navigation").get_by_role("link", name="Authors").click()

    # She is redirected to the page with all the authors
    expect(page).to_have_title("Authors")
    expect(page.locator("ul.author-list")).to_be_visible()

    # The home page link is still visible and Alice clicks on it
    expect(
        page.get_by_role("navigation").get_by_role("link", name="Home")
    ).to_be_visible()
    page.get_by_role("navigation").get_by_role("link", name="Home").click()

    # She is back at the home page
    expect(page).to_have_title(re.compile(r"reviews", re.IGNORECASE))


def test_search_functionality(
    live_server,
    page,
    close_db_connections,
    king_of_color,
    sound_of_falling,
    night_patrol,
):
    home_page = HomePage(page)

    # Alice is once again on the home page
    home_page.navigate(live_server)

    # She notices there is a search field
    search_field = page.get_by_role("textbox", name="Search")
    expect(search_field).to_be_visible()

    # She's just watched a movie called `The King of Color` and is curious to know
    # if there are any reviews for it on the website
    search_field.fill("king of color")
    search_field.press("Enter")

    # Alice is redirected to a new page with search results
    expect(page).to_have_title(re.compile(r"Search results for"))

    # The page says there was one review found
    expect(page.get_by_text("Found in titles: 1")).to_be_visible()

    # And the review is listed on the page
    expect(page.locator("div.review")).to_be_visible()
    expect(page.locator("div.review")).to_have_count(1)

    # Sure enough, the review's title is `The King of Color`
    expect(
        page.locator("div.review").get_by_text("The King of Color", exact=True)
    ).to_be_visible()

    # Alice clicks on the review link
    page.locator("div.review").get_by_role("link", name="The King of Color").click()

    # She is redirected to this review's page
    expect(page).to_have_title("The King of Color")

    # Alice notices that the search field is also available on this page
    search_field = page.get_by_role("textbox", name="Search")
    expect(search_field).to_be_visible()

    # Alice is a big fan of the movie critic Sheila O'Malley and she wants to find out
    # if this websites features some of her reviews
    search_field.fill("sheila")
    search_field.press("Enter")

    # Alice is redirected to the search results page once again
    expect(page).to_have_title(re.compile(r"Search results for"))

    # And yes, there is a critic with the name of Sheila O'Malley
    expect(page.get_by_text("Found in authors: 1")).to_be_visible()
    author_list = page.locator("ul.author-list")
    expect(author_list).to_be_visible()
    expect(author_list.get_by_role("listitem", name="Sheila O'Malley"))
    expect(author_list.get_by_role("listitem")).to_have_count(1)
