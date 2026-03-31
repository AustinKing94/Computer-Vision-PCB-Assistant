import os
import shutil
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, send_file, request, jsonify
from src.image_capture import capture_raw_images

app = Flask(__name__)

# --- CONFIGURATION ---
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
CURRENT_DIR = DATA_DIR / 'current'
CAPTURES_DIR = DATA_DIR / 'captures'

# Ensure directories exist
for directory in [DATA_DIR, CURRENT_DIR, CAPTURES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Helper functions to get current image paths
def get_current_frame(): return CURRENT_DIR / 'current_frame.jpg'
def get_current_thermal(): return CURRENT_DIR / 'current_thermal.jpg'


# --- DASHBOARD ROUTES ---
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/get_current_image')
def get_current_image():
    """Serves the standard RGB frame."""
    if get_current_frame().exists():
        return send_file(str(get_current_frame()), mimetype='image/jpeg', cache_timeout=0)
    return jsonify({'error': 'No image'}), 404

@app.route('/get_current_thermal')
def get_current_thermal():
    """Serves the thermal overlay frame."""
    if get_current_thermal().exists():
        return send_file(str(get_current_thermal()), mimetype='image/jpeg', cache_timeout=0)
    return jsonify({'error': 'No thermal image'}), 404


# --- API ROUTES ---
@app.route('/api/capture', methods=['POST'])
def api_capture():
    """
    ACTION 1: Triggers the physical hardware.
    Takes a new picture and overwrites the 'current' canvas.
    """
    try:
        # Call your new script, passing the exact file paths it needs to use
        success, message = capture_raw_images(
            rgb_save_path=str(get_current_frame()), 
            thermal_save_path=str(get_current_thermal())
        )
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': message}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/save', methods=['POST'])
def api_save():
    """
    ACTION 2: Saves to files.
    Copies whatever is currently on the canvas to the 'captures' folder.
    """
    try:
        if not get_current_frame().exists():
            return jsonify({'success': False, 'error': 'No image on canvas to save'}), 400
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Copy standard frame
        capture_filename = f'capture_{timestamp}.jpg'
        shutil.copy2(str(get_current_frame()), str(CAPTURES_DIR / capture_filename))
        
        # Copy thermal frame (if it exists)
        if get_current_thermal().exists():
            shutil.copy2(str(get_current_thermal()), str(CAPTURES_DIR / f'thermal_{timestamp}.jpg'))
            
        return jsonify({'success': True, 'filename': capture_filename})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/load_capture', methods=['POST'])
def api_load_capture():
    """Copies a saved capture back to the 'current' directory to view on dashboard."""
    try:
        filename = request.json.get('filename') # e.g., capture_20260330_1234.jpg
        if not filename: return jsonify({'success': False}), 400

        timestamp = filename.replace('capture_', '').replace('.jpg', '')
        
        # Safe paths
        target_frame = CAPTURES_DIR / filename
        target_thermal = CAPTURES_DIR / f'thermal_{timestamp}.jpg'

        if target_frame.exists():
            shutil.copy2(str(target_frame), str(get_current_frame()))
        if target_thermal.exists():
            shutil.copy2(str(target_thermal), str(get_current_thermal()))
            
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/delete_capture', methods=['POST'])
def api_delete_capture():
    """Deletes both standard and thermal versions of a capture."""
    try:
        filename = request.json.get('filename')
        timestamp = filename.replace('capture_', '').replace('.jpg', '')
        
        frame_path = CAPTURES_DIR / filename
        thermal_path = CAPTURES_DIR / f'thermal_{timestamp}.jpg'

        if frame_path.exists(): frame_path.unlink()
        if thermal_path.exists(): thermal_path.unlink()
            
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# --- GALLERY ROUTES ---
@app.route('/gallery')
def gallery():
    captures = []
    if CAPTURES_DIR.exists():
        # Get only the base capture images, sort newest first
        files = sorted(CAPTURES_DIR.glob('capture_*.jpg'), key=lambda p: p.stat().st_ctime, reverse=True)
        for f in files:
            captures.append({'filename': f.name, 'date': datetime.fromtimestamp(f.stat().st_ctime).strftime('%b %d, %Y')})
            
    return render_template('gallery.html', captures=captures)

@app.route('/api/capture/<filename>')
def get_capture(filename):
    """Serves a specific image for export/download."""
    file_path = CAPTURES_DIR / filename
    if file_path.exists() and str(file_path.resolve()).startswith(str(CAPTURES_DIR.resolve())):
        return send_file(str(file_path), mimetype='image/jpeg', as_attachment=True)
    return jsonify({'error': 'Not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)