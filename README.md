# Computer-Vision-PCB-Assistant

A self-contained PCB inspection system built on a Raspberry Pi 4B that combines computer vision, machine learning, and thermal imaging to identify components and generate a Bill of Materials from a captured image.
 
---
 
## Hardware Requirements
 
- Raspberry Pi 4B
- Raspberry Pi Camera V2
- MLX90640 Thermal Sensor (connected via I2C)
- USB battery bank
- 3D printed frame and inspection plate (3D files included)
- 4x ArUco markers (DICT_5X5_1000) printed and attached to the inspection plate corners
 
To generate ArUco markers: https://chev.me/arucogen/
Select dictionary **5x5_1000** and print markers with IDs 0, 1, 2, and 3.
 
---
 
## Software Requirements
 
- Raspberry Pi OS (64-bit recommended)
- Python 3.9+
- `rpicam-still` (included with Raspberry Pi OS)
 
---
 
## Installation
 
Clone the repository:
 
```bash
git clone https://github.com/AustinKing94/Computer-Vision-PCB-Assistant.git
cd Computer-Vision-PCB-Assistant
```
 
Create and activate a virtual environment:
 
```bash
python -m venv venv
source venv/bin/activate
```
 
Install dependencies:
 
```bash
pip install -r requirements.txt
```
 
Place the YOLOv8 model weights file (`yolov8n_pcb.pt`) in the `src/` directory.
 
---
 
## Running the Application
 
With the virtual environment active, start the Flask server:
 
```bash
python app.py
```
 
Connect to the Raspberry Pi hotspot and navigate to:
 
```
http://10.42.0.1:8080
```
 
---
 
## Usage
 
1. Place a PCB on the inspection plate inside the frame
2. Click **Capture** on the dashboard to trigger the camera and run detection
3. The annotated image and Bill of Materials will appear on the dashboard
4. Toggle **Thermal** to switch between the RGB and thermal views
5. Click **Save** to store the current capture to the gallery
6. Navigate to **Gallery** to review, load, or export past captures
 
---
 
## Project Structure
 
```
├── app.py                  # Flask application and routes
├── src/
│   ├── image_capture.py    # RGB and thermal hardware capture
│   ├── image_processing.py # ArUco detection and perspective warp pipeline
│   ├── thermal_processing.py # Thermal frame rendering
│   └── analyzer.py         # YOLOv8 component detection and BOM generation
├── templates/
│   ├── dashboard.html
│   └── gallery.html
├── static/
│   ├── style.css
│   └── app.js
├── data/                   # Created at runtime
│   ├── current/            # Active dashboard images
│   └── captures/           # Saved inspection captures
└── requirements.txt
```
