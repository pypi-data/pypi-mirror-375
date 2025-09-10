from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time

def navigate_to_url(context, url: str):
    context.driver.get(url)

def navigate(context, direction: str):
    if direction == "back":
        context.driver.back()
    elif direction == "forward":
        context.driver.forward()

def close_driver(context):
    context.driver.quit()

"""
def get_key():
    os = platform.system().upper()
    if os in ["WINDOWS", "LINUX"]:
        return Keys.CONTROL
    elif os == "DARWIN":  # Mac
        return Keys.COMMAND
    else:
        raise Exception("Invalid OS")
"""    
def get_key():
    # 👇 change this depending on your need (CTRL, ALT, SHIFT, etc.)
    return Keys.CONTROL

def zoom_in_out(context, operation: str):
    driver = context.driver
    if driver.capabilities.get("browserName") == "chrome":
        actual_zoom = driver.execute_script("return document.body.style.zoom")
        if not actual_zoom:
            actual_zoom = 100
        else:
            actual_zoom = int(str(actual_zoom).replace("%", ""))

        if operation == "add":
            actual_zoom = min(actual_zoom + 15, 500)
        elif operation == "subtract":
            actual_zoom = max(actual_zoom - 15, 25)
        else:
            actual_zoom = 100

        driver.execute_script(f"document.body.style.zoom='{actual_zoom}%'")
    else:
        body = driver.find_element("tag name", "body")
        if operation == "add":
            ActionChains(driver).key_down(get_key()).send_keys(Keys.ADD).key_up(get_key()).perform()
        elif operation == "subtract":
            ActionChains(driver).key_down(get_key()).send_keys(Keys.SUBTRACT).key_up(get_key()).perform()
        else:
            ActionChains(driver).key_down(get_key()).send_keys("0").key_up(get_key()).perform()


def zoom_in_out_till_element_display(context, locator_type, locator):
    driver = context.driver
    while True:
        try:
            element = driver.find_element(locator_type, locator)
            if element.is_displayed():
                break
        except:
            pass
        zoom_in_out(context, "subtract")
        time.sleep(0.5)


def resize_browser(context, width, height):
    context.driver.set_window_size(width, height)

def maximize_browser(context):
    context.driver.maximize_window()

def hover_over_element(context, locator_type, locator):
    element = context.driver.find_element(locator_type, locator)
    ActionChains(context.driver).move_to_element(element).perform()

def scroll_to_element(context, locator_type, locator):
    element = context.driver.find_element(locator_type, locator)
    context.driver.execute_script("arguments[0].scrollIntoView(true);", element)

def scroll_page(context, direction):
    if direction == "end":
        context.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    elif direction == "top":
        context.driver.execute_script("window.scrollTo(0, 0);")
    else:
        raise Exception("Invalid direction (use 'top' or 'end')")

def switch_to_previous_window(context):
    driver = context.driver
    driver.switch_to.window(context.previous_window)

def switch_to_new_window(context):
    driver = context.driver
    context.previous_window = driver.current_window_handle
    driver.switch_to.window(driver.window_handles[-1])

def switch_to_main_window(context):
    driver = context.driver
    context.previous_window = driver.current_window_handle
    driver.switch_to.window(driver.window_handles[0])

def switch_to_window_by_title(context, title):
    driver = context.driver
    context.previous_window = driver.current_window_handle
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        if driver.title == title:
            return
    raise Exception(f'Window with title "{title}" not found')

def switch_to_window_by_url(context, url):
    driver = context.driver
    context.previous_window = driver.current_window_handle
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        if url in driver.current_url:
            return
    raise Exception(f'Window with url "{url}" not found')

def close_new_window(context):
    context.driver.close()

def switch_frame(context, frame):
    context.driver.switch_to.frame(frame)

def switch_to_main_content(context):
    context.driver.switch_to.default_content()