"""
API Action Plugin
Handles HTTP API calls and webhook integrations
"""
from typing import Dict, Any, Optional
import requests
import json
import time
from urllib.parse import urljoin
from loguru import logger


class APIActionPlugin:
    """Plugin for API-based actions"""
    
    def __init__(self, base_url: Optional[str] = None, timeout: float = 5.0):
        self.base_url = base_url or "http://localhost:8080"
        self.timeout = timeout
        self.last_action_time = {}
        self.cooldown_time = 0.5
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'HAPTICA-GestureEngine/1.0'
        })
        
        # API endpoints configuration
        self.endpoints = {
            'gesture_webhook': '/api/gesture',
            'action_webhook': '/api/action',
            'system_control': '/api/system',
            'custom_endpoint': '/api/custom'
        }
        
        logger.info(f"API action plugin initialized: base_url={self.base_url}")
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute API action
        
        Args:
            context: Action context containing:
                - action: API endpoint or full URL
                - gesture: gesture name
                - method: HTTP method (GET, POST, PUT, DELETE)
                - payload: request payload
                - headers: additional headers
        
        Returns:
            Execution result
        """
        action_command = context.get('action', '')
        gesture = context.get('gesture', '')
        method = context.get('method', 'POST').upper()
        payload = context.get('payload', {})
        headers = context.get('headers', {})
        
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
            # Prepare URL
            if action_command.startswith('http'):
                url = action_command
            else:
                # Relative endpoint
                endpoint = self.endpoints.get(action_command, action_command)
                url = urljoin(self.base_url, endpoint)
            
            # Prepare payload with gesture context
            request_payload = {
                'gesture': gesture,
                'timestamp': current_time,
                'confidence': context.get('confidence', 0.0),
                'action_type': context.get('action_type', 'short_press'),
                **payload
            }
            
            # Merge headers
            request_headers = {**self.session.headers, **headers}
            
            # Execute request
            response = self._make_request(method, url, request_payload, request_headers)
            
            if response and response.status_code < 400:
                self.last_action_time[f"{gesture}_{action_command}"] = current_time
                logger.info(f"API action executed: {method} {url} -> {response.status_code}")
                
                return {
                    'executed': True,
                    'action_type': 'api',
                    'method': method,
                    'url': url,
                    'status_code': response.status_code,
                    'response': self._parse_response(response),
                    'gesture': gesture,
                    'timestamp': current_time
                }
            else:
                status_code = response.status_code if response else 0
                return {
                    'executed': False,
                    'reason': 'api_error',
                    'status_code': status_code,
                    'url': url,
                    'method': method
                }
            
        except Exception as e:
            logger.error(f"API action failed: {e}")
            return {
                'executed': False,
                'error': str(e),
                'action_type': 'api',
                'url': action_command
            }
    
    def _make_request(self, method: str, url: str, payload: Dict, headers: Dict) -> Optional[requests.Response]:
        """Make HTTP request with error handling"""
        try:
            if method == 'GET':
                response = self.session.get(url, params=payload, headers=headers, timeout=self.timeout)
            elif method == 'POST':
                response = self.session.post(url, json=payload, headers=headers, timeout=self.timeout)
            elif method == 'PUT':
                response = self.session.put(url, json=payload, headers=headers, timeout=self.timeout)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers, timeout=self.timeout)
            elif method == 'PATCH':
                response = self.session.patch(url, json=payload, headers=headers, timeout=self.timeout)
            else:
                logger.warning(f"Unsupported HTTP method: {method}")
                return None
            
            return response
            
        except requests.exceptions.Timeout:
            logger.warning(f"API request timeout: {url}")
            return None
        except requests.exceptions.ConnectionError:
            logger.warning(f"API connection error: {url}")
            return None
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return None
    
    def _parse_response(self, response: requests.Response) -> Dict[str, Any]:
        """Parse API response"""
        try:
            # Try to parse JSON
            if 'application/json' in response.headers.get('content-type', ''):
                return response.json()
            else:
                return {'text': response.text[:500]}  # Limit text response
                
        except json.JSONDecodeError:
            return {'text': response.text[:500]}
        except Exception as e:
            return {'error': f"Response parsing failed: {e}"}
    
    def execute_webhook(self, webhook_url: str, gesture_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute webhook with gesture data"""
        try:
            payload = {
                'event': 'gesture_detected',
                'data': gesture_data,
                'timestamp': time.time(),
                'source': 'haptica'
            }
            
            response = self.session.post(webhook_url, json=payload, timeout=self.timeout)
            
            return {
                'executed': response.status_code < 400,
                'status_code': response.status_code,
                'response': self._parse_response(response)
            }
            
        except Exception as e:
            logger.error(f"Webhook execution failed: {e}")
            return {'executed': False, 'error': str(e)}
    
    def execute_batch_requests(self, requests_config: list) -> Dict[str, Any]:
        """Execute multiple API requests in sequence"""
        results = []
        
        for config in requests_config:
            try:
                result = self.execute(config)
                results.append(result)
                
                # Brief delay between requests
                time.sleep(0.1)
                
            except Exception as e:
                results.append({'executed': False, 'error': str(e)})
        
        return {
            'batch_executed': True,
            'total_requests': len(requests_config),
            'successful_requests': sum(1 for r in results if r.get('executed', False)),
            'results': results
        }
    
    def test_connectivity(self) -> Dict[str, Any]:
        """Test API connectivity"""
        try:
            test_url = urljoin(self.base_url, '/health')
            response = self.session.get(test_url, timeout=2.0)
            
            return {
                'connected': response.status_code < 400,
                'status_code': response.status_code,
                'response_time_ms': response.elapsed.total_seconds() * 1000,
                'url': test_url
            }
            
        except Exception as e:
            return {
                'connected': False,
                'error': str(e),
                'url': self.base_url
            }
    
    def set_authentication(self, auth_type: str, credentials: Dict[str, str]):
        """Set authentication for API requests"""
        if auth_type == 'bearer':
            token = credentials.get('token')
            self.session.headers['Authorization'] = f'Bearer {token}'
        elif auth_type == 'api_key':
            key = credentials.get('key')
            header_name = credentials.get('header', 'X-API-Key')
            self.session.headers[header_name] = key
        elif auth_type == 'basic':
            username = credentials.get('username')
            password = credentials.get('password')
            self.session.auth = (username, password)
        
        logger.info(f"API authentication set: {auth_type}")
    
    def add_custom_endpoint(self, name: str, endpoint: str):
        """Add custom API endpoint"""
        self.endpoints[name] = endpoint
        logger.info(f"Custom endpoint added: {name} -> {endpoint}")
    
    def set_base_url(self, base_url: str):
        """Update base URL"""
        self.base_url = base_url
        logger.info(f"API base URL updated: {base_url}")
    
    def set_cooldown(self, cooldown_seconds: float):
        """Set action cooldown time"""
        self.cooldown_time = max(0.1, cooldown_seconds)
        logger.info(f"API cooldown set to {self.cooldown_time}s")
    
    def get_available_actions(self) -> Dict[str, str]:
        """Get list of available API actions"""
        return {
            'endpoints': ', '.join(self.endpoints.keys()),
            'methods': 'GET, POST, PUT, DELETE, PATCH',
            'features': 'webhooks, batch requests, authentication',
            'base_url': self.base_url
        }
    
    def close(self):
        """Close session and cleanup"""
        self.session.close()
        logger.info("API session closed")