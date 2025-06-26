# Minecraft Compass Generator

An interactive compass generator that creates Minecraft-style compass sprites with customizable needle directions.

## Features

- **Interactive Mode**: Click to set compass direction in real-time
- **Programmatic Generation**: Generate compass sprites for specific angles
- **Accurate Minecraft Styling**: Reproduces the exact compass needle appearance from Minecraft
- **Save Functionality**: Export generated compass sprites as PNG images

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Interactive Mode

Run the interactive compass generator:
```bash
python main.py
```

**Controls:**
- **Left Click**: Set compass needle direction by clicking around the compass
- **S Key**: Save current compass as PNG file
- **Q Key**: Quit the application

The compass will display:
- Current angle in degrees
- Cardinal directions (N, E, S, W) around the compass
- Real-time needle updates as you click

### Programmatic Generation

Use the demo script to generate a complete set of compass directions:
```bash
python demo.py
```

This will create compass sprites for all 8 cardinal and intercardinal directions (0°, 45°, 90°, 135°, 180°, 225°, 270°, 315°).

### Custom Usage

You can also use the compass generator in your own code:

```python
from main import setup_compass_sprite, CompassImage
import math

# Create base compass (16x16 pixels)
base_compass = CompassImage(16, 16)
# ... set up base texture ...

# Create output compass
output_compass = CompassImage(16, 16)

# Generate compass pointing northeast (45 degrees)
angle = math.radians(45)
setup_compass_sprite(base_compass, angle, output_compass)
```

## Files

- `main.py`: Main interactive compass generator
- `demo.py`: Batch generation script for all directions
- `compass.png`: Base compass texture (if available)
- `requirements.txt`: Python dependencies

## Compass Mechanics

The compass needle consists of:
- **Red pointer**: Main direction indicator (front half)
- **Grey back**: Opposite direction (back half)  
- **Grey spurs**: Horizontal needle supports

Angles follow standard compass convention:
- 0° = North (up)
- 90° = East (right)
- 180° = South (down)
- 270° = West (left)

## Output

Generated compass images are saved as PNG files with the naming convention:
- Interactive mode: `compass_XXX_generated.png`
- Demo mode: `compass_XXX_demo.png`

Where `XXX` is the angle in degrees (000-359).
