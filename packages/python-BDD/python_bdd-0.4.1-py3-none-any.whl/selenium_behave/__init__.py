
# selenium_behave/__init__.py
import pkgutil
import importlib
import selenium_behave.steps

# Auto-discover and import all step definition modules
for _, module_name, _ in pkgutil.iter_modules(selenium_behave.steps.__path__):
    importlib.import_module(f"{selenium_behave.steps.__name__}.{module_name}")
