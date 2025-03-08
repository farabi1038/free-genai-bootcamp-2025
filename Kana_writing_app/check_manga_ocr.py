#!/usr/bin/env python3
"""
MangaOCR Integration Helper for Kana Writing Practice

This script helps check if MangaOCR is properly installed and
pre-downloads the required models for offline use.
"""

import os
import sys
import platform
import importlib.util
import subprocess
from pathlib import Path
import time

def check_manga_ocr_installed():
    """Check if MangaOCR is installed"""
    return importlib.util.find_spec("manga_ocr") is not None

def estimate_disk_space():
    """Estimate disk space required for MangaOCR"""
    # Model is approximately 160MB, but account for dependencies
    return 200  # MB

def check_available_disk_space(directory):
    """Check available disk space in MB"""
    if platform.system() == "Windows":
        import ctypes
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(
            ctypes.c_wchar_p(directory), None, None, 
            ctypes.pointer(free_bytes)
        )
        return free_bytes.value / (1024 * 1024)
    else:
        import shutil
        return shutil.disk_usage(directory).free / (1024 * 1024)

def get_cache_dir():
    """Get the MangaOCR cache directory"""
    if platform.system() == "Windows":
        cache_dir = os.path.expanduser("~\\.cache\\manga_ocr")
    else:
        cache_dir = os.path.expanduser("~/.cache/manga_ocr")
    return cache_dir

def download_manga_ocr_models():
    """Download MangaOCR models for offline use"""
    try:
        print("Initializing MangaOCR. This will download models if needed...")
        
        # Import here to trigger the download
        from manga_ocr import MangaOcr
        
        # Initialize to download models
        print("Downloading models (this may take a few minutes)...")
        start_time = time.time()
        mocr = MangaOcr()
        end_time = time.time()
        
        print(f"✅ MangaOCR initialized successfully in {end_time - start_time:.1f} seconds")
        
        # Test with a small image
        test_image_path = create_test_image()
        if test_image_path:
            print("Testing MangaOCR with a sample image...")
            result = mocr(test_image_path)
            print(f"Test recognition result: {result}")
            os.unlink(test_image_path)
        
        return True
    except Exception as e:
        print(f"Error downloading MangaOCR models: {str(e)}")
        return False

def create_test_image():
    """Create a simple test image with Japanese text"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import tempfile
        
        # Create a blank image with white background
        img = Image.new('RGB', (200, 100), color='white')
        d = ImageDraw.Draw(img)
        
        # Try to use a default font (this may not have Japanese characters)
        try:
            if platform.system() == "Windows":
                font = ImageFont.truetype("msgothic.ttc", 24)
            elif platform.system() == "Darwin":  # macOS
                font = ImageFont.truetype("/System/Library/Fonts/AppleGothic.ttf", 24)
            else:  # Linux
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            # If font loading fails, use default
            font = None
        
        # Draw text
        d.text((20, 40), "テスト", fill="black", font=font)
        
        # Save to a temporary file
        fd, path = tempfile.mkstemp(suffix='.png')
        os.close(fd)
        img.save(path)
        return path
    except Exception as e:
        print(f"Error creating test image: {e}")
        return None

def install_manga_ocr():
    """Install MangaOCR package if not already installed"""
    try:
        print("Installing MangaOCR...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "manga-ocr==0.1.10"
        ])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing MangaOCR: {e}")
        return False

def main():
    """Main function to check MangaOCR installation and download models"""
    print("Checking MangaOCR integration for Kana Writing Practice...\n")
    
    # Check disk space
    cache_dir = get_cache_dir()
    os.makedirs(cache_dir, exist_ok=True)
    
    required_space = estimate_disk_space()
    available_space = check_available_disk_space(cache_dir)
    
    print(f"Required disk space: {required_space} MB")
    print(f"Available disk space: {available_space:.1f} MB")
    
    if available_space < required_space:
        print(f"\n❌ Not enough disk space to download MangaOCR models.")
        print(f"   Please free up at least {required_space} MB and try again.")
        return 1
    
    # Check if MangaOCR is installed
    if not check_manga_ocr_installed():
        print("❌ MangaOCR is not installed.")
        
        print("\nWould you like to install it now? (y/n)")
        response = input("> ").strip().lower()
        
        if response in ["y", "yes"]:
            if not install_manga_ocr():
                print("\nFailed to install MangaOCR.")
                return 2
        else:
            print("\nPlease install MangaOCR manually with: pip install manga-ocr==0.1.10")
            return 2
    
    print("✅ MangaOCR is installed.")
    
    # Download models
    print("\nChecking MangaOCR models...")
    if not download_manga_ocr_models():
        print("\n❌ Failed to download MangaOCR models.")
        return 3
    
    print("\n🎉 MangaOCR is properly configured!")
    print("You can now run the Kana Writing Practice application with full offline capability.")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 