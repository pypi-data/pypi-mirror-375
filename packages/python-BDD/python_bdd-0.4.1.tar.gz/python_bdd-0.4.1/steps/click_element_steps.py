from behave import when, then
from selenium_behave.methods.click_element_methods import *

@then('I click on element having {locator_type} "{locator}"')
def step_click(context, locator_type, locator):
    click(context, locator_type, locator)

"""
@when('I click on element having {locator_type} "{locator}" and text "{text}"')
def step_click_with_text(context, locator_type, locator, text):
    click_by_text(context, locator_type, locator, text)
"""

@then('I forcefully click on element having {locator_type} "{locator}"')
def step_click_forcefully(context, locator_type, locator):
    click_forcefully(context, locator_type, locator)

@then('I double click on element having {locator_type} "{locator}"')
def step_double_click(context, locator_type, locator):
    double_click(context, locator_type, locator)

@then('I click on link having text "{text}"')
def step_click_link_text(context, text):
    click(context, "link_text", text)

@then('I click on link having partial text "{text}"')
def step_click_link_partial_text(context, text):
    click(context, "partial_link_text", text)

@when('I tap on element having {locator_type} "{locator}"')
def step_tap(context, locator_type, locator):
    click(context, locator_type, locator)
