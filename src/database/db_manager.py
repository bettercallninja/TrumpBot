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
                min_size=DB_POOL_MIN_SIZE, 
                max_size=DB_POOL_MAX_SIZE, 
                conninfo=DATABASE_URL,
                timeout=DB_COMMAND_TIMEOUT
            )
            logger.info(f"Database connection pool initialized: min={DB_POOL_MIN_SIZE}, max={DB_POOL_MAX_SIZE}")
            logger.info(f"استخر اتصالات پایگاه داده مقداردهی شد: کمینه={DB_POOL_MIN_SIZE}, بیشینه={DB_POOL_MAX_SIZE}")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            logger.error(f"خطا در مقداردهی استخر پایگاه داده: {e}")
            raise DatabaseError(f"Database initialization failed: {e}")

class DBManager:
    """
    مدیر پیشرفته پایگاه داده با قابلیت‌های کامل
    Advanced Database Manager with comprehensive functionality and Persian support
    """
    
    def __init__(self):
        self._pool = pool
        self._query_cache: Dict[str, Any] = {}
        self._cache_ttl = 300  # 5 minutes cache TTL
        
    async def ensure_pool(self) -> None:
        """اطمینان از وجود استخر اتصالات - Ensure connection pool exists"""
        if not self._pool:
            await initialize_pool()
            self._pool = pool
    
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
                logger.warning(f"خطای اتصال پایگاه داده، تلاش مجدد... ({retry_count + 1}/{DB_RETRY_ATTEMPTS})")
                await asyncio.sleep(1 * (retry_count + 1))  # Exponential backoff
                return await self.db(query, params, fetch, retry_count + 1)
            else:
                logger.error(f"Database connection failed after {DB_RETRY_ATTEMPTS} attempts")
                logger.error(f"اتصال پایگاه داده پس از {DB_RETRY_ATTEMPTS} تلاش ناموفق بود")
                raise DatabaseError(f"Database connection failed: {e}")
        except Exception as e:
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
        
        try:
            async with self._pool.connection() as conn:
                async with conn.transaction():
                    for query, params in queries:
                        await conn.execute(query, params)
            logger.info(f"Transaction completed successfully with {len(queries)} queries")
            logger.info(f"تراکنش با موفقیت با {len(queries)} کوئری کامل شد")
            return True
        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            logger.error(f"تراکنش ناموفق بود: {e}")
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
    
    async def update_user_activity(self, chat_id: int, user_id: int) -> bool:
        """به‌روزرسانی فعالیت کاربر - Update user activity"""
        try:
            current_time = int(time.time())
            result = await self.db(
                "UPDATE players SET last_active = %s WHERE chat_id = %s AND user_id = %s",
                (current_time, chat_id, user_id)
            )
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
        """دریافت سطح کاربر - Get user level"""
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
    
    async def set_cooldown(self, chat_id: int, user_id: int, action: str, 
                          duration: int, data: Optional[str] = None) -> bool:
        """تنظیم کولدان - Set cooldown for an action"""
        try:
            until_time = int(time.time()) + duration
            await self.db("""
                INSERT INTO cooldowns (chat_id, user_id, action, until, data)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (chat_id, user_id, action) 
                DO UPDATE SET until = EXCLUDED.until, data = EXCLUDED.data
            """, (chat_id, user_id, action, until_time, data))
            
            logger.info(f"Cooldown set for user {user_id}: {action} for {duration} seconds")
            logger.info(f"کولدان برای کاربر {user_id} تنظیم شد: {action} برای {duration} ثانیه")
            return True
        except Exception as e:
            logger.error(f"Error setting cooldown: {e}")
            return False
    
    async def get_cooldown(self, chat_id: int, user_id: int, action: str) -> Optional[int]:
        """دریافت زمان باقیمانده کولدان - Get remaining cooldown time"""
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
        """پاک کردن کولدان - Clear cooldown"""
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
        """پاک‌سازی کولدان‌های منقضی - Clean up expired cooldowns"""
        try:
            current_time = int(time.time())
            result = await self.db(
                "DELETE FROM cooldowns WHERE until < %s",
                (current_time,)
            )
            logger.info(f"Cleaned up expired cooldowns")
            logger.info(f"کولدان‌های منقضی پاک‌سازی شدند")
            return True
        except Exception as e:
            logger.error(f"Error cleaning up cooldowns: {e}")
            return False

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
                level INT DEFAULT 1,
                created_at BIGINT DEFAULT EXTRACT(EPOCH FROM NOW()),
                total_attacks INT DEFAULT 0,
                total_damage INT DEFAULT 0,
                times_attacked INT DEFAULT 0,
                damage_taken INT DEFAULT 0,
                preferred_weapon TEXT,
                settings JSONB DEFAULT '{}',
                PRIMARY KEY(chat_id, user_id),
                CONSTRAINT positive_hp CHECK (hp >= 0 AND hp <= 100),
                CONSTRAINT positive_level CHECK (level >= 1),
                CONSTRAINT positive_tg_stars CHECK (tg_stars >= 0)
            )
        """)
        logger.info("Players table created/verified - جدول بازیکنان ایجاد/تایید شد")
        
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
            "CREATE INDEX IF NOT EXISTS idx_defenses_expires ON active_defenses(chat_id, expires_at)"
        ]
        
        for index_query in indexes:
            await db_manager.db(index_query)
        
        logger.info("Database indexes created/verified - ایندکس‌های پایگاه داده ایجاد/تایید شدند")
        
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
    'validate_database_config',
    'db'  # Legacy support
]
