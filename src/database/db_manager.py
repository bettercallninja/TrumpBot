#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ù¾ÛŒØ´Ø±ÙØªÙ‡â€ŒØªØ±ÛŒÙ† Ù…Ø¯ÛŒØ±ÛŒØª Ù¾Ø§ÛŒÚ¯Ø§Ù‡ Ø¯Ø§Ø¯Ù‡ Ø¨Ø§ Ù¾Ø´ØªÛŒØ¨Ø§Ù†ÛŒ Ú©Ø§Ù…Ù„ Ø§Ø² Ø²Ø¨Ø§Ù† ÙØ§Ø±Ø³ÛŒ
Enhanced Database Manager with comprehensive Persian language support and advanced functionality
"""

import os
import logging
import time
import json
import asyncio
from typing import Any, Dict, List, Optional, Tuple, Union, AsyncGenerator
from datetime import datetime, timedelta
from psycopg_pool import AsyncConnectionPool
from dotenv import load_dotenv
import psycopg
from dataclasses import dataclass
from enum import Enum

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

# Database configuration with enhanced settings
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/trumpbot")
DB_POOL_MIN_SIZE = int(os.getenv("DB_POOL_MIN_SIZE", "2"))
DB_POOL_MAX_SIZE = int(os.getenv("DB_POOL_MAX_SIZE", "20"))
DB_COMMAND_TIMEOUT = int(os.getenv("DB_COMMAND_TIMEOUT", "60"))
DB_RETRY_ATTEMPTS = int(os.getenv("DB_RETRY_ATTEMPTS", "3"))

pool: Optional[AsyncConnectionPool] = None

class DatabaseError(Exception):
    """Ø®Ø·Ø§ÛŒ Ù¾Ø§ÛŒÚ¯Ø§Ù‡ Ø¯Ø§Ø¯Ù‡ - Database Error"""
    pass

class UserNotFoundError(DatabaseError):
    """Ú©Ø§Ø±Ø¨Ø± ÛŒØ§ÙØª Ù†Ø´Ø¯ - User Not Found Error"""
    pass

class TransactionError(DatabaseError):
    """Ø®Ø·Ø§ÛŒ ØªØ±Ø§Ú©Ù†Ø´ - Transaction Error"""
    pass

class QueryType(Enum):
    """Ø§Ù†ÙˆØ§Ø¹ Ú©ÙˆØ¦Ø±ÛŒ - Query Types"""
    SELECT = "SELECT"
    INSERT = "INSERT" 
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    TRANSACTION = "TRANSACTION"

@dataclass
class UserStats:
    """Ø¢Ù…Ø§Ø± Ú©Ø§Ø±Ø¨Ø± - User Statistics"""
    user_id: int
    chat_id: int
    level: int
    score: int
    hp: int
    tg_stars: int
    total_attacks: int
    total_damage: int
    times_attacked: int
    damage_taken: int
    items_owned: int
    medals_spent: int
    created_at: datetime
    last_active: datetime
    language: str
    # Additional fields for helpers.py compatibility
    experience: int = 0
    join_date: datetime = None
    attacks_made: int = 0
    attacks_received: int = 0
    victories: int = 0
    defeats: int = 0
    shields_used: int = 0
    items_bought: int = 0
    activity_points: int = 0

@dataclass
class ChatStats:
    """Ø¢Ù…Ø§Ø± Ú†Øª - Chat Statistics"""
    chat_id: int
    total_players: int
    total_attacks: int
    total_damage: int
    most_active_player: Optional[str]
    highest_level: int
    total_items_purchased: int
    created_at: datetime
    last_active: datetime

async def initialize_pool() -> None:
    """Ù…Ù‚Ø¯Ø§Ø±Ø¯Ù‡ÛŒ Ø§ÙˆÙ„ÛŒÙ‡ Ø§Ø³ØªØ®Ø± Ø§ØªØµØ§Ù„Ø§Øª - Initialize the database connection pool"""
    global pool
    if pool is None:
        try:
            pool = AsyncConnectionPool(
                min_size=DB_POOL_MIN_SIZE, 
                max_size=DB_POOL_MAX_SIZE, 
                conninfo=DATABASE_URL,
                timeout=DB_COMMAND_TIMEOUT,
                open=False  # Don't open in constructor to avoid deprecation warning
            )
            # Open the pool properly using await
            await pool.open()
            logger.info(f"Database connection pool initialized: min={DB_POOL_MIN_SIZE}, max={DB_POOL_MAX_SIZE}")
            logger.info(f"Ø§Ø³ØªØ®Ø± Ø§ØªØµØ§Ù„Ø§Øª Ù¾Ø§ÛŒÚ¯Ø§Ù‡ Ø¯Ø§Ø¯Ù‡ Ù…Ù‚Ø¯Ø§Ø±Ø¯Ù‡ÛŒ Ø´Ø¯: Ú©Ù…ÛŒÙ†Ù‡={DB_POOL_MIN_SIZE}, Ø¨ÛŒØ´ÛŒÙ†Ù‡={DB_POOL_MAX_SIZE}")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            logger.error(f"Ø®Ø·Ø§ Ø¯Ø± Ù…Ù‚Ø¯Ø§Ø±Ø¯Ù‡ÛŒ Ø§Ø³ØªØ®Ø± Ù¾Ø§ÛŒÚ¯Ø§Ù‡ Ø¯Ø§Ø¯Ù‡: {e}")
            raise DatabaseError(f"Database initialization failed: {e}")

class DBManager:
    """
    Ù…Ø¯ÛŒØ± Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ù¾Ø§ÛŒÚ¯Ø§Ù‡ Ø¯Ø§Ø¯Ù‡ Ø¨Ø§ Ù‚Ø§Ø¨Ù„ÛŒØªâ€ŒÙ‡Ø§ÛŒ Ú©Ø§Ù…Ù„
    Advanced Database Manager with comprehensive functionality and Persian support
    """
    
    def __init__(self):
        self._pool = pool
        self._query_cache: Dict[str, Any] = {}
        self._cache_ttl = 300  # 5 minutes cache TTL
        
    async def ensure_pool(self) -> None:
        """Ø§Ø·Ù…ÛŒÙ†Ø§Ù† Ø§Ø² ÙˆØ¬ÙˆØ¯ Ø§Ø³ØªØ®Ø± Ø§ØªØµØ§Ù„Ø§Øª - Ensure connection pool exists"""
        if not self._pool:
            await initialize_pool()
            self._pool = pool
    
    async def db(self, query: str, params: Optional[Tuple] = None, fetch: Optional[str] = None, 
                retry_count: int = 0) -> Any:
        """
        Ø§Ø¬Ø±Ø§ÛŒ Ú©ÙˆØ¦Ø±ÛŒ Ù¾Ø§ÛŒÚ¯Ø§Ù‡ Ø¯Ø§Ø¯Ù‡ Ø¨Ø§ Ù…Ø¯ÛŒØ±ÛŒØª Ø®Ø·Ø§ Ùˆ ØªÙ„Ø§Ø´ Ù…Ø¬Ø¯Ø¯
        Execute database query with error handling and retry logic
        
        Args:
            query: SQL query to execute
            params: Parameters for the query
            fetch: Type of fetch ('one', 'all', 'one_dict', 'all_dicts', 'count')
            retry_count: Current retry attempt
            
        Returns:
            Query results based on fetch type
        """
        await self.ensure_pool()
        
        try:
            async with self._pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query, params)
                    
                    if fetch == "one":
                        return await cur.fetchone()
                    elif fetch == "all":
                        return await cur.fetchall()
                    elif fetch == "one_dict":
                        row = await cur.fetchone()
                        if row:
                            columns = [desc[0] for desc in cur.description]
                            return dict(zip(columns, row))
                        return None
                    elif fetch == "all_dicts":
                        rows = await cur.fetchall()
                        if rows:
                            columns = [desc[0] for desc in cur.description]
                            return [dict(zip(columns, row)) for row in rows]
                        return []
                    elif fetch == "count":
                        result = await cur.fetchone()
                        return result[0] if result else 0
                    return None
                    
        except psycopg.OperationalError as e:
            if retry_count < DB_RETRY_ATTEMPTS:
                logger.warning(f"Database connection error, retrying... ({retry_count + 1}/{DB_RETRY_ATTEMPTS})")
                logger.warning(f"Ø®Ø·Ø§ÛŒ Ø§ØªØµØ§Ù„ Ù¾Ø§ÛŒÚ¯Ø§Ù‡ Ø¯Ø§Ø¯Ù‡ØŒ ØªÙ„Ø§Ø´ Ù…Ø¬Ø¯Ø¯... ({retry_count + 1}/{DB_RETRY_ATTEMPTS})")
                await asyncio.sleep(1 * (retry_count + 1))  # Exponential backoff
                return await self.db(query, params, fetch, retry_count + 1)
            else:
                logger.error(f"Database connection failed after {DB_RETRY_ATTEMPTS} attempts")
                logger.error(f"Ø§ØªØµØ§Ù„ Ù¾Ø§ÛŒÚ¯Ø§Ù‡ Ø¯Ø§Ø¯Ù‡ Ù¾Ø³ Ø§Ø² {DB_RETRY_ATTEMPTS} ØªÙ„Ø§Ø´ Ù†Ø§Ù…ÙˆÙÙ‚ Ø¨ÙˆØ¯")
                raise DatabaseError(f"Database connection failed: {e}")
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            logger.error(f"Ø®Ø·Ø§ÛŒ Ù¾Ø§ÛŒÚ¯Ø§Ù‡ Ø¯Ø§Ø¯Ù‡: {str(e)}")
            raise DatabaseError(f"Query execution failed: {e}")
    
    async def transaction(self, queries: List[Tuple[str, Optional[Tuple]]]) -> bool:
        """
        Ø§Ø¬Ø±Ø§ÛŒ Ú†Ù†Ø¯ÛŒÙ† Ú©ÙˆØ¦Ø±ÛŒ Ø¯Ø± ÛŒÚ© ØªØ±Ø§Ú©Ù†Ø´
        Execute multiple queries in a transaction
        
        Args:
            queries: List of (query, params) tuples
            
        Returns:
            True if transaction succeeded, False otherwise
        """
        await self.ensure_pool()
        
        try:
            async with self._pool.connection() as conn:
                async with conn.transaction():
                    for query, params in queries:
                        await conn.execute(query, params)
            logger.info(f"Transaction completed successfully with {len(queries)} queries")
            logger.info(f"ØªØ±Ø§Ú©Ù†Ø´ Ø¨Ø§ Ù…ÙˆÙÙ‚ÛŒØª Ø¨Ø§ {len(queries)} Ú©ÙˆØ¦Ø±ÛŒ Ú©Ø§Ù…Ù„ Ø´Ø¯")
            return True
        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            logger.error(f"ØªØ±Ø§Ú©Ù†Ø´ Ù†Ø§Ù…ÙˆÙÙ‚ Ø¨ÙˆØ¯: {e}")
            raise TransactionError(f"Transaction failed: {e}")

    # =============================================================================
    # Ù…Ø¯ÛŒØ±ÛŒØª Ú©Ø§Ø±Ø¨Ø±Ø§Ù† - User Management
    # =============================================================================
    
    async def get_user(self, chat_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Ø¯Ø±ÛŒØ§ÙØª Ø§Ø·Ù„Ø§Ø¹Ø§Øª Ú©Ø§Ø±Ø¨Ø± - Get user data from the database"""
        try:
            return await self.db(
                "SELECT * FROM players WHERE chat_id=%s AND user_id=%s", 
                (chat_id, user_id), 
                fetch="one_dict"
            )
        except Exception as e:
            logger.error(f"Error getting user {user_id} in chat {chat_id}: {e}")
            return None
    
    async def create_user(self, chat_id: int, user_id: int, first_name: str, 
                         username: Optional[str] = None, language: str = "en") -> bool:
        """Ø§ÛŒØ¬Ø§Ø¯ Ú©Ø§Ø±Ø¨Ø± Ø¬Ø¯ÛŒØ¯ - Create new user"""
        try:
            current_time = int(time.time())
            await self.db("""
                INSERT INTO players (chat_id, user_id, first_name, username, language, last_active)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (chat_id, user_id) DO UPDATE SET
                    first_name = EXCLUDED.first_name,
                    username = EXCLUDED.username,
                    last_active = EXCLUDED.last_active
            """, (chat_id, user_id, first_name, username, language, current_time))
            
            logger.info(f"User created/updated: {first_name} ({user_id}) in chat {chat_id}")
            logger.info(f"Ú©Ø§Ø±Ø¨Ø± Ø§ÛŒØ¬Ø§Ø¯/Ø¨Ù‡â€ŒØ±ÙˆØ²Ø±Ø³Ø§Ù†ÛŒ Ø´Ø¯: {first_name} ({user_id}) Ø¯Ø± Ú†Øª {chat_id}")
            return True
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            logger.error(f"Ø®Ø·Ø§ Ø¯Ø± Ø§ÛŒØ¬Ø§Ø¯ Ú©Ø§Ø±Ø¨Ø±: {e}")
            return False
    
    async def get_chat_language(self, chat_id: int) -> str:
        """Ø¯Ø±ÛŒØ§ÙØª Ø²Ø¨Ø§Ù† Ù¾ÛŒØ´â€ŒÙØ±Ø¶ Ú†Øª - Get chat default language"""
        try:
            result = await self.db(
                "SELECT language FROM groups WHERE chat_id = %s",
                (chat_id,),
                fetch="one_dict"
            )
            return result.get('language', 'en') if result else 'en'
        except Exception as e:
            logger.error(f"Error getting chat language: {e}")
            return 'en'
    
    async def update_user_activity(self, chat_id: int = None, user_id: int = None, activity_type: str = None, activity_data: Dict = None, **kwargs) -> bool:
        """Ø¨Ù‡â€ŒØ±ÙˆØ²Ø±Ø³Ø§Ù†ÛŒ ÙØ¹Ø§Ù„ÛŒØª Ú©Ø§Ø±Ø¨Ø± - Update user activity"""
        try:
            # Handle flexible parameter passing
            if chat_id is None and 'chat_id' in kwargs:
                chat_id = kwargs['chat_id']
            if user_id is None and 'user_id' in kwargs:
                user_id = kwargs['user_id']
            
            if not chat_id or not user_id:
                logger.error("Both chat_id and user_id are required for update_user_activity")
                return False
                
            current_time = int(time.time())
            result = await self.db(
                "UPDATE players SET last_active = %s WHERE chat_id = %s AND user_id = %s",
                (current_time, chat_id, user_id)
            )
            
            # Log activity type if provided for analytics
            if activity_type:
                logger.debug(f"User activity recorded: {activity_type} for user {user_id} in chat {chat_id}")
                if activity_data:
                    logger.debug(f"Activity data: {activity_data}")
            
            return True
        except Exception as e:
            logger.error(f"Error updating user activity: {e}")
            return False
    
    async def get_user_stats(self, chat_id: int, user_id: int) -> Optional[UserStats]:
        """Ø¯Ø±ÛŒØ§ÙØª Ø¢Ù…Ø§Ø± Ú©Ø§Ù…Ù„ Ú©Ø§Ø±Ø¨Ø± - Get comprehensive user statistics"""
        try:
            # Get basic user data
            user_data = await self.get_user(chat_id, user_id)
            if not user_data:
                return None
            
            # Get attack statistics
            attack_stats = await self.db("""
                SELECT 
                    COUNT(*) as total_attacks,
                    COALESCE(SUM(damage), 0) as total_damage
                FROM attacks 
                WHERE chat_id = %s AND attacker_id = %s
            """, (chat_id, user_id), fetch="one_dict")
            
            # Get defense statistics
            defense_stats = await self.db("""
                SELECT 
                    COUNT(*) as times_attacked,
                    COALESCE(SUM(damage), 0) as damage_taken
                FROM attacks 
                WHERE chat_id = %s AND victim_id = %s
            """, (chat_id, user_id), fetch="one_dict")
            
            # Get inventory count
            items_count = await self.db("""
                SELECT COUNT(*) FROM inventories 
                WHERE chat_id = %s AND user_id = %s AND qty > 0
            """, (chat_id, user_id), fetch="count")
            
            # Get spending statistics
            medals_spent = await self.db("""
                SELECT COALESCE(SUM(price), 0) FROM purchases 
                WHERE chat_id = %s AND user_id = %s
            """, (chat_id, user_id), fetch="count")
            
            return UserStats(
                user_id=user_id,
                chat_id=chat_id,
                level=user_data.get('level', 1),
                score=user_data.get('score', 0),
                hp=user_data.get('hp', 100),
                tg_stars=user_data.get('tg_stars', 0),
                total_attacks=attack_stats.get('total_attacks', 0),
                total_damage=attack_stats.get('total_damage', 0),
                times_attacked=defense_stats.get('times_attacked', 0),
                damage_taken=defense_stats.get('damage_taken', 0),
                items_owned=items_count,
                medals_spent=medals_spent,
                created_at=datetime.fromtimestamp(user_data.get('created_at', time.time())),
                last_active=datetime.fromtimestamp(user_data.get('last_active', time.time())),
                language=user_data.get('language', 'en')
            )
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return None
    
    async def update_user_language(self, chat_id: int, user_id: int, language: str) -> bool:
        """Ø¨Ù‡â€ŒØ±ÙˆØ²Ø±Ø³Ø§Ù†ÛŒ Ø²Ø¨Ø§Ù† Ú©Ø§Ø±Ø¨Ø± - Update user language preference"""
        try:
            await self.db(
                "UPDATE players SET language = %s WHERE chat_id = %s AND user_id = %s",
                (language, chat_id, user_id)
            )
            logger.info(f"Language updated for user {user_id}: {language}")
            logger.info(f"Ø²Ø¨Ø§Ù† Ú©Ø§Ø±Ø¨Ø± {user_id} Ø¨Ù‡â€ŒØ±ÙˆØ²Ø±Ø³Ø§Ù†ÛŒ Ø´Ø¯: {language}")
            return True
        except Exception as e:
            logger.error(f"Error updating user language: {e}")
            return False
    
    async def get_user_level(self, chat_id: int, user_id: int) -> int:
        """Ø¯Ø±ÛŒØ§ÙØª Ø³Ø·Ø­ Ú©Ø§Ø±Ø¨Ø± - Get user level"""
        try:
            result = await self.db(
                "SELECT level FROM players WHERE chat_id = %s AND user_id = %s",
                (chat_id, user_id), fetch="one"
            )
            return result[0] if result else 1
        except Exception as e:
            logger.error(f"Error getting user level: {e}")
            return 1
    
    async def update_user_score(self, chat_id: int, user_id: int, score_change: int) -> Optional[int]:
        """Ø¨Ù‡â€ŒØ±ÙˆØ²Ø±Ø³Ø§Ù†ÛŒ Ø§Ù…ØªÛŒØ§Ø² Ú©Ø§Ø±Ø¨Ø± - Update user score"""
        try:
            result = await self.db("""
                UPDATE players 
                SET score = score + %s,
                    level = GREATEST(1, (score + %s) / 10 + 1),
                    last_active = %s
                WHERE chat_id = %s AND user_id = %s
                RETURNING score, level
            """, (score_change, score_change, int(time.time()), chat_id, user_id), fetch="one_dict")
            
            if result:
                logger.info(f"Score updated for user {user_id}: +{score_change} (total: {result['score']}, level: {result['level']})")
                return result['score']
            return None
        except Exception as e:
            logger.error(f"Error updating user score: {e}")
            return None
    
    async def update_user_hp(self, chat_id: int, user_id: int, hp_change: int) -> Optional[int]:
        """Ø¨Ù‡â€ŒØ±ÙˆØ²Ø±Ø³Ø§Ù†ÛŒ Ø¬Ø§Ù† Ú©Ø§Ø±Ø¨Ø± - Update user HP"""
        try:
            result = await self.db("""
                UPDATE players 
                SET hp = GREATEST(0, LEAST(100, hp + %s)),
                    last_active = %s
                WHERE chat_id = %s AND user_id = %s
                RETURNING hp
            """, (hp_change, int(time.time()), chat_id, user_id), fetch="one")
            
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error updating user HP: {e}")
            return None
    
    async def update_user_tg_stars(self, chat_id: int, user_id: int, stars_change: int) -> Optional[int]:
        """Ø¨Ù‡â€ŒØ±ÙˆØ²Ø±Ø³Ø§Ù†ÛŒ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù… - Update user TG Stars"""
        try:
            result = await self.db("""
                UPDATE players 
                SET tg_stars = GREATEST(0, tg_stars + %s),
                    last_active = %s
                WHERE chat_id = %s AND user_id = %s
                RETURNING tg_stars
            """, (stars_change, int(time.time()), chat_id, user_id), fetch="one")
            
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error updating user TG Stars: {e}")
            return None

    # =============================================================================
    # Ù…Ø¯ÛŒØ±ÛŒØª Ù…ÙˆØ¬ÙˆØ¯ÛŒ - Inventory Management
    # =============================================================================
    
    async def get_inventory(self, chat_id: int, user_id: int) -> Dict[str, int]:
        """Ø¯Ø±ÛŒØ§ÙØª Ù…ÙˆØ¬ÙˆØ¯ÛŒ Ú©Ø§Ø±Ø¨Ø± - Get user inventory from the database"""
        try:
            rows = await self.db(
                "SELECT item, qty FROM inventories WHERE chat_id=%s AND user_id=%s AND qty > 0", 
                (chat_id, user_id), 
                fetch="all_dicts"
            )
            return {row['item']: row['qty'] for row in rows} if rows else {}
        except Exception as e:
            logger.error(f"Error getting inventory for user {user_id}: {e}")
            return {}
    
    async def get_item_quantity(self, chat_id: int, user_id: int, item: str) -> int:
        """Ø¯Ø±ÛŒØ§ÙØª ØªØ¹Ø¯Ø§Ø¯ Ø¢ÛŒØªÙ… Ø®Ø§Øµ - Get quantity of specific item"""
        try:
            result = await self.db(
                "SELECT qty FROM inventories WHERE chat_id = %s AND user_id = %s AND item = %s",
                (chat_id, user_id, item), fetch="one"
            )
            return result[0] if result else 0
        except Exception as e:
            logger.error(f"Error getting item quantity: {e}")
            return 0
    
    async def add_item(self, chat_id: int, user_id: int, item: str, quantity: int = 1) -> bool:
        """Ø§ÙØ²ÙˆØ¯Ù† Ø¢ÛŒØªÙ… Ø¨Ù‡ Ù…ÙˆØ¬ÙˆØ¯ÛŒ - Add item to inventory"""
        try:
            await self.db("""
                INSERT INTO inventories (chat_id, user_id, item, qty)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (chat_id, user_id, item) 
                DO UPDATE SET qty = inventories.qty + EXCLUDED.qty
            """, (chat_id, user_id, item, quantity))
            
            logger.info(f"Added {quantity}x {item} to user {user_id} inventory")
            logger.info(f"{quantity} Ø¹Ø¯Ø¯ {item} Ø¨Ù‡ Ù…ÙˆØ¬ÙˆØ¯ÛŒ Ú©Ø§Ø±Ø¨Ø± {user_id} Ø§Ø¶Ø§ÙÙ‡ Ø´Ø¯")
            return True
        except Exception as e:
            logger.error(f"Error adding item to inventory: {e}")
            return False
    
    async def remove_item(self, chat_id: int, user_id: int, item: str, quantity: int = 1) -> bool:
        """Ø­Ø°Ù Ø¢ÛŒØªÙ… Ø§Ø² Ù…ÙˆØ¬ÙˆØ¯ÛŒ - Remove item from inventory"""
        try:
            # Check if user has enough items
            current_qty = await self.get_item_quantity(chat_id, user_id, item)
            if current_qty < quantity:
                logger.warning(f"User {user_id} doesn't have enough {item} (has: {current_qty}, needs: {quantity})")
                return False
            
            await self.db("""
                UPDATE inventories 
                SET qty = GREATEST(0, qty - %s)
                WHERE chat_id = %s AND user_id = %s AND item = %s
            """, (quantity, chat_id, user_id, item))
            
            # Delete row if quantity becomes 0
            await self.db(
                "DELETE FROM inventories WHERE chat_id = %s AND user_id = %s AND item = %s AND qty = 0",
                (chat_id, user_id, item)
            )
            
            logger.info(f"Removed {quantity}x {item} from user {user_id} inventory")
            logger.info(f"{quantity} Ø¹Ø¯Ø¯ {item} Ø§Ø² Ù…ÙˆØ¬ÙˆØ¯ÛŒ Ú©Ø§Ø±Ø¨Ø± {user_id} Ø­Ø°Ù Ø´Ø¯")
            return True
        except Exception as e:
            logger.error(f"Error removing item from inventory: {e}")
            return False
    
    async def get_inventory_value(self, chat_id: int, user_id: int) -> Dict[str, int]:
        """Ù…Ø­Ø§Ø³Ø¨Ù‡ Ø§Ø±Ø²Ø´ Ú©Ù„ Ù…ÙˆØ¬ÙˆØ¯ÛŒ - Calculate total inventory value"""
        try:
            from src.config.items import ITEMS
            
            inventory = await self.get_inventory(chat_id, user_id)
            total_medals = 0
            total_stars = 0
            
            for item, qty in inventory.items():
                item_data = ITEMS.get(item, {})
                price = item_data.get('price', 0)
                payment_type = item_data.get('payment', 'medals')
                
                if payment_type == 'tg_stars':
                    total_stars += price * qty
                else:
                    total_medals += price * qty
            
            return {
                'medals': total_medals,
                'tg_stars': total_stars,
                'total_items': len(inventory)
            }
        except Exception as e:
            logger.error(f"Error calculating inventory value: {e}")
            return {'medals': 0, 'tg_stars': 0, 'total_items': 0}

    # =============================================================================
    # Ù…Ø¯ÛŒØ±ÛŒØª Ø­Ù…Ù„Ø§Øª - Attack Management
    # =============================================================================
    
    async def record_attack(self, chat_id: int, attacker_id: int, victim_id: int, 
                           damage: int, weapon: str) -> bool:
        """Ø«Ø¨Øª Ø­Ù…Ù„Ù‡ - Record an attack"""
        try:
            current_time = int(time.time())
            await self.db("""
                INSERT INTO attacks (chat_id, attacker_id, victim_id, damage, attack_time, weapon)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (chat_id, attacker_id, victim_id, damage, current_time, weapon))
            
            logger.info(f"Attack recorded: {attacker_id} -> {victim_id} ({damage} damage with {weapon})")
            logger.info(f"Ø­Ù…Ù„Ù‡ Ø«Ø¨Øª Ø´Ø¯: {attacker_id} -> {victim_id} ({damage} Ø¢Ø³ÛŒØ¨ Ø¨Ø§ {weapon})")
            return True
        except Exception as e:
            logger.error(f"Error recording attack: {e}")
            return False
    
    async def get_attack_history(self, chat_id: int, user_id: Optional[int] = None, 
                                limit: int = 50) -> List[Dict[str, Any]]:
        """Ø¯Ø±ÛŒØ§ÙØª ØªØ§Ø±ÛŒØ®Ú†Ù‡ Ø­Ù…Ù„Ø§Øª - Get attack history"""
        try:
            if user_id:
                # Get attacks involving specific user
                attacks = await self.db("""
                    SELECT a.*, 
                           p1.first_name as attacker_name,
                           p2.first_name as victim_name
                    FROM attacks a
                    JOIN players p1 ON a.chat_id = p1.chat_id AND a.attacker_id = p1.user_id
                    JOIN players p2 ON a.chat_id = p2.chat_id AND a.victim_id = p2.user_id
                    WHERE a.chat_id = %s AND (a.attacker_id = %s OR a.victim_id = %s)
                    ORDER BY a.attack_time DESC
                    LIMIT %s
                """, (chat_id, user_id, user_id, limit), fetch="all_dicts")
            else:
                # Get all attacks in chat
                attacks = await self.db("""
                    SELECT a.*, 
                           p1.first_name as attacker_name,
                           p2.first_name as victim_name
                    FROM attacks a
                    JOIN players p1 ON a.chat_id = p1.chat_id AND a.attacker_id = p1.user_id
                    JOIN players p2 ON a.chat_id = p2.chat_id AND a.victim_id = p2.user_id
                    WHERE a.chat_id = %s
                    ORDER BY a.attack_time DESC
                    LIMIT %s
                """, (chat_id, limit), fetch="all_dicts")
            
            return attacks or []
        except Exception as e:
            logger.error(f"Error getting attack history: {e}")
            return []
    
    async def get_user_combat_stats(self, chat_id: int, user_id: int) -> Dict[str, Any]:
        """Ø¯Ø±ÛŒØ§ÙØª Ø¢Ù…Ø§Ø± Ø¬Ù†Ú¯ÛŒ Ú©Ø§Ø±Ø¨Ø± - Get user combat statistics"""
        try:
            # Attack stats
            attack_stats = await self.db("""
                SELECT 
                    COUNT(*) as total_attacks,
                    COALESCE(SUM(damage), 0) as total_damage,
                    COALESCE(AVG(damage), 0) as avg_damage,
                    COALESCE(MAX(damage), 0) as max_damage
                FROM attacks 
                WHERE chat_id = %s AND attacker_id = %s
            """, (chat_id, user_id), fetch="one_dict")
            
            # Defense stats
            defense_stats = await self.db("""
                SELECT 
                    COUNT(*) as times_attacked,
                    COALESCE(SUM(damage), 0) as damage_taken,
                    COALESCE(AVG(damage), 0) as avg_damage_taken,
                    COALESCE(MAX(damage), 0) as max_damage_taken
                FROM attacks 
                WHERE chat_id = %s AND victim_id = %s
            """, (chat_id, user_id), fetch="one_dict")
            
            # Most used weapon
            weapon_stats = await self.db("""
                SELECT weapon, COUNT(*) as usage_count
                FROM attacks 
                WHERE chat_id = %s AND attacker_id = %s
                GROUP BY weapon
                ORDER BY usage_count DESC
                LIMIT 1
            """, (chat_id, user_id), fetch="one_dict")
            
            # Most attacked victim
            victim_stats = await self.db("""
                SELECT p.first_name, COUNT(*) as attack_count
                FROM attacks a
                JOIN players p ON a.chat_id = p.chat_id AND a.victim_id = p.user_id
                WHERE a.chat_id = %s AND a.attacker_id = %s
                GROUP BY a.victim_id, p.first_name
                ORDER BY attack_count DESC
                LIMIT 1
            """, (chat_id, user_id), fetch="one_dict")
            
            return {
                'attacks': attack_stats or {},
                'defense': defense_stats or {},
                'favorite_weapon': weapon_stats.get('weapon') if weapon_stats else None,
                'most_attacked_victim': victim_stats.get('first_name') if victim_stats else None
            }
        except Exception as e:
            logger.error(f"Error getting combat stats: {e}")
            return {}

    # =============================================================================
    # Ù…Ø¯ÛŒØ±ÛŒØª Ø®Ø±ÛŒØ¯Ù‡Ø§ - Purchase Management  
    # =============================================================================
    
    async def record_purchase(self, chat_id: int, user_id: int, item: str, price: int, 
                             payment_type: str = "medals") -> bool:
        """Ø«Ø¨Øª Ø®Ø±ÛŒØ¯ - Record a purchase"""
        try:
            current_time = int(time.time())
            
            if payment_type == "tg_stars":
                # Record TG Stars purchase
                await self.db("""
                    INSERT INTO tg_stars_purchases (chat_id, user_id, item_id, stars_amount, purchase_time, status)
                    VALUES (%s, %s, %s, %s, %s, 'completed')
                """, (chat_id, user_id, item, price, current_time))
            else:
                # Record regular purchase
                await self.db("""
                    INSERT INTO purchases (chat_id, user_id, item, price, purchase_time)
                    VALUES (%s, %s, %s, %s, %s)
                """, (chat_id, user_id, item, price, current_time))
            
            logger.info(f"Purchase recorded: user {user_id} bought {item} for {price} {payment_type}")
            logger.info(f"Ø®Ø±ÛŒØ¯ Ø«Ø¨Øª Ø´Ø¯: Ú©Ø§Ø±Ø¨Ø± {user_id} Ø¢ÛŒØªÙ… {item} Ø±Ø§ Ø¨Ù‡ Ù‚ÛŒÙ…Øª {price} {payment_type} Ø®Ø±ÛŒØ¯")
            return True
        except Exception as e:
            logger.error(f"Error recording purchase: {e}")
            return False
    
    async def get_purchase_history(self, chat_id: int, user_id: Optional[int] = None, 
                                  limit: int = 50) -> List[Dict[str, Any]]:
        """Ø¯Ø±ÛŒØ§ÙØª ØªØ§Ø±ÛŒØ®Ú†Ù‡ Ø®Ø±ÛŒØ¯Ù‡Ø§ - Get purchase history"""
        try:
            if user_id:
                # Get purchases for specific user
                purchases = await self.db("""
                    SELECT p.*, pl.first_name
                    FROM purchases p
                    JOIN players pl ON p.chat_id = pl.chat_id AND p.user_id = pl.user_id
                    WHERE p.chat_id = %s AND p.user_id = %s
                    ORDER BY p.purchase_time DESC
                    LIMIT %s
                """, (chat_id, user_id, limit), fetch="all_dicts")
            else:
                # Get all purchases in chat
                purchases = await self.db("""
                    SELECT p.*, pl.first_name
                    FROM purchases p
                    JOIN players pl ON p.chat_id = pl.chat_id AND p.user_id = pl.user_id
                    WHERE p.chat_id = %s
                    ORDER BY p.purchase_time DESC
                    LIMIT %s
                """, (chat_id, limit), fetch="all_dicts")
            
            return purchases or []
        except Exception as e:
            logger.error(f"Error getting purchase history: {e}")
            return []
    
    async def get_spending_stats(self, chat_id: int, user_id: int) -> Dict[str, Any]:
        """Ø¯Ø±ÛŒØ§ÙØª Ø¢Ù…Ø§Ø± Ø®Ø±Ø¬ Ú©Ø±Ø¯ - Get spending statistics"""
        try:
            # Medal spending
            medal_stats = await self.db("""
                SELECT 
                    COUNT(*) as total_purchases,
                    COALESCE(SUM(price), 0) as total_spent,
                    COALESCE(AVG(price), 0) as avg_spent
                FROM purchases 
                WHERE chat_id = %s AND user_id = %s
            """, (chat_id, user_id), fetch="one_dict")
            
            # TG Stars spending
            stars_stats = await self.db("""
                SELECT 
                    COUNT(*) as total_purchases,
                    COALESCE(SUM(stars_amount), 0) as total_spent,
                    COALESCE(AVG(stars_amount), 0) as avg_spent
                FROM tg_stars_purchases 
                WHERE chat_id = %s AND user_id = %s AND status = 'completed'
            """, (chat_id, user_id), fetch="one_dict")
            
            # Most purchased item
            popular_item = await self.db("""
                SELECT item, COUNT(*) as purchase_count
                FROM purchases 
                WHERE chat_id = %s AND user_id = %s
                GROUP BY item
                ORDER BY purchase_count DESC
                LIMIT 1
            """, (chat_id, user_id), fetch="one_dict")
            
            return {
                'medals': medal_stats or {},
                'tg_stars': stars_stats or {},
                'most_purchased_item': popular_item.get('item') if popular_item else None
            }
        except Exception as e:
            logger.error(f"Error getting spending stats: {e}")
            return {}

    # =============================================================================
    # Ù…Ø¯ÛŒØ±ÛŒØª Ú©ÙˆÙ„Ø¯Ø§Ù† - Cooldown Management
    # =============================================================================
    
    async def set_cooldown(self, chat_id: int, user_id: int, action: str, 
                          duration: int, data: Optional[str] = None) -> bool:
        """ØªÙ†Ø¸ÛŒÙ… Ú©ÙˆÙ„Ø¯Ø§Ù† - Set cooldown for an action"""
        try:
            until_time = int(time.time()) + duration
            await self.db("""
                INSERT INTO cooldowns (chat_id, user_id, action, until, data)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (chat_id, user_id, action) 
                DO UPDATE SET until = EXCLUDED.until, data = EXCLUDED.data
            """, (chat_id, user_id, action, until_time, data))
            
            logger.info(f"Cooldown set for user {user_id}: {action} for {duration} seconds")
            logger.info(f"Ú©ÙˆÙ„Ø¯Ø§Ù† Ø¨Ø±Ø§ÛŒ Ú©Ø§Ø±Ø¨Ø± {user_id} ØªÙ†Ø¸ÛŒÙ… Ø´Ø¯: {action} Ø¨Ø±Ø§ÛŒ {duration} Ø«Ø§Ù†ÛŒÙ‡")
            return True
        except Exception as e:
            logger.error(f"Error setting cooldown: {e}")
            return False
    
    async def get_cooldown(self, chat_id: int, user_id: int, action: str) -> Optional[int]:
        """Ø¯Ø±ÛŒØ§ÙØª Ø²Ù…Ø§Ù† Ø¨Ø§Ù‚ÛŒÙ…Ø§Ù†Ø¯Ù‡ Ú©ÙˆÙ„Ø¯Ø§Ù† - Get remaining cooldown time"""
        try:
            result = await self.db(
                "SELECT until FROM cooldowns WHERE chat_id = %s AND user_id = %s AND action = %s",
                (chat_id, user_id, action), fetch="one"
            )
            
            if result:
                remaining = result[0] - int(time.time())
                return max(0, remaining)
            return 0
        except Exception as e:
            logger.error(f"Error getting cooldown: {e}")
            return 0
    
    async def clear_cooldown(self, chat_id: int, user_id: int, action: str) -> bool:
        """Ù¾Ø§Ú© Ú©Ø±Ø¯Ù† Ú©ÙˆÙ„Ø¯Ø§Ù† - Clear cooldown"""
        try:
            await self.db(
                "DELETE FROM cooldowns WHERE chat_id = %s AND user_id = %s AND action = %s",
                (chat_id, user_id, action)
            )
            return True
        except Exception as e:
            logger.error(f"Error clearing cooldown: {e}")
            return False
    
    async def cleanup_expired_cooldowns(self) -> int:
        """Ù¾Ø§Ú©â€ŒØ³Ø§Ø²ÛŒ Ú©ÙˆÙ„Ø¯Ø§Ù†â€ŒÙ‡Ø§ÛŒ Ù…Ù†Ù‚Ø¶ÛŒ - Clean up expired cooldowns"""
        try:
            current_time = int(time.time())
            result = await self.db(
                "DELETE FROM cooldowns WHERE until < %s",
                (current_time,)
            )
            logger.info(f"Cleaned up expired cooldowns")
            logger.info(f"Ú©ÙˆÙ„Ø¯Ø§Ù†â€ŒÙ‡Ø§ÛŒ Ù…Ù†Ù‚Ø¶ÛŒ Ù¾Ø§Ú©â€ŒØ³Ø§Ø²ÛŒ Ø´Ø¯Ù†Ø¯")
            return True
        except Exception as e:
            logger.error(f"Error cleaning up cooldowns: {e}")
            return False

    # =============================================================================
    # Ù…Ø¯ÛŒØ±ÛŒØª Ø¯ÙØ§Ø¹ ÙØ¹Ø§Ù„ - Active Defense Management
    # =============================================================================
    
    async def set_active_defense(self, chat_id: int, user_id: int, defense_type: str, 
                                duration: int) -> bool:
        """ÙØ¹Ø§Ù„â€ŒØ³Ø§Ø²ÛŒ Ø¯ÙØ§Ø¹ - Activate defense"""
        try:
            expires_at = int(time.time()) + duration
            await self.db("""
                INSERT INTO active_defenses (chat_id, user_id, defense_type, expires_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (chat_id, user_id) 
                DO UPDATE SET defense_type = EXCLUDED.defense_type, expires_at = EXCLUDED.expires_at
            """, (chat_id, user_id, defense_type, expires_at))
            
            logger.info(f"Active defense set for user {user_id}: {defense_type} for {duration} seconds")
            logger.info(f"Ø¯ÙØ§Ø¹ ÙØ¹Ø§Ù„ Ø¨Ø±Ø§ÛŒ Ú©Ø§Ø±Ø¨Ø± {user_id} ØªÙ†Ø¸ÛŒÙ… Ø´Ø¯: {defense_type} Ø¨Ø±Ø§ÛŒ {duration} Ø«Ø§Ù†ÛŒÙ‡")
            return True
        except Exception as e:
            logger.error(f"Error setting active defense: {e}")
            return False
    
    async def get_active_defense(self, chat_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Ø¯Ø±ÛŒØ§ÙØª Ø¯ÙØ§Ø¹ ÙØ¹Ø§Ù„ - Get active defense"""
        try:
            current_time = int(time.time())
            result = await self.db("""
                SELECT defense_type, expires_at FROM active_defenses 
                WHERE chat_id = %s AND user_id = %s AND expires_at > %s
            """, (chat_id, user_id, current_time), fetch="one_dict")
            
            return result
        except Exception as e:
            logger.error(f"Error getting active defense: {e}")
            return None
    
    async def clear_active_defense(self, chat_id: int, user_id: int) -> bool:
        """Ù¾Ø§Ú© Ú©Ø±Ø¯Ù† Ø¯ÙØ§Ø¹ ÙØ¹Ø§Ù„ - Clear active defense"""
        try:
            await self.db(
                "DELETE FROM active_defenses WHERE chat_id = %s AND user_id = %s",
                (chat_id, user_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error clearing active defense: {e}")
            return False
    
    async def cleanup_expired_defenses(self) -> bool:
        """Ù¾Ø§Ú©â€ŒØ³Ø§Ø²ÛŒ Ø¯ÙØ§Ø¹â€ŒÙ‡Ø§ÛŒ Ù…Ù†Ù‚Ø¶ÛŒ - Clean up expired defenses"""
        try:
            current_time = int(time.time())
            await self.db(
                "DELETE FROM active_defenses WHERE expires_at < %s",
                (current_time,)
            )
            logger.info("Cleaned up expired defenses")
            logger.info("Ø¯ÙØ§Ø¹â€ŒÙ‡Ø§ÛŒ Ù…Ù†Ù‚Ø¶ÛŒ Ù¾Ø§Ú©â€ŒØ³Ø§Ø²ÛŒ Ø´Ø¯Ù†Ø¯")
            return True
        except Exception as e:
            logger.error(f"Error cleaning up defenses: {e}")
    # =============================================================================
    # Ù…Ø¯ÛŒØ±ÛŒØª Ù„ÛŒØ¯Ø±Ø¨ÙˆØ±Ø¯ Ùˆ Ø±ØªØ¨Ù‡â€ŒØ¨Ù†Ø¯ÛŒ - Leaderboard Management
    # =============================================================================
    
    async def get_leaderboard(self, chat_id: int, limit: int = 10, 
                             order_by: str = "score") -> List[Dict[str, Any]]:
        """Ø¯Ø±ÛŒØ§ÙØª Ù„ÛŒØ¯Ø±Ø¨ÙˆØ±Ø¯ - Get leaderboard"""
        try:
            valid_orders = {
                "score": "score DESC",
                "level": "level DESC", 
                "hp": "hp DESC",
                "tg_stars": "tg_stars DESC",
                "attacks": "total_attacks DESC",
                "damage": "total_damage DESC"
            }
            
            order_clause = valid_orders.get(order_by, "score DESC")
            
            # Complex query to get comprehensive leaderboard data
            leaderboard = await self.db(f"""
                SELECT 
                    p.*,
                    COALESCE(attack_stats.total_attacks, 0) as total_attacks,
                    COALESCE(attack_stats.total_damage, 0) as total_damage,
                    COALESCE(defense_stats.times_attacked, 0) as times_attacked,
                    COALESCE(defense_stats.damage_taken, 0) as damage_taken,
                    COALESCE(purchase_stats.total_spent, 0) as total_spent,
                    COALESCE(inventory_stats.items_count, 0) as items_count,
                    ROW_NUMBER() OVER (ORDER BY {order_clause}) as rank
                FROM players p
                LEFT JOIN (
                    SELECT attacker_id, COUNT(*) as total_attacks, SUM(damage) as total_damage
                    FROM attacks WHERE chat_id = %s GROUP BY attacker_id
                ) attack_stats ON p.user_id = attack_stats.attacker_id
                LEFT JOIN (
                    SELECT victim_id, COUNT(*) as times_attacked, SUM(damage) as damage_taken
                    FROM attacks WHERE chat_id = %s GROUP BY victim_id
                ) defense_stats ON p.user_id = defense_stats.victim_id
                LEFT JOIN (
                    SELECT user_id, SUM(price) as total_spent
                    FROM purchases WHERE chat_id = %s GROUP BY user_id
                ) purchase_stats ON p.user_id = purchase_stats.user_id
                LEFT JOIN (
                    SELECT user_id, COUNT(*) as items_count
                    FROM inventories WHERE chat_id = %s AND qty > 0 GROUP BY user_id
                ) inventory_stats ON p.user_id = inventory_stats.user_id
                WHERE p.chat_id = %s
                ORDER BY {order_clause}
                LIMIT %s
            """, (chat_id, chat_id, chat_id, chat_id, chat_id, limit), fetch="all_dicts")
            
            return leaderboard or []
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
    
    async def get_user_rank(self, chat_id: int, user_id: int, 
                           order_by: str = "score") -> Optional[int]:
        """Ø¯Ø±ÛŒØ§ÙØª Ø±ØªØ¨Ù‡ Ú©Ø§Ø±Ø¨Ø± - Get user rank"""
        try:
            valid_orders = {
                "score": "score DESC",
                "level": "level DESC",
                "hp": "hp DESC", 
                "tg_stars": "tg_stars DESC"
            }
            
            order_clause = valid_orders.get(order_by, "score DESC")
            
            result = await self.db(f"""
                SELECT rank FROM (
                    SELECT user_id, ROW_NUMBER() OVER (ORDER BY {order_clause}) as rank
                    FROM players WHERE chat_id = %s
                ) ranked_players
                WHERE user_id = %s
            """, (chat_id, user_id), fetch="one")
            
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting user rank: {e}")
            return None
    
    async def get_chat_statistics(self, chat_id: int) -> Optional[ChatStats]:
        """Ø¯Ø±ÛŒØ§ÙØª Ø¢Ù…Ø§Ø± Ú©Ø§Ù…Ù„ Ú†Øª - Get comprehensive chat statistics"""
        try:
            # Basic chat info
            chat_info = await self.db(
                "SELECT * FROM groups WHERE chat_id = %s",
                (chat_id,), fetch="one_dict"
            )
            
            # Player statistics
            player_stats = await self.db("""
                SELECT 
                    COUNT(*) as total_players,
                    MAX(level) as highest_level,
                    AVG(score) as avg_score,
                    MAX(score) as highest_score
                FROM players WHERE chat_id = %s
            """, (chat_id,), fetch="one_dict")
            
            # Attack statistics
            attack_stats = await self.db("""
                SELECT 
                    COUNT(*) as total_attacks,
                    SUM(damage) as total_damage,
                    AVG(damage) as avg_damage
                FROM attacks WHERE chat_id = %s
            """, (chat_id,), fetch="one_dict")
            
            # Most active player
            most_active = await self.db("""
                SELECT p.first_name, COUNT(*) as attack_count
                FROM attacks a
                JOIN players p ON a.chat_id = p.chat_id AND a.attacker_id = p.user_id
                WHERE a.chat_id = %s
                GROUP BY a.attacker_id, p.first_name
                ORDER BY attack_count DESC
                LIMIT 1
            """, (chat_id,), fetch="one_dict")
            
            # Purchase statistics
            purchase_stats = await self.db("""
                SELECT COUNT(*) as total_purchases
                FROM purchases WHERE chat_id = %s
            """, (chat_id,), fetch="one_dict")
            
            if not chat_info and not player_stats:
                return None
            
            return ChatStats(
                chat_id=chat_id,
                total_players=player_stats.get('total_players', 0),
                total_attacks=attack_stats.get('total_attacks', 0),
                total_damage=attack_stats.get('total_damage', 0),
                most_active_player=most_active.get('first_name') if most_active else None,
                highest_level=player_stats.get('highest_level', 1),
                total_items_purchased=purchase_stats.get('total_purchases', 0),
                created_at=datetime.fromtimestamp(chat_info.get('created_at', time.time())) if chat_info else datetime.now(),
                last_active=datetime.fromtimestamp(chat_info.get('last_active', time.time())) if chat_info else datetime.now()
            )
        except Exception as e:
            logger.error(f"Error getting chat statistics: {e}")
            return None

    # =============================================================================
    # Ú¯Ø²Ø§Ø±Ø´â€ŒÚ¯ÛŒØ±ÛŒ Ùˆ ØªØ­Ù„ÛŒÙ„ - Analytics and Reporting
    # =============================================================================
    
    async def get_daily_activity(self, chat_id: int, days: int = 7) -> Dict[str, List[int]]:
        """Ø¯Ø±ÛŒØ§ÙØª ÙØ¹Ø§Ù„ÛŒØª Ø±ÙˆØ²Ø§Ù†Ù‡ - Get daily activity statistics"""
        try:
            import asyncio
            
            current_time = int(time.time())
            day_seconds = 24 * 60 * 60
            
            daily_data = {
                'attacks': [],
                'purchases': [],
                'new_users': []
            }
            
            for i in range(days):
                day_start = current_time - (i + 1) * day_seconds
                day_end = current_time - i * day_seconds
                
                # Daily attacks
                attack_count = await self.db("""
                    SELECT COUNT(*) FROM attacks 
                    WHERE chat_id = %s AND attack_time BETWEEN %s AND %s
                """, (chat_id, day_start, day_end), fetch="count")
                
                # Daily purchases
                purchase_count = await self.db("""
                    SELECT COUNT(*) FROM purchases 
                    WHERE chat_id = %s AND purchase_time BETWEEN %s AND %s
                """, (chat_id, day_start, day_end), fetch="count")
                
                # New users (using last_active as proxy for join date)
                new_users = await self.db("""
                    SELECT COUNT(*) FROM players 
                    WHERE chat_id = %s AND last_active BETWEEN %s AND %s
                """, (chat_id, day_start, day_end), fetch="count")
                
                daily_data['attacks'].insert(0, attack_count)
                daily_data['purchases'].insert(0, purchase_count)
                daily_data['new_users'].insert(0, new_users)
            
            return daily_data
        except Exception as e:
            logger.error(f"Error getting daily activity: {e}")
            return {'attacks': [], 'purchases': [], 'new_users': []}
    
    async def get_weapon_usage_stats(self, chat_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Ø¯Ø±ÛŒØ§ÙØª Ø¢Ù…Ø§Ø± Ø§Ø³ØªÙØ§Ø¯Ù‡ Ø§Ø² Ø³Ù„Ø§Ø­â€ŒÙ‡Ø§ - Get weapon usage statistics"""
        try:
            weapon_stats = await self.db("""
                SELECT 
                    weapon,
                    COUNT(*) as usage_count,
                    SUM(damage) as total_damage,
                    AVG(damage) as avg_damage,
                    MAX(damage) as max_damage,
                    COUNT(DISTINCT attacker_id) as unique_users
                FROM attacks 
                WHERE chat_id = %s
                GROUP BY weapon
                ORDER BY usage_count DESC
                LIMIT %s
            """, (chat_id, limit), fetch="all_dicts")
            
            return weapon_stats or []
        except Exception as e:
            logger.error(f"Error getting weapon usage stats: {e}")
            return []
    
    async def get_item_popularity(self, chat_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Ø¯Ø±ÛŒØ§ÙØª Ù…Ø­Ø¨ÙˆØ¨ÛŒØª Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ - Get item popularity statistics"""
        try:
            item_stats = await self.db("""
                SELECT 
                    item,
                    COUNT(*) as purchase_count,
                    SUM(price) as total_revenue,
                    AVG(price) as avg_price,
                    COUNT(DISTINCT user_id) as unique_buyers
                FROM purchases 
                WHERE chat_id = %s
                GROUP BY item
                ORDER BY purchase_count DESC
                LIMIT %s
            """, (chat_id, limit), fetch="all_dicts")
            
            return item_stats or []
        except Exception as e:
            logger.error(f"Error getting item popularity: {e}")
            return []
    
    async def export_user_data(self, chat_id: int, user_id: int) -> Dict[str, Any]:
        """ØµØ§Ø¯Ø±Ø§Øª Ú©Ø§Ù…Ù„ Ø¯Ø§Ø¯Ù‡â€ŒÙ‡Ø§ÛŒ Ú©Ø§Ø±Ø¨Ø± - Export complete user data"""
        try:
            # Get all user-related data
            user_data = await self.get_user(chat_id, user_id)
            inventory = await self.get_inventory(chat_id, user_id)
            attack_history = await self.get_attack_history(chat_id, user_id)
            purchase_history = await self.get_purchase_history(chat_id, user_id)
            combat_stats = await self.get_user_combat_stats(chat_id, user_id)
            
            return {
                'user_profile': user_data,
                'inventory': inventory,
                'attack_history': attack_history,
                'purchase_history': purchase_history,
                'combat_statistics': combat_stats,
                'export_time': datetime.now().isoformat(),
                'export_timestamp': int(time.time())
            }
        except Exception as e:
            logger.error(f"Error exporting user data: {e}")
            return {}

    # =============================================================================
    # Ø¨Ú©Ø§Ù¾ Ùˆ Ø¨Ø§Ø²ÛŒØ§Ø¨ÛŒ - Backup and Recovery  
    # =============================================================================
    
    async def create_chat_backup(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """Ø§ÛŒØ¬Ø§Ø¯ Ø¨Ú©Ø§Ù¾ Ú©Ø§Ù…Ù„ Ú†Øª - Create complete chat backup"""
        try:
            backup_data = {
                'chat_id': chat_id,
                'backup_time': datetime.now().isoformat(),
                'backup_timestamp': int(time.time()),
                'players': [],
                'attacks': [],
                'purchases': [],
                'inventories': [],
                'cooldowns': [],
                'active_defenses': []
            }
            
            # Export all data tables
            tables = [
                ('players', 'SELECT * FROM players WHERE chat_id = %s'),
                ('attacks', 'SELECT * FROM attacks WHERE chat_id = %s'),
                ('purchases', 'SELECT * FROM purchases WHERE chat_id = %s'),
                ('inventories', 'SELECT * FROM inventories WHERE chat_id = %s'),
                ('cooldowns', 'SELECT * FROM cooldowns WHERE chat_id = %s'),
                ('active_defenses', 'SELECT * FROM active_defenses WHERE chat_id = %s')
            ]
            
            for table_name, query in tables:
                data = await self.db(query, (chat_id,), fetch="all_dicts")
                backup_data[table_name] = data or []
            
            logger.info(f"Chat backup created for chat {chat_id}")
            logger.info(f"Ø¨Ú©Ø§Ù¾ Ú†Øª Ø¨Ø±Ø§ÛŒ Ú†Øª {chat_id} Ø§ÛŒØ¬Ø§Ø¯ Ø´Ø¯")
            return backup_data
        except Exception as e:
            logger.error(f"Error creating chat backup: {e}")
            return None
    
    async def maintenance_cleanup(self) -> Dict[str, int]:
        """Ù¾Ø§Ú©â€ŒØ³Ø§Ø²ÛŒ Ø¯ÙˆØ±Ù‡â€ŒØ§ÛŒ Ù¾Ø§ÛŒÚ¯Ø§Ù‡ Ø¯Ø§Ø¯Ù‡ - Periodic database maintenance"""
        try:
            cleanup_stats = {
                'expired_cooldowns': 0,
                'expired_defenses': 0,
                'old_attacks': 0,
                'empty_inventories': 0
            }
            
            current_time = int(time.time())
            thirty_days_ago = current_time - (30 * 24 * 60 * 60)
            
            # Clean expired cooldowns
            await self.cleanup_expired_cooldowns()
            cleanup_stats['expired_cooldowns'] = 1
            
            # Clean expired defenses
            await self.cleanup_expired_defenses()
            cleanup_stats['expired_defenses'] = 1
            
            # Clean old attacks (older than 30 days)
            old_attacks = await self.db(
                "DELETE FROM attacks WHERE attack_time < %s",
                (thirty_days_ago,)
            )
            cleanup_stats['old_attacks'] = 1
            
            # Clean empty inventory entries
            empty_inventories = await self.db(
                "DELETE FROM inventories WHERE qty <= 0"
            )
            cleanup_stats['empty_inventories'] = 1
            
            logger.info(f"Database maintenance completed: {cleanup_stats}")
            logger.info(f"Ù†Ú¯Ù‡Ø¯Ø§Ø±ÛŒ Ù¾Ø§ÛŒÚ¯Ø§Ù‡ Ø¯Ø§Ø¯Ù‡ Ú©Ø§Ù…Ù„ Ø´Ø¯: {cleanup_stats}")
            return cleanup_stats
        except Exception as e:
            logger.error(f"Error during maintenance cleanup: {e}")
            return {}
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Ø¯Ø±ÛŒØ§ÙØª Ø¢Ù…Ø§Ø± Ú©Ù„ÛŒ Ù¾Ø§ÛŒÚ¯Ø§Ù‡ Ø¯Ø§Ø¯Ù‡ - Get overall database statistics"""
        try:
            stats = {}
            
            # Table sizes
            tables = ['players', 'attacks', 'purchases', 'inventories', 'cooldowns', 'active_defenses']
            for table in tables:
                count = await self.db(f"SELECT COUNT(*) FROM {table}", fetch="count")
                stats[f'{table}_count'] = count
            
            # Active chats
            active_chats = await self.db(
                "SELECT COUNT(DISTINCT chat_id) FROM players",
                fetch="count"
            )
            stats['active_chats'] = active_chats
            
            # Recent activity (last 24 hours)
            day_ago = int(time.time()) - (24 * 60 * 60)
            recent_attacks = await self.db(
                "SELECT COUNT(*) FROM attacks WHERE attack_time > %s",
                (day_ago,), fetch="count"
            )
            stats['recent_attacks_24h'] = recent_attacks
            
            recent_purchases = await self.db(
                "SELECT COUNT(*) FROM purchases WHERE purchase_time > %s",
                (day_ago,), fetch="count"
            )
            stats['recent_purchases_24h'] = recent_purchases
            
            return stats
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}

    async def log_message_interaction(self, chat_id: int, user_id: int, message_type: str, data: Dict[str, Any] = None) -> bool:
        """Ø«Ø¨Øª ØªØ¹Ø§Ù…Ù„ Ù¾ÛŒØ§Ù… Ú©Ø§Ø±Ø¨Ø± - Log user message interaction"""
        try:
            current_time = int(time.time())
            await self.db("""
                INSERT INTO interactions (chat_id, user_id, interaction_type, interaction_data, timestamp)
                VALUES (%s, %s, %s, %s, %s)
            """, (chat_id, user_id, message_type, json.dumps(data) if data else None, current_time))
            
            logger.info(f"Logged message interaction: {message_type} for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error logging message interaction: {e}")
            return False


async def setup_database() -> None:
    """
    Ø±Ø§Ù‡â€ŒØ§Ù†Ø¯Ø§Ø²ÛŒ Ø¬Ø¯Ø§ÙˆÙ„ Ù¾Ø§ÛŒÚ¯Ø§Ù‡ Ø¯Ø§Ø¯Ù‡ Ø§Ú¯Ø± ÙˆØ¬ÙˆØ¯ Ù†Ø¯Ø§Ø´ØªÙ‡ Ø¨Ø§Ø´Ù†Ø¯
    Set up the database tables if they don't exist with enhanced schema
    """
    logger.info("Setting up database - Ø±Ø§Ù‡â€ŒØ§Ù†Ø¯Ø§Ø²ÛŒ Ù¾Ø§ÛŒÚ¯Ø§Ù‡ Ø¯Ø§Ø¯Ù‡")
    
    await initialize_pool()
    db_manager = DBManager()
    
    try:
        # Create groups table with enhanced fields
        await db_manager.db("""
            CREATE TABLE IF NOT EXISTS groups(
                chat_id BIGINT PRIMARY KEY,
                title TEXT,
                username TEXT,
                chat_type TEXT DEFAULT 'group',
                member_count INT DEFAULT 0,
                created_at BIGINT DEFAULT EXTRACT(EPOCH FROM NOW()),
                last_active BIGINT DEFAULT EXTRACT(EPOCH FROM NOW()),
                settings JSONB DEFAULT '{}',
                language TEXT DEFAULT 'en'
            )
        """)
        logger.info("Groups table created/verified - Ø¬Ø¯ÙˆÙ„ Ú¯Ø±ÙˆÙ‡â€ŒÙ‡Ø§ Ø§ÛŒØ¬Ø§Ø¯/ØªØ§ÛŒÛŒØ¯ Ø´Ø¯")
        
        # Create enhanced players table
        await db_manager.db("""
            CREATE TABLE IF NOT EXISTS players(
                chat_id BIGINT,
                user_id BIGINT,
                first_name TEXT NOT NULL,
                username TEXT,
                score INT DEFAULT 0,
                language TEXT DEFAULT 'en',
                last_active BIGINT DEFAULT EXTRACT(EPOCH FROM NOW()),
                tg_stars INT DEFAULT 0,
                hp INT DEFAULT 100,
                level INT DEFAULT 1,
                created_at BIGINT DEFAULT EXTRACT(EPOCH FROM NOW()),
                total_attacks INT DEFAULT 0,
                total_damage INT DEFAULT 0,
                times_attacked INT DEFAULT 0,
                damage_taken INT DEFAULT 0,
                preferred_weapon TEXT,
                settings JSONB DEFAULT '{}',
                -- Additional columns for helpers.py compatibility
                experience INT DEFAULT 0,
                join_date BIGINT DEFAULT EXTRACT(EPOCH FROM NOW()),
                attacks_made INT DEFAULT 0,
                attacks_received INT DEFAULT 0,
                victories INT DEFAULT 0,
                defeats INT DEFAULT 0,
                shields_used INT DEFAULT 0,
                items_bought INT DEFAULT 0,
                activity_points INT DEFAULT 0,
                PRIMARY KEY(chat_id, user_id),
                CONSTRAINT positive_hp CHECK (hp >= 0 AND hp <= 100),
                CONSTRAINT positive_level CHECK (level >= 1),
                CONSTRAINT positive_tg_stars CHECK (tg_stars >= 0),
                CONSTRAINT positive_experience CHECK (experience >= 0),
                CONSTRAINT positive_activities CHECK (attacks_made >= 0 AND attacks_received >= 0 AND victories >= 0 AND defeats >= 0)
            )
        """)
        logger.info("Players table created/verified - Ø¬Ø¯ÙˆÙ„ Ø¨Ø§Ø²ÛŒÚ©Ù†Ø§Ù† Ø§ÛŒØ¬Ø§Ø¯/ØªØ§ÛŒÛŒØ¯ Ø´Ø¯")
        
        # Create enhanced cooldowns table
        await db_manager.db("""
            CREATE TABLE IF NOT EXISTS cooldowns(
                chat_id BIGINT,
                user_id BIGINT,
                action TEXT,
                until BIGINT,
                data TEXT,
                created_at BIGINT DEFAULT EXTRACT(EPOCH FROM NOW()),
                PRIMARY KEY(chat_id, user_id, action),
                CONSTRAINT future_until CHECK (until > created_at)
            )
        """)
        logger.info("Cooldowns table created/verified - Ø¬Ø¯ÙˆÙ„ Ú©ÙˆÙ„Ø¯Ø§Ù†â€ŒÙ‡Ø§ Ø§ÛŒØ¬Ø§Ø¯/ØªØ§ÛŒÛŒØ¯ Ø´Ø¯")
        
        # Create enhanced purchases table
        await db_manager.db("""
            CREATE TABLE IF NOT EXISTS purchases(
                id SERIAL PRIMARY KEY,
                chat_id BIGINT,
                user_id BIGINT,
                item TEXT NOT NULL,
                price INT NOT NULL,
                payment_type TEXT DEFAULT 'medals',
                purchase_time BIGINT DEFAULT EXTRACT(EPOCH FROM NOW()),
                quantity INT DEFAULT 1,
                CONSTRAINT positive_price CHECK (price >= 0),
                CONSTRAINT positive_quantity CHECK (quantity > 0)
            )
        """)
        logger.info("Purchases table created/verified - Ø¬Ø¯ÙˆÙ„ Ø®Ø±ÛŒØ¯Ù‡Ø§ Ø§ÛŒØ¬Ø§Ø¯/ØªØ§ÛŒÛŒØ¯ Ø´Ø¯")
        
        # Create enhanced attacks table
        await db_manager.db("""
            CREATE TABLE IF NOT EXISTS attacks(
                id SERIAL PRIMARY KEY,
                chat_id BIGINT,
                attacker_id BIGINT,
                victim_id BIGINT,
                damage INT NOT NULL,
                attack_time BIGINT DEFAULT EXTRACT(EPOCH FROM NOW()),
                weapon TEXT NOT NULL,
                is_critical BOOLEAN DEFAULT FALSE,
                defense_reduced BOOLEAN DEFAULT FALSE,
                CONSTRAINT positive_damage CHECK (damage > 0),
                CONSTRAINT different_users CHECK (attacker_id != victim_id)
            )
        """)
        logger.info("Attacks table created/verified - Ø¬Ø¯ÙˆÙ„ Ø­Ù…Ù„Ø§Øª Ø§ÛŒØ¬Ø§Ø¯/ØªØ§ÛŒÛŒØ¯ Ø´Ø¯")
        
        # Create enhanced inventories table
        await db_manager.db("""
            CREATE TABLE IF NOT EXISTS inventories(
                chat_id BIGINT,
                user_id BIGINT,
                item TEXT,
                qty INT DEFAULT 0,
                acquired_at BIGINT DEFAULT EXTRACT(EPOCH FROM NOW()),
                last_used BIGINT,
                PRIMARY KEY(chat_id, user_id, item),
                CONSTRAINT non_negative_qty CHECK (qty >= 0)
            )
        """)
        logger.info("Inventories table created/verified - Ø¬Ø¯ÙˆÙ„ Ù…ÙˆØ¬ÙˆØ¯ÛŒâ€ŒÙ‡Ø§ Ø§ÛŒØ¬Ø§Ø¯/ØªØ§ÛŒÛŒØ¯ Ø´Ø¯")
        
        # Create enhanced TG Stars purchases table
        await db_manager.db("""
            CREATE TABLE IF NOT EXISTS tg_stars_purchases(
                id SERIAL PRIMARY KEY,
                chat_id BIGINT,
                user_id BIGINT,
                payment_id TEXT UNIQUE,
                item_id TEXT NOT NULL,
                stars_amount INT NOT NULL,
                purchase_time BIGINT DEFAULT EXTRACT(EPOCH FROM NOW()),
                status TEXT DEFAULT 'pending',
                processed_at BIGINT,
                CONSTRAINT positive_stars CHECK (stars_amount > 0),
                CONSTRAINT valid_status CHECK (status IN ('pending', 'completed', 'failed', 'refunded'))
            )
        """)
        logger.info("TG Stars purchases table created/verified - Ø¬Ø¯ÙˆÙ„ Ø®Ø±ÛŒØ¯Ù‡Ø§ÛŒ Ø³ØªØ§Ø±Ù‡ ØªÙ„Ú¯Ø±Ø§Ù… Ø§ÛŒØ¬Ø§Ø¯/ØªØ§ÛŒÛŒØ¯ Ø´Ø¯")

        # Create enhanced active_defenses table
        await db_manager.db("""
            CREATE TABLE IF NOT EXISTS active_defenses(
                chat_id BIGINT,
                user_id BIGINT,
                defense_type TEXT NOT NULL,
                expires_at BIGINT NOT NULL,
                activated_at BIGINT DEFAULT EXTRACT(EPOCH FROM NOW()),
                effectiveness DECIMAL(3,2) DEFAULT 1.00,
                PRIMARY KEY(chat_id, user_id),
                CONSTRAINT future_expiry CHECK (expires_at > activated_at),
                CONSTRAINT valid_effectiveness CHECK (effectiveness > 0 AND effectiveness <= 1)
            )
        """)
        logger.info("Active defenses table created/verified - Ø¬Ø¯ÙˆÙ„ Ø¯ÙØ§Ø¹â€ŒÙ‡Ø§ÛŒ ÙØ¹Ø§Ù„ Ø§ÛŒØ¬Ø§Ø¯/ØªØ§ÛŒÛŒØ¯ Ø´Ø¯")
        
        # Create interactions table for logging user interactions
        await db_manager.db("""
            CREATE TABLE IF NOT EXISTS interactions(
                id SERIAL PRIMARY KEY,
                chat_id BIGINT NOT NULL,
                user_id BIGINT NOT NULL,
                interaction_type TEXT NOT NULL,
                interaction_data JSONB,
                timestamp BIGINT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("Interactions table created/verified - Ø¬Ø¯ÙˆÙ„ ØªØ¹Ø§Ù…Ù„Ø§Øª Ø§ÛŒØ¬Ø§Ø¯/ØªØ§ÛŒÛŒØ¯ Ø´Ø¯")
        
        # Create player achievements table for tracking player accomplishments
        await db_manager.db("""
            CREATE TABLE IF NOT EXISTS player_achievements(
                id SERIAL PRIMARY KEY,
                chat_id BIGINT NOT NULL,
                user_id BIGINT NOT NULL,
                achievement_id TEXT NOT NULL,
                earned_at BIGINT DEFAULT EXTRACT(EPOCH FROM NOW()),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(chat_id, user_id, achievement_id)
            )
        """)
        logger.info("Player achievements table created/verified - Ø¬Ø¯ÙˆÙ„ Ø¯Ø³ØªØ§ÙˆØ±Ø¯Ù‡Ø§ÛŒ Ø¨Ø§Ø²ÛŒÚ©Ù† Ø§ÛŒØ¬Ø§Ø¯/ØªØ§ÛŒÛŒØ¯ Ø´Ø¯")
        
        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_players_score ON players(chat_id, score DESC)",
            "CREATE INDEX IF NOT EXISTS idx_players_level ON players(chat_id, level DESC)",
            "CREATE INDEX IF NOT EXISTS idx_attacks_time ON attacks(chat_id, attack_time DESC)",
            "CREATE INDEX IF NOT EXISTS idx_attacks_attacker ON attacks(chat_id, attacker_id)",
            "CREATE INDEX IF NOT EXISTS idx_attacks_victim ON attacks(chat_id, victim_id)",
            "CREATE INDEX IF NOT EXISTS idx_purchases_time ON purchases(chat_id, purchase_time DESC)",
            "CREATE INDEX IF NOT EXISTS idx_inventories_user ON inventories(chat_id, user_id)",
            "CREATE INDEX IF NOT EXISTS idx_cooldowns_until ON cooldowns(chat_id, user_id, until)",
            "CREATE INDEX IF NOT EXISTS idx_defenses_expires ON active_defenses(chat_id, expires_at)",
            "CREATE INDEX IF NOT EXISTS idx_achievements_user ON player_achievements(chat_id, user_id)",
            "CREATE INDEX IF NOT EXISTS idx_interactions_user ON interactions(chat_id, user_id, timestamp DESC)"
        ]
        
        for index_query in indexes:
            await db_manager.db(index_query)
        
        logger.info("Database indexes created/verified - Ø§ÛŒÙ†Ø¯Ú©Ø³â€ŒÙ‡Ø§ÛŒ Ù¾Ø§ÛŒÚ¯Ø§Ù‡ Ø¯Ø§Ø¯Ù‡ Ø§ÛŒØ¬Ø§Ø¯/ØªØ§ÛŒÛŒØ¯ Ø´Ø¯Ù†Ø¯")
        
        # Add triggers for automatic updates (PostgreSQL specific)
        await db_manager.db("""
            CREATE OR REPLACE FUNCTION update_player_stats()
            RETURNS TRIGGER AS $$
            BEGIN
                IF TG_OP = 'INSERT' THEN
                    UPDATE players 
                    SET total_attacks = total_attacks + 1,
                        total_damage = total_damage + NEW.damage
                    WHERE chat_id = NEW.chat_id AND user_id = NEW.attacker_id;
                    
                    UPDATE players 
                    SET times_attacked = times_attacked + 1,
                        damage_taken = damage_taken + NEW.damage
                    WHERE chat_id = NEW.chat_id AND user_id = NEW.victim_id;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)
        
        await db_manager.db("""
            DROP TRIGGER IF EXISTS trigger_update_player_stats ON attacks;
            CREATE TRIGGER trigger_update_player_stats
                AFTER INSERT ON attacks
                FOR EACH ROW
                EXECUTE FUNCTION update_player_stats();
        """)
        
        logger.info("Database triggers created/verified - ØªØ±ÛŒÚ¯Ø±Ù‡Ø§ÛŒ Ù¾Ø§ÛŒÚ¯Ø§Ù‡ Ø¯Ø§Ø¯Ù‡ Ø§ÛŒØ¬Ø§Ø¯/ØªØ§ÛŒÛŒØ¯ Ø´Ø¯Ù†Ø¯")
        logger.info("Database setup complete - Ø±Ø§Ù‡â€ŒØ§Ù†Ø¯Ø§Ø²ÛŒ Ù¾Ø§ÛŒÚ¯Ø§Ù‡ Ø¯Ø§Ø¯Ù‡ Ú©Ø§Ù…Ù„ Ø´Ø¯")
        
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        logger.error(f"Ø®Ø·Ø§ Ø¯Ø± Ø±Ø§Ù‡â€ŒØ§Ù†Ø¯Ø§Ø²ÛŒ Ù¾Ø§ÛŒÚ¯Ø§Ù‡ Ø¯Ø§Ø¯Ù‡: {e}")
        raise DatabaseError(f"Database setup failed: {e}")

# =============================================================================
# ØªÙˆØ§Ø¨Ø¹ Ø³Ø§Ø²Ú¯Ø§Ø±ÛŒ Ùˆ Ú©Ù…Ú©ÛŒ - Legacy Support and Helper Functions
# =============================================================================

async def db(query: str, params: Optional[Tuple] = None, fetch: Optional[str] = None) -> Any:
    """
    ØªØ§Ø¨Ø¹ Ù‚Ø¯ÛŒÙ…ÛŒ Ù¾Ø§ÛŒÚ¯Ø§Ù‡ Ø¯Ø§Ø¯Ù‡ - Ø¯Ø± Ù†Ø³Ø®Ù‡â€ŒÙ‡Ø§ÛŒ Ø¢ØªÛŒ Ø­Ø°Ù Ø®ÙˆØ§Ù‡Ø¯ Ø´Ø¯
    Legacy database function - will be removed in future versions
    """
    logger.warning("Using legacy db function. Please migrate to DBManager.")
    logger.warning("Ø§Ø³ØªÙØ§Ø¯Ù‡ Ø§Ø² ØªØ§Ø¨Ø¹ Ù‚Ø¯ÛŒÙ…ÛŒ db. Ù„Ø·ÙØ§Ù‹ Ø¨Ù‡ DBManager Ù…Ù‡Ø§Ø¬Ø±Øª Ú©Ù†ÛŒØ¯.")
    db_manager = DBManager()
    return await db_manager.db(query, params, fetch)

def validate_database_config() -> bool:
    """Ø§Ø¹ØªØ¨Ø§Ø±Ø³Ù†Ø¬ÛŒ ØªÙ†Ø¸ÛŒÙ…Ø§Øª Ù¾Ø§ÛŒÚ¯Ø§Ù‡ Ø¯Ø§Ø¯Ù‡ - Validate database configuration"""
    try:
        required_vars = ['DATABASE_URL']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            logger.error(f"Ù…ØªØºÛŒØ±Ù‡Ø§ÛŒ Ù…Ø­ÛŒØ·ÛŒ Ù…ÙˆØ±Ø¯ Ù†ÛŒØ§Ø² Ù…ÙˆØ¬ÙˆØ¯ Ù†ÛŒØ³ØªÙ†Ø¯: {missing_vars}")
            return False
        
        # Test database URL format
        db_url = os.getenv('DATABASE_URL')
        if not db_url.startswith(('postgresql://', 'postgres://')):
            logger.error("Invalid DATABASE_URL format. Must start with postgresql:// or postgres://")
            logger.error("ÙØ±Ù…Øª DATABASE_URL Ù†Ø§Ù…Ø¹ØªØ¨Ø± Ø§Ø³Øª. Ø¨Ø§ÛŒØ¯ Ø¨Ø§ postgresql:// ÛŒØ§ postgres:// Ø´Ø±ÙˆØ¹ Ø´ÙˆØ¯")
            return False
        
        logger.info("Database configuration validated successfully")
        logger.info("ØªÙ†Ø¸ÛŒÙ…Ø§Øª Ù¾Ø§ÛŒÚ¯Ø§Ù‡ Ø¯Ø§Ø¯Ù‡ Ø¨Ø§ Ù…ÙˆÙÙ‚ÛŒØª Ø§Ø¹ØªØ¨Ø§Ø±Ø³Ù†Ø¬ÛŒ Ø´Ø¯")
        return True
    except Exception as e:
        logger.error(f"Error validating database config: {e}")
        return False

# Export main classes and functions
__all__ = [
    'DBManager',
    'UserStats', 
    'ChatStats',
    'DatabaseError',
    'UserNotFoundError', 
    'TransactionError',
    'setup_database',
    'initialize_pool',
    'validate_database_config',
    'db'  # Legacy support
]

