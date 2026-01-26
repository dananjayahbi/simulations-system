#!/usr/bin/env python3
# server.py - Backend server for Loops Visualization System

"""
Loops Backend Server
====================
A Flask-based backend server that:
- Serves the frontend dashboard
- Provides API endpoints for simulation management
- Launches micro app control panels
"""

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import os
import sys
import subprocess
import json
from pathlib import Path

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
SIMULATIONS_DIR = BASE_DIR / "simulations"

# Add base dir to path for imports
sys.path.insert(0, str(BASE_DIR))

app = Flask(__name__, static_folder=str(FRONTEND_DIR))
CORS(app)

# Registry of available simulations
SIMULATIONS_REGISTRY = {}


def discover_simulations():
    """Discover all available simulations in the simulations folder."""
    simulations = {}
    
    if not SIMULATIONS_DIR.exists():
        return simulations
    
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
                
                simulations[item.name] = metadata
    
    return simulations


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
        return jsonify({
            "status": "error",
            "message": "No launchable file found"
        }), 400
    
    try:
        # Launch in a new process (non-blocking)
        if sys.platform == 'win32':
            # Windows: Use pythonw for GUI apps to avoid console
            subprocess.Popen(
                [sys.executable, str(launch_file)],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            subprocess.Popen([sys.executable, str(launch_file)])
        
        return jsonify({
            "status": "success",
            "message": f"Launched {sim['name']}"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


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
        }
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


def main():
    """Start the backend server."""
    print("=" * 50)
    print("🚀 Loops Visualization System - Backend Server")
    print("=" * 50)
    print(f"📁 Base Directory: {BASE_DIR}")
    print(f"🌐 Frontend: {FRONTEND_DIR}")
    print(f"🎮 Simulations: {SIMULATIONS_DIR}")
    print("-" * 50)
    
    # Discover simulations on startup
    global SIMULATIONS_REGISTRY
    SIMULATIONS_REGISTRY = discover_simulations()
    print(f"📊 Found {len(SIMULATIONS_REGISTRY)} simulation(s):")
    for sim_id, sim in SIMULATIONS_REGISTRY.items():
        print(f"   {sim['icon']} {sim['name']}")
    
    print("-" * 50)
    print("🌐 Server starting on http://127.0.0.1:5000")
    print("   Press Ctrl+C to stop")
    print("=" * 50)
    
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)


if __name__ == "__main__":
    main()
