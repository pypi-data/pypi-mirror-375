import os

import cv2
import numpy as np
import onnxruntime
import torch
import torchvision.transforms as transforms
import wxw.common as cm
from PIL import Image


class MarkLoc:
    def __init__(self, folder, size=320):
        onnx_path = os.path.join(folder, "mark_loc.onnx")
        self.model = cm.ONNXRunner(onnx_path)
        self.size = size

    def preprocess(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cm.size_pre_process(image, long=self.size, align=1)
        image = cm.pad_image(image, centre=False)[0]
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = image.astype(np.float32) / 127.5 - 1
        image = np.transpose(image, (2, 0, 1))
        return image[None]

    def __call__(self, image):
        height, width = image.shape[:2]
        block = self.preprocess(image)
        p_mask = self.model(block)[0].squeeze(0)
        score = np.max(p_mask)
        y, x = np.where(p_mask == score)
        b_h, b_w = block.shape[2:4]
        x, y, score, mask = x / b_w, y / b_h, score, p_mask
        print(x, y, score, mask.shape)
        size = max(height, width)
        x, y = int(x * size), int(y * size)
        # mask = cm.image_norm(mask)
        # cv2.imshow("mask", mask)
        return x, y, score


def get_meanface(meanface_file, num_nb):
    with open(meanface_file) as f:
        meanface = f.readlines()[0]

    meanface = meanface.strip().split()
    meanface = [float(x) for x in meanface]
    meanface = np.array(meanface).reshape(-1, 2)
    # each landmark predicts num_nb neighbors
    meanface_indices = []
    for i in range(meanface.shape[0]):
        pt = meanface[i, :]
        dists = np.sum(np.power(pt - meanface, 2), axis=1)
        indices = np.argsort(dists)
        meanface_indices.append(indices[1:1 + num_nb])

    # each landmark predicted by X neighbors, X varies
    meanface_indices_reversed = {}
    for i in range(meanface.shape[0]):
        meanface_indices_reversed[i] = [[], []]
    for i in range(meanface.shape[0]):
        for j in range(num_nb):
            meanface_indices_reversed[meanface_indices[i][j]][0].append(i)
            meanface_indices_reversed[meanface_indices[i][j]][1].append(j)

    max_len = 0
    for i in range(meanface.shape[0]):
        tmp_len = len(meanface_indices_reversed[i][0])
        if tmp_len > max_len:
            max_len = tmp_len

    # tricks, make them have equal length for efficient computation
    for i in range(meanface.shape[0]):
        tmp_len = len(meanface_indices_reversed[i][0])
        meanface_indices_reversed[i][0] += meanface_indices_reversed[i][0] * 10
        meanface_indices_reversed[i][1] += meanface_indices_reversed[i][1] * 10
        meanface_indices_reversed[i][0] = meanface_indices_reversed[i][0][:max_len]
        meanface_indices_reversed[i][1] = meanface_indices_reversed[i][1][:max_len]

    # make the indices 1-dim
    reverse_index1 = []
    reverse_index2 = []
    for i in range(meanface.shape[0]):
        reverse_index1 += meanface_indices_reversed[i][0]
        reverse_index2 += meanface_indices_reversed[i][1]
    return meanface_indices, reverse_index1, reverse_index2, max_len


class FaceLandMark:
    def __init__(self, folder):
        onnx_path = os.path.join(folder, "face_landmark.onnx")
        self.mean_face_txt = os.path.join(folder, "mean_face.txt")
        self.onnx_session = onnxruntime.InferenceSession(
            onnx_path, providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
        )
        print(len(self.onnx_session.get_inputs()))
        self.input_name = self.onnx_session.get_inputs()[0].name

    def obtain_face_lmk(self, img):
        img = cv2.resize(img, (256, 256))
        inputs = Image.fromarray(img[:, :, ::-1].astype('uint8'), 'RGB')
        normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        preprocess = transforms.Compose([transforms.Resize((256, 256)), transforms.ToTensor(), normalize])
        inputs = preprocess(inputs).unsqueeze(0).numpy()
        # print(inputs.shape)

        # print(len(self.onnx_session.run([], {self.input_name: inputs})))
        outputs_cls, outputs_x, outputs_y, outputs_nb_x, outputs_nb_y = self.onnx_session.run(
            [], {self.input_name: inputs})
        # print(outputs_cls.shape, outputs_x.shape, outputs_y.shape, outputs_nb_x.shape, outputs_nb_y.shape)
        outputs_x = torch.from_numpy(outputs_x)
        outputs_y = torch.from_numpy(outputs_y)
        outputs_nb_x = torch.from_numpy(outputs_nb_x)
        outputs_nb_y = torch.from_numpy(outputs_nb_y)
        outputs_cls = torch.from_numpy(outputs_cls)

        # print(outputs_cls.shape, outputs_x.shape, outputs_nb_x.shape)

        tmp_batch, tmp_channel, tmp_height, tmp_width = outputs_cls.size()
        assert tmp_batch == 1

        outputs_cls = outputs_cls.view(tmp_batch * tmp_channel, -1)
        max_ids = torch.argmax(outputs_cls, 1)
        # max_cls = torch.max(outputs_cls, 1)[0]
        max_ids = max_ids.view(-1, 1)
        max_ids_nb = max_ids.repeat(1, 10).view(-1, 1)

        outputs_x = outputs_x.view(tmp_batch * tmp_channel, -1)
        outputs_x_select = torch.gather(outputs_x, 1, max_ids)
        outputs_x_select = outputs_x_select.squeeze(1)
        outputs_y = outputs_y.view(tmp_batch * tmp_channel, -1)
        outputs_y_select = torch.gather(outputs_y, 1, max_ids)
        outputs_y_select = outputs_y_select.squeeze(1)

        outputs_nb_x = outputs_nb_x.view(tmp_batch * 10 * tmp_channel, -1)
        outputs_nb_x_select = torch.gather(outputs_nb_x, 1, max_ids_nb)
        outputs_nb_x_select = outputs_nb_x_select.squeeze(1).view(-1, 10)
        outputs_nb_y = outputs_nb_y.view(tmp_batch * 10 * tmp_channel, -1)
        outputs_nb_y_select = torch.gather(outputs_nb_y, 1, max_ids_nb)
        outputs_nb_y_select = outputs_nb_y_select.squeeze(1).view(-1, 10)

        tmp_x = (max_ids % tmp_width).view(-1, 1).float() + outputs_x_select.view(-1, 1)
        tmp_y = (max_ids // tmp_width).view(-1, 1).float() + outputs_y_select.view(-1, 1)
        tmp_x /= 1.0 * 256 / 32
        tmp_y /= 1.0 * 256 / 32

        tmp_nb_x = (max_ids % tmp_width).view(-1, 1).float() + outputs_nb_x_select
        tmp_nb_y = (max_ids // tmp_width).view(-1, 1).float() + outputs_nb_y_select
        tmp_nb_x = tmp_nb_x.view(-1, 10)
        tmp_nb_y = tmp_nb_y.view(-1, 10)
        tmp_nb_x /= 1.0 * 256 / 32
        tmp_nb_y /= 1.0 * 256 / 32
        lms_pred_x, lms_pred_y, lms_pred_nb_x, lms_pred_nb_y = tmp_x, tmp_y, tmp_nb_x, tmp_nb_y
        # lms_pred = torch.cat((lms_pred_x, lms_pred_y), dim=1).flatten()
        _, reverse_index1, reverse_index2, max_len = get_meanface(self.mean_face_txt, 10)
        tmp_nb_x = lms_pred_nb_x[reverse_index1, reverse_index2].view(98, max_len)
        tmp_nb_y = lms_pred_nb_y[reverse_index1, reverse_index2].view(98, max_len)
        tmp_x = torch.mean(torch.cat((lms_pred_x, tmp_nb_x), dim=1), dim=1).view(-1, 1)
        tmp_y = torch.mean(torch.cat((lms_pred_y, tmp_nb_y), dim=1), dim=1).view(-1, 1)
        lms_pred_merge = torch.cat((tmp_x, tmp_y), dim=1).flatten()
        lms_pred_merge = lms_pred_merge.cpu().numpy()
        landmarks = []
        for i in [60, 64, 68, 72, 76, 82]:
            x_pred = lms_pred_merge[i * 2] * img.shape[1]
            y_pred = lms_pred_merge[i * 2 + 1] * img.shape[0]
            landmarks.append([x_pred / 256, y_pred / 256])
        return landmarks


class FaceDet:
    def __init__(self) -> None:
        from insightface.app import FaceAnalysis

        det_size = 320
        self.app = FaceAnalysis(providers=["CUDAExecutionProvider"])
        models = {}
        for key in ["detection"]:  # "landmark_2d_106"
            models[key] = self.app.models[key]
        self.app.models = models
        self.app.prepare(ctx_id=0, det_size=(det_size, det_size))

    def run_face(self, img):
        return self.app.get(img)

# model = MarkLoc("markloc.onnx")
# pathname = "/home/weixianwei/code/MarkLoc/scripts/parse_train_data/process/*1227*/*.png"
# all_path = glob(pathname)
# for path in all_path:
#     image = cv2.imread(path)
#     x, y, score = model(image)
#     print(x, y, score)
#     cv2.circle(image, (x, y), 3, (0, 0, 222), -1)
#     cv2.imshow("image", image)
#     cv2.waitKey(0)
