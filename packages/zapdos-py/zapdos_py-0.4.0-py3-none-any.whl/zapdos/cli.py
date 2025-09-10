"""CLI module for zapdos video indexing."""

import argparse
import sys
from pathlib import Path
from typing import Union, List, Dict, Any
from .video_indexer import index
from .definitions import IndexEvents
from .client import Client
import json
import os

class ProgressIndicator:
    """Simple progress indicator for video indexing."""
    
    def __init__(self):
        self.uploaded_count = 0
        self.total_uploads = 0
        self.is_uploading = False
        self.embedding_count = 0
        self.total_embeddings = 0
        
    def start_upload_tracking(self, total_count):
        """Initialize upload tracking."""
        self.total_uploads = total_count
        self.uploaded_count = 0
        self.is_uploading = True
        self._update_upload_progress()
        
    def update_upload(self):
        """Update upload progress."""
        if self.is_uploading:
            self.uploaded_count += 1
            self._update_upload_progress()
            
    def finish_uploading(self):
        """Finish upload tracking."""
        self.is_uploading = False
        # Clear the progress line
        if self.total_uploads > 0:
            sys.stdout.write('\r' + ' ' * 60 + '\r')
            sys.stdout.flush()
            
    def _update_upload_progress(self):
        """Update the upload progress display."""
        if self.is_uploading and self.total_uploads > 0:
            percentage = (self.uploaded_count / self.total_uploads) * 100
            bar_length = 30
            filled_length = int(bar_length * self.uploaded_count // self.total_uploads)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            sys.stdout.write(f'\r📤 Uploading media: |{bar}| {self.uploaded_count}/{self.total_uploads} ({percentage:.1f}%)')
            sys.stdout.flush()

# Global progress indicator instance
progress_indicator = ProgressIndicator()

def _progress_callback(event_data):
    """Callback function to handle progress updates."""
    event_type = event_data.get("event", "unknown")
    
    if event_type == IndexEvents.INSERTED_VIDEO_FILE_RECORD:
        video_file_id = event_data.get("video_file_id")
        print(f"✓ Created video file record with ID: {video_file_id}")
    elif event_type == IndexEvents.UPLOADED_FRAME:
        # Track uploads with progress indicator
        progress_indicator.update_upload()
    elif event_type == IndexEvents.INSERTED_FRAMES_RECORDS:
        count = event_data.get("count", 0)
        progress_indicator.finish_uploading()
        print(f"💾 Indexed {count} items into database")
    elif event_type == IndexEvents.CREATED_IMAGE_DESCRIPTION_JOB:
        job_id = event_data.get("job_id")
        print(f"⚙️  Created image description job with ID: {job_id}")
    elif event_type == IndexEvents.COMPLETED_IMAGE_DESCRIPTION_JOB:
        job_id = event_data.get("job_id")
        print(f"✅ Completed image description job with ID: {job_id}")
    elif event_type == IndexEvents.CREATED_OBJECT_DETECTION_JOB:
        job_id = event_data.get("job_id")
        print(f"🔍 Created object detection job with ID: {job_id}")
    elif event_type == IndexEvents.COMPLETED_OBJECT_DETECTION_JOB:
        job_id = event_data.get("job_id")
        print(f"✅ Completed object detection job with ID: {job_id}")
    elif event_type == IndexEvents.CREATED_SUMMARY_JOB:
        job_id = event_data.get("job_id")
        print(f"📝 Created summary job with ID: {job_id}")
    elif event_type == IndexEvents.COMPLETED_SUMMARY_JOB:
        job_id = event_data.get("job_id")
        print(f"✅ Completed summary job with ID: {job_id}")
    elif event_type == IndexEvents.CREATED_EMBEDDING_JOB:
        job_id = event_data.get("job_id")
        total_embeddings = event_data.get("total_embeddings", 0)
        print(f"🧠 Created embedding job with ID: {job_id}")
        # Initialize embedding counter
        progress_indicator.embedding_count = 0
        progress_indicator.total_embeddings = total_embeddings
    elif event_type == "partial-embedding-result":
        # Update embedding counter and show progress
        progress_indicator.embedding_count += 1
        # Update the progress display
        sys.stdout.write(f'\r🧠 Received embeddings: {progress_indicator.embedding_count}/{progress_indicator.total_embeddings}')
        sys.stdout.flush()
    elif event_type == IndexEvents.COMPLETED_EMBEDDING_JOB:
        job_id = event_data.get("job_id")
        frame_ids = event_data.get("frame_ids", [])
        # Set total embeddings if not already set
        if progress_indicator.total_embeddings == 0:
            progress_indicator.total_embeddings = len(frame_ids)
        # Clear the progress line and show completion
        sys.stdout.write(f'\r{" " * 60}\r')  # Clear the line
        sys.stdout.flush()
        print(f"✅ Completed embedding job with ID: {job_id} ({len(frame_ids)} embeddings)")
    elif event_type == IndexEvents.DONE_INDEXING:
        print(f"🎉 Video indexing completed successfully!")
    elif event_type == IndexEvents.ERROR_INDEXING:
        error_msg = event_data.get("message", "Unknown error")
        progress_indicator.finish_uploading()
        print(f"❌ Error: {error_msg}")
    else:
        print(f"ℹ️  Unknown event: {event_data}")

def index_video_file(file_path: Union[str, Path], interval: int = 30, output_file: Union[str, Path] = None) -> bool:
    """Index the specified video file by processing and uploading items.
    
    Args:
        file_path: Path to the video file to index
        interval: Interval between items in seconds (default: 30)
        output_file: Output file path for the indexing results (default: temporary file)
        
    Returns:
        bool: True if indexing was successful, False otherwise
    """
    path = Path(file_path) if isinstance(file_path, str) else file_path
    if not path.exists():
        raise FileNotFoundError(f"Video file '{file_path}' does not exist.")
    
    # Get API key from environment variable
    api_key = os.getenv("ZAPDOS_API_KEY")
    if not api_key:
        print("Error: ZAPDOS_API_KEY environment variable not set.")
        return False
    
    try:
        print(f"Indexing video file: {path.absolute()}")
        # Estimate number of items based on video duration and interval
        print("📤 Preparing media for upload...")
        result = index(path, interval_sec=interval, progress_callback=_progress_callback, api_key=api_key)
        print(f"Successfully processed {len(result['items'])} items")
        
        # Write results to output file
        if output_file:
            output_path = Path(output_file)
            # Create parent directories if they don't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Results written to: {output_path.absolute()}")
        else:
            # Write to temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(result, f, indent=2)
                temp_path = f.name
            print(f"Results written to temporary file: {temp_path}")
        
        return True
    except Exception as e:
        progress_indicator.finish_uploading()
        print(f"Error indexing video file: {e}")
        return False


def search(query: Union[str, List[str], List[Dict[str, Any]]], output_file: Union[str, Path] = None) -> bool:
    """Search for content using text queries.
    
    Args:
        query: Can be one of:
            - A single string: "a sentence"
            - A list of strings: ['query1', 'query2']
            - A list of dictionaries: [{'type': 'text', 'value': 'query1'}, ...]
        output_file: Output file path for the search results (default: temporary file)
        
    Returns:
        bool: True if search was successful, False otherwise
    """
    # Get API key from environment variable
    api_key = os.getenv("ZAPDOS_API_KEY")
    if not api_key:
        print("Error: ZAPDOS_API_KEY environment variable not set.")
        return False
    
    try:
        # Create client and perform search
        client = Client(api_key=api_key)
        result = client.search(query)
        
        # Print summary of results
        results = result.get("results", [])
        print(f"Search completed successfully with {len(results)} result sets")
        for i, result_set in enumerate(results):
            print(f"Result set {i} has {len(result_set)} items")
            if result_set:  # If there are results
                print(f"First item in result set {i}: {result_set[0]['field'].get('value', {}).get('string_value', 'N/A')}")
        
        # Write results to output file
        if output_file:
            output_path = Path(output_file)
            # Create parent directories if they don't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Results written to: {output_path.absolute()}")
        else:
            # Write to temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(result, f, indent=2)
                temp_path = f.name
            print(f"Results written to temporary file: {temp_path}")
        
        return True
    except Exception as e:
        print(f"Error performing search: {e}")
        return False


def main() -> None:
    """Main entry point for the zapdos CLI."""
    parser = argparse.ArgumentParser(
        description="Zapdos - A CLI tool for indexing video files and searching content"
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Index command
    index_parser = subparsers.add_parser('index', help='Index a video file')
    index_parser.add_argument(
        "file_path", 
        help="Path to the video file to index"
    )
    index_parser.add_argument(
        "--interval", 
        type=int, 
        default=5,
        help="Interval between items in seconds (default: 5)"
    )
    index_parser.add_argument(
        "-o", "--out",
        help="Output file path for the indexing results (default: temporary file)"
    )
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for content using text queries')
    search_parser.add_argument(
        "query",
        help="Search query - can be a single string or a JSON array of strings/dictionaries"
    )
    search_parser.add_argument(
        "-o", "--out",
        help="Output file path for the search results (default: temporary file)"
    )
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    
    if args.command == 'index':
        # Handle video indexing
        try:
            success = index_video_file(args.file_path, args.interval, args.out)
            if not success:
                sys.exit(1)
        except FileNotFoundError as e:
            print(f"Error: {e}")
            sys.exit(1)
    elif args.command == 'search':
        # Handle search
        try:
            # Try to parse as JSON, otherwise treat as a simple string
            try:
                query = json.loads(args.query)
            except json.JSONDecodeError:
                # If it's not valid JSON, treat as a simple string
                query = args.query
            
            success = search(query, args.out)
            if not success:
                sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()