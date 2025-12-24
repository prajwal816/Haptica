# HAPTICA API Documentation

## REST API Endpoints

### Gesture Recognition API

#### POST /api/predict

Predict gesture from uploaded image

**Request:**

```json
{
  "image": "base64_encoded_image",
  "confidence_threshold": 0.7
}
```

**Response:**

```json
{
  "gesture": "palm",
  "confidence": 0.85,
  "timestamp": "2024-01-01T12:00:00Z",
  "processing_time_ms": 45
}
```

#### GET /api/gestures

Get available gesture classes

**Response:**

```json
{
  "gestures": {
    "0": "palm",
    "1": "fist",
    "2": "thumb",
    ...
  }
}
```

#### POST /api/actions/execute

Execute action for gesture

**Request:**

```json
{
  "gesture": "palm",
  "confidence": 0.85
}
```

**Response:**

```json
{
  "executed": true,
  "action_type": "keyboard",
  "action_command": "space",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Configuration API

#### GET /api/config/actions

Get current action mappings

#### PUT /api/config/actions

Update action mappings

#### GET /api/config/labels

Get gesture labels configuration

### System API

#### GET /api/status

Get system status and health

**Response:**

```json
{
  "status": "running",
  "fps": 28.5,
  "model_loaded": true,
  "camera_active": true,
  "uptime_seconds": 3600
}
```

#### POST /api/system/reload

Reload configuration files

## WebSocket API

### Real-time Gesture Stream

Connect to `ws://localhost:8080/ws/gestures` for real-time gesture predictions.

**Message Format:**

```json
{
  "type": "gesture_prediction",
  "data": {
    "gesture": "palm",
    "confidence": 0.85,
    "is_stable": true,
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

## Python SDK

```python
from haptica_sdk import HapticaClient

client = HapticaClient("http://localhost:8080")

# Predict gesture from image
result = client.predict_gesture(image_path="hand.jpg")

# Execute action
client.execute_action("palm")

# Get system status
status = client.get_status()
```
