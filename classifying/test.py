import cv2
import psutil
import GPUtil
import time
import csv
from datetime import datetime

# Replace these paths with the paths to your video files
video_paths = [
    'd:\\W20 Topside Pre-Fabrication Area-1 20231102 1500-1505.mp4',
    'd:\W20 Topside Pre-Fabrication Area-1 20231102 1532-1537.mp4',
    'd:\W20 Topside Pre-Fabrication Area-1 20231102 1615-1620.mp4'
]

# Initialize video captures
caps = [cv2.VideoCapture(video_path) for video_path in video_paths]

# Check if all videos opened successfully
for i, cap in enumerate(caps):
    if not cap.isOpened():
        print(f"Error: Could not open video {i + 1}.")
        exit()

# Path to save the system resource usage data
data_path = 'C:\\Users\\jack\\Desktop\\Coding\\augmentation\\classifying\\resource_usage.csv'

# Create CSV file and write the header
with open(data_path, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Timestamp', 'CPU_Usage', 'RAM_Usage', 'GPU_Usage'])

while True:
    frames = []
    for cap in caps:
        ret, frame = cap.read()
        if not ret:
            # If any video reaches the end, break the loop
            break
        frames.append(frame)
    
    if len(frames) != len(caps):
        break

    for i, frame in enumerate(frames):
        cv2.imshow(f'Video {i + 1}', frame)

    # Collect system resource usage data
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    gpus = GPUtil.getGPUs()
    gpu_usage = gpus[0].load * 100 if gpus else 0

    # Save the data to the CSV file
    with open(data_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), cpu_usage, ram_usage, gpu_usage])

    # Exit if 'q' is pressed
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

# Release the video capture objects and close all OpenCV windows
for cap in caps:
    cap.release()
cv2.destroyAllWindows()
