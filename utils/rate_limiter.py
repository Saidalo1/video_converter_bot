"""
Rate limiting module to prevent spam and abuse.
"""
import time
from collections import defaultdict
from typing import Dict, Tuple

from utils.logger import logger
from utils.config import config


class RateLimiter:
    """
    Rate limiter to prevent spam and abuse.
    Tracks request counts per user and enforces limits.
    """
    
    def __init__(self):
        # Dictionary to store user request timestamps
        # {user_id: [timestamp1, timestamp2, ...]}
        self._user_requests: Dict[int, list] = defaultdict(list)
        self._window_seconds = 60  # 1-minute window
        self._max_requests = config.MAX_REQUESTS_PER_MINUTE
    
    def _cleanup_old_requests(self, user_id: int) -> None:
        """
        Remove requests older than the time window for a specific user.
        
        Args:
            user_id: Telegram user ID
        """
        current_time = time.time()
        window_start = current_time - self._window_seconds
        
        # Filter out timestamps older than the window
        self._user_requests[user_id] = [
            timestamp for timestamp in self._user_requests[user_id]
            if timestamp > window_start
        ]
    
    def check_rate_limit(self, user_id: int) -> Tuple[bool, int]:
        """
        Check if a user has exceeded their rate limit.
        
        Args:
            user_id: Telegram user ID
        
        Returns:
            Tuple of (is_allowed, requests_remaining)
        """
        # Skip rate limiting for admin users
        if user_id in config.ADMIN_USER_IDS:
            return True, self._max_requests
        
        # Clean up old requests
        self._cleanup_old_requests(user_id)
        
        # Count current requests within the window
        current_requests = len(self._user_requests[user_id])
        
        # Check if user has exceeded limit
        is_allowed = current_requests < self._max_requests
        requests_remaining = max(0, self._max_requests - current_requests)
        
        # If allowed, record this request
        if is_allowed:
            self._user_requests[user_id].append(time.time())
            logger.info(f"Rate limit check for user {user_id}: {current_requests+1}/{self._max_requests} requests")
        else:
            logger.warning(f"Rate limit exceeded for user {user_id}: {current_requests}/{self._max_requests} requests")
        
        return is_allowed, requests_remaining


# Create a global instance
rate_limiter = RateLimiter()
