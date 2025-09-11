import os
import sys
import time
from datetime import datetime

import cv2

try:
    os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH")
except:
    pass
import imageio
import numpy as np
from PIL import Image
from PyQt5 import uic
import wxw.common as cm
from PyQt5 import QtCore
from PyQt5.QtGui import QImage, QPixmap, QDesktopServices
from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox
from wxw.qt_utils import pop_info_box
from copy import deepcopy


class BaseCameras(QtCore.QThread):
    # 定义两个信号，用于在读取到新的帧时发送给其他对象
    show_signal = QtCore.pyqtSignal(list)
    save_signal = QtCore.pyqtSignal(list)

    def __init__(self, num_cameras=8):
        super().__init__()
        self.num_cameras = num_cameras
        self.cameras = []
        self.opened = False

    def release(self):
        """
        关闭所有摄像头
        """
        self.opened = False
        for cap in self.cameras:
            cap.release()

    def open_all_cameras(self):
        """
        打开所有摄像头
        """
        print("[info] Turning on the camera.")
        for i in range(self.num_cameras):
            cap = cv2.VideoCapture(i)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            if cap.isOpened():
                self.cameras.append(cap)
        self.opened = len(self.cameras) > 0
        print(f'[info] 共打开{len(self.cameras)}个相机!')

    def run(self):
        """
        在新的线程中运行，打开所有摄像头并读取帧
        """
        self.open_all_cameras()
        while self.opened:
            show_frames = []
            save_frames = []
            for vi, camera in enumerate(self.cameras):
                ret, frame = camera.read()
                if ret:  # 摄像头获取到图片
                    save_frames.append(frame)
                    show_frames.append(frame)

            # 发送信号，带有新的帧列表
            self.show_signal.emit(show_frames)
            self.save_signal.emit(show_frames)


def set_image_on_label(ui_view, image):
    fsg_show = cm.size_pre_process(image, height=ui_view.height(), align=1)
    fsg_show = cv2.cvtColor(fsg_show, cv2.COLOR_BGR2RGB)
    height, width, channel = fsg_show.shape
    fsg_show = np.ascontiguousarray(fsg_show)
    bytees_per_line = channel * width
    qimg = QImage(fsg_show.data, width, height, bytees_per_line, QImage.Format_RGB888)
    pixmap = QPixmap.fromImage(qimg)
    ui_view.setPixmap(pixmap)


class BaseTool(QWidget):
    def __init__(
            self,
            ui_path,
            windows_number_per_page=4,
            CamerasFunction=BaseCameras,
    ):
        super().__init__()
        # 加载由Qt Designer设计的ui文件
        self.ui = uic.loadUi(ui_path)

        # ======== camera ========
        self.CamerasFunction = CamerasFunction
        self.camera_stream = None
        self.cameras_num = 0
        self.camera_blocked_detectors = []

        # ========= view =========
        self.current_page = 0
        self.windows_number_per_page = windows_number_per_page
        self.sliders = None
        self.page_info = {}
        self.save_views_state = []

        # ========= path ========
        self.save_path = None

        # status
        self.used_box = 0
        self.video_writers = []
        self.is_saving_video = False

        # =========== shoot ===========
        self.shoot_num, self.saved_shoot_paths = 0, []
        self.video_num, self.saved_video_paths = 0, []

        # ============ init =============
        self.init_button()
        self.bind_button_function()

    def init_button(self):
        """
        初始化按钮状态
        打开show_button按钮,禁用其他按钮
        """
        for button in ['show_button']:
            getattr(self.ui, f"{button}").setEnabled(True)

        for button in [
            "save_button", "change_folder_button",
            "open_folder_button", "reset_button",
            "start_button", "stop_button", "delete_prev_video",
            "shoot_button", "delete_prev_shoot",
            "next_page_button", "prev_page_button",
            'scan_button',
        ]:
            getattr(self.ui, f"{button}").setEnabled(False)

        # 把日期设置为当前日期
        self.ui.date.setText(datetime.now().strftime("%Y%m%d"))

    def bind_button_function(self):
        """
        设置按钮的功能
        """
        self.ui.show_button.clicked.connect(self.open_camera)
        self.ui.reset_button.clicked.connect(self.reset_cameras)
        self.ui.exit_button.clicked.connect(self.quit_software)

        self.ui.save_button.clicked.connect(self.select_save_folder)
        self.ui.open_folder_button.clicked.connect(self.open_save_folder)
        self.ui.change_folder_button.clicked.connect(self.change_folder)

        self.ui.scan_button.clicked.connect(self.scan_view)

        self.ui.shoot_button.clicked.connect(self.get_shoot_signal)

        self.ui.start_button.clicked.connect(self.get_video_signal)

        self.ui.stop_button.clicked.connect(self.get_stop_recording_signal)

        self.sliders = []
        for i in range(self.windows_number_per_page):
            idx = i + 1
            left_bar = getattr(self.ui, f"s_left_{idx}")
            right_bar = getattr(self.ui, f"s_right_{idx}")
            top_bar = getattr(self.ui, f"s_top_{idx}")
            bottom_bar = getattr(self.ui, f"s_bottom_{idx}")
            self.sliders.append([left_bar, right_bar])
            self.sliders.append([top_bar, bottom_bar])

        for slider_a, slider_b in self.sliders:
            slider_a.valueChanged.connect(self.update_sliders)
            slider_b.valueChanged.connect(self.update_sliders)

        self.ui.next_page_button.clicked.connect(self.next_page)

        self.ui.prev_page_button.clicked.connect(self.prev_page)

        self.ui.delete_prev_shoot.clicked.connect(self.delete_shoot_files)
        self.ui.delete_prev_video.clicked.connect(self.delete_videos)

    def open_camera(self):
        """
        打开摄像头
        """
        try:
            self.camera_stream = self.CamerasFunction()
            self.camera_stream.show_signal.connect(self.show_image)
            self.camera_stream.start()
            self.ui.show_button.setEnabled(False)
            for button in [
                "save_button", "reset_button", "next_page_button"
            ]:
                getattr(self.ui, f"{button}").setEnabled(True)
        except:
            self.camera_stream = None
            pop_info_box("打开相机失败！", "Error!")
            self.reset_cameras()

    def quit_software(self):
        self.reset_cameras()
        exit()

    def reset_cameras(self):
        """重置软件"""
        self.init_button()
        self.ui.show_button.setText("显示")
        if self.camera_stream:
            self.camera_stream.show_signal.disconnect(self.show_image)
            self.init_views()
            self.camera_stream.release()
            del self.camera_stream
            self.camera_stream = None

    def select_save_folder(self):
        """获取保存路径位置"""
        self.save_path = QFileDialog.getExistingDirectory()
        self.ui.scan_button.setEnabled(True)
        self.ui.open_folder_button.setEnabled(True)
        self.ui.change_folder_button.setEnabled(True)

    def update_sliders(self):
        for slider_a, slider_b in self.sliders:
            if slider_a.value() >= slider_b.value() - 10:
                slider_a.setValue(slider_b.value() - 10)

    def next_page(self):
        self.ui.prev_page_button.setEnabled(True)
        self.page_info[self.current_page] = self.get_views()
        self.init_views()
        self.current_page = self.current_page + 1
        self.ui.page.setText(str(self.current_page))
        if self.current_page in self.page_info:
            self.restore_views(self.page_info[self.current_page])

    def prev_page(self):
        self.page_info[self.current_page] = self.get_views()
        self.init_views()
        self.current_page = max(self.current_page - 1, 0)
        self.ui.page.setText(str(self.current_page))
        self.restore_views(self.page_info[self.current_page])
        if self.current_page == 0:
            self.ui.prev_page_button.setEnabled(False)

    def init_views(self):
        for i in range(self.windows_number_per_page):
            idx = i + 1
            getattr(self.ui, f"view_{idx}").clear()
            getattr(self.ui, f"state_{idx}").clear()
            getattr(self.ui, f"selected_{idx}").setChecked(False)
            getattr(self.ui, f"save_bin_{idx}").setChecked(False)
            getattr(self.ui, f"use_model_{idx}").setChecked(False)

    def get_views(self):
        states = {}
        for i in range(self.windows_number_per_page):
            idx = i + 1
            states[i] = {
                "location": getattr(self.ui, f"location_{idx}").text(),
                "type": getattr(self.ui, f"type_{idx}").currentText(),
                "selected": getattr(self.ui, f"selected_{idx}").isChecked(),
                "save_bin": getattr(self.ui, f"save_bin_{idx}").isChecked(),
                "use_model": getattr(self.ui, f"use_model_{idx}").isChecked(),
            }
        return states

    def restore_views(self, info):
        for i in range(self.windows_number_per_page):
            idx = i + 1
            getattr(self.ui, f"location_{idx}").setText(info[i]["location"])
            getattr(self.ui, f"type_{idx}").setCurrentText(info[i]['type'])
            getattr(self.ui, f"selected_{idx}").setChecked(info[i]['selected'])
            getattr(self.ui, f"save_bin_{idx}").setChecked(info[i]['save_bin'])
            getattr(self.ui, f"use_model_{idx}").setChecked(info[i]['use_model'])

    def scan_view(self):
        try:
            assert self.ui.plate.text
            assert self.ui.name.text
            assert self.ui.car_type.currentText() != "CarType"
            assert self.ui.brightness.currentText() != "Brightness"
            assert self.ui.weather.currentText() != "Weather"
        except:
            pop_info_box(
                f"Please set [Plate, Name, CarType, Brightness and Weather]",
                'ERROR'
            )
            return
        # 把当前页设置更新到记录中
        self.page_info[self.current_page] = self.get_views()
        self.save_views_state = []
        print(self.page_info)
        for page_idx, page in self.page_info.items():
            idx = page_idx * self.windows_number_per_page
            for view_idx, view in page.items():
                selected = view['selected']
                if selected and idx + view_idx < self.cameras_num:
                    self.save_views_state.append([
                        idx + view_idx, view
                    ])
        if len(self.save_views_state) > 0:
            string = f"Will Save {[x[0] for x in self.save_views_state]}"
            pop_info_box(string, 'INFO')
            self.ui.start_button.setEnabled(True)
            self.ui.shoot_button.setEnabled(True)
            return True
        else:
            pop_info_box("Select view to save", 'ERROR')

    def use_model(self, data):
        raise NotImplementedError("Use model子类需要进行实现")

    def show_image(self, fsgs):
        """
        显示画面
        """
        self.cameras_num = len(fsgs)
        self.ui.show_button.setText(f"cameras num: {self.cameras_num}")
        if len(fsgs) <= self.windows_number_per_page * (self.current_page + 1):
            self.ui.next_page_button.setEnabled(False)
        else:
            self.ui.next_page_button.setEnabled(True)
        begin = self.current_page * self.windows_number_per_page
        self.used_box = len(fsgs)
        for i in range(self.windows_number_per_page):
            frames_idx = begin + i
            if frames_idx == len(fsgs):
                break
            idx = i + 1
            fsg = np.ascontiguousarray(fsgs[frames_idx].copy())
            height, width = fsg.shape[:2]

            left_bar = getattr(self.ui, f"s_left_{idx}")
            right_bar = getattr(self.ui, f"s_right_{idx}")
            top_bar = getattr(self.ui, f"s_top_{idx}")
            bottom_bar = getattr(self.ui, f"s_bottom_{idx}")

            ui_left = int(left_bar.value() / 100 * width)
            ui_right = int(right_bar.value() / 100 * width)
            ui_top = int(top_bar.value() / 100 * height)
            ui_bottom = int(bottom_bar.value() / 100 * height)
            sub_fsg = np.ascontiguousarray(fsg[ui_top:ui_bottom, ui_left:ui_right, :])

            # fixme: 这里进行模型推理
            if getattr(self.ui, f"use_model_{idx}").isChecked():
                try:
                    data = [fsg, sub_fsg, frames_idx]
                    [fsg, sub_fsg] = self.use_model(data)
                except Exception as e:
                    getattr(self.ui, f"use_model_{idx}").setChecked(False)
                    if isinstance(e, NotImplementedError):
                        pop_info_box(f"self.use_model\n{e}", "ERROR")
                    pop_info_box(f"self.use_model\n{e}", "ERROR")

            # 显示
            set_image_on_label(getattr(self.ui, f"view_{idx}"), sub_fsg)
            state_bar = getattr(self.ui, f"state_{idx}")
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 获取当前时间
            state_bar.setText(f"{now}@{fsg.shape}")

    def open_save_folder(self):
        """打开保存的路径"""
        open_path = self.save_path
        if self.saved_shoot_paths:
            open_path = os.path.dirname(self.saved_shoot_paths[-1][-1])
        QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(open_path))

    def change_folder(self):
        self.shoot_num, self.saved_shoot_paths = 0, []
        self.video_num, self.saved_video_paths = 0, []
        self.ui.shoot_button.setText("单帧拍摄")
        self.ui.save_button.setEnabled(True)
        self.flags_lock(True)
        self.ui.delete_prev_shoot.setEnabled(False)
        self.ui.delete_prev_video.setEnabled(False)
        self.ui.shoot_button.setEnabled(False)
        self.ui.start_button.setEnabled(False)

    def get_folder_info(self):
        # path/20231212/CarType_Weather_Brightness
        v_type = self.ui.car_type.currentText()
        weather = self.ui.weather.currentText()
        brightness = self.ui.brightness.currentText()
        name = self.ui.name.text()
        folder = os.path.join(
            self.save_path,
            f"{self.ui.plate.text()}",
            self.ui.date.text(),
            f"{v_type}_{weather}_{brightness}_{name}"
        )
        folder = folder.replace(' ', '')
        return folder

    # fixme: 基于奥比中光需要修改
    def get_shoot_signal(self):
        global NEED_IR_FRAME
        NEED_IR_FRAME = True
        self.camera_stream.save_signal.connect(self.writing_one_shoot)
        self.ui.shoot_button.setEnabled(False)
        self.ui.delete_prev_shoot.setEnabled(True)

    # fixme: 基于奥比中光需要修改
    def writing_one_shoot(self, fsgs):
        # 保存每个位置相机的图片
        self.shoot_num += 1
        self.ui.shoot_button.setText(f"拍摄({self.shoot_num})")
        self.flags_lock(False)
        all_save_path = []
        timestamp = datetime.now().strftime("%H%M%S")
        root = self.get_folder_info()
        # c_type: IR RGB DEPTH ....
        for vi, view_state in deepcopy(self.save_views_state):
            c_type = view_state['type']
            c_location = view_state['location']
            save_bin = view_state['save_bin']
            folder = f"{root}_{c_location}"
            os.makedirs(folder, exist_ok=True)
            basename = f"{c_type}_{timestamp}"
            basename += f"_{self.ui.remark.text()}"

            # 写文件
            data_path = os.path.join(folder, basename)
            data_path += '.npy' if save_bin else '.png'
            if os.path.exists(data_path):
                pop_info_box(
                    f"Check View Configer, Path exists: {data_path}",
                    "ERROR"
                )
                self.change_folder()
                break
            data = fsgs[vi]
            if save_bin:
                np.save(data_path, data)
            else:
                image = Image.fromarray(cv2.cvtColor(data, cv2.COLOR_BGR2RGB))
                image.save(data_path)
            all_save_path.append(data_path)
        self.saved_shoot_paths.append(all_save_path)
        if len(self.saved_shoot_paths) > 10:
            self.saved_shoot_paths.pop(0)
        self.camera_stream.save_signal.disconnect(self.writing_one_shoot)
        self.ui.shoot_button.setEnabled(True)
        global NEED_IR_FRAME
        NEED_IR_FRAME = False

    def get_video_signal(self):
        """事件: 视频记录按钮按下"""
        self.make_video_writer()
        self.camera_stream.save_signal.connect(self.write_video)
        self.ui.start_button.setEnabled(False)
        self.ui.stop_button.setEnabled(True)
        self.ui.reset_button.setEnabled(False)
        self.ui.exit_button.setEnabled(False)

    def make_video_writer(self):
        """事件: 构建写视频句柄"""
        self.video_writers = []
        self.ui.start_button.setText(f"录制中...")
        self.t1 = time.time()
        self.frame_number = 0
        self.flags_lock(False)
        timestamp = datetime.now().strftime("%H%M%S")
        root = self.get_folder_info()
        saved_path = []
        for vi, view_state in deepcopy(self.save_views_state):
            c_type = view_state['type']
            c_location = view_state['location']
            folder = f"{root}_{c_location}"
            os.makedirs(folder, exist_ok=True)
            basename = os.path.join(str(folder), f"{c_type}_{timestamp}")
            remark = self.ui.remark.text()
            basename = basename + f"_{remark}" if remark else basename
            # 写视频
            video_path = basename + ".mp4"
            saved_path.append(video_path)

            # 设置视频编解码器（codec）
            out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'XVID'), 30, (1920, 1080))
            # writer = imageio.get_writer(video_path)
            self.video_writers.append([out, vi])

        self.saved_video_paths.append(saved_path)

    def write_video(self, frames):
        """开始写入视频"""
        self.frame_number += 1
        for writer, vi in self.video_writers:
            # writer.append_data(cv2.cvtColor(frames[vi], cv2.COLOR_RGB2BGR))
            writer.write(frames[vi])
        fps = (self.frame_number) / (time.time() - self.t1)
        self.ui.start_button.setText(f"fps: {fps:.1f}")

    def get_stop_recording_signal(self):
        """停止写入视频"""
        self.is_saving_video = False
        self.camera_stream.save_signal.disconnect(self.write_video)
        for writer, vi in self.video_writers:
            # writer.close()
            writer.release()
        self.ui.start_button.setEnabled(True)
        self.ui.stop_button.setEnabled(False)
        self.ui.reset_button.setEnabled(True)
        self.ui.exit_button.setEnabled(True)
        self.ui.delete_prev_video.setEnabled(True)
        self.video_num += 1
        self.ui.start_button.setText(f"开始录制({self.video_num})")

    def delete_files(self, paths):
        string = '\n'.join([os.path.basename(x) for x in paths])
        question = f"是否删除\n{string}?"
        reply = QMessageBox.question(
            self, "删除文件", question,
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
        )
        deleted = False
        if reply == QMessageBox.Yes:
            for path in paths:
                try:
                    os.remove(path)
                    pop_info_box(f"{path}删除成功", "INFO")
                    deleted = True
                except Exception as e:
                    print("why?", e)
                    pop_info_box(f"无法删除{path}", "ERROR")
        return deleted

    def delete_shoot_files(self):
        if self.delete_files(self.saved_shoot_paths[-1]):
            self.saved_shoot_paths.pop(-1)
        self.shoot_num -= 1
        self.ui.shoot_button.setText(f"拍摄({self.shoot_num})")
        if len(self.saved_shoot_paths) == 0:
            self.ui.delete_prev_shoot.setEnabled(False)

    def delete_videos(self):
        print(self.saved_video_paths)
        if self.delete_files(self.saved_video_paths[-1]):
            self.saved_video_paths.pop(-1)
        self.video_num -= 1
        self.ui.start_button.setText(f"开始录制({self.video_num})")
        if len(self.saved_video_paths) == 0:
            self.ui.delete_prev_video.setEnabled(False)

    def flags_lock(self, unlock):
        pushes = [
            "plate",
            "date",
            "weather",
            "brightness",
            "car_type"
        ]
        for i in range(self.cameras_num % self.windows_number_per_page):
            idx = i + 1
            pushes += [
                f"type_{idx}",
                f"location_{idx}",
                f"selected_{idx}",
                f"save_bin_{idx}"
            ]
        for name in pushes:
            getattr(self.ui, f"{name}").setEnabled(unlock)
