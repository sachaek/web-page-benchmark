import time
from selenium import webdriver


class PageDriver:
    def __init__(self, headless: bool = True):
        self.driver = self.setup_driver(headless=headless)

    def setup_driver(self, headless: bool = True):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        return webdriver.Chrome(options=options)

    def close(self):
        self.driver.quit()


class PageMetrics:
    def __init__(self, page_driver: PageDriver):
        self.driver = page_driver.driver



def main():
    page = PageDriver(headless=False)
    page.driver.get("https://ya.ru/")


if __name__ == "__main__":
    main()
    time.sleep(1)