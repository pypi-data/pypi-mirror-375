# SEO Sentinel - Automated SEO Auditing Tool

![Build](https://img.shields.io/github/actions/workflow/status/nayandas69/SEO-Sentinel/publish.yml?branch=main)
![PyPI](https://img.shields.io/pypi/v/seo-sentinel)
![Python Version](https://img.shields.io/pypi/pyversions/seo-sentinel)
![License](https://img.shields.io/github/license/nayandas69/SEO-Sentinel?style=flat-square&color=blue&logo=github&logoColor=white)

A comprehensive SEO analysis tool that crawls websites, identifies SEO issues, and generates detailed HTML reports for website optimization.

> \[!CAUTION]
> SEO Sentinel is a helpful utility for SEO auditing but does not guarantee search engine ranking improvements. Please ensure your usage complies with the target site's policies.
> Always respect the `robots.txt` file of the websites you crawl.
> Use responsibly and ethically.
> The author is not responsible for any misuse or damage caused by the tool.
> Always test on your own sites or with permission from the site owner.

## Features

- **Website Crawling**: Intelligent crawling with configurable depth and page limits
- **SEO Analysis**: Comprehensive analysis of metadata, links, and content
- **Keyword Density**: Track keyword usage and density across pages
- **Broken Link Detection**: Identify and report broken internal/external links
- **Performance Metrics**: Page load time and response code monitoring
- **HTML Reports**: Beautiful, detailed reports with actionable insights
- **Auto Updates**: Built-in update checker for latest features
- **Configurable**: Customizable crawling parameters and settings

## Installation
## Getting Started

### Clone & Run Locally

```bash
# Clone the repository
git clone https://github.com/nayandas69/SEO-Sentinel
cd SEO-Sentinel

# Create a virtual environment
python3 -m venv venv

# Activate the environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt

# Run the project
python3 seose.py
```

### Install via PyPI

```bash
pip3 install seo-sentinel
```

Then run via:

```bash
seo-sentinel
```

> [!NOTE]
> Always make sure your internet connection is active while using SEO Sentinel for crawling and update checking.

> [!IMPORTANT]
> Make sure your URLs include `http://` or `https://` otherwise they will be rejected.

> [!TIP]
> Generate reports regularly to monitor improvements after fixing SEO issues.

### Programmatic Usage

```python
from seose import SEOSentinel, SEOConfig

# Initialize with default config
sentinel = SEOSentinel()

# Or with custom configuration
config = SEOConfig(
    crawl_depth=2,
    max_pages=50,
    request_timeout=15
)
sentinel = SEOSentinel(config)

# Crawl and analyze a website
urls = sentinel.crawl_website("https://example.com")
results = {}

for url in urls:
    results[url] = sentinel.analyze_seo_issues(url, keywords=["seo", "optimization"])

# Generate HTML report
report_path = sentinel.generate_report(results, "https://example.com")
print(f"Report saved to: {report_path}")
```

## Configuration

The `SEOConfig` class allows you to customize the analysis:

```python
from seose import SEOConfig

config = SEOConfig(
    report_directory="reports",      # Directory for HTML reports
    log_directory="logs",           # Directory for log files
    crawl_depth=3,                  # Maximum crawling depth
    max_pages=100,                  # Maximum pages to crawl
    request_timeout=10,             # Request timeout in seconds
    max_workers=5,                  # Concurrent workers (future use)
    user_agent="SEO-Sentinel/1.0.2", # Custom user agent
    verify_ssl=True                 # SSL certificate verification
)
```

## Requirements

### Runtime Dependencies

- Python 3.8+
- beautifulsoup4 >= 4.12.0
- requests >= 2.31.0
- tqdm >= 4.65.0
- jinja2 >= 3.1.0

### Development Dependencies

- pytest >= 7.0.0
- black >= 23.0.0
- flake8 >= 6.0.0
- mypy >= 1.0.0
- coverage >= 7.0.0

## Usage Examples

### Basic Website Analysis

```python
from seose import SEOSentinel

sentinel = SEOSentinel()

# Analyze a single page
issues = sentinel.analyze_seo_issues("https://example.com")
print(f"Found {len(issues.missing_metadata)} metadata issues")

# Full website crawl and analysis
urls = sentinel.crawl_website("https://example.com")
results = {url: sentinel.analyze_seo_issues(url) for url in urls}
report_path = sentinel.generate_report(results, "https://example.com")
```

### Keyword Analysis

```python
keywords = ["seo", "optimization", "website", "ranking"]
issues = sentinel.analyze_seo_issues("https://example.com", keywords=keywords)

for keyword, data in issues.keyword_density.items():
    print(f"{keyword}: {data['count']} occurrences ({data['density']}%)")
```

### Custom Configuration

```python
from seose import SEOSentinel, SEOConfig

config = SEOConfig(
    crawl_depth=2,
    max_pages=25,
    request_timeout=15
)

sentinel = SEOSentinel(config)
urls = sentinel.crawl_website("https://example.com", max_depth=1, max_pages=10)
```

## Report Features

The generated HTML reports include:

- **Executive Summary**: Total pages, issues, and performance metrics
- **Page-by-Page Analysis**: Detailed breakdown of each crawled page
- **Performance Indicators**: Load times and response codes
- **Broken Link Detection**: Complete list of broken internal/external links
- **Metadata Analysis**: Missing or problematic meta tags, titles, descriptions
- **Keyword Density**: Frequency and density analysis for target keywords

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=seose

# Run specific test file
pytest tests/test_seose.py
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Format code (`black .`)
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Nayan Das**
- Website: [https://linkinbio-nextjs-ashen.vercel.app](https://linkinbio-nextjs-ashen.vercel.app)
- Email: nayanchandradas@hotmail.com
- GitHub: [@nayandas69](https://github.com/nayandas69)

## Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/nayandas69/SEO-Sentinel/issues)
- 💬 **Community**: [Discord Server](https://discord.gg/skHyssu)
- 📧 **Email**: nayanchandradas@hotmail.com

## Roadmap

- [ ] Multi-threading support for faster crawling
- [ ] Additional SEO checks (schema markup, social meta tags)
- [ ] JSON/CSV export options
- [ ] Web interface
- [ ] Integration with popular CMS platforms
- [ ] Advanced keyword analysis and suggestions