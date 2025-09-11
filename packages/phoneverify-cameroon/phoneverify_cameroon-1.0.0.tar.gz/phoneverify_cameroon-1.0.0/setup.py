"""
Setup configuration for phoneverify-cameroon package
"""
from setuptools import setup, find_packages
import os

def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "Validation des numéros mobile money camerounais"

# Lire la version depuis le package
def get_version():
    version = {}
    with open("phoneverify_cameroon/__init__.py", "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                exec(line, version)
                return version["__version__"]
    return "1.0.0"

setup(
    name="phoneverify-cameroon",
    version=get_version(),
    author="Djoko Christian",
    author_email="contact@example.com",
    description="Validation des numéros mobile money camerounais (MTN et Orange)",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/djoko-christian/phoneverify-cameroon",
    project_urls={
        "Bug Tracker": "https://github.com/djoko-christian/phoneverify-cameroon/issues",
        "Documentation": "https://github.com/djoko-christian/phoneverify-cameroon#readme",
        "Source Code": "https://github.com/djoko-christian/phoneverify-cameroon",
    },
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'phoneverify_cameroon': ['data/*.json'],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Telephony",
        "Topic :: Office/Business :: Financial",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="cameroon, mobile money, phone validation, mtn, orange, fintech",
    python_requires=">=3.8",
    install_requires=[
        # Aucune dépendance externe - package autonome !
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0", 
            "black>=21.0",
            "flake8>=3.8",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "phoneverify=phoneverify_cameroon.cli:main",
        ],
    },
    zip_safe=False,
)