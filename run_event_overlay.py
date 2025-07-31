#!/usr/bin/env python3
"""
Event Overlay Launcher
This script runs the real-time event overlay that displays event information
in a semi-transparent box on screen.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.event_overlay import main

if __name__ == "__main__":
    print("🎮 Umamusume Event Overlay")
    print("=" * 50)
    print("This will create a semi-transparent overlay window that shows")
    print("event information in real-time as you play.")
    print()
    print("Overlay will appear at position (964, 810) with size 796x269")
    print("Close the overlay window or press Ctrl+C to stop.")
    print()
    
    input("Press Enter to start the event overlay...")
    
    main() 