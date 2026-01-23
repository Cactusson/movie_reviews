from pytest_django import asserts


class TestHomePage:
    def test_uses_home_page_template(self, client):
        response = client.get("/")
        asserts.assertTemplateUsed(response, "reviews/home_page.html")
