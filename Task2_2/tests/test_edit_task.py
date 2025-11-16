"""
Тест-кейсы для редактирования задачи
"""
from pages.dashboard_page import DashboardPage


def test_edit_task_status_field(browser, created_task):
    """
    Редактирование статуса задачи
    """
    dashboard = DashboardPage(browser)
    edit_task_page = dashboard.open_edit_task_form()
    edit_task_page.select_status('InProgress')
    edit_task_page.update_form()



def test_edit_task_priority_and_status(browser, created_task):
    """
    Редактирование полей задачи (приоритет и статус)
    """
    dashboard = DashboardPage(browser)
    edit_task_page = dashboard.open_edit_task_form()
    edit_task_page.select_priority('High') \
                    .select_status('InProgress')
    edit_task_page.update_form()

