from behave import given, then, when
from selenium_behave.methods.navigation_methods import *


@given('I navigate to "{url}"')
def step_navigate(context, url):
    navigate_to_url(context, url)

@then('I navigate forward')
def step_navigate_forward(context):
    navigate(context, "forward")


@then('I navigate back')
def step_navigate_back(context):
    navigate(context, "back")


@then('I close browser')
def step_close_browser(context):
    close_driver(context)


@then('I resize browser window size to width {width:d} and height {height:d}')
def step_resize_browser(context, width, height):
    resize_browser(context, width, height)

@then('I maximize browser window')
def step_maximize_browser(context):
    maximize_browser(context)

@then('I refresh page')
def step_refresh_page(context):
    context.driver.refresh()

@then('I switch to new window')
def step_switch_to_new_window(context):
    switch_to_new_window(context)

@then('I switch to previous window')
def step_switch_to_previous_window(context):
    switch_to_previous_window(context)

@then('I switch to main window')
def step_switch_to_main_window(context):
    switch_to_main_window(context)

@then('I switch to window having title "{title}"')
def step_switch_to_window_by_title(context, title):
    switch_to_window_by_title(context, title)

@then('I switch to window having url "{url}"')
def step_switch_to_window_by_url(context, url):
    switch_to_window_by_url(context, url)

@then('I close new window')
def step_close_new_window(context):
    close_new_window(context)

@then('I switch to main content')
def step_switch_to_main_content(context):
    switch_to_main_content(context)

@then('I switch to frame "{frame}"')
def step_switch_to_frame(context, frame):
    switch_frame(context, frame)

@then('I scroll to element having {locator_type} "{locator}"')
def step_scroll_to_element(context, locator_type, locator):
    scroll_to_element(context, locator_type, locator)

@then('I scroll to {direction} of page')
def step_scroll_page(context, direction):
    scroll_page(context, direction)

@when('I hover over element having {locator_type} "{locator}"')
def step_hover_over_element(context, locator_type, locator):
    hover_over_element(context, locator_type, locator)

@then('I zoom in page')
def step_zoom_in(context):
    zoom_in_out(context, "add")

@then('I zoom out page')
def step_zoom_out(context):
    zoom_in_out(context, "subtract")

@then('I reset page view')
def step_reset_zoom(context):
    zoom_in_out(context, "reset")

@then('I zoom out page till I see element having {locator_type} "{locator}"')
def step_zoom_out_till_element_display(context, locator_type, locator):
    zoom_in_out_till_element_display(context, locator_type, locator)

