import os
from video_processing import *
from config import INPUT_DIR, OUTPUT_DIR
import time

def main():
    video_paths = get_all_video_files(INPUT_DIR)
    print(f"Found {len(video_paths)} video files in {INPUT_DIR}.")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    clip_index = 0
    for i, video_path in enumerate(video_paths):
        try:
            print(f"[{i+1}/{len(video_paths)}] {video_path}")
            num_segments = process_video(video_path, clip_index)
            clip_index += 1
            print(f" -> Produced {num_segments} clips")
            print(f"Done with the clip name {video_path} and number {i}")
            sleep_duration = 0.5 * i  # because of slow internet (not exponential)
            #time.sleep(sleep_duration)
            if i == 20:
                break
        except:
            print(f"problem with the clip name {video_path} and number {i}")
            continue

    print("All videos processed successfully!")

if __name__ == "__main__":
    main()
