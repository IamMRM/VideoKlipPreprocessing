import os
import h5py
import cv2
import numpy as np

def store_video_in_hdf5(video_path, h5_path):
    """
    Read frames from 'video_path', normalize to [0,1], and store
    them in an HDF5 dataset for efficient sequential access later.
    """
    cap = cv2.VideoCapture(video_path)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Convert BGR (OpenCV) to RGB, then to float [0,1]
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_norm = frame_rgb.astype(np.float32) / 255.0
        frames.append(frame_norm)
    cap.release()

    # Create HDF5 file
    with h5py.File(h5_path, "w") as f:
        # Store frames in a dataset of shape (num_frames, H, W, 3)
        f.create_dataset("video", data=np.array(frames), compression="gzip")

# Example usage for all .mp4 clips in OUTPUT_DIR:
if __name__ == "__main__":
    for file in os.listdir(OUTPUT_DIR):
        if file.endswith(".mp4"):
            input_path = os.path.join(OUTPUT_DIR, file)
            h5_output = os.path.join(OUTPUT_DIR, file.replace(".mp4", ".h5"))
            store_video_in_hdf5(input_path, h5_output)
