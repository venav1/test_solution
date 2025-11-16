from selenium.webdriver.common.by import By
from .base_page import BasePage
import logging
import time
import json

LOGGING = logging.getLogger(__name__)


class CreateTaskPage(BasePage):
    """Класс для работы с формой создания/редактирования задачи"""

    TITLE_INPUT = (By.XPATH, "//input[@type='text' and @required]")
    DESCRIPTION_TEXTAREA = (By.CSS_SELECTOR, "textarea")

    OPTION_TEMPLATE = (By.CSS_SELECTOR, "[data-value='*']")
    DROPDOWN_TEMPLATE = (By.XPATH,
                         "(//div[contains(@class, 'MuiModal-root')]//div[contains(@class, 'MuiSelect-root')])[*]")

    CREATE_BUTTON = (By.XPATH, "//div[contains(@class, 'MuiModal-root')]//*[contains(text(), 'Создать')]")
    UPDATE_BUTTON = (By.XPATH, "//div[contains(@class, 'MuiModal-root')]//*[contains(text(), 'Обновить')]")

    MODAL_CREATE_TITLE = (By.XPATH, "//div[contains(@class, 'MuiModal-root')]//*[contains(text(), 'Создание')]")
    MODAL_UPDATE_TITLE = (By.XPATH, "//div[contains(@class, 'MuiModal-root')]//*[contains(text(), 'Редактирование')]")

    def __init__(self, driver):
        super().__init__(driver)
        self._initial_request_count = len(driver.requests) if hasattr(driver, 'requests') else 0
        self._form_data = {
            'title': None,
            'description': None,
            'project_id': None,
            'project_name': None,
            'priority': None,
            'status': None,
            'assignee_id': None,
            'assignee_name': None
        }

    def fill_title(self, title):
        self.fill_input(self.TITLE_INPUT, title)
        self._form_data['title'] = title
        return self

    def fill_description(self, description):
        self.fill_input(self.DESCRIPTION_TEXTAREA, description)
        self._form_data['description'] = description
        return self

    def return_option_locator(self, data_value):
        return self.get_dynamic_locator(self.OPTION_TEMPLATE, data_value)

    def return_dropdown_locator(self, number):
        """
        Возвращает локатор выпадающего списка, number - его номер
        """
        return self.get_dynamic_locator(self.DROPDOWN_TEMPLATE, str(number))

    def select_project(self, project_id):
        project_dropdown_locator = self.return_dropdown_locator(1)
        option_locator = self.return_option_locator(project_id)
        self.click_in_dropdown(project_dropdown_locator, option_locator)

        time.sleep(0.3)
        project_element = self.find_element(project_dropdown_locator)
        project_name = project_element.text.strip()

        self._form_data['project_id'] = project_id
        self._form_data['project_name'] = project_name
        return self

    def select_priority(self, priority_name):
        priority_dropdown_locator = self.return_dropdown_locator(2)
        self.click_in_dropdown(priority_dropdown_locator, self.return_option_locator(priority_name))
        self._form_data['priority'] = priority_name
        return self

    def select_status(self, status_name):
        status_dropdown_locator = self.return_dropdown_locator(3)
        self.click_in_dropdown(status_dropdown_locator, self.return_option_locator(status_name))
        self._form_data['status'] = status_name
        return self

    def select_assignee(self, assignee_id):
        assignee_dropdown_locator = self.return_dropdown_locator(4)
        self.click_button(assignee_dropdown_locator)
        time.sleep(0.3)

        option_locator = self.return_option_locator(assignee_id)
        option_element = self.find_element(option_locator)
        assignee_name = option_element.text.strip()

        self.click_button(option_locator)

        self._form_data['assignee_id'] = assignee_id
        self._form_data['assignee_name'] = assignee_name
        return self

    def _wait_for_api_request(self, method, url_pattern, timeout=10):
        start_time = time.time()
        checked_requests = set()

        while time.time() - start_time < timeout:
            all_requests = list(self.driver.requests) if hasattr(self.driver, 'requests') else []

            for request in all_requests:
                request_id = id(request)
                if request_id in checked_requests:
                    continue

                if request.method == method and url_pattern in request.url:
                    checked_requests.add(request_id)
                    max_wait_for_response = 5
                    response_wait_start = time.time()

                    while time.time() - response_wait_start < max_wait_for_response:
                        if hasattr(request, 'response') and request.response:
                            return request
                        time.sleep(0.2)

                    return request

            time.sleep(0.3)

        raise AssertionError(f"API запрос {method} {url_pattern} не найден за {timeout} секунд")

    def _get_response_body(self, request):
        if not request or not hasattr(request, 'response') or not request.response:
            return ""

        try:
            body = request.response.body
            if body:
                return body.decode('utf-8')
        except Exception:
            return ""
        return ""

    def _get_request_body(self, request):
        if not request:
            raise AssertionError("Запрос не передан")

        try:
            body = request.body
            if not body:
                raise AssertionError("Тело запроса пустое")
            body_str = body.decode('utf-8')
            return json.loads(body_str)
        except json.JSONDecodeError as e:
            raise AssertionError(f"Не удалось распарсить JSON из тела запроса: {e}")
        except Exception as e:
            raise AssertionError(f"Ошибка при получении тела запроса: {e}")

    def _validate_payload(self, payload):
        if not payload:
            raise AssertionError("Payload пустой")

    def _check_title(self, payload):
        if self._form_data['title'] is not None:
            assert payload.get('title') == self._form_data['title'], \
                f"title в запросе не соответствует: ожидалось '{self._form_data['title']}', получено '{payload.get('title')}'"

    def _check_description(self, payload):
        if self._form_data['description'] is not None:
            assert payload.get('description') == self._form_data['description'], \
                f"description в запросе не соответствует: ожидалось '{self._form_data['description']}', получено '{payload.get('description')}'"
        else:
            payload_description = payload.get('description')
            assert payload_description is None or payload_description == "", \
                f"description в запросе должно быть None или пустой строкой, если не заполнено, получено: '{payload_description}'"

    def _check_description_update(self, payload):
        if self._form_data['description'] is not None:
            assert payload.get('description') == self._form_data['description'], \
                f"description в запросе не соответствует: ожидалось '{self._form_data['description']}', получено '{payload.get('description')}'"

    def _check_priority(self, payload):
        if self._form_data['priority'] is not None:
            assert payload.get('priority') == self._form_data['priority'], \
                f"priority в запросе не соответствует: ожидалось '{self._form_data['priority']}', получено '{payload.get('priority')}'"

    def _check_project_id(self, payload):
        if self._form_data['project_id'] is not None:
            expected_board_id = int(self._form_data['project_id'])
            actual_board_id = payload.get('boardId')
            assert actual_board_id == expected_board_id, \
                f"boardId в запросе не соответствует: ожидалось {expected_board_id}, получено {actual_board_id}"

    def _check_assignee_id_create(self, payload):
        assignee_id = payload.get('assigneeId')
        assert assignee_id == 1, \
            f"assigneeId в запросе должен быть равен 1, получено {assignee_id}"

    def _check_status(self, payload):
        if self._form_data['status'] is not None:
            assert payload.get('status') == self._form_data['status'], \
                f"status в запросе не соответствует: ожидалось '{self._form_data['status']}', получено '{payload.get('status')}'"

    def _check_assignee_id_update(self, payload):
        if self._form_data['assignee_id'] is not None:
            expected_assignee_id = int(self._form_data['assignee_id'])
            actual_assignee_id = payload.get('assigneeId')
            assert actual_assignee_id == expected_assignee_id, \
                f"assigneeId в запросе не соответствует: ожидалось {expected_assignee_id}, получено {actual_assignee_id}"

    def _check_request_payload(self, request):
        payload = self._get_request_body(request)
        self._validate_payload(payload)
        self._check_title(payload)
        self._check_description(payload)
        self._check_priority(payload)
        self._check_project_id(payload)
        self._check_assignee_id_create(payload)

    def _check_update_request_payload(self, request):
        payload = self._get_request_body(request)
        self._validate_payload(payload)
        self._check_title(payload)
        self._check_description_update(payload)
        self._check_priority(payload)
        self._check_status(payload)
        self._check_assignee_id_update(payload)

    def _check_api_response(self, method, url_pattern, payload_checker, error_message, expected_status=200, timeout=10):
        api_request = self._wait_for_api_request(method, url_pattern, timeout)
        if not hasattr(api_request, 'response') or not api_request.response:
            raise AssertionError(error_message)

        payload_checker(api_request)

        status_code = api_request.response.status_code
        response_body = self._get_response_body(api_request)

        assert status_code == expected_status, \
            f"Ожидался статус {expected_status}, получен {status_code}. Тело ответа: {response_body}"

    def check_response_code(self, expected_status=200, timeout=10):
        self._check_api_response(
            'POST',
            "https://avito-tech-internship-production.up.railway.app/api/v1/tasks/create",
            self._check_request_payload,
            "POST /api/v1/tasks/create не найден или без ответа",
            expected_status,
            timeout
        )

    def check_update_response_code(self, expected_status=200, timeout=10):
        self._check_api_response(
            'PUT',
            "/api/v1/tasks/update/",
            self._check_update_request_payload,
            "PUT /api/v1/tasks/update/* не найден или без ответа",
            expected_status,
            timeout
        )

    def check_modal_create_close(self):
        self.is_element_not_visible(self.MODAL_CREATE_TITLE, 5)

    def check_modal_update_close(self):
        self.is_element_not_visible(self.MODAL_UPDATE_TITLE)

    def check_after_create(self, code=200):
        self.check_modal_create_close()
        self.check_response_code(code)

    def check_after_update(self, code=200):
        self.check_modal_update_close()
        self.check_update_response_code(code)

    def get_form_data(self):
        return self._form_data.copy()

    def click_create_button(self):
        self.click_button(self.CREATE_BUTTON)

    def click_update_button(self):
        self.click_button(self.UPDATE_BUTTON)

    def submit_form(self, code=200):
        self.click_create_button()
        self.check_after_create(code)
        from .dashboard_page import DashboardPage
        return DashboardPage(self.driver)

    def update_form(self, code=200):
        self.click_update_button()
        self.check_after_update(code)
        from .dashboard_page import DashboardPage
        return DashboardPage(self.driver)

    def is_create_button_disabled(self):
        self.is_button_disabled(self.CREATE_BUTTON)

    def get_default_status(self):
        element = self.find_element(self.STATUS_DROPDOWN)
        return element.text.strip()
