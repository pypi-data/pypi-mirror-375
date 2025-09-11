import cv2
import numpy as np

import einops
import wxw.common as cm


class CameraBlockDetector:

    def __init__(self):
        self.blockCounter = 0
        self.grid_mean_threshold = 5.0
        self.rows = 4

    def processFrame(self, frame):
        frame_resized = cm.size_pre_process(frame, height=640, align=640)
        height, width = frame_resized.shape[:2]
        gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        edge = cv2.Canny(gray, 0, 30)
        edge = cv2.morphologyEx(edge, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8), iterations=2)

        rows, columns = self.rows, int(self.rows / height * width)
        edge_grid = einops.rearrange(edge, "(r h) (c w) -> r c h w", r=rows, c=columns)
        grid_mean = np.mean(edge_grid, axis=(2, 3))
        grid_binary = np.where(grid_mean > self.grid_mean_threshold, 1, 0)
        # cv2.imshow("grid_binary", grid_binary.astype(np.float32))

        left_sum = np.sum(grid_binary[:, : columns // 2])
        right_sum = np.sum(grid_binary[:, columns // 2:])
        center_sum = np.sum(grid_binary[1:-1, 3:-3])
        is_blocked = False
        if left_sum == 0 or right_sum == 0 or center_sum < 3:
            is_blocked = True
        if is_blocked and center_sum > 40:
            print(center_sum)
            is_blocked = False
        if not is_blocked:
            # 连通区域
            grid_binary = 255 - (grid_binary * 255).astype(np.uint8)
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(grid_binary, connectivity=4)
            max_idx = np.argmax(stats[:, 4])
            x1, y1, w, h, area = stats[max_idx]
            in_percentage = area / w / h
            ex_percentage = area / height / width
            if ex_percentage > 0.3 and in_percentage > 0.5:
                print("Recall one!")
                is_blocked = True

        self.blockCounter = self.blockCounter + 1 if is_blocked else -1
        self.blockCounter = np.clip(self.blockCounter, 0, 10)

    def isBlocked(self):
        return self.blockCounter >= 5

    def draw(self, frame):
        h, w = frame.shape[:2]
        color = (0, 0, 222) if self.isBlocked() else (0, 222, 0)
        cv2.rectangle(frame, (0, 0), (w, h), color, 20)
        # string = f"{self.blockCounter}   "
        # string += "blocked" if self.isBlocked() else "well"
        # frame = cm.put_text(frame, string)
        return frame


if __name__ == '__main__':
    cbd = CameraBlockDetector()
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    if not cap.isOpened(): print("no camera")
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        frame = np.ascontiguousarray(frame[:, ::-1, :])
        cbd.processFrame(frame)
        frame = cbd.draw(frame)
        cv2.imshow("frame", frame)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
    cap.release()
