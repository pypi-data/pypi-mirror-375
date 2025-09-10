from selenium.webdriver.common.by import By

# Map string locator types to Selenium By
LOCATOR_MAP = {
    "id": By.ID,
    "name": By.NAME,
    "class_name": By.CLASS_NAME,
    "tag_name": By.TAG_NAME,
    "link_text": By.LINK_TEXT,
    "partial_link_text": By.PARTIAL_LINK_TEXT,
    "css": By.CSS_SELECTOR,
    "xpath": By.XPATH,
}

def get_by(locator_type: str):
    """Return correct By locator from string"""
    locator_type = locator_type.lower()
    if locator_type in LOCATOR_MAP:
        return LOCATOR_MAP[locator_type]
    raise ValueError(f"❌ Unsupported locator type: {locator_type}. "
                     f"Supported: {list(LOCATOR_MAP.keys())}")
