import numpy as np
import cv2
import onnxruntime as ort
import warnings

from gwel.network import Detector

warnings.filterwarnings("ignore")


def bbox_to_polygon(bboxes):
    polygons = []
    for bbox in bboxes:
        x1, y1, x2, y2 = bbox
        polygon = [[x1, y1], [x1, y2], [x2, y2], [x2, y1]]
        polygons.append([np.array(polygon, dtype=np.int32).reshape(-1, 1, 2)])
    return polygons


def non_max_suppression(boxes, scores, iou_threshold=0.45):
    # boxes: [N,4] numpy array
    # scores: [N] numpy array
    idxs = scores.argsort()[::-1]
    keep = []

    while len(idxs) > 0:
        i = idxs[0]
        keep.append(i)
        if len(idxs) == 1:
            break
        ious = compute_iou(boxes[i], boxes[idxs[1:]])
        idxs = idxs[1:][ious < iou_threshold]

    return keep


def compute_iou(box, boxes):
    x1 = np.maximum(box[0], boxes[:, 0])
    y1 = np.maximum(box[1], boxes[:, 1])
    x2 = np.minimum(box[2], boxes[:, 2])
    y2 = np.minimum(box[3], boxes[:, 3])

    inter_area = np.maximum(0, x2 - x1) * np.maximum(0, y2 - y1)
    box_area = (box[2] - box[0]) * (box[3] - box[1])
    boxes_area = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    union_area = box_area + boxes_area - inter_area
    return inter_area / (union_area + 1e-6)


class YOLOv8(Detector):
    def __init__(self, weights: str, device: str = "cpu", patch_size: tuple = None, threshold: float = 0.5):
        self.device = device
        self.patch_size = patch_size
        self.threshold = threshold
        self.weights = weights
        self.session = ort.InferenceSession(weights, providers=["CPUExecutionProvider"])

    def inference(self, image: np.ndarray):
        if self.patch_size:
            return self.inference_with_patches(self.patch_size, image)

        input_tensor = self.preprocess(image)
        outputs = self.session.run(None, {"images": input_tensor})
        detections = self.postprocess(outputs, image.shape[:2])
        return bbox_to_polygon(detections)

    def inference_with_patches(self, patch_size: tuple, image: np.ndarray):
        h, w = image.shape[:2]
        patch_h, patch_w = patch_size
        pad_h = (patch_h - h % patch_h) % patch_h
        pad_w = (patch_w - w % patch_w) % patch_w
        padded_image = cv2.copyMakeBorder(image, 0, pad_h, 0, pad_w, cv2.BORDER_CONSTANT, value=(0, 0, 0))

        detections = []
        for i in range(0, padded_image.shape[0], patch_h):
            for j in range(0, padded_image.shape[1], patch_w):
                patch = padded_image[i:i + patch_h, j:j + patch_w]
                input_tensor = self.preprocess(patch)
                outputs = self.session.run(None, {"images": input_tensor})
                boxes = self.postprocess(outputs, patch.shape[:2])
                # adjust boxes to original coordinates
                for bbox in boxes:
                    x1, y1, x2, y2 = bbox
                    x1 += j
                    x2 += j
                    y1 += i
                    y2 += i
                    x1, y1 = max(0, x1), max(0, y1)
                    x2, y2 = min(w, x2), min(h, y2)
                    detections.append([x1, y1, x2, y2])

        return bbox_to_polygon(detections)

    def preprocess(self, image: np.ndarray):
        img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (640, 640))
        img = img.astype(np.float32) / 255.0
        img = np.transpose(img, (2, 0, 1))
        return np.expand_dims(img, axis=0)

    def postprocess(self, outputs, original_shape):
        # ONNX YOLOv8 raw output: [batch, num_boxes, 85]
        # 85 = [x, y, w, h, conf, class_probs...]
        predictions = outputs[0][0]  # take first batch
        boxes = predictions[:, :4]
        scores = predictions[:, 4] * predictions[:, 5:].max(axis=1)
        mask = scores > self.threshold
        boxes = boxes[mask]
        scores = scores[mask]
        if len(boxes) == 0:
            return []
        keep = non_max_suppression(boxes, scores)
        # Convert xywh to xyxy
        xyxy_boxes = []
        for i in keep:
            x, y, w, h = boxes[i]
            xyxy_boxes.append([x, y, x + w, y + h])
        return xyxy_boxes

