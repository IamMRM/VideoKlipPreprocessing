# config.py
INPUT_DIR = "dataset_unprocessed"
OUTPUT_DIR = "dataset_cleaned"
SEGMENT_LENGTH = 10  # Duration of each clip in seconds
RESOLUTION = 256  # Desired resolution (width and height)
FRAMERATE = 30  # Desired frame rate
START_OFFSET = 40
END_OFFSET = 10
RESOLUTION_FILTER = (
    f"scale={RESOLUTION+50}:{RESOLUTION+50}:force_original_aspect_ratio=decrease,"
    f"pad={RESOLUTION+50}:{RESOLUTION+50}:-1:-1:color=black,"
    f"crop={RESOLUTION}:{RESOLUTION}" 
)
