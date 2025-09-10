import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_behave.utils.driver_extensions import get_by


def wait(seconds: int):
    """Simple static wait"""
    time.sleep(seconds)


def wait_for_element_to_display(context, locator_type, locator, duration: int):
    """Wait until element is visible within duration"""
    WebDriverWait(context.driver, duration).until(
        EC.visibility_of_element_located((get_by(locator_type), locator))
    )


def wait_for_element_to_enable(context, locator_type, locator, duration: int):
    """Wait until element is enabled (clickable) within duration"""
    WebDriverWait(context.driver, duration).until(
        EC.element_to_be_clickable((get_by(locator_type), locator))
    )
