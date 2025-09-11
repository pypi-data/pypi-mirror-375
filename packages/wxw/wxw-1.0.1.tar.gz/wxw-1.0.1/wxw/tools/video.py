import os
import sys

import cv2

# opencv和qt可能会冲突
# try:
#     os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH")
# except:
#     pass
import numpy as np
from PyQt5.QtWidgets import QFileDialog, QApplication

import wxw.common as cm
from baseTool import BaseTool
from CameraBlock import CameraBlockDetector
from onnx_inference import FaceDet, MarkLoc, FaceLandMark


class CollectionTool(BaseTool):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 相机遮挡
        self.camera_blocked_detectors = []

        # onnx推理
        self.face_det_model = None  # FaceDet()
        self.mark_loc_model = None  # MarkLoc("")
        self.face_landmark_model = None  # FaceLandMark("")

        # 绑定按键
        self.ui.use_face_det_model.stateChanged.connect(self.select_face_det_model_folder)
        self.ui.use_mark_loc_model.stateChanged.connect(self.select_mark_loc_model_folder)
        self.ui.use_face_landmark_model.stateChanged.connect(self.select_face_landmark_model_folder)

    def use_model(self, data):
        if not self.camera_blocked_detectors:
            for _ in range(self.cameras_num):
                self.camera_blocked_detectors.append(CameraBlockDetector())
        [fsg, sub_fsg, idx] = data
        model = self.camera_blocked_detectors[idx]
        model.processFrame(fsg)
        sub_fsg = model.draw(sub_fsg)
        return fsg, sub_fsg

    def select_face_det_model_folder(self):
        if not self.ui.use_face_det_model.isChecked():
            self.face_det_model = None
            return
        if self.face_det_model:
            return
        self.face_det_model = FaceDet()

    def select_face_landmark_model_folder(self):
        if not self.ui.use_face_landmark_model.isChecked():
            self.face_landmark_model = None
            return
        self.ui.use_face_landmark_model.setChecked(True)
        if self.face_landmark_model:
            return
        folder = QFileDialog.getExistingDirectory()
        self.face_landmark_model = FaceLandMark(folder)

    def select_mark_loc_model_folder(self):
        if not self.ui.use_mark_loc_model.isChecked():
            self.mark_loc_model = None
            return
        self.ui.use_mark_loc_model.setChecked(True)
        if self.mark_loc_model is not None:
            return
        folder = QFileDialog.getExistingDirectory()
        self.mark_loc_model = MarkLoc(folder)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = CollectionTool('window.ui')
    w.ui.show()
    sys.exit(app.exec_())
