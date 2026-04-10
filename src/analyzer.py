import os
from ultralytics import YOLO

class PCBAnalyzer:
    def __init__(self, model_path="src/yolov8n_pcb.pt"): # Path to the model file
        # Initializes the YOLOv8 Nano model
        self.model = YOLO(model_path)

    def analyze_board(self, warped_image):
        # Takes the flattened OpenCV image, runs detection, and returns the annotated image and a Bill of Materials (BOM).
        # 1. Run Inference (conf=0.4 filters out weak, messy guesses)
        results = self.model(warped_image, conf=0.4, verbose=False)
        
        # We only passed one image so weneed the first result object
        result = results[0]

        # 2. Generate the Annotated Image
        # result.plot() automatically draws the bounding boxes and labels onto the image!
        annotated_image = result.plot()

        # 3. Generate the Bill of Materials (BOM)
        # We extract the class names from the detected bounding boxes
        bom_counts = {}
        for box in result.boxes:
            class_id = int(box.cls[0].item())
            class_name = self.model.names[class_id]
            
            # Tally up components
            bom_counts[class_name] = bom_counts.get(class_name, 0) + 1

        # Format the BOM for the Flask front-end
        bom_list = [{"component": k, "count": v} for k, v in bom_counts.items()]

        return annotated_image, bom_list
