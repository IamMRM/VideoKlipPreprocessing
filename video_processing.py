import os
import subprocess
import cv2
import tensorflow as tf

from config import SEGMENT_LENGTH, START_OFFSET, END_OFFSET, RESOLUTION_FILTER, OUTPUT_DIR, OUTPUT_TEMP_DIR

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

def convert_mp4_segment_to_tfrecord(mp4_path, tfrecord_path):
    """
    Convert a given MP4 segment into a TFRecord where each frame is
    stored as a JPEG-encoded byte string in one tf.train.Example.
    """
    cap = cv2.VideoCapture(mp4_path)
    if not cap.isOpened():
        print(f"Failed to open {mp4_path}")
        return 0

    frame_count = 0
    with tf.io.TFRecordWriter(tfrecord_path) as writer:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Encode frame to JPEG in memory
            success, encoded_image = cv2.imencode(".jpg", frame)
            if not success:
                continue

            # Build a simple Example with one 'frame' feature
            example = tf.train.Example(
                features=tf.train.Features(
                    feature={
                        "frame": tf.train.Feature(
                            bytes_list=tf.train.BytesList(value=[encoded_image.tobytes()])
                        )
                    }
                )
            )
            writer.write(example.SerializeToString())
            frame_count += 1

    cap.release()
    return frame_count

def process_video(video_path, clip_index):
    """
    1) Determine usable portion: skip first 10s & last 10s.
    2) Split into 5s segments.
    3) Scale to 512x512 with black bars (no cropping).
    4) Save each output segment as .mp4 in OUTPUT_TEMP_DIR.
    5) Convert each output mp4 segment to a TFRecord in OUTPUT_DIR.
    6) Delete the temporary .mp4 file from OUTPUT_TEMP_DIR.
    """
    duration = get_video_duration(video_path)
    if duration <= (START_OFFSET + END_OFFSET):
        print(f"Skipping {video_path} (too short after offsets).")
        return 0

    usable_duration = duration - (START_OFFSET + END_OFFSET)
    print(f"Processing {video_path} -> usable {usable_duration:.1f}s")

    # Make sure OUTPUT_TEMP_DIR exists
    if not os.path.exists(OUTPUT_TEMP_DIR):
        os.makedirs(OUTPUT_TEMP_DIR, exist_ok=True)

    segment_count = 0
    start = 0
    while start < usable_duration:
        # Determine how long this segment should be
        clip_duration = min(SEGMENT_LENGTH, usable_duration - start)
        if clip_duration <= 0:
            break

        # Output filename for the MP4 segment
        out_name = f"clip{clip_index}_segment{segment_count}.mp4"

        # Path in the temporary directory
        tmp_out_path = os.path.join(OUTPUT_TEMP_DIR, out_name)

        # Actual start time in the original video
        video_start_time = START_OFFSET + start

        # ffmpeg command to generate the mp4 segment in OUTPUT_TEMP_DIR
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
            tmp_out_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Convert the temporary MP4 segment to TFRecord in OUTPUT_DIR
        tfrecord_name = out_name.replace(".mp4", ".tfrecord")
        tfrecord_path = os.path.join(OUTPUT_DIR, tfrecord_name)
        frame_count = convert_mp4_segment_to_tfrecord(tmp_out_path, tfrecord_path)
        #print(f"Converted {tmp_out_path} -> {tfrecord_path} [{frame_count} frames]")

        # Delete the temporary MP4 file
        if os.path.exists(tmp_out_path):
            os.remove(tmp_out_path)
            #print(f"Deleted temp file: {tmp_out_path}")

        segment_count += 1
        start += SEGMENT_LENGTH

    return segment_count
