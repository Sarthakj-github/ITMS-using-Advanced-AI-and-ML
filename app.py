from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_cors import CORS
import threading
import time
import os
from pathlib import Path
from main import TrafficSystem
from config import BASE_DIR, INPUT_DIR, INPRO_DIR, EXIT_DIR, create_dirs
import uuid  # For generating unique filenames
from glob import glob
from datetime import datetime, timedelta


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure debug image folder
DEBUG_IMAGE_FOLDER = os.path.join(BASE_DIR, 'debug_images')
os.makedirs(DEBUG_IMAGE_FOLDER, exist_ok=True)

# Configuration
DEBUG_IMAGE_RETENTION = timedelta(hours=1)  # Keep images for 1 hour
MAX_DEBUG_IMAGES = 50  # Maximum number of debug images to keep

# Initialize the traffic system and directories
system = TrafficSystem()
create_dirs()

@app.route('/start', methods=['POST'])
def start_system():
    """Endpoint to start the traffic management system"""
    if system.is_running:
        return jsonify({
            "status": "error",
            "message": "System is already running",
            "system_status": "running"
        }), 400

    # Start in a separate thread to avoid blocking
    def run_system():
        system.start_system()

    thread = threading.Thread(target=run_system)
    thread.daemon = True
    thread.start()

    return jsonify({
        "status": "started",
        "message": "Traffic system started successfully",
        "system_status": "running"
    })

@app.route('/stop', methods=['POST'])
def stop_system():
    """Endpoint to stop the traffic management system"""
    if not system.is_running:
        return jsonify({
            "status": "error",
            "message": "System is not running",
            "system_status": "stopped"
        }), 400

    success = system.stop_system()
    return jsonify({
        "status": "stopped",
        "message": "Traffic system stopped" + (" and reset" if success else ""),
        "system_status": "stopped"
    })

@app.route('/status', methods=['GET'])
def get_status():
    """Debug version of status endpoint"""
    status = {
        "lane_status": system.get_lane_status(),
        "system_status": "running" if system.is_running else "stopped",
        "time_remain": system.lane_time,
        "current_lane": system.green_lane,
        "yellow_lanes": system.yellow_lanes,
        "vehicle_counts": system.count_lane_vehicles() if system.is_running else []
    }
    print("DEBUG - Status payload:", status)  # Add this line
    return jsonify(status)

@app.route('/debug', methods=['POST'])
def debug_image():
    """Endpoint for debugging vehicle detection with image display"""
    if 'image' not in request.files:
        return jsonify({
            "status": "error",
            "message": "No image provided"
        }), 400

    try:
        # Generate unique filename
        unique_id = str(uuid.uuid4())
        original_filename = request.files['image'].filename
        file_ext = os.path.splitext(original_filename)[1]
        
         # Create paths
        debug_filename = f"debug_{unique_id}{file_ext}"
        debug_path = os.path.join(DEBUG_IMAGE_FOLDER, debug_filename)
        
        # Process the image (assuming system.debug_detection exists)
        processed_filename = f"processed_{unique_id}{file_ext}"
        processed_path = os.path.join(DEBUG_IMAGE_FOLDER, processed_filename)

        # Save the uploaded image
        request.files['image'].save(debug_path)
        system.debug_detection(debug_path, processed_path)
        
        # Return URL to access the processed image
        return jsonify({
            "status": "success",
            "original_filename": original_filename,
            "processed_url": f"/debug_images/{processed_filename}"
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/debug_images/<filename>')
def serve_debug_image(filename):
    """Serve processed debug images"""
    return send_from_directory(DEBUG_IMAGE_FOLDER, filename)


@app.route('/view_debug')
def view_debug():
    """Endpoint to serve the processed debug image"""
    debug_path = str(BASE_DIR / "debug.jpg")
    return send_file(debug_path, mimetype='image/jpeg')

@app.teardown_request
def cleanup_debug_images(exception=None):
    """Clean up debug images based on age and quantity"""
    try:
        now = datetime.now()
        debug_images = []
        
        # Collect all debug images with their timestamps
        for pattern in ['debug_*.*', 'processed_*.*']:
            for image_path in glob(os.path.join(DEBUG_IMAGE_FOLDER, pattern)):
                try:
                    mtime = datetime.fromtimestamp(os.path.getmtime(image_path))
                    debug_images.append((image_path, mtime))
                except Exception as e:
                    app.logger.error(f"Could not get mtime for {image_path}: {str(e)}")
                    continue
        
        # Sort by modification time (oldest first)
        debug_images.sort(key=lambda x: x[1])
        
        # Cleanup based on age
        for image_path, mtime in debug_images:
            if now - mtime > DEBUG_IMAGE_RETENTION:
                try:
                    os.remove(image_path)
                    app.logger.info(f"Cleaned up old debug image: {image_path}")
                except Exception as e:
                    app.logger.error(f"Failed to delete {image_path}: {str(e)}")
        
        # Cleanup based on quantity (if we have too many)
        if len(debug_images) > MAX_DEBUG_IMAGES:
            for image_path, _ in debug_images[:len(debug_images) - MAX_DEBUG_IMAGES]:
                try:
                    os.remove(image_path)
                    app.logger.info(f"Cleaned up excess debug image: {image_path}")
                except Exception as e:
                    app.logger.error(f"Failed to delete {image_path}: {str(e)}")
                    
    except Exception as e:
        app.logger.error(f"Error during debug image cleanup: {str(e)}")

@app.route('/reset', methods=['POST'])
def reset_system():
    """Endpoint to manually reset the system"""
    success = system.reset_input_folder()
    return jsonify({
        "status": "success" if success else "error",
        "message": "System reset completed" if success else "No images to reset",
        "system_status": "stopped"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)