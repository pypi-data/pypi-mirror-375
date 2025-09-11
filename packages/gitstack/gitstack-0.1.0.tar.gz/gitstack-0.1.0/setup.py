from setuptools import setup, find_packages

setup(
    name="gitstack",
    version="0.1.0",
    description="An advanced modern version control system",
    packages=find_packages(),
    authors=["Bola Banjo <omogbolahanng@gmail.com>"],
    py_modules=["main"],
    install_requires=[
        "click",
        "tabulate",
    ],
    entry_points={"console_scripts": ["gitstack=gitstack.main:main"]},
)