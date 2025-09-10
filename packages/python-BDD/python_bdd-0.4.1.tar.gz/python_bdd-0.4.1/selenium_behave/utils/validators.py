# selenium_behave/utils/validators.py

def validate_locator(locator_type: str):
    """
    Validate supported locator types.
    """
    supported_types = [
        "id", "name", "xpath", "css selector",
        "class name", "tag name", "link text", "partial link text"
    ]
    if locator_type not in supported_types:
        raise ValueError(f"Unsupported locator type: {locator_type}. "
                         f"Supported types: {supported_types}")


def validate_option_by(option_by: str):
    """
    Validate supported option_by types for dropdowns/radio groups.
    """
    supported = ["text", "value", "index"]
    if option_by not in supported:
        raise ValueError(f"Unsupported option_by: {option_by}. "
                         f"Supported: {supported}")
