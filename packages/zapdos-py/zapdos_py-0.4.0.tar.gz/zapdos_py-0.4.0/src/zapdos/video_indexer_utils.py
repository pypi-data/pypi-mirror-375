import os
import aiohttp
import asyncio
import jsonlines
import json
from typing import List, Optional, Callable
from .definitions import IndexEvents
import re

async def _upload_batch(session, batch_files, batch_timestamps, base_data, server_url, progress_callback, semaphore, items, api_key=None):
    """
    Upload a single batch asynchronously. Semaphore controls when batch can start.
    """
    async with semaphore:
        data = base_data.copy()
        files = {}

        # Prepare files for aiohttp multipart upload
        for idx, (filename, file_path) in enumerate(batch_files):
            data[f"timestamp_{idx}"] = str(batch_timestamps[idx])
            files[f"frame_{idx}"] = open(file_path, "rb")

        try:
            # aiohttp multipart POST
            form = aiohttp.FormData()
            for k, f in files.items():
                form.add_field(k, f, filename=os.path.basename(f.name), content_type="image/jpeg")
            for k, v in data.items():
                form.add_field(k, v)

            # Add authorization header if API key is provided
            headers = {}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

            async with session.post(f"{server_url}/index", data=form, headers=headers, timeout=aiohttp.ClientTimeout(total=180)) as resp:
                if resp.status in [200, 201, 207]:
                    # Initialize data structures to collect results
                    frame_results = {}  # frame_id -> {description, objects}
                    summary_result = None
                    video_file_id = None
                    
                    # Process streaming response line by line
                    async for line in resp.content:
                        try:
                            event_data = json.loads(line.decode())
                        except Exception:
                            continue

                        event_type = event_data.get("event", "unknown")

                        # Call progress callback
                        if progress_callback:
                            progress_callback(event_data)

                        # Handle object detection job completion with full result and frame IDs
                        if event_type == IndexEvents.COMPLETED_OBJECT_DETECTION_JOB and "result" in event_data and "frame_ids" in event_data:
                            job_result = event_data["result"]
                            frame_ids = event_data["frame_ids"]
                            if "detections" in job_result:
                                detections = job_result["detections"]
                                # Associate each detection with its frame ID
                                for i, detection in enumerate(detections):
                                    if i < len(frame_ids):
                                        frame_id = frame_ids[i]
                                        if frame_id not in frame_results:
                                            frame_results[frame_id] = {}
                                        if "objects" not in frame_results[frame_id]:
                                            frame_results[frame_id]["objects"] = []
                                        frame_results[frame_id]["objects"].extend(detection)

                        # Handle image description job completion with full result and frame IDs
                        if event_type == IndexEvents.COMPLETED_IMAGE_DESCRIPTION_JOB and "result" in event_data and "frame_ids" in event_data:
                            job_result = event_data["result"]
                            frame_ids = event_data["frame_ids"]
                            if "descriptions" in job_result:
                                descriptions = job_result["descriptions"]
                                # Associate each description with its frame ID
                                for i, description in enumerate(descriptions):
                                    if i < len(frame_ids):
                                        frame_id = frame_ids[i]
                                        if frame_id not in frame_results:
                                            frame_results[frame_id] = {}
                                        frame_results[frame_id]["description"] = description

                        # Handle individual embedding results
                        if event_type == "partial-embedding-result" and "frame_id" in event_data and "embedding" in event_data:
                            frame_id = event_data["frame_id"]
                            embedding = event_data["embedding"]
                            if frame_id not in frame_results:
                                frame_results[frame_id] = {}
                            frame_results[frame_id]["embedding"] = embedding

                        # Handle summary result
                        if event_type == IndexEvents.COMPLETED_SUMMARY_JOB and "result" in event_data:
                            job_result = event_data["result"]
                            if job_result and "summaries" in job_result and job_result["summaries"]:
                                # Always use the first (and only) summary since we process one video at a time
                                the_summary = job_result["summaries"][0]
                                summary_result = {
                                    "type": "segment",
                                    "summary": the_summary
                                }
                                if "media_unit_id" in event_data:
                                    summary_result["id"] = event_data["media_unit_id"]

                        # Handle embedding job completion with frame IDs
                        if event_type == IndexEvents.COMPLETED_EMBEDDING_JOB and "frame_ids" in event_data:
                            frame_ids = event_data["frame_ids"]
                            # For any frames that didn't get individual embedding results, mark them as processed
                            for frame_id in frame_ids:
                                if frame_id not in frame_results:
                                    frame_results[frame_id] = {}
                                # If we don't have an embedding yet, add a placeholder
                                if "embedding" not in frame_results[frame_id]:
                                    frame_results[frame_id]["embedding_processed"] = True

                        # Handle video file ID from DONE_INDEXING event
                        if event_type == IndexEvents.DONE_INDEXING:
                            video_file_id = event_data.get("video_file_id")
                            
                            # Compose final items from collected results
                            batch_items = []
                            
                            # Add frame results
                            for frame_id, frame_data in frame_results.items():
                                item = {
                                    "type": "frame",
                                    "id": frame_id
                                }
                                item.update(frame_data)
                                batch_items.append(item)
                            
                            # Add summary result if available
                            if summary_result:
                                batch_items.append(summary_result)
                                
                            items.extend(batch_items)

                        # COMPLETED_IMAGE_DESCRIPTION_JOB: allow next batch to start
                        if event_type == IndexEvents.COMPLETED_IMAGE_DESCRIPTION_JOB and "result" not in event_data:
                            semaphore.release()
                else:
                    print(f"Failed to upload batch: {resp.status} - {await resp.text()}")
        except aiohttp.ClientConnectionError as e:
            print(f"Connection error during upload: {e}")
        except asyncio.TimeoutError as e:
            print(f"Timeout during upload: {e}")
        except Exception as e:
            import traceback
            print(f"Error during upload: {e}")
            traceback.print_exc()
        finally:
            # Close all file handles
            for f in files.values():
                try:
                    f.close()
                except:
                    pass


async def _upload_and_index_frames_async(frame_paths: List[str], video_width: int, video_height: int, video_duration_ms: float,
                                         server_url: str,
                                         progress_callback: Optional[Callable[[dict], None]] = None,
                                         api_key: Optional[str] = None):
    items = []

    # Prepare files and timestamps
    files_to_upload = []
    timestamps = []

    for frame_path in frame_paths:
        filename = os.path.basename(frame_path)
        match = re.search(r'(\d+)ms', filename)
        timestamp_ms = int(match.group(1)) if match else 0
        files_to_upload.append((filename, frame_path))
        timestamps.append(timestamp_ms)

    # Sort by timestamp
    sorted_files_data = sorted(zip(files_to_upload, timestamps), key=lambda x: x[1])
    files_to_upload, timestamps = zip(*sorted_files_data)

    # Batch files - create balanced batches
    total_files = len(files_to_upload)
    batch_size = 50
    num_batches = (total_files + batch_size - 1) // batch_size  # Ceiling division
    
    # If we have more than one batch, balance them
    if num_batches > 1 and total_files % num_batches != 0:
        # Calculate a more balanced batch size
        balanced_batch_size = (total_files + num_batches - 1) // num_batches  # Ceiling division
        batches = [(files_to_upload[i:i + balanced_batch_size], timestamps[i:i + balanced_batch_size])
                   for i in range(0, len(files_to_upload), balanced_batch_size)]
    else:
        # Use fixed batch size if evenly divisible or only one batch
        batches = [(files_to_upload[i:i + batch_size], timestamps[i:i + batch_size])
                   for i in range(0, len(files_to_upload), batch_size)]

    print('Processing batches:', len(batches), 'Batch sizes:', [len(b[0]) for b in batches])

    base_data = {
        "video_width": str(video_width),
        "video_height": str(video_height),
        "video_duration_ms": str(video_duration_ms)
    }

    # Semaphore: allow only first batch to start
    image_description_semaphore = asyncio.Semaphore(1)

    async with aiohttp.ClientSession() as session:
        tasks = []
        for batch_files, batch_timestamps in batches:
            task = asyncio.create_task(_upload_batch(session, batch_files, batch_timestamps, base_data,
                                                     server_url, progress_callback, image_description_semaphore, items, api_key))
            tasks.append(task)

        await asyncio.gather(*tasks)

    return {"items": items}


def _upload_and_index_frames(frame_paths: List[str],
                             video_width: int,
                             video_height: int,
                             video_duration_ms: float,
                             server_url: str,
                             progress_callback: Optional[Callable[[dict], None]] = None,
                             api_key: Optional[str] = None) -> dict:
    """
    Synchronous wrapper for async upload/index.
    """
    return asyncio.run(_upload_and_index_frames_async(
        frame_paths,
        video_width,
        video_height,
        video_duration_ms,
        server_url,
        progress_callback,
        api_key
    ))
