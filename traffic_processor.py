import os
import shutil
import time
from pathlib import Path
import cv2
import torch

class VehicleDetector:
    def __init__(self):
        """Initialize YOLOv5 model for vehicle detection"""
        print("Loading YOLOv5 model...")
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        self.model.eval()
        self.vehicle_classes = [2, 3, 5, 7]  # COCO classes: car, motorcycle, bus, truck
        print("Model loaded successfully!")

    def count_vehicles(self, image_path):
        """Count vehicles in an image"""
        img = cv2.imread(str(image_path))
        if img is None:
            print(f"Error: Could not read image {image_path}")
            return 0
            
        results = self.model(img)
        return sum(1 for *_, conf, cls in results.xyxy[0] 
               if int(cls) in self.vehicle_classes and conf > 0.5)

class ImageProcessor:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.input_dir = self.base_dir / "input_imgs"
        self.inpro_dir = self.base_dir / "inpro_imgs"
        self.exit_dir = self.base_dir / "exit_imgs"
        self.detector = VehicleDetector()
        
        # Create directories if they don't exist
        for directory in [self.input_dir, self.inpro_dir, self.exit_dir]:
            directory.mkdir(exist_ok=True)

    def wait_for_images(self, required=4):
        """Wait until enough images are available"""
        while True:
            input_images = list(self.input_dir.glob("*.jpg"))
            if len(input_images) >= required:
                return sorted(input_images)[:required]
            
            print(f"Waiting for images... (have {len(input_images)}, need {required})")
            time.sleep(5)

    def process_batch(self):
        """Process one batch of 4 images"""
        # Get next batch
        image_paths = self.wait_for_images()
        
        # Process each lane
        lane_counts = []
        for i, img_path in enumerate(image_paths, 1):
            # Move to inpro directory
            lane_name = f"lane{i}.jpg"
            dest_path = self.inpro_dir / lane_name
            shutil.move(str(img_path), str(dest_path))
            
            # Count vehicles
            count = self.detector.count_vehicles(dest_path)
            lane_counts.append(count)
            print(f"{lane_name}: {count} vehicles")
            
            # Write count to file
            with open(self.inpro_dir / f"lane{i}_count.txt", "w") as f:
                f.write(str(count))
        
        # Find busiest lane
        max_count = max(lane_counts)
        busiest_lane = lane_counts.index(max_count) + 1
        
        # Move busiest image to exit directory
        busiest_img = self.inpro_dir / f"lane{busiest_lane}.jpg"
        shutil.move(str(busiest_img), self.exit_dir / busiest_img.name)
        print(f"Moved {busiest_img.name} to exit directory")
        
        return lane_counts

if __name__ == "__main__":
    processor = ImageProcessor()
    while True:
        print("\n" + "="*50)
        print("Processing new batch...")
        counts = processor.process_batch()
        print(f"Current counts: {counts}")