"""
Simplified local database management for Clyrdia CLI MVP - handles SQLite storage.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
from datetime import datetime, timedelta

from .models import BenchmarkResult, PlanTier, UserRole
from .console import console

class LocalDatabase:
    """Local SQLite database for zero-knowledge storage - simplified for MVP"""
    
    def __init__(self):
        self.db_path = Path.home() / ".clyrdia" / "clyrdia.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema - simplified for MVP"""
        with sqlite3.connect(self.db_path) as conn:
            # Create the main benchmark_results table that the dashboard expects
            conn.execute("""
                CREATE TABLE IF NOT EXISTS benchmark_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    benchmark_id TEXT NOT NULL,
                    benchmark_name TEXT,
                    model TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    test_name TEXT NOT NULL,
                    prompt TEXT,
                    response TEXT,
                    latency_ms INTEGER,
                    input_tokens INTEGER,
                    output_tokens INTEGER,
                    cost REAL,
                    success BOOLEAN,
                    error TEXT,
                    quality_score REAL,
                    metadata TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS benchmarks (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    config TEXT,
                    tags TEXT
                )
            """)
            
            # Simplified user system - only Developer and Business tiers
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    plan_tier TEXT NOT NULL DEFAULT 'developer',
                    monthly_credits INTEGER NOT NULL DEFAULT 100,
                    credits_remaining INTEGER NOT NULL DEFAULT 100,
                    credits_reset_date TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS credit_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    transaction_type TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    benchmark_id TEXT,
                    metadata TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_benchmark_results_benchmark ON benchmark_results(benchmark_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_benchmark_results_model ON benchmark_results(model)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_benchmark_results_timestamp ON benchmark_results(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_plan_tier ON users(plan_tier)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_credits ON users(credits_remaining)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_credit_transactions_user ON credit_transactions(user_id)")
            
            conn.commit()
    
    def save_benchmark(self, benchmark_id: str, name: str, description: str, config: Dict, tags: List[str]) -> str:
        """Save benchmark configuration"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO benchmarks (id, name, description, config, tags) VALUES (?, ?, ?, ?, ?)",
                (benchmark_id, name, description, json.dumps(config), json.dumps(tags))
            )
        return benchmark_id
    
    def save_result(self, result: BenchmarkResult, benchmark_id: Optional[str] = None, cicd_run: bool = False) -> int:
        """Save benchmark result to database"""
        with sqlite3.connect(self.db_path) as conn:
            # Extract quality score (use first score if multiple, or 0.0 if none)
            quality_score = 0.0
            if result.quality_scores and len(result.quality_scores) > 0:
                if isinstance(result.quality_scores, dict):
                    quality_score = list(result.quality_scores.values())[0]
                elif isinstance(result.quality_scores, list):
                    quality_score = result.quality_scores[0]
                else:
                    quality_score = float(result.quality_scores)
            
            # Get benchmark name if available
            benchmark_name = None
            if benchmark_id:
                try:
                    name_cursor = conn.execute(
                        "SELECT name FROM benchmarks WHERE id = ?",
                        (benchmark_id,)
                    )
                    name_row = name_cursor.fetchone()
                    if name_row:
                        benchmark_name = name_row[0]
                except:
                    pass
            
            cursor = conn.execute(
                """INSERT INTO benchmark_results 
                   (benchmark_id, benchmark_name, model, provider, test_name, prompt, response, 
                    latency_ms, input_tokens, output_tokens, cost, success, error, 
                    quality_score, metadata, timestamp, cicd_run)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    benchmark_id,
                    benchmark_name,
                    result.model,
                    result.provider,
                    result.test_name,
                    result.prompt,
                    result.response,
                    result.latency_ms,
                    result.input_tokens,
                    result.output_tokens,
                    result.cost,
                    result.success,
                    result.error,
                    quality_score,
                    json.dumps(result.metadata),
                    result.timestamp,
                    cicd_run
                )
            )
            
            return cursor.lastrowid
    
    def get_recent_benchmarks(self, limit: int = 10) -> List[Dict]:
        """Get recent benchmark runs"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM benchmarks ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_model_performance(self, model: str, days: int = 30) -> pd.DataFrame:
        """Get model performance over time"""
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT timestamp, latency_ms, cost, success, quality_score
                FROM benchmark_results
                WHERE model = ? AND timestamp > datetime('now', '-{} days')
                ORDER BY timestamp
            """.format(days)
            return pd.read_sql_query(query, conn, params=(model,))
    
    def create_user(self, user_id: str, username: str, email: str, plan_tier: str = "developer") -> bool:
        """Create a new user with default plan"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Set default credits based on plan
                monthly_credits = self._get_default_credits(plan_tier)
                credits_reset_date = self._get_next_reset_date()
                
                conn.execute("""
                    INSERT INTO users (id, username, email, plan_tier, monthly_credits, credits_remaining, credits_reset_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, username, email, plan_tier, monthly_credits, monthly_credits, credits_reset_date))
                
                conn.commit()
                return True
        except Exception as e:
            console.print(f"[red]Error creating user: {str(e)}[/red]")
            return False
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            console.print(f"[red]Error getting user: {str(e)}[/red]")
            return None
    
    def update_user_plan(self, user_id: str, new_plan: str) -> bool:
        """Update user's plan tier and reset credits"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                monthly_credits = self._get_default_credits(new_plan)
                credits_reset_date = self._get_next_reset_date()
                
                conn.execute("""
                    UPDATE users 
                    SET plan_tier = ?, monthly_credits = ?, credits_remaining = ?, credits_reset_date = ?
                    WHERE id = ?
                """, (new_plan, monthly_credits, monthly_credits, credits_reset_date, user_id))
                
                conn.commit()
                return True
        except Exception as e:
            console.print(f"[red]Error updating user plan: {str(e)}[/red]")
            return False
    
    def deduct_credits(self, user_id: str, amount: int, description: str, benchmark_id: str = None) -> bool:
        """Deduct credits from user account"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check current balance
                cursor = conn.execute("SELECT credits_remaining FROM users WHERE id = ?", (user_id,))
                current_credits = cursor.fetchone()[0]
                
                if current_credits < amount:
                    return False  # Insufficient credits
                
                # Deduct credits
                conn.execute("""
                    UPDATE users 
                    SET credits_remaining = credits_remaining - ?, last_active = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (amount, user_id))
                
                # Record transaction
                conn.execute("""
                    INSERT INTO credit_transactions (user_id, transaction_type, amount, description, benchmark_id)
                    VALUES (?, 'debit', ?, ?, ?)
                """, (user_id, amount, description, benchmark_id))
                
                conn.commit()
                return True
        except Exception as e:
            console.print(f"[red]Error deducting credits: {str(e)}[/red]")
            return False
    
    def add_credits(self, user_id: str, amount: int, description: str) -> bool:
        """Add credits to user account"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Add credits
                conn.execute("""
                    UPDATE users 
                    SET credits_remaining = credits_remaining + ?, last_active = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (amount, user_id))
                
                # Record transaction
                conn.execute("""
                    INSERT INTO credit_transactions (user_id, transaction_type, amount, description)
                    VALUES (?, 'credit', ?, ?)
                """, (user_id, amount, description))
                
                conn.commit()
                return True
        except Exception as e:
            console.print(f"[red]Error adding credits: {str(e)}[/red]")
            return False
    
    def get_credit_history(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get credit transaction history for a user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM credit_transactions 
                    WHERE user_id = ? AND timestamp >= datetime('now', '-{} days')
                    ORDER BY timestamp DESC
                """.format(days), (user_id,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            console.print(f"[red]Error getting credit history: {str(e)}[/red]")
            return []
    
    def reset_monthly_credits(self) -> int:
        """Reset monthly credits for all users (called by cron job)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get users whose credits need to be reset
                cursor = conn.execute("""
                    SELECT id, plan_tier FROM users 
                    WHERE credits_reset_date <= date('now') AND is_active = 1
                """)
                
                reset_count = 0
                for row in cursor.fetchall():
                    user_id, plan_tier = row
                    monthly_credits = self._get_default_credits(plan_tier)
                    next_reset = self._get_next_reset_date()
                    
                    conn.execute("""
                        UPDATE users 
                        SET credits_remaining = ?, credits_reset_date = ?
                        WHERE id = ?
                    """, (monthly_credits, next_reset, user_id))
                    
                    reset_count += 1
                
                conn.commit()
                return reset_count
        except Exception as e:
            console.print(f"[red]Error resetting monthly credits: {str(e)}[/red]")
            return 0
    
    def _get_default_credits(self, plan_tier: str) -> int:
        """Get default monthly credits for a plan tier"""
        credit_map = {
            "developer": 100,
            "business": 25000
        }
        return credit_map.get(plan_tier, 100)
    
    def _get_next_reset_date(self) -> str:
        """Get the next monthly reset date"""
        now = datetime.now()
        if now.day >= 25:  # Reset on 25th of each month
            next_month = now.replace(day=25) + timedelta(days=32)
            next_month = next_month.replace(day=25)
        else:
            next_month = now.replace(day=25)
        
        return next_month.strftime("%Y-%m-%d")
