#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🛠️ TrumpBot Advanced Utilities & Helpers System | سیستم پیشرفته ابزارها و کمک‌کننده‌های ترامپ‌بات
==================================================================

🎯 Enterprise-Grade Helper System | سیستم کمک‌کننده سازمانی
• Advanced player management with AI-powered features
• Comprehensive game mechanics with intelligent algorithms  
• Smart message processing with context awareness
• Multi-language support with Persian cultural adaptation
• Performance optimization with caching and analytics
• Security features with validation and protection

مدیریت پیشرفته بازیکنان با ویژگی‌های مبتنی بر هوش مصنوعی •
مکانیک‌های جامع بازی با الگوریتم‌های هوشمند •
پردازش هوشمند پیام با آگاهی از بافت •
پشتیبانی چندزبانه با تطبیق فرهنگی فارسی •
بهینه‌سازی عملکرد با کشینگ و آنالیتیکس •
ویژگی‌های امنیتی با اعتبارسنجی و محافظت •

📚 Version: 2.0.0-Enterprise | نسخه: ۲.۰.۰-سازمانی
🔧 Enhanced: August 2025 | تقویت شده: اوت ۲۰۲۵
"""

import asyncio
import hashlib
import json
import math
import time
import logging
import re
import random
import statistics
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from functools import wraps, lru_cache
from typing import Optional, Dict, Any, List, Tuple, Set, Union, NamedTuple, Callable
import telebot
from telebot import types
from src.database.db_manager import DBManager
from src.utils.translations import T

# 🚀 Enhanced Logging Configuration | پیکربندی پیشرفته لاگ‌گیری
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 📊 Data Classes and Enums | کلاس‌ها و انواع داده

@dataclass
class PlayerStats:
    """Comprehensive player statistics | آمار جامع بازیکن"""
    user_id: int
    chat_id: int
    score: int = 0
    level: int = 1
    experience: int = 0
    attacks_made: int = 0
    attacks_received: int = 0
    victories: int = 0
    defeats: int = 0
    shields_used: int = 0
    items_bought: int = 0
    activity_points: int = 0
    last_active: int = 0
    join_date: int = 0
    language: str = "en"
    achievements: List[str] = field(default_factory=list)
    
    @property
    def win_rate(self) -> float:
        """Calculate win rate percentage"""
        total_battles = self.attacks_made + self.attacks_received
        return (self.victories / total_battles * 100) if total_battles > 0 else 0.0
    
    @property
    def activity_score(self) -> float:
        """Calculate activity score based on various factors"""
        days_since_join = max((time.time() - self.join_date) / 86400, 1)
        return (self.activity_points + self.attacks_made * 5) / days_since_join

@dataclass
class GameSession:
    """Game session tracking | ردیابی جلسه بازی"""
    chat_id: int
    session_id: str
    start_time: int
    active_players: Set[int] = field(default_factory=set)
    actions_count: int = 0
    language_distribution: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    
class ActionType(Enum):
    """Game action types | انواع اقدامات بازی"""
    ATTACK = auto()
    DEFEND = auto()
    SHOP = auto()
    STATUS = auto()
    HELP = auto()
    SOCIAL = auto()

class DifficultyLevel(Enum):
    """Game difficulty levels | سطوح دشواری بازی"""
    BEGINNER = "beginner"      # مبتدی
    INTERMEDIATE = "intermediate"  # متوسط
    ADVANCED = "advanced"      # پیشرفته
    EXPERT = "expert"         # خبره
    LEGENDARY = "legendary"   # افسانه‌ای

class CacheEntry(NamedTuple):
    """Cache entry structure | ساختار ورودی کش"""
    data: Any
    timestamp: float
    expires_at: float

# 🕒 Enhanced Time and Utility Functions | توابع پیشرفته زمان و کمکی

def now() -> int:
    """Get current Unix timestamp with validation | دریافت زمان یونیکس فعلی با اعتبارسنجی"""
    return int(time.time())

def format_time_persian(timestamp: int, lang: str = "en") -> str:
    """Format timestamp with Persian calendar support | فرمت زمان با پشتیبانی تقویم فارسی"""
    try:
        dt = datetime.fromtimestamp(timestamp)
        
        if lang == "fa":
            # Persian month names | نام‌های ماه‌های فارسی
            persian_months = [
                "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
                "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
            ]
            # Simplified Persian date formatting
            return f"{dt.day} {persian_months[dt.month-1]} {dt.year}"
        else:
            return dt.strftime("%B %d, %Y")
    except Exception as e:
        logger.error(f"Error formatting time: {e}")
        return "Unknown date"

def format_duration(seconds: int, lang: str = "en") -> str:
    """Format duration with bilingual support | فرمت مدت زمان با پشتیبانی دوزبانه"""
    try:
        if seconds <= 0:
            return T[lang].get('time_expired', {})
        
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if lang == "fa":
            parts = []
            if days > 0:
                parts.append(f"{days} روز")
            if hours > 0:
                parts.append(f"{hours} ساعت")
            if minutes > 0:
                parts.append(f"{minutes} دقیقه")
            if secs > 0 and not parts:  # Only show seconds if no larger units
                parts.append(f"{secs} ثانیه")
            return " و ".join(parts) if parts else "منقضی شده"
        else:
            parts = []
            if days > 0:
                parts.append(f"{days}d")
            if hours > 0:
                parts.append(f"{hours}h")
            if minutes > 0:
                parts.append(f"{minutes}m")
            if secs > 0 and not parts:
                parts.append(f"{secs}s")
            return " ".join(parts) if parts else "expired"
    except Exception as e:
        logger.error(f"Error formatting duration: {e}")
        return "Unknown"

def sanitize_text(text: str, max_length: int = 500) -> str:
    """Sanitize user input with security features | پاک‌سازی ورودی کاربر با ویژگی‌های امنیتی"""
    try:
        if not text:
            return ""
        
        # Remove potential injection patterns
        text = re.sub(r'[<>"\'\`]', '', text)
        
        # Limit length
        text = text[:max_length]
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        return text
    except Exception as e:
        logger.error(f"Error sanitizing text: {e}")
        return ""

# 💾 Advanced Caching System | سیستم پیشرفته کشینگ

class SmartCache:
    """Intelligent caching system with TTL and LRU | سیستم کشینگ هوشمند با TTL و LRU"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._access_order: List[str] = []
        self._stats = {"hits": 0, "misses": 0, "evictions": 0}
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value with expiration check"""
        current_time = time.time()
        
        if key in self._cache:
            entry = self._cache[key]
            if current_time <= entry.expires_at:
                # Move to end (most recently used)
                self._access_order.remove(key)
                self._access_order.append(key)
                self._stats["hits"] += 1
                return entry.data
            else:
                # Expired entry
                del self._cache[key]
                if key in self._access_order:
                    self._access_order.remove(key)
        
        self._stats["misses"] += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set cached value with TTL"""
        current_time = time.time()
        ttl = ttl or self.default_ttl
        
        # Remove old entry if exists
        if key in self._cache:
            self._access_order.remove(key)
        
        # Check size limit and evict if necessary
        while len(self._cache) >= self.max_size:
            oldest_key = self._access_order.pop(0)
            del self._cache[oldest_key]
            self._stats["evictions"] += 1
        
        # Add new entry
        self._cache[key] = CacheEntry(
            data=value,
            timestamp=current_time,
            expires_at=current_time + ttl
        )
        self._access_order.append(key)
    
    def clear(self) -> None:
        """Clear all cached entries"""
        self._cache.clear()
        self._access_order.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hit_rate": round(hit_rate, 2),
            "stats": self._stats.copy()
        }

# Global cache instance
smart_cache = SmartCache(max_size=2000, default_ttl=600)

class AdvancedPlayerManager:
    """🎮 Advanced player management with AI features | مدیریت پیشرفته بازیکن با ویژگی‌های هوش مصنوعی"""
    
    def __init__(self, db_manager: DBManager):
        self.db_manager = db_manager
        self._session_cache: Dict[int, GameSession] = {}
        self.achievement_tracker = AchievementTracker()
    
    async def ensure_group(self, chat_id: int, title: str, username: str) -> None:
        """Ensure a group exists with enhanced tracking | تضمین وجود گروه با ردیابی پیشرفته"""
        try:
            cache_key = f"group_{chat_id}"
            cached_group = smart_cache.get(cache_key)
            
            if not cached_group:
                await self.db_manager.db("""
                    INSERT INTO groups(chat_id, title, username, created_at, last_active, member_count, activity_score)
                    VALUES(%s, %s, %s, %s, %s, 0, 0.0)
                    ON CONFLICT(chat_id) DO UPDATE 
                      SET title      = EXCLUDED.title,
                          username   = EXCLUDED.username,
                          last_active= EXCLUDED.last_active
                """, (chat_id, title, username, now(), now()))
                
                # Cache group data
                smart_cache.set(cache_key, {"chat_id": chat_id, "title": title}, ttl=1800)
                
            # Update activity tracking
            await self._update_group_activity(chat_id)
            
        except Exception as e:
            logger.error(f"Error ensuring group {chat_id}: {e}")
    
    async def ensure_player(self, chat_id: int, user: telebot.types.User) -> PlayerStats:
        """Ensure player exists with comprehensive stats | تضمین وجود بازیکن با آمار جامع"""
        try:
            cache_key = f"player_{chat_id}_{user.id}"
            cached_player = smart_cache.get(cache_key)
            
            if cached_player:
                return cached_player
            
            username = sanitize_text(user.username or "")
            first_name = sanitize_text(user.first_name or "Unknown")
            
            # Advanced player insertion with full stats
            await self.db_manager.db("""
                INSERT INTO players(
                    chat_id, user_id, first_name, username, last_active, 
                    score, level, experience, join_date, language,
                    attacks_made, attacks_received, victories, defeats,
                    shields_used, items_bought, activity_points
                )
                VALUES(%s, %s, %s, %s, %s, 0, 1, 0, %s, 'en', 0, 0, 0, 0, 0, 0, 0)
                ON CONFLICT(chat_id, user_id) DO UPDATE 
                  SET first_name = EXCLUDED.first_name,
                      username   = EXCLUDED.username,
                      last_active= EXCLUDED.last_active
            """, (chat_id, user.id, first_name, username, now(), now()))
            
            # Create player stats object
            player_stats = await self._get_player_stats(chat_id, user.id)
            
            # Cache player data
            smart_cache.set(cache_key, player_stats, ttl=300)
            
            # Check for achievements
            await self.achievement_tracker.check_achievements(player_stats, self.db_manager)
            
            return player_stats
            
        except Exception as e:
            logger.error(f"Error ensuring player {user.id} in {chat_id}: {e}")
            return PlayerStats(user_id=user.id, chat_id=chat_id)
    
    async def _get_player_stats(self, chat_id: int, user_id: int) -> PlayerStats:
        """Get comprehensive player statistics | دریافت آمار جامع بازیکن"""
        try:
            result = await self.db_manager.db("""
                SELECT user_id, chat_id, score, level, experience, 
                       attacks_made, attacks_received, victories, defeats,
                       shields_used, items_bought, activity_points,
                       last_active, join_date, language
                FROM players 
                WHERE chat_id=%s AND user_id=%s
            """, (chat_id, user_id), fetch="one_dict")
            
            if result:
                # Get achievements
                achievements_result = await self.db_manager.db(
                    "SELECT achievement_id FROM player_achievements WHERE chat_id=%s AND user_id=%s",
                    (chat_id, user_id), fetch="all"
                )
                achievements = [row['achievement_id'] for row in achievements_result] if achievements_result else []
                
                return PlayerStats(
                    user_id=result['user_id'],
                    chat_id=result['chat_id'],
                    score=result['score'] or 0,
                    level=result['level'] or 1,
                    experience=result['experience'] or 0,
                    attacks_made=result['attacks_made'] or 0,
                    attacks_received=result['attacks_received'] or 0,
                    victories=result['victories'] or 0,
                    defeats=result['defeats'] or 0,
                    shields_used=result['shields_used'] or 0,
                    items_bought=result['items_bought'] or 0,
                    activity_points=result['activity_points'] or 0,
                    last_active=result['last_active'] or 0,
                    join_date=result['join_date'] or now(),
                    language=result['language'] or "en",
                    achievements=achievements
                )
            else:
                return PlayerStats(user_id=user_id, chat_id=chat_id)
                
        except Exception as e:
            logger.error(f"Error getting player stats: {e}")
            return PlayerStats(user_id=user_id, chat_id=chat_id)
    
    async def get_language(self, chat_id: int, user_id: int) -> str:
        """Get player language with intelligent detection | دریافت زبان بازیکن با تشخیص هوشمند"""
        try:
            cache_key = f"lang_{chat_id}_{user_id}"
            cached_lang = smart_cache.get(cache_key)
            
            if cached_lang:
                return cached_lang
            
            result = await self.db_manager.db(
                "SELECT language FROM players WHERE chat_id=%s AND user_id=%s",
                (chat_id, user_id), 
                fetch="one_dict"
            )
            
            language = result['language'] if result else "en"
            
            # Cache language
            smart_cache.set(cache_key, language, ttl=1800)
            
            return language
            
        except Exception as e:
            logger.error(f"Error getting language for {user_id}: {e}")
            return "en"
    
    async def set_language(self, chat_id: int, user_id: int, language: str) -> bool:
        """Set player language with validation | تنظیم زبان بازیکن با اعتبارسنجی"""
        try:
            # Validate language
            if language not in ["en", "fa"]:
                language = "en"
            
            await self.db_manager.db(
                "UPDATE players SET language=%s WHERE chat_id=%s AND user_id=%s",
                (language, chat_id, user_id)
            )
            
            # Update cache
            cache_key = f"lang_{chat_id}_{user_id}"
            smart_cache.set(cache_key, language, ttl=1800)
            
            logger.info(f"Language set to {language} for user {user_id} in {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting language for {user_id}: {e}")
            return False
    
    async def update_player_stats(self, chat_id: int, user_id: int, 
                                 stat_updates: Dict[str, Any]) -> bool:
        """Update player statistics with validation | به‌روزرسانی آمار بازیکن با اعتبارسنجی"""
        try:
            # Build dynamic update query
            update_fields = []
            values = []
            
            allowed_fields = {
                'score', 'level', 'experience', 'attacks_made', 'attacks_received',
                'victories', 'defeats', 'shields_used', 'items_bought', 
                'activity_points', 'last_active'
            }
            
            for field, value in stat_updates.items():
                if field in allowed_fields:
                    if field == 'last_active' and value is None:
                        value = now()
                    update_fields.append(f"{field} = %s")
                    values.append(value)
            
            if not update_fields:
                return False
            
            # Add WHERE clause values
            values.extend([chat_id, user_id])
            
            query = f"""
                UPDATE players 
                SET {', '.join(update_fields)}
                WHERE chat_id=%s AND user_id=%s
            """
            
            await self.db_manager.db(query, values)
            
            # Clear cache
            cache_key = f"player_{chat_id}_{user_id}"
            smart_cache.set(cache_key, None, ttl=0)  # Invalidate cache
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating player stats: {e}")
            return False
    
    async def get_medals(self, chat_id: int, user_id: int) -> int:
        """Get player medal count with caching | دریافت تعداد مدال بازیکن با کشینگ"""
        try:
            cache_key = f"medals_{chat_id}_{user_id}"
            cached_medals = smart_cache.get(cache_key)
            
            if cached_medals is not None:
                return cached_medals
            
            result = await self.db_manager.db(
                "SELECT score FROM players WHERE chat_id=%s AND user_id=%s",
                (chat_id, user_id), 
                fetch="one_dict"
            )
            
            medals = result['score'] if result else 0
            
            # Cache medals
            smart_cache.set(cache_key, medals, ttl=120)
            
            return medals
            
        except Exception as e:
            logger.error(f"Error getting medals for {user_id}: {e}")
            return 0
    
    async def add_medals(self, chat_id: int, user_id: int, amount: int, 
                        reason: str = "activity") -> bool:
        """Add medals with transaction logging | افزودن مدال با ثبت تراکنش"""
        try:
            if amount <= 0:
                return False
            
            # Update medals
            await self.db_manager.db(
                "UPDATE players SET score = score + %s, last_active = %s WHERE chat_id=%s AND user_id=%s",
                (amount, now(), chat_id, user_id)
            )
            
            # Log transaction
            await self._log_medal_transaction(chat_id, user_id, amount, reason)
            
            # Clear cache
            cache_key = f"medals_{chat_id}_{user_id}"
            smart_cache.set(cache_key, None, ttl=0)  # Invalidate
            
            # Check level progression
            await self._check_level_progression(chat_id, user_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding medals: {e}")
            return False
    
    async def _log_medal_transaction(self, chat_id: int, user_id: int, 
                                   amount: int, reason: str) -> None:
        """Log medal transaction for audit trail"""
        try:
            await self.db_manager.db("""
                INSERT INTO medal_transactions(chat_id, user_id, amount, reason, timestamp)
                VALUES(%s, %s, %s, %s, %s)
            """, (chat_id, user_id, amount, reason, now()))
        except Exception as e:
            logger.error(f"Error logging medal transaction: {e}")
    
    async def _check_level_progression(self, chat_id: int, user_id: int) -> None:
        """Check and handle level progression"""
        try:
            player_stats = await self._get_player_stats(chat_id, user_id)
            level_info = AdvancedGameMechanics.get_player_level_info(player_stats.score)
            
            if level_info['level'] > player_stats.level:
                # Level up!
                await self.update_player_stats(chat_id, user_id, {
                    'level': level_info['level']
                })
                
                # Award level up bonus
                bonus_medals = level_info['level'] * 10
                await self.add_medals(chat_id, user_id, bonus_medals, "level_up")
                
                logger.info(f"Player {user_id} leveled up to {level_info['level']}")
                
        except Exception as e:
            logger.error(f"Error checking level progression: {e}")
    
    async def _update_group_activity(self, chat_id: int) -> None:
        """Update group activity metrics"""
        try:
            await self.db_manager.db(
                "UPDATE groups SET last_active = %s WHERE chat_id = %s",
                (now(), chat_id)
            )
        except Exception as e:
            logger.error(f"Error updating group activity: {e}")
    
    async def get_top_players(self, chat_id: int, limit: int = 10, 
                            metric: str = "score") -> List[Dict[str, Any]]:
        """Get top players by various metrics | دریافت برترین بازیکنان بر اساس معیارهای مختلف"""
        try:
            allowed_metrics = ["score", "level", "activity_points", "victories", "win_rate"]
            if metric not in allowed_metrics:
                metric = "score"
            
            # Special handling for calculated metrics
            if metric == "win_rate":
                query = """
                    SELECT user_id, first_name, score, victories, defeats,
                           attacks_made, attacks_received,
                           CASE 
                               WHEN (attacks_made + attacks_received) > 0 
                               THEN (victories::float / (attacks_made + attacks_received)) * 100
                               ELSE 0 
                           END as win_rate
                    FROM players 
                    WHERE chat_id = %s AND (attacks_made + attacks_received) >= 5
                    ORDER BY win_rate DESC, score DESC
                    LIMIT %s
                """
            else:
                query = f"""
                    SELECT user_id, first_name, score, level, activity_points, 
                           victories, defeats, attacks_made, attacks_received
                    FROM players 
                    WHERE chat_id = %s 
                    ORDER BY {metric} DESC, score DESC
                    LIMIT %s
                """
            
            result = await self.db_manager.db(query, (chat_id, limit), fetch="all")
            
            if result:
                return [dict(row) for row in result]
            return []
            
        except Exception as e:
            logger.error(f"Error getting top players: {e}")
            return []

class AdvancedDefenseManager:
    """🛡️ Advanced defense and cooldown management | مدیریت پیشرفته دفاع و زمان انتظار"""
    
    def __init__(self, db_manager: DBManager):
        self.db_manager = db_manager
        self.defense_algorithms = DefenseAlgorithms()
    
    async def get_shield_remaining(self, chat_id: int, user_id: int) -> Dict[str, Any]:
        """Get comprehensive shield information | دریافت اطلاعات جامع سپر"""
        try:
            cache_key = f"shield_{chat_id}_{user_id}"
            cached_shield = smart_cache.get(cache_key)
            
            if cached_shield:
                return cached_shield
            
            result = await self.db_manager.db(
                "SELECT until, data FROM cooldowns WHERE chat_id=%s AND user_id=%s AND action='shield'",
                (chat_id, user_id), 
                fetch="one_dict"
            )
            
            current_time = now()
            shield_info = {
                "remaining_time": 0,
                "is_active": False,
                "strength": 0,
                "type": "none"
            }
            
            if result and result['until'] > current_time:
                remaining = result['until'] - current_time
                shield_data = json.loads(result['data'] or '{}')
                
                shield_info.update({
                    "remaining_time": remaining,
                    "is_active": True,
                    "strength": shield_data.get('strength', 100),
                    "type": shield_data.get('type', 'basic')
                })
            
            # Cache result
            smart_cache.set(cache_key, shield_info, ttl=60)
            
            return shield_info
            
        except Exception as e:
            logger.error(f"Error getting shield info: {e}")
            return {"remaining_time": 0, "is_active": False, "strength": 0, "type": "none"}
    
    async def activate_shield(self, chat_id: int, user_id: int, 
                            duration: int, shield_type: str = "basic", 
                            strength: int = 100) -> bool:
        """Activate advanced shield with customization | فعال‌سازی سپر پیشرفته با سفارشی‌سازی"""
        try:
            shield_data = {
                "type": shield_type,
                "strength": strength,
                "activated_at": now(),
                "activator_id": user_id
            }
            
            await self.update_cooldown(
                chat_id, user_id, "shield", duration, 
                json.dumps(shield_data)
            )
            
            # Log shield activation
            await self._log_defense_action(chat_id, user_id, "shield_activate", {
                "duration": duration,
                "type": shield_type,
                "strength": strength
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error activating shield: {e}")
            return False
    
    async def get_intercept_state(self, chat_id: int, user_id: int) -> Dict[str, Any]:
        """Get advanced intercept system state | دریافت وضعیت پیشرفته سیستم رهگیری"""
        try:
            result = await self.db_manager.db(
                "SELECT until, data FROM cooldowns WHERE chat_id=%s AND user_id=%s AND action='intercept'",
                (chat_id, user_id), 
                fetch="one_dict"
            )
            
            current_time = now()
            intercept_info = {
                "remaining_time": 0,
                "is_active": False,
                "bonus_percentage": 0,
                "accuracy": 0,
                "range": 0
            }
            
            if result and result['until'] > current_time:
                remaining = result['until'] - current_time
                intercept_data = json.loads(result['data'] or '{}')
                
                intercept_info.update({
                    "remaining_time": remaining,
                    "is_active": True,
                    "bonus_percentage": intercept_data.get('bonus', 20),
                    "accuracy": intercept_data.get('accuracy', 75),
                    "range": intercept_data.get('range', 100)
                })
            
            return intercept_info
            
        except Exception as e:
            logger.error(f"Error getting intercept state: {e}")
            return {"remaining_time": 0, "is_active": False, "bonus_percentage": 0}
    
    async def activate_intercept(self, chat_id: int, user_id: int, 
                               duration: int, bonus: int = 20, 
                               accuracy: int = 75) -> bool:
        """Activate advanced intercept system | فعال‌سازی سیستم پیشرفته رهگیری"""
        try:
            intercept_data = {
                "bonus": bonus,
                "accuracy": accuracy,
                "range": 100,
                "activated_at": now()
            }
            
            await self.update_cooldown(
                chat_id, user_id, "intercept", duration,
                json.dumps(intercept_data)
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error activating intercept: {e}")
            return False
    
    async def update_cooldown(self, chat_id: int, user_id: int, action: str, 
                            duration: int, data: Optional[str] = None) -> bool:
        """Enhanced cooldown management | مدیریت پیشرفته زمان انتظار"""
        try:
            until = now() + duration
            await self.db_manager.db("""
                INSERT INTO cooldowns(chat_id, user_id, action, until, data, created_at)
                VALUES(%s, %s, %s, %s, %s, %s)
                ON CONFLICT(chat_id, user_id, action) DO UPDATE 
                  SET until = EXCLUDED.until,
                      data  = EXCLUDED.data,
                      created_at = EXCLUDED.created_at
            """, (chat_id, user_id, action, until, data, now()))
            
            # Clear relevant caches
            cache_patterns = [f"shield_{chat_id}_{user_id}", f"intercept_{chat_id}_{user_id}"]
            for pattern in cache_patterns:
                smart_cache.set(pattern, None, ttl=0)  # Invalidate
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating cooldown: {e}")
            return False
    
    async def get_all_active_defenses(self, chat_id: int, user_id: int) -> Dict[str, Any]:
        """Get all active defensive measures | دریافت تمام اقدامات دفاعی فعال"""
        try:
            result = await self.db_manager.db(
                "SELECT action, until, data FROM cooldowns WHERE chat_id=%s AND user_id=%s AND until > %s",
                (chat_id, user_id, now()), 
                fetch="all"
            )
            
            defenses = {}
            
            if result:
                for row in result:
                    action = row['action']
                    remaining = row['until'] - now()
                    data = json.loads(row['data'] or '{}')
                    
                    defenses[action] = {
                        "remaining_time": remaining,
                        "data": data,
                        "expires_at": row['until']
                    }
            
            return defenses
            
        except Exception as e:
            logger.error(f"Error getting active defenses: {e}")
            return {}
    
    async def calculate_defense_effectiveness(self, chat_id: int, user_id: int, 
                                           attack_power: int) -> Dict[str, Any]:
        """Calculate comprehensive defense effectiveness | محاسبه اثربخشی جامع دفاع"""
        try:
            active_defenses = await self.get_all_active_defenses(chat_id, user_id)
            
            total_defense = 0
            defense_types = []
            
            # Calculate shield defense
            if 'shield' in active_defenses:
                shield_data = active_defenses['shield']['data']
                shield_strength = shield_data.get('strength', 100)
                shield_defense = min(shield_strength, attack_power * 0.8)  # Max 80% reduction
                total_defense += shield_defense
                defense_types.append('shield')
            
            # Calculate intercept defense
            if 'intercept' in active_defenses:
                intercept_data = active_defenses['intercept']['data']
                intercept_bonus = intercept_data.get('bonus', 20)
                intercept_defense = attack_power * (intercept_bonus / 100)
                total_defense += intercept_defense
                defense_types.append('intercept')
            
            # Apply diminishing returns for multiple defenses
            if len(defense_types) > 1:
                total_defense *= 0.85  # 15% reduction for stacking
            
            # Calculate final damage
            final_damage = max(0, attack_power - total_defense)
            damage_reduction = ((attack_power - final_damage) / attack_power * 100) if attack_power > 0 else 0
            
            return {
                "original_damage": attack_power,
                "defense_value": total_defense,
                "final_damage": round(final_damage),
                "damage_reduction_percent": round(damage_reduction, 1),
                "active_defenses": defense_types,
                "effectiveness_rating": self._calculate_effectiveness_rating(damage_reduction)
            }
            
        except Exception as e:
            logger.error(f"Error calculating defense effectiveness: {e}")
            return {
                "original_damage": attack_power,
                "final_damage": attack_power,
                "damage_reduction_percent": 0,
                "active_defenses": []
            }
    
    def _calculate_effectiveness_rating(self, reduction_percent: float) -> str:
        """Calculate defense effectiveness rating"""
        if reduction_percent >= 80:
            return "legendary"  # افسانه‌ای
        elif reduction_percent >= 60:
            return "excellent"  # عالی
        elif reduction_percent >= 40:
            return "good"      # خوب
        elif reduction_percent >= 20:
            return "average"   # متوسط
        else:
            return "poor"      # ضعیف
    
    async def _log_defense_action(self, chat_id: int, user_id: int, 
                                action: str, data: Dict[str, Any]) -> None:
        """Log defense actions for analytics"""
        try:
            await self.db_manager.db("""
                INSERT INTO defense_logs(chat_id, user_id, action, data, timestamp)
                VALUES(%s, %s, %s, %s, %s)
            """, (chat_id, user_id, action, json.dumps(data), now()))
        except Exception as e:
            logger.error(f"Error logging defense action: {e}")

class DefenseAlgorithms:
    """Advanced defense calculation algorithms | الگوریتم‌های پیشرفته محاسبه دفاع"""
    
    @staticmethod
    def calculate_optimal_defense(attack_pattern: List[int], 
                                available_defenses: Dict[str, int]) -> Dict[str, Any]:
        """Calculate optimal defense strategy based on attack patterns"""
        try:
            if not attack_pattern:
                return {"strategy": "none", "confidence": 0}
            
            # Analyze attack pattern
            avg_attack = statistics.mean(attack_pattern)
            max_attack = max(attack_pattern)
            attack_frequency = len(attack_pattern)
            
            # Determine best defense strategy
            if max_attack > avg_attack * 2:  # High variance attacks
                strategy = "reactive_shield"
                confidence = 0.8
            elif attack_frequency > 5:  # Frequent attacks
                strategy = "continuous_intercept"
                confidence = 0.7
            else:  # Balanced approach
                strategy = "adaptive_defense"
                confidence = 0.6
            
            return {
                "strategy": strategy,
                "confidence": confidence,
                "recommended_duration": min(300 + attack_frequency * 30, 1800),
                "analysis": {
                    "avg_attack": avg_attack,
                    "max_attack": max_attack,
                    "frequency": attack_frequency
                }
            }
            
        except Exception as e:
            logger.error(f"Error in defense algorithm: {e}")
            return {"strategy": "basic", "confidence": 0.5}

class AdvancedGameMechanics:
    """🎮 Advanced game mechanics with AI algorithms | مکانیک‌های پیشرفته بازی با الگوریتم‌های هوش مصنوعی"""
    
    @staticmethod
    def get_player_level_info(score: int) -> Dict[str, Any]:
        """Enhanced player level calculation with exponential progression | محاسبه پیشرفته سطح بازیکن با پیشرفت نمایی"""
        try:
            # Enhanced level thresholds with exponential growth
            level_thresholds = {
                1: 0, 2: 100, 3: 300, 4: 700, 5: 1500,
                6: 3000, 7: 6000, 8: 12000, 9: 24000, 10: 50000
            }
            
            level = 1
            for lvl in range(1, 11):
                if score >= level_thresholds.get(lvl, float('inf')):
                    level = lvl
                else:
                    break
            
            current_threshold = level_thresholds.get(level, 0)
            next_threshold = level_thresholds.get(level + 1, float('inf'))
            
            # Calculate progress with smooth curve
            if next_threshold == float('inf'):
                progress = 1.0
                next_level_score = score
            else:
                progress_score = score - current_threshold
                needed_score = next_threshold - current_threshold
                progress = min(max(progress_score / needed_score, 0), 1) if needed_score > 0 else 1
                next_level_score = next_threshold
            
            # Calculate additional metrics
            prestige_level = max(0, level - 10)
            skill_points = level * 2 + prestige_level * 5
            
            return {
                'level': level,
                'score': score,
                'next_level': min(level + 1, 10),
                'next_level_threshold': next_level_score,
                'current_level_threshold': current_threshold,
                'progress': progress,
                'progress_percentage': round(progress * 100, 1),
                'prestige_level': prestige_level,
                'skill_points': skill_points,
                'rank_title': AdvancedGameMechanics._get_rank_title(level, prestige_level)
            }
            
        except Exception as e:
            logger.error(f"Error calculating level info: {e}")
            return {'level': 1, 'score': score, 'progress': 0}
    
    @staticmethod
    def _get_rank_title(level: int, prestige: int) -> Dict[str, str]:
        """Get rank title in multiple languages"""
        rank_titles = {
            1: {"en": "Rookie", "fa": "تازه‌کار"},
            2: {"en": "Private", "fa": "سرباز"},
            3: {"en": "Corporal", "fa": "سرجوخه"},
            4: {"en": "Sergeant", "fa": "گروهبان"},
            5: {"en": "Lieutenant", "fa": "ستوان"},
            6: {"en": "Captain", "fa": "سروان"},
            7: {"en": "Major", "fa": "سرگرد"},
            8: {"en": "Colonel", "fa": "سرهنگ"},
            9: {"en": "General", "fa": "سرلشکر"},
            10: {"en": "Marshal", "fa": "فرمانده"}
        }
        
        base_title = rank_titles.get(min(level, 10), {"en": "Unknown", "fa": "نامشخص"})
        
        if prestige > 0:
            return {
                "en": f"Elite {base_title['en']} ★{prestige}",
                "fa": f"{base_title['fa']} نخبه ★{prestige}"
            }
        
        return base_title
    
    @staticmethod
    def calculate_activity_points(text_length: int, message_type: str = "text", 
                                has_media: bool = False) -> int:
        """Enhanced activity points calculation | محاسبه پیشرفته امتیاز فعالیت"""
        try:
            base_points = max(text_length // 15, 1)  # More generous base calculation
            
            # Message type multipliers
            type_multipliers = {
                "text": 1.0,
                "photo": 1.5,
                "video": 2.0,
                "document": 1.8,
                "voice": 2.2,
                "sticker": 0.8,
                "game": 3.0
            }
            
            multiplier = type_multipliers.get(message_type, 1.0)
            
            # Media bonus
            if has_media:
                multiplier *= 1.3
            
            # Quality bonus for longer messages
            if text_length > 100:
                multiplier *= 1.2
            elif text_length > 50:
                multiplier *= 1.1
            
            # Calculate final points with cap
            final_points = min(round(base_points * multiplier), 15)
            
            return max(final_points, 1)
            
        except Exception as e:
            logger.error(f"Error calculating activity points: {e}")
            return 1
    
    @staticmethod
    def contains_attack_keyword(text: str, lang: str = "auto") -> Dict[str, Any]:
        """Advanced attack keyword detection with confidence scoring | تشخیص پیشرفته کلیدواژه حمله با امتیازدهی اعتماد"""
        try:
            # Comprehensive attack keywords with weights
            attack_patterns = {
                "direct_attack": {
                    "en": [
                        (r'\b(attack|strike|hit|destroy|bomb|missile|nuke|eliminate)\b', 3),
                        (r'\b(fight|battle|war|combat|assault|raid)\b', 2),
                        (r'\b(shoot|fire|blast|explode|crush|smash)\b', 2)
                    ],
                    "fa": [
                        (r'\b(حمله|ضربه|تخریب|بمباران|موشک|نابودی)\b', 3),
                        (r'\b(جنگ|نبرد|مبارزه|حمله|یورش)\b', 2),
                        (r'\b(شلیک|انفجار|درهم‌کوبیدن|له کردن)\b', 2)
                    ]
                },
                "aggressive_intent": {
                    "en": [
                        (r'\b(kill|die|death|murder|slaughter)\b', 4),
                        (r'\b(revenge|payback|retaliation)\b', 3),
                        (r'\b(angry|mad|furious|rage)\b', 2)
                    ],
                    "fa": [
                        (r'\b(بکش|بمیر|قتل|کشتار)\b', 4),
                        (r'\b(انتقام|تلافی|انتقام‌جویی)\b', 3),
                        (r'\b(عصبانی|خشمگین|غضبناک)\b', 2)
                    ]
                }
            }
            
            # Auto-detect language if not specified
            if lang == "auto":
                # Simple Persian character detection
                persian_chars = re.findall(r'[\u0600-\u06FF]', text)
                lang = "fa" if len(persian_chars) > len(text) * 0.3 else "en"
            
            # Normalize text
            normalized_text = re.sub(r'[^\w\s\u0600-\u06FF]', '', text.lower())
            
            total_score = 0
            matched_patterns = []
            
            # Scan all patterns
            for category, patterns_dict in attack_patterns.items():
                if lang in patterns_dict:
                    for pattern, weight in patterns_dict[lang]:
                        matches = re.findall(pattern, normalized_text, re.IGNORECASE)
                        if matches:
                            score = len(matches) * weight
                            total_score += score
                            matched_patterns.append({
                                "category": category,
                                "pattern": pattern,
                                "matches": matches,
                                "score": score
                            })
            
            # Calculate confidence (0-100)
            confidence = min((total_score / 10) * 100, 100)
            
            return {
                "is_attack": total_score >= 3,
                "confidence": round(confidence, 1),
                "total_score": total_score,
                "language": lang,
                "matched_patterns": matched_patterns,
                "severity": AdvancedGameMechanics._get_severity_level(total_score)
            }
            
        except Exception as e:
            logger.error(f"Error detecting attack keywords: {e}")
            return {"is_attack": False, "confidence": 0, "total_score": 0}
    
    @staticmethod
    def _get_severity_level(score: int) -> str:
        """Determine attack severity level"""
        if score >= 10:
            return "critical"  # بحرانی
        elif score >= 6:
            return "high"      # بالا
        elif score >= 3:
            return "medium"    # متوسط
        else:
            return "low"       # پایین
    
    @staticmethod
    def calculate_battle_outcome(attacker_stats: PlayerStats, 
                               defender_stats: PlayerStats,
                               attack_power: int,
                               defense_info: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive battle outcome | محاسبه نتیجه جامع نبرد"""
        try:
            # Base damage calculation
            base_damage = attack_power
            
            # Attacker level bonus
            attacker_bonus = 1 + (attacker_stats.level - 1) * 0.1
            base_damage *= attacker_bonus
            
            # Defender level resistance
            defender_resistance = 1 + (defender_stats.level - 1) * 0.05
            base_damage /= defender_resistance
            
            # Apply defense calculations
            final_damage = defense_info.get('final_damage', base_damage)
            
            # Calculate experience and rewards
            exp_gain = max(1, round(final_damage / 10))
            medal_gain = max(1, round(final_damage / 5))
            
            # Determine battle result
            is_critical = random.random() < 0.15  # 15% critical chance
            if is_critical:
                final_damage *= 1.5
                exp_gain *= 2
                medal_gain *= 2
            
            # Battle success determination
            success_chance = 0.7  # Base 70% success rate
            if attacker_stats.level > defender_stats.level:
                success_chance += 0.1 * (attacker_stats.level - defender_stats.level)
            
            is_successful = random.random() < min(success_chance, 0.95)
            
            if not is_successful:
                final_damage *= 0.3  # Reduced damage on failure
                exp_gain *= 0.5
                medal_gain = 0
            
            return {
                "success": is_successful,
                "damage_dealt": round(final_damage),
                "is_critical": is_critical,
                "attacker_exp_gain": exp_gain,
                "attacker_medal_gain": medal_gain,
                "defender_medal_loss": max(0, medal_gain // 2),
                "battle_rating": AdvancedGameMechanics._calculate_battle_rating(
                    final_damage, is_critical, is_successful
                ),
                "defense_effectiveness": defense_info.get('damage_reduction_percent', 0)
            }
            
        except Exception as e:
            logger.error(f"Error calculating battle outcome: {e}")
            return {"success": False, "damage_dealt": 0}
    
    @staticmethod
    def _calculate_battle_rating(damage: float, is_critical: bool, is_successful: bool) -> str:
        """Calculate battle performance rating"""
        if not is_successful:
            return "failed"
        elif is_critical and damage > 50:
            return "legendary"
        elif damage > 40:
            return "excellent"
        elif damage > 25:
            return "good"
        else:
            return "average"
    
    @staticmethod
    def generate_battle_report(battle_outcome: Dict[str, Any], 
                             attacker_name: str, defender_name: str, 
                             lang: str = "en") -> str:
        """Generate detailed battle report | تولید گزارش جامع نبرد"""
        try:
            if lang == "fa":
                if battle_outcome["success"]:
                    if battle_outcome["is_critical"]:
                        base_msg = f"💥 {attacker_name} ضربه کاری به {defender_name} زد!\n"
                        base_msg += f"⚡ آسیب وارده: {battle_outcome['damage_dealt']} (ضربه بحرانی!)\n"
                    else:
                        base_msg = f"⚔️ {attacker_name} به {defender_name} حمله کرد!\n"
                        base_msg += f"💔 آسیب وارده: {battle_outcome['damage_dealt']}\n"
                    
                    base_msg += f"🏆 {attacker_name} {battle_outcome['attacker_medal_gain']} مدال کسب کرد\n"
                    
                    if battle_outcome.get('defense_effectiveness', 0) > 0:
                        base_msg += f"🛡️ دفاع {defender_name}: {battle_outcome['defense_effectiveness']}% کاهش آسیب\n"
                        
                else:
                    base_msg = f"🛡️ {defender_name} حمله {attacker_name} را دفع کرد!\n"
                    base_msg += f"💫 آسیب کم: {battle_outcome['damage_dealt']}\n"
            else:
                if battle_outcome["success"]:
                    if battle_outcome["is_critical"]:
                        base_msg = f"💥 {attacker_name} delivered a critical strike to {defender_name}!\n"
                        base_msg += f"⚡ Damage dealt: {battle_outcome['damage_dealt']} (Critical Hit!)\n"
                    else:
                        base_msg = f"⚔️ {attacker_name} attacked {defender_name}!\n"
                        base_msg += f"💔 Damage dealt: {battle_outcome['damage_dealt']}\n"
                    
                    base_msg += f"🏆 {attacker_name} gained {battle_outcome['attacker_medal_gain']} medals\n"
                    
                    if battle_outcome.get('defense_effectiveness', 0) > 0:
                        base_msg += f"🛡️ {defender_name}'s defense: {battle_outcome['defense_effectiveness']}% damage reduction\n"
                        
                else:
                    base_msg = f"🛡️ {defender_name} successfully defended against {attacker_name}'s attack!\n"
                    base_msg += f"💫 Reduced damage: {battle_outcome['damage_dealt']}\n"
            
            return base_msg
            
        except Exception as e:
            logger.error(f"Error generating battle report: {e}")
            return "Battle completed."

class AchievementTracker:
    """🏆 Advanced achievement tracking system | سیستم پیشرفته ردیابی دستاوردها"""
    
    def __init__(self):
        self.achievement_definitions = self._load_achievement_definitions()
    
    def _load_achievement_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Load achievement definitions with bilingual support"""
        return {
            "first_victory": {
                "name": {"en": "First Blood", "fa": "اولین پیروزی"},
                "description": {"en": "Win your first battle", "fa": "اولین نبرد خود را ببرید"},
                "icon": "🥇",
                "condition": lambda stats: stats.victories >= 1,
                "reward_medals": 50
            },
            "level_5": {
                "name": {"en": "Rising Star", "fa": "ستاره در حال طلوع"},
                "description": {"en": "Reach level 5", "fa": "به سطح ۵ برسید"},
                "icon": "⭐",
                "condition": lambda stats: stats.level >= 5,
                "reward_medals": 100
            },
            "hundred_attacks": {
                "name": {"en": "Warrior", "fa": "جنگجو"},
                "description": {"en": "Make 100 attacks", "fa": "۱۰۰ حمله انجام دهید"},
                "icon": "⚔️",
                "condition": lambda stats: stats.attacks_made >= 100,
                "reward_medals": 200
            },
            "win_streak": {
                "name": {"en": "Unstoppable", "fa": "متوقف‌نشدنی"},
                "description": {"en": "Win 10 battles in a row", "fa": "۱۰ نبرد پشت سر هم ببرید"},
                "icon": "🔥",
                "condition": lambda stats: stats.victories >= 10 and stats.win_rate > 80,
                "reward_medals": 300
            },
            "shield_master": {
                "name": {"en": "Shield Master", "fa": "استاد سپر"},
                "description": {"en": "Use shields 50 times", "fa": "۵۰ بار از سپر استفاده کنید"},
                "icon": "🛡️",
                "condition": lambda stats: stats.shields_used >= 50,
                "reward_medals": 150
            }
        }
    
    async def check_achievements(self, player_stats: PlayerStats, 
                               db_manager: DBManager) -> List[Dict[str, Any]]:
        """Check and award new achievements | بررسی و اعطای دستاوردهای جدید"""
        try:
            new_achievements = []
            
            for achievement_id, achievement in self.achievement_definitions.items():
                # Check if player already has this achievement
                existing = await db_manager.db("""
                    SELECT 1 FROM player_achievements 
                    WHERE chat_id=%s AND user_id=%s AND achievement_id=%s
                """, (player_stats.chat_id, player_stats.user_id, achievement_id), fetch="one")
                
                if not existing and achievement["condition"](player_stats):
                    # Award achievement
                    await db_manager.db("""
                        INSERT INTO player_achievements(chat_id, user_id, achievement_id, earned_at)
                        VALUES(%s, %s, %s, %s)
                    """, (player_stats.chat_id, player_stats.user_id, achievement_id, now()))
                    
                    # Award medals
                    await db_manager.db("""
                        UPDATE players SET score = score + %s 
                        WHERE chat_id=%s AND user_id=%s
                    """, (achievement["reward_medals"], player_stats.chat_id, player_stats.user_id))
                    
                    new_achievements.append({
                        "id": achievement_id,
                        "name": achievement["name"],
                        "description": achievement["description"],
                        "icon": achievement["icon"],
                        "reward_medals": achievement["reward_medals"]
                    })
            
            return new_achievements
            
        except Exception as e:
            logger.error(f"Error checking achievements: {e}")
            return []

class AdvancedMessageUtils:
    """🔧 Advanced message processing utilities | ابزارهای پیشرفته پردازش پیام"""
    
    @staticmethod
    def get_args(message: telebot.types.Message) -> List[str]:
        """Extract command arguments with enhanced parsing | استخراج آرگومان‌های دستور با تحلیل پیشرفته"""
        try:
            if not message.text:
                return []
            
            # Advanced argument parsing with quote handling
            text = message.text.strip()
            parts = []
            current_arg = ""
            in_quotes = False
            quote_char = None
            
            i = 0
            while i < len(text):
                char = text[i]
                
                if char in ['"', "'"] and not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char and in_quotes:
                    in_quotes = False
                    quote_char = None
                elif char == ' ' and not in_quotes:
                    if current_arg:
                        parts.append(current_arg)
                        current_arg = ""
                else:
                    current_arg += char
                
                i += 1
            
            if current_arg:
                parts.append(current_arg)
            
            # Return arguments excluding the command itself
            return parts[1:] if len(parts) > 1 else []
            
        except Exception as e:
            logger.error(f"Error parsing message arguments: {e}")
            return []
    
    @staticmethod
    def get_weapon_display_name(weapon_type: str, lang: str) -> str:
        """Get localized weapon display name | دریافت نام نمایشی سلاح به زبان محلی"""
        try:
            weapon_names = {
                "pistol": {"en": "Pistol", "fa": "تپانچه"},
                "rifle": {"en": "Rifle", "fa": "تفنگ"},
                "sniper": {"en": "Sniper Rifle", "fa": "تفنگ تک‌تیرانداز"},
                "shotgun": {"en": "Shotgun", "fa": "ساچمه‌ای"},
                "machine_gun": {"en": "Machine Gun", "fa": "مسلسل"},
                "grenade": {"en": "Grenade", "fa": "نارنجک"},
                "rocket": {"en": "Rocket Launcher", "fa": "راکت انداز"},
                "bomb": {"en": "Bomb", "fa": "بمب"},
                "missile": {"en": "Missile", "fa": "موشک"},
                "nuke": {"en": "Nuclear Weapon", "fa": "سلاح هسته‌ای"}
            }
            
            return weapon_names.get(weapon_type, {}).get(lang, weapon_type.title())
            
        except Exception as e:
            logger.error(f"Error getting weapon name: {e}")
            return weapon_type
    
    @staticmethod
    def get_weapon_emoji(weapon_type: str) -> str:
        """Get appropriate emoji for weapon type | دریافت ایموجی مناسب برای نوع سلاح"""
        weapon_emojis = {
            "pistol": "🔫",
            "rifle": "🔫",
            "sniper": "🎯",
            "shotgun": "💥",
            "machine_gun": "⚡",
            "grenade": "💣",
            "rocket": "🚀",
            "bomb": "💣",
            "missile": "🚀",
            "nuke": "☢️",
            "knife": "🗡️",
            "sword": "⚔️"
        }
        
        return weapon_emojis.get(weapon_type, "🔫")
    
    @staticmethod
    def format_number(number: Union[int, float], lang: str = "en") -> str:
        """Format numbers with locale support | فرمت اعداد با پشتیبانی زبان محلی"""
        try:
            if lang == "fa":
                # Persian digit conversion
                persian_digits = "۰۱۲۳۴۵۶۷۸۹"
                english_digits = "0123456789"
                
                formatted = f"{number:,}"
                
                # Convert to Persian digits
                for eng, per in zip(english_digits, persian_digits):
                    formatted = formatted.replace(eng, per)
                
                return formatted
            else:
                return f"{number:,}"
                
        except Exception as e:
            logger.error(f"Error formatting number: {e}")
            return str(number)
    
    @staticmethod
    def create_progress_bar(current: int, maximum: int, length: int = 10, 
                          style: str = "default") -> str:
        """Create visual progress bar | ایجاد نوار پیشرفت بصری"""
        try:
            if maximum <= 0:
                return "█" * length
            
            progress = min(current / maximum, 1.0)
            filled_length = round(length * progress)
            
            if style == "persian":
                filled_char = "█"
                empty_char = "░"
            elif style == "arrows":
                filled_char = "▶"
                empty_char = "▷"
            else:  # default
                filled_char = "█"
                empty_char = "▓"
            
            bar = filled_char * filled_length + empty_char * (length - filled_length)
            percentage = round(progress * 100, 1)
            
            return f"{bar} {percentage}%"
            
        except Exception as e:
            logger.error(f"Error creating progress bar: {e}")
            return "Error"
    
    @staticmethod
    def extract_mentions(message: telebot.types.Message) -> List[Dict[str, Any]]:
        """Extract user mentions with comprehensive info | استخراج اشاره‌ها با اطلاعات جامع"""
        try:
            mentions = []
            
            if message.entities:
                for entity in message.entities:
                    if entity.type == "mention":
                        username = message.text[entity.offset:entity.offset + entity.length]
                        mentions.append({
                            "type": "username",
                            "value": username,
                            "offset": entity.offset,
                            "length": entity.length
                        })
                    elif entity.type == "text_mention":
                        mentions.append({
                            "type": "user_id",
                            "value": entity.user.id,
                            "user": entity.user,
                            "offset": entity.offset,
                            "length": entity.length
                        })
            
            return mentions
            
        except Exception as e:
            logger.error(f"Error extracting mentions: {e}")
            return []
    
    @staticmethod
    def detect_language(text: str) -> str:
        """Simple language detection | تشخیص ساده زبان"""
        try:
            # Count Persian characters
            persian_chars = len(re.findall(r'[\u0600-\u06FF]', text))
            latin_chars = len(re.findall(r'[a-zA-Z]', text))
            
            if persian_chars > latin_chars:
                return "fa"
            else:
                return "en"
                
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            return "en"
    
    @staticmethod
    def create_smart_keyboard(context: Dict[str, Any], lang: str = "en") -> types.InlineKeyboardMarkup:
        """Create context-aware keyboard | ایجاد کیبورد آگاه از بافت"""
        try:
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            
            # Determine context-appropriate buttons
            user_level = context.get('user_level', 1)
            user_medals = context.get('user_medals', 0)
            
            if lang == "fa":
                buttons = [
                    types.InlineKeyboardButton("🎮 شروع بازی", callback_data="game:start"),
                    types.InlineKeyboardButton("📊 آمار من", callback_data="stats:me"),
                    types.InlineKeyboardButton("🏆 رتبه‌بندی", callback_data="stats:leaderboard"),
                    types.InlineKeyboardButton("🛒 فروشگاه", callback_data="shop:main")
                ]
                
                if user_level >= 3:
                    buttons.extend([
                        types.InlineKeyboardButton("⚔️ حمله", callback_data="attack:menu"),
                        types.InlineKeyboardButton("🛡️ دفاع", callback_data="defense:menu")
                    ])
                
                if user_medals >= 100:
                    buttons.append(
                        types.InlineKeyboardButton("🎯 مأموریت‌ها", callback_data="missions:list")
                    )
            else:
                buttons = [
                    types.InlineKeyboardButton("🎮 Start Game", callback_data="game:start"),
                    types.InlineKeyboardButton("📊 My Stats", callback_data="stats:me"),
                    types.InlineKeyboardButton("🏆 Leaderboard", callback_data="stats:leaderboard"),
                    types.InlineKeyboardButton("🛒 Shop", callback_data="shop:main")
                ]
                
                if user_level >= 3:
                    buttons.extend([
                        types.InlineKeyboardButton("⚔️ Attack", callback_data="attack:menu"),
                        types.InlineKeyboardButton("🛡️ Defense", callback_data="defense:menu")
                    ])
                
                if user_medals >= 100:
                    buttons.append(
                        types.InlineKeyboardButton("🎯 Missions", callback_data="missions:list")
                    )
            
            # Add buttons in rows
            for i in range(0, len(buttons), 2):
                if i + 1 < len(buttons):
                    keyboard.add(buttons[i], buttons[i + 1])
                else:
                    keyboard.add(buttons[i])
            
            return keyboard
            
        except Exception as e:
            logger.error(f"Error creating smart keyboard: {e}")
            return types.InlineKeyboardMarkup()

class PerformanceMonitor:
    """📈 Performance monitoring and analytics | نظارت و آنالیتیکس عملکرد"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.start_time = time.time()
    
    def track_execution_time(self, function_name: str):
        """Decorator for tracking function execution time"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start = time.time()
                try:
                    result = await func(*args, **kwargs)
                    execution_time = time.time() - start
                    self.metrics[function_name].append(execution_time)
                    
                    # Keep only recent 100 measurements
                    if len(self.metrics[function_name]) > 100:
                        self.metrics[function_name] = self.metrics[function_name][-100:]
                    
                    return result
                except Exception as e:
                    execution_time = time.time() - start
                    logger.error(f"Function {function_name} failed after {execution_time:.3f}s: {e}")
                    raise
            return wrapper
        return decorator
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        stats = {}
        
        for function_name, times in self.metrics.items():
            if times:
                stats[function_name] = {
                    "calls": len(times),
                    "avg_time": statistics.mean(times),
                    "min_time": min(times),
                    "max_time": max(times),
                    "total_time": sum(times)
                }
        
        # Global stats
        uptime = time.time() - self.start_time
        total_calls = sum(len(times) for times in self.metrics.values())
        
        stats["_global"] = {
            "uptime_seconds": uptime,
            "total_function_calls": total_calls,
            "cache_stats": smart_cache.get_stats()
        }
        
        return stats

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

# 🔄 Enhanced Legacy Function Wrappers | بسته‌بندی توابع قدیمی پیشرفته
# Maintaining backward compatibility while providing enhanced functionality
# حفظ سازگاری با نسخه‌های قبلی در عین ارائه عملکرد پیشرفته

# Initialize global manager instances
_player_manager = None
_defense_manager = None

def _get_player_manager(db_manager: DBManager) -> AdvancedPlayerManager:
    """Get or create player manager instance"""
    global _player_manager
    if _player_manager is None or _player_manager.db_manager != db_manager:
        _player_manager = AdvancedPlayerManager(db_manager)
    return _player_manager

def _get_defense_manager(db_manager: DBManager) -> AdvancedDefenseManager:
    """Get or create defense manager instance"""
    global _defense_manager
    if _defense_manager is None or _defense_manager.db_manager != db_manager:
        _defense_manager = AdvancedDefenseManager(db_manager)
    return _defense_manager

@performance_monitor.track_execution_time("ensure_group")
async def ensure_group(chat_id: int, title: str, username: str, db_manager: DBManager) -> None:
    """Enhanced legacy wrapper for ensure_group | بسته‌بندی پیشرفته برای تضمین گروه"""
    manager = _get_player_manager(db_manager)
    await manager.ensure_group(chat_id, sanitize_text(title), sanitize_text(username))

@performance_monitor.track_execution_time("ensure_player")
async def ensure_player(chat_id: int, user: telebot.types.User, db_manager: DBManager) -> PlayerStats:
    """Enhanced legacy wrapper for ensure_player | بسته‌بندی پیشرفته برای تضمین بازیکن"""
    manager = _get_player_manager(db_manager)
    return await manager.ensure_player(chat_id, user)

@performance_monitor.track_execution_time("get_lang")
async def get_lang(chat_id: int, user_id: int, db_manager: DBManager) -> str:
    """Enhanced legacy wrapper for get_language | بسته‌بندی پیشرفته برای دریافت زبان"""
    manager = _get_player_manager(db_manager)
    return await manager.get_language(chat_id, user_id)

@performance_monitor.track_execution_time("set_lang")
async def set_lang(chat_id: int, user_id: int, lang: str, db_manager: DBManager) -> bool:
    """Enhanced legacy wrapper for set_language | بسته‌بندی پیشرفته برای تنظیم زبان"""
    manager = _get_player_manager(db_manager)
    return await manager.set_language(chat_id, user_id, lang)

@performance_monitor.track_execution_time("medals")
async def medals(user_id: int, chat_id: int, db_manager: DBManager) -> int:
    """Enhanced legacy wrapper for get_medals | بسته‌بندی پیشرفته برای دریافت مدال‌ها"""
    manager = _get_player_manager(db_manager)
    return await manager.get_medals(chat_id, user_id)

@performance_monitor.track_execution_time("add_medals")
async def add_medals(chat_id: int, user_id: int, amount: int, db_manager: DBManager, 
                    reason: str = "activity") -> bool:
    """Enhanced legacy wrapper for add_medals | بسته‌بندی پیشرفته برای افزودن مدال‌ها"""
    manager = _get_player_manager(db_manager)
    return await manager.add_medals(chat_id, user_id, amount, reason)

@performance_monitor.track_execution_time("shield_rem")
async def shield_rem(chat_id: int, user_id: int, db_manager: DBManager) -> int:
    """Enhanced legacy wrapper for get_shield_remaining | بسته‌بندی پیشرفته برای زمان باقی‌مانده سپر"""
    manager = _get_defense_manager(db_manager)
    shield_info = await manager.get_shield_remaining(chat_id, user_id)
    return shield_info.get("remaining_time", 0)

@performance_monitor.track_execution_time("intercept_state")
async def intercept_state(chat_id: int, user_id: int, db_manager: DBManager) -> Tuple[int, int]:
    """Enhanced legacy wrapper for get_intercept_state | بسته‌بندی پیشرفته برای وضعیت رهگیری"""
    manager = _get_defense_manager(db_manager)
    intercept_info = await manager.get_intercept_state(chat_id, user_id)
    return (intercept_info.get("remaining_time", 0), intercept_info.get("bonus_percentage", 0))

@performance_monitor.track_execution_time("update_cooldown")
async def update_cooldown(chat_id: int, user_id: int, action: str, duration: int, 
                         db_manager: DBManager, data: Optional[str] = None) -> bool:
    """Enhanced legacy wrapper for update_cooldown | بسته‌بندی پیشرفته برای به‌روزرسانی زمان انتظار"""
    manager = _get_defense_manager(db_manager)
    return await manager.update_cooldown(chat_id, user_id, action, duration, data)

def get_args(message: telebot.types.Message) -> List[str]:
    """Enhanced legacy wrapper for get_args | بسته‌بندی پیشرفته برای دریافت آرگومان‌ها"""
    return AdvancedMessageUtils.get_args(message)

def contains_attack_keyword(text: str, lang: str = "auto") -> bool:
    """Enhanced legacy wrapper for contains_attack_keyword | بسته‌بندی پیشرفته برای تشخیص کلیدواژه حمله"""
    result = AdvancedGameMechanics.contains_attack_keyword(text, lang)
    return result.get("is_attack", False)

def get_weapon_display_name(weapon_type: str, lang: str) -> str:
    """Enhanced legacy wrapper for get_weapon_display_name | بسته‌بندی پیشرفته برای نام سلاح"""
    return AdvancedMessageUtils.get_weapon_display_name(weapon_type, lang)

def get_weapon_emoji(weapon_type: str) -> str:
    """Enhanced legacy wrapper for get_weapon_emoji | بسته‌بندی پیشرفته برای ایموجی سلاح"""
    return AdvancedMessageUtils.get_weapon_emoji(weapon_type)

@performance_monitor.track_execution_time("get_player_level_info")
async def get_player_level_info(chat_id: int, user_id: int, db_manager: DBManager) -> Dict[str, Any]:
    """Enhanced player level information | اطلاعات پیشرفته سطح بازیکن"""
    manager = _get_player_manager(db_manager)
    score = await manager.get_medals(chat_id, user_id)
    return AdvancedGameMechanics.get_player_level_info(score)

@performance_monitor.track_execution_time("handle_regular_messages")
async def handle_regular_messages(message: telebot.types.Message, bot: telebot.async_telebot.AsyncTeleBot, 
                                is_mentioned: bool, db_manager: DBManager) -> Optional[str]:
    """Enhanced regular message handling | مدیریت پیشرفته پیام‌های معمولی"""
    try:
        if message.content_type != 'text' or message.chat.type not in ['group', 'supergroup']:
            return None
        
        manager = _get_player_manager(db_manager)
        player_stats = await manager.ensure_player(message.chat.id, message.from_user)
        lang = player_stats.language
        
        # Enhanced activity point calculation
        activity_points = AdvancedGameMechanics.calculate_activity_points(
            len(message.text), 
            message.content_type,
            bool(message.photo or message.video or message.document)
        )
        
        # Update activity with enhanced tracking
        await manager.update_player_stats(message.chat.id, message.from_user.id, {
            'activity_points': player_stats.activity_points + activity_points,
            'last_active': now()
        })
        
        # Enhanced mention handling
        if is_mentioned:
            responses_key = f'enhanced_mentioned_responses.{lang}'
            responses = T[lang].get('enhanced_mentioned_responses', {})
            return random.choice(responses).format(first_name=message.from_user.first_name or "User")
        
        # Enhanced attack keyword detection
        attack_analysis = AdvancedGameMechanics.contains_attack_keyword(message.text, lang)
        if attack_analysis["is_attack"] and attack_analysis["confidence"] > 60:
            if random.random() < (attack_analysis["confidence"] / 200):  # Probability based on confidence
                severity = attack_analysis["severity"]
                
                if lang == "fa":
                    responses = {
                        "low": ["آماده نبرد! ⚔️", "بزن بریم! 💪"],
                        "medium": ["این که جدی شد! 🔥", "حالا که حرف از جنگ میزنی... 😈"],
                        "high": ["واقعاً می‌خوای جنگ؟ 💀", "آماده نابودی؟ 💣"],
                        "critical": ["این جنگ تمام عیار میشه! ☢️", "زمان نهایی فرا رسیده! 🔥💀"]
                    }
                else:
                    responses = {
                        "low": ["Ready for battle! ⚔️", "Let's go! 💪"],
                        "medium": ["Now this is serious! 🔥", "So you want to fight... 😈"],
                        "high": ["You really want war? 💀", "Ready for destruction? 💣"],
                        "critical": ["This will be total war! ☢️", "The final hour has come! 🔥💀"]
                    }
                
                response_list = responses.get(severity, responses["low"])
                return random.choice(response_list)
        
        # Random engagement (reduced frequency for enhanced quality)
        if random.random() < 0.03:  # 3% chance for quality over quantity
            engagement_responses = T[lang].get('random_engagement', {})
            return random.choice(engagement_responses)
        
        return None
        
    except Exception as e:
        logger.error(f"Error in enhanced regular message handling: {e}")
        return None

def ensure_group_command(bot: telebot.async_telebot.AsyncTeleBot, db_manager: DBManager):
    """Enhanced decorator ensuring command is executed in group chat | دکوراتور پیشرفته تضمین اجرا در گروه"""
    def decorator(func):
        @wraps(func)
        @performance_monitor.track_execution_time(f"group_command_{func.__name__}")
        async def wrapper(message: telebot.types.Message):
            try:
                if message.chat.type == 'private':
                    manager = _get_player_manager(db_manager)
                    player_stats = await manager.ensure_player(message.chat.id, message.from_user)
                    lang = player_stats.language
                    
                    error_messages = {
                        "en": "🚫 This command can only be used in groups.\n\n💡 Add me to a group and try again!",
                        "fa": "🚫 این دستور فقط در گروه‌ها قابل استفاده است.\n\n💡 من را به گروه اضافه کنید و دوباره امتحان کنید!"
                    }
                    
                    error_msg = error_messages.get(lang, error_messages["en"])
                    
                    # Create helpful keyboard
                    keyboard = types.InlineKeyboardMarkup()
                    if lang == "fa":
                        keyboard.add(
                            types.InlineKeyboardButton("📚 راهنما", callback_data="help:main"),
                            types.InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings:main")
                        )
                    else:
                        keyboard.add(
                            types.InlineKeyboardButton("📚 Help", callback_data="help:main"),
                            types.InlineKeyboardButton("⚙️ Settings", callback_data="settings:main")
                        )
                    
                    await bot.send_message(message.chat.id, error_msg, reply_markup=keyboard)
                    return
                
                return await func(message)
                
            except Exception as e:
                logger.error(f"Error in enhanced group command wrapper: {e}")
                error_msg = "An error occurred processing your command. Please try again later."
                await bot.send_message(message.chat.id, error_msg)
        return wrapper
    return decorator

# 🚀 Advanced Helper Functions | توابع کمکی پیشرفته

async def get_comprehensive_player_info(chat_id: int, user_id: int, 
                                      db_manager: DBManager) -> Dict[str, Any]:
    """Get comprehensive player information | دریافت اطلاعات جامع بازیکن"""
    try:
        manager = _get_player_manager(db_manager)
        defense_manager = _get_defense_manager(db_manager)
        
        # Get basic player stats
        player_stats = await manager._get_player_stats(chat_id, user_id)
        
        # Get level information
        level_info = AdvancedGameMechanics.get_player_level_info(player_stats.score)
        
        # Get active defenses
        active_defenses = await defense_manager.get_all_active_defenses(chat_id, user_id)
        
        # Get recent achievements
        achievements = await manager.achievement_tracker.check_achievements(player_stats, db_manager)
        
        return {
            "basic_stats": player_stats,
            "level_info": level_info,
            "active_defenses": active_defenses,
            "recent_achievements": achievements,
            "performance_rating": _calculate_performance_rating(player_stats),
            "next_milestone": _get_next_milestone(player_stats)
        }
        
    except Exception as e:
        logger.error(f"Error getting comprehensive player info: {e}")
        return {}

def _calculate_performance_rating(stats: PlayerStats) -> Dict[str, Any]:
    """Calculate player performance rating"""
    try:
        # Calculate various performance metrics
        efficiency = stats.victories / max(stats.attacks_made, 1) * 100
        activity_rating = min(stats.activity_points / 100, 10)  # Scale to 0-10
        level_progress = stats.level * 20  # Each level worth 20 points
        
        # Overall rating (0-100)
        overall = (efficiency * 0.4 + activity_rating * 10 * 0.3 + level_progress * 0.3)
        overall = min(overall, 100)
        
        # Determine rating tier
        if overall >= 80:
            tier = {"en": "Elite", "fa": "نخبه"}
        elif overall >= 60:
            tier = {"en": "Expert", "fa": "خبره"}
        elif overall >= 40:
            tier = {"en": "Advanced", "fa": "پیشرفته"}
        elif overall >= 20:
            tier = {"en": "Intermediate", "fa": "متوسط"}
        else:
            tier = {"en": "Beginner", "fa": "مبتدی"}
        
        return {
            "overall_score": round(overall, 1),
            "tier": tier,
            "efficiency": round(efficiency, 1),
            "activity_rating": round(activity_rating, 1),
            "level_contribution": round(level_progress, 1)
        }
        
    except Exception as e:
        logger.error(f"Error calculating performance rating: {e}")
        return {"overall_score": 0, "tier": {"en": "Unknown", "fa": "نامشخص"}}

def _get_next_milestone(stats: PlayerStats) -> Dict[str, Any]:
    """Get next achievement milestone"""
    milestones = [
        {"type": "level", "target": 5, "current": stats.level},
        {"type": "score", "target": 1000, "current": stats.score},
        {"type": "victories", "target": 50, "current": stats.victories},
        {"type": "attacks", "target": 100, "current": stats.attacks_made}
    ]
    
    # Find next achievable milestone
    for milestone in milestones:
        if milestone["current"] < milestone["target"]:
            progress = milestone["current"] / milestone["target"] * 100
            return {
                "type": milestone["type"],
                "target": milestone["target"],
                "current": milestone["current"],
                "progress": round(progress, 1),
                "remaining": milestone["target"] - milestone["current"]
            }
    
    return {"type": "none", "message": "All basic milestones achieved!"}

# 📊 Enhanced Analytics Functions | توابع آنالیتیکس پیشرفته

async def get_group_analytics(chat_id: int, db_manager: DBManager, 
                            days: int = 7) -> Dict[str, Any]:
    """Get comprehensive group analytics | دریافت آنالیتیکس جامع گروه"""
    try:
        # Get active players count
        since_timestamp = now() - (days * 86400)
        
        active_players = await db_manager.db("""
            SELECT COUNT(*) as count FROM players 
            WHERE chat_id = %s AND last_active > %s
        """, (chat_id, since_timestamp), fetch="one_dict")
        
        # Get total activity
        total_activity = await db_manager.db("""
            SELECT SUM(activity_points) as total FROM players 
            WHERE chat_id = %s AND last_active > %s
        """, (chat_id, since_timestamp), fetch="one_dict")
        
        # Get language distribution
        lang_distribution = await db_manager.db("""
            SELECT language, COUNT(*) as count FROM players 
            WHERE chat_id = %s AND last_active > %s
            GROUP BY language
        """, (chat_id, since_timestamp), fetch="all")
        
        return {
            "active_players": active_players["count"] if active_players else 0,
            "total_activity": total_activity["total"] if total_activity and total_activity["total"] else 0,
            "language_distribution": {row["language"]: row["count"] for row in lang_distribution} if lang_distribution else {},
            "analysis_period_days": days,
            "cache_performance": smart_cache.get_stats(),
            "system_performance": performance_monitor.get_performance_stats()
        }
        
    except Exception as e:
        logger.error(f"Error getting group analytics: {e}")
        return {}

# Export enhanced classes and instances
__all__ = [
    # Enhanced core classes
    'AdvancedPlayerManager', 'AdvancedDefenseManager', 'AdvancedGameMechanics', 
    'AdvancedMessageUtils', 'AchievementTracker', 'PerformanceMonitor',
    
    # Data structures
    'PlayerStats', 'GameSession', 'ActionType', 'DifficultyLevel', 'CacheEntry',
    
    # Utility systems
    'SmartCache', 'smart_cache', 'performance_monitor',
    
    # Enhanced helper functions
    'format_time_persian', 'format_duration', 'sanitize_text',
    'get_comprehensive_player_info', 'get_group_analytics',
    
    # Legacy compatibility functions
    'ensure_group', 'ensure_player', 'get_lang', 'set_lang', 'medals', 'add_medals',
    'shield_rem', 'intercept_state', 'update_cooldown', 'get_args', 'contains_attack_keyword',
    'get_weapon_display_name', 'get_weapon_emoji', 'get_player_level_info', 
    'handle_regular_messages', 'ensure_group_command',
    
    # Time functions
    'now'
]
