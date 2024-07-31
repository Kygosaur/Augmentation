import cv2
import os

def process_video(video_path, output_dir):
    """
    coding for proces single video file
    
    Parameters:
    - video_path: The path to the video file.
    - output_dir: The directory where the extracted frames will be saved.
    """
    
    Second=2
    specific_folder = "datasets"
    full_output_path = os.path.join(output_dir, specific_folder)

    # if dir x exist
    if not os.path.exists(full_output_path):
        os.makedirs(full_output_path)

    cap = cv2.VideoCapture(video_path)

    # Check video file open success
    if not cap.isOpened():
        print(f"Error opening video stream or file: {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count =   0

    # Calc extract interval 
    interval = int(fps * Second)

    # Loop each frame of vid
    print("now running")
    
    while True:
        ret, frame = cap.read()

        # Check frame read correct
        if not ret:
            print(f"Can't receive frame (stream end?). Exiting...")
            break

        # Extract frame use calc interval
        if frame_count % interval ==   0:
            # Construct the filename for the extracted frame
            frame_filename = os.path.join(full_output_path, f"{os.path.basename(video_path).split('.')[0]}_frame_{frame_count}.jpg")
            # Save the frame 
            cv2.imwrite(frame_filename, frame)

        frame_count +=   1

    cap.release()
    cv2.destroyAllWindows()

    print(f"Extracted {frame_count} frames from {video_path} to {full_output_path}")

def process_all_videos_in_folder(video_dir, output_dir):
    """
    Processes all video files in a specified directory
    
    Parameters:
    - video_dir: The directory containing the video files.
    - output_dir: The directory where the extracted frames will be saved.
    """
    for filename in os.listdir(video_dir):
        # Check if the file is a video file
        if filename.endswith(".mp4"): 
            video_path = os.path.join(video_dir, filename)
            process_video(video_path, output_dir)

def process_single_video(video_path, output_dir):
    """
    Processes a single video file
    
    Parameters:
    - video_path: The path to the video file.
    - output_dir: The directory where the extracted frames will be saved.
    """
    process_video(video_path, output_dir)

if __name__ == "__main__":
    output_dir = "frames"
    # Uncomment below to process all videos in the folder
    #video_dir = r"C:\Users\Kygo\Desktop\2 NOV"
    #process_all_videos_in_folder(video_dir, output_dir)
    
    # Uncomment below to process a single video
    video_path = r"c:\Users\Kygo\Desktop\20231102\W20 Topside Pre-Fabrication Area-1 20231102 1615-1620.mp4"
    output_dir = r"C:\Users\Kygo\Desktop\extracted_frames"  
    process_single_video(video_path, output_dir)
