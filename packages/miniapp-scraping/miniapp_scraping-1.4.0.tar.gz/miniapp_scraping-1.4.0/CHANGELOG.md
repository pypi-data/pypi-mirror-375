# Miniapp Scraping v1.4.0 Changelog

## [1.4.0] - 2025-09-10 - PyPI Release

### Added
- 🎯 **PyPI Package**: Official package published to PyPI as `miniapp-scraping`
- 📧 **Enhanced Email Extraction**: Multi-pattern email detection system
- 🛠️ **CLI Interface**: Command-line tool for easy integration
- ⚡ **Performance Optimized**: Lightweight design with minimal dependencies
- 📝 **Comprehensive Documentation**: English, Japanese, and Chinese docs

### Changed
- 🔄 **Package Name**: Changed from `prtimes-scraper` to `miniapp-scraping` (trademark compliance)
- 🏗️ **Architecture**: Restructured as proper Python package
- 📦 **Dependencies**: Reduced to only 3 core packages (requests, beautifulsoup4, lxml)

### Technical Details
- **Class Name**: `PRTimesScraper` → `MiniappScraper`
- **Package Structure**: Proper `__init__.py`, `scraper.py`, `cli.py` organization
- **Entry Point**: `miniapp-scraping` command-line tool
- **Python Support**: 3.8+ compatibility

### Installation
```bash
pip install miniapp-scraping
```

### Usage
```bash
# Command line
miniapp-scraping https://example.com/press-release

# Python code
from miniapp_scraping import MiniappScraper
scraper = MiniappScraper()
result = scraper.scrape(url)
```

---

## Previous Versions

### [1.3.0] - Email Extraction Enhancement
- Multi-stage email address extraction system
- Pure Python web scraping validation
- Contact information prioritization

### [1.2.1] - JSONL Database Integration
- Unified JSONL database support
- Category-based management

### [1.1.0] - Structured Data Output
- JSONL format output support
- Enhanced data structuring
