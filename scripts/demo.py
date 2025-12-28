#!/usr/bin/env python3
"""
HAPTICA Demo Script
Interactive demonstration of gesture recognition capabilities
"""
import time
import sys
from pathlib import Path

def print_banner():
    """Print HAPTICA demo banner"""
    print("=" * 60)
    print("🎯 HAPTICA DEMO - Hand Gesture Recognition System")
    print("=" * 60)
    print()

def print_step(step_num, title, description):
    """Print formatted step"""
    print(f"📋 STEP {step_num}: {title}")
    print(f"   {description}")
    print()

def wait_for_user():
    """Wait for user to press Enter"""
    input("   Press Enter to continue...")
    print()

def main():
    """Run HAPTICA demo"""
    print_banner()
    
    print("Welcome to the HAPTICA Interactive Demo!")
    print("This will guide you through using hand gesture recognition.")
    print()
    wait_for_user()
    
    # Step 1: Setup
    print_step(1, "SETUP", 
               "Make sure your camera is connected and you have good lighting.")
    print("   ✅ Camera connected")
    print("   ✅ Good lighting (no shadows)")
    print("   ✅ Clear background")
    print("   ✅ Sit 2-3 feet from camera")
    wait_for_user()
    
    # Step 2: Launch
    print_step(2, "LAUNCH HAPTICA", 
               "We'll start the gesture recognition system.")
    print("   Command to run:")
    print("   📝 python src/main.py")
    print()
    print("   What you'll see:")
    print("   📹 Camera window opens")
    print("   🟢 Green boxes around your hands")
    print("   📊 Gesture labels and confidence bars")
    wait_for_user()
    
    # Step 3: Basic Gestures
    print_step(3, "TRY BASIC GESTURES", 
               "Let's test the main gestures one by one.")
    
    gestures = [
        ("PALM ✋", "Open hand, palm facing camera", "Spacebar (Play/Pause)"),
        ("FIST ✊", "Closed fist", "Ctrl+C (Copy)"),
        ("THUMB 👍", "Thumbs up", "Volume Up"),
        ("INDEX 👆", "Pointing finger", "Left Mouse Click"),
        ("OK 👌", "OK sign with thumb and finger", "Enter Key")
    ]
    
    for gesture, shape, action in gestures:
        print(f"   🎯 Try: {gesture}")
        print(f"      Shape: {shape}")
        print(f"      Action: {action}")
        print()
    
    wait_for_user()
    
    # Step 4: Practical Examples
    print_step(4, "PRACTICAL EXAMPLES", 
               "Here are real-world scenarios to try.")
    
    examples = [
        ("Media Control", "Open YouTube → Make PALM gesture → Video pauses/plays"),
        ("Text Editing", "Select text → Make FIST gesture → Text gets copied"),
        ("Web Browsing", "Make INDEX gesture → Clicks on links"),
        ("Presentation", "Open PowerPoint → Use PALM for next slide")
    ]
    
    for title, description in examples:
        print(f"   🎪 {title}:")
        print(f"      {description}")
        print()
    
    wait_for_user()
    
    # Step 5: Controls
    print_step(5, "KEYBOARD CONTROLS", 
               "While HAPTICA is running, use these keys.")
    
    controls = [
        ("'q'", "Quit HAPTICA"),
        ("'d'", "Toggle debug mode"),
        ("'f'", "Toggle FPS display"),
        ("'r'", "Reload configuration"),
        ("'e'", "Emergency disable gestures")
    ]
    
    for key, action in controls:
        print(f"   ⌨️  {key} → {action}")
    
    print()
    wait_for_user()
    
    # Step 6: Customization
    print_step(6, "CUSTOMIZE GESTURES", 
               "You can change what each gesture does.")
    
    print("   📝 Edit file: config/actions.json")
    print("   🔄 Press 'r' in HAPTICA to reload")
    print()
    print("   Example - Change PALM to press 'P' key:")
    print('   {')
    print('     "palm": {')
    print('       "type": "keyboard",')
    print('       "action": "p",')
    print('       "description": "Press P key"')
    print('     }')
    print('   }')
    print()
    wait_for_user()
    
    # Step 7: Troubleshooting
    print_step(7, "TROUBLESHOOTING", 
               "Common issues and solutions.")
    
    issues = [
        ("Gestures not recognized", "Check lighting, hand position, hold steady"),
        ("Actions not working", "Check config/actions.json, test with spacebar"),
        ("Low FPS", "Close other apps, check CPU usage"),
        ("Camera not found", "Check camera connection, try different index")
    ]
    
    for issue, solution in issues:
        print(f"   ❌ {issue}")
        print(f"      ✅ {solution}")
        print()
    
    wait_for_user()
    
    # Final
    print("🎉 DEMO COMPLETE!")
    print()
    print("You're now ready to use HAPTICA! Here's what to do next:")
    print()
    print("1. 🚀 Launch HAPTICA:")
    print("   python src/main.py")
    print()
    print("2. 🎯 Try the gestures:")
    print("   ✋ PALM → Spacebar")
    print("   ✊ FIST → Ctrl+C")
    print("   👍 THUMB → Volume Up")
    print()
    print("3. 🎮 Have fun controlling your computer with gestures!")
    print()
    print("📚 For detailed help, see: docs/USER_GUIDE.md")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Thanks for trying HAPTICA!")
        sys.exit(0)