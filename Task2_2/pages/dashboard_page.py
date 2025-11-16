from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from .base_page import BasePage
import logging
import time

LOGGING = logging.getLogger(__name__)


class DashboardPage(BasePage):
    """Класс для работы со страницей дашборда"""

    CREATE_TASK_BUTTON = (By.XPATH, "//button[contains(text(), 'Создать задачу')]")
    TASK_CARD = (By.CSS_SELECTOR, "div.MuiPaper-root.MuiPaper-outlined")

    def __init__(self, driver):
        super().__init__(driver)

    def click_create_task_button(self):
        self.click_button(self.CREATE_TASK_BUTTON)
        from .create_task_page import CreateTaskPage
        return CreateTaskPage(self.driver)

    def open_edit_task_form(self, task_title=None):
        cards = self.find_elements(self.TASK_CARD, timeout=10)
        assert len(cards) > 0, "Карточки задач не найдены на дашборде"

        last_card = cards[-1]
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", last_card)
        time.sleep(0.5)

        try:
            last_card.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", last_card)

        time.sleep(0.5)
        from .create_task_page import CreateTaskPage
        return CreateTaskPage(self.driver)

    def find_task_by_title(self, title, timeout=10):
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                cards = self.find_elements(self.TASK_CARD, timeout=5)
            except TimeoutException:
                time.sleep(0.5)
                continue

            last_card = cards[-1]
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'end'});", last_card)
            time.sleep(0.3)

            try:
                card_text = last_card.text

                if title not in card_text:
                    time.sleep(0.5)
                    continue

                title_elems = last_card.find_elements(By.CSS_SELECTOR, "h4, h5, h6")
                if title_elems and title_elems[0].text.strip() == title:
                    return last_card

                time.sleep(0.5)
                continue

            except Exception:
                time.sleep(0.5)
                continue

        raise AssertionError(f"Задача с названием '{title}' не найдена за {timeout} секунд")

    def get_task_info(self, task_card):
        try:
            task_info = {
                'title': None,
                'status': None,
                'board': None,
                'assignee': None
            }

            title_elems = task_card.find_elements(By.CSS_SELECTOR, "h4, h5, h6")
            if title_elems:
                task_info['title'] = title_elems[0].text.strip()

            status_chips = task_card.find_elements(By.CSS_SELECTOR, ".MuiChip-root .MuiChip-label")
            if status_chips:
                task_info['status'] = status_chips[0].text.strip()

            description_elems = task_card.find_elements(By.CSS_SELECTOR, "p.MuiTypography-body2")
            if description_elems:
                description_text = description_elems[0].text

                if "Доска:" in description_text:
                    board_part = description_text.split("Доска:")[1].split("|")[0].strip()
                    task_info['board'] = board_part

                if "Исполнитель:" in description_text:
                    assignee_part = description_text.split("Исполнитель:")[1].strip()
                    task_info['assignee'] = assignee_part

            return task_info

        except Exception:
            return {}

    def _validate_title_in_form_data(self, form_data):
        title = form_data.get('title')
        if not title:
            raise AssertionError("Название задачи не указано в form_data")
        return title

    def _find_task_card(self, title, timeout):
        time.sleep(1)
        return self.find_task_by_title(title, timeout)

    def _verify_title(self, task_info, expected_title):
        actual_title = task_info.get('title')
        assert actual_title == expected_title, \
            f"Название задачи не совпадает: ожидалось '{expected_title}', получено '{actual_title}'"

    def _verify_status(self, task_info, expected_status="Backlog"):
        actual_status = task_info.get('status')
        assert actual_status == expected_status, \
            f"Статус новой задачи должен быть '{expected_status}', получено '{actual_status}'"

    def _verify_board(self, task_info, expected_board):
        actual_board = task_info.get('board')
        assert actual_board == expected_board, \
            f"Доска не совпадает: ожидалось '{expected_board}', получено '{actual_board}'"

    def _verify_assignee(self, task_info, expected_assignee):
        actual_assignee = task_info.get('assignee')
        assert actual_assignee == expected_assignee, \
            f"Исполнитель не совпадает: ожидалось '{expected_assignee}', получено '{actual_assignee}'"

    def verify_task_created(self, form_data, timeout=10):
        title = self._validate_title_in_form_data(form_data)
        task_card = self._find_task_card(title, timeout)
        task_info = self.get_task_info(task_card)

        self._verify_title(task_info, title)
        self._verify_status(task_info)

        if form_data.get('project_name'):
            self._verify_board(task_info, form_data['project_name'])

        if form_data.get('assignee_name'):
            self._verify_assignee(task_info, form_data['assignee_name'])

        return True
