"""
Simplified caching manager for Clyrdia CLI MVP - handles result caching.
"""

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass

from .console import console

@dataclass
class CachedResult:
    """Cached benchmark result"""
    response: str
    input_tokens: int
    output_tokens: int
    quality_scores: Dict[str, float]
    metadata: Dict[str, Any]
    cached_at: datetime

class CacheManager:
    """Simplified cache manager for MVP"""
    
    def __init__(self):
        self.cache_path = Path.home() / ".clyrdia" / "cache.db"
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_cache()
    
    def _init_cache(self):
        """Initialize cache database"""
        with sqlite3.connect(self.cache_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_key TEXT UNIQUE NOT NULL,
                    model TEXT NOT NULL,
                    test_name TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    response TEXT NOT NULL,
                    input_tokens INTEGER NOT NULL,
                    output_tokens INTEGER NOT NULL,
                    quality_scores TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    max_tokens INTEGER NOT NULL,
                    temperature REAL NOT NULL,
                    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cache_key ON cache(cache_key)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cache_model ON cache(model)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cache_expires ON cache(expires_at)")
            
            conn.commit()
    
    def _generate_cache_key(self, model: str, test_name: str, prompt: str, 
                           max_tokens: int, temperature: float) -> str:
        """Generate a unique cache key for the test"""
        content = f"{model}:{test_name}:{prompt}:{max_tokens}:{temperature}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_cached_result(self, model: str, test_name: str, prompt: str, 
                         max_tokens: int, temperature: float) -> Optional[CachedResult]:
        """Get cached result if available and not expired"""
        cache_key = self._generate_cache_key(model, test_name, prompt, max_tokens, temperature)
        
        try:
            with sqlite3.connect(self.cache_path) as conn:
                cursor = conn.execute("""
                    SELECT response, input_tokens, output_tokens, quality_scores, 
                           metadata, cached_at, expires_at
                    FROM cache 
                    WHERE cache_key = ? AND expires_at > datetime('now')
                """, (cache_key,))
                
                row = cursor.fetchone()
                if row:
                    return CachedResult(
                        response=row[0],
                        input_tokens=row[1],
                        output_tokens=row[2],
                        quality_scores=json.loads(row[3]),
                        metadata=json.loads(row[4]),
                        cached_at=datetime.fromisoformat(row[5])
                    )
        except Exception as e:
            console.print(f"[yellow]⚠️  Cache read error: {str(e)}[/yellow]")
        
        return None
    
    def cache_result(self, model: str, test_name: str, prompt: str, response: str,
                    input_tokens: int, output_tokens: int, quality_scores: Dict[str, float],
                    max_tokens: int, temperature: float, metadata: Dict[str, Any],
                    ttl_hours: int = 24 * 7) -> bool:
        """Cache a benchmark result"""
        cache_key = self._generate_cache_key(model, test_name, prompt, max_tokens, temperature)
        expires_at = datetime.now() + timedelta(hours=ttl_hours)
        
        try:
            with sqlite3.connect(self.cache_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO cache 
                    (cache_key, model, test_name, prompt, response, input_tokens, 
                     output_tokens, quality_scores, metadata, max_tokens, temperature, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cache_key, model, test_name, prompt, response, input_tokens,
                    output_tokens, json.dumps(quality_scores), json.dumps(metadata),
                    max_tokens, temperature, expires_at
                ))
                conn.commit()
                return True
        except Exception as e:
            console.print(f"[yellow]⚠️  Cache write error: {str(e)}[/yellow]")
            return False
    
    def clear_expired_cache(self) -> int:
        """Clear expired cache entries"""
        try:
            with sqlite3.connect(self.cache_path) as conn:
                cursor = conn.execute("""
                    DELETE FROM cache WHERE expires_at <= datetime('now')
                """)
                deleted_count = cursor.rowcount
                conn.commit()
                return deleted_count
        except Exception as e:
            console.print(f"[yellow]⚠️  Cache cleanup error: {str(e)}[/yellow]")
            return 0
    
    def clear_all_cache(self) -> bool:
        """Clear all cache entries"""
        try:
            with sqlite3.connect(self.cache_path) as conn:
                conn.execute("DELETE FROM cache")
                conn.commit()
                return True
        except Exception as e:
            console.print(f"[yellow]⚠️  Cache clear error: {str(e)}[/yellow]")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            with sqlite3.connect(self.cache_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM cache")
                total_entries = cursor.fetchone()[0]
                
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM cache WHERE expires_at > datetime('now')
                """)
                active_entries = cursor.fetchone()[0]
                
                cursor = conn.execute("""
                    SELECT SUM(input_tokens + output_tokens) FROM cache 
                    WHERE expires_at > datetime('now')
                """)
                total_tokens = cursor.fetchone()[0] or 0
                
                return {
                    "total_entries": total_entries,
                    "active_entries": active_entries,
                    "expired_entries": total_entries - active_entries,
                    "total_tokens_cached": total_tokens
                }
        except Exception as e:
            console.print(f"[yellow]⚠️  Cache stats error: {str(e)}[/yellow]")
            return {
                "total_entries": 0,
                "active_entries": 0,
                "expired_entries": 0,
                "total_tokens_cached": 0
            }
