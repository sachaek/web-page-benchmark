import time
from typing import List, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import sys


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
        Замеряет время полной загрузки страницы в секундах.
        Использует Navigation Timing API с fallback на document.readyState.
        Возвращает время загрузки или -1 при ошибке.
        """
        try:
            start_time = time.time()
            self.driver.get(url)

            # Пробуем получить метрики через Navigation Timing API
            load_time = self.driver.execute_script("""
                // Пробуем современный API
                const navEntries = performance.getEntriesByType('navigation');
                if (navEntries.length > 0 && navEntries[0].loadEventEnd > 0) {
                    return (navEntries[0].loadEventEnd - navEntries[0].startTime) / 1000;
                }

                // Fallback для старых браузеров
                if (performance.timing && performance.timing.loadEventEnd > 0) {
                    return (performance.timing.loadEventEnd - performance.timing.navigationStart) / 1000;
                }

                // Если API недоступны, возвращаем null для использования системного времени
                return null;
            """)

            # Если Navigation API вернул данные, используем их
            if load_time is not None and load_time > 0:
                return float(load_time)

            # Fallback: ждем readyState и используем системное время
            WebDriverWait(self.driver, 10).until(
                lambda d: d.execute_script("return document.readyState === 'complete'")
            )
            return time.time() - start_time

        except Exception as e:
            print(f"Ошибка при замере времени загрузки: {e}")
            return -1


class WebSurfer:
    def __init__(self, page_driver: PageDriver, max_pages: int = 50):
        self.driver = page_driver.driver
        self.page_metrics = PageMetrics(page_driver)
        self.max_pages = max_pages

    def analyze_site(self, start_url: str) -> List[Tuple[str, float]]:
        """Анализирует только ссылки с начальной страницы"""
        print(f"Получаем ссылки с начальной страницы: {start_url}")

        # Получаем все ссылки с начальной страницы
        initial_links = self.get_all_links(start_url)
        if not initial_links:
            return []

        print(f"Найдено {len(initial_links)} ссылок для анализа")

        # Анализируем начальную страницу
        results = []
        initial_load_time = self.page_metrics.measure_load_time(start_url)
        if initial_load_time > 0:
            results.append((start_url, initial_load_time))

        # Анализируем найденные ссылки (не более max_pages-1, так как начальная уже учтена)
        for i, url in enumerate(initial_links[:self.max_pages - 1], 1):
            print(f"Анализ страницы {i}/{min(len(initial_links), self.max_pages - 1)}: {url}")
            load_time = self.page_metrics.measure_load_time(url)
            if load_time > 0:
                results.append((url, load_time))

        return sorted(results, key=lambda x: x[1], reverse=True)

    def get_all_links(self, base_url: str) -> List[str]:
        """Получение всех уникальных ссылок на странице"""
        try:
            self.driver.get(base_url)
            WebDriverWait(self.driver, 10).until(
                lambda d: d.execute_script("return document.readyState === 'complete'")
            )

            links = set()
            for element in self.driver.find_elements(By.TAG_NAME, 'a'):
                href = element.get_attribute('href')
                if href and href.startswith(('http://', 'https://')):
                    links.add(href)

            print(f"Найдено уникальных ссылок: {len(links)}")
            return list(links)
        except Exception as e:
            print(f"Ошибка при получении ссылок: {e}")
            return []


def main():
    # Параметры по умолчанию
    default_url = "https://tensor.ru/"
    default_max_pages = 50

    # Обработка аргументов командной строки
    if len(sys.argv) > 1:
        start_url = sys.argv[1]
        if not start_url.startswith(('http://', 'https://')):
            start_url = 'https://' + start_url
    else:
        start_url = default_url

    if len(sys.argv) > 2:
        try:
            max_pages = int(sys.argv[2])
        except ValueError:
            print("Ошибка: max_pages должен быть числом. Используется значение по умолчанию 50")
            max_pages = default_max_pages
    else:
        max_pages = default_max_pages

    page_driver = PageDriver(headless=False)
    web_surfer = WebSurfer(page_driver, max_pages=max_pages)

    try:
        print(f"Начинаем анализ сайта: {start_url}")
        print(f"Максимальное количество страниц для анализа: {max_pages}")

        results = web_surfer.analyze_site(start_url)

        print("\nТоп страниц по времени загрузки (от самых медленных):")
        for i, (url, load_time) in enumerate(results, 1):
            print(f"{i}. {url} - {load_time:.2f} сек")

    finally:
        page_driver.close()


if __name__ == "__main__":
    main()