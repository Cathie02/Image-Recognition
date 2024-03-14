import cv2 as cv
import numpy as np

class Vision:
    def __init__(self, needle_img_path, method=cv.TM_CCOEFF_NORMED):
        self.needle_img = cv.imread(needle_img_path, cv.IMREAD_UNCHANGED)
        self.needle_img = cv.resize(self.needle_img, (0, 0), fx=0.5, fy=0.5)
        self.method = method
        self.needle_h, self.needle_w = self.needle_img.shape[:2]

    def find(self, haystack_img, threshold=0.5, debug_mode=None):
        result = cv.matchTemplate(haystack_img, self.needle_img, self.method)
        locations = np.where(result >= threshold)
        locations = list(zip(*locations[::-1]))
        rectangles = np.array([[x, y, self.needle_w, self.needle_h] for x, y in locations])
        rectangles, weights = cv.groupRectangles(rectangles.tolist(), groupThreshold=1, eps=0.5)

        points = []
        if len(rectangles):
            line_color = (0, 255, 0)
            line_type = cv.LINE_4
            marker_color = (255, 0, 255)
            marker_type = cv.MARKER_CROSS

            for (x, y, w, h) in rectangles:
                center_x = x + w // 2
                center_y = y + h // 2
                points.append((center_x, center_y))

                if debug_mode == 'rectangles':
                    top_left = (x, y)
                    bottom_right = (x + w, y + h)
                    cv.rectangle(haystack_img, top_left, bottom_right, color=line_color, lineType=line_type, thickness=2)
                elif debug_mode == 'points':
                    cv.drawMarker(haystack_img, (center_x, center_y), color=marker_color, markerType=marker_type, markerSize=40, thickness=2)

        if debug_mode:
            cv.imshow('Matches', haystack_img)
        return points
