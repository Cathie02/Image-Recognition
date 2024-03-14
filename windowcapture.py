import cv2
import numpy as np
import win32gui
import win32api
import win32ui
import win32con
import threading
import time

class WindowCapture:
    def __init__(self, window_name, scale_factor=0.5):
        self.window_name = window_name
        self.hwnd = win32gui.FindWindow(None, window_name)
        self.lock = threading.Lock()
        self.frame = None
        self.number_of_threads = 1
        self.scale_factor = scale_factor

        # Capture FPS variables
        self.capture_start_time = time.time()
        self.capture_frame_count = 0
        self.capture_fps = 0

        # Start threads to continuously capture frames and calculate FPS
        self.capture_thread = threading.Thread(target=self._capture_frames)
        self.fps_thread = threading.Thread(target=self._calculate_fps)
        self.capture_thread.daemon = True
        self.fps_thread.daemon = True
        self.capture_thread.start()
        self.fps_thread.start()

    def _capture_frames(self):
        while True:
            screenshot = self._capture_window()
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            frame = cv2.resize(frame, (0, 0), fx=self.scale_factor, fy=self.scale_factor)
            
            with self.lock:
                self.frame = frame
                self.capture_frame_count += 1 

    def _capture_window(self):
        hwnd = self.hwnd
        
        # Get client area dimensions (excluding the title bar)
        left, top, right, bot = win32gui.GetClientRect(hwnd)
        title_bar_height = win32api.GetSystemMetrics(win32con.SM_CYCAPTION) + 10
        border_width = win32api.GetSystemMetrics(win32con.SM_CXSIZEFRAME) + 10
        left, top, right, bot = win32gui.GetClientRect(hwnd)
        width = right - left - 2 * border_width
        height = bot - top - title_bar_height - border_width + 45

        # Adjust capture region to exclude the title bar and borders
        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()

        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)

        saveDC.SelectObject(saveBitMap)
        saveDC.BitBlt((0, 0), (width, height), mfcDC, (border_width, title_bar_height), win32con.SRCCOPY)
        
        bmpstr = saveBitMap.GetBitmapBits(True)

        image = np.frombuffer(bmpstr, dtype='uint8')
        image.shape = (height, width, 4)

        mfcDC.DeleteDC()
        saveDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)
        win32gui.DeleteObject(saveBitMap.GetHandle())

        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert from BGR to RGB

    def capture_frame(self):
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

    def _calculate_fps(self):
        while True:
            time.sleep(2)
            current_time = time.time()
            elapsed_time = current_time - self.capture_start_time
            self.capture_fps = self.capture_frame_count / elapsed_time if elapsed_time > 0 else 0
            # print(f"Capture FPS: {self.capture_fps:.2f}")
            self.capture_start_time = current_time
            self.capture_frame_count = 0

    def record_video(self, output_filename, fps=60, duration=10):
        frame_size = (self.frame.shape[1], self.frame.shape[0])
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_filename, fourcc, fps, frame_size)
        
        start_time = cv2.getTickCount()
        while (cv2.getTickCount() - start_time) / cv2.getTickFrequency() < duration:
            frame = self.capture_frame()
            if frame is not None:
                out.write(frame)

        out.release()
