from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler as rate_limit_handler

# Central limiter used across the app and routers
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])  # default global limit

__all__ = ["limiter", "RateLimitExceeded", "rate_limit_handler"]