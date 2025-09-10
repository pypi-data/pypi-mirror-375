from behave import then
from selenium_behave.methods.progress_methods import *


@then('I wait for {time:d} sec')
def step_wait(context, time):
    """Wait for specific seconds"""
    wait(time)


@then('I wait {duration:d} seconds for element having {locator_type} "{locator}" to display')
def step_wait_for_display(context, duration, locator_type, locator):
    """Wait for element to be visible"""
    wait_for_element_to_display(context, locator_type, locator, duration)


@then('I wait {duration:d} seconds for element having {locator_type} "{locator}" to enable')
def step_wait_for_enable(context, duration, locator_type, locator):
    """Wait for element to be enabled"""
    wait_for_element_to_enable(context, locator_type, locator, duration)
