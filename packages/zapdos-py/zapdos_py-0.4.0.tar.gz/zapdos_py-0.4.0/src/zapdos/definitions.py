"""
Definitions for the zapdos SDK.
"""

# Event types for video indexing
class IndexEvents:
    INSERTED_VIDEO_FILE_RECORD = "inserted-video-file-record"
    UPLOADED_FRAME = "uploaded"
    INSERTED_FRAMES_RECORDS = "inserted-frames-records"
    CREATED_IMAGE_DESCRIPTION_JOB = "created-image-description-job"
    COMPLETED_IMAGE_DESCRIPTION_JOB = "completed-image-description-job"
    CREATED_OBJECT_DETECTION_JOB = "created-object-detection-job"
    COMPLETED_OBJECT_DETECTION_JOB = "completed-object-detection-job"
    CREATED_SUMMARY_JOB = "created-summary-job"
    COMPLETED_SUMMARY_JOB = "completed-summary-job"
    CREATED_EMBEDDING_JOB = "created-embedding-job"
    COMPLETED_EMBEDDING_JOB = "completed-embedding-job"
    DONE_INDEXING = "done-indexing"
    ERROR_INDEXING = "error-indexing"