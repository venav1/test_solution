"""
Тест-кейсы для создания задачи
"""
import pytest
from pages.dashboard_page import DashboardPage
import string

@pytest.mark.parametrize("project_id", [1, 2, 3, 4, 5, 6])
@pytest.mark.parametrize("priority", ["Low", "Medium", "High"])
def test_create_task_with_all_fields_success(browser, project_id, priority):
    """
    Успешное создание задачи со всеми заполненными полями (декартово произведение проектов и приоритетов)
    """
    priority_index = {"Low": 0, "Medium": 1, "High": 2}[priority]
    run_number = priority_index * 6 + project_id
    
    dashboard = DashboardPage(browser)
    create_task_page = dashboard.click_create_task_button()
    
    create_task_page.fill_title(f"Тест_{run_number}") \
                    .fill_description("Описание") \
                    .select_project(str(project_id)) \
                    .select_priority(priority) \
                    .select_assignee('1')
    
    form_data = create_task_page.get_form_data()
    dashboard = create_task_page.submit_form()
    dashboard.verify_task_created(form_data)
    


@pytest.mark.skip
@pytest.mark.parametrize("project_id", [1, 2, 3, 4, 5, 6])
@pytest.mark.parametrize("priority", ["Low", "Medium", "High"])
def test_create_task_only_required_fields(browser, project_id, priority):
    """
    Успешное создание задачи только с обязательными полями 
    """
    priority_index = {"Low": 0, "Medium": 1, "High": 2}[priority]
    run_number = priority_index * 6 + project_id
    
    dashboard = DashboardPage(browser)
    create_task_page = dashboard.click_create_task_button()
    
    create_task_page.fill_title(f"Без_описания_{run_number}") \
                    .select_project(str(project_id)) \
                    .select_priority(priority) \
                    .select_assignee('1')
    
    form_data = create_task_page.get_form_data()
    dashboard = create_task_page.submit_form()
    dashboard.verify_task_created(form_data)


@pytest.mark.parametrize("missing_field", ["title", "project", "priority", "assignee"])
def test_create_button_disabled_when_required_field_missing(browser, missing_field):
    """
    Проверка, что кнопка "Создать" неактивна, если не заполнено одно из обязательных полей
    """
    dashboard = DashboardPage(browser)
    create_task_page = dashboard.click_create_task_button()
    
    if missing_field == "title":
        create_task_page.select_project('1') \
                        .select_priority('Medium') \
                        .select_assignee('1') \
                        .fill_description("Описание") 
    elif missing_field == "project":
        create_task_page.fill_title("Тестовая задача") \
                        .select_priority('High') \
                        .select_assignee('1') \
                        .fill_description("Описание") 
    elif missing_field == "priority":
        create_task_page.fill_title("Тестовая задача") \
                        .fill_description("Описание") \
                        .select_project('2') \
                        .select_assignee('1')
    elif missing_field == "assignee":
        create_task_page.fill_title("Тестовая задача") \
                        .fill_description("Описание") \
                        .select_project('3') \
                        .select_priority('Low')
    create_task_page.is_create_button_disabled()


def english_alphabet():
    return string.ascii_letters

def russian_alphabet():
    return ''.join(chr(i) for i in range(0x0410, 0x0450) if chr(i).isalpha() or chr(i) in 'ёЁ')

SPECIAL_CHARS = "!@#$%^&*()_+-=[]{};':,.<>?"
LONG_STRING = "a" * 255

@pytest.mark.parametrize(
    "title",
    [
        pytest.param("a", id="одна_латинская_буква"),
        pytest.param("1234567890", id="цифры"),
        pytest.param(russian_alphabet(), id="полный_русский_алфавит"),
        pytest.param(english_alphabet(), id="полный_английский_алфавит"),
        pytest.param(SPECIAL_CHARS, id="специальные_символы"),
        pytest.param("<script>alert(1)</script>", id="попытка_xss"),
    ]
)
def test_create_task_with_different_titles(browser, title):
    dashboard = DashboardPage(browser)
    create_task_page = dashboard.click_create_task_button()
    
    create_task_page.fill_title(title) \
                    .fill_description("Описание") \
                    .select_project('1') \
                    .select_priority('Low') \
                    .select_assignee('1')
    
    form_data = create_task_page.get_form_data()
    dashboard = create_task_page.submit_form()
    dashboard.verify_task_created(form_data)

@pytest.mark.parametrize(
    "description,run_number",
    [
        pytest.param("a", 1, id="одна_латинская_буква"),
        pytest.param("1234567890", 2, id="цифры"),
        pytest.param(russian_alphabet(), 3, id="полный_русский_алфавит"),
        pytest.param(english_alphabet(), 4, id="полный_английский_алфавит"),
        pytest.param(LONG_STRING, 5, id="максимальная_длина"),
        pytest.param(SPECIAL_CHARS, 6, id="специальные_символы"),
        pytest.param("<script>alert(1)</script>", 7, id="попытка_xss"),
    ]
)
def test_create_task_with_different_descriptions(browser, description, run_number):
    dashboard = DashboardPage(browser)
    create_task_page = dashboard.click_create_task_button()
    
    create_task_page.fill_title(f"Тест_{run_number}") \
                    .fill_description(description) \
                    .select_project('1') \
                    .select_priority('Low') \
                    .select_assignee('1')
    
    form_data = create_task_page.get_form_data()
    dashboard = create_task_page.submit_form()
    dashboard.verify_task_created(form_data)
