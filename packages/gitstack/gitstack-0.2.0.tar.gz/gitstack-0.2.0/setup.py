from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    description = f.read()

setup(
    name="gitstack",
    version="0.2.0",
    description="An advanced modern version control system",
    packages=find_packages(),
    authors=["Bola Banjo <omogbolahanng@gmail.com>"],
    py_modules=["main"],
    install_requires=[
        "click",
        "tabulate",
    ],
    entry_points={
        "console_scripts":[
        "gitstack=gitstack.main:main"
        ]
    },
    long_description=description,
    long_description_content_type="text/markdown",
)