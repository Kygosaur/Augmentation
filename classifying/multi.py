import cv2
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import time
import json
import os
import psutil
import contextlib
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO, # Set up logging
                    format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s',
                    filename='video_processing.log',
                    filemode='w')

logger = logging.getLogger(__name__)

try:
    import pynvml
    pynvml.nvmlInit()
    GPU_AVAILABLE = True
    logger.info("GPU support initialized successfully")
except ImportError:
    GPU_AVAILABLE = False
    logger.warning("GPU support not available")

class VideoPlayer:
    def __init__(self, video_path: str):
        self.video_path = video_path
        self.cap = None
        self.is_running = threading.Event()
        self.frame_queue = queue.Queue(maxsize=30)
        self.display_thread = None
        self.start_time = None
        self.end_time = None
        self.performance_lock = threading.Lock()
        self.cpu_usage: List[float] = []
        self.memory_usage: List[float] = []
        self.gpu_usage: List[float] = []
        self.frames_processed = 0
        self.io_counters_start = None
        self.io_counters_end = None
        self.logger = logging.getLogger(f"{__name__}.VideoPlayer")

    @contextlib.contextmanager
    def video_capture(self):
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            self.logger.error(f"Failed to open video: {self.video_path}")
            raise IOError(f"Could not open video file: {self.video_path}")
        self.logger.info(f"Opened video: {self.video_path}")
        try:
            yield self.cap
        finally:
            if self.cap:
                self.cap.release()
                self.logger.info(f"Closed video: {self.video_path}")

    def start(self):
        self.logger.info(f"Starting video player for {self.video_path}")
        self.is_running.set()
        try:
            with self.video_capture() as cap:
                self.display_thread = threading.Thread(target=self._display_frames)
                self.display_thread.start()
                self.start_time = time.time()
                self.io_counters_start = psutil.disk_io_counters()
                self._process_video(cap)
        except Exception as e:
            self.logger.error(f"Error in video player for {self.video_path}: {str(e)}", exc_info=True)
            raise

    def stop(self):
        self.logger.info(f"Stopping video player for {self.video_path}")
        self.is_running.clear()
        self.end_time = time.time()
        self.io_counters_end = psutil.disk_io_counters()
        if self.display_thread:
            self.display_thread.join()
        cv2.destroyWindow(f"Video: {self.video_path}")

    def _process_video(self, cap):
        while self.is_running.is_set():
            ret, frame = cap.read()
            if not ret:
                self.logger.info(f"Reached end of video: {self.video_path}")
                break
            try:
                self.frame_queue.put(frame, timeout=1)
                with self.performance_lock:
                    self._update_performance_metrics()
                    self.frames_processed += 1
            except queue.Full:
                self.logger.warning(f"Frame queue full for {self.video_path}")
                continue
            except Exception as e:
                self.logger.error(f"Error processing frame for {self.video_path}: {str(e)}", exc_info=True)

    def _display_frames(self):
        window_name = f"Video: {self.video_path}"
        while self.is_running.is_set():
            try:
                frame = self.frame_queue.get(timeout=1)
                cv2.imshow(window_name, frame)
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    self.logger.info(f"User requested stop for {self.video_path}")
                    self.is_running.clear()
                    break
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error displaying frame for {self.video_path}: {str(e)}", exc_info=True)

    def _update_performance_metrics(self):
        try:
            self.cpu_usage.append(psutil.cpu_percent(interval=None))
            self.memory_usage.append(psutil.virtual_memory().percent)
            if GPU_AVAILABLE:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                self.gpu_usage.append(utilization.gpu)
        except Exception as e:
            self.logger.error(f"Error updating performance metrics for {self.video_path}: {str(e)}", exc_info=True)

    def get_performance_data(self) -> Dict[str, Any]:
        with self.performance_lock:
            processing_time = self.end_time - self.start_time
            io_read = self.io_counters_end.read_bytes - self.io_counters_start.read_bytes
            io_write = self.io_counters_end.write_bytes - self.io_counters_start.write_bytes
            return {
                "video_path": self.video_path,
                "processing_time": processing_time,
                "avg_cpu_usage": sum(self.cpu_usage) / len(self.cpu_usage) if self.cpu_usage else 0,
                "max_cpu_usage": max(self.cpu_usage) if self.cpu_usage else 0,
                "avg_memory_usage": sum(self.memory_usage) / len(self.memory_usage) if self.memory_usage else 0,
                "max_memory_usage": max(self.memory_usage) if self.memory_usage else 0,
                "avg_gpu_usage": sum(self.gpu_usage) / len(self.gpu_usage) if self.gpu_usage else 0,
                "max_gpu_usage": max(self.gpu_usage) if self.gpu_usage else 0,
                "frames_processed": self.frames_processed,
                "fps": self.frames_processed / processing_time if processing_time > 0 else 0,
                "io_read_mb": io_read / (1024 * 1024),
                "io_write_mb": io_write / (1024 * 1024)
            }

class VideoManager:
    def __init__(self, max_threads: int = 3):
        self.players: List[VideoPlayer] = []
        self.executor = ThreadPoolExecutor(max_workers=max_threads)
        self.futures = []
        self.start_time = None
        self.end_time = None
        self.shutdown_event = threading.Event()
        self.logger = logging.getLogger(f"{__name__}.VideoManager")

    def add_video(self, video_path: str):
        player = VideoPlayer(video_path)
        self.players.append(player)
        self.logger.info(f"Added video: {video_path}")

    def start_all(self):
        self.start_time = time.time()
        for player in self.players:
            future = self.executor.submit(player.start)
            self.futures.append(future)
        self.logger.info(f"Started processing {len(self.players)} videos")

    def stop_all(self):
        self.shutdown_event.set()
        for player in self.players:
            player.stop()
        self.executor.shutdown(wait=True)
        self.end_time = time.time()
        self.logger.info("Stopped all video players")

    def wait_for_completion(self):
        try:
            for i, future in enumerate(as_completed(self.futures)):
                try:
                    future.result()  # This will raise any exceptions that occurred in the thread
                    self.logger.info(f"Thread {i+1} completed successfully")
                except Exception as e:
                    self.logger.error(f"Error in thread {i+1}: {str(e)}", exc_info=True)
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {str(e)}", exc_info=True)
        finally:
            self.stop_all()

    def get_performance_data(self) -> Dict[str, Any]:
        # ... (same as before)
        self.logger.info("Collected performance data")
        return performance_data

def save_performance_data(data: Dict[str, Any]):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    json_path = os.path.join(parent_dir, "performance.json")
    
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=4)
    logger.info(f"Performance data saved to {json_path}")

if __name__ == "__main__":
    logger.info("Starting video processing application")
    manager = VideoManager(max_threads=10)  # Set to desired number of threads

    # Add your video paths here
    video_paths = [
        r"d:\W20 Topside Pre-Fabrication Area-1 20231102 1500-1505.mp4",
        r"d:\W20 Topside Pre-Fabrication Area-1 20231102 1532-1537.mp4",
        r"d:\W20 Topside Pre-Fabrication Area-1 20231102 1615-1620.mp4",
        # Add more video paths as needed here but change thread first 
    ]
    
    manager = VideoManager(max_threads=len(video_paths))
    
    for path in video_paths:
        manager.add_video(path)

    manager.start_all()

    try:
        manager.wait_for_completion()
    except KeyboardInterrupt:
        logger.warning("Keyboard interrupt received. Stopping all videos...")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}", exc_info=True)
    finally:
        manager.stop_all()
        performance_data = manager.get_performance_data()
        save_performance_data(performance_data)

    logger.info("All videos stopped and performance data saved.")