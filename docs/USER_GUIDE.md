# HAPTICA User Guide

## How to Operate Your Real-Time Hand Gesture Recognition System

### 🚀 Quick Start

#### 1. **Choose Your Version**

HAPTICA comes in two versions:

**🔹 Standard Version** (`src/main.py`)

- Stable, tested, reliable
- Core gesture recognition
- Perfect for daily use

**🔹 Enhanced Version** (`src/app.py`)

- Advanced features and improvements
- Adaptive ROI calibration
- Background robustness
- Intent-aware state machine
- Plugin-based actions

#### 2. **Launch HAPTICA**

```bash
# Standard version (recommended for beginners)
python src/main.py

# Enhanced version (advanced features)
python src/app.py --log-level INFO

# With debug info
python src/main.py --log-level DEBUG
python src/app.py --log-level DEBUG
```

#### 3. **What You'll See**

**Standard Version:**

- **Camera window** opens showing live video feed
- **Green boxes** around detected hands
- **Gesture labels** displayed in center (e.g., "PALM", "FIST")
- **Confidence bars** showing prediction certainty
- **FPS counter** in top-left corner

**Enhanced Version (Additional Features):**

- **Adaptive ROI boxes** that adjust to hand distance
- **State indicators** showing gesture confirmation process
- **ROI stability metrics** in overlay
- **Enhanced background processing** for better recognition
- **Advanced gesture state machine** with cooldowns

---

## 🎮 **How to Use Gestures**

### **Available Gestures & Actions**

| Gesture     | Hand Shape         | Action     | What It Does           |
| ----------- | ------------------ | ---------- | ---------------------- |
| **PALM**    | ✋ Open hand       | Spacebar   | Play/Pause media       |
| **FIST**    | ✊ Closed fist     | Ctrl+C     | Copy text              |
| **THUMB**   | 👍 Thumbs up       | Volume Up  | Increase system volume |
| **INDEX**   | 👆 Pointing finger | Left Click | Mouse left click       |
| **OK**      | 👌 OK sign         | Enter      | Confirm/Enter key      |
| **C_SHAPE** | 🤏 C-shaped hand   | API Call   | Custom web request     |

### **Step-by-Step Operation**

#### **Step 1: Position Yourself**

```
📹 Camera Setup:
- Sit 2-3 feet from camera
- Ensure good lighting
- Keep background simple
- Hand should fill about 1/4 of screen
```

#### **Step 2: Make Gestures**

```
✋ PALM Gesture Example:
1. Hold hand flat, palm facing camera
2. Keep fingers spread and visible
3. Hold steady for 0.3 seconds
4. System will show "PALM" label
5. Action: Spacebar pressed (Play/Pause)
```

#### **Step 3: See Real-Time Feedback**

```
📊 Visual Feedback:
- Green box around your hand
- "PALM" text in center
- Confidence bar: ████████░░ 0.85
- Action confirmation in logs
```

---

## 🎯 **Practical Examples**

### **Example 1: Media Control**

```bash
# Start HAPTICA
python src/main.py

# Open a video (YouTube, VLC, etc.)
# Make PALM gesture → Video pauses/plays
# Make THUMB gesture → Volume increases
```

### **Example 2: Text Editing**

```bash
# Open a text editor (Notepad, Word, etc.)
# Type some text: "Hello World"
# Select the text with mouse
# Make FIST gesture → Text gets copied (Ctrl+C)
# Move cursor elsewhere
# Make OK gesture → Press Enter for new line
```

### **Example 3: Web Browsing**

```bash
# Open a web browser
# Make INDEX gesture → Left click on links
# Make PALM gesture → Pause/play videos
# Make FIST gesture → Copy selected text
```

---

## ⚙️ **Keyboard Controls**

While HAPTICA is running, use these keys:

**Standard Version:**
| Key | Action |
| ------- | -------------------------- |
| **'q'** | Quit HAPTICA |
| **'d'** | Toggle debug mode |
| **'f'** | Toggle FPS display |
| **'c'** | Toggle confidence bars |

**Enhanced Version (Additional Controls):**
| Key | Action |
| ------- | -------------------------- |
| **'q'** | Quit HAPTICA |
| **'m'** | Show performance metrics |
| **'r'** | Reload configuration |
| **'e'** | Emergency disable gestures |
| **'s'** | Re-enable gestures |

---

## 🔧 **Customizing Gestures**

### **Edit Actions Configuration**

```bash
# Open configuration file
notepad config/actions.json

# Example: Change PALM action from spacebar to 'p' key
{
  "gesture_actions": {
    "palm": {
      "type": "keyboard",
      "action": "p",
      "description": "Press P key"
    }
  }
}

# Reload config while HAPTICA is running
# Press 'r' key in HAPTICA window
```

### **Available Action Types**

```json
{
  "keyboard": {
    "action": "space", // Single key
    "action": "ctrl+c", // Key combination
    "action": "Hello World" // Type text
  },
  "mouse": {
    "action": "left_click", // Mouse clicks
    "action": "move_100_200", // Move to position
    "action": "scroll_up" // Scroll actions
  },
  "media": {
    "action": "volume_up", // System volume
    "action": "play_pause", // Media control
    "action": "next_track" // Skip tracks
  }
}
```

---

## 🎪 **Demo Scenarios**

### **Scenario 1: Presentation Control**

```bash
# Perfect for PowerPoint presentations
1. Start HAPTICA: python src/main.py
2. Open PowerPoint presentation
3. Use gestures:
   - PALM → Spacebar (Next slide)
   - FIST → Ctrl+C (Copy content)
   - OK → Enter (Confirm actions)
```

### **Scenario 2: Music Player Control**

```bash
# Control Spotify, iTunes, etc.
1. Start HAPTICA
2. Open music player
3. Use gestures:
   - PALM → Play/Pause music
   - THUMB → Volume up
   - Configure for next/previous track
```

### **Scenario 3: Gaming Control**

```bash
# Map gestures to game controls
1. Edit config/actions.json:
   "palm": {"type": "keyboard", "action": "w"}     // Move forward
   "fist": {"type": "keyboard", "action": "space"} // Jump
   "thumb": {"type": "mouse", "action": "left_click"} // Shoot
2. Start game and HAPTICA
3. Use hand gestures instead of keyboard!
```

---

## 🚨 **Troubleshooting**

### **Common Issues & Solutions**

#### **"No camera detected"**

```bash
# Check camera connection
python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"

# Try different camera index
python src/main.py --camera 1
```

#### **"Gestures not recognized"**

```bash
# Check lighting - ensure bright, even lighting
# Check hand position - fill 1/4 of screen
# Check model file exists: models/hand_recognition_model.h5
# Lower confidence threshold in config/labels.json
```

#### **"Actions not working"**

```bash
# Check action configuration in config/actions.json
# Verify keyboard/mouse permissions
# Test with simple action like spacebar first
```

#### **"Low FPS / Slow performance"**

```bash
# Close other applications
# Use lower camera resolution
# Check CPU usage in Task Manager
```

---

## 📱 **Advanced Usage**

### **API Integration**

```bash
# Set up webhook endpoint
# Configure in config/actions.json:
{
  "c_shape": {
    "type": "api",
    "action": "http://localhost:8080/gesture",
    "method": "POST"
  }
}

# Make C-shape gesture → Sends HTTP request
```

### **Multiple Gesture Sequences**

```bash
# Create gesture combinations
# Example: PALM → FIST → OK = Special action
# Implement in custom action plugin
```

### **Voice + Gesture Control**

```bash
# Combine with speech recognition
# "HAPTICA activate" + PALM gesture = Enhanced control
```

---

## 🎯 **Best Practices**

### **For Best Recognition**

- ✅ **Good lighting** - avoid shadows
- ✅ **Steady hands** - hold gesture for 0.5 seconds
- ✅ **Clear background** - avoid clutter behind hand
- ✅ **Proper distance** - 2-3 feet from camera
- ✅ **Full hand visible** - don't cut off fingers

### **For Smooth Operation**

- ✅ **Start simple** - test PALM and FIST first
- ✅ **Practice gestures** - get familiar with hand shapes
- ✅ **Customize actions** - map to your favorite shortcuts
- ✅ **Use cooldowns** - prevent accidental repeated actions

---

## 🆘 **Emergency Controls**

### **If System Gets Stuck**

```bash
# Emergency disable gestures
Press 'e' key in HAPTICA window

# Force quit HAPTICA
Press Ctrl+C in terminal
# OR
Press 'q' key in HAPTICA window

# Kill process if unresponsive
Ctrl+Alt+Delete → Task Manager → End HAPTICA process
```

---

## 🎉 **Fun Examples to Try**

### **1. Touchless Photo Booth**

```bash
# Configure PALM → Spacebar
# Open camera app
# Make PALM gesture to take photos!
```

### **2. Gesture DJ**

```bash
# Configure gestures for music controls
# PALM → Play/Pause
# THUMB → Volume up
# INDEX → Next track
# Control your music with hand movements!
```

### **3. Smart Home Control**

```bash
# Set up API endpoints for smart devices
# FIST → Turn on lights
# PALM → Adjust thermostat
# OK → Lock doors
```

---

## 📞 **Getting Help**

### **Check Logs**

```bash
# View detailed logs
tail -f logs/haptica_*.log

# Debug mode
python src/main.py --log-level DEBUG
```

### **Test Components**

```bash
# Test camera
python scripts/test_camera.py

# Test model
python scripts/test_model.py

# Test actions
python scripts/test_actions.py
```

### **Performance Monitoring**

```bash
# Press 'm' key while HAPTICA is running
# Check FPS, confidence, and system stats
```

---

**🎊 Congratulations! You're now ready to control your computer with hand gestures using HAPTICA!**
