# HAPTICA

## Real-Time Hand Gesture Recognition & Interaction Engine

### Overview

HAPTICA is a professional-grade real-time hand gesture recognition platform that converts live camera input into meaningful digital actions. Designed as a scalable platform for enterprise applications.

### Core Vision

"Translate human hand gestures into machine-interpretable commands in real time."

### Company-Level Use Cases

- **Touchless UI Control**: Healthcare environments, public kiosks
- **Gesture-Controlled Applications**: Media control, robotics, AR/VR
- **Assistive Technology**: Accessibility solutions
- **Smart Systems Interaction**: IoT devices, dashboards

### System Architecture

```
Camera Feed → Frame Acquisition → Hand Detection → Preprocessing →
Deep Learning Model → Gesture Classification → Action Mapping → Output Layer
```

### Key Features

- Real-time processing (15-30 FPS)
- Modular architecture for enterprise scalability
- Configurable gesture-to-action mappings
- Multiple output interfaces (UI, API, system commands)
- Temporal smoothing for stable predictions
- GPU optimization support

## Quick Start

### 1. Setup & Installation

```bash
# Run automated setup
python scripts/setup.py

# Or manual installation
pip install -r requirements.txt
```

### 2. Run HAPTICA

```bash
# Start the application
python src/main.py

# With custom configuration
python src/main.py --config custom_config --log-level DEBUG
```

### 3. Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t haptica .
docker run -p 8080:8080 --device /dev/video0 haptica
```

## Project Structure

```
HAPTICA/
├── src/                    # Core application code
│   ├── camera/            # Video input handling
│   ├── detection/         # Hand detection (MediaPipe)
│   ├── preprocessing/     # Image transforms
│   ├── inference/         # ML model inference
│   ├── logic/            # Gesture smoothing & actions
│   ├── ui/               # Real-time overlay
│   └── main.py           # Application entry point
├── config/               # Configuration files
├── models/               # ML models
├── docs/                 # Documentation
├── tests/                # Unit tests
├── scripts/              # Utility scripts
└── notebooks/            # Jupyter notebooks
```

## Supported Gestures

- **Palm**: Open hand gesture
- **Fist**: Closed hand
- **Thumb**: Thumbs up
- **Index**: Pointing finger
- **OK**: OK hand sign
- **C-Shape**: C-shaped hand
- **L-Shape**: L-shaped hand

## Configuration

Edit `config/actions.json` to customize gesture-to-action mappings:

```json
{
  "gesture_actions": {
    "palm": {
      "type": "keyboard",
      "action": "space",
      "description": "Play/Pause media"
    }
  }
}
```

## Testing

```bash
# Run all tests
python scripts/run_tests.py --all

# Run with coverage
python scripts/run_tests.py --coverage

# Performance benchmarks
python scripts/run_tests.py --performance
```

## Documentation

- [System Architecture](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## Requirements

- Python 3.8+
- OpenCV 4.8+
- TensorFlow 2.13+
- MediaPipe 0.10+
- Camera (USB/built-in)

## License

Enterprise License - Contact for commercial use

## Support

For technical support and enterprise inquiries, contact the HAPTICA team.
