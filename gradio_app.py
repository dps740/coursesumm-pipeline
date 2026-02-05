#!/usr/bin/env python3
"""
CourseSumm v2 - Gradio Web UI Launcher
"""

import sys
import os

# Add coursumm_v2 to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from coursumm_v2.gradio_ui import launch_ui

if __name__ == "__main__":
    print("="*60)
    print("CourseSumm v2 - Web Interface")
    print("="*60)
    print("\nStarting Gradio web interface...")
    print("Access at: http://localhost:7860")
    print("\nPress Ctrl+C to stop\n")
    
    launch_ui()
