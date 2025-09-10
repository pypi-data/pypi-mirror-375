from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
from selenium_behave.utils.driver_extensions import get_by


def get_page_title(context):
    return context.driver.title


def check_title(context, expected, test_case: bool):
    page_title = get_page_title(context)
    if test_case:
        assert page_title == expected, f"Expected title '{expected}', got '{page_title}'"
    else:
        assert page_title != expected, f"Title should not be '{expected}'"


def check_partial_title(context, partial, test_case: bool):
    page_title = get_page_title(context)
    if test_case:
        assert partial in page_title, f"Expected '{partial}' in '{page_title}'"
    else:
        assert partial not in page_title, f"Title should not contain '{partial}'"


def get_element_text(context, locator_type, locator):
    return context.driver.find_element(get_by(locator_type), locator).text


def check_element_text(context, locator_type, locator, expected, test_case: bool):
    element_text = get_element_text(context, locator_type, locator)
    if test_case:
        assert element_text == expected, f"Expected '{expected}', got '{element_text}'"
    else:
        assert element_text != expected, f"Element text should not be '{expected}'"


def check_element_partial_text(context, locator_type, locator, expected, test_case: bool):
    element_text = get_element_text(context, locator_type, locator)
    if test_case:
        assert expected in element_text, f"Expected '{expected}' in '{element_text}'"
    else:
        assert expected not in element_text, f"Element text should not contain '{expected}'"


def is_element_enabled(context, locator_type, locator):
    return context.driver.find_element(get_by(locator_type), locator).is_enabled()


def check_element_enable(context, locator_type, locator, test_case: bool):
    result = is_element_enabled(context, locator_type, locator)
    assert result is test_case, f"Expected element enabled={test_case}, got {result}"


def get_element_attribute(context, locator_type, locator, attr):
    return context.driver.find_element(get_by(locator_type), locator).get_attribute(attr)


def check_element_attribute(context, locator_type, locator, attr, value, test_case: bool):
    actual = get_element_attribute(context, locator_type, locator, attr)
    if test_case:
        assert actual == value, f"Expected '{attr}'='{value}', got '{actual}'"
    else:
        assert actual != value, f"Attribute '{attr}' should not be '{value}'"


def is_element_displayed(context, locator_type, locator):
    try:
        return context.driver.find_element(get_by(locator_type), locator).is_displayed()
    except NoSuchElementException:
        return False


def check_element_presence(context, locator_type, locator, test_case: bool):
    assert is_element_displayed(context, locator_type, locator) is test_case, \
        f"Presence mismatch for element {locator_type}='{locator}'"


def is_checkbox_checked(context, locator_type, locator, should_be_checked=True):
    checkbox = context.driver.find_element(get_by(locator_type), locator)
    assert checkbox.is_selected() is should_be_checked, \
        f"Expected checkbox checked={should_be_checked}, got {checkbox.is_selected()}"


def is_radio_button_selected(context, locator_type, locator, should_be_selected=True):
    radio = context.driver.find_element(get_by(locator_type), locator)
    assert radio.is_selected() is should_be_selected, \
        f"Expected radio selected={should_be_selected}, got {radio.is_selected()}"


def is_option_from_radio_button_group_selected(context, locator_type, locator, by, option, should_be_selected=True):
    group = context.driver.find_elements(get_by(locator_type), locator)
    getter = (lambda rb: rb.get_attribute("value")) if by == "value" else (lambda rb: rb.text)
    ele = next((rb for rb in group if getter(rb) == option), None)
    assert ele is not None, f"No radio button found with {by}='{option}'"
    assert ele.is_selected() is should_be_selected, \
        f"Expected radio '{option}' selected={should_be_selected}, got {ele.is_selected()}"


def get_alert_text(context):
    return context.driver.switch_to.alert.text


def check_alert_text(context, expected):
    actual = get_alert_text(context)
    assert actual == expected, f"Expected alert '{expected}', got '{actual}'"


def is_option_from_dropdown_selected(context, locator_type, locator, by, option, should_be_selected=True):
    dropdown = context.driver.find_element(get_by(locator_type), locator)
    select_list = Select(dropdown)

    if by == "text":
        actual = select_list.first_selected_option.text
    else:
        actual = select_list.first_selected_option.get_attribute("value")

    if should_be_selected:
        assert actual == option, f"Expected dropdown option '{option}', got '{actual}'"
    else:
        assert actual != option, f"Dropdown option should not be '{option}'"
