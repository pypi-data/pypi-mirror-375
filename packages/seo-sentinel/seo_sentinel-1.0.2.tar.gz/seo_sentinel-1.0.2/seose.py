#!/usr/bin/env python3
"""
SEO Sentinel - Automated SEO Auditing Tool

A comprehensive SEO analysis tool that crawls websites, identifies SEO issues,
and generates detailed HTML reports for website optimization.

Author: Nayan Das
Email: nayanchandradas@hotmail.com
Website: https://linkinbio-nextjs-ashen.vercel.app
GitHub: https://github.com/nayandas69/SEO-Sentinel
"""

import os
import re
import json
import logging
import sys
from collections import Counter
from datetime import datetime
from typing import Dict, List, Set, Optional, Tuple, Any
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, asdict
from pathlib import Path

try:
    from bs4 import BeautifulSoup
    from tqdm import tqdm
    import requests
    from jinja2 import Template
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Please install dependencies with: pip install -r requirements.txt")
    sys.exit(1)

__version__ = "1.0.2"
__author__ = "Nayan Das"
__email__ = "nayanchandradas@hotmail.com"
__website__ = "https://linkinbio-nextjs-ashen.vercel.app"
__github__ = "https://github.com/nayandas69/SEO-Sentinel"
__discord__ = "https://discord.gg/skHyssu"


@dataclass
class SEOConfig:
    """Configuration settings for SEO Sentinel."""

    report_directory: str = "reports"
    log_directory: str = "logs"
    crawl_depth: int = 3
    max_pages: int = 100
    request_timeout: int = 10
    max_workers: int = 5
    user_agent: str = "SEO-Sentinel/1.0.2 (+https://github.com/nayandas69/SEO-Sentinel)"
    verify_ssl: bool = True


@dataclass
class SEOIssues:
    """Structure for storing SEO analysis results."""

    broken_links: List[str]
    missing_metadata: List[str]
    keyword_density: Dict[str, int]
    page_load_time: Optional[float] = None
    status_code: Optional[int] = None
    content_length: Optional[int] = None


class SEOSentinel:
    """
    Main SEO Sentinel class for website analysis and reporting.

    This class provides comprehensive SEO analysis capabilities including
    website crawling, issue detection, and report generation.
    """

    def __init__(self, config: Optional[SEOConfig] = None):
        """
        Initialize SEO Sentinel with configuration.

        Args:
            config: SEOConfig instance with custom settings
        """
        self.config = config or SEOConfig()
        self._setup_directories()
        self._setup_logging()
        self._setup_session()

    def _setup_directories(self) -> None:
        """Create necessary directories for reports and logs."""
        try:
            Path(self.config.report_directory).mkdir(exist_ok=True)
            Path(self.config.log_directory).mkdir(exist_ok=True)
        except OSError as e:
            print(f"Error creating directories: {e}")
            sys.exit(1)

    def _setup_logging(self) -> None:
        """Configure logging with proper formatting and handlers."""
        log_file = Path(self.config.log_directory) / "seo_sentinel.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler(sys.stdout),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def _setup_session(self) -> None:
        """Configure requests session with proper headers and settings."""
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": self.config.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }
        )

        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def check_internet_connection(self) -> bool:
        """
        Verify internet connectivity by testing connection to reliable hosts.

        Returns:
            bool: True if internet connection is available, False otherwise
        """
        test_urls = ["https://www.google.com", "https://www.cloudflare.com"]

        for url in test_urls:
            try:
                response = self.session.head(url, timeout=5)
                if response.status_code == 200:
                    return True
            except requests.RequestException:
                continue

        self.logger.warning("No internet connection detected")
        return False

    def fetch_html_content(self, url: str) -> Optional[Tuple[str, int, float]]:
        """
        Fetch HTML content from the specified URL with performance metrics.

        Args:
            url: The URL to fetch content from

        Returns:
            Tuple of (html_content, status_code, load_time) or None if failed
        """
        try:
            start_time = datetime.now()
            response = self.session.get(
                url, timeout=self.config.request_timeout, verify=self.config.verify_ssl
            )
            load_time = (datetime.now() - start_time).total_seconds()

            response.raise_for_status()
            return response.text, response.status_code, load_time

        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            return None

    def validate_url(self, url: str) -> bool:
        """
        Validate URL format and accessibility.

        Args:
            url: URL to validate

        Returns:
            bool: True if URL is valid and accessible, False otherwise
        """
        try:
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                return False

            response = self.session.head(url, timeout=5)
            return response.status_code < 400

        except (requests.RequestException, ValueError):
            return False

    def crawl_website(
        self,
        base_url: str,
        max_depth: Optional[int] = None,
        max_pages: Optional[int] = None,
    ) -> Set[str]:
        """
        Crawl website starting from base URL with configurable depth and limits.

        Args:
            base_url: Starting URL for crawling
            max_depth: Maximum crawl depth (overrides config if provided)
            max_pages: Maximum pages to crawl (overrides config if provided)

        Returns:
            Set of discovered URLs
        """
        max_depth = max_depth or self.config.crawl_depth
        max_pages = max_pages or self.config.max_pages

        if not self.validate_url(base_url):
            self.logger.error(f"Invalid or inaccessible URL: {base_url}")
            return set()

        visited_urls: Set[str] = set()
        urls_to_visit: Set[str] = {base_url}
        depth_tracker: Dict[str, int] = {base_url: 0}
        base_domain = urlparse(base_url).netloc

        self.logger.info(
            f"Starting crawl of {base_url} (max_depth={max_depth}, max_pages={max_pages})"
        )

        with tqdm(desc="Crawling pages", unit="page") as pbar:
            while urls_to_visit and len(visited_urls) < max_pages:
                current_url = urls_to_visit.pop()
                current_depth = depth_tracker[current_url]

                if current_url in visited_urls or current_depth > max_depth:
                    continue

                pbar.set_description(f"Crawling: {current_url[:50]}...")
                result = self.fetch_html_content(current_url)

                if result:
                    html_content, _, _ = result
                    visited_urls.add(current_url)
                    pbar.update(1)

                    new_urls = self._extract_links(html_content, base_url, base_domain)
                    for new_url in new_urls:
                        if new_url not in visited_urls and new_url not in depth_tracker:
                            urls_to_visit.add(new_url)
                            depth_tracker[new_url] = current_depth + 1

        self.logger.info(f"Crawling completed. Total pages: {len(visited_urls)}")
        return visited_urls

    def _extract_links(
        self, html_content: str, base_url: str, base_domain: str
    ) -> Set[str]:
        """
        Extract and filter links from HTML content.

        Args:
            html_content: HTML content to parse
            base_url: Base URL for resolving relative links
            base_domain: Domain to restrict crawling to

        Returns:
            Set of filtered absolute URLs
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            links = set()

            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"].strip()

                if href.startswith(("#", "mailto:", "tel:", "javascript:")):
                    continue

                absolute_url = urljoin(base_url, href)
                parsed_url = urlparse(absolute_url)

                if parsed_url.netloc == base_domain and parsed_url.scheme in [
                    "http",
                    "https",
                ]:
                    # Remove fragment and normalize
                    clean_url = (
                        f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                    )
                    if parsed_url.query:
                        clean_url += f"?{parsed_url.query}"
                    links.add(clean_url)

            return links

        except Exception as e:
            self.logger.error(f"Error extracting links: {e}")
            return set()

    def analyze_seo_issues(
        self, url: str, keywords: Optional[List[str]] = None
    ) -> SEOIssues:
        """
        Perform comprehensive SEO analysis on a single page.

        Args:
            url: URL to analyze
            keywords: Optional list of keywords to analyze density for

        Returns:
            SEOIssues object containing analysis results
        """
        issues = SEOIssues(broken_links=[], missing_metadata=[], keyword_density={})

        result = self.fetch_html_content(url)
        if not result:
            return issues

        html_content, status_code, load_time = result
        issues.status_code = status_code
        issues.page_load_time = load_time
        issues.content_length = len(html_content)

        try:
            soup = BeautifulSoup(html_content, "html.parser")

            self._analyze_metadata(soup, issues)

            self._analyze_links(soup, url, issues)

            if keywords:
                self._analyze_keyword_density(soup, keywords, issues)

        except Exception as e:
            self.logger.error(f"Error analyzing {url}: {e}")

        return issues

    def _analyze_metadata(self, soup: BeautifulSoup, issues: SEOIssues) -> None:
        """Analyze page metadata for SEO issues."""
        # Title tag analysis
        title_tag = soup.find("title")
        if not title_tag:
            issues.missing_metadata.append("Missing <title> tag")
        elif not title_tag.get_text().strip():
            issues.missing_metadata.append("Empty <title> tag")
        elif len(title_tag.get_text()) > 60:
            issues.missing_metadata.append("Title tag too long (>60 characters)")

        # Meta description analysis
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if not meta_desc:
            issues.missing_metadata.append("Missing meta description")
        elif not meta_desc.get("content", "").strip():
            issues.missing_metadata.append("Empty meta description")
        elif len(meta_desc.get("content", "")) > 160:
            issues.missing_metadata.append(
                "Meta description too long (>160 characters)"
            )

        if not soup.find("meta", attrs={"name": "viewport"}):
            issues.missing_metadata.append("Missing viewport meta tag")

        if not soup.find("link", attrs={"rel": "canonical"}):
            issues.missing_metadata.append("Missing canonical link")

        # Check for heading structure
        h1_tags = soup.find_all("h1")
        if not h1_tags:
            issues.missing_metadata.append("Missing H1 tag")
        elif len(h1_tags) > 1:
            issues.missing_metadata.append("Multiple H1 tags found")

    def _analyze_links(
        self, soup: BeautifulSoup, base_url: str, issues: SEOIssues
    ) -> None:
        """Analyze links for broken or problematic URLs."""
        links = soup.find_all("a", href=True)

        for a_tag in links[:50]:  # Limit to first 50 links to avoid timeout
            href = a_tag["href"]
            absolute_url = urljoin(base_url, href)

            # Skip non-HTTP links
            if not absolute_url.startswith(("http://", "https://")):
                continue

            try:
                response = self.session.head(absolute_url, timeout=5)
                if response.status_code >= 400:
                    issues.broken_links.append(absolute_url)
            except requests.RequestException:
                issues.broken_links.append(absolute_url)

    def _analyze_keyword_density(
        self, soup: BeautifulSoup, keywords: List[str], issues: SEOIssues
    ) -> None:
        """Analyze keyword density in page content."""
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()

        page_text = soup.get_text().lower()
        words = re.findall(r"\b\w+\b", page_text)
        word_count = Counter(words)
        total_words = len(words)

        for keyword in keywords:
            keyword_lower = keyword.lower()
            count = word_count.get(keyword_lower, 0)
            density = (count / total_words * 100) if total_words > 0 else 0
            issues.keyword_density[keyword] = {
                "count": count,
                "density": round(density, 2),
            }

    def generate_report(self, results: Dict[str, SEOIssues], base_url: str) -> str:
        """
        Generate comprehensive HTML report from analysis results.

        Args:
            results: Dictionary mapping URLs to their SEO issues
            base_url: Base URL that was analyzed

        Returns:
            Path to generated report file
        """
        template = Template(
            """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO Sentinel Report - {{ base_url }}</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; margin-top: 30px; }
        .header-info { background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .metric-card { background: #fff; border: 1px solid #ddd; border-radius: 5px; padding: 15px; text-align: center; }
        .metric-value { font-size: 2em; font-weight: bold; color: #3498db; }
        .metric-label { color: #7f8c8d; font-size: 0.9em; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; vertical-align: top; }
        th { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; font-weight: 600; }
        tr:nth-child(even) { background-color: #f8f9fa; }
        tr:hover { background-color: #e8f4f8; }
        .issue-list { margin: 0; padding-left: 20px; }
        .issue-list li { margin: 5px 0; }
        .status-good { color: #27ae60; font-weight: bold; }
        .status-warning { color: #f39c12; font-weight: bold; }
        .status-error { color: #e74c3c; font-weight: bold; }
        .performance-indicator { display: inline-block; padding: 4px 8px; border-radius: 3px; font-size: 0.8em; font-weight: bold; }
        .perf-good { background: #d4edda; color: #155724; }
        .perf-warning { background: #fff3cd; color: #856404; }
        .perf-poor { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <h1>SEO Sentinel Report</h1>
        
        <div class="header-info">
            <p><strong>Website Analyzed:</strong> <a href="{{ base_url }}" target="_blank">{{ base_url }}</a></p>
            <p><strong>Report Generated:</strong> {{ date }}</p>
            <p><strong>SEO Sentinel Version:</strong> {{ version }}</p>
        </div>

        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value">{{ total_pages }}</div>
                <div class="metric-label">Pages Crawled</div>
            </div>
            <div class="metric-card">
                <div class="metric-value {{ 'status-error' if total_issues > 0 else 'status-good' }}">{{ total_issues }}</div>
                <div class="metric-label">Total Issues</div>
            </div>
            <div class="metric-card">
                <div class="metric-value {{ 'status-error' if broken_links > 0 else 'status-good' }}">{{ broken_links }}</div>
                <div class="metric-label">Broken Links</div>
            </div>
            <div class="metric-card">
                <div class="metric-value {{ 'status-warning' if missing_metadata > 0 else 'status-good' }}">{{ missing_metadata }}</div>
                <div class="metric-label">Metadata Issues</div>
            </div>
        </div>

        <h2>Detailed Analysis</h2>
        <table>
            <thead>
                <tr>
                    <th>Page URL</th>
                    <th>Performance</th>
                    <th>Broken Links</th>
                    <th>Metadata Issues</th>
                    <th>Keyword Analysis</th>
                </tr>
            </thead>
            <tbody>
                {% for url, issues in results.items() %}
                <tr>
                    <td><a href="{{ url }}" target="_blank">{{ url }}</a></td>
                    <td>
                        {% if issues.page_load_time %}
                            <span class="performance-indicator {{ 'perf-good' if issues.page_load_time < 2 else 'perf-warning' if issues.page_load_time < 5 else 'perf-poor' }}">
                                {{ "%.2f"|format(issues.page_load_time) }}s
                            </span><br>
                            <small>Status: {{ issues.status_code or 'Unknown' }}</small>
                        {% else %}
                            <span class="status-error">Failed to load</span>
                        {% endif %}
                    </td>
                    <td>
                        {% if issues.broken_links %}
                            <ul class="issue-list">
                                {% for link in issues.broken_links %}
                                <li><small>{{ link }}</small></li>
                                {% endfor %}
                            </ul>
                        {% else %}
                            <span class="status-good">✓ No broken links</span>
                        {% endif %}
                    </td>
                    <td>
                        {% if issues.missing_metadata %}
                            <ul class="issue-list">
                                {% for metadata in issues.missing_metadata %}
                                <li>{{ metadata }}</li>
                                {% endfor %}
                            </ul>
                        {% else %}
                            <span class="status-good">✓ All metadata present</span>
                        {% endif %}
                    </td>
                    <td>
                        {% if issues.keyword_density %}
                            <ul class="issue-list">
                                {% for keyword, data in issues.keyword_density.items() %}
                                <li>{{ keyword }}: {{ data.count }} ({{ data.density }}%)</li>
                                {% endfor %}
                            </ul>
                        {% else %}
                            <span class="status-warning">Not analyzed</span>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <div class="footer">
            <p>Generated by <a href="{{ github_url }}" target="_blank">SEO Sentinel v{{ version }}</a> | 
            <a href="{{ discord_url }}" target="_blank">Join our Discord</a> | 
            <a href="{{ author_website }}" target="_blank">{{ author_name }}</a></p>
        </div>
    </div>
</body>
</html>
        """
        )

        # Calculate summary statistics
        total_pages = len(results)
        total_issues = sum(
            len(issues.broken_links) + len(issues.missing_metadata)
            for issues in results.values()
        )
        broken_links = sum(len(issues.broken_links) for issues in results.values())
        missing_metadata = sum(
            len(issues.missing_metadata) for issues in results.values()
        )

        # Render report
        rendered_content = template.render(
            base_url=base_url,
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            version=__version__,
            total_pages=total_pages,
            total_issues=total_issues,
            broken_links=broken_links,
            missing_metadata=missing_metadata,
            results=results,
            github_url=__github__,
            discord_url=__discord__,
            author_name=__author__,
            author_website=__website__,
        )

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        domain = urlparse(base_url).netloc.replace(".", "_")
        report_filename = f"seo_report_{domain}_{timestamp}.html"
        report_path = Path(self.config.report_directory) / report_filename

        try:
            with open(report_path, "w", encoding="utf-8") as file:
                file.write(rendered_content)
            self.logger.info(f"Report generated: {report_path}")
            return str(report_path)
        except IOError as e:
            self.logger.error(f"Failed to save report: {e}")
            raise

    def check_for_updates(self) -> None:
        """Check for updates from PyPI and notify users about new versions."""
        if not self.check_internet_connection():
            print("\n❌ No internet connection. Please connect and try again.")
            return

        print(f"\n Checking for updates... (Current version: {__version__})")

        try:
            response = self.session.get(
                "https://pypi.org/pypi/seo-sentinel/json", timeout=10
            )
            response.raise_for_status()
            data = response.json()

            # Get latest version from PyPI
            latest_version = data.get("info", {}).get("version", "").strip()
            current_version = __version__.strip()

            if (
                latest_version
                and self._compare_versions(latest_version, current_version) > 0
            ):
                print(f"\n New version available: v{latest_version}")
                print(f"PyPI: https://pypi.org/project/seo-sentinel/")
                print(f"GitHub: {__github__}/releases/latest")
                print(
                    f"\nUpgrade with: \033[1;32mpip install seo-sentinel --upgrade\033[0m"
                )
            else:
                print("\n✅ You're running the latest version!")
                print(f"\nJoin our community: {__discord__}")

        except requests.RequestException as e:
            print(f"\nError checking for updates: {e}")
            self.logger.error(f"Update check failed: {e}")
        except (KeyError, ValueError) as e:
            print(f"\nError parsing version information: {e}")
            self.logger.error(f"Version parsing failed: {e}")

    def _compare_versions(self, version1: str, version2: str) -> int:
        """
        Compare two version strings using semantic versioning.

        Args:
            version1: First version string (e.g., "1.2.3")
            version2: Second version string (e.g., "1.2.2")

        Returns:
            int: 1 if version1 > version2, -1 if version1 < version2, 0 if equal
        """

        def normalize_version(v: str) -> List[int]:
            """Convert version string to list of integers for comparison."""
            return [int(x) for x in v.replace("v", "").split(".")]

        try:
            v1_parts = normalize_version(version1)
            v2_parts = normalize_version(version2)

            # Pad shorter version with zeros
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))

            for i in range(max_len):
                if v1_parts[i] > v2_parts[i]:
                    return 1
                elif v1_parts[i] < v2_parts[i]:
                    return -1

            return 0

        except (ValueError, AttributeError):
            # Fallback to string comparison if parsing fails
            return 1 if version1 > version2 else (-1 if version1 < version2 else 0)


def main() -> None:
    """
    Main CLI interface for SEO Sentinel.

    Provides an interactive command-line interface for website analysis,
    update checking, and configuration management.
    """
    print("=" * 70)
    print("SEO Sentinel - Automated SEO Auditing Tool")
    print("=" * 70)
    print(f"Version: {__version__}")
    print(f"Author: {__author__}")
    print(f"Website: {__website__}")
    print(f"GitHub: {__github__}")
    print("=" * 70)

    sentinel = SEOSentinel()

    while True:
        print("\n Available Options:")
        print("1. Analyze Website SEO")
        print("2. Check for Updates")
        print("3. View Configuration")
        print("4. Exit")

        try:
            choice = input("\n👉 Select an option (1-4): ").strip()

            if choice == "1":
                # Website analysis workflow
                base_url = input("\nEnter website URL to analyze: ").strip()

                if not base_url:
                    print("❌ URL cannot be empty. Please enter a valid URL.")
                    continue

                # Add protocol if missing
                if not base_url.startswith(("http://", "https://")):
                    base_url = "https://" + base_url

                if not sentinel.validate_url(base_url):
                    print("❌ Invalid or inaccessible URL. Please check and try again.")
                    continue

                # Optional keyword analysis
                keywords_input = input(
                    "\nEnter keywords to analyze (comma-separated, optional): "
                ).strip()
                keywords = (
                    [k.strip() for k in keywords_input.split(",")]
                    if keywords_input
                    else None
                )

                print(f"\nStarting analysis of {base_url}...")

                try:
                    # Crawl website
                    crawled_urls = sentinel.crawl_website(base_url)

                    if not crawled_urls:
                        print(
                            "❌ No pages could be crawled. Please check the URL and try again."
                        )
                        continue

                    # Analyze each page
                    results = {}
                    print(f"\n🔬 Analyzing {len(crawled_urls)} pages for SEO issues...")

                    for url in tqdm(crawled_urls, desc="Analyzing pages"):
                        results[url] = sentinel.analyze_seo_issues(url, keywords)

                    # Generate report
                    report_path = sentinel.generate_report(results, base_url)
                    print(f"\n✅ Analysis complete! Report saved to: {report_path}")
                    print(f"Open the report in your browser to view detailed results.")

                except Exception as e:
                    print(f"❌ Error during analysis: {e}")
                    sentinel.logger.error(f"Analysis failed: {e}")

            elif choice == "2":
                sentinel.check_for_updates()

            elif choice == "3":
                print("\n Current Configuration:")
                config_dict = asdict(sentinel.config)
                for key, value in config_dict.items():
                    print(f"  {key}: {value}")

            elif choice == "4":
                print("\n👋 Thanks for using SEO Sentinel! Stay optimized!")
                break

            else:
                print("❌ Invalid choice. Please select 1-4.")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            sentinel.logger.error(f"Unexpected error in main loop: {e}")


if __name__ == "__main__":
    main()
