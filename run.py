from selenium import webdriver

driver = webdriver.Chrome()
driver.get("https://ya.ru/")

class PageDriver:
    def __init__(self):
        self.driver = self._setup_driver()

    def _setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        return webdriver.Chrome(options=options)

    def close(self):
        self.driver.quit()


page = PageDriver()._setup_driver()
page.get("https://ya.ru/")
page.pause()