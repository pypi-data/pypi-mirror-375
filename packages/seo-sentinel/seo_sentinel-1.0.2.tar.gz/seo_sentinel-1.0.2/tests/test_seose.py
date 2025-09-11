"""
Comprehensive test suite for SEO Sentinel.

This module contains unit and integration tests for all major functionality
of the SEO Sentinel tool, ensuring reliability and correctness.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup
import requests

# Import the modules to test
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seose import SEOSentinel, SEOConfig, SEOIssues, __version__


class TestSEOConfig:
    """Test cases for SEOConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = SEOConfig()
        assert config.report_directory == "reports"
        assert config.log_directory == "logs"
        assert config.crawl_depth == 3
        assert config.max_pages == 100
        assert config.request_timeout == 10
        assert config.max_workers == 5
        assert config.verify_ssl is True
        assert "SEO-Sentinel" in config.user_agent

    def test_custom_config(self):
        """Test custom configuration values."""
        config = SEOConfig(
            report_directory="custom_reports",
            crawl_depth=5,
            max_pages=50,
            request_timeout=15,
        )
        assert config.report_directory == "custom_reports"
        assert config.crawl_depth == 5
        assert config.max_pages == 50
        assert config.request_timeout == 15


class TestSEOIssues:
    """Test cases for SEOIssues dataclass."""

    def test_default_issues(self):
        """Test default SEOIssues initialization."""
        issues = SEOIssues(broken_links=[], missing_metadata=[], keyword_density={})
        assert issues.broken_links == []
        assert issues.missing_metadata == []
        assert issues.keyword_density == {}
        assert issues.page_load_time is None
        assert issues.status_code is None
        assert issues.content_length is None

    def test_issues_with_data(self):
        """Test SEOIssues with actual data."""
        issues = SEOIssues(
            broken_links=["http://broken.link"],
            missing_metadata=["Missing title"],
            keyword_density={"seo": {"count": 5, "density": 2.5}},
            page_load_time=1.5,
            status_code=200,
            content_length=1024,
        )
        assert len(issues.broken_links) == 1
        assert len(issues.missing_metadata) == 1
        assert "seo" in issues.keyword_density
        assert issues.page_load_time == 1.5
        assert issues.status_code == 200
        assert issues.content_length == 1024


class TestSEOSentinel:
    """Test cases for SEOSentinel main class."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sentinel(self, temp_dir):
        """Create SEOSentinel instance with temporary directories."""
        config = SEOConfig(
            report_directory=str(Path(temp_dir) / "reports"),
            log_directory=str(Path(temp_dir) / "logs"),
        )
        return SEOSentinel(config)

    def test_initialization(self, sentinel):
        """Test SEOSentinel initialization."""
        assert sentinel.config is not None
        assert sentinel.logger is not None
        assert sentinel.session is not None
        assert hasattr(sentinel.session, "headers")

    def test_directory_creation(self, sentinel):
        """Test that required directories are created."""
        assert Path(sentinel.config.report_directory).exists()
        assert Path(sentinel.config.log_directory).exists()

    @patch("seose.requests.Session.head")
    def test_check_internet_connection_success(self, mock_head, sentinel):
        """Test successful internet connection check."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_head.return_value = mock_response

        assert sentinel.check_internet_connection() is True

    @patch("seose.requests.Session.head")
    def test_check_internet_connection_failure(self, mock_head, sentinel):
        """Test failed internet connection check."""
        mock_head.side_effect = requests.RequestException("Connection failed")

        assert sentinel.check_internet_connection() is False

    def test_validate_url_valid(self, sentinel):
        """Test URL validation with valid URLs."""
        with patch.object(sentinel.session, "head") as mock_head:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_head.return_value = mock_response

            assert sentinel.validate_url("https://example.com") is True

    def test_validate_url_invalid(self, sentinel):
        """Test URL validation with invalid URLs."""
        assert sentinel.validate_url("not-a-url") is False
        assert sentinel.validate_url("") is False
        assert sentinel.validate_url("ftp://example.com") is False

    @patch("seose.requests.Session.get")
    def test_fetch_html_content_success(self, mock_get, sentinel):
        """Test successful HTML content fetching."""
        mock_response = Mock()
        mock_response.text = "<html><body>Test</body></html>"
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = sentinel.fetch_html_content("https://example.com")

        assert result is not None
        html, status, load_time = result
        assert html == "<html><body>Test</body></html>"
        assert status == 200
        assert isinstance(load_time, float)
        assert load_time >= 0

    @patch("seose.requests.Session.get")
    def test_fetch_html_content_failure(self, mock_get, sentinel):
        """Test failed HTML content fetching."""
        mock_get.side_effect = requests.RequestException("Request failed")

        result = sentinel.fetch_html_content("https://example.com")
        assert result is None

    def test_extract_links(self, sentinel):
        """Test link extraction from HTML content."""
        html_content = """
        <html>
            <body>
                <a href="https://example.com/page1">Page 1</a>
                <a href="/page2">Page 2</a>
                <a href="mailto:test@example.com">Email</a>
                <a href="#section">Section</a>
                <a href="javascript:void(0)">JS Link</a>
                <a href="https://other-domain.com/page">Other Domain</a>
            </body>
        </html>
        """

        links = sentinel._extract_links(
            html_content, "https://example.com", "example.com"
        )

        # Should only include same-domain HTTP(S) links
        assert "https://example.com/page1" in links
        assert "https://example.com/page2" in links
        assert len([link for link in links if "mailto:" in link]) == 0
        assert len([link for link in links if "javascript:" in link]) == 0
        assert len([link for link in links if "other-domain.com" in link]) == 0

    def test_analyze_metadata_missing_title(self, sentinel):
        """Test metadata analysis with missing title."""
        html_content = "<html><body>Content without title</body></html>"
        soup = BeautifulSoup(html_content, "html.parser")
        issues = SEOIssues(broken_links=[], missing_metadata=[], keyword_density={})

        sentinel._analyze_metadata(soup, issues)

        assert "Missing <title> tag" in issues.missing_metadata

    def test_analyze_metadata_empty_title(self, sentinel):
        """Test metadata analysis with empty title."""
        html_content = "<html><head><title></title></head><body>Content</body></html>"
        soup = BeautifulSoup(html_content, "html.parser")
        issues = SEOIssues(broken_links=[], missing_metadata=[], keyword_density={})

        sentinel._analyze_metadata(soup, issues)

        assert "Empty <title> tag" in issues.missing_metadata

    def test_analyze_metadata_long_title(self, sentinel):
        """Test metadata analysis with overly long title."""
        long_title = "A" * 70  # Longer than 60 characters
        html_content = (
            f"<html><head><title>{long_title}</title></head><body>Content</body></html>"
        )
        soup = BeautifulSoup(html_content, "html.parser")
        issues = SEOIssues(broken_links=[], missing_metadata=[], keyword_density={})

        sentinel._analyze_metadata(soup, issues)

        assert "Title tag too long (>60 characters)" in issues.missing_metadata

    def test_analyze_metadata_missing_description(self, sentinel):
        """Test metadata analysis with missing meta description."""
        html_content = (
            "<html><head><title>Good Title</title></head><body>Content</body></html>"
        )
        soup = BeautifulSoup(html_content, "html.parser")
        issues = SEOIssues(broken_links=[], missing_metadata=[], keyword_density={})

        sentinel._analyze_metadata(soup, issues)

        assert "Missing meta description" in issues.missing_metadata

    def test_analyze_metadata_missing_h1(self, sentinel):
        """Test metadata analysis with missing H1 tag."""
        html_content = """
        <html>
            <head>
                <title>Good Title</title>
                <meta name="description" content="Good description">
            </head>
            <body>
                <h2>Only H2 here</h2>
            </body>
        </html>
        """
        soup = BeautifulSoup(html_content, "html.parser")
        issues = SEOIssues(broken_links=[], missing_metadata=[], keyword_density={})

        sentinel._analyze_metadata(soup, issues)

        assert "Missing H1 tag" in issues.missing_metadata

    def test_analyze_metadata_multiple_h1(self, sentinel):
        """Test metadata analysis with multiple H1 tags."""
        html_content = """
        <html>
            <head>
                <title>Good Title</title>
                <meta name="description" content="Good description">
            </head>
            <body>
                <h1>First H1</h1>
                <h1>Second H1</h1>
            </body>
        </html>
        """
        soup = BeautifulSoup(html_content, "html.parser")
        issues = SEOIssues(broken_links=[], missing_metadata=[], keyword_density={})

        sentinel._analyze_metadata(soup, issues)

        assert "Multiple H1 tags found" in issues.missing_metadata

    def test_analyze_keyword_density(self, sentinel):
        """Test keyword density analysis."""
        html_content = """
        <html>
            <body>
                <p>SEO is important for websites. Good SEO practices help with SEO optimization.</p>
                <p>Python is a programming language. Python developers use Python for web development.</p>
            </body>
        </html>
        """
        soup = BeautifulSoup(html_content, "html.parser")
        issues = SEOIssues(broken_links=[], missing_metadata=[], keyword_density={})
        keywords = ["SEO", "Python"]

        sentinel._analyze_keyword_density(soup, keywords, issues)

        assert "SEO" in issues.keyword_density
        assert "Python" in issues.keyword_density
        assert issues.keyword_density["SEO"]["count"] == 3
        assert issues.keyword_density["Python"]["count"] == 3
        assert isinstance(issues.keyword_density["SEO"]["density"], float)

    @patch("seose.requests.Session.head")
    def test_analyze_links_broken(self, mock_head, sentinel):
        """Test broken link analysis."""
        html_content = """
        <html>
            <body>
                <a href="https://broken-link.com">Broken Link</a>
                <a href="https://working-link.com">Working Link</a>
            </body>
        </html>
        """

        def mock_head_response(url, **kwargs):
            if "broken-link" in url:
                raise requests.RequestException("Connection failed")
            else:
                response = Mock()
                response.status_code = 200
                return response

        mock_head.side_effect = mock_head_response

        soup = BeautifulSoup(html_content, "html.parser")
        issues = SEOIssues(broken_links=[], missing_metadata=[], keyword_density={})

        sentinel._analyze_links(soup, "https://example.com", issues)

        assert "https://broken-link.com" in issues.broken_links
        assert "https://working-link.com" not in issues.broken_links

    def test_compare_versions(self, sentinel):
        """Test version comparison functionality."""
        # Test newer version
        assert sentinel._compare_versions("1.2.3", "1.2.2") == 1
        assert sentinel._compare_versions("2.0.0", "1.9.9") == 1
        assert sentinel._compare_versions("1.2.10", "1.2.9") == 1

        # Test older version
        assert sentinel._compare_versions("1.2.2", "1.2.3") == -1
        assert sentinel._compare_versions("1.9.9", "2.0.0") == -1

        # Test equal versions
        assert sentinel._compare_versions("1.2.3", "1.2.3") == 0
        assert sentinel._compare_versions("2.0.0", "2.0.0") == 0

        # Test with 'v' prefix
        assert sentinel._compare_versions("v1.2.3", "1.2.2") == 1
        assert sentinel._compare_versions("1.2.3", "v1.2.2") == 1

    @patch("seose.requests.Session.get")
    def test_check_for_updates_newer_available(self, mock_get, sentinel):
        """Test update check when newer version is available."""
        mock_response = Mock()
        mock_response.json.return_value = {"info": {"version": "2.0.0"}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        with patch("seose.SEOSentinel.check_internet_connection", return_value=True):
            with patch("builtins.print") as mock_print:
                sentinel.check_for_updates()

                # Check that update notification was printed
                print_calls = [str(call) for call in mock_print.call_args_list]
                assert any("New version available" in call for call in print_calls)

    @patch("seose.requests.Session.get")
    def test_check_for_updates_current_latest(self, mock_get, sentinel):
        """Test update check when current version is latest."""
        mock_response = Mock()
        mock_response.json.return_value = {"info": {"version": __version__}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        with patch("seose.SEOSentinel.check_internet_connection", return_value=True):
            with patch("builtins.print") as mock_print:
                sentinel.check_for_updates()

                # Check that "latest version" message was printed
                print_calls = [str(call) for call in mock_print.call_args_list]
                assert any("latest version" in call for call in print_calls)

    @patch("seose.requests.Session.get")
    def test_check_for_updates_network_error(self, mock_get, sentinel):
        """Test update check with network error."""
        mock_get.side_effect = requests.RequestException("Network error")

        with patch("seose.SEOSentinel.check_internet_connection", return_value=True):
            with patch("builtins.print") as mock_print:
                sentinel.check_for_updates()

                # Check that error message was printed
                print_calls = [str(call) for call in mock_print.call_args_list]
                assert any("Error checking for updates" in call for call in print_calls)

    def test_check_for_updates_no_internet(self, sentinel):
        """Test update check without internet connection."""
        with patch("seose.SEOSentinel.check_internet_connection", return_value=False):
            with patch("builtins.print") as mock_print:
                sentinel.check_for_updates()

                # Check that no internet message was printed
                print_calls = [str(call) for call in mock_print.call_args_list]
                assert any("No internet connection" in call for call in print_calls)


@pytest.mark.integration
class TestSEOSentinelIntegration:
    """Integration tests for SEO Sentinel."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sentinel(self, temp_dir):
        """Create SEOSentinel instance with temporary directories."""
        config = SEOConfig(
            report_directory=str(Path(temp_dir) / "reports"),
            log_directory=str(Path(temp_dir) / "logs"),
            max_pages=5,  # Limit for testing
            crawl_depth=1,
        )
        return SEOSentinel(config)

    @patch("seose.requests.Session.get")
    @patch("seose.requests.Session.head")
    def test_full_analysis_workflow(self, mock_head, mock_get, sentinel):
        """Test complete analysis workflow with mocked responses."""
        # Mock successful URL validation
        mock_head_response = Mock()
        mock_head_response.status_code = 200
        mock_head.return_value = mock_head_response

        # Mock HTML content fetching
        mock_html = """
        <html>
            <head>
                <title>Test Page</title>
                <meta name="description" content="Test description">
            </head>
            <body>
                <h1>Main Heading</h1>
                <p>This is a test page with SEO content.</p>
                <a href="/page2">Internal Link</a>
            </body>
        </html>
        """

        mock_get_response = Mock()
        mock_get_response.text = mock_html
        mock_get_response.status_code = 200
        mock_get_response.raise_for_status = Mock()
        mock_get.return_value = mock_get_response

        # Run analysis
        base_url = "https://example.com"
        crawled_urls = sentinel.crawl_website(base_url)

        assert len(crawled_urls) > 0
        assert base_url in crawled_urls

        # Analyze SEO issues
        results = {}
        for url in crawled_urls:
            results[url] = sentinel.analyze_seo_issues(url, ["SEO", "test"])

        # Verify results
        assert base_url in results
        issues = results[base_url]
        assert isinstance(issues, SEOIssues)
        assert issues.status_code == 200
        assert isinstance(issues.page_load_time, float)

        # Generate report
        report_path = sentinel.generate_report(results, base_url)
        assert Path(report_path).exists()

        # Verify report content
        with open(report_path, "r", encoding="utf-8") as f:
            report_content = f.read()
            assert "SEO Sentinel Report" in report_content
            assert base_url in report_content
            assert __version__ in report_content


@pytest.mark.slow
class TestSEOSentinelPerformance:
    """Performance tests for SEO Sentinel."""

    def test_large_html_parsing(self):
        """Test parsing of large HTML documents."""
        # Create large HTML content
        large_html = "<html><body>"
        for i in range(1000):
            large_html += f"<p>This is paragraph {i} with some content.</p>"
        large_html += "</body></html>"

        sentinel = SEOSentinel()
        soup = BeautifulSoup(large_html, "html.parser")
        issues = SEOIssues(broken_links=[], missing_metadata=[], keyword_density={})

        # This should complete without timeout
        import time

        start_time = time.time()
        sentinel._analyze_metadata(soup, issues)
        end_time = time.time()

        # Should complete within reasonable time (adjust as needed)
        assert end_time - start_time < 5.0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
