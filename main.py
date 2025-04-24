import shutil
import time
import emoji
import cv2
import torch
# import torchvision
# import albumentations as A  # For image augmentations
from config import BASE_DIR,INPRO_DIR,INPUT_DIR,EXIT_DIR
from vehicle_detector import VehicleDetector

import warnings
warnings.filterwarnings("ignore")

class TrafficSystem:
    def __init__(self):
        print("Initializing Enhanced Traffic System...")
        self.detector = VehicleDetector()
        self.green_lane = None
        self.base_green_time = 30
        self.yellow_lanes = []
        self.exit_counter = 1
        self.lane_time = 0
        self.is_running = False
        self._warm_up_model()

    def _warm_up_model(self):
        dummy_img = torch.zeros((1, 3, 640, 640), dtype=torch.float32)
        with torch.no_grad():
            _ = self.detector.model(dummy_img)
        print("Model warmup complete on CPU")

    def initialize_lanes(self):
        input_images = sorted(INPUT_DIR.glob("*.jpg"))[:4]
        if len(input_images) < 4:
            print(f"Need 4 images, only found {len(input_images)}")
            return False

        for i, img_path in enumerate(input_images, 1):
            lane_name = f"lane{i}.jpg"
            shutil.move(str(img_path), str(INPRO_DIR / lane_name))
            print(f"Moved {img_path.name} -> inpro_imgs/{lane_name}")
        return True

    def count_lane_vehicles(self):
        counts = []
        for i in range(1, 5):
            img_path = INPRO_DIR / f"lane{i}.jpg"
            details, weight = self.get_detailed_counts(img_path)
            print(f"Lane {i}: {weight:.1f} vehicle equivalents")
            print(f"Details: {details}")
            counts.append(weight)
        return counts

    def get_detailed_counts(self, image_path):
        img = cv2.imread(str(image_path))
        if img is None:
            return {}, 0
            
        results = self.detector.model(img)
        details = {self.detector.class_names[cls_id]: 0 for cls_id in self.detector.vehicle_classes.keys()}
        weight = 0
    
        for *_, conf, cls in results.xyxy[0]:
            cls = int(cls)
            if cls in self.detector.vehicle_classes and conf > 0.5:
                name, w_eqv = self.detector.vehicle_classes[cls]
                weight += w_eqv
                details[name] += 1
            
        return {k: v for k, v in details.items() if v > 0}, weight

    def display_lanes(self):
        lanes = ["Lane 1", "Lane 2", "Lane 3", "Lane 4"]
        status = []
        
        for i in range(4):
            if self.green_lane and i == self.green_lane - 1:
                status.append(emoji.emojize(":green_circle:"))
            elif i + 1 in self.yellow_lanes:
                status.append(emoji.emojize(":yellow_circle:"))
            else:
                status.append(emoji.emojize(":red_circle:"))
        
        print("\n" + "\t".join(lanes), end='\n ')
        print("\t".join(status) + '\n', sep=' ')

    def replace_lane_image(self, lane_num):
        image_exts = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')
        input_images = [f for f in INPUT_DIR.glob("*") if f.suffix.lower() in image_exts]
    
        if not input_images:
            print("\nNo more images in input directory")
            return False
    
        old_img = INPRO_DIR / f"lane{lane_num}.jpg"
        exit_name = f"l{self.exit_counter}{old_img.suffix}"
        shutil.move(str(old_img), EXIT_DIR / exit_name)
        print(f"\nMoved lane{lane_num}.jpg to exit_imgs/{exit_name}")
        self.exit_counter += 1
    
        new_img = input_images[0]
        shutil.move(str(new_img), str(INPRO_DIR / f"lane{lane_num}{new_img.suffix}"))
        print(f"Replaced with {new_img.name}")
        return True

    def control_traffic_lights(self, current_lane, duration):
        self.lane_time = duration
        self.green_lane = current_lane
        print(f"\nOpening Lane {current_lane} for {duration} seconds")
        self.display_lanes()
        next_lane, next_time = None, 0
        
        while self.lane_time > 0 and self.is_running:
            print(f"\rTime remaining: {self.lane_time}s", end="")
            
            if self.lane_time <= 15 and next_lane is None:
                if not self.replace_lane_image(current_lane):
                    time.sleep(1)
                    self.lane_time -= 1
                    continue
                
                next_lane, next_time = self.lane_calc()
                self.yellow_lanes = [current_lane, next_lane]
                self.green_lane = None
                self.display_lanes()
                print("\nYELLOW PHASE: Preparing transition...")
            
            time.sleep(1)
            self.lane_time -= 1

        if next_lane and self.is_running:
            print("\n\nTransition complete")
            self.green_lane = next_lane
            self.yellow_lanes = []
            self.control_traffic_lights(next_lane, next_time)

    def lane_calc(self):
        print("\n" + "="*50)
        print("Counting vehicles for lane selection...")
        
        counts = self.count_lane_vehicles()
        max_weight = max(counts)
        lane = counts.index(max_weight) + 1
        lane_time = int(self.base_green_time + (2 * max_weight))
        
        return lane, lane_time

    def reset_input_folder(self):
        inpro_images = list(INPRO_DIR.glob("*"))
        exit_images = list(EXIT_DIR.glob("*"))

        if not (inpro_images or exit_images):
            return False
    
        for img in exit_images:
            shutil.move(str(img), str(INPUT_DIR / img.name))
            print(f"Moved {img.name} back to input_imgs")
        
        for img in inpro_images:
            shutil.move(str(img), str(INPUT_DIR / img.name))
            print(f"Moved {img.name} back to input_imgs")
    
        self.exit_counter = 1
        return True

    def debug_detection(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            print("No Image")
            return

        with torch.no_grad():
            results = self.detector.model(img)

        annotated_img = img.copy()
        for det in results.xyxy[0]:
            x1, y1, x2, y2, conf, cls = det
            class_name = self.detector.class_names.get(int(cls), "Unknown")
            confidence = round(conf.item(), 2)
        
            annotated_img = cv2.rectangle(annotated_img, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
            annotated_img = cv2.putText(annotated_img, f"{class_name} {confidence}", (int(x1), int(y1)-10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        debug_path = BASE_DIR / "debug.jpg"
        cv2.imwrite(str(debug_path), cv2.cvtColor(annotated_img, cv2.COLOR_RGB2BGR))
    
    def get_lane_status(self):
        status = {}
        for i in range(1, 5):
            img_path = INPRO_DIR / f"lane{i}.jpg"
            if not img_path.exists():
                status[i] = "off"
                continue
        
            if self.green_lane == i:
                status[i] = "green"
            elif i in self.yellow_lanes:
                status[i] = "yellow"
            else:
                status[i] = "red"
        return status

    def start_system(self):
        if not self.is_running:
            self.is_running = True
            if not self.initialize_lanes():
                self.is_running = False
                return False
            
            self.green_lane, green_time = self.lane_calc()
            self.control_traffic_lights(self.green_lane, green_time)
            return True
        return False

    def stop_system(self):
        self.is_running = False
        self.green_lane = None
        self.yellow_lanes = []
        self.lane_time = 0
        return self.reset_input_folder()
    
    
# if __name__ == "__main__":
#     system = TrafficSystem()
#     #For debugging specific images:
#     # system.debug_detection("D:/FYP/fyp_main/input_imgs/lane6.jpg")
#     system.run()
#     if system.reset_input_folder():
#         print("Reset Completed")