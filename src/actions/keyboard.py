"""
Keyboard Action Plugin
Handles keyboard-based gesture actions
"""
from typing import Dict, Any
from pynput import keyboard
from pynput.keyboard import Key
import time
from loguru import logger


class KeyboardActionPlugin:
    """Plugin for keyboard-based actions"""
    
    def __init__(self):
        self.controller = keyboard.Controller()
        self.last_action_time = {}
        self.cooldown_time = 0.5  # Default cooldown
        
        # Key mapping for special keys
        self.key_map = {
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
            'right': Key.right,
            'home': Key.home,
            'end': Key.end,
            'page_up': Key.page_up,
            'page_down': Key.page_down,
            'delete': Key.delete,
            'backspace': Key.backspace,
            'f1': Key.f1, 'f2': Key.f2, 'f3': Key.f3, 'f4': Key.f4,
            'f5': Key.f5, 'f6': Key.f6, 'f7': Key.f7, 'f8': Key.f8,
            'f9': Key.f9, 'f10': Key.f10, 'f11': Key.f11, 'f12': Key.f12
        }
        
        logger.info("Keyboard action plugin initialized")
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute keyboard action
        
        Args:
            context: Action context containing:
                - action: keyboard command (e.g., 'ctrl+c', 'space', 'hello')
                - gesture: gesture name
                - action_type: 'short_press' or 'long_press'
                - confidence: prediction confidence
        
        Returns:
            Execution result
        """
        action_command = context.get('action', '')
        gesture = context.get('gesture', '')
        action_type = context.get('action_type', 'short_press')
        
        current_time = time.time()
        
        # Check cooldown
        last_time = self.last_action_time.get(f"{gesture}_{action_command}", 0)
        if current_time - last_time < self.cooldown_time:
            return {
                'executed': False,
                'reason': 'cooldown',
                'cooldown_remaining': self.cooldown_time - (current_time - last_time)
            }
        
        try:
            # Execute keyboard action
            if '+' in action_command:
                # Key combination (e.g., 'ctrl+c')
                success = self._execute_key_combination(action_command)
            elif action_command in self.key_map:
                # Special key
                success = self._execute_special_key(action_command)
            elif len(action_command) == 1:
                # Single character
                success = self._execute_character(action_command)
            else:
                # Text string
                success = self._execute_text(action_command)
            
            if success:
                self.last_action_time[f"{gesture}_{action_command}"] = current_time
                logger.info(f"Keyboard action executed: {action_command}")
            
            return {
                'executed': success,
                'action_type': 'keyboard',
                'command': action_command,
                'gesture': gesture,
                'timestamp': current_time
            }
            
        except Exception as e:
            logger.error(f"Keyboard action failed: {e}")
            return {
                'executed': False,
                'error': str(e),
                'action_type': 'keyboard',
                'command': action_command
            }
    
    def _execute_key_combination(self, combination: str) -> bool:
        """Execute key combination like 'ctrl+c'"""
        try:
            keys = [key.strip().lower() for key in combination.split('+')]
            key_objects = []
            
            # Convert to key objects
            for key in keys:
                if key in self.key_map:
                    key_objects.append(self.key_map[key])
                elif len(key) == 1:
                    key_objects.append(key)
                else:
                    logger.warning(f"Unknown key in combination: {key}")
                    return False
            
            # Press all keys
            for key_obj in key_objects:
                self.controller.press(key_obj)
            
            # Small delay
            time.sleep(0.01)
            
            # Release all keys in reverse order
            for key_obj in reversed(key_objects):
                self.controller.release(key_obj)
            
            return True
            
        except Exception as e:
            logger.error(f"Key combination execution failed: {e}")
            return False
    
    def _execute_special_key(self, key_name: str) -> bool:
        """Execute special key press"""
        try:
            key_obj = self.key_map.get(key_name.lower())
            if key_obj:
                self.controller.press(key_obj)
                time.sleep(0.01)
                self.controller.release(key_obj)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Special key execution failed: {e}")
            return False
    
    def _execute_character(self, char: str) -> bool:
        """Execute single character press"""
        try:
            self.controller.press(char)
            time.sleep(0.01)
            self.controller.release(char)
            return True
            
        except Exception as e:
            logger.error(f"Character execution failed: {e}")
            return False
    
    def _execute_text(self, text: str) -> bool:
        """Execute text typing"""
        try:
            self.controller.type(text)
            return True
            
        except Exception as e:
            logger.error(f"Text execution failed: {e}")
            return False
    
    def execute_long_press(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute long press action (hold key)"""
        action_command = context.get('action', '')
        hold_duration = context.get('hold_duration', 1.0)
        
        try:
            if action_command in self.key_map:
                key_obj = self.key_map[action_command]
                
                # Press and hold
                self.controller.press(key_obj)
                time.sleep(hold_duration)
                self.controller.release(key_obj)
                
                logger.info(f"Long press executed: {action_command} for {hold_duration}s")
                
                return {
                    'executed': True,
                    'action_type': 'keyboard_long_press',
                    'command': action_command,
                    'duration': hold_duration
                }
            
            return {'executed': False, 'reason': 'unsupported_long_press'}
            
        except Exception as e:
            logger.error(f"Long press execution failed: {e}")
            return {'executed': False, 'error': str(e)}
    
    def set_cooldown(self, cooldown_seconds: float):
        """Set action cooldown time"""
        self.cooldown_time = max(0.1, cooldown_seconds)
        logger.info(f"Keyboard cooldown set to {self.cooldown_time}s")
    
    def get_available_actions(self) -> Dict[str, str]:
        """Get list of available keyboard actions"""
        return {
            'key_combinations': 'ctrl+c, alt+tab, shift+delete, etc.',
            'special_keys': ', '.join(self.key_map.keys()),
            'characters': 'Any single character (a-z, 0-9, symbols)',
            'text': 'Any text string for typing'
        }