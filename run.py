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

    def measure_load_time(self, url: str) -> float:
        """
        Замеряет время полной загрузки страницы в секундах
        Возвращает время загрузки или -1 при ошибке
        Navigation Timing API
        """
        try:
            self.driver.get(url)

            load_time = self.driver.execute_script(
                "return (window.performance.timing.loadEventEnd - "
                "window.performance.timing.navigationStart) / 1000"
            )
            return float(load_time)
        except Exception as e:
            print(f"Ошибка при замере времени загрузки: {e}")
            return -1


def main():
    page_driver = PageDriver(headless=False)
    page_metrics = PageMetrics(page_driver)
    page_load_time = page_metrics.measure_load_time("https://ya.ru")
    if page_load_time > 0:
        print(f"Страница загрузилась с временем {page_load_time}")
    else:
        print("Не удалось загрузить страницу")


if __name__ == "__main__":
    main()
    time.sleep(1)