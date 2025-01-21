import os
import subprocess
from config import SEGMENT_LENGTH, START_OFFSET, END_OFFSET, RESOLUTION_FILTER, OUTPUT_DIR

def get_all_video_files(root_dir):
    """
    Recursively collect all video file paths from root_dir.
    """
    valid_extensions = (".mp4", ".mov", ".avi", ".mkv", ".webm")
    video_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(valid_extensions):
                video_files.append(os.path.join(root, file))
    return video_files

def get_video_duration(video_path):
    """
    Use ffprobe to get the duration of a video in seconds.
    Returns float or 0 if something fails.
    """
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        return float(output.strip())
    except:
        return 0.0

def process_video(video_path, clip_index):
    """
    1) Determine usable portion: skip first 10s & last 10s.
    2) Split into 5s segments.
    3) Scale to 512x512 with black bars (no cropping).
    4) Name output as clip{clip_index}_segment{segment_num}.mp4
    """
    duration = get_video_duration(video_path)
    if duration <= (START_OFFSET + END_OFFSET):
        print(f"Skipping {video_path} (too short after offsets).")
        return 0

    usable_duration = duration - (START_OFFSET + END_OFFSET)
    print(f"Processing {video_path} -> usable {usable_duration:.1f}s")

    segment_count = 0
    start = 0
    while start < usable_duration:
        # Determine how long this segment should be
        clip_duration = min(SEGMENT_LENGTH, usable_duration - start)
        if clip_duration <= 0:
            break

        # Output filename
        out_name = f"clip{clip_index}_segment{segment_count}.mp4"
        out_path = os.path.join(OUTPUT_DIR, out_name)

        # Actual start time in the original video
        video_start_time = START_OFFSET + start

        # ffmpeg command:
        # -ss: start time, -t: clip duration
        # -vf: video filter (scaling + padding)
        # -c:v libx264: re-encode to H.264
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(video_start_time),
            "-i", video_path,
            "-t", str(clip_duration),
            "-vf", RESOLUTION_FILTER,
            "-c:v", "libx264",
            "-crf", "23",
            "-preset", "fast",
            "-c:a", "aac",  # If there's audio track
            "-pix_fmt", "yuv420p",
            out_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        segment_count += 1
        start += SEGMENT_LENGTH

    return segment_count
