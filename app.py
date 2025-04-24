from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import threading
import time
import os
from pathlib import Path
from main import TrafficSystem
from config import BASE_DIR, INPUT_DIR, INPRO_DIR, EXIT_DIR, create_dirs

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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
    """Endpoint to get current system status"""
    return jsonify({
        "lane_status": system.get_lane_status(),
        "system_status": "running" if system.is_running else "stopped",
        "time_remain": system.lane_time,
        "current_lane": system.green_lane,
        "yellow_lanes": system.yellow_lanes,
        "vehicle_counts": system.count_lane_vehicles() if system.is_running else []
    })


@app.route('/debug', methods=['POST'])
def debug_image():
    """Endpoint for debugging vehicle detection with image display"""
    if 'image' not in request.files:
        return jsonify({
            "error": "No image provided",
            "status": "error"
        }), 400
    
    # Save the uploaded image temporarily
    image_file = request.files['image']
    temp_path = os.path.join(BASE_DIR, "debug_temp.jpg")
    image_file.save(temp_path)
    
    # Process the image (assuming system.debug_detection exists)
    system.debug_detection(temp_path)
    debug_path = str(BASE_DIR / "debug.jpg")
    
    # Return HTML response with the debug image
    return f"""
    <html>
        <head>
            <title>Debug Image Results</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                img {{ max-width: 80%; border: 1px solid #ddd; margin: 20px 0; }}
                .info {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>Vehicle Detection Debug Results</h1>
            <div class="image-container">
                <img src="/view_debug" alt="Debug Image">
            </div>
            <div class="info">
                <p><strong>Status:</strong> Processing complete</p>
                <p><strong>Image saved at:</strong> {debug_path}</p>
                <p><strong>Original filename:</strong> {image_file.filename}</p>
            </div>
        </body>
    </html>
    """

@app.route('/view_debug')
def view_debug():
    """Endpoint to serve the processed debug image"""
    debug_path = str(BASE_DIR / "debug.jpg")
    return send_file(debug_path, mimetype='image/jpeg')

# Clean up function (optional)
@app.teardown_request
def remove_temp_files(exception=None):
    temp_path = os.path.join(BASE_DIR, "debug_temp.jpg")
    if os.path.exists(temp_path):
        os.remove(temp_path)

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