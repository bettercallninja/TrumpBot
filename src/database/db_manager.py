#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
پیشرفته‌ترین مدیریت پایگاه داده با پشتیبانی کامل از زبان فارسی
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
    """خطای پایگاه داده - Database Error"""
    pass

class UserNotFoundError(DatabaseError):
    """کاربر یافت نشد - User Not Found Error"""
    pass

class TransactionError(DatabaseError):
    """خطای تراکنش - Transaction Error"""
    pass

class QueryType(Enum):
    """انواع کوئری - Query Types"""
    SELECT = "SELECT"
    INSERT = "INSERT" 
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    TRANSACTION = "TRANSACTION"

@dataclass
class UserStats:
    """آمار کاربر - User Statistics"""
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
    """آمار چت - Chat Statistics"""
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
    """مقداردهی اولیه استخر اتصالات - Initialize the database connection pool"""
    global pool
    if pool is None:
        try:
            pool = AsyncConnectionPool(
                conninfo=DATABASE_URL,
                min_size=DB_POOL_MIN_SIZE, 
                max_size=DB_POOL_MAX_SIZE,
                open=False  # Don't open in constructor
            )
            # Open the pool properly using await
            await pool.open()
            logger.info(f"Database connection pool initialized: min={DB_POOL_MIN_SIZE}, max={DB_POOL_MAX_SIZE}")
            logger.info(f"استخر اتصالات پایگاه داده مقداردهی شد: کمینه={DB_POOL_MIN_SIZE}, بیشینه={DB_POOL_MAX_SIZE}")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            logger.error(f"خطا در مقداردهی استخر پایگاه داده: {e}")
            raise DatabaseError(f"Database initialization failed: {e}")

async def refresh_pool() -> None:
    """تازه‌سازی استخر اتصالات - Refresh the database connection pool"""
    global pool
    try:
        if pool:
            logger.info("Refreshing database connection pool...")
            logger.info("در حال تازه‌سازی استخر اتصالات پایگاه داده...")
            # Close the existing pool
            await pool.close()
            # Create a new pool
            pool = None
            await initialize_pool()
            logger.info("Database connection pool refreshed successfully")
            logger.info("استخر اتصالات پایگاه داده با موفقیت تازه‌سازی شد")
    except Exception as e:
        logger.error(f"Failed to refresh database pool: {e}")
        logger.error(f"خطا در تازه‌سازی استخر پایگاه داده: {e}")
        # Try to initialize a new pool anyway
        pool = None
        await initialize_pool()

class DBManager:
    """
    مدیر پیشرفته پایگاه داده با قابلیت‌های کامل
    Advanced Database Manager with comprehensive functionality and Persian support
    """
    
    def __init__(self):
        self._pool = pool
        self._query_cache: Dict[str, Any] = {}
        self._cache_ttl = 300  # 5 minutes cache TTL
        self._last_pool_refresh = time.time()
        self._pool_refresh_interval = 3600  # Refresh pool every hour
        
    async def _validate_connection(self, conn) -> bool:
        """
        اعتبارسنجی اتصال پایگاه داده
        Validate database connection by executing a simple query
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            # Execute a simple query to check if connection is valid
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")
                result = await cur.fetchone()
                return result is not None and result[0] == 1
        except Exception as e:
            logger.warning(f"Connection validation failed: {e}")
            return False
            
    async def ensure_pool(self) -> None:
        """اطمینان از وجود استخر اتصالات - Ensure connection pool exists and is healthy"""
        # If no pool exists, initialize it
        if not self._pool:
            await initialize_pool()
            self._pool = pool
            self._last_pool_refresh = time.time()
            return
            
        # Check if we need to refresh the pool based on time
        current_time = time.time()
        if current_time - self._last_pool_refresh > self._pool_refresh_interval:
            logger.info("Pool refresh interval reached, refreshing connection pool...")
            await refresh_pool()
            self._pool = pool
            self._last_pool_refresh = current_time
    
    async def db(self, query: str, params: Optional[Tuple] = None, fetch: Optional[str] = None, 
                retry_count: int = 0) -> Any:
        """
        اجرای کوئری پایگاه داده با مدیریت خطا و تلاش مجدد
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
            # Log query for debugging in case of issues
            if retry_count > 0:
                logger.debug(f"Retry attempt {retry_count} for query: {query}")
                
            async with self._pool.connection() as conn:
                # Validate connection before executing query
                if not await self._validate_connection(conn):
                    logger.warning("Connection validation failed, refreshing pool...")
                    await refresh_pool()
                    self._pool = pool
                    self._last_pool_refresh = time.time()
                    # Try again with a fresh connection
                    if retry_count < DB_RETRY_ATTEMPTS:
                        return await self.db(query, params, fetch, retry_count + 1)
                    else:
                        raise DatabaseError("Connection validation failed repeatedly")
                
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
            # Handle connection errors with retry logic
            if retry_count < DB_RETRY_ATTEMPTS:
                logger.warning(f"Database connection error, retrying... ({retry_count + 1}/{DB_RETRY_ATTEMPTS})")
                logger.warning(f"خطای اتصال پایگاه داده، تلاش مجدد... ({retry_count + 1}/{DB_RETRY_ATTEMPTS})")
                
                # Force pool refresh on connection errors
                if "connection" in str(e).lower() or "timeout" in str(e).lower():
                    logger.info("Connection error detected, refreshing pool before retry...")
                    await refresh_pool()
                    self._pool = pool
                    self._last_pool_refresh = time.time()
                
                # Exponential backoff before retry
                await asyncio.sleep(1 * (retry_count + 1))
                return await self.db(query, params, fetch, retry_count + 1)
            else:
                logger.error(f"Database connection failed after {DB_RETRY_ATTEMPTS} attempts: {e}")
                logger.error(f"اتصال پایگاه داده پس از {DB_RETRY_ATTEMPTS} تلاش ناموفق بود: {e}")
                raise DatabaseError(f"Database connection failed: {e}")
                
        except psycopg.InterfaceError as e:
            # Handle interface errors (like closed connection)
            logger.warning(f"Database interface error: {e}, refreshing pool and retrying...")
            await refresh_pool()
            self._pool = pool
            self._last_pool_refresh = time.time()
            
            if retry_count < DB_RETRY_ATTEMPTS:
                return await self.db(query, params, fetch, retry_count + 1)
            else:
                raise DatabaseError(f"Database interface error persisted: {e}")
                
        except Exception as e:
            # Log detailed information about other errors
            logger.error(f"Database error: {str(e)}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            logger.error(f"خطای پایگاه داده: {str(e)}")
            raise DatabaseError(f"Query execution failed: {e}")
    
    async def transaction(self, queries: List[Tuple[str, Optional[Tuple]]]) -> bool:
        """
        اجرای چندین کوئری در یک تراکنش
        Execute multiple queries in a transaction
        
        Args:
            queries: List of (query, params) tuples
            
        Returns:
            True if transaction succeeded, False otherwise
        """
        await self.ensure_pool()
        
        retry_count = 0
        max_retries = DB_RETRY_ATTEMPTS
        
        while retry_count <= max_retries:
            try:
                async with self._pool.connection() as conn:
                    # Validate connection before starting transaction
                    if not await self._validate_connection(conn):
                        logger.warning("Connection validation failed before transaction, refreshing pool...")
                        await refresh_pool()
                        self._pool = pool
                        self._last_pool_refresh = time.time()
                        retry_count += 1
                        continue
                        
                    async with conn.transaction():
                        for query, params in queries:
                            await conn.execute(query, params)
                            
                logger.info(f"Transaction completed successfully with {len(queries)} queries")
                logger.info(f"تراکنش با موفقیت با {len(queries)} کوئری کامل شد")
                return True
                
            except psycopg.OperationalError as e:
                # Handle connection errors
                logger.warning(f"Transaction connection error (attempt {retry_count+1}/{max_retries+1}): {e}")
                
                # Force pool refresh on connection errors
                if "connection" in str(e).lower() or "timeout" in str(e).lower():
                    logger.info("Connection error detected in transaction, refreshing pool...")
                    await refresh_pool()
                    self._pool = pool
                    self._last_pool_refresh = time.time()
                
                if retry_count < max_retries:
                    retry_count += 1
                    # Exponential backoff
                    await asyncio.sleep(1 * retry_count)
                    continue
                else:
                    logger.error(f"Transaction failed after {max_retries+1} attempts: {e}")
                    logger.error(f"تراکنش پس از {max_retries+1} تلاش ناموفق بود: {e}")
                    raise TransactionError(f"Transaction failed: {e}")
            
            except psycopg.InterfaceError as e:
                # Handle interface errors
                logger.warning(f"Transaction interface error: {e}, refreshing pool and retrying...")
                await refresh_pool()
                self._pool = pool
                self._last_pool_refresh = time.time()
                
                if retry_count < max_retries:
                    retry_count += 1
                    continue
                else:
                    raise TransactionError(f"Transaction interface error persisted: {e}")
                    
            except Exception as e:
                # Log details for other errors
                logger.error(f"Transaction failed: {e}")
                logger.error(f"تراکنش ناموفق بود: {e}")
                logger.error(f"Queries: {queries}")
                raise TransactionError(f"Transaction failed: {e}")

    # =============================================================================
    # مدیریت کاربران - User Management
    # =============================================================================
    
    async def get_user(self, chat_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """دریافت اطلاعات کاربر - Get user data from the database"""
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
        """ایجاد کاربر جدید - Create new user"""
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
            logger.info(f"کاربر ایجاد/به‌روزرسانی شد: {first_name} ({user_id}) در چت {chat_id}")
            return True
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            logger.error(f"خطا در ایجاد کاربر: {e}")
            return False
    
    async def get_chat_language(self, chat_id: int) -> str:
        """دریافت زبان پیش‌فرض چت - Get chat default language"""
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
        """به‌روزرسانی فعالیت کاربر - Update user activity"""
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
        """دریافت آمار کامل کاربر - Get comprehensive user statistics"""
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
        """به‌روزرسانی زبان کاربر - Update user language preference"""
        try:
            await self.db(
                "UPDATE players SET language = %s WHERE chat_id = %s AND user_id = %s",
                (language, chat_id, user_id)
            )
            logger.info(f"Language updated for user {user_id}: {language}")
            logger.info(f"زبان کاربر {user_id} به‌روزرسانی شد: {language}")
            return True
        except Exception as e:
            logger.error(f"Error updating user language: {e}")
            return False
    
    async def get_user_level(self, chat_id: int, user_id: int) -> int:
        """Get user level with fallback to 1"""
        try:
            level_data = await self.db(
                "SELECT level FROM players WHERE chat_id=%s AND user_id=%s",
                (chat_id, user_id),
                fetch="one_dict"
            )
            return level_data['level'] if level_data else 1
        except Exception as e:
            logger.error(f"Error getting user level: {e}")
            return 1
    
    async def update_user_score(self, chat_id: int, user_id: int, score_change: int) -> Optional[int]:
        """به‌روزرسانی امتیاز کاربر - Update user score"""
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
        """به‌روزرسانی جان کاربر - Update user HP"""
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
        """به‌روزرسانی ستاره‌های تلگرام - Update user TG Stars"""
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
    # مدیریت موجودی - Inventory Management
    # =============================================================================
    
    async def get_inventory(self, chat_id: int, user_id: int) -> Dict[str, int]:
        """دریافت موجودی کاربر - Get user inventory from the database"""
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
        """دریافت تعداد آیتم خاص - Get quantity of specific item"""
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
        """افزودن آیتم به موجودی - Add item to inventory"""
        try:
            await self.db("""
                INSERT INTO inventories (chat_id, user_id, item, qty)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (chat_id, user_id, item) 
                DO UPDATE SET qty = inventories.qty + EXCLUDED.qty
            """, (chat_id, user_id, item, quantity))
            
            logger.info(f"Added {quantity}x {item} to user {user_id} inventory")
            logger.info(f"{quantity} عدد {item} به موجودی کاربر {user_id} اضافه شد")
            return True
        except Exception as e:
            logger.error(f"Error adding item to inventory: {e}")
            return False
    
    async def remove_item(self, chat_id: int, user_id: int, item: str, quantity: int = 1) -> bool:
        """حذف آیتم از موجودی - Remove item from inventory"""
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
            logger.info(f"{quantity} عدد {item} از موجودی کاربر {user_id} حذف شد")
            return True
        except Exception as e:
            logger.error(f"Error removing item from inventory: {e}")
            return False
    
    async def get_inventory_value(self, chat_id: int, user_id: int) -> Dict[str, int]:
        """محاسبه ارزش کل موجودی - Calculate total inventory value"""
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
    # مدیریت حملات - Attack Management
    # =============================================================================
    
    async def record_attack(self, chat_id: int, attacker_id: int, victim_id: int, 
                           damage: int, weapon: str) -> bool:
        """ثبت حمله - Record an attack"""
        try:
            current_time = int(time.time())
            await self.db("""
                INSERT INTO attacks (chat_id, attacker_id, victim_id, damage, attack_time, weapon)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (chat_id, attacker_id, victim_id, damage, current_time, weapon))
            
            logger.info(f"Attack recorded: {attacker_id} -> {victim_id} ({damage} damage with {weapon})")
            logger.info(f"حمله ثبت شد: {attacker_id} -> {victim_id} ({damage} آسیب با {weapon})")
            return True
        except Exception as e:
            logger.error(f"Error recording attack: {e}")
            return False
    
    async def get_attack_history(self, chat_id: int, user_id: Optional[int] = None, 
                                limit: int = 50) -> List[Dict[str, Any]]:
        """دریافت تاریخچه حملات - Get attack history"""
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
        """دریافت آمار جنگی کاربر - Get user combat statistics"""
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
    # مدیریت خریدها - Purchase Management  
    # =============================================================================
    
    async def record_purchase(self, chat_id: int, user_id: int, item: str, price: int, 
                             payment_type: str = "medals") -> bool:
        """ثبت خرید - Record a purchase"""
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
            logger.info(f"خرید ثبت شد: کاربر {user_id} آیتم {item} را به قیمت {price} {payment_type} خرید")
            return True
        except Exception as e:
            logger.error(f"Error recording purchase: {e}")
            return False
    
    async def get_purchase_history(self, chat_id: int, user_id: Optional[int] = None, 
                                  limit: int = 50) -> List[Dict[str, Any]]:
        """دریافت تاریخچه خریدها - Get purchase history"""
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
        """دریافت آمار خرج کرد - Get spending statistics"""
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
    # مدیریت کولدان - Cooldown Management
    # =============================================================================
    
    async def check_cooldown(self, chat_id: int, user_id: int, cooldown_type: str) -> int:
        """
        بررسی وضعیت کولدان برای یک اقدام خاص
        Check if a cooldown is active and return remaining time in seconds
        Returns 0 if no cooldown is active
        """
        try:
            current_time = int(time.time())
            cooldown_data = await self.db(
                "SELECT expires_at FROM cooldowns WHERE chat_id=%s AND user_id=%s AND cooldown_type=%s AND expires_at > %s",
                (chat_id, user_id, cooldown_type, current_time),
                fetch="one_dict"
            )
            
            if cooldown_data and cooldown_data.get("expires_at"):
                # Return remaining seconds
                return cooldown_data["expires_at"] - current_time
            return 0
        except Exception as e:
            logger.error(f"Error checking cooldown: {e}")
            logger.error(f"خطا در بررسی کولدان: {e}")
            return 0
    
    async def set_cooldown(self, chat_id: int, user_id: int, cooldown_type: str, duration: int) -> bool:
        """
        تنظیم کولدان برای یک اقدام خاص
        Set a cooldown timer for a specific action
        Returns True if successful, False otherwise
        """
        try:
            current_time = int(time.time())
            expires_at = current_time + duration
            
            # First remove any existing cooldown of this type
            await self.db(
                "DELETE FROM cooldowns WHERE chat_id=%s AND user_id=%s AND cooldown_type=%s",
                (chat_id, user_id, cooldown_type)
            )
            
            # Then add the new cooldown
            await self.db(
                "INSERT INTO cooldowns (chat_id, user_id, cooldown_type, expires_at, created_at) VALUES (%s, %s, %s, %s, %s)",
                (chat_id, user_id, cooldown_type, expires_at, current_time)
            )
            
            logger.debug(f"Cooldown set for user {user_id} in chat {chat_id}: {cooldown_type} for {duration}s")
            return True
        except Exception as e:
            logger.error(f"Error setting cooldown: {e}")
            return False
            
    async def cleanup_expired_cooldowns(self) -> int:
        """
        پاکسازی کولدان‌های منقضی شده
        Clean up expired cooldowns from the database
        
        Returns:
            Number of removed cooldowns
        """
        try:
            current_time = int(time.time())
            result = await self.db(
                "DELETE FROM cooldowns WHERE expires_at < %s RETURNING id",
                (current_time,),
                fetch="all"
            )
            removed_count = len(result) if result else 0
            logger.info(f"Cleaned up {removed_count} expired cooldowns")
            return removed_count
        except Exception as e:
            logger.error(f"Error cleaning up expired cooldowns: {e}")
            return 0
            
    async def repair_cooldowns_table(self) -> bool:
        """
        تعمیر جدول کولدان‌ها و حل مشکلات احتمالی
        Repair cooldowns table and fix potential schema issues
        
        Returns:
            True if repair was successful, False otherwise
        """
        try:
            # 1. Validate the table structure
            await self.db("""
                DO $$
                BEGIN
                    -- Ensure cooldown_type column exists and is properly typed
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                  WHERE table_name='cooldowns' AND column_name='cooldown_type') THEN
                        ALTER TABLE cooldowns ADD COLUMN cooldown_type TEXT NOT NULL DEFAULT 'attack';
                    END IF;
                    
                    -- Ensure data JSONB column exists
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                  WHERE table_name='cooldowns' AND column_name='data') THEN
                        ALTER TABLE cooldowns ADD COLUMN data JSONB DEFAULT '{}';
                    END IF;
                    
                    -- Ensure proper constraint exists
                    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints
                                  WHERE table_name='cooldowns' AND constraint_name='future_expiry') THEN
                        ALTER TABLE cooldowns ADD CONSTRAINT future_expiry CHECK (expires_at > created_at);
                    END IF;
                    
                    -- Add unique constraint if it doesn't exist
                    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints
                                  WHERE table_name='cooldowns' AND constraint_name='cooldowns_chat_user_type_key') THEN
                        ALTER TABLE cooldowns ADD CONSTRAINT cooldowns_chat_user_type_key 
                        UNIQUE (chat_id, user_id, cooldown_type);
                    END IF;
                END
                $$;
            """)
            
            # 2. Cleanup any invalid entries (negative durations, etc)
            await self.db(
                "DELETE FROM cooldowns WHERE expires_at <= created_at",
                fetch="count"
            )
            
            # 3. Convert any old attack_cooldown entries if they exist
            try:
                # Check if the old attack_cooldown table exists
                old_table_exists = await self.db("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'attack_cooldown'
                    )
                """, fetch="one")
                
                if old_table_exists and old_table_exists[0]:
                    logger.info("Found old attack_cooldown table, migrating data...")
                    
                    # Migrate data from old table to new cooldowns table
                    await self.db("""
                        INSERT INTO cooldowns (chat_id, user_id, cooldown_type, expires_at, created_at)
                        SELECT chat_id, user_id, 'attack', expires_at, created_at 
                        FROM attack_cooldown
                        ON CONFLICT (chat_id, user_id, cooldown_type) DO UPDATE
                        SET expires_at = EXCLUDED.expires_at,
                            created_at = EXCLUDED.created_at
                    """)
                    
                    # Optionally rename the old table instead of dropping it
                    await self.db("ALTER TABLE IF EXISTS attack_cooldown RENAME TO attack_cooldown_legacy")
                    
                    logger.info("Migration from attack_cooldown to cooldowns completed")
            except Exception as migration_error:
                logger.warning(f"Error during attack_cooldown migration: {migration_error}")
            
            # 4. Report success
            logger.info("Cooldowns table repair completed successfully")
            return True
        except Exception as e:
            logger.error(f"Error repairing cooldowns table: {e}")
            return False
            
    async def handle_attack_cooldown(self, chat_id: int, user_id: int) -> Optional[int]:
        """
        بررسی و مدیریت کولدان حمله
        Check if user is in attack cooldown and return remaining time
        
        Returns:
            Remaining seconds if cooldown active, None if no cooldown or error
        """
        try:
            # Check for attack cooldown
            remaining = await self.check_cooldown(chat_id, user_id, "attack")
            if remaining > 0:
                return remaining
                
            return None
        except Exception as e:
            logger.error(f"Error handling attack cooldown: {e}")
            return None
    
    async def set_attack_cooldown(self, chat_id: int, user_id: int, duration: int = 300) -> bool:
        """
        تنظیم کولدان حمله برای کاربر
        Set attack cooldown for a user
        
        Args:
            chat_id: Chat ID
            user_id: User ID
            duration: Cooldown duration in seconds (default: 5 minutes)
            
        Returns:
            True if cooldown was set, False otherwise
        """
        try:
            return await self.set_cooldown(chat_id, user_id, "attack", duration)
        except Exception as e:
            logger.error(f"Error setting attack cooldown: {e}")
            return False
            
            logger.info(f"Set cooldown for user {user_id}, type {cooldown_type}, duration {duration}s")
            logger.info(f"کولدان برای کاربر {user_id}، نوع {cooldown_type}، مدت {duration} ثانیه تنظیم شد")
            return True
        except Exception as e:
            logger.error(f"Error setting cooldown: {e}")
            logger.error(f"خطا در تنظیم کولدان: {e}")
            return False
    
    async def clear_cooldown(self, chat_id: int, user_id: int, cooldown_type: str) -> bool:
        """
        پاکسازی کولدان برای یک اقدام خاص
        Clear a cooldown for a specific action
        Returns True if successful, False otherwise
        """
        try:
            await self.db(
                "DELETE FROM cooldowns WHERE chat_id=%s AND user_id=%s AND cooldown_type=%s",
                (chat_id, user_id, cooldown_type)
            )
            
            logger.info(f"Cleared cooldown for user {user_id}, type {cooldown_type}")
            logger.info(f"کولدان برای کاربر {user_id}، نوع {cooldown_type} پاک شد")
            return True
        except Exception as e:
            logger.error(f"Error clearing cooldown: {e}")
            logger.error(f"خطا در پاکسازی کولدان: {e}")
            return False
    
    async def get_all_cooldowns(self, chat_id: int, user_id: int) -> Dict[str, int]:
        """
        دریافت تمامی کولدان‌های فعال کاربر
        Get all active cooldowns for a user
        Returns a dictionary with cooldown_type as key and remaining seconds as value
        """
        try:
            current_time = int(time.time())
            cooldowns = await self.db(
                "SELECT cooldown_type, expires_at FROM cooldowns WHERE chat_id=%s AND user_id=%s AND expires_at > %s",
                (chat_id, user_id, current_time),
                fetch="all_dicts"
            )
            
            return {cd["cooldown_type"]: cd["expires_at"] - current_time for cd in cooldowns} if cooldowns else {}
        except Exception as e:
            logger.error(f"Error getting all cooldowns: {e}")
            logger.error(f"خطا در دریافت تمامی کولدان‌ها: {e}")
            return {}
    
    # Legacy cooldown functions - preserved for backward compatibility
    async def set_cooldown_legacy(self, chat_id: int, user_id: int, action: str, 
                          duration: int, data: Optional[str] = None) -> bool:
        """تنظیم کولدان - Set cooldown for an action (Legacy)"""
        try:
            # Redirect to new implementation
            logger.warning("Using legacy set_cooldown with action parameter. Please update to use cooldown_type parameter.")
            return await self.set_cooldown(chat_id, user_id, action, duration)
        except Exception as e:
            logger.error(f"Error setting cooldown: {e}")
            return False
    
    async def get_cooldown(self, chat_id: int, user_id: int, action: str) -> Optional[int]:
        """دریافت زمان باقیمانده کولدان - Get remaining cooldown time (Legacy)"""
        try:
            # Redirect to new implementation
            logger.warning("Using legacy get_cooldown. Please update to check_cooldown.")
            return await self.check_cooldown(chat_id, user_id, action)
        except Exception as e:
            logger.error(f"Error getting cooldown: {e}")
            return 0
    
    async def clear_cooldown_legacy(self, chat_id: int, user_id: int, action: str) -> bool:
        """پاک کردن کولدان - Clear cooldown (Legacy)"""
        try:
            # Redirect to new implementation
            logger.warning("Using legacy clear_cooldown with action parameter. Please update to use cooldown_type parameter.")
            return await self.clear_cooldown(chat_id, user_id, action)
        except Exception as e:
            logger.error(f"Error clearing cooldown: {e}")
            return False
    
    async def cleanup_expired_cooldowns(self) -> int:
        """پاک‌سازی کولدان‌های منقضی - Clean up expired cooldowns"""
        try:
            current_time = int(time.time())
            result = await self.db(
                "DELETE FROM cooldowns WHERE expires_at < %s",
                (current_time,)
            )
            logger.info(f"Cleaned up expired cooldowns")
            logger.info(f"کولدان‌های منقضی پاک‌سازی شدند")
            return True
        except Exception as e:
            logger.error(f"Error cleaning up cooldowns: {e}")
            return False
            
    async def repair_cooldowns_table(self) -> int:
        """
        تعمیر جدول کولدان‌ها
        Repair cooldowns table if there are any inconsistencies between column names
        """
        try:
            logger.info("Repairing cooldowns table...")
            
            # 1. First check if we need to migrate legacy cooldowns
            try:
                # Check if the action column exists (old schema)
                await self.db("SELECT action FROM cooldowns LIMIT 1")
                # If we get here, action column exists, we need to migrate
                logger.info("Legacy cooldown table detected with 'action' column, migrating data...")
                
                # Get all legacy cooldowns
                legacy_cooldowns = await self.db(
                    "SELECT chat_id, user_id, action, expires_at, created_at, data FROM cooldowns",
                    fetch="all_dicts"
                )
                
                # Create a temporary table for the migration
                await self.db("""
                    CREATE TEMP TABLE cooldowns_new(
                        id SERIAL PRIMARY KEY,
                        chat_id BIGINT NOT NULL,
                        user_id BIGINT NOT NULL,
                        cooldown_type TEXT NOT NULL,
                        expires_at BIGINT NOT NULL,
                        created_at BIGINT DEFAULT EXTRACT(EPOCH FROM NOW()),
                        data JSONB DEFAULT '{}',
                        UNIQUE(chat_id, user_id, cooldown_type)
                    )
                """)
                
                # Insert legacy data into the new table with correct column names
                for cd in legacy_cooldowns:
                    await self.db(
                        "INSERT INTO cooldowns_new (chat_id, user_id, cooldown_type, expires_at, created_at, data) VALUES (%s, %s, %s, %s, %s, %s)",
                        (cd["chat_id"], cd["user_id"], cd["action"], cd["expires_at"], cd["created_at"], cd.get("data", "{}"))
                    )
                
                # Drop the old table and rename the new one
                await self.db("DROP TABLE cooldowns")
                await self.db("ALTER TABLE cooldowns_new RENAME TO cooldowns")
                
                # Re-create the correct indexes
                await self.db("""
                    ALTER TABLE cooldowns ADD CONSTRAINT future_expiry CHECK (expires_at > created_at)
                """)
                
                logger.info(f"Successfully migrated {len(legacy_cooldowns)} legacy cooldowns")
                return len(legacy_cooldowns)
                
            except Exception as e:
                # If the action column doesn't exist, we might already have the new schema
                if "column \"action\" does not exist" in str(e):
                    logger.info("Cooldowns table already has the correct schema")
                else:
                    logger.error(f"Error checking legacy cooldowns: {e}")
            
            # 2. Clean up any duplicate entries
            duplicates_removed = await self.db("""
                DELETE FROM cooldowns 
                WHERE id IN (
                    SELECT id FROM (
                        SELECT id, ROW_NUMBER() OVER (PARTITION BY chat_id, user_id, cooldown_type ORDER BY expires_at DESC) as row_num
                        FROM cooldowns
                    ) as duplicates 
                    WHERE row_num > 1
                )
            """)
            
            # 3. Remove any expired cooldowns
            current_time = int(time.time())
            expired_removed = await self.db(
                "DELETE FROM cooldowns WHERE expires_at < %s",
                (current_time,)
            )
            
            # 4. Re-create indexes if needed
            try:
                await self.db("DROP INDEX IF EXISTS idx_cooldowns_user")
                await self.db("CREATE INDEX idx_cooldowns_user ON cooldowns(chat_id, user_id)")
                
                await self.db("DROP INDEX IF EXISTS idx_cooldowns_expiry")
                await self.db("CREATE INDEX idx_cooldowns_expiry ON cooldowns(expires_at)")
            except Exception as e:
                logger.error(f"Error recreating indexes: {e}")
            
            logger.info("Cooldowns table repair completed")
            return 1
            
        except Exception as e:
            logger.error(f"Error repairing cooldowns table: {e}")
            return 0

    async def update_players_table_schema(self) -> bool:
        """Update players table to include missing columns needed by commands"""
        try:
            # Add missing columns if they don't exist
            missing_columns = [
                ("max_hp", "INT DEFAULT 100"),
                ("last_attack", "BIGINT"),
                ("last_attack_time", "BIGINT"),
                ("experience", "INT DEFAULT 0"),
                ("join_date", "BIGINT DEFAULT EXTRACT(EPOCH FROM NOW())"),
                ("attacks_made", "INT DEFAULT 0"),
                ("attacks_received", "INT DEFAULT 0"),
                ("victories", "INT DEFAULT 0"),
                ("defeats", "INT DEFAULT 0"),
                ("shields_used", "INT DEFAULT 0"),
                ("items_bought", "INT DEFAULT 0"),
                ("activity_points", "INT DEFAULT 0")
            ]
            
            for column_name, column_def in missing_columns:
                try:
                    await self.db(f"ALTER TABLE players ADD COLUMN IF NOT EXISTS {column_name} {column_def}")
                    logger.info(f"Added column {column_name} to players table")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        logger.info(f"Column {column_name} already exists")
                    else:
                        logger.error(f"Error adding column {column_name}: {e}")
            
            # Update max_hp for existing users who might have it as NULL
            await self.db("UPDATE players SET max_hp = 100 WHERE max_hp IS NULL")
            
            # Update join_date for existing users who might have it as NULL
            await self.db("UPDATE players SET join_date = created_at WHERE join_date IS NULL")
            
            # Update HP constraint to use max_hp
            try:
                await self.db("ALTER TABLE players DROP CONSTRAINT IF EXISTS positive_hp")
                await self.db("ALTER TABLE players ADD CONSTRAINT positive_hp CHECK (hp >= 0 AND hp <= COALESCE(max_hp, 100))")
            except Exception as e:
                logger.warning(f"Could not update HP constraint: {e}")
            
            logger.info("Players table schema updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating players table schema: {e}")
            return False

    async def get_attack_history(self, chat_id: int, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get attack history for a user"""
        try:
            attacks = await self.db("""
                SELECT attacker_id, victim_id, damage, weapon, attack_time, is_critical, defense_reduced
                FROM attacks 
                WHERE chat_id = %s AND (attacker_id = %s OR victim_id = %s)
                ORDER BY attack_time DESC 
                LIMIT %s
            """, (chat_id, user_id, user_id, limit), fetch="all_dicts")
            
            return attacks or []
        except Exception as e:
            logger.error(f"Error getting attack history: {e}")
            return []

    async def get_purchase_history(self, chat_id: int, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get purchase history for a user"""
        try:
            purchases = await self.db("""
                SELECT item, price, payment_type, purchase_time, quantity
                FROM purchases 
                WHERE chat_id = %s AND user_id = %s
                ORDER BY purchase_time DESC 
                LIMIT %s
            """, (chat_id, user_id, limit), fetch="all_dicts")
            
            return purchases or []
        except Exception as e:
            logger.error(f"Error getting purchase history: {e}")
            return []

    async def get_user_combat_stats(self, chat_id: int, user_id: int) -> Dict[str, Any]:
        """Get detailed combat statistics for a user"""
        try:
            # Get attack statistics
            attack_stats = await self.db("""
                SELECT 
                    COUNT(*) as total_attacks,
                    SUM(damage) as total_damage_dealt,
                    AVG(damage) as avg_damage_dealt,
                    MAX(damage) as max_damage_dealt,
                    COUNT(CASE WHEN is_critical THEN 1 END) as critical_hits
                FROM attacks 
                WHERE chat_id = %s AND attacker_id = %s
            """, (chat_id, user_id), fetch="one_dict")
            
            # Get defense statistics
            defense_stats = await self.db("""
                SELECT 
                    COUNT(*) as times_attacked,
                    SUM(damage) as total_damage_taken,
                    AVG(damage) as avg_damage_taken,
                    MAX(damage) as max_damage_taken,
                    COUNT(CASE WHEN defense_reduced THEN 1 END) as successful_defenses
                FROM attacks 
                WHERE chat_id = %s AND victim_id = %s
            """, (chat_id, user_id), fetch="one_dict")
            
            # Get weapon preferences
            weapon_stats = await self.db("""
                SELECT weapon, COUNT(*) as usage_count
                FROM attacks 
                WHERE chat_id = %s AND attacker_id = %s 
                GROUP BY weapon 
                ORDER BY usage_count DESC 
                LIMIT 5
            """, (chat_id, user_id), fetch="all_dicts")
            
            return {
                "attack_stats": attack_stats or {},
                "defense_stats": defense_stats or {},
                "weapon_preferences": weapon_stats or []
            }
        except Exception as e:
            logger.error(f"Error getting user combat stats: {e}")
            return {"attack_stats": {}, "defense_stats": {}, "weapon_preferences": []}

    # =============================================================================
    # مدیریت دفاع فعال - Active Defense Management
    # =============================================================================
    
    async def set_active_defense(self, chat_id: int, user_id: int, defense_type: str, 
                                duration: int) -> bool:
        """فعال‌سازی دفاع - Activate defense"""
        try:
            expires_at = int(time.time()) + duration
            await self.db("""
                INSERT INTO active_defenses (chat_id, user_id, defense_type, expires_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (chat_id, user_id) 
                DO UPDATE SET defense_type = EXCLUDED.defense_type, expires_at = EXCLUDED.expires_at
            """, (chat_id, user_id, defense_type, expires_at))
            
            logger.info(f"Active defense set for user {user_id}: {defense_type} for {duration} seconds")
            logger.info(f"دفاع فعال برای کاربر {user_id} تنظیم شد: {defense_type} برای {duration} ثانیه")
            return True
        except Exception as e:
            logger.error(f"Error setting active defense: {e}")
            return False
    
    async def get_active_defense(self, chat_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """دریافت دفاع فعال - Get active defense"""
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
        """پاک کردن دفاع فعال - Clear active defense"""
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
        """پاک‌سازی دفاع‌های منقضی - Clean up expired defenses"""
        try:
            current_time = int(time.time())
            await self.db(
                "DELETE FROM active_defenses WHERE expires_at < %s",
                (current_time,)
            )
            logger.info("Cleaned up expired defenses")
            logger.info("دفاع‌های منقضی پاک‌سازی شدند")
            return True
        except Exception as e:
            logger.error(f"Error cleaning up defenses: {e}")
    # =============================================================================
    # مدیریت لیدربورد و رتبه‌بندی - Leaderboard Management
    # =============================================================================
    
    async def get_leaderboard(self, chat_id: int, limit: int = 10, 
                             order_by: str = "score") -> List[Dict[str, Any]]:
        """دریافت لیدربورد - Get leaderboard"""
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
        """دریافت رتبه کاربر - Get user rank"""
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
        """دریافت آمار کامل چت - Get comprehensive chat statistics"""
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
    # گزارش‌گیری و تحلیل - Analytics and Reporting
    # =============================================================================
    
    async def get_daily_activity(self, chat_id: int, days: int = 7) -> Dict[str, List[int]]:
        """دریافت فعالیت روزانه - Get daily activity statistics"""
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
        """دریافت آمار استفاده از سلاح‌ها - Get weapon usage statistics"""
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
        """دریافت محبوبیت آیتم‌ها - Get item popularity statistics"""
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
        """صادرات کامل داده‌های کاربر - Export complete user data"""
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
    # بکاپ و بازیابی - Backup and Recovery  
    # =============================================================================
    
    async def create_chat_backup(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """ایجاد بکاپ کامل چت - Create complete chat backup"""
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
            logger.info(f"بکاپ چت برای چت {chat_id} ایجاد شد")
            return backup_data
        except Exception as e:
            logger.error(f"Error creating chat backup: {e}")
            return None
    
    async def maintenance_cleanup(self) -> Dict[str, int]:
        """پاک‌سازی دوره‌ای پایگاه داده - Periodic database maintenance"""
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
            logger.info(f"نگهداری پایگاه داده کامل شد: {cleanup_stats}")
            return cleanup_stats
        except Exception as e:
            logger.error(f"Error during maintenance cleanup: {e}")
            return {}
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """دریافت آمار کلی پایگاه داده - Get overall database statistics"""
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

    async def log_message_interaction(self, chat_id: int = None, user_id: int = None, message_type: str = None, 
                                    data: Dict[str, Any] = None, intention: str = None, sentiment: str = None, 
                                    confidence_score: float = None, response_generated: bool = None, 
                                    timestamp: int = None) -> bool:
        """ثبت تعامل پیام کاربر - Log user message interaction"""
        try:
            # Handle both old and new calling patterns
            if data is None:
                data = {}
            
            # Add new parameters to data if provided
            if intention is not None:
                data['intention'] = intention
            if sentiment is not None:
                data['sentiment'] = sentiment
            if confidence_score is not None:
                data['confidence_score'] = confidence_score
            if response_generated is not None:
                data['response_generated'] = response_generated
            
            current_time = timestamp if timestamp else int(time.time())
            
            await self.db("""
                INSERT INTO interactions (chat_id, user_id, interaction_type, interaction_data, timestamp)
                VALUES (%s, %s, %s, %s, %s)
            """, (chat_id, user_id, message_type, json.dumps(data) if data else None, current_time))
            
            logger.info(f"Logged message interaction: {message_type} for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error logging message interaction: {e}")
            return False

    async def log_new_user_join(self, chat_id: int, user_id: int, user_lang: str = 'en') -> bool:
        """ثبت عضویت کاربر جدید - Log new user join"""
        try:
            current_time = int(time.time())
            
            # Create event data
            event_data = {
                "language": user_lang,
                "join_timestamp": current_time
            }
            
            # Log to interactions table if it exists
            await self.db("""
                INSERT INTO interactions (chat_id, user_id, interaction_type, interaction_data, timestamp)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (chat_id, user_id, "new_user_join", json.dumps(event_data), current_time))
            
            logger.info(f"Logged new user join: {user_id} in chat {chat_id}")
            return True
        except Exception as e:
            logger.error(f"Error logging new user join: {e}")
            return False

    async def log_user_event(self, user_id: int, chat_id: int, event_type: str, event_data: Dict[str, Any] = None) -> bool:
        """ثبت رویداد کاربر - Log user event"""
        try:
            current_time = int(time.time())
            
            # Log to interactions table
            await self.db("""
                INSERT INTO interactions (chat_id, user_id, interaction_type, interaction_data, timestamp)
                VALUES (%s, %s, %s, %s, %s)
            """, (chat_id, user_id, event_type, json.dumps(event_data) if event_data else None, current_time))
            
            logger.info(f"Logged user event: {event_type} for user {user_id} in chat {chat_id}")
            return True
        except Exception as e:
            logger.error(f"Error logging user event: {e}")
            return False


async def setup_database() -> None:
    """
    راه‌اندازی جداول پایگاه داده اگر وجود نداشته باشند
    Set up the database tables if they don't exist with enhanced schema
    """
    logger.info("Setting up database - راه‌اندازی پایگاه داده")
    
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
        logger.info("Groups table created/verified - جدول گروه‌ها ایجاد/تایید شد")
        
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
                max_hp INT DEFAULT 100,
                level INT DEFAULT 1,
                created_at BIGINT DEFAULT EXTRACT(EPOCH FROM NOW()),
                total_attacks INT DEFAULT 0,
                total_damage INT DEFAULT 0,
                times_attacked INT DEFAULT 0,
                damage_taken INT DEFAULT 0,
                preferred_weapon TEXT,
                settings JSONB DEFAULT '{}',
                -- Additional columns for commands compatibility
                experience INT DEFAULT 0,
                join_date BIGINT DEFAULT EXTRACT(EPOCH FROM NOW()),
                attacks_made INT DEFAULT 0,
                attacks_received INT DEFAULT 0,
                victories INT DEFAULT 0,
                defeats INT DEFAULT 0,
                shields_used INT DEFAULT 0,
                items_bought INT DEFAULT 0,
                activity_points INT DEFAULT 0,
                last_attack BIGINT,
                last_attack_time BIGINT,
                PRIMARY KEY(chat_id, user_id),
                CONSTRAINT positive_hp CHECK (hp >= 0 AND hp <= max_hp),
                CONSTRAINT positive_max_hp CHECK (max_hp >= 50 AND max_hp <= 200),
                CONSTRAINT positive_level CHECK (level >= 1),
                CONSTRAINT positive_tg_stars CHECK (tg_stars >= 0),
                CONSTRAINT positive_experience CHECK (experience >= 0),
                CONSTRAINT positive_activities CHECK (attacks_made >= 0 AND attacks_received >= 0 AND victories >= 0 AND defeats >= 0)
            )
        """)
        logger.info("Players table created/verified - جدول بازیکنان ایجاد/تایید شد")
        
        # Create enhanced cooldowns table
        await db_manager.db("""
            CREATE TABLE IF NOT EXISTS cooldowns(
                id SERIAL PRIMARY KEY,
                chat_id BIGINT NOT NULL,
                user_id BIGINT NOT NULL,
                cooldown_type TEXT NOT NULL,
                expires_at BIGINT NOT NULL,
                created_at BIGINT DEFAULT EXTRACT(EPOCH FROM NOW()),
                data JSONB DEFAULT '{}',
                UNIQUE(chat_id, user_id, cooldown_type),
                CONSTRAINT future_expiry CHECK (expires_at > created_at)
            )
        """)
        logger.info("Cooldowns table created/verified - جدول کولدان‌ها ایجاد/تایید شد")
        
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
        logger.info("Purchases table created/verified - جدول خریدها ایجاد/تایید شد")
        
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
        logger.info("Attacks table created/verified - جدول حملات ایجاد/تایید شد")
        
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
        logger.info("Inventories table created/verified - جدول موجودی‌ها ایجاد/تایید شد")
        
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
        logger.info("TG Stars purchases table created/verified - جدول خریدهای ستاره تلگرام ایجاد/تایید شد")

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
        logger.info("Active defenses table created/verified - جدول دفاع‌های فعال ایجاد/تایید شد")
        
        # Create active_boosts table for temporary item effects
        await db_manager.db("""
            CREATE TABLE IF NOT EXISTS active_boosts(
                id SERIAL PRIMARY KEY,
                chat_id BIGINT NOT NULL,
                user_id BIGINT NOT NULL,
                boost_type TEXT NOT NULL,
                boost_value DOUBLE PRECISION NOT NULL DEFAULT 1.0,
                expires_at BIGINT NOT NULL,
                activated_at BIGINT DEFAULT EXTRACT(EPOCH FROM NOW()),
                UNIQUE(chat_id, user_id, boost_type),
                CONSTRAINT future_expiry_boost CHECK (expires_at > activated_at),
                CONSTRAINT positive_boost CHECK (boost_value > 0)
            )
        """)
        logger.info("Active boosts table created/verified - جدول تقویت‌های فعال ایجاد/تایید شد")
        
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
        logger.info("Interactions table created/verified - جدول تعاملات ایجاد/تایید شد")
        
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
        logger.info("Player achievements table created/verified - جدول دستاوردهای بازیکن ایجاد/تایید شد")
        
        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_players_score ON players(chat_id, score DESC)",
            "CREATE INDEX IF NOT EXISTS idx_players_level ON players(chat_id, level DESC)",
            "CREATE INDEX IF NOT EXISTS idx_attacks_time ON attacks(chat_id, attack_time DESC)",
            "CREATE INDEX IF NOT EXISTS idx_attacks_attacker ON attacks(chat_id, attacker_id)",
            "CREATE INDEX IF NOT EXISTS idx_attacks_victim ON attacks(chat_id, victim_id)",
            "CREATE INDEX IF NOT EXISTS idx_purchases_time ON purchases(chat_id, purchase_time DESC)",
            "CREATE INDEX IF NOT EXISTS idx_inventories_user ON inventories(chat_id, user_id)",
            "CREATE INDEX IF NOT EXISTS idx_cooldowns_expires ON cooldowns(chat_id, user_id, expires_at)",
            "CREATE INDEX IF NOT EXISTS idx_cooldowns_type ON cooldowns(chat_id, user_id, cooldown_type)",
            "CREATE INDEX IF NOT EXISTS idx_defenses_expires ON active_defenses(chat_id, expires_at)",
            "CREATE INDEX IF NOT EXISTS idx_boosts_expires ON active_boosts(chat_id, user_id, expires_at)",
            "CREATE INDEX IF NOT EXISTS idx_boosts_type ON active_boosts(chat_id, user_id, boost_type)",
            "CREATE INDEX IF NOT EXISTS idx_achievements_user ON player_achievements(chat_id, user_id)",
            "CREATE INDEX IF NOT EXISTS idx_interactions_user ON interactions(chat_id, user_id, timestamp DESC)"
        ]
        
        for index_query in indexes:
            await db_manager.db(index_query)
        
        logger.info("Database indexes created/verified - ایندکس‌های پایگاه داده ایجاد/تایید شدند")
        
        # Fix cooldowns table issues - repair table structure and consolidate any mixed data
        try:
            logger.info("Repairing cooldowns table structure...")
            await db_manager.repair_cooldowns_table()
            logger.info("Cooldowns table structure repaired")
        except Exception as e:
            logger.error(f"Error repairing cooldowns table: {e}")
        
        # Update players table schema to include missing columns
        try:
            logger.info("Updating players table schema...")
            await db_manager.update_players_table_schema()
            logger.info("Players table schema updated")
        except Exception as e:
            logger.error(f"Error updating players table schema: {e}")
        
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
        
        logger.info("Database triggers created/verified - تریگرهای پایگاه داده ایجاد/تایید شدند")
        logger.info("Database setup complete - راه‌اندازی پایگاه داده کامل شد")
        
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        logger.error(f"خطا در راه‌اندازی پایگاه داده: {e}")
        raise DatabaseError(f"Database setup failed: {e}")

# =============================================================================
# توابع سازگاری و کمکی - Legacy Support and Helper Functions
# =============================================================================

async def db(query: str, params: Optional[Tuple] = None, fetch: Optional[str] = None) -> Any:
    """
    تابع قدیمی پایگاه داده - در نسخه‌های آتی حذف خواهد شد
    Legacy database function - will be removed in future versions
    """
    logger.warning("Using legacy db function. Please migrate to DBManager.")
    logger.warning("استفاده از تابع قدیمی db. لطفاً به DBManager مهاجرت کنید.")
    db_manager = DBManager()
    return await db_manager.db(query, params, fetch)

def validate_database_config() -> bool:
    """اعتبارسنجی تنظیمات پایگاه داده - Validate database configuration"""
    try:
        required_vars = ['DATABASE_URL']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            logger.error(f"متغیرهای محیطی مورد نیاز موجود نیستند: {missing_vars}")
            return False
        
        # Test database URL format
        db_url = os.getenv('DATABASE_URL')
        if not db_url.startswith(('postgresql://', 'postgres://')):
            logger.error("Invalid DATABASE_URL format. Must start with postgresql:// or postgres://")
            logger.error("فرمت DATABASE_URL نامعتبر است. باید با postgresql:// یا postgres:// شروع شود")
            return False
        
        logger.info("Database configuration validated successfully")
        logger.info("تنظیمات پایگاه داده با موفقیت اعتبارسنجی شد")
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
    'refresh_pool',
    'validate_database_config',
    'db',  # Legacy support
    'pool'  # Global connection pool
]
