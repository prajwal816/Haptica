"""
Action Mapping Engine - Maps gestures to system actions
"""
import json
import time
import requests
from typing import Dict, Optional
from pathlib import Path
from pynput import keyboard, mouse
from pynput.keyboard import Key
import subprocess
from loguru import logger


class ActionMapper:
    """Maps recognized gestures to configurable system actions"""
    
    def __init__(self, actions_config_path: str):
        self.config_path = Path(actions_config_path)
        self.actions = {}
        self.cooldown_time = 1.0
        self.last_action_time = {}
        self.enable_feedback = True
        
        # Initialize input controllers
        self.keyboard_controller = keyboard.Controller()
        self.mouse_controller = mouse.Controller()
        
        self._load_actions()
    
    def _load_actions(self):
        """Load action mappings from configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            self.actions = config.get('gesture_actions', {})
            self.cooldown_time = config.get('action_cooldown', 1.0)
            self.enable_feedback = config.get('enable_feedback', True)
            
            logger.info(f"Action mappings loaded: {len(self.actions)} gestures")
            
        except Exception as e:
            logger.error(f"Failed to load actions config: {e}")
            self.actions = {}
    
    def execute_action(self, gesture: str, confidence: float = 1.0) -> Dict:
        """
        Execute action for recognized gesture
        
        Args:
            gesture: Recognized gesture name
            confidence: Prediction confidence
            
        Returns:
            Execution result dictionary
        """
        current_time = time.time()
        
        # Check if gesture has action mapping
        if gesture not in self.actions:
            return {
                'executed': False,
                'reason': 'no_mapping',
                'gesture': gesture,
                'timestamp': current_time
            }
        
        # Check cooldown
        last_time = self.last_action_time.get(gesture, 0)
        if current_time - last_time < self.cooldown_time:
            return {
                'executed': False,
                'reason': 'cooldown',
                'gesture': gesture,
                'cooldown_remaining': self.cooldown_time - (current_time - last_time),
                'timestamp': current_time
            }
        
        # Get action configuration
        action_config = self.actions[gesture]
        action_type = action_config.get('type', 'keyboard')
        action_command = action_config.get('action', '')
        
        # Execute action based on type
        try:
            success = False
            
            if action_type == 'keyboard':
                success = self._execute_keyboard_action(action_command)
            elif action_type == 'mouse':
                success = self._execute_mouse_action(action_command)
            elif action_type == 'system':
                success = self._execute_system_action(action_command)
            elif action_type == 'api':
                success = self._execute_api_action(action_command)
            else:
                logger.warning(f"Unknown action type: {action_type}")
            
            if success:
                self.last_action_time[gesture] = current_time
                logger.info(f"Action executed: {gesture} -> {action_command}")
            
            return {
                'executed': success,
                'gesture': gesture,
                'action_type': action_type,
                'action_command': action_command,
                'confidence': confidence,
                'timestamp': current_time
            }
            
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return {
                'executed': False,
                'reason': 'execution_error',
                'error': str(e),
                'gesture': gesture,
                'timestamp': current_time
            }
    
    def _execute_keyboard_action(self, command: str) -> bool:
        """Execute keyboard action"""
        try:
            # Handle special key combinations
            if '+' in command:
                keys = command.split('+')
                # Press all keys
                for key in keys:
                    key_obj = self._get_key_object(key.strip())
                    if key_obj:
                        self.keyboard_controller.press(key_obj)
                
                # Release all keys in reverse order
                for key in reversed(keys):
                    key_obj = self._get_key_object(key.strip())
                    if key_obj:
                        self.keyboard_controller.release(key_obj)
            else:
                # Single key or string
                key_obj = self._get_key_object(command)
                if key_obj:
                    self.keyboard_controller.press(key_obj)
                    self.keyboard_controller.release(key_obj)
                else:
                    # Type string
                    self.keyboard_controller.type(command)
            
            return True
            
        except Exception as e:
            logger.error(f"Keyboard action failed: {e}")
            return False
    
    def _get_key_object(self, key_name: str):
        """Convert key name to pynput key object"""
        key_map = {
            'ctrl': Key.ctrl,
            'alt': Key.alt,
            'shift': Key.shift,
            'space': Key.space,
            'enter': Key.enter,
            'tab': Key.tab,
            'esc': Key.esc,
            'up': Key.up,
            'down': Key.down,
            'left': Key.left,
            'right': Key.right
        }
        
        return key_map.get(key_name.lower(), key_name if len(key_name) == 1 else None)
    
    def _execute_mouse_action(self, command: str) -> bool:
        """Execute mouse action"""
        try:
            if command == 'left_click':
                self.mouse_controller.click(mouse.Button.left)
            elif command == 'right_click':
                self.mouse_controller.click(mouse.Button.right)
            elif command == 'double_click':
                self.mouse_controller.click(mouse.Button.left, 2)
            elif command.startswith('move_'):
                # Parse move command: move_x_y
                parts = command.split('_')
                if len(parts) >= 3:
                    x, y = int(parts[1]), int(parts[2])
                    self.mouse_controller.position = (x, y)
            
            return True
            
        except Exception as e:
            logger.error(f"Mouse action failed: {e}")
            return False
    
    def _execute_system_action(self, command: str) -> bool:
        """Execute system command"""
        try:
            if command == 'volume_up':
                subprocess.run(['nircmd', 'changesysvolume', '2000'], check=False)
            elif command == 'volume_down':
                subprocess.run(['nircmd', 'changesysvolume', '-2000'], check=False)
            elif command == 'volume_mute':
                subprocess.run(['nircmd', 'mutesysvolume', '2'], check=False)
            else:
                # Generic system command
                subprocess.run(command.split(), check=False)
            
            return True
            
        except Exception as e:
            logger.error(f"System action failed: {e}")
            return False
    
    def _execute_api_action(self, url: str) -> bool:
        """Execute API call"""
        try:
            response = requests.post(url, timeout=5)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"API action failed: {e}")
            return False
    
    def reload_config(self):
        """Reload action configuration"""
        self._load_actions()
        logger.info("Action configuration reloaded")
    
    def get_available_actions(self) -> Dict:
        """Get list of available actions"""
        return {
            gesture: {
                'type': config.get('type'),
                'action': config.get('action'),
                'description': config.get('description', '')
            }
            for gesture, config in self.actions.items()
        }