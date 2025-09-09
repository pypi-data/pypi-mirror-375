from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="ira-ev-api-wrapper",
    version="0.1.1",
    author="Milo Thomas",
    author_email="your.email@example.com",
    description="A simple HTTP library for handling device actions",
    packages=find_packages(where="ira_ev_api_wrapper"),
    package_dir={"": "ira_ev_api_wrapper"},
    install_requires=[
        "requests",
    ],
    python_requires=">=3.6",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
