import time
from typing import List

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


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
        """
        try:
            start_time = time.time()
            self.driver.get(url)

            # Ожидаем полной загрузки страницы
            WebDriverWait(self.driver, 10).until(
                lambda d: d.execute_script(
                    "return document.readyState === 'complete'"
                )
            )
            return time.time() - start_time
        except Exception as e:
            print(f"Ошибка при замере времени загрузки: {e}")
            return -1


class WebSurfer:
    def __init__(self, page_driver: PageDriver):
        self.driver = page_driver.driver
        self.checked_urls = set()

    def get_all_links(self, base_url: str) -> List[str]:
        """Получение всех валидных ссылок на странице"""
        try:
            self.driver.get(base_url)
            time.sleep(1)  # Даем странице время на загрузку

            links = []
            for element in self.driver.find_elements(By.TAG_NAME, 'a'):
                href = element.get_attribute('href')
                if href and self._is_valid_url(href):
                    links.append(href)
            return links
        except Exception as e:
            print(f"Ошибка при получении ссылок: {e}")
            return []

    def _is_valid_url(self, url: str) -> bool:
        if not (url.startswith('http://') or url.startswith('https://')):  # Проверяем, что URL начинается с http/https
            return False
        if url in self.checked_urls:  # Проверяем, что URL еще не посещали
            return False
        return True


def main():
    page_driver = PageDriver(headless=False)
    page_metrics = PageMetrics(page_driver)
    web_surfer = WebSurfer(page_driver)

    try:
        url = "https://ya.ru"
        page_load_time = page_metrics.measure_load_time(url)

        if page_load_time > -1:
            print(f"Страница загрузилась за {page_load_time:.2f} сек")

            links = web_surfer.get_all_links(url)  # Получаем ссылки
            print(f"\nНайдено ссылок: {len(links)}")
            for i, link in enumerate(links[:5], 1):  # Показываем первые 5 ссылок
                print(f"{i}. {link}")
        else:
            print("Не удалось загрузить страницу")

    finally:
        page_driver.close()


if __name__ == "__main__":
    main()
    time.sleep(1)
