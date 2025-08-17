# Uma Event Helper

This project is inspired by [Kisegami/Uma-Event-Helper](https://github.com/Kisegami/Uma-Event-Helper)

---

A real-time event overlay tool for Umamusume Pretty Derby that displays event information in a semi-transparent overlay window.

**Note**: This project serves as a function test for [umamusume-auto-train](https://github.com/Kisegami/umamusume-auto-train) and may be developed as a standalone tool in the future.

![Screenshot](Screenshot.png)

## Features

- **Real-time Event Detection**: Automatically detects when events appear in the game
- **Event Information Display**: Shows event options and rewards from comprehensive databases
- **Semi-transparent Overlay**: Non-intrusive overlay that stays on top of the game window
- **Smart OCR**: Advanced text recognition optimized for event names
- **Fuzzy Matching**: Handles OCR mistakes and variations in event names

## Requirements

- Python 3.7+
- Tesseract OCR installed on your system
- Windows 10/11 (tested on Windows)
- **Game must run at 1920x1080 resolution**

## Installation

1. **Install Tesseract OCR**:
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install to default location: `C:\Program Files\Tesseract-OCR\`

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the overlay**:
   ```bash
   python run_event_overlay.py
   ```

2. **Position the overlay**:
   - The overlay appears at position (964, 810) with size 796x269
   - You can modify these coordinates in `core/event_overlay.py` if needed

3. **Play the game**:
   - **Ensure the game is running at 1920x1080 resolution**
   - The overlay will automatically detect events and display information
   - Close the overlay window or press Ctrl+C to stop

## How it Works

1. **Event Detection**: Uses image recognition to detect the event choice icon
2. **OCR Processing**: Captures and processes the event name text using Tesseract
3. **Database Lookup**: Searches comprehensive event databases for matches
4. **Overlay Display**: Shows event options and rewards in real-time

## File Structure

```
Uma_event_helper/
├── run_event_overlay.py      # Main entry point
├── core/
│   ├── event_overlay.py      # Main overlay logic
│   └── ocr.py               # OCR functions for event names
├── utils/
│   └── screenshot.py        # Screen capture utilities
├── assets/
│   ├── events/
│   │   ├── support_card.json # Support card event database
│   │   ├── uma_data.json    # Uma event database
│   │   └── ura_finale.json  # Ura finale event database
│   └── icons/
│       └── event_choice_1.png # Event detection icon
├── tessdata/
│   └── eng.traineddata      # Tesseract training data
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Configuration

### Overlay Position
Edit `core/event_overlay.py` to change overlay position:
```python
self.overlay_x = 964      # X coordinate
self.overlay_y = 810      # Y coordinate
self.overlay_width = 796  # Width
self.overlay_height = 269 # Height
```

### Event Detection Region
Edit the event name capture region:
```python
self.event_region = (243, 201, 365, 45)  # (x, y, width, height)
```

## Troubleshooting

### Game Resolution Issues
- **The game MUST run at 1920x1080 resolution**
- Event detection and OCR are calibrated for this specific resolution
- Running at different resolutions will cause detection failures

### Tesseract Not Found
If you get Tesseract errors:
1. Ensure Tesseract is installed in the default location
2. Add Tesseract to your system PATH
3. Or modify the path in `core/ocr.py`

### Overlay Not Detecting Events
1. Check that the game window is visible and not minimized
2. **Verify the game is running at 1920x1080 resolution**
3. Verify the event detection region is correct for your screen resolution
4. Ensure the `event_choice_1.png` icon file is present

### Poor OCR Results
1. **Make sure the game is running at 1920x1080 resolution**
2. Check that the event region coordinates are correct
3. Try adjusting the OCR confidence threshold in `core/ocr.py`

## Development

This tool is designed to be easily extensible:
- Add new event databases to `assets/events/`
- Modify OCR settings in `core/ocr.py`
- Adjust overlay appearance in `core/event_overlay.py`

## Related Projects

This project is a function test for the main [umamusume-auto-train](https://github.com/Kisegami/umamusume-auto-train) project, which provides comprehensive auto-training and racing functionality for Umamusume Pretty Derby.

## License

This project is for educational purposes. Please respect the terms of service of Umamusume Pretty Derby.

## Contributing

Feel free to submit issues and enhancement requests! 
