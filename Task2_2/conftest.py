import pytest
import os
import random
import subprocess
import logging
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

logging.getLogger('seleniumwire').setLevel(logging.WARNING)
logging.getLogger('seleniumwire.handler').setLevel(logging.WARNING)
logging.getLogger('WDM').setLevel(logging.WARNING)
os.environ['WDM_LOG_LEVEL'] = '0'


@pytest.fixture(scope="function")
def created_task(browser):
    from pages.dashboard_page import DashboardPage
    
    random_number = random.randint(1, 9999)
    task_title = f"Тест_{random_number}"
    
    dashboard = DashboardPage(browser)
    create_task_page = dashboard.click_create_task_button()
    
    create_task_page.fill_title(task_title) \
                    .fill_description("Описание") \
                    .select_project('1') \
                    .select_assignee('1') \
                    .select_priority('Low')
    
    create_task_page.click_create_button()
    create_task_page.check_modal_create_close()
    return task_title

def pytest_addoption(parser):
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Запуск браузера в headless режиме"
    )
    parser.addoption(
        "--base-url",
        action="store",
        default="https://avito-tech-internship-psi.vercel.app",
        help="Базовый URL для тестирования"
    )


@pytest.fixture(scope="session")
def headless_mode(request):
    return request.config.getoption("--headless")


@pytest.fixture(scope="function")
def driver(headless_mode):
    chrome_options = Options()
    if headless_mode:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver_path = ChromeDriverManager().install()
    
    if not driver_path.endswith('chromedriver.exe'):
        driver_dir = os.path.dirname(driver_path)
        chromedriver_exe = os.path.join(driver_dir, 'chromedriver.exe')
        if os.path.exists(chromedriver_exe):
            driver_path = chromedriver_exe
        else:
            for root, dirs, files in os.walk(driver_dir):
                if 'chromedriver.exe' in files:
                    driver_path = os.path.join(root, 'chromedriver.exe')
                    break
    
    service = Service(driver_path, log_output=subprocess.DEVNULL)
    seleniumwire_options = {
        'suppress_connection_errors': True,
    }
    driver = webdriver.Chrome(service=service, options=chrome_options, seleniumwire_options=seleniumwire_options)
    driver.maximize_window()
    driver.implicitly_wait(10)
    
    yield driver
    driver.quit()


@pytest.fixture(scope="session")
def base_url(request):
    return request.config.getoption("--base-url")


@pytest.fixture(scope="function")
def browser(driver, base_url):
    driver.get(base_url)
    yield driver



