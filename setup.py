import pathlib

from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="pyPreservicaSearch",
    version="0.1.0",
    description="Simple Report Designer for Preservica",
    long_description=README,
    long_description_content_type="text/markdown",
    url="",    author="James Carr",
    author_email="james.carr@preservica.com",
    license="Apache License 2.0",
    packages=["pyPreservicaSearch"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: System :: Archiving",
    ],
    install_requires=["requests", "certifi", "pyPreservica >= 0.7.3", "PySide2 == 5.15.0", "shiboken2 == 5.15.0"]
)
