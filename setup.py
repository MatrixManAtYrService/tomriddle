#!/usr/bin/env python
from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

requirements = ["sympy", "pycosat", "nltk", "pyphen"]

setup_requirements = [
    "pytest-runner",
]

test_requirements = [
    "pytest>=3",
]

setup(
    author="Matt Rixman",
    author_email="MatrixManAtYrService@users.noreply.github.com",
    python_requires=">=3.5",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    description="Generate pronouncable anagrams: 'I am Lord Voldemort' -> 'Tom Marvolo Riddle'",
    entry_points={
        "console_scripts": [
            "tomriddle=tomriddle.cli:tomriddle",
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    include_package_data=True,
    keywords="tomriddle",
    name="tomriddle",
    packages=find_packages(include=["tomriddle", "tomriddle.*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/MatrixManAtYrService/tomriddle",
    version="0.1.0",
    zip_safe=False,
)
