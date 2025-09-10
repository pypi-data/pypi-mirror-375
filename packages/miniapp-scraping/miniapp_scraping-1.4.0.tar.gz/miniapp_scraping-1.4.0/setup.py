#!/usr/bin/env python3
"""
Setup configuration for Miniapp Scraping v1.4.0
Lightweight web scraping tool with email extraction
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="miniapp-scraping",
    version="1.4.0",
    author="TECHFUND Development Team",
    author_email="dev@techfund.jp",
    description="Lightweight web scraping tool with email extraction",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/TECHFUND/miniapp-scraping",
    project_urls={
        "Bug Tracker": "https://github.com/TECHFUND/miniapp-scraping/issues",
        "Documentation": "https://github.com/TECHFUND/miniapp-scraping#readme",
        "Source Code": "https://github.com/TECHFUND/miniapp-scraping",
        "Changelog": "https://github.com/TECHFUND/miniapp-scraping/blob/main/CHANGELOG.md",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Communications :: Email",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "black>=22.0.0",
            "flake8>=4.0.0",
            "pytest>=7.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "miniapp-scraping=miniapp_scraping.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt"],
    },
    keywords=[
        "scraping",
        "miniapp",
        "press-release",
        "email-extraction",
        "web-scraping",
        "data-extraction",
        "journalism",
        "media",
        "automation",
    ],
    zip_safe=False,
)
