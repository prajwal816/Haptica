"""
Media Control Action Plugin
Handles media playback control actions
"""
from typing import Dict, Any
import subprocess
import platform
import time
from loguru import logger


class MediaActionPlugin:
    """Plugin for media control actions"""
    
    def __init__(self):
        self.last_action_time = {}
        self.cooldown_time = 0.5
        self.system = platform.system().lower()
        
        # System-specific media control commands
        self.media_commands = self._get_system_commands()
        
        logger.info(f"Media action plugin initialized for {self.system}")
    
    def _get_system_commands(self) -> Dict[str, str]:
        """Get system-specific media control commands"""
        if self.system == 'windows':
            return {
                'play_pause': 'nircmd sendkeypress 0xB3',  # VK_MEDIA_PLAY_PAUSE
                'stop': 'nircmd sendkeypress 0xB2',        # VK_MEDIA_STOP
                'next_track': 'nircmd sendkeypress 0xB0',  # VK_MEDIA_NEXT_TRACK
                'prev_track': 'nircmd sendkeypress 0xB1',  # VK_MEDIA_PREV_TRACK
                'volume_up': 'nircmd changesysvolume 2000',
                'volume_down': 'nircmd changesysvolume -2000',
                'volume_mute': 'nircmd mutesysvolume 2'
            }
        elif self.system == 'darwin':  # macOS
            return {
                'play_pause': 'osascript -e "tell application \\"System Events\\" to key code 16"',
                'stop': 'osascript -e "tell application \\"System Events\\" to key code 53"',
                'next_track': 'osascript -e "tell application \\"System Events\\" to key code 19"',
                'prev_track': 'osascript -e "tell application \\"System Events\\" to key code 20"',
                'volume_up': 'osascript -e "set volume output volume (output volume of (get volume settings) + 10)"',
                'volume_down': 'osascript -e "set volume output volume (output volume of (get volume settings) - 10)"',
                'volume_mute': 'osascript -e "set volume with output muted"'
            }
        else:  # Linux
            return {
                'play_pause': 'playerctl play-pause',
                'stop': 'playerctl stop',
                'next_track': 'playerctl next',
                'prev_track': 'playerctl previous',
                'volume_up': 'pactl set-sink-volume @DEFAULT_SINK@ +5%',
                'volume_down': 'pactl set-sink-volume @DEFAULT_SINK@ -5%',
                'volume_mute': 'pactl set-sink-mute @DEFAULT_SINK@ toggle'
            }
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute media control action
        
        Args:
            context: Action context containing:
                - action: media command (e.g., 'play_pause', 'volume_up')
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
            # Get system command
            system_command = self.media_commands.get(action_command)
            if not system_command:
                return {
                    'executed': False,
                    'reason': 'unsupported_action',
                    'available_actions': list(self.media_commands.keys())
                }
            
            # Execute command
            success = self._execute_system_command(system_command)
            
            if success:
                self.last_action_time[f"{gesture}_{action_command}"] = current_time
                logger.info(f"Media action executed: {action_command}")
            
            return {
                'executed': success,
                'action_type': 'media',
                'command': action_command,
                'gesture': gesture,
                'timestamp': current_time
            }
            
        except Exception as e:
            logger.error(f"Media action failed: {e}")
            return {
                'executed': False,
                'error': str(e),
                'action_type': 'media',
                'command': action_command
            }
    
    def _execute_system_command(self, command: str) -> bool:
        """Execute system command"""
        try:
            if self.system == 'windows':
                # Windows commands
                result = subprocess.run(command.split(), 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=5)
                return result.returncode == 0
            else:
                # Unix-like systems
                result = subprocess.run(command, 
                                      shell=True, 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=5)
                return result.returncode == 0
                
        except subprocess.TimeoutExpired:
            logger.warning(f"Command timeout: {command}")
            return False
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return False
    
    def execute_long_press(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute long press media action (e.g., continuous volume change)"""
        action_command = context.get('action', '')
        hold_duration = context.get('hold_duration', 2.0)
        
        try:
            if action_command in ['volume_up', 'volume_down']:
                # Continuous volume adjustment
                steps = int(hold_duration * 4)  # 4 steps per second
                step_delay = hold_duration / steps
                
                for _ in range(steps):
                    system_command = self.media_commands.get(action_command)
                    if system_command:
                        self._execute_system_command(system_command)
                        time.sleep(step_delay)
                
                logger.info(f"Media long press executed: {action_command} for {hold_duration}s")
                
                return {
                    'executed': True,
                    'action_type': 'media_long_press',
                    'command': action_command,
                    'duration': hold_duration,
                    'steps': steps
                }
            
            # For other actions, just execute once
            return self.execute(context)
            
        except Exception as e:
            logger.error(f"Media long press failed: {e}")
            return {'executed': False, 'error': str(e)}
    
    def get_current_media_info(self) -> Dict[str, Any]:
        """Get current media player information (if available)"""
        try:
            if self.system == 'linux':
                # Try to get playerctl info
                result = subprocess.run(['playerctl', 'metadata', '--format', 
                                       '{{title}}|{{artist}}|{{status}}'], 
                                      capture_output=True, text=True, timeout=2)
                
                if result.returncode == 0:
                    parts = result.stdout.strip().split('|')
                    return {
                        'title': parts[0] if len(parts) > 0 else 'Unknown',
                        'artist': parts[1] if len(parts) > 1 else 'Unknown',
                        'status': parts[2] if len(parts) > 2 else 'Unknown'
                    }
            
            # For other systems or if playerctl fails
            return {'status': 'unavailable'}
            
        except Exception as e:
            logger.debug(f"Media info retrieval failed: {e}")
            return {'status': 'error'}
    
    def get_volume_level(self) -> int:
        """Get current system volume level (0-100)"""
        try:
            if self.system == 'windows':
                # Windows volume detection would require additional tools
                return -1
            elif self.system == 'darwin':
                result = subprocess.run(['osascript', '-e', 
                                       'output volume of (get volume settings)'], 
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    return int(result.stdout.strip())
            else:  # Linux
                result = subprocess.run(['pactl', 'get-sink-volume', '@DEFAULT_SINK@'], 
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    # Parse volume from pactl output
                    output = result.stdout
                    if '%' in output:
                        volume_str = output.split('%')[0].split()[-1]
                        return int(volume_str)
            
            return -1
            
        except Exception as e:
            logger.debug(f"Volume level retrieval failed: {e}")
            return -1
    
    def set_cooldown(self, cooldown_seconds: float):
        """Set action cooldown time"""
        self.cooldown_time = max(0.1, cooldown_seconds)
        logger.info(f"Media cooldown set to {self.cooldown_time}s")
    
    def get_available_actions(self) -> Dict[str, str]:
        """Get list of available media actions"""
        return {
            'playback': 'play_pause, stop, next_track, prev_track',
            'volume': 'volume_up, volume_down, volume_mute',
            'system': f'Optimized for {self.system}',
            'long_press': 'volume_up, volume_down (continuous adjustment)'
        }