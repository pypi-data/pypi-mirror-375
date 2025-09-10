"""Client module for zapdos API."""

from typing import Optional, Callable, Union, List, Dict, Any
from pathlib import Path
import requests
import json
from .video_indexer import index


class Client:
    """Zapdos API Client.
    
    This client is used to interact with the Zapdos API services.
    """
    
    def __init__(self, api_key: str, server_url: str = "https://api.zapdoslabs.com"):
        """Initialize the Zapdos client.
        
        Args:
            api_key: Your Zapdos API key for authentication
            server_url: The base URL for the Zapdos API (default: https://api.zapdoslabs.com)
        """
        self.api_key = api_key
        self.server_url = server_url
    
    def index(self, video_path: Union[str, Path], interval_sec: int = 30, 
              progress_callback: Optional[Callable[[dict], None]] = None) -> dict:
        """Index a video file by processing items and uploading them for processing.
        
        Args:
            video_path: Path to the video file to index
            interval_sec: Interval between items in seconds (default: 30)
            progress_callback: Optional callback function to receive progress updates
            
        Returns:
            Dictionary containing the indexing results
        """
        return index(
            video_path=video_path,
            interval_sec=interval_sec,
            server_url=self.server_url,
            progress_callback=progress_callback,
            api_key=self.api_key
        )
    
    def search(self, query: Union[str, List[str], List[Dict[str, Any]]]) -> dict:
        """Search for content using text queries.
        
        Args:
            query: Can be one of:
                - A single string: "a sentence"
                - A list of strings: ['query1', 'query2']
                - A list of dictionaries: [{'type': 'text', 'value': 'query1'}, ...]
                
        Returns:
            Dictionary containing search results with matched fields and media units
        """
        # Normalize input to the expected format
        if isinstance(query, str):
            # Single string case
            texts = [{"type": "text", "value": query}]
        elif isinstance(query, list):
            # List case - check if it's a list of strings or dicts
            if all(isinstance(item, str) for item in query):
                # List of strings
                texts = [{"type": "text", "value": item} for item in query]
            elif all(isinstance(item, dict) for item in query):
                # List of dictionaries - validate format
                for item in query:
                    if not (isinstance(item, dict) and 
                            item.get("type") == "text" and 
                            "value" in item):
                        raise ValueError("All items in dictionary list must have 'type': 'text' and 'value' fields")
                texts = query
            else:
                raise ValueError("List must contain either all strings or all dictionaries with 'type' and 'value' keys")
        else:
            raise ValueError("Query must be a string, list of strings, or list of dictionaries")
        
        # Make the API request
        url = f"{self.server_url}/search"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {"texts": texts}
        
        response = requests.post(url, headers=headers, json=data)
        
        # Raise an exception for bad status codes
        response.raise_for_status()
        
        return response.json()