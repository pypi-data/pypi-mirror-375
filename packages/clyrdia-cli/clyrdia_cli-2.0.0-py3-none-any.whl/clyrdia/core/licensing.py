"""
Simplified licensing management for Clyrdia CLI MVP - handles authentication and credit system.
"""

import os
import json
import asyncio
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta

from .models import UserStatus, PlanTier, UserRole
from .database import LocalDatabase
from .console import console

class LicensingManager:
    """Simplified licensing manager for MVP - two-tier system only"""
    
    def __init__(self):
        self.db = LocalDatabase()
        # Initialize config directory and file paths
        self.config_dir = Path.home() / ".clyrdia"
        self.config_file = self.config_dir / "config.json"
        self.api_key = self._load_api_key()
        
        # Security: Rate limiting and abuse prevention
        self.rate_limit_file = self.config_dir / "rate_limit.json"
        self.max_requests_per_minute = 10
        self.max_requests_per_hour = 100
        
    def _load_api_key(self) -> Optional[str]:
        """Load API key from config file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('api_key')
            except (json.JSONDecodeError, KeyError):
                pass
        return None
    
    def is_first_run(self) -> bool:
        """Check if this is the user's first run"""
        return not self.config_file.exists()
    
    def _save_api_key(self, api_key: str):
        """Save API key to config file with secure permissions"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        config = {'api_key': api_key}
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Set secure file permissions (600)
        os.chmod(self.config_file, 0o600)
    
    async def _make_api_request(self, endpoint: str, method: str = "GET", 
                         data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated API request to Clyrdia backend"""
        if not self.api_key:
            raise Exception("No API key configured. Please run 'clyrdia-cli login' first.")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Import config here to avoid circular imports
        from ..config import config
        url = config.get_api_url(endpoint)
        
        try:
            import httpx
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method == "GET":
                    response = await client.get(url, headers=headers)
                elif method == "POST":
                    response = await client.post(url, headers=headers, json=data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise Exception("Invalid API key. Please run 'clyrdia-cli login' again.")
            elif e.response.status_code == 402:
                # Return payment required response with error details
                error_data = e.response.json() if e.response.content else {}
                error_data["error_type"] = "payment_required"
                return error_data
            else:
                raise Exception(f"API request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"API request failed: {str(e)}")
    
    async def login(self, api_key: str) -> UserStatus:
        """Login with API key and validate subscription"""
        # Test the API key by calling the status endpoint
        self._save_api_key(api_key)
        self.api_key = api_key
        
        try:
            status = await self.get_status()
            return status
        except Exception as e:
            # Remove invalid key
            self._remove_api_key()
            raise e
    
    async def get_status(self) -> UserStatus:
        """Get current user status and credit balance from Clyrdia.com backend"""
        if not self.api_key:
            raise Exception("No API key configured. Please run 'clyrdia-cli login' first.")
        
        # Validate API key format for security
        if not self._validate_api_key_format(self.api_key):
            self._log_security_event("invalid_api_key_format", "Invalid API key format attempted")
            raise Exception("Invalid API key format. Please check your key and try again.")
        
        # Check rate limits
        if not self._check_rate_limit():
            self._log_security_event("rate_limit_exceeded", "Rate limit exceeded")
            raise Exception("Rate limit exceeded. Please try again later.")
        
        # Always call the backend /api/cli/status endpoint to prevent bypass
        try:
            response = await self._make_secure_api_request("/cli/status")
            self._log_security_event("api_call_success", "Successful API call to get_status")
            return self._create_user_status_from_api(response)
        except Exception as e:
            # Log security events
            if "401" in str(e) or "Unauthorized" in str(e):
                self._log_security_event("unauthorized_access", "Invalid API key used")
                raise Exception("Invalid API key. Please run 'clyrdia-cli login' again.")
            elif "402" in str(e) or "Payment Required" in str(e):
                # User is authenticated but out of credits
                response = e.response.json() if hasattr(e, 'response') else {}
                return self._create_user_status_from_api(response)
            elif "403" in str(e) or "Forbidden" in str(e):
                self._log_security_event("access_denied", "Access denied by server")
                raise Exception("Access denied. Your account may be suspended. Please contact support.")
            elif "429" in str(e) or "Rate Limited" in str(e):
                self._log_security_event("server_rate_limit", "Server rate limit exceeded")
                raise Exception("Rate limit exceeded. Please try again later.")
            else:
                self._log_security_event("api_error", f"API error: {str(e)}")
                raise Exception(f"Could not verify authentication status: {str(e)}")
    
    def _validate_api_key_format(self, api_key: str) -> bool:
        """Validate API key format for security"""
        if not api_key or not isinstance(api_key, str):
            return False
        
        # API key must be at least 32 characters and start with 'cly' or 'clyrdia'
        if len(api_key) < 32 or not (api_key.startswith('cly_') or api_key.startswith('clyrdia_')):
            return False
        
        # Check for valid characters (alphanumeric, underscore, hyphen)
        import re
        if not re.match(r'^(cly|clyrdia)_[a-zA-Z0-9_-]+$', api_key):
            return False
        
        return True
    
    def _make_secure_api_request(self, endpoint: str) -> Dict[str, Any]:
        """Make secure API request to Clyrdia.com backend"""
        import aiohttp
        import ssl
        import asyncio
        
        async def _make_request():
            # Create SSL context for secure connections
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = True
            ssl_context.verify_mode = ssl.CERT_REQUIRED
            
            # Add security headers
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'User-Agent': 'Clyrdia-CLI/2.0.0',
                'Content-Type': 'application/json',
                'X-Client-Version': '2.0.0',
                'X-Platform': 'cli'
            }
            
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                connector=aiohttp.TCPConnector(ssl=ssl_context)
            ) as session:
                async with session.get(
                    f'https://api.clyrdia.com/v1{endpoint}',
                    headers=headers
                ) as response:
                    if response.status == 401:
                        raise Exception("401 Unauthorized")
                    elif response.status == 403:
                        raise Exception("403 Forbidden")
                    elif response.status == 429:
                        raise Exception("429 Rate Limited")
                    elif response.status != 200:
                        raise Exception(f"{response.status} API Error")
                    
                    return await response.json()
        
        # Run the async request
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        try:
            return loop.run_until_complete(_make_request())
        finally:
            if loop.is_running():
                loop.close()
    
    def _get_user_id_from_api_key(self) -> Optional[str]:
        """Extract user ID from API key (simplified for demo)"""
        if not self.api_key:
            return None
        
        # In a real implementation, this would decode the JWT or hash
        # For now, we'll use a simple hash-based approach
        import hashlib
        user_hash = hashlib.md5(self.api_key.encode()).hexdigest()[:8]
        return f"user_{user_hash}"
    
    def _create_user_status_from_api(self, response: Dict[str, Any]) -> UserStatus:
        """Create UserStatus from API response"""
        # Handle different API response formats
        if "error" in response:
            # This is an error response, create a minimal status
            return UserStatus(
                user_name="Unknown",
                plan=PlanTier.DEVELOPER,
                credits_remaining=0,
                credits_monthly_limit=100,
                resets_on=self._get_next_reset_date(),
                api_key=self.api_key,
                team_id=None,
                role=None,
                team_name=None,
                max_team_members=None,
                has_cicd_access=False
            )
        
        plan_str = response.get("plan", "developer")
        try:
            plan = PlanTier(plan_str)
        except ValueError:
            plan = PlanTier.DEVELOPER
        
        role = None
        if "role" in response:
            try:
                role = UserRole(response["role"])
            except ValueError:
                role = UserRole.MEMBER
        
        return UserStatus(
            user_name=response.get("user_name", "Unknown"),
            plan=plan,
            credits_remaining=response.get("credits_remaining", 0),
            credits_monthly_limit=response.get("credits_monthly_limit", 100),
            resets_on=response.get("resets_on", self._get_next_reset_date()),
            api_key=self.api_key,
            team_id=response.get("team_id"),
            role=role,
            team_name=response.get("team_name"),
            max_team_members=response.get("max_team_members"),
            has_cicd_access=response.get("has_cicd_access", False)
        )
    
    # Security: Mock authentication methods removed for production
    
    def _check_rate_limit(self) -> bool:
        """Check if user is within rate limits"""
        import time
        current_time = time.time()
        
        # Load rate limit data
        rate_data = {"requests": []}
        if self.rate_limit_file.exists():
            try:
                with open(self.rate_limit_file, 'r') as f:
                    rate_data = json.load(f)
            except (json.JSONDecodeError, KeyError):
                rate_data = {"requests": []}
        
        # Clean old requests (older than 1 hour)
        one_hour_ago = current_time - 3600
        rate_data["requests"] = [req_time for req_time in rate_data["requests"] if req_time > one_hour_ago]
        
        # Check hourly limit
        if len(rate_data["requests"]) >= self.max_requests_per_hour:
            return False
        
        # Check minute limit
        one_minute_ago = current_time - 60
        recent_requests = [req_time for req_time in rate_data["requests"] if req_time > one_minute_ago]
        if len(recent_requests) >= self.max_requests_per_minute:
            return False
        
        # Add current request
        rate_data["requests"].append(current_time)
        
        # Save updated rate data
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.rate_limit_file, 'w') as f:
            json.dump(rate_data, f)
        
        return True
    
    def _log_security_event(self, event_type: str, details: str):
        """Log security events for auditing"""
        import time
        import hashlib
        log_entry = {
            "timestamp": time.time(),
            "event_type": event_type,
            "details": details,
            "api_key_hash": hashlib.sha256(self.api_key.encode()).hexdigest()[:16] if self.api_key else "none"
        }
        
        # Log to security file
        security_log_file = self.config_dir / "security.log"
        with open(security_log_file, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def _get_next_reset_date(self) -> str:
        """Get the next monthly reset date"""
        now = datetime.now()
        if now.day >= 25:  # Reset on 25th of each month
            next_month = now.replace(day=25) + timedelta(days=32)
            next_month = next_month.replace(day=25)
        else:
            next_month = now.replace(day=25)
        
        return next_month.strftime("%Y-%m-%d")
    
    def _remove_api_key(self):
        """Remove API key from config"""
        if self.config_file.exists():
            self.config_file.unlink()
        self.api_key = None
    
    def logout(self):
        """Logout and remove API key"""
        self._remove_api_key()
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated by validating against server"""
        # Security: No mock authentication modes in production
        
        if not self.api_key:
            return False
        
        try:
            # Try to get user status from server to validate the API key
            # This prevents users from creating fake API key files
            import asyncio
            import signal
            
            # Set a timeout to prevent hanging on network issues
            async def check_auth_with_timeout():
                try:
                    user_status = await self.get_status()
                    return user_status is not None and user_status.credits_remaining >= 0
                except asyncio.TimeoutError:
                    return False
            
            # Run with 10 second timeout
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    asyncio.wait_for(check_auth_with_timeout(), timeout=10.0)
                )
                return result
            finally:
                loop.close()
                
        except Exception:
            # If server validation fails, user is not authenticated
            return False
    
    def get_plan_features(self, plan: PlanTier) -> Dict[str, Any]:
        """Get features for a specific plan tier"""
        # Security: No mock authentication modes in production
        
        # Simplified two-tier system
        if plan == PlanTier.BUSINESS:
            return {
                "monthly_credits": 25000,
                "max_users": 10,
                "has_cicd": True,
                "has_advanced_reporting": True,
                "has_team_management": True,
                "has_priority_support": True,
                "price_usd": 500
            }
        else:  # DEVELOPER
            return {
                "monthly_credits": 100,
                "max_users": 1,
                "has_cicd": False,
                "has_advanced_reporting": False,
                "has_team_management": False,
                "has_priority_support": False,
                "price_usd": 0
            }
    
    def can_access_cicd(self, user_status: UserStatus) -> bool:
        """Check if user can access CI/CD features"""
        return user_status.has_cicd_access and user_status.plan == PlanTier.BUSINESS
    
    def check_credits(self, required_credits: int = 1) -> tuple[bool, int]:
        """Check if user has enough credits for operation"""
        try:
            user_id = self._get_user_id_from_api_key()
            if not user_id:
                return False, 0
            
            user_data = self.db.get_user(user_id)
            if not user_data:
                return False, 0
            
            if user_data['credits_remaining'] >= required_credits:
                return True, user_data['credits_remaining']
            else:
                return False, user_data['credits_remaining']
        except Exception as e:
            console.print(f"[red]❌ Could not check credit balance: {str(e)}[/red]")
            return False, 0
    
    def deduct_credits(self, amount: int, description: str = "Benchmark operation") -> bool:
        """Deduct credits from user account"""
        try:
            user_id = self._get_user_id_from_api_key()
            if not user_id:
                return False
            
            return self.db.deduct_credits(user_id, amount, description)
        except Exception as e:
            console.print(f"[red]❌ Could not deduct credits: {str(e)}[/red]")
            return False
