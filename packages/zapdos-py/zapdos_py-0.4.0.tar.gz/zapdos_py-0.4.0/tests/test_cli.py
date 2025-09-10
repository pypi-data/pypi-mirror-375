"""Test module for zapdos video indexing."""

import unittest
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch
from zapdos.cli import index_video_file, search


class TestZapdos(unittest.TestCase):
    def test_index_video_file_not_exists(self):
        """Test indexing a video file that does not exist."""
        with self.assertRaises(FileNotFoundError):
            index_video_file("nonexistent_video.mp4")
    
    @patch('zapdos.cli.os.getenv')
    def test_search_no_api_key(self, mock_getenv):
        """Test search when no API key is set."""
        # Mock environment variable to return None
        mock_getenv.return_value = None
        
        # Capture stdout to check error message
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            result = search("test query")
            output = captured_output.getvalue()
            self.assertFalse(result)
            self.assertIn("Error: ZAPDOS_API_KEY environment variable not set.", output)
        finally:
            sys.stdout = old_stdout


if __name__ == "__main__":
    unittest.main()