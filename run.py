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


page = PageDriver(headless=False)
page.driver.get("https://ya.ru/")
time.sleep(1)