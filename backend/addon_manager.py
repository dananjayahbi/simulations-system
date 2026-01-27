#!/usr/bin/env python3
"""
Add-on Manager Service
======================
Handles installation, validation, and management of simulation add-ons.
"""

import json
import shutil
import zipfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AddonManager:
    """Manages simulation add-ons lifecycle."""
    
    def __init__(self, base_dir: Path = None):
        """Initialize the add-on manager.
        
        Args:
            base_dir: Base directory of the Loops system (default: auto-detect)
        """
        if base_dir is None:
            # Auto-detect base directory (parent of backend)
            self.base_dir = Path(__file__).resolve().parent.parent
        else:
            self.base_dir = Path(base_dir)
            
        self.simulations_dir = self.base_dir / "simulations"
        self.uploads_dir = self.base_dir / "uploads"
        self.output_dir = self.base_dir / "output"
        self.registry_file = self.base_dir / "addons.json"
        
        # Create necessary directories
        self.uploads_dir.mkdir(exist_ok=True)
        self.simulations_dir.mkdir(exist_ok=True)
        (self.output_dir / "frames").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "videos").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "thumbnails").mkdir(parents=True, exist_ok=True)
        
        # Initialize registry
        self._init_registry()
        
    def _init_registry(self):
        """Initialize the add-on registry file."""
        if not self.registry_file.exists():
            self._save_registry({
                "version": "1.0.0",
                "addons": {},
                "last_updated": datetime.now().isoformat()
            })
            
    def _load_registry(self) -> Dict:
        """Load the add-on registry."""
        try:
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
            return {"version": "1.0.0", "addons": {}}
            
    def _save_registry(self, registry: Dict):
        """Save the add-on registry."""
        registry["last_updated"] = datetime.now().isoformat()
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2)
            
    def list_addons(self) -> List[Dict]:
        """List all installed add-ons.
        
        Returns:
            List of add-on metadata dictionaries
        """
        registry = self._load_registry()
        addons = []
        
        for addon_id, addon_data in registry.get("addons", {}).items():
            # Verify the add-on still exists
            addon_dir = self.simulations_dir / addon_id
            if addon_dir.exists():
                addons.append(addon_data)
            else:
                logger.warning(f"Add-on {addon_id} in registry but folder missing")
                
        return addons
    
    def get_addon(self, addon_id: str) -> Optional[Dict]:
        """Get details of a specific add-on.
        
        Args:
            addon_id: Unique identifier of the add-on
            
        Returns:
            Add-on metadata dictionary or None if not found
        """
        registry = self._load_registry()
        return registry.get("addons", {}).get(addon_id)
    
    def validate_addon_structure(self, addon_path: Path) -> Tuple[bool, List[str]]:
        """Validate add-on directory structure.
        
        Args:
            addon_path: Path to the add-on directory
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check if directory exists
        if not addon_path.exists():
            errors.append("Add-on directory does not exist")
            return False, errors
            
        # Check required files
        required_files = ["simulation.json", "main.py", "__init__.py"]
        for filename in required_files:
            if not (addon_path / filename).exists():
                errors.append(f"Required file missing: {filename}")
                
        # Validate simulation.json
        simulation_json = addon_path / "simulation.json"
        if simulation_json.exists():
            try:
                with open(simulation_json, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                # Check required fields
                required_fields = ["id", "name", "description", "icon", "color", "version", "author"]
                for field in required_fields:
                    if field not in config:
                        errors.append(f"Required field missing in simulation.json: {field}")
                        
                # Validate id matches directory name
                if "id" in config and config["id"] != addon_path.name:
                    errors.append(f"Add-on ID '{config['id']}' does not match directory name '{addon_path.name}'")
                    
            except json.JSONDecodeError as e:
                errors.append(f"Invalid JSON in simulation.json: {e}")
            except Exception as e:
                errors.append(f"Error reading simulation.json: {e}")
                
        # Check for path traversal attempts
        for item in addon_path.rglob("*"):
            try:
                item.relative_to(addon_path)
            except ValueError:
                errors.append(f"Path traversal detected: {item}")
                
        return len(errors) == 0, errors
    
    def install_addon(self, zip_path: Path) -> Tuple[bool, str, Optional[Dict]]:
        """Install an add-on from a ZIP file.
        
        Args:
            zip_path: Path to the ZIP file
            
        Returns:
            Tuple of (success, message, addon_metadata)
        """
        try:
            # Extract to temporary directory
            temp_dir = self.uploads_dir / f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            temp_dir.mkdir(exist_ok=True)
            
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    # Security check: validate file paths
                    for filename in zip_ref.namelist():
                        if filename.startswith('/') or '..' in filename:
                            return False, "Invalid ZIP: path traversal detected", None
                    
                    zip_ref.extractall(temp_dir)
                    
            except zipfile.BadZipFile:
                return False, "Invalid ZIP file", None
                
            # Find the add-on directory (should be the only top-level directory)
            addon_dirs = [d for d in temp_dir.iterdir() if d.is_dir()]
            if len(addon_dirs) != 1:
                shutil.rmtree(temp_dir)
                return False, "ZIP must contain exactly one top-level directory", None
                
            addon_temp_path = addon_dirs[0]
            
            # Validate structure
            is_valid, errors = self.validate_addon_structure(addon_temp_path)
            if not is_valid:
                shutil.rmtree(temp_dir)
                return False, f"Validation failed: {'; '.join(errors)}", None
                
            # Load metadata
            with open(addon_temp_path / "simulation.json", 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                
            addon_id = metadata["id"]
            addon_dest = self.simulations_dir / addon_id
            
            # Check if already installed
            if addon_dest.exists():
                shutil.rmtree(temp_dir)
                return False, f"Add-on '{addon_id}' is already installed", None
                
            # Copy to simulations directory
            shutil.copytree(addon_temp_path, addon_dest)
            
            # Create output directories
            (self.output_dir / "frames" / addon_id).mkdir(parents=True, exist_ok=True)
            (self.output_dir / "videos" / addon_id).mkdir(parents=True, exist_ok=True)
            
            # Update registry
            registry = self._load_registry()
            registry["addons"][addon_id] = {
                **metadata,
                "installed_at": datetime.now().isoformat(),
                "enabled": True,
                "builtin": False
            }
            self._save_registry(registry)
            
            # Cleanup
            shutil.rmtree(temp_dir)
            
            logger.info(f"Add-on '{addon_id}' installed successfully")
            return True, "Add-on installed successfully", registry["addons"][addon_id]
            
        except Exception as e:
            logger.error(f"Installation failed: {e}")
            return False, f"Installation error: {str(e)}", None
    
    def uninstall_addon(self, addon_id: str) -> Tuple[bool, str, Dict]:
        """Uninstall an add-on completely.
        
        Args:
            addon_id: Unique identifier of the add-on
            
        Returns:
            Tuple of (success, message, removal_stats)
        """
        stats = {
            "simulation_folder": False,
            "frames": 0,
            "videos": 0,
            "thumbnails": 0
        }
        
        try:
            # Check if exists
            addon_dir = self.simulations_dir / addon_id
            if not addon_dir.exists():
                return False, f"Add-on '{addon_id}' not found", stats
                
            # Check if it's a built-in addon
            registry = self._load_registry()
            addon_data = registry.get("addons", {}).get(addon_id, {})
            if addon_data.get("builtin", False):
                return False, f"Cannot uninstall built-in add-on '{addon_id}'", stats
                
            # Remove simulation folder
            shutil.rmtree(addon_dir)
            stats["simulation_folder"] = True
            
            # Remove frames
            frames_dir = self.output_dir / "frames" / addon_id
            if frames_dir.exists():
                stats["frames"] = len(list(frames_dir.glob("*.png")))
                shutil.rmtree(frames_dir)
                
            # Remove videos
            videos_dir = self.output_dir / "videos" / addon_id
            if videos_dir.exists():
                stats["videos"] = len(list(videos_dir.glob("*.mp4")))
                shutil.rmtree(videos_dir)
                
            # Remove thumbnails
            thumbnails_dir = self.output_dir / "thumbnails"
            if thumbnails_dir.exists():
                for thumb in thumbnails_dir.glob(f"{addon_id}_*.png"):
                    thumb.unlink()
                    stats["thumbnails"] += 1
                    
            # Remove from registry
            if addon_id in registry["addons"]:
                del registry["addons"][addon_id]
                self._save_registry(registry)
                
            logger.info(f"Add-on '{addon_id}' uninstalled successfully")
            return True, "Add-on removed completely", stats
            
        except Exception as e:
            logger.error(f"Uninstallation failed: {e}")
            return False, f"Uninstallation error: {str(e)}", stats
    
    def enable_addon(self, addon_id: str) -> Tuple[bool, str]:
        """Enable a disabled add-on.
        
        Args:
            addon_id: Unique identifier of the add-on
            
        Returns:
            Tuple of (success, message)
        """
        registry = self._load_registry()
        
        if addon_id not in registry["addons"]:
            return False, f"Add-on '{addon_id}' not found"
            
        registry["addons"][addon_id]["enabled"] = True
        self._save_registry(registry)
        
        return True, f"Add-on '{addon_id}' enabled"
    
    def disable_addon(self, addon_id: str) -> Tuple[bool, str]:
        """Disable an add-on without removing it.
        
        Args:
            addon_id: Unique identifier of the add-on
            
        Returns:
            Tuple of (success, message)
        """
        registry = self._load_registry()
        
        if addon_id not in registry["addons"]:
            return False, f"Add-on '{addon_id}' not found"
            
        registry["addons"][addon_id]["enabled"] = False
        self._save_registry(registry)
        
        return True, f"Add-on '{addon_id}' disabled"
    
    def export_addon(self, addon_id: str, output_path: Path = None) -> Tuple[bool, str, Optional[Path]]:
        """Export an add-on as a ZIP file.
        
        Args:
            addon_id: Unique identifier of the add-on
            output_path: Optional custom output path
            
        Returns:
            Tuple of (success, message, zip_path)
        """
        try:
            addon_dir = self.simulations_dir / addon_id
            if not addon_dir.exists():
                return False, f"Add-on '{addon_id}' not found", None
                
            if output_path is None:
                output_path = self.uploads_dir / f"{addon_id}.zip"
                
            # Create ZIP
            shutil.make_archive(
                str(output_path.with_suffix('')),
                'zip',
                self.simulations_dir,
                addon_id
            )
            
            return True, f"Add-on exported successfully", output_path
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False, f"Export error: {str(e)}", None
    
    def scan_and_register_builtin(self):
        """Scan simulations directory and register built-in add-ons."""
        registry = self._load_registry()
        
        for addon_dir in self.simulations_dir.iterdir():
            if not addon_dir.is_dir():
                continue
                
            addon_id = addon_dir.name
            simulation_json = addon_dir / "simulation.json"
            
            # Skip if not a valid add-on
            if not simulation_json.exists():
                continue
                
            # Skip if already registered
            if addon_id in registry["addons"]:
                continue
                
            try:
                with open(simulation_json, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    
                # Register as built-in
                registry["addons"][addon_id] = {
                    **metadata,
                    "installed_at": datetime.now().isoformat(),
                    "enabled": True,
                    "builtin": True
                }
                
                logger.info(f"Registered built-in add-on: {addon_id}")
                
            except Exception as e:
                logger.error(f"Failed to register {addon_id}: {e}")
                
        self._save_registry(registry)


# Utility functions for standalone use
def main():
    """CLI interface for add-on manager."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Loops Add-on Manager')
    parser.add_argument('command', choices=['list', 'install', 'uninstall', 'enable', 'disable', 'export', 'scan'])
    parser.add_argument('--addon-id', help='Add-on ID')
    parser.add_argument('--zip-path', help='Path to ZIP file')
    parser.add_argument('--output', help='Output path for export')
    
    args = parser.parse_args()
    
    manager = AddonManager()
    
    if args.command == 'list':
        addons = manager.list_addons()
        print(f"\n{'ID':<20} {'Name':<30} {'Version':<10} {'Enabled':<10}")
        print("-" * 70)
        for addon in addons:
            print(f"{addon['id']:<20} {addon['name']:<30} {addon['version']:<10} {'✓' if addon['enabled'] else '✗':<10}")
            
    elif args.command == 'install':
        if not args.zip_path:
            print("Error: --zip-path required")
            return
        success, message, _ = manager.install_addon(Path(args.zip_path))
        print(message)
        
    elif args.command == 'uninstall':
        if not args.addon_id:
            print("Error: --addon-id required")
            return
        success, message, stats = manager.uninstall_addon(args.addon_id)
        print(message)
        if success:
            print(f"Removed: {stats}")
            
    elif args.command == 'enable':
        if not args.addon_id:
            print("Error: --addon-id required")
            return
        success, message = manager.enable_addon(args.addon_id)
        print(message)
        
    elif args.command == 'disable':
        if not args.addon_id:
            print("Error: --addon-id required")
            return
        success, message = manager.disable_addon(args.addon_id)
        print(message)
        
    elif args.command == 'export':
        if not args.addon_id:
            print("Error: --addon-id required")
            return
        output = Path(args.output) if args.output else None
        success, message, path = manager.export_addon(args.addon_id, output)
        print(message)
        if success:
            print(f"Exported to: {path}")
            
    elif args.command == 'scan':
        manager.scan_and_register_builtin()
        print("Built-in add-ons scanned and registered")


if __name__ == "__main__":
    main()
