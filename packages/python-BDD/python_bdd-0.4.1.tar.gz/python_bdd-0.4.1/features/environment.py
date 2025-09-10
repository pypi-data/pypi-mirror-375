from selenium import webdriver
import selenium_behave
'''from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
import os'''

from selenium import webdriver

def before_all(context):
    # Require BROWSER parameter from command line
    print("✅ before_all executed!") 
    browser = context.config.userdata.get("BROWSER")

    if not browser:
        raise ValueError(
            "❌ BROWSER parameter is missing! Run as: behave -D BROWSER=chrome"
        )

    browser = browser.lower()

    if browser == "firefox":
        context.driver = webdriver.Firefox()
    elif browser == "edge":
        context.driver = webdriver.Edge()
    elif browser == "chrome":
        context.driver = webdriver.Chrome()
    else:
        raise ValueError(
            f"❌ Unsupported browser: {browser}. Use chrome | firefox | edge"
        )

def after_all(context):
    if hasattr(context, "driver"):
        context.driver.quit()

