"""
Rate limiting middleware for API abuse prevention
"""

import time
import logging
from typing import Dict, Optional
from collections import defaultdict, deque
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Token bucket rate limiter with sliding window
    """
    
    def __init__(self):
        # Store rate limit data per IP
        self.clients: Dict[str, Dict] = defaultdict(lambda: {
            'tokens': 0,
            'last_refill': time.time(),
            'requests': deque(),
            'blocked_until': None
        })
        
        # Rate limit configurations
        self.limits = {
            'chat': {
                'requests_per_minute': 30,
                'requests_per_hour': 200,
                'burst_limit': 10,
                'tokens_per_second': 0.5,  # 30 requests per minute
                'max_tokens': 10
            },
            'upload': {
                'requests_per_minute': 5,
                'requests_per_hour': 20,
                'burst_limit': 3,
                'tokens_per_second': 0.083,  # 5 requests per minute
                'max_tokens': 3
            },
            'default': {
                'requests_per_minute': 60,
                'requests_per_hour': 500,
                'burst_limit': 20,
                'tokens_per_second': 1.0,  # 60 requests per minute
                'max_tokens': 20
            }
        }
        
        # Cleanup task
        self._cleanup_task = None
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start background cleanup task"""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
    
    async def _periodic_cleanup(self):
        """Periodically clean up old client data"""
        while True:
            try:
                await asyncio.sleep(300)  # Clean up every 5 minutes
                current_time = time.time()
                
                # Remove clients that haven't made requests in the last hour
                inactive_clients = []
                for client_ip, data in self.clients.items():
                    if current_time - data['last_refill'] > 3600:  # 1 hour
                        inactive_clients.append(client_ip)
                
                for client_ip in inactive_clients:
                    del self.clients[client_ip]
                
                if inactive_clients:
                    logger.info(f"Cleaned up {len(inactive_clients)} inactive rate limit entries")
                    
            except Exception as e:
                logger.error(f"Error in rate limiter cleanup: {e}")
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        # Check for forwarded headers first (for reverse proxies)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        return request.client.host if request.client else 'unknown'
    
    def _get_endpoint_type(self, path: str) -> str:
        """Determine endpoint type for rate limiting"""
        if '/chat' in path:
            return 'chat'
        elif '/documents/upload' in path:
            return 'upload'
        else:
            return 'default'
    
    def _refill_tokens(self, client_data: Dict, limit_config: Dict):
        """Refill tokens using token bucket algorithm"""
        current_time = time.time()
        time_passed = current_time - client_data['last_refill']
        
        # Add tokens based on time passed
        tokens_to_add = time_passed * limit_config['tokens_per_second']
        client_data['tokens'] = min(
            limit_config['max_tokens'],
            client_data['tokens'] + tokens_to_add
        )
        client_data['last_refill'] = current_time
    
    def _check_sliding_window(self, client_data: Dict, limit_config: Dict) -> bool:
        """Check sliding window rate limits"""
        current_time = time.time()
        requests = client_data['requests']
        
        # Remove old requests outside the window
        minute_ago = current_time - 60
        hour_ago = current_time - 3600
        
        # Clean up old requests
        while requests and requests[0] < hour_ago:
            requests.popleft()
        
        # Count requests in different windows
        requests_last_minute = sum(1 for req_time in requests if req_time > minute_ago)
        requests_last_hour = len(requests)
        
        # Check limits
        if requests_last_minute >= limit_config['requests_per_minute']:
            return False
        
        if requests_last_hour >= limit_config['requests_per_hour']:
            return False
        
        return True
    
    def _is_blocked(self, client_data: Dict) -> bool:
        """Check if client is temporarily blocked"""
        if client_data['blocked_until']:
            if time.time() < client_data['blocked_until']:
                return True
            else:
                # Unblock client
                client_data['blocked_until'] = None
        return False
    
    def _block_client(self, client_data: Dict, duration: int = 300):
        """Temporarily block a client (default 5 minutes)"""
        client_data['blocked_until'] = time.time() + duration
        logger.warning(f"Client blocked for {duration} seconds due to rate limit violation")
    
    async def check_rate_limit(self, request: Request) -> Optional[JSONResponse]:
        """
        Check if request should be rate limited
        Returns JSONResponse if rate limited, None if allowed
        """
        client_ip = self._get_client_ip(request)
        endpoint_type = self._get_endpoint_type(str(request.url.path))
        limit_config = self.limits[endpoint_type]
        
        client_data = self.clients[client_ip]
        
        # Check if client is blocked
        if self._is_blocked(client_data):
            remaining_time = int(client_data['blocked_until'] - time.time())
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Try again in {remaining_time} seconds.",
                    "retry_after": remaining_time,
                    "endpoint_type": endpoint_type
                },
                headers={"Retry-After": str(remaining_time)}
            )
        
        # Refill tokens
        self._refill_tokens(client_data, limit_config)
        
        # Check sliding window limits
        if not self._check_sliding_window(client_data, limit_config):
            # Block client for repeated violations
            self._block_client(client_data)
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests for {endpoint_type} endpoint. Please slow down.",
                    "retry_after": 300,
                    "endpoint_type": endpoint_type
                },
                headers={"Retry-After": "300"}
            )
        
        # Check token bucket
        if client_data['tokens'] < 1:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Request rate too high for {endpoint_type} endpoint. Please wait.",
                    "retry_after": int(1 / limit_config['tokens_per_second']),
                    "endpoint_type": endpoint_type
                },
                headers={"Retry-After": str(int(1 / limit_config['tokens_per_second']))}
            )
        
        # Consume token and record request
        client_data['tokens'] -= 1
        client_data['requests'].append(time.time())
        
        # Add rate limit headers
        request.state.rate_limit_headers = {
            "X-RateLimit-Limit": str(limit_config['requests_per_minute']),
            "X-RateLimit-Remaining": str(max(0, int(client_data['tokens']))),
            "X-RateLimit-Reset": str(int(client_data['last_refill'] + (limit_config['max_tokens'] / limit_config['tokens_per_second'])))
        }
        
        return None  # Allow request
    
    def get_rate_limit_info(self, client_ip: str, endpoint_type: str = 'default') -> Dict:
        """Get current rate limit status for a client"""
        client_data = self.clients[client_ip]
        limit_config = self.limits[endpoint_type]
        
        self._refill_tokens(client_data, limit_config)
        
        current_time = time.time()
        requests = client_data['requests']
        
        # Count recent requests
        minute_ago = current_time - 60
        requests_last_minute = sum(1 for req_time in requests if req_time > minute_ago)
        
        return {
            "endpoint_type": endpoint_type,
            "tokens_remaining": int(client_data['tokens']),
            "max_tokens": limit_config['max_tokens'],
            "requests_last_minute": requests_last_minute,
            "requests_per_minute_limit": limit_config['requests_per_minute'],
            "is_blocked": self._is_blocked(client_data),
            "blocked_until": client_data['blocked_until'],
            "reset_time": client_data['last_refill'] + (limit_config['max_tokens'] / limit_config['tokens_per_second'])
        }

# Global rate limiter instance
rate_limiter = RateLimiter()