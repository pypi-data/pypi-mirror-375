# coding:utf8
from os import path

from setuptools import setup

# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pqquotation",
    version="0.8.4",
    description="A utility for Fetch China Stock Info",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="bushuhui",
    author_email="bushuhui@foxmail.com",
    license="BSD",
    url="https://github.com/bushuhui/pqquotation",
    keywords="China stock trade",
    install_requires=["requests"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: BSD License",
    ],
    python_requires=">=3.6",
    packages=["pqquotation"],
    package_data={"": ["*.conf"]},
)
