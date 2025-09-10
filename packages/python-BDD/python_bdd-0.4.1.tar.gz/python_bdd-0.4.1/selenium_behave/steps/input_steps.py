from behave import then
from selenium_behave.methods.input_methods import *
from selenium_behave.utils.validators import validate_locator, validate_option_by


@then('I enter "{text}" into input field having {locator_type} "{locator}"')
def step_enter_text(context, text, locator_type, locator):
    validate_locator(locator_type)
    enter_text(context, locator_type, locator, text)

@then('I clear input field having {locator_type} "{locator}"')
def step_clear_text(context, locator_type, locator):
    validate_locator(locator_type)
    clear_text(context, locator_type, locator)

@then('I select "{option}" option by {option_by} from {present}dropdown having {locator_type} "{locator}"')
def step_select_dropdown(context, option, option_by, present, locator_type, locator):
    validate_locator(locator_type)
    validate_option_by(option_by)
    select_option_from_dropdown(context, locator_type, locator, option_by, option)

@then('I select {index:d} option by index from {present}dropdown having {locator_type} "{locator}"')
def step_select_dropdown_index(context, index, present, locator_type, locator):
    validate_locator(locator_type)
    select_option_from_dropdown(context, locator_type, locator, 'index', index - 1)

@then('I select all options from multiselect dropdown having {locator_type} "{locator}"')
def step_select_all_multiselect(context, locator_type, locator):
    validate_locator(locator_type)
    select_all_option_from_multiselect_dropdown(context, locator_type, locator)

@then('I unselect all options from multiselect dropdown having {locator_type} "{locator}"')
def step_unselect_all_multiselect(context, locator_type, locator):
    validate_locator(locator_type)
    unselect_all_option_from_multiselect_dropdown(context, locator_type, locator)

@then('I check the checkbox having {locator_type} "{locator}"')
def step_check_checkbox(context, locator_type, locator):
    validate_locator(locator_type)
    check_checkbox(context, locator_type, locator)

@then('I uncheck the checkbox having {locator_type} "{locator}"')
def step_uncheck_checkbox(context, locator_type, locator):
    validate_locator(locator_type)
    uncheck_checkbox(context, locator_type, locator)

@then('I toggle checkbox having {locator_type} "{locator}"')
def step_toggle_checkbox(context, locator_type, locator):
    validate_locator(locator_type)
    toggle_checkbox(context, locator_type, locator)

@then('I select radio button having {locator_type} "{locator}"')
def step_select_radio(context, locator_type, locator):
    validate_locator(locator_type)
    select_radio_button(context, locator_type, locator)

@then('I select "{option}" option by {option_by} from radio button group having {locator_type} "{locator}"')
def step_select_radio_group(context, option, option_by, locator_type, locator):
    validate_locator(locator_type)
    validate_option_by(option_by)
    select_option_from_radio_button_group(context, locator_type, locator, option_by, option)