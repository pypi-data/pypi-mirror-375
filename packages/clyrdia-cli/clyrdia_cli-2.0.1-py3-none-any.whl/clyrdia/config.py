"""
Configuration management for Clyrdia CLI MVP
"""

import os
from typing import Optional

class Config:
    """Simple configuration management for MVP"""
    
    # API Configuration
    API_BASE_URL = os.getenv("CLYRDIA_API_BASE_URL", "https://api.clyrdia.com")
    
    # Default settings
    DEFAULT_CACHE_TTL_HOURS = 24 * 7  # 1 week
    DEFAULT_QUALITY_GATE_THRESHOLD = 0.7
    DEFAULT_COST_THRESHOLD = 10.0
    
    @classmethod
    def get_api_url(cls, endpoint: str) -> str:
        """Get full API URL for an endpoint"""
        if endpoint.startswith('/'):
            endpoint = endpoint[1:]
        return f"{cls.API_BASE_URL}/{endpoint}"
    
    @classmethod
    def get_dashboard_port(cls) -> int:
        """Get dashboard port from environment or default"""
        return int(os.getenv("CLYRDIA_DASHBOARD_PORT", "3000"))
    
    @classmethod
    def get_dashboard_host(cls) -> str:
        """Get dashboard host from environment or default"""
        return os.getenv("CLYRDIA_DASHBOARD_HOST", "localhost")

# Create global config instance
config = Config()