import cv2
from windowcapture import WindowCapture
from vision import Vision
import threading
import psutil
import os
from concurrent.futures import ThreadPoolExecutor
import time

class RectangleDrawer(threading.Thread):
    def __init__(self, overlay, points, needle_w, needle_h, fps_display):
        super().__init__()
        self.overlay = overlay
        self.points = points
        self.needle_w = needle_w
        self.needle_h = needle_h
        self.fps_display = fps_display

    def run(self):
        start_time = time.time()
        for point in self.points:
            cv2.rectangle(self.overlay, (point[0] - self.needle_w//2, point[1] - self.needle_h//2), 
                          (point[0] + self.needle_w//2, point[1] + self.needle_h//2), 
                          (0, 255, 0), 2)
        end_time = time.time()
        elapsed_time = end_time - start_time
        if elapsed_time != 0:
            fps = 1 / elapsed_time
            self.fps_display[0] = fps

if __name__ == "__main__":
    window_name = "Minecraft* 1.19.2 - Singleplayer"
    capture = WindowCapture(window_name)

    needle_image_path = 'test.jpg'
    confidence_threshold = 0.5
    vision = Vision(needle_image_path)

    # Define the number of threads
    num_threads = 1
    cpu_limit = 50
    pid = os.getpid()
    process = psutil.Process(pid)

    # Set CPU affinity to limit the process to specific CPU cores
    cpu_count = psutil.cpu_count(logical=False)
    process.cpu_affinity(list(range(cpu_count)))

    # Set CPU priority to "below normal" to reduce CPU usage
    process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)

    fps_display = [0]

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        last_time = time.time()
        while True:
            # Get the CPU usage
            cpu_percent = process.cpu_percent()
            frame = capture.capture_frame()
            if frame is not None:
                points = vision.find(frame, threshold=confidence_threshold)
                overlay = frame.copy()

                # Submit tasks to the thread pool
                tasks = [executor.submit(RectangleDrawer(overlay, points, vision.needle_w, vision.needle_h, fps_display).run) for _ in range(num_threads)]
                for task in tasks:
                    task.result()

                # Calculate average draw FPS
                avg_draw_fps = sum(fps_display) / len(fps_display)

                # Draw draw FPS on top right corner
                cv2.putText(overlay, f"Draw FPS: {avg_draw_fps:.2f}", (5, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

                # Capture FPS on top left corner
                cv2.putText(overlay, f"Capture FPS: {capture.capture_fps:.2f}", (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

                # Write Cathie02 in top right corner
                cv2.putText(overlay, "Cathie02", (overlay.shape[1] - 75, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

                # Limit the frame rate
                current_time = time.time()
                elapsed_time = current_time - last_time
                if elapsed_time >= 0.033:  # Adjust this value for desired frame rate higher value = lower frame rate
                    cv2.imshow(window_name, overlay)
                    last_time = current_time

            # TODO : test
            if cpu_percent > cpu_limit:
                time.sleep(0.01)

            key = cv2.waitKey(1)
            if key == 27:
                break

    cv2.destroyAllWindows()

    output_filename = "record.avi"
    capture.record_video(output_filename, fps=60, duration=10)
