"""
Mouse Action Plugin
Handles mouse-based gesture actions
"""
from typing import Dict, Any, Tuple
from pynput import mouse
from pynput.mouse import Button
import time
from loguru import logger


class MouseActionPlugin:
    """Plugin for mouse-based actions"""
    
    def __init__(self):
        self.controller = mouse.Controller()
        self.last_action_time = {}
        self.cooldown_time = 0.3  # Shorter cooldown for mouse actions
        
        # Button mapping
        self.button_map = {
            'left': Button.left,
            'right': Button.right,
            'middle': Button.middle
        }
        
        # Screen dimensions (will be updated dynamically)
        self.screen_width = 1920
        self.screen_height = 1080
        
        logger.info("Mouse action plugin initialized")
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute mouse action
        
        Args:
            context: Action context containing:
                - action: mouse command (e.g., 'left_click', 'move_100_200', 'scroll_up')
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
            success = False
            
            if action_command.endswith('_click'):
                # Click actions
                success = self._execute_click(action_command)
            elif action_command.startswith('move_'):
                # Move actions
                success = self._execute_move(action_command)
            elif action_command.startswith('scroll_'):
                # Scroll actions
                success = self._execute_scroll(action_command)
            elif action_command.startswith('drag_'):
                # Drag actions
                success = self._execute_drag(action_command)
            else:
                logger.warning(f"Unknown mouse action: {action_command}")
                return {'executed': False, 'reason': 'unknown_action'}
            
            if success:
                self.last_action_time[f"{gesture}_{action_command}"] = current_time
                logger.info(f"Mouse action executed: {action_command}")
            
            return {
                'executed': success,
                'action_type': 'mouse',
                'command': action_command,
                'gesture': gesture,
                'timestamp': current_time
            }
            
        except Exception as e:
            logger.error(f"Mouse action failed: {e}")
            return {
                'executed': False,
                'error': str(e),
                'action_type': 'mouse',
                'command': action_command
            }
    
    def _execute_click(self, action_command: str) -> bool:
        """Execute click actions"""
        try:
            if action_command == 'left_click':
                self.controller.click(Button.left)
            elif action_command == 'right_click':
                self.controller.click(Button.right)
            elif action_command == 'middle_click':
                self.controller.click(Button.middle)
            elif action_command == 'double_click':
                self.controller.click(Button.left, 2)
            else:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Click execution failed: {e}")
            return False
    
    def _execute_move(self, action_command: str) -> bool:
        """Execute mouse movement"""
        try:
            # Parse move command: move_x_y or move_relative_dx_dy
            parts = action_command.split('_')
            
            if len(parts) >= 3:
                if parts[1] == 'relative':
                    # Relative movement
                    dx, dy = int(parts[2]), int(parts[3])
                    current_pos = self.controller.position
                    new_x = current_pos[0] + dx
                    new_y = current_pos[1] + dy
                else:
                    # Absolute movement
                    new_x, new_y = int(parts[1]), int(parts[2])
                
                # Clamp to screen bounds
                new_x = max(0, min(self.screen_width - 1, new_x))
                new_y = max(0, min(self.screen_height - 1, new_y))
                
                self.controller.position = (new_x, new_y)
                return True
            
            return False
            
        except (ValueError, IndexError) as e:
            logger.error(f"Move parsing failed: {e}")
            return False
    
    def _execute_scroll(self, action_command: str) -> bool:
        """Execute scroll actions"""
        try:
            if action_command == 'scroll_up':
                self.controller.scroll(0, 1)
            elif action_command == 'scroll_down':
                self.controller.scroll(0, -1)
            elif action_command == 'scroll_left':
                self.controller.scroll(-1, 0)
            elif action_command == 'scroll_right':
                self.controller.scroll(1, 0)
            else:
                # Parse custom scroll: scroll_dx_dy
                parts = action_command.split('_')
                if len(parts) >= 3:
                    dx, dy = int(parts[1]), int(parts[2])
                    self.controller.scroll(dx, dy)
                else:
                    return False
            
            return True
            
        except (ValueError, IndexError) as e:
            logger.error(f"Scroll execution failed: {e}")
            return False
    
    def _execute_drag(self, action_command: str) -> bool:
        """Execute drag actions"""
        try:
            # Parse drag command: drag_start_x_y or drag_end_x_y
            parts = action_command.split('_')
            
            if len(parts) >= 4 and parts[1] == 'to':
                # drag_to_x_y
                end_x, end_y = int(parts[2]), int(parts[3])
                
                # Start drag from current position
                self.controller.press(Button.left)
                time.sleep(0.1)  # Brief pause
                
                # Move to end position
                self.controller.position = (end_x, end_y)
                time.sleep(0.1)
                
                # Release
                self.controller.release(Button.left)
                
                return True
            
            return False
            
        except (ValueError, IndexError) as e:
            logger.error(f"Drag execution failed: {e}")
            return False
    
    def execute_long_press(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute long press mouse action"""
        action_command = context.get('action', '')
        hold_duration = context.get('hold_duration', 1.0)
        
        try:
            if action_command.endswith('_click'):
                button_name = action_command.replace('_click', '')
                button = self.button_map.get(button_name, Button.left)
                
                # Press and hold
                self.controller.press(button)
                time.sleep(hold_duration)
                self.controller.release(button)
                
                logger.info(f"Mouse long press executed: {button_name} for {hold_duration}s")
                
                return {
                    'executed': True,
                    'action_type': 'mouse_long_press',
                    'command': action_command,
                    'duration': hold_duration
                }
            
            return {'executed': False, 'reason': 'unsupported_long_press'}
            
        except Exception as e:
            logger.error(f"Mouse long press failed: {e}")
            return {'executed': False, 'error': str(e)}
    
    def get_current_position(self) -> Tuple[int, int]:
        """Get current mouse position"""
        return self.controller.position
    
    def set_screen_dimensions(self, width: int, height: int):
        """Set screen dimensions for boundary checking"""
        self.screen_width = width
        self.screen_height = height
        logger.info(f"Screen dimensions set: {width}x{height}")
    
    def set_cooldown(self, cooldown_seconds: float):
        """Set action cooldown time"""
        self.cooldown_time = max(0.1, cooldown_seconds)
        logger.info(f"Mouse cooldown set to {self.cooldown_time}s")
    
    def get_available_actions(self) -> Dict[str, str]:
        """Get list of available mouse actions"""
        return {
            'clicks': 'left_click, right_click, middle_click, double_click',
            'movement': 'move_x_y (absolute), move_relative_dx_dy',
            'scrolling': 'scroll_up, scroll_down, scroll_left, scroll_right',
            'dragging': 'drag_to_x_y',
            'long_press': 'Any click action with hold duration'
        }