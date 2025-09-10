from setuptools import setup, find_packages

setup(
    name='python_BDD',
    version='0.4.1',
    packages=find_packages(),  # Detect all packages
    include_package_data=True,  # Include non-code files specified in MANIFEST.in
    install_requires=[
        # List of dependencies
    ],
    package_data={
        # If you have non-Python files
        '': ['*.txt', '*.md'],
        'your_package': ['data/*.dat'],  # Example: specific directory
    },
)