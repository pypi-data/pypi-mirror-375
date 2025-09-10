from behave import then
from selenium_behave.methods.assertion_methods import *

@then('I should{not_flag} see page title as "{title}"')
def step_check_page_title(context, not_flag, title):
    check_title(context, title, not not_flag.strip())


@then('I should{not_flag} see page title having partial text as "{partial_text}"')
def step_check_partial_title(context, not_flag, partial_text):
    check_partial_title(context, partial_text, not not_flag.strip())


@then('element having {locator_type} "{locator}" should{not_flag} have text as "{value}"')
def step_check_element_text(context, locator_type, locator, not_flag, value):
    check_element_text(context, locator_type, locator, value, not not_flag.strip())


@then('element having {locator_type} "{locator}" should{not_flag} have partial text as "{value}"')
def step_check_element_partial_text(context, locator_type, locator, not_flag, value):
    check_element_partial_text(context, locator_type, locator, value, not not_flag.strip())


@then('element having {locator_type} "{locator}" should{not_flag} have attribute "{attr}" with value "{value}"')
def step_check_element_attribute(context, locator_type, locator, not_flag, attr, value):
    check_element_attribute(context, locator_type, locator, attr, value, not not_flag.strip())

""""
@then('element having {locator_type} "{locator}" should{not_flag} be {state}')
def step_check_element_enabled(context, locator_type, locator, not_flag, state):
    flag = (state == "enabled")
    if not_flag.strip():
        flag = not flag
    check_element_enable(context, locator_type, locator, flag)
"""


@then('element having {locator_type} "{locator}" should{not_flag} be present')
def step_check_element_present(context, locator_type, locator, not_flag):
    check_element_presence(context, locator_type, locator, not not_flag.strip())


@then('checkbox having {locator_type} "{locator}" should be {state}')
def step_checkbox_state(context, locator_type, locator, state):
    is_checkbox_checked(context, locator_type, locator, state == "checked")


@then('radio button having {locator_type} "{locator}" should be {state}')
def step_radio_button_state(context, locator_type, locator, state):
    is_radio_button_selected(context, locator_type, locator, state == "selected")


@then('option "{option}" by {by} from radio button group having {locator_type} "{locator}" should be {state}')
def step_radio_button_group_option(context, option, by, locator_type, locator, state):
    is_option_from_radio_button_group_selected(
        context, locator_type, locator, by, option, state == "selected"
    )


@then('link having text "{text}" should{not_flag} be present')
def step_link_presence(context, text, not_flag):
    check_element_presence(context, "link text", text, not not_flag.strip())


@then('link having partial text "{text}" should{not_flag} be present')
def step_partial_link_presence(context, text, not_flag):
    check_element_presence(context, "partial link text", text, not not_flag.strip())


@then('I should see alert text as "{expected}"')
def step_alert_text(context, expected):
    check_alert_text(context, expected)


@then('option "{option}" by {by} from dropdown having {locator_type} "{locator}" should be {state}')
def step_dropdown_option(context, option, by, locator_type, locator, state):
    is_option_from_dropdown_selected(
        context, locator_type, locator, by, option, state == "selected"
    )
