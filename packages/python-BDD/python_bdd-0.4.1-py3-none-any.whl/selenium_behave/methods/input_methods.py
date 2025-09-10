from selenium.webdriver.support.ui import Select
from selenium_behave.utils.driver_extensions import get_by

def enter_text(context, locator_type, locator, text):
    context.driver.find_element(get_by(locator_type), locator).send_keys(text)

def clear_text(context, locator_type, locator):
    context.driver.find_element(get_by(locator_type), locator).clear()

def select_option_from_dropdown(context, locator_type, locator, by, option):
    dropdown = context.driver.find_element(get_by(locator_type), locator)
    select_list = Select(dropdown)

    if by == "text":
        select_list.select_by_visible_text(option)
    elif by == "value":
        select_list.select_by_value(option)
    elif by == "index":
        select_list.select_by_index(option)
    else:
        raise ValueError(f"Invalid option_by: {by}")


def select_all_option_from_multiselect_dropdown(context, locator_type, locator):
    dropdown = context.driver.find_element(get_by(locator_type), locator)
    select_list = Select(dropdown)
    for option in select_list.options:
        select_list.select_by_visible_text(option.text)


def unselect_all_option_from_multiselect_dropdown(context, locator_type, locator):
    dropdown = context.driver.find_element(get_by(locator_type), locator)
    select_list = Select(dropdown)
    select_list.deselect_all()


def check_checkbox(context, locator_type, locator):
    checkbox = context.driver.find_element(get_by(locator_type), locator)
    if not checkbox.is_selected():
        checkbox.click()


def uncheck_checkbox(context, locator_type, locator):
    checkbox = context.driver.find_element(get_by(locator_type), locator)
    if checkbox.is_selected():
        checkbox.click()


def toggle_checkbox(context, locator_type, locator):
    context.driver.find_element(get_by(locator_type), locator).click()


def select_radio_button(context, locator_type, locator):
    radio_button = context.driver.find_element(get_by(locator_type), locator)
    if not radio_button.is_selected():
        radio_button.click()


def select_option_from_radio_button_group(context, locator_type, locator, by, option):
    radio_group = context.driver.find_elements(get_by(locator_type), locator)

    for rb in radio_group:
        value = rb.get_attribute("value") if by == "value" else rb.text
        if value == option:
            if not rb.is_selected():
                rb.click()
            break
