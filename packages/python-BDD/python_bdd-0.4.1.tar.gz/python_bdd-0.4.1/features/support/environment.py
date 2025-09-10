from selenium import webdriver

def before_all(context):
    # Require BROWSER parameter from command line
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

