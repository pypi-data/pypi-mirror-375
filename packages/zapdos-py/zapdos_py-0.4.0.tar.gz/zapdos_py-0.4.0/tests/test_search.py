"""Test module for zapdos search functionality."""

import unittest
import json
from unittest.mock import patch, MagicMock
from zapdos.client import Client
from zapdos.cli import search


class TestSearch(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key"
        self.client = Client(api_key=self.api_key)
        
    def test_search_single_string(self):
        """Test search with a single string query."""
        # Mock the requests.post response
        with patch('requests.post') as mock_post:
            # Create a mock response
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "results": [
                    [
                        {
                            "field": {
                                "tenant_id": "tenant1",
                                "media_unit_id": "media1",
                                "name": "description",
                                "value": {
                                    "string_value": "Hello world test",
                                    "number_value": None
                                },
                                "vector": None
                            },
                            "media_unit": {
                                "tenant_id": "tenant1",
                                "id": "media1",
                                "type": "frame",
                                "root_id": None,
                                "value": {
                                    "from_ms": 1000,
                                    "to_ms": 2000,
                                    "x": None,
                                    "y": None,
                                    "width": None,
                                    "height": None
                                }
                            }
                        }
                    ]
                ]
            }
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            # Call the search method
            result = self.client.search("Hello world")
            
            # Verify the request was made with correct parameters
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            self.assertEqual(kwargs['headers']['Authorization'], f"Bearer {self.api_key}")
            self.assertEqual(kwargs['json']['texts'], [{"type": "text", "value": "Hello world"}])
            
            # Verify the result
            self.assertIn("results", result)
            self.assertEqual(len(result["results"]), 1)
            
    def test_search_list_of_strings(self):
        """Test search with a list of string queries."""
        # Mock the requests.post response
        with patch('requests.post') as mock_post:
            # Create a mock response
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "results": [
                    [],  # Results for first query
                    []   # Results for second query
                ]
            }
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            # Call the search method
            result = self.client.search(["Hello", "world"])
            
            # Verify the request was made with correct parameters
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            self.assertEqual(kwargs['headers']['Authorization'], f"Bearer {self.api_key}")
            self.assertEqual(kwargs['json']['texts'], [
                {"type": "text", "value": "Hello"},
                {"type": "text", "value": "world"}
            ])
            
            # Verify the result
            self.assertIn("results", result)
            self.assertEqual(len(result["results"]), 2)
            
    def test_search_list_of_dicts(self):
        """Test search with a list of dictionary queries."""
        # Mock the requests.post response
        with patch('requests.post') as mock_post:
            # Create a mock response
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "results": [
                    [],  # Results for first query
                    []   # Results for second query
                ]
            }
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            # Call the search method
            result = self.client.search([
                {"type": "text", "value": "Hello"},
                {"type": "text", "value": "world"}
            ])
            
            # Verify the request was made with correct parameters
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            self.assertEqual(kwargs['headers']['Authorization'], f"Bearer {self.api_key}")
            self.assertEqual(kwargs['json']['texts'], [
                {"type": "text", "value": "Hello"},
                {"type": "text", "value": "world"}
            ])
            
            # Verify the result
            self.assertIn("results", result)
            self.assertEqual(len(result["results"]), 2)
            
    def test_search_invalid_input(self):
        """Test search with invalid input types."""
        # Test with invalid dictionary format
        with self.assertRaises(ValueError):
            self.client.search([{"type": "image", "value": "test"}])
            
        # Test with mixed types in list
        with self.assertRaises(ValueError):
            self.client.search(["string", {"type": "text", "value": "test"}])
            
        # Test with unsupported type
        with self.assertRaises(ValueError):
            self.client.search(123)
            
    @patch('zapdos.cli.os.getenv')
    def test_cli_search_success(self, mock_getenv):
        """Test CLI search function success case."""
        # Mock environment variable
        mock_getenv.return_value = self.api_key
        
        # Mock the Client.search method
        with patch('zapdos.cli.Client.search') as mock_search:
            mock_search.return_value = {
                "results": [
                    [
                        {
                            "field": {
                                "value": {
                                    "string_value": "Test result"
                                }
                            }
                        }
                    ]
                ]
            }
            
            # Call the search function
            result = search("test query")
            
            # Verify it was successful
            self.assertTrue(result)
            mock_search.assert_called_once_with("test query")
            
    @patch('zapdos.cli.os.getenv')
    def test_cli_search_no_api_key(self, mock_getenv):
        """Test CLI search function when no API key is set."""
        # Mock environment variable to return None
        mock_getenv.return_value = None
        
        # Call the search function and capture stdout
        result = search("test query")
        
        # Verify it failed
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()