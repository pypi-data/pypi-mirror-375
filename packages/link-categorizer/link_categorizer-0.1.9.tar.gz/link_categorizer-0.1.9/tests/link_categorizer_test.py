# setup unit test for link_categorizer.py

from pathlib import Path
import unittest
import yaml
from link_categorizer.categorizer import categorize_links, categorize_link


class TestLinkCategorizer(unittest.TestCase):
    def setUp(self):
        # Use pathlib for cross-platform path handling
        test_dir = Path(__file__).parent
        self.data_schemes = yaml.safe_load((test_dir / "test_data_url_schemes.yml").read_text())
        self.data_domains = yaml.safe_load((test_dir / "test_data_domains.yml").read_text())
        self.data_paths = yaml.safe_load((test_dir / "test_data_paths.yml").read_text())
        self.data_titles = yaml.safe_load((test_dir / "test_data_titles.yml").read_text())

    def test_categorize_link_schemes(self):
        for test in self.data_schemes:
            with self.subTest(test=test):
                self.assertEqual(categorize_link(test), test["expected"])

    def test_categorize_link_domains(self):
        for test in self.data_domains:
            with self.subTest(test=test):
                self.assertEqual(categorize_link(test), test["expected"])

    def test_categorize_link_paths(self):
        for test in self.data_paths:
            with self.subTest(test=test):
                self.assertEqual(categorize_link(test), test["expected"])

    def test_categorize_link_titles(self):
        for test in self.data_titles:
            with self.subTest(test=test):
                self.assertEqual(categorize_link(test), test["expected"])

    def test_categorize_link_text(self):
        for test in self.data_titles:
            test["text"] = test["title"]
            del test["title"]
            with self.subTest(test=test):
                self.assertEqual(categorize_link(test), test["expected"])


class TestDeduplicateLinks(unittest.TestCase):
    def test_deduplicate_links(self):
        test_data = [
            {"href": "https://example.com", "text": "Example"},
            {"href": "https://example.com", "text": "Example"},
            {"href": "https://example.org", "text": "Example Org"},
        ]

        expected_result = [
            {"category": "home", "href": "https://example.com", "text": "Example"},
            {"category": "home", "href": "https://example.org", "text": "Example Org"},
        ]

        result = categorize_links(test_data)
        self.assertEqual(result, expected_result)
