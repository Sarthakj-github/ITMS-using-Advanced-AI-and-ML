import cv2
import torch
# import torchvision
# import albumentations as A  # For image augmentations
import numpy as np

import warnings
warnings.filterwarnings("ignore")

# def verify_setup():
#     print("=== System Verification ===")
#     print(f"PyTorch: {torch.__version__}")
#     print(f"Torchvision: {torchvision.__version__}")
#     print(f"YOLOv5 commit: {torch.hub.list('ultralytics/yolov5')[-1]}")

# Configure paths

class VehicleDetector:
    def __init__(self):
        print("Loading YOLOv5 model on CPU...")
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5l', pretrained=True)
        self.model.eval()

        # Class ID to weight map (vehicles only)
        self.vehicle_classes = {
            1: ("bicycle", 0.5),  # bicycle
            2: ("car", 1.0),      # car
            3: ("motorcycle", 0.7), # motorcycle
            5: ("bus", 3.0),      # bus
            6: ("train", 4.0),    # train
            7: ("truck", 2.5),    # truck
            8: ("boat", 1.5)      # boat
        }

        # Extract class names correctly
        self.class_names = {k: v[0] for k, v in self.vehicle_classes.items()}

    def preprocess(self, img_path):
        """Preprocess image for detection"""
        img = cv2.imread(str(img_path))  # Ensure string path
        if img is None:
            print(f"Failed to read image: {img_path}")
            return None

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.astype('float32') / 255.0

        h, w = img.shape[:2]
        if h != w:
            size = max(h, w)
            pad_h = (size - h) // 2
            pad_w = (size - w) // 2
            img = np.pad(img, [(pad_h, size-h-pad_h), (pad_w, size-w-pad_w), (0, 0)], mode='constant')

        return img


    # def count_vehicles(self, img_path):
    #     img_tensor = self.preprocess(img_path)
    #     if img_tensor is None:
    #         return 0.0

    #     with torch.no_grad():
    #         results = self.model(img_tensor)

    #     total_weight = 0.0

    #     # results.pred[0] contains the detections: (x1, y1, x2, y2, confidence, class)
    #     for det in results.pred[0]:
    #         cls_id = int(det[5])
    #         conf = float(det[4])
    #         if cls_id in self.vehicle_classes and conf > 0.3:
    #             total_weight += self.vehicle_classes[cls_id] * conf

    #     return total_weight
