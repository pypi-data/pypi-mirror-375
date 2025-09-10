from behave import given, then

@given("I open Google")
def step_open_google(context):
    context.execute_steps('Given I navigate to "https://www.google.com"')
