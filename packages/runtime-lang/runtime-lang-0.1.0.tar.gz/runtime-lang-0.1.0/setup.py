from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "pypi.md").read_text()

setup(
    name = "runtime-lang",
    version = "0.1.0",
    description = "Interpreter for the RUNTIME programming language",
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    packages = find_packages(),
    install_requires = ["colorama"],
    entry_points = {
        'console_scripts': ['runtime=runtime.cli:main'],
    },
)