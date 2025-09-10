import os
import sys

def create_file(path, content):
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(content)
        print(f"✅ Created {path}")
    else:
        print(f"⚠️ {path} already exists, skipping.")

def generate_structure():
    base_path = os.getcwd()
    features_path = os.path.join(base_path, "features")
    steps_path = os.path.join(features_path, "steps")
    screenshots_path = os.path.join(features_path, "screenshots")

    # Create folders
    os.makedirs(features_path, exist_ok=True)
    os.makedirs(steps_path, exist_ok=True)
    os.makedirs(screenshots_path, exist_ok=True)

    # environment.py with Selenium setup
    env_py = '''from selenium import webdriver
import os

driver = None

def before_all(context):
    global driver
    browser = os.getenv("BROWSER", "chrome").lower()
    if browser == "chrome":
        driver = webdriver.Chrome()
    elif browser == "firefox":
        driver = webdriver.Firefox()
    elif browser == "edge":
        driver = webdriver.Edge()
    else:
        raise Exception(f"Unsupported browser: {browser}")
    context.driver = driver
    print(f"[INFO] Starting tests on {browser} browser.")

def after_all(context):
    global driver
    if driver:
        driver.quit()
        print("[INFO] Browser closed after tests.")
'''
    create_file(os.path.join(features_path, "environment.py"), env_py)

    # Sample feature file
    feature_file = '''Feature: Navigate to Google and validate redirection

  Scenario: Open Google homepage
    Given I open Google
    Then I should be on Google homepage
'''
    create_file(os.path.join(features_path, "my_first.feature"), feature_file)

    # Step definitions
    steps_py = '''from behave import given, then

@given("I open Google")
def step_open_google(context):
    context.driver.get("https://www.google.com")

@then("I should be on Google homepage")
def step_validate_google(context):
    assert "Google" in context.driver.title
'''
    create_file(os.path.join(steps_path, "custom_steps.py"), steps_py)

    # requirements.txt
    requirements = '''behave
selenium
'''
    create_file(os.path.join(features_path, "requirements.txt"), requirements)
    print("\n✅ Project structure generated successfully!")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "gen":
        generate_structure()
    else:
        print("Use 'selenium-behave gen' to generate project structure.")

if __name__ == "__main__":
    main()
