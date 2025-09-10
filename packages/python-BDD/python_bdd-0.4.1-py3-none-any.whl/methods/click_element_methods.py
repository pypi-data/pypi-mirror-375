from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium_behave.utils.driver_extensions import get_by

def click(context, locator_type, locator):
    """Normal click"""
    element = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((get_by(locator_type), locator))
    )
    element.click()

def click_by_text(context, locator_type, locator, text):
    elements = context.driver.find_elements(get_by(locator_type), locator)
    for el in elements:
        if el.text.strip() == text.strip():
            el.click()
            return
    raise NoSuchElementException(
        f"Element not found with {locator_type}='{locator}' and text='{text}'"
    )

def click_forcefully(context, locator_type, locator):
    element = context.driver.find_element(get_by(locator_type), locator)
    context.driver.execute_script("arguments[0].click();", element)


def double_click(context, locator_type, locator):
    element = context.driver.find_element(get_by(locator_type), locator)
    ActionChains(context.driver).double_click(element).perform()


def submit(context, locator_type, locator):
    context.driver.find_element(get_by(locator_type), locator).submit()
