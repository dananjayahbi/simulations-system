#!/usr/bin/env python3
"""
Test Video Generation
=====================
Tests to verify video generation works correctly for sorting_circles plugin.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared.video_generator import VideoGenerator


def test_video_generator_import():
    """Test 1: VideoGenerator can be imported"""
    print("Test 1: VideoGenerator Import")
    try:
        from shared.video_generator import VideoGenerator
        print("✅ PASS: VideoGenerator imported successfully")
        return True
    except ImportError as e:
        print(f"❌ FAIL: Cannot import VideoGenerator: {e}")
        return False


def test_video_generator_instantiation():
    """Test 2: VideoGenerator can be instantiated"""
    print("\nTest 2: VideoGenerator Instantiation")
    try:
        generator = VideoGenerator()
        print(f"✅ PASS: VideoGenerator instantiated: {generator}")
        return True
    except Exception as e:
        print(f"❌ FAIL: Cannot instantiate VideoGenerator: {e}")
        return False


def test_sorting_circles_frames_directory():
    """Test 3: sorting_circles frames directory exists"""
    print("\nTest 3: Frames Directory Check")
    frames_dir = Path(__file__).resolve().parent.parent / "simulations" / "sorting_circles" / "frames"
    print(f"Checking: {frames_dir}")
    
    if not frames_dir.exists():
        print(f"❌ FAIL: Frames directory does not exist")
        print(f"   Create it by running sorting_circles and pressing 's' to record")
        return False
    
    frame_files = list(frames_dir.glob("frame_*.png"))
    if not frame_files:
        print(f"❌ FAIL: Frames directory exists but is empty")
        print(f"   Run sorting_circles simulation and press 's' to record frames")
        return False
    
    print(f"✅ PASS: Frames directory exists with {len(frame_files)} frames")
    return True


def test_video_generation_with_sorting_circles_frames():
    """Test 4: Generate video from sorting_circles frames"""
    print("\nTest 4: Video Generation from Frames")
    
    frames_dir = Path(__file__).resolve().parent.parent / "simulations" / "sorting_circles" / "frames"
    
    if not frames_dir.exists() or not list(frames_dir.glob("frame_*.png")):
        print("⚠️  SKIP: No frames available (run Test 3 first)")
        return None
    
    try:
        from datetime import datetime
        
        generator = VideoGenerator()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_name = f"test_sorting_circles_{timestamp}"
        
        print(f"Generating video: {output_name}")
        print(f"Frame folder: {frames_dir}")
        print(f"FPS: 60")
        print(f"Quality: high")
        
        output_path = generator.generate_video(
            frame_folder=str(frames_dir.absolute()),
            output_name=output_name,
            fps=60,
            quality='high'
        )
        
        output_file = Path(output_path)
        if output_file.exists():
            file_size = output_file.stat().st_size
            print(f"✅ PASS: Video generated successfully")
            print(f"   Path: {output_path}")
            print(f"   Size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")
            return True
        else:
            print(f"❌ FAIL: Video file was not created at {output_path}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Video generation failed with error:")
        print(f"   {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_video_generator_parameters():
    """Test 5: VideoGenerator with different parameters"""
    print("\nTest 5: VideoGenerator Parameter Validation")
    
    frames_dir = Path(__file__).resolve().parent.parent / "simulations" / "sorting_circles" / "frames"
    
    if not frames_dir.exists() or not list(frames_dir.glob("frame_*.png")):
        print("⚠️  SKIP: No frames available")
        return None
    
    test_cases = [
        {"name": "Low FPS", "fps": 30, "quality": "low"},
        {"name": "High FPS", "fps": 120, "quality": "medium"},
        {"name": "Ultra Quality", "fps": 60, "quality": "ultra"},
    ]
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        try:
            from datetime import datetime
            generator = VideoGenerator()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_name = f"test_{test_case['name'].replace(' ', '_').lower()}_{timestamp}"
            
            output_path = generator.generate_video(
                frame_folder=str(frames_dir.absolute()),
                output_name=output_name,
                fps=test_case['fps'],
                quality=test_case['quality']
            )
            
            if Path(output_path).exists():
                print(f"  ✅ {test_case['name']}: PASS (fps={test_case['fps']}, quality={test_case['quality']})")
                passed += 1
            else:
                print(f"  ❌ {test_case['name']}: FAIL (file not created)")
                failed += 1
        except Exception as e:
            print(f"  ❌ {test_case['name']}: FAIL ({type(e).__name__}: {str(e)})")
            failed += 1
    
    if failed == 0:
        print(f"✅ PASS: All {passed} parameter tests passed")
        return True
    else:
        print(f"❌ FAIL: {failed} of {passed + failed} tests failed")
        return False


def test_control_panel_can_import_video_generator():
    """Test 6: sorting_circles control_panel.py can import VideoGenerator"""
    print("\nTest 6: Control Panel Import Check")
    
    control_panel_file = Path(__file__).resolve().parent.parent / "simulations" / "sorting_circles" / "control_panel.py"
    
    if not control_panel_file.exists():
        print(f"❌ FAIL: control_panel.py not found at {control_panel_file}")
        return False
    
    # Read the file and check for VideoGenerator import
    content = control_panel_file.read_text(encoding='utf-8')
    
    if "from shared.video_generator import VideoGenerator" in content:
        print("✅ PASS: control_panel.py imports VideoGenerator correctly")
    else:
        print("❌ FAIL: control_panel.py does NOT import VideoGenerator")
        print("   Expected: 'from shared.video_generator import VideoGenerator'")
        return False
    
    # Check that requests is NOT imported
    if "import requests" in content:
        print("⚠️  WARNING: control_panel.py still imports 'requests' (not needed)")
    else:
        print("✅ PASS: control_panel.py does NOT import 'requests'")
    
    # Check for API endpoint usage (should not exist)
    if "requests.post" in content or "/api/video/generate" in content or "/api/generate-video" in content:
        print("❌ FAIL: control_panel.py still uses HTTP API (should use VideoGenerator directly)")
        return False
    else:
        print("✅ PASS: control_panel.py does NOT use HTTP API")
    
    return True


def run_all_tests():
    """Run all tests and report results"""
    print("="*70)
    print("Video Generation Test Suite for sorting_circles")
    print("="*70)
    
    tests = [
        test_video_generator_import,
        test_video_generator_instantiation,
        test_sorting_circles_frames_directory,
        test_video_generation_with_sorting_circles_frames,
        test_video_generator_parameters,
        test_control_panel_can_import_video_generator,
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)
    
    passed = sum(1 for r in results if r is True)
    failed = sum(1 for r in results if r is False)
    skipped = sum(1 for r in results if r is None)
    total = len(results)
    
    print(f"✅ Passed:  {passed}/{total}")
    print(f"❌ Failed:  {failed}/{total}")
    print(f"⚠️  Skipped: {skipped}/{total}")
    
    if failed == 0 and skipped == 0:
        print("\n🎉 ALL TESTS PASSED! Video generation is working correctly!")
        return 0
    elif failed == 0:
        print("\n⚠️  All tests passed, but some were skipped (need frames)")
        print("   Run sorting_circles simulation and press 's' to record frames")
        return 1
    else:
        print("\n❌ SOME TESTS FAILED! Video generation needs fixing.")
        return 2


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
