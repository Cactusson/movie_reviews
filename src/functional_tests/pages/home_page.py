class HomePage:
    def __init__(self, page):
        self.page = page

    def navigate(self, live_server):
        self.page.goto(live_server.url)
