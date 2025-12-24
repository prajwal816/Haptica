"""
Gesture State Machine - Intent-aware gesture recognition
Implements IDLE → DETECTING → CONFIRMED → COOLDOWN flow
"""
import time
from enum import Enum
from typing import Dict, Optional, Callable
from dataclasses import dataclass
from loguru import logger


class GestureState(Enum):
    """Gesture recognition states"""
    IDLE = "idle"
    DETECTING = "detecting"
    CONFIRMED = "confirmed"
    COOLDOWN = "cooldown"
    DISABLED = "disabled"


@dataclass
class GestureEvent:
    """Gesture event data"""
    gesture: str
    confidence: float
    timestamp: float
    is_stable: bool
    duration: float = 0.0


class GestureStateMachine:
    """
    Intent-aware gesture state machine
    Prevents accidental actions and enables long-press vs short-gesture differentiation
    """
    
    def __init__(self, 
                 detection_threshold: float = 0.7,
                 confirmation_time: float = 0.3,
                 cooldown_time: float = 1.0,
                 long_press_threshold: float = 2.0):
        
        self.detection_threshold = detection_threshold
        self.confirmation_time = confirmation_time
        self.cooldown_time = cooldown_time
        self.long_press_threshold = long_press_threshold
        
        # State tracking
        self.current_state = GestureState.IDLE
        self.current_gesture = None
        self.state_start_time = time.time()
        self.last_action_time = 0
        
        # Gesture tracking
        self.detecting_gesture = None
        self.detecting_start_time = 0
        self.confirmed_gesture = None
        self.confirmed_start_time = 0
        
        # Action callbacks
        self.action_callbacks: Dict[str, Callable] = {}
        self.long_press_callbacks: Dict[str, Callable] = {}
        
        # Statistics
        self.stats = {
            'total_detections': 0,
            'confirmed_gestures': 0,
            'false_positives': 0,
            'long_press_actions': 0
        }
        
        logger.info(f"Gesture state machine initialized: "
                   f"detection={detection_threshold}, confirmation={confirmation_time}s, "
                   f"cooldown={cooldown_time}s")
    
    def register_action_callback(self, gesture: str, callback: Callable, 
                               long_press_callback: Optional[Callable] = None):
        """Register action callbacks for gestures"""
        self.action_callbacks[gesture] = callback
        if long_press_callback:
            self.long_press_callbacks[gesture] = long_press_callback
        logger.debug(f"Registered callbacks for gesture: {gesture}")
    
    def process_gesture(self, gesture_event: GestureEvent) -> dict:
        """
        Process gesture through state machine
        
        Args:
            gesture_event: Current gesture detection event
            
        Returns:
            State machine result with actions to execute
        """
        current_time = time.time()
        result = {
            'state': self.current_state.value,
            'action': None,
            'action_type': None,
            'gesture': gesture_event.gesture,
            'confidence': gesture_event.confidence,
            'state_duration': current_time - self.state_start_time,
            'transition': None
        }
        
        # State machine logic
        if self.current_state == GestureState.IDLE:
            result.update(self._handle_idle_state(gesture_event, current_time))
            
        elif self.current_state == GestureState.DETECTING:
            result.update(self._handle_detecting_state(gesture_event, current_time))
            
        elif self.current_state == GestureState.CONFIRMED:
            result.update(self._handle_confirmed_state(gesture_event, current_time))
            
        elif self.current_state == GestureState.COOLDOWN:
            result.update(self._handle_cooldown_state(gesture_event, current_time))
            
        elif self.current_state == GestureState.DISABLED:
            result.update(self._handle_disabled_state(gesture_event, current_time))
        
        return result
    
    def _handle_idle_state(self, event: GestureEvent, current_time: float) -> dict:
        """Handle IDLE state logic"""
        if (event.gesture != 'none' and event.gesture != 'uncertain' and 
            event.confidence >= self.detection_threshold):
            
            # Transition to DETECTING
            self._transition_to_state(GestureState.DETECTING, current_time)
            self.detecting_gesture = event.gesture
            self.detecting_start_time = current_time
            self.stats['total_detections'] += 1
            
            return {
                'transition': 'idle_to_detecting',
                'detecting_gesture': event.gesture
            }
        
        return {}
    
    def _handle_detecting_state(self, event: GestureEvent, current_time: float) -> dict:
        """Handle DETECTING state logic"""
        detection_duration = current_time - self.detecting_start_time
        
        # Check if same gesture is still being detected
        if (event.gesture == self.detecting_gesture and 
            event.confidence >= self.detection_threshold and
            event.is_stable):
            
            # Check if confirmation time reached
            if detection_duration >= self.confirmation_time:
                # Transition to CONFIRMED
                self._transition_to_state(GestureState.CONFIRMED, current_time)
                self.confirmed_gesture = self.detecting_gesture
                self.confirmed_start_time = current_time
                self.stats['confirmed_gestures'] += 1
                
                # Execute short-press action
                action_result = self._execute_action(self.confirmed_gesture, 'short_press')
                
                return {
                    'transition': 'detecting_to_confirmed',
                    'action': action_result.get('action'),
                    'action_type': 'short_press',
                    'confirmed_gesture': self.confirmed_gesture
                }
        else:
            # Gesture changed or lost confidence - back to IDLE
            self._transition_to_state(GestureState.IDLE, current_time)
            self.stats['false_positives'] += 1
            
            return {
                'transition': 'detecting_to_idle',
                'reason': 'gesture_lost'
            }
        
        return {'detection_duration': detection_duration}
    
    def _handle_confirmed_state(self, event: GestureEvent, current_time: float) -> dict:
        """Handle CONFIRMED state logic"""
        confirmed_duration = current_time - self.confirmed_start_time
        
        # Check for long press
        if (event.gesture == self.confirmed_gesture and 
            event.confidence >= self.detection_threshold and
            confirmed_duration >= self.long_press_threshold):
            
            # Execute long-press action if available
            long_press_result = self._execute_action(self.confirmed_gesture, 'long_press')
            
            if long_press_result.get('executed'):
                self.stats['long_press_actions'] += 1
                # Transition to cooldown after long press
                self._transition_to_state(GestureState.COOLDOWN, current_time)
                
                return {
                    'transition': 'confirmed_to_cooldown',
                    'action': long_press_result.get('action'),
                    'action_type': 'long_press',
                    'confirmed_duration': confirmed_duration
                }
        
        # Check if gesture is no longer detected
        if (event.gesture != self.confirmed_gesture or 
            event.confidence < self.detection_threshold):
            
            # Transition to cooldown
            self._transition_to_state(GestureState.COOLDOWN, current_time)
            
            return {
                'transition': 'confirmed_to_cooldown',
                'reason': 'gesture_ended',
                'confirmed_duration': confirmed_duration
            }
        
        return {'confirmed_duration': confirmed_duration}
    
    def _handle_cooldown_state(self, event: GestureEvent, current_time: float) -> dict:
        """Handle COOLDOWN state logic"""
        cooldown_duration = current_time - self.state_start_time
        
        if cooldown_duration >= self.cooldown_time:
            # Transition back to IDLE
            self._transition_to_state(GestureState.IDLE, current_time)
            
            return {
                'transition': 'cooldown_to_idle',
                'cooldown_duration': cooldown_duration
            }
        
        return {
            'cooldown_remaining': self.cooldown_time - cooldown_duration
        }
    
    def _handle_disabled_state(self, event: GestureEvent, current_time: float) -> dict:
        """Handle DISABLED state logic"""
        # Check for emergency re-enable gesture (e.g., specific gesture sequence)
        if event.gesture == 'palm' and event.confidence > 0.9:
            self._transition_to_state(GestureState.IDLE, current_time)
            logger.info("Gesture recognition re-enabled")
            return {'transition': 'disabled_to_idle'}
        
        return {'status': 'disabled'}
    
    def _transition_to_state(self, new_state: GestureState, current_time: float):
        """Transition to new state"""
        old_state = self.current_state
        self.current_state = new_state
        self.state_start_time = current_time
        
        logger.debug(f"State transition: {old_state.value} → {new_state.value}")
    
    def _execute_action(self, gesture: str, action_type: str) -> dict:
        """Execute action for gesture"""
        try:
            if action_type == 'short_press' and gesture in self.action_callbacks:
                callback = self.action_callbacks[gesture]
                result = callback(gesture, action_type)
                self.last_action_time = time.time()
                return {'executed': True, 'action': result}
                
            elif action_type == 'long_press' and gesture in self.long_press_callbacks:
                callback = self.long_press_callbacks[gesture]
                result = callback(gesture, action_type)
                self.last_action_time = time.time()
                return {'executed': True, 'action': result}
            
            return {'executed': False, 'reason': 'no_callback'}
            
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return {'executed': False, 'error': str(e)}
    
    def emergency_disable(self):
        """Emergency disable gesture recognition"""
        self._transition_to_state(GestureState.DISABLED, time.time())
        logger.warning("Gesture recognition DISABLED via emergency stop")
    
    def force_enable(self):
        """Force enable gesture recognition"""
        self._transition_to_state(GestureState.IDLE, time.time())
        logger.info("Gesture recognition force ENABLED")
    
    def get_stats(self) -> dict:
        """Get state machine statistics"""
        current_time = time.time()
        return {
            **self.stats,
            'current_state': self.current_state.value,
            'state_duration': current_time - self.state_start_time,
            'uptime': current_time - self.last_action_time if self.last_action_time else 0,
            'false_positive_rate': (
                self.stats['false_positives'] / max(1, self.stats['total_detections'])
            ),
            'confirmation_rate': (
                self.stats['confirmed_gestures'] / max(1, self.stats['total_detections'])
            )
        }
    
    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            'total_detections': 0,
            'confirmed_gestures': 0,
            'false_positives': 0,
            'long_press_actions': 0
        }