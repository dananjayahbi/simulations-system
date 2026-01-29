#!/usr/bin/env python3
# server.py - Backend server for Loops Visualization System

"""
Loops Backend Server
====================
A Flask-based backend server that:
- Serves the frontend dashboard
- Provides API endpoints for simulation management
- Launches micro app control panels
- Streams terminal output via WebSocket
"""

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import sys
import subprocess
import json
import threading
import queue
import logging
from datetime import datetime
from pathlib import Path

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
SIMULATIONS_DIR = BASE_DIR / "simulations"
LOGS_DIR = BASE_DIR / "logs"
VENV_DIR = BASE_DIR / "venv"

# Determine the Python executable to use (prefer venv if exists)
if sys.platform == 'win32':
    VENV_PYTHON = VENV_DIR / "Scripts" / "python.exe"
else:
    VENV_PYTHON = VENV_DIR / "bin" / "python"

# Use venv Python if it exists, otherwise use system Python
PYTHON_EXECUTABLE = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable

# Create logs directory if it doesn't exist
LOGS_DIR.mkdir(exist_ok=True)

# Configure logging
log_filename = LOGS_DIR / f"loops_{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('loops')

# Add base dir to path for imports
sys.path.insert(0, str(BASE_DIR))

# Import add-on manager
from backend.addon_manager import AddonManager

app = Flask(__name__, static_folder=str(FRONTEND_DIR))
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Registry of available simulations
SIMULATIONS_REGISTRY = {}

# Store running processes
RUNNING_PROCESSES = {}

# Add-on manager instance
addon_manager = None

def get_addon_manager():
    """Get or create the add-on manager instance."""
    global addon_manager
    if addon_manager is None:
        addon_manager = AddonManager(BASE_DIR)
        # Scan and register built-in add-ons on first access
        addon_manager.scan_and_register_builtin()
    return addon_manager


def discover_simulations():
    """Discover all available simulations in the simulations folder."""
    simulations = {}
    
    if not SIMULATIONS_DIR.exists():
        return simulations
    
    # Load addon registry for timestamps and metadata
    addon_mgr = get_addon_manager()
    registry = addon_mgr._load_registry()
    addons_registry = registry.get("addons", {})
    
    for item in SIMULATIONS_DIR.iterdir():
        if item.is_dir() and not item.name.startswith('__'):
            # Check for control_panel.py or main.py
            control_panel = item / "control_panel.py"
            main_file = item / "main.py"
            config_file = item / "simulation.json"
            
            if control_panel.exists() or main_file.exists():
                # Load metadata if exists
                metadata = {
                    "id": item.name,
                    "name": item.name.replace("_", " ").title(),
                    "description": f"{item.name.replace('_', ' ').title()} simulation",
                    "icon": "🔄",
                    "color": "#4CAF50",
                    "has_control_panel": control_panel.exists(),
                    "has_main": main_file.exists(),
                    "path": str(item)
                }
                
                # Load custom metadata if available
                if config_file.exists():
                    try:
                        with open(config_file, 'r') as f:
                            custom = json.load(f)
                            metadata.update(custom)
                    except:
                        pass
                
                # Merge with addon registry data (includes installed_at timestamp)
                if item.name in addons_registry:
                    addon_data = addons_registry[item.name]
                    metadata["installed_at"] = addon_data.get("installed_at")
                    metadata["enabled"] = addon_data.get("enabled", True)
                    metadata["builtin"] = addon_data.get("builtin", False)
                else:
                    # Fallback to directory creation time if no registry entry
                    stat = item.stat()
                    metadata["installed_at"] = datetime.fromtimestamp(stat.st_ctime).isoformat()
                    metadata["enabled"] = True
                    metadata["builtin"] = False
                
                simulations[item.name] = metadata
    
    return simulations


def stream_process_output(process, sim_id):
    """Stream process output to WebSocket clients and log file."""
    
    # Create a per-simulation log file
    sim_log_file = LOGS_DIR / f"simulation_{sim_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    def read_stream(stream, stream_type):
        try:
            with open(sim_log_file, 'a', encoding='utf-8') as log_file:
                for line in iter(stream.readline, b''):
                    if line:
                        text = line.decode('utf-8', errors='replace').rstrip()
                        # Write to log file
                        log_file.write(f"[{stream_type}] {text}\n")
                        log_file.flush()
                        # Send to WebSocket
                        socketio.emit('terminal_output', {
                            'sim_id': sim_id,
                            'type': stream_type,
                            'data': text
                        })
        except Exception as e:
            logger.error(f"Error streaming output for {sim_id}: {str(e)}")
            socketio.emit('terminal_output', {
                'sim_id': sim_id,
                'type': 'error',
                'data': str(e)
            })
    
    logger.info(f"Started streaming output for simulation: {sim_id}")
    logger.info(f"Simulation log: {sim_log_file}")
    
    # Start threads to read stdout and stderr
    stdout_thread = threading.Thread(target=read_stream, args=(process.stdout, 'stdout'))
    stderr_thread = threading.Thread(target=read_stream, args=(process.stderr, 'stderr'))
    stdout_thread.daemon = True
    stderr_thread.daemon = True
    stdout_thread.start()
    stderr_thread.start()
    
    # Wait for process to complete
    process.wait()
    
    exit_message = f'Process exited with code {process.returncode}'
    logger.info(f"Simulation {sim_id}: {exit_message}")
    
    # Write exit to log file
    with open(sim_log_file, 'a', encoding='utf-8') as log_file:
        log_file.write(f"[EXIT] {exit_message}\n")
    
    # Notify completion
    socketio.emit('terminal_output', {
        'sim_id': sim_id,
        'type': 'exit',
        'data': exit_message
    })
    
    # Cleanup
    if sim_id in RUNNING_PROCESSES:
        del RUNNING_PROCESSES[sim_id]


@app.route('/')
def serve_frontend():
    """Serve the main dashboard."""
    return send_from_directory(str(FRONTEND_DIR), 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files."""
    return send_from_directory(str(FRONTEND_DIR), path)


@app.route('/api/simulations', methods=['GET'])
def get_simulations():
    """Get list of available simulations."""
    global SIMULATIONS_REGISTRY
    SIMULATIONS_REGISTRY = discover_simulations()
    return jsonify({
        "status": "success",
        "simulations": list(SIMULATIONS_REGISTRY.values())
    })


@app.route('/api/simulations/<sim_id>/launch', methods=['POST'])
def launch_simulation(sim_id):
    """Launch a simulation's control panel."""
    global SIMULATIONS_REGISTRY
    
    if not SIMULATIONS_REGISTRY:
        SIMULATIONS_REGISTRY = discover_simulations()
    
    if sim_id not in SIMULATIONS_REGISTRY:
        logger.warning(f"Simulation not found: {sim_id}")
        return jsonify({
            "status": "error",
            "message": f"Simulation '{sim_id}' not found"
        }), 404
    
    sim = SIMULATIONS_REGISTRY[sim_id]
    sim_path = Path(sim["path"])
    
    # Determine which file to launch
    if sim["has_control_panel"]:
        launch_file = sim_path / "control_panel.py"
    elif sim["has_main"]:
        launch_file = sim_path / "main.py"
    else:
        logger.error(f"No launchable file for: {sim_id}")
        return jsonify({
            "status": "error",
            "message": "No launchable file found"
        }), 400
    
    # Check if embedded terminal is requested
    use_embedded = False
    try:
        data = request.get_json(silent=True) or {}
        use_embedded = data.get('embedded', False)
    except:
        pass
    
    try:
        logger.info(f"Launching simulation: {sim['name']} (embedded={use_embedded})")
        logger.info(f"Using Python: {PYTHON_EXECUTABLE}")
        
        if use_embedded:
            # Launch with output streaming using venv Python
            process = subprocess.Popen(
                [PYTHON_EXECUTABLE, '-u', str(launch_file)],  # -u for unbuffered output
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(sim_path)
            )
            
            RUNNING_PROCESSES[sim_id] = process
            
            # Start streaming thread
            stream_thread = threading.Thread(
                target=stream_process_output,
                args=(process, sim_id)
            )
            stream_thread.daemon = True
            stream_thread.start()
            
            socketio.emit('terminal_output', {
                'sim_id': sim_id,
                'type': 'start',
                'data': f'Starting {sim["name"]}...'
            })
        else:
            # Launch in a new window using venv Python
            if sys.platform == 'win32':
                subprocess.Popen(
                    [PYTHON_EXECUTABLE, str(launch_file)],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:
                subprocess.Popen([PYTHON_EXECUTABLE, str(launch_file)])
        
        return jsonify({
            "status": "success",
            "message": f"Launched {sim['name']}",
            "embedded": use_embedded
        })
    except Exception as e:
        logger.error(f"Error launching {sim_id}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/simulations/<sim_id>/stop', methods=['POST'])
def stop_simulation(sim_id):
    """Stop a running simulation."""
    if sim_id in RUNNING_PROCESSES:
        process = RUNNING_PROCESSES[sim_id]
        process.terminate()
        del RUNNING_PROCESSES[sim_id]
        logger.info(f"Stopped simulation: {sim_id}")
        return jsonify({
            "status": "success",
            "message": f"Stopped {sim_id}"
        })
    logger.warning(f"Tried to stop non-running simulation: {sim_id}")
    return jsonify({
        "status": "error",
        "message": "Simulation not running"
    }), 400


@app.route('/api/simulations/<sim_id>/info', methods=['GET'])
def get_simulation_info(sim_id):
    """Get detailed info about a simulation."""
    global SIMULATIONS_REGISTRY
    
    if not SIMULATIONS_REGISTRY:
        SIMULATIONS_REGISTRY = discover_simulations()
    
    if sim_id not in SIMULATIONS_REGISTRY:
        return jsonify({
            "status": "error",
            "message": f"Simulation '{sim_id}' not found"
        }), 404
    
    sim = SIMULATIONS_REGISTRY[sim_id]
    
    # Get frame counts if applicable
    frames_folder = Path(sim["path"]) / "frames"
    comparison_frames = Path(sim["path"]) / "comparison_frames"
    
    frame_count = len(list(frames_folder.glob("*.png"))) if frames_folder.exists() else 0
    comparison_count = len(list(comparison_frames.glob("*.png"))) if comparison_frames.exists() else 0
    
    return jsonify({
        "status": "success",
        "simulation": sim,
        "stats": {
            "frames": frame_count,
            "comparison_frames": comparison_count
        },
        "running": sim_id in RUNNING_PROCESSES
    })


@app.route('/api/system/info', methods=['GET'])
def get_system_info():
    """Get system information."""
    import platform
    
    return jsonify({
        "status": "success",
        "system": {
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "base_dir": str(BASE_DIR),
            "simulations_count": len(SIMULATIONS_REGISTRY) if SIMULATIONS_REGISTRY else 0
        }
    })


# ============================================
# VIDEO GENERATION ENDPOINTS
# ============================================

# Import video generator (lazy import to avoid circular imports)
video_generator = None

def get_video_generator():
    """Get or create the video generator instance."""
    global video_generator
    if video_generator is None:
        from shared.video_generator import VideoGenerator
        video_generator = VideoGenerator()
    return video_generator


@app.route('/api/video/generate', methods=['POST'])
def generate_video_endpoint():
    """
    Generate a video from frame folder(s).
    
    Request body:
    {
        "frame_folders": ["path/to/frames"],  # Required: list of frame folder paths
        "output_name": "my_video",            # Optional: output video name
        "fps": 60,                            # Optional: frames per second
        "quality": "high"                     # Optional: low/medium/high/ultra/lossless
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'frame_folders' not in data:
            return jsonify({
                "status": "error",
                "message": "Missing required field: frame_folders"
            }), 400
        
        frame_folders = data.get('frame_folders', [])
        output_name = data.get('output_name')
        fps = data.get('fps', 60)
        quality = data.get('quality', 'high')
        
        if not frame_folders:
            return jsonify({
                "status": "error",
                "message": "frame_folders cannot be empty"
            }), 400
        
        generator = get_video_generator()
        
        logger.info(f"Video generation request: {len(frame_folders)} folder(s), fps={fps}, quality={quality}")
        
        if len(frame_folders) == 1:
            # Single folder
            output_path = generator.generate_video(
                frame_folder=frame_folders[0],
                output_name=output_name,
                fps=fps,
                quality=quality
            )
        else:
            # Multiple folders - combine
            if not output_name:
                output_name = f"combined_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            output_path = generator.generate_from_multiple_folders(
                frame_folders=frame_folders,
                output_name=output_name,
                fps=fps,
                quality=quality
            )
        
        return jsonify({
            "status": "success",
            "message": "Video generated successfully",
            "video": {
                "path": str(output_path),
                "name": output_path.name,
                "size_mb": output_path.stat().st_size / (1024 * 1024)
            }
        })
        
    except Exception as e:
        logger.error(f"Video generation failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/video/list', methods=['GET'])
def list_videos():
    """List all generated videos."""
    try:
        generator = get_video_generator()
        videos = generator.list_output_videos()
        
        return jsonify({
            "status": "success",
            "videos": videos,
            "count": len(videos)
        })
    except Exception as e:
        logger.error(f"Error listing videos: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/video/stream/<path:video_name>', methods=['GET'])
def stream_video(video_name):
    """Stream a video file."""
    try:
        output_dir = BASE_DIR / "output" / "videos"
        video_path = output_dir / video_name
        
        if not video_path.exists():
            return jsonify({
                "status": "error",
                "message": "Video not found"
            }), 404
        
        # Use Flask's send_file for video streaming
        from flask import send_file, Response
        
        # Get file size for Content-Length header
        file_size = video_path.stat().st_size
        
        # Check for Range header for seeking support
        range_header = request.headers.get('Range', None)
        
        if range_header:
            # Parse range header
            byte_start = 0
            byte_end = file_size - 1
            
            match = range_header.replace('bytes=', '').split('-')
            if match[0]:
                byte_start = int(match[0])
            if match[1]:
                byte_end = int(match[1])
            
            length = byte_end - byte_start + 1
            
            def generate():
                with open(video_path, 'rb') as f:
                    f.seek(byte_start)
                    remaining = length
                    while remaining > 0:
                        chunk_size = min(8192, remaining)
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        remaining -= len(chunk)
                        yield chunk
            
            response = Response(
                generate(),
                status=206,
                mimetype='video/mp4',
                headers={
                    'Content-Range': f'bytes {byte_start}-{byte_end}/{file_size}',
                    'Accept-Ranges': 'bytes',
                    'Content-Length': str(length),
                    'Content-Disposition': f'inline; filename="{video_name}"'
                }
            )
            return response
        else:
            # Full file response
            return send_file(
                video_path,
                mimetype='video/mp4',
                as_attachment=False,
                download_name=video_name
            )
    except Exception as e:
        logger.error(f"Error streaming video {video_name}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/video/open-folder', methods=['POST'])
def open_video_folder():
    """Open the folder containing a video file."""
    try:
        data = request.get_json(silent=True) or {}
        video_name = data.get('video_name')
        
        output_dir = BASE_DIR / "output" / "videos"
        
        if video_name:
            video_path = output_dir / video_name
            if video_path.exists():
                # Open folder and select file
                if sys.platform == 'win32':
                    subprocess.Popen(['explorer', '/select,', str(video_path)])
                elif sys.platform == 'darwin':
                    subprocess.Popen(['open', '-R', str(video_path)])
                else:
                    subprocess.Popen(['xdg-open', str(output_dir)])
            else:
                # Just open the output folder
                if sys.platform == 'win32':
                    subprocess.Popen(['explorer', str(output_dir)])
                elif sys.platform == 'darwin':
                    subprocess.Popen(['open', str(output_dir)])
                else:
                    subprocess.Popen(['xdg-open', str(output_dir)])
        else:
            # Open the videos folder
            if sys.platform == 'win32':
                subprocess.Popen(['explorer', str(output_dir)])
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', str(output_dir)])
            else:
                subprocess.Popen(['xdg-open', str(output_dir)])
        
        return jsonify({
            "status": "success",
            "message": "Folder opened"
        })
    except Exception as e:
        logger.error(f"Error opening video folder: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/video/thumbnail/<path:video_name>', methods=['GET'])
def get_video_thumbnail(video_name):
    """Get thumbnail image for a video (extracts 5th frame)."""
    try:
        from flask import send_file
        from shared.video_generator import VideoGenerator
        
        # Initialize video generator
        generator = VideoGenerator(output_dir=BASE_DIR / "output" / "videos")
        
        # Generate or get cached thumbnail
        thumb_path = generator.generate_thumbnail(video_name, frame_number=5)
        
        if thumb_path and thumb_path.exists():
            return send_file(
                thumb_path,
                mimetype='image/jpeg',
                as_attachment=False,
                download_name=thumb_path.name
            )
        else:
            # Return a default placeholder (404)
            return jsonify({
                "status": "error",
                "message": "Could not generate thumbnail"
            }), 404
            
    except Exception as e:
        logger.error(f"Error getting thumbnail for {video_name}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/simulations/<sim_id>/frames', methods=['GET'])
def get_simulation_frames(sim_id):
    """Get list of frame folders for a simulation."""
    global SIMULATIONS_REGISTRY
    
    if not SIMULATIONS_REGISTRY:
        SIMULATIONS_REGISTRY = discover_simulations()
    
    if sim_id not in SIMULATIONS_REGISTRY:
        return jsonify({
            "status": "error",
            "message": f"Simulation '{sim_id}' not found"
        }), 404
    
    sim = SIMULATIONS_REGISTRY[sim_id]
    sim_path = Path(sim["path"])
    
    # Find all frame folders (directories containing images)
    frame_folders = []
    
    for item in sim_path.iterdir():
        if item.is_dir() and not item.name.startswith('__'):
            # Check if it contains image files
            has_images = any(
                item.glob(f'*{ext}') 
                for ext in ['.png', '.jpg', '.jpeg', '.bmp']
            )
            if has_images:
                # Count frames
                frame_count = sum(
                    len(list(item.glob(f'*{ext}'))) 
                    for ext in ['.png', '.jpg', '.jpeg', '.bmp']
                )
                frame_folders.append({
                    "name": item.name,
                    "path": str(item),
                    "frame_count": frame_count
                })
    
    return jsonify({
        "status": "success",
        "simulation": sim["name"],
        "frame_folders": frame_folders
    })


# ============================================
# ADD-ON MANAGEMENT ENDPOINTS
# ============================================

@app.route('/api/addon/list', methods=['GET'])
def list_addons():
    """List all installed add-ons."""
    try:
        manager = get_addon_manager()
        addons = manager.list_addons()
        
        return jsonify({
            "status": "success",
            "addons": addons,
            "count": len(addons)
        })
    except Exception as e:
        logger.error(f"Error listing add-ons: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/addon/upload', methods=['POST'])
def upload_addon():
    """Upload and install a new add-on from ZIP file."""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                "status": "error",
                "message": "No file provided"
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                "status": "error",
                "message": "Empty filename"
            }), 400
        
        if not file.filename.endswith('.zip'):
            return jsonify({
                "status": "error",
                "message": "File must be a ZIP archive"
            }), 400
        
        # Save the uploaded file
        manager = get_addon_manager()
        upload_path = manager.uploads_dir / file.filename
        file.save(upload_path)
        
        logger.info(f"Uploaded add-on file: {file.filename}")
        
        # Install the add-on
        success, message, addon_data = manager.install_addon(upload_path)
        
        # Clean up the uploaded file
        if upload_path.exists():
            upload_path.unlink()
        
        if success:
            # Refresh simulations registry
            global SIMULATIONS_REGISTRY
            SIMULATIONS_REGISTRY = discover_simulations()
            
            return jsonify({
                "status": "success",
                "message": message,
                "addon": addon_data
            })
        else:
            return jsonify({
                "status": "error",
                "message": message
            }), 400
            
    except Exception as e:
        logger.error(f"Error uploading add-on: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/addon/<addon_id>', methods=['GET'])
def get_addon(addon_id):
    """Get details of a specific add-on."""
    try:
        manager = get_addon_manager()
        addon = manager.get_addon(addon_id)
        
        if addon:
            return jsonify({
                "status": "success",
                "addon": addon
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"Add-on '{addon_id}' not found"
            }), 404
    except Exception as e:
        logger.error(f"Error getting add-on {addon_id}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/addon/<addon_id>', methods=['DELETE'])
def delete_addon(addon_id):
    """Uninstall an add-on completely."""
    try:
        manager = get_addon_manager()
        success, message, stats = manager.uninstall_addon(addon_id)
        
        if success:
            # Refresh simulations registry
            global SIMULATIONS_REGISTRY
            SIMULATIONS_REGISTRY = discover_simulations()
            
            return jsonify({
                "status": "success",
                "message": message,
                "removed": stats
            })
        else:
            return jsonify({
                "status": "error",
                "message": message
            }), 400
    except Exception as e:
        logger.error(f"Error deleting add-on {addon_id}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/addon/<addon_id>/enable', methods=['POST'])
def enable_addon(addon_id):
    """Enable a disabled add-on."""
    try:
        manager = get_addon_manager()
        success, message = manager.enable_addon(addon_id)
        
        if success:
            # Refresh simulations registry
            global SIMULATIONS_REGISTRY
            SIMULATIONS_REGISTRY = discover_simulations()
            
            return jsonify({
                "status": "success",
                "message": message
            })
        else:
            return jsonify({
                "status": "error",
                "message": message
            }), 400
    except Exception as e:
        logger.error(f"Error enabling add-on {addon_id}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/addon/<addon_id>/disable', methods=['POST'])
def disable_addon(addon_id):
    """Disable an add-on without removing it."""
    try:
        manager = get_addon_manager()
        success, message = manager.disable_addon(addon_id)
        
        if success:
            # Refresh simulations registry
            global SIMULATIONS_REGISTRY
            SIMULATIONS_REGISTRY = discover_simulations()
            
            return jsonify({
                "status": "success",
                "message": message
            })
        else:
            return jsonify({
                "status": "error",
                "message": message
            }), 400
    except Exception as e:
        logger.error(f"Error disabling add-on {addon_id}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/addon/<addon_id>/export', methods=['GET'])
def export_addon(addon_id):
    """Export an add-on as a ZIP file."""
    try:
        from flask import send_file
        
        manager = get_addon_manager()
        success, message, zip_path = manager.export_addon(addon_id)
        
        if success and zip_path and zip_path.exists():
            return send_file(
                zip_path,
                mimetype='application/zip',
                as_attachment=True,
                download_name=f"{addon_id}.zip"
            )
        else:
            return jsonify({
                "status": "error",
                "message": message
            }), 400
    except Exception as e:
        logger.error(f"Error exporting add-on {addon_id}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# WebSocket Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    logger.info("Client connected via WebSocket")


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.info("Client disconnected from WebSocket")


def main():
    """Start the backend server."""
    print("=" * 50)
    print("🚀 Loops Visualization System - Backend Server")
    print("=" * 50)
    print(f"📁 Base Directory: {BASE_DIR}")
    print(f"🌐 Frontend: {FRONTEND_DIR}")
    print(f"🎮 Simulations: {SIMULATIONS_DIR}")
    print(f"📝 Logs: {LOGS_DIR}")
    print(f"🐍 Python: {PYTHON_EXECUTABLE}")
    print("-" * 50)
    
    logger.info("=" * 50)
    logger.info("Loops Visualization System - Starting")
    logger.info(f"Base Directory: {BASE_DIR}")
    logger.info(f"Using Python: {PYTHON_EXECUTABLE}")
    
    # Discover simulations on startup
    global SIMULATIONS_REGISTRY
    SIMULATIONS_REGISTRY = discover_simulations()
    print(f"📊 Found {len(SIMULATIONS_REGISTRY)} simulation(s):")
    logger.info(f"Found {len(SIMULATIONS_REGISTRY)} simulation(s)")
    for sim_id, sim in SIMULATIONS_REGISTRY.items():
        print(f"   {sim['icon']} {sim['name']}")
        logger.info(f"  - {sim['name']} ({sim_id})")
    
    print("-" * 50)
    print("🌐 Server starting on http://127.0.0.1:5000")
    print("📡 WebSocket enabled for terminal streaming")
    print("   Press Ctrl+C to stop")
    print("=" * 50)
    logger.info("Server starting on http://127.0.0.1:5000")
    
    socketio.run(app, host='127.0.0.1', port=5000, debug=True, use_reloader=False)


if __name__ == "__main__":
    main()
