# config.py
INPUT_DIR = "dataset_unprocessed"#"/media/roscha/T7 Shield/Datasets/blabla"
OUTPUT_TEMP_DIR = "dataset_cleaned_1"
OUTPUT_DIR = "dataset_cleaned"
SEGMENT_LENGTH = 20  # Duration of each clip in seconds
RESOLUTION = 256  # Desired resolution (width and height)
FRAMERATE = 30  # Desired frame rate
START_OFFSET = 40
END_OFFSET = 5
RESOLUTION_FILTER = (
    f"scale={RESOLUTION}:{RESOLUTION}:force_original_aspect_ratio=decrease,"
    f"pad={RESOLUTION}:{RESOLUTION}:-1:-1:color=black,"
    f"crop={RESOLUTION}:{RESOLUTION}" 
)
