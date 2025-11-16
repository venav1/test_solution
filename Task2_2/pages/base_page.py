from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
from selenium.webdriver.support.ui import Select

# Создаем объект логгера на уровне модуля
LOGGING = logging.getLogger(__name__)


class BasePage:

    def __init__(self, driver, base_url="https://avito-tech-internship-psi.vercel.app/issues"):
        self.driver = driver
        self.base_url = base_url

    def open(self):
        LOGGING.info(f"Открытие страницы: {self.base_url}")
        self.driver.get(self.base_url)

    def find_element(self, locator, timeout=10):
        """
        Поиск элемента с ожиданием
        :param locator: Кортеж
        :param timeout: Время ожидания в секундах
        :return: WebElement
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            LOGGING.info(f"Элемент найден: {locator}")
            return element
        except TimeoutException:
            LOGGING.error(f"Элемент не найден: {locator}")
            raise

    def select_by_text(self, locator, text, timeout=10):
        try:
            select = Select(self.find_element(locator, timeout))
            select.select_by_visible_text(text)
            LOGGING.info(f"Выбран элемент: {text}")
            return select
        except TimeoutException:
            LOGGING.error(f"Не удалось выбрать элемент: {text}")
            raise

    def click_in_dropdown(self, menu_locator, option_locator, timeout=10):
        """
        Клик по элементу в выпадающем списке
        :param menu_locator: Кортеж выпадающего списка
        :param option_locator: Кортеж опции
        :param timeout: Время ожидания в секундах
        """
        try:
            self.click_button(menu_locator, timeout=timeout)
            self.click_button(option_locator, timeout=timeout)
        except TimeoutException:
            LOGGING.error(f"Невозможно выбрать опцию: {option_locator}")
            raise

    def get_dynamic_locator(self, template: tuple, value: str):
        """
        возвращает динамический локатор по шаблону
        :param template: Шаблон локатора
        :param value: Значение для замены в шаблоне
        :return: Динамический локатор
        """
        return (template[0], template[1].replace("*", value))

    def find_elements(self, locator, timeout=10):
        """
        Поиск всех элементов с ожиданием
        
        :param locator: Кортеж (By, значение)
        :param timeout: Время ожидания в секундах
        :return: Список WebElement
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return self.driver.find_elements(*locator)
        except TimeoutException:
            LOGGING.warning(f"Элементы не найдены: {locator}")
            raise

    def click_button(self, locator, timeout=10):
        """
        Клик по элементу с ожиданием кликабельности
        
        :param locator: Кортеж (By, значение)
        :param timeout: Время ожидания в секундах
        """
        try:
            self.find_element(locator, timeout)

            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            element.click()
            LOGGING.info(f"Клик по элементу: {locator}")
        except TimeoutException:
            LOGGING.error(f"Элемент не кликабелен: {locator}")
            raise

    def fill_input(self, locator, text, timeout=10):
        """
        Ввод текста в поле
        
        :param locator: Кортеж 
        :param text: Текст для ввода
        :param timeout: Время ожидания в секундах
        """
        try:
            element = self.find_element(locator, timeout)
            element.send_keys(text)
        except TimeoutException:
            LOGGING.error(f"Не удалось ввести текст в элемент: {locator}")
            raise

    def get_text(self, locator, timeout=10):
        """
        Получение текста элемента
        
        :param locator: Кортеж 
        :param timeout: Время ожидания в секундах
        :return: Текст элемента
        """
        try:
            element = self.find_element(locator, timeout)
            text = element.text
            LOGGING.info(f"Получен текст '{text}' из элемента: {locator}")
            return text
        except TimeoutException:
            LOGGING.error(f"Не удалось получить текст из элемента: {locator}")
            raise

    def is_element_not_visible(self, locator, timeout=5):
        """
        Проверка отсутствия элемента на странице
        
        :param locator: Кортеж 
        :param timeout: Время ожидания в секундах
        :raises: TimeoutException если элемент все еще видим после timeout
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(locator)
            )
            LOGGING.info(f"Элемент исчез: {locator}")
        except TimeoutException:
            LOGGING.error(f"Элемент НЕ исчез: {locator}")
            raise AssertionError(f"Элемент всё ещё видим: {locator}")

    def is_button_enabled(self, locator, timeout=10):
        """
        Проверяет, что кнопка доступна для нажатия.
        Падает с AssertionError, если кнопка не кликабельна.
        """
        try:
            # Ждём, что кнопка кликабельна (видимая + enabled)
            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            LOGGING.info(f"Кнопка {locator} доступна для нажатия")
            return True
        except (TimeoutException, NoSuchElementException) as e:
            LOGGING.error(f"Кнопка {locator} НЕ доступна для нажатия: {e}")
            raise AssertionError(f"Кнопка НЕ кликабельна: {locator}")

    def is_button_disabled(self, locator, timeout=10):
        """
        Проверяет, что кнопка НЕДОСТУПНА для нажатия.
        Падает, если она кликабельна.
        """
        # Ждём появления элемента
        button = self.find_element(locator, timeout)
        if button.is_enabled():
            LOGGING.error(f"Кнопка НЕОЖИДАННО доступна: {locator}")
            raise AssertionError(f"Кнопка НЕОЖИДАННО доступна: {locator}")
        LOGGING.info(f"Кнопка {locator} отключена (как и ожидалось)")
        return True

    def get_current_url(self):
        """Получение текущего URL"""
        return self.driver.current_url

    def get_title(self):
        """Получение заголовка страницы"""
        return self.driver.title

    def scroll_to_element(self, locator):
        """
        Прокрутка страницы до элемента
        
        :param locator: Кортеж (By, значение)
        """
        element = self.find_element(locator)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        LOGGING.info(f"Прокрутка до элемента: {locator}")

