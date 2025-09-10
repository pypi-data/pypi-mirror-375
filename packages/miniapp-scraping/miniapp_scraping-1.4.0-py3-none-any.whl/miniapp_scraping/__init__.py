"""
Miniapp Scraping v1.4.0
A lightweight, efficient tool for web scraping press releases.

Features:
- Pure Python scraping (requests + BeautifulSoup)
- Email and contact extraction
- Business opportunity scoring
- CLI interface for easy integration

Author: TECHFUND Development Team
License: MIT
"""

__version__ = "1.4.0"
__author__ = "TECHFUND Development Team"
__email__ = "dev@techfund.jp"

from .scraper import MiniappScraper
from .cli import main

__all__ = ['MiniappScraper', 'main']
