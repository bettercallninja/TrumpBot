#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
مدیریت‌کننده‌های پیشرفته پیام با پشتیبانی کامل از زبان فارسی
Enhanced Message Handlers with Comprehensive Persian Language Support

این ماژول شامل سیستم مدیریت پیام‌های پیشرفته با ویژگی‌های زیر است:
- مدیریت پیام‌های متنی هوشمند با تشخیص قصد
- سیستم خوشامدگویی پیشرفته با شخصی‌سازی
- مدیریت پرداخت‌های Telegram Stars
- تحلیل احساسات و تشخیص زبان خودکار
- سیستم پاسخ‌گویی هوشمند با AI
- مدیریت اعضای گروه با ویژگی‌های پیشرفته
- سیستم انتی‌اسپم و مدیریت محتوا
- گزارش‌گیری و تحلیل عملکرد
"""

import logging
import random
import re
import time
import asyncio
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict, deque

from telebot import types
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message, User, Chat, CallbackQuery

from src.database.db_manager import DBManager
from src.utils.helpers import ensure_player, get_lang, set_lang, handle_regular_messages
from src.utils.translations import T
from src.config.bot_config import BOT_CONFIG

# تنظیم لاگینگ پیشرفته - Enhanced Logging Setup
logger = logging.getLogger(__name__)
message_logger = logging.getLogger(f"{__name__}.messages")
security_logger = logging.getLogger(f"{__name__}.security")
analytics_logger = logging.getLogger(f"{__name__}.analytics")

# =============================================================================
# انواع و کلاس‌های داده - Data Types and Classes
# =============================================================================

class MessageType(Enum):
    """انواع پیام - Message Types"""
    TEXT = "text"
    COMMAND = "command"
    NEW_MEMBER = "new_member"
    LEFT_MEMBER = "left_member"
    PHOTO = "photo"
    VIDEO = "video"
    DOCUMENT = "document"
    AUDIO = "audio"
    VOICE = "voice"
    STICKER = "sticker"
    LOCATION = "location"
    CONTACT = "contact"
    PAYMENT = "payment"
    WEB_APP_DATA = "web_app_data"
    FORWARD = "forward"
    REPLY = "reply"
    EDIT = "edit"
    PIN = "pin"
    GAME = "game"
    UNKNOWN = "unknown"

class MessageSentiment(Enum):
    """احساسات پیام - Message Sentiment"""
    POSITIVE = "positive"    # مثبت
    NEGATIVE = "negative"    # منفی
    NEUTRAL = "neutral"      # خنثی
    AGGRESSIVE = "aggressive"  # تهاجمی
    FRIENDLY = "friendly"    # دوستانه
    QUESTIONING = "questioning"  # سوالی

class UserIntention(Enum):
    """قصد کاربر - User Intention"""
    PLAY_GAME = "play_game"          # بازی کردن
    GET_HELP = "get_help"            # درخواست کمک
    CHECK_STATUS = "check_status"    # بررسی وضعیت
    ATTACK_PLAYER = "attack_player"  # حمله به بازیکن
    BUY_ITEM = "buy_item"            # خرید آیتم
    VIEW_STATS = "view_stats"        # مشاهده آمار
    CHANGE_SETTINGS = "change_settings"  # تغییر تنظیمات
    SOCIAL_CHAT = "social_chat"      # گفتگوی اجتماعی
    COMPLAINT = "complaint"          # شکایت
    SUPPORT = "support"              # پشتیبانی
    UNKNOWN = "unknown"              # نامشخص

@dataclass
class MessageContext:
    """بافت پیام - Message Context"""
    message: Message
    bot: AsyncTeleBot
    db_manager: DBManager
    message_type: MessageType
    user_id: int
    chat_id: int
    user_lang: str
    chat_lang: str
    is_private: bool
    is_group: bool
    is_supergroup: bool
    is_channel: bool
    is_bot_mentioned: bool
    is_reply_to_bot: bool
    timestamp: datetime
    message_hash: str
    user_history: List[Dict[str, Any]] = field(default_factory=list)
    sentiment: Optional[MessageSentiment] = None
    intention: Optional[UserIntention] = None
    confidence_score: float = 0.0

@dataclass
class UserProfile:
    """پروفایل کاربر - User Profile"""
    user_id: int
    username: Optional[str]
    first_name: str
    last_name: Optional[str]
    language_code: Optional[str]
    is_bot: bool
    is_premium: bool = False
    join_date: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    message_count: int = 0
    command_usage: Dict[str, int] = field(default_factory=dict)
    preferred_language: str = "en"
    timezone: Optional[str] = None
    reputation_score: float = 0.0
    interaction_style: str = "neutral"

@dataclass
class ChatMetrics:
    """معیارهای گروه - Chat Metrics"""
    chat_id: int
    title: str
    type: str
    member_count: int = 0
    active_users_today: int = 0
    message_count_today: int = 0
    command_count_today: int = 0
    spam_score: float = 0.0
    engagement_rate: float = 0.0
    language_distribution: Dict[str, int] = field(default_factory=dict)
    peak_activity_hour: int = 12
    
# =============================================================================
# سیستم تحلیل پیام - Message Analysis System
# =============================================================================

class MessageAnalyzer:
    """تحلیل‌گر پیام‌های پیشرفته - Advanced Message Analyzer"""
    
    def __init__(self):
        # الگوهای تشخیص قصد - Intent Recognition Patterns
        self.intent_patterns = {
            UserIntention.PLAY_GAME: [
                # English patterns
                r'\b(play|game|start|begin|let\'s play)\b',
                r'\b(trump|attack|fight|battle)\b',
                # Persian patterns
                r'\b(بازی|شروع|بیا|بازی کن|شروع کن)\b',
                r'\b(ترامپ|حمله|نبرد|جنگ|بازی کردن)\b'
            ],
            UserIntention.GET_HELP: [
                # English patterns
                r'\b(help|how|guide|explain|tutorial)\b',
                r'\b(what|how do|how to|instruction)\b',
                # Persian patterns
                r'\b(کمک|راهنما|چطور|چگونه|آموزش)\b',
                r'\b(توضیح|راهنمایی|کمک کن|بگو)\b'
            ],
            UserIntention.CHECK_STATUS: [
                # English patterns
                r'\b(status|stats|level|health|money)\b',
                r'\b(profile|account|balance|score)\b',
                # Persian patterns
                r'\b(وضعیت|آمار|سطح|سلامتی|پول)\b',
                r'\b(پروفایل|حساب|موجودی|امتیاز)\b'
            ],
            UserIntention.ATTACK_PLAYER: [
                # English patterns
                r'\b(attack|fight|kill|shoot|hit)\b',
                r'\b(weapon|gun|sword|bomb)\b',
                # Persian patterns
                r'\b(حمله|بکش|تیراندازی|زدن|نبرد)\b',
                r'\b(سلاح|تفنگ|شمشیر|بمب)\b'
            ],
            UserIntention.BUY_ITEM: [
                # English patterns
                r'\b(buy|purchase|shop|store|get)\b',
                r'\b(item|weapon|medicine|upgrade)\b',
                # Persian patterns
                r'\b(خرید|بخر|فروشگاه|دکان|بگیر)\b',
                r'\b(آیتم|سلاح|دارو|ارتقا)\b'
            ],
            UserIntention.SOCIAL_CHAT: [
                # English patterns
                r'\b(hello|hi|good|nice|thanks|bye)\b',
                r'\b(how are you|what\'s up|see you)\b',
                # Persian patterns  
                r'\b(سلام|درود|خوبی|چطوری|ممنون|خداحافظ)\b',
                r'\b(حالت چطوره|چه خبر|تا بعد)\b'
            ]
        }
        
        # الگوهای تحلیل احساسات - Sentiment Analysis Patterns
        self.sentiment_patterns = {
            MessageSentiment.POSITIVE: [
                # English
                r'\b(good|great|awesome|nice|love|like|happy|excellent)\b',
                r'\b(thank|thanks|cool|amazing|wonderful|fantastic)\b',
                # Persian
                r'\b(خوب|عالی|فوق‌العاده|قشنگ|دوست دارم|خوشحال|ممنون)\b',
                r'\b(باحال|جالب|کول|مرسی|تشکر|شگفت‌انگیز)\b'
            ],
            MessageSentiment.NEGATIVE: [
                # English
                r'\b(bad|terrible|awful|hate|suck|worst|annoying)\b',
                r'\b(stupid|dumb|boring|useless|disappointed)\b',
                # Persian
                r'\b(بد|افتضاح|متنفر|کسل‌کننده|احمق|بیخود)\b',
                r'\b(ناامید|ضایع|مزخرف|کودن|بی‌فایده)\b'
            ],
            MessageSentiment.AGGRESSIVE: [
                # English
                r'\b(kill|die|shut up|idiot|damn|hell|fuck)\b',
                r'\b(destroy|murder|violence|angry|mad|rage)\b',
                # Persian
                r'\b(بکش|بمیر|خفه شو|احمق|لعنت|جهنم)\b',
                r'\b(نابود|قتل|خشمگین|عصبانی|خشم)\b'
            ],
            MessageSentiment.FRIENDLY: [
                # English
                r'\b(friend|buddy|pal|mate|welcome|join)\b',
                r'\b(together|team|group|community|help)\b',
                # Persian
                r'\b(دوست|رفیق|همراه|خوش آمدی|بپیوند)\b',
                r'\b(با هم|تیم|گروه|جامعه|کمک)\b'
            ]
        }
        
        # کلمات کلیدی مهم - Important Keywords
        self.important_keywords = {
            'bot_mentions': [
                'trump', 'bot', 'ربات', 'ترامپ'
            ],
            'game_terms': [
                'game', 'play', 'attack', 'weapon', 'بازی', 'حمله', 'سلاح'
            ],
            'help_terms': [
                'help', 'how', 'guide', 'کمک', 'راهنما', 'چطور'
            ]
        }
    
    async def analyze_message(self, context: MessageContext) -> MessageContext:
        """تحلیل جامع پیام - Comprehensive message analysis"""
        try:
            if not context.message.text:
                return context
            
            message_text = context.message.text.lower()
            
            # تشخیص قصد - Intent Recognition
            context.intention = await self._detect_intention(message_text)
            
            # تحلیل احساسات - Sentiment Analysis
            context.sentiment = await self._analyze_sentiment(message_text)
            
            # محاسبه امتیاز اطمینان - Calculate Confidence Score
            context.confidence_score = await self._calculate_confidence(
                message_text, context.intention, context.sentiment
            )
            
            # ثبت آنالیتیکس - Log Analytics
            await self._log_analysis(context)
            
            return context
            
        except Exception as e:
            logger.error(f"Error analyzing message: {e}")
            return context
    
    async def _detect_intention(self, text: str) -> UserIntention:
        """تشخیص قصد کاربر - Detect user intention"""
        intention_scores = {}
        
        for intention, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                score += matches
            intention_scores[intention] = score
        
        # پیدا کردن بیشترین امتیاز - Find highest score
        if intention_scores and max(intention_scores.values()) > 0:
            return max(intention_scores, key=intention_scores.get)
        
        return UserIntention.UNKNOWN
    
    async def _analyze_sentiment(self, text: str) -> MessageSentiment:
        """تحلیل احساسات - Analyze sentiment"""
        sentiment_scores = {}
        
        for sentiment, patterns in self.sentiment_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                score += matches
            sentiment_scores[sentiment] = score
        
        # پیدا کردن بیشترین امتیاز - Find highest score
        if sentiment_scores and max(sentiment_scores.values()) > 0:
            return max(sentiment_scores, key=sentiment_scores.get)
        
        return MessageSentiment.NEUTRAL
    
    async def _calculate_confidence(
        self, 
        text: str, 
        intention: UserIntention, 
        sentiment: MessageSentiment
    ) -> float:
        """محاسبه امتیاز اطمینان - Calculate confidence score"""
        base_score = 0.5
        
        # افزایش امتیاز بر اساس تطبیق الگو - Increase score based on pattern matching
        if intention != UserIntention.UNKNOWN:
            base_score += 0.3
        
        if sentiment != MessageSentiment.NEUTRAL:
            base_score += 0.2
        
        # افزایش امتیاز برای کلمات کلیدی - Increase score for keywords
        for category, keywords in self.important_keywords.items():
            for keyword in keywords:
                if keyword in text.lower():
                    base_score += 0.05
        
        return min(base_score, 1.0)
    
    async def _log_analysis(self, context: MessageContext):
        """ثبت نتایج تحلیل - Log analysis results"""
        analytics_logger.info(
            f"Message analysis - User: {context.user_id}, "
            f"Intention: {context.intention.value if context.intention else 'unknown'}, "
            f"Sentiment: {context.sentiment.value if context.sentiment else 'neutral'}, "
            f"Confidence: {context.confidence_score:.2f}"
        )

# نمونه سراسری تحلیل‌گر - Global analyzer instance
message_analyzer = MessageAnalyzer()

# =============================================================================
# سیستم مدیریت انتی‌اسپم - Anti-Spam Management System  
# =============================================================================

class AntiSpamManager:
    """مدیر انتی‌اسپم پیشرفته - Advanced Anti-Spam Manager"""
    
    def __init__(self):
        self.user_message_history: Dict[int, deque] = defaultdict(lambda: deque(maxlen=20))
        self.spam_scores: Dict[int, float] = defaultdict(float)
        self.blocked_users: Dict[int, datetime] = {}
        
        # تنظیمات انتی‌اسپم - Anti-spam settings
        self.max_messages_per_minute = 10
        self.max_duplicate_messages = 3
        self.spam_threshold = 0.8
        self.block_duration = timedelta(minutes=30)
        
        # الگوهای اسپم - Spam patterns
        self.spam_patterns = [
            r'(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)',  # URLs
            r'(@[a-zA-Z0-9_]+)',  # Mentions
            r'(\b[A-Z]{5,}\b)',  # All caps words
            r'(.)\1{5,}',  # Repeated characters
            r'(💰|💵|💸|🤑|💲)',  # Money emojis
        ]
    
    async def check_message_spam(self, context: MessageContext) -> bool:
        """بررسی اسپم بودن پیام - Check if message is spam"""
        try:
            user_id = context.user_id
            message_text = context.message.text or ""
            current_time = datetime.now()
            
            # بررسی کاربران مسدود شده - Check blocked users
            if user_id in self.blocked_users:
                if current_time - self.blocked_users[user_id] < self.block_duration:
                    return True  # Still blocked
                else:
                    del self.blocked_users[user_id]  # Unblock user
            
            # افزودن پیام به تاریخچه - Add message to history
            self.user_message_history[user_id].append({
                'text': message_text,
                'timestamp': current_time,
                'hash': hashlib.md5(message_text.encode()).hexdigest()
            })
            
            # محاسبه امتیاز اسپم - Calculate spam score
            spam_score = await self._calculate_spam_score(user_id, message_text, current_time)
            self.spam_scores[user_id] = spam_score
            
            # بررسی آستانه اسپم - Check spam threshold
            if spam_score >= self.spam_threshold:
                self.blocked_users[user_id] = current_time
                security_logger.warning(f"User {user_id} blocked for spam (score: {spam_score:.2f})")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking spam: {e}")
            return False
    
    async def _calculate_spam_score(self, user_id: int, message_text: str, current_time: datetime) -> float:
        """محاسبه امتیاز اسپم - Calculate spam score"""
        score = 0.0
        user_history = self.user_message_history[user_id]
        
        # بررسی فرکانس پیام - Check message frequency
        recent_messages = [
            msg for msg in user_history 
            if (current_time - msg['timestamp']).seconds < 60
        ]
        if len(recent_messages) > self.max_messages_per_minute:
            score += 0.4
        
        # بررسی پیام‌های تکراری - Check duplicate messages
        message_hash = hashlib.md5(message_text.encode()).hexdigest()
        duplicate_count = sum(1 for msg in user_history if msg['hash'] == message_hash)
        if duplicate_count > self.max_duplicate_messages:
            score += 0.3
        
        # بررسی الگوهای اسپم - Check spam patterns
        for pattern in self.spam_patterns:
            if re.search(pattern, message_text, re.IGNORECASE):
                score += 0.1
        
        # بررسی طول پیام - Check message length
        if len(message_text) > 500:
            score += 0.1
        
        # بررسی ایموجی‌های مشکوک - Check suspicious emojis
        if len(re.findall(r'[🎰🎲🔞💰💵💸🤑💲]', message_text)) > 3:
            score += 0.2
        
        return min(score, 1.0)
    
    def get_user_spam_score(self, user_id: int) -> float:
        """دریافت امتیاز اسپم کاربر - Get user spam score"""
        return self.spam_scores.get(user_id, 0.0)
    
    def is_user_blocked(self, user_id: int) -> bool:
        """بررسی مسدود بودن کاربر - Check if user is blocked"""
        if user_id not in self.blocked_users:
            return False
        
        if datetime.now() - self.blocked_users[user_id] >= self.block_duration:
            del self.blocked_users[user_id]
            return False
        
        return True

# نمونه سراسری مدیر انتی‌اسپم - Global anti-spam manager instance
anti_spam_manager = AntiSpamManager()

# =============================================================================
# سیستم پاسخ‌گویی هوشمند - Intelligent Response System
# =============================================================================

class SmartResponseSystem:
    """سیستم پاسخ‌گویی هوشمند - Smart Response System"""
    
    def __init__(self):
        # پاسخ‌های هوشمند بر اساس قصد - Smart responses based on intention
        self.intention_responses = {
            UserIntention.PLAY_GAME: {
                'fa': [
                    "🎮 عالی! آماده‌ای برای شروع نبرد؟\n\nاز /start برای شروع بازی استفاده کن!",
                    "⚔️ ترامپ بات آماده نبرد است!\n\nبا /attack می‌تونی به دیگران حمله کنی!",
                    "🚀 بیا شروع کنیم! با /help راهنمای کامل رو ببین.",
                    "💪 آماده برای اکشن؟ با /shop سلاح بخر و قدرتت رو افزایش بده!"
                ],
                'en': [
                    "🎮 Great! Ready to start the battle?\n\nUse /start to begin playing!",
                    "⚔️ Trump Bot is ready for battle!\n\nUse /attack to attack others!",
                    "🚀 Let's get started! Check /help for complete guide.",
                    "💪 Ready for action? Buy weapons with /shop and boost your power!"
                ]
            },
            UserIntention.GET_HELP: {
                'fa': [
                    "📚 حتماً کمکت می‌کنم!\n\nاز /help برای راهنمای کامل استفاده کن.",
                    "🤝 در خدمتم! چه سوالی داری؟\n\n/help - راهنمای کامل\n/status - وضعیت\n/shop - فروشگاه",
                    "💡 سوال داری؟ من اینجام تا کمکت کنم!\n\nبا /help همه چیز رو یاد بگیر.",
                    "🎯 چه کاری برات انجام بدم؟\n\nاز منوی /start می‌تونی همه امکانات رو ببینی."
                ],
                'en': [
                    "📚 Sure, I'll help you!\n\nUse /help for complete guidance.",
                    "🤝 At your service! What questions do you have?\n\n/help - Complete guide\n/status - Status\n/shop - Shop",
                    "💡 Have questions? I'm here to help!\n\nLearn everything with /help.",
                    "🎯 What can I do for you?\n\nCheck all features in /start menu."
                ]
            },
            UserIntention.CHECK_STATUS: {
                'fa': [
                    "📊 بیا وضعیتت رو بررسی کنیم!\n\nاز /status استفاده کن.",
                    "💪 می‌خوای ببینی چقدر قدرتمندی؟\n\n/status - وضعیت کلی\n/stats - آمار کامل",
                    "🎯 آمارهات رو ببین!\n\nبا /status وضعیت فعلیت رو چک کن.",
                    "📈 پیشرفتت رو بررسی کن!\n\n/status برای دیدن سلامتی و پول\n/stats برای آمار کامل"
                ],
                'en': [
                    "📊 Let's check your status!\n\nUse /status command.",
                    "💪 Want to see how powerful you are?\n\n/status - General status\n/stats - Complete statistics",
                    "🎯 Check your stats!\n\nUse /status to see current condition.",
                    "📈 Review your progress!\n\n/status for health and money\n/stats for complete statistics"
                ]
            },
            UserIntention.ATTACK_PLAYER: {
                'fa': [
                    "⚔️ آماده نبرد؟!\n\nبا /attack یک هدف انتخاب کن و حمله کن!",
                    "💥 زمان نبرد فرا رسیده!\n\nاز /attack استفاده کن تا به دشمنانت حمله کنی.",
                    "🔫 سلاح‌هات آماده؟\n\nبا /weapons سلاح‌هات رو ببین و با /attack حمله کن!",
                    "⚡ انرژی نبرد رو حس می‌کنم!\n\nبا /attack مخالفت رو شروع کن!"
                ],
                'en': [
                    "⚔️ Ready for battle?!\n\nUse /attack to select a target and attack!",
                    "💥 Battle time has come!\n\nUse /attack to strike your enemies.",
                    "🔫 Are your weapons ready?\n\nCheck /weapons and attack with /attack!",
                    "⚡ I can feel the battle energy!\n\nStart the fight with /attack!"
                ]
            },
            UserIntention.BUY_ITEM: {
                'fa': [
                    "🛒 وقت خرید رسیده!\n\nبا /shop ببین چه چیزهای باحالی داریم!",
                    "💰 پولت کافیه؟\n\nاز /shop برای خرید سلاح و آیتم استفاده کن.",
                    "🎯 می‌خوای قدرتت رو افزایش بدی?\n\nبرو /shop و بهترین‌ها رو بخر!",
                    "⚡ نیاز به تجهیزات بهتر؟\n\nفروشگاه /shop منتظرته!"
                ],
                'en': [
                    "🛒 Shopping time!\n\nCheck /shop to see what cool stuff we have!",
                    "💰 Got enough money?\n\nUse /shop to buy weapons and items.",
                    "🎯 Want to boost your power?\n\nGo to /shop and buy the best items!",
                    "⚡ Need better equipment?\n\nThe /shop is waiting for you!"
                ]
            },
            UserIntention.SOCIAL_CHAT: {
                'fa': [
                    "😊 سلام! چه حال خوبی داری!\n\nمی‌خوای یه بازی کنیم؟",
                    "🤗 دوست داشتنی! خوش آمدی!\n\nبرای شروع از /start استفاده کن.",
                    "👋 چه خبر؟ امیدوارم حالت خوب باشه!\n\nیه بازی خفن داریم اینجا!",
                    "🌟 سلام گل! چطوری؟\n\nبیا با ترامپ بات سرگرم شیم!"
                ],
                'en': [
                    "😊 Hello! You seem to be in a good mood!\n\nWant to play a game?",
                    "🤗 Lovely! Welcome!\n\nUse /start to begin.",
                    "👋 What's up? Hope you're doing well!\n\nWe have a cool game here!",
                    "🌟 Hey there! How are you?\n\nLet's have fun with Trump Bot!"
                ]
            }
        }
        
        # پاسخ‌های بر اساس احساسات - Responses based on sentiment
        self.sentiment_responses = {
            MessageSentiment.POSITIVE: {
                'fa': [
                    "😊 خوشحالم که حال خوبی داری!",
                    "🌟 انرژی مثبتت فوق‌العادهه!",
                    "🎉 عالیه! همین طور ادامه بده!",
                    "💫 با این انرژی حتماً برنده می‌شی!"
                ],
                'en': [
                    "😊 Glad you're feeling good!",
                    "🌟 Your positive energy is amazing!",
                    "🎉 Awesome! Keep it up!",
                    "💫 With this energy you'll definitely win!"
                ]
            },
            MessageSentiment.NEGATIVE: {
                'fa': [
                    "😔 ناراحتی؟ شاید یه بازی حالت رو بهتر کنه!",
                    "🤗 نگران نباش، همه چیز درست میشه!",
                    "💪 با یه پیروزی تو بازی حالت بهتر میشه!",
                    "🌈 بعد از باران، آفتاب میاد!"
                ],
                'en': [
                    "😔 Feeling down? Maybe a game will cheer you up!",
                    "🤗 Don't worry, everything will be fine!",
                    "💪 A victory in the game will make you feel better!",
                    "🌈 After rain comes sunshine!"
                ]
            },
            MessageSentiment.AGGRESSIVE: {
                'fa': [
                    "😮 انگار عصبانی هستی! بیا انرژیت رو تو بازی خالی کن!",
                    "⚔️ این انرژی رو می‌تونی تو نبرد استفاده کنی!",
                    "🔥 آروم باش! بازی یه راه خوب برای تخلیه انرژیه!",
                    "🎯 بجای عصبانیت، بیا توی بازی قدرت نشون بدی!"
                ],
                'en': [
                    "😮 You seem angry! Let's channel that energy into the game!",
                    "⚔️ You can use this energy in battle!",
                    "🔥 Calm down! Gaming is a great way to release energy!",
                    "🎯 Instead of anger, show your power in the game!"
                ]
            },
            MessageSentiment.FRIENDLY: {
                'fa': [
                    "🤗 چقدر مهربونی! دوست دارم باهات حرف بزنم!",
                    "😍 چه آدم خوبی هستی!",
                    "🌟 با این دوستی، قطعاً تو تیم برنده‌ها جات داری!",
                    "💝 ممنون که انقدر مودب و مهربونی!"
                ],
                'en': [
                    "🤗 You're so kind! I love talking with you!",
                    "😍 What a good person you are!",
                    "🌟 With this friendliness, you definitely belong in the winning team!",
                    "💝 Thank you for being so polite and kind!"
                ]
            }
        }
        
        # پاسخ‌های پیش‌فرض - Default responses
        self.default_responses = {
            'fa': [
                "🤖 سلام! من ترامپ بات هستم!\n\nبرای شروع از /start استفاده کن.",
                "👋 چطوری؟ آماده‌ای برای یه بازی باحال؟\n\n/help رو بزن تا همه چیز رو یاد بگیری!",
                "🎮 ترامپ بات در خدمتته!\n\nبا /start بازی رو شروع کن!",
                "⚡ انرژی داری؟ بیا نبرد کنیم!\n\nاز /attack برای حمله استفاده کن!"
            ],
            'en': [
                "🤖 Hello! I'm Trump Bot!\n\nUse /start to begin.",
                "👋 How are you? Ready for a cool game?\n\nTry /help to learn everything!",
                "🎮 Trump Bot at your service!\n\nStart playing with /start!",
                "⚡ Got energy? Let's battle!\n\nUse /attack to strike!"
            ]
        }
    
    async def generate_smart_response(self, context: MessageContext) -> Optional[str]:
        """تولید پاسخ هوشمند - Generate smart response"""
        try:
            lang = context.user_lang
            
            # پاسخ بر اساس قصد - Response based on intention
            if context.intention and context.intention in self.intention_responses:
                responses = self.intention_responses[context.intention].get(lang, 
                           self.intention_responses[context.intention]['en'])
                if responses:
                    return random.choice(responses)
            
            # پاسخ بر اساس احساسات - Response based on sentiment
            if context.sentiment and context.sentiment in self.sentiment_responses:
                responses = self.sentiment_responses[context.sentiment].get(lang,
                           self.sentiment_responses[context.sentiment]['en'])
                if responses:
                    base_response = random.choice(responses)
                    
                    # افزودن پیشنهاد دستور - Add command suggestion
                    if lang == 'fa':
                        suggestion = "\n\nمی‌خوای بازی کنیم؟ /start رو بزن!"
                    else:
                        suggestion = "\n\nWant to play? Try /start!"
                    
                    return base_response + suggestion
            
            # پاسخ پیش‌فرض - Default response
            default_responses = self.default_responses.get(lang, self.default_responses['en'])
            return random.choice(default_responses)
            
        except Exception as e:
            logger.error(f"Error generating smart response: {e}")
            return None

# نمونه سراسری سیستم پاسخ هوشمند - Global smart response system instance
smart_response_system = SmartResponseSystem()

# =============================================================================
# مدیریت‌کننده‌های پیام پیشرفته - Enhanced Message Handlers
# =============================================================================

async def handle_new_chat_members(message: Message, bot: AsyncTeleBot, db_manager: DBManager):
    """
    مدیریت پیشرفته عضویت اعضای جدید
    Enhanced handling of new chat members
    
    Args:
        message (Message): Message object containing new member info
        bot (AsyncTeleBot): Bot instance
        db_manager (DBManager): Database manager instance
    """
    if not message.new_chat_members:
        return
    
    try:
        # دریافت زبان گروه - Get chat language
        chat_lang = await db_manager.get_chat_language(message.chat.id)
        if not chat_lang:
            chat_lang = "en"
        
        # بررسی اینکه آیا خود ربات اضافه شده - Check if bot itself was added
        bot_info = await bot.get_me()
        for new_member in message.new_chat_members:
            if new_member.id == bot_info.id:
                await handle_bot_added_to_group(message, bot, db_manager, chat_lang)
                return
        
        # مدیریت اعضای جدید - Handle new members
        for new_member in message.new_chat_members:
            await handle_new_member_welcome(message, bot, db_manager, new_member, chat_lang)
            
        # ثبت آمار - Log statistics
        await log_new_members_event(message, db_manager)
        
    except Exception as e:
        logger.error(f"Error handling new chat members: {e}")

async def handle_bot_added_to_group(message: Message, bot: AsyncTeleBot, db_manager: DBManager, chat_lang: str):
    """مدیریت اضافه شدن ربات به گروه - Handle bot added to group"""
    try:
        # ثبت گروه در پایگاه داده - Register chat in database
        await db_manager.ensure_chat_exists(
            chat_id=message.chat.id,
            title=message.chat.title or "Unknown Group",
            chat_type=message.chat.type,
            language=chat_lang
        )
        
        # پیام خوشامدگویی پیشرفته - Advanced welcome message
        if chat_lang == "fa":
            welcome_text = "🤖 **سلام! من ترامپ بات هستم!** 🎮\n\n"
            welcome_text += "🌟 **من یک بازی گروهی پیشرفته و سرگرم‌کننده هستم که شامل:**\n\n"
            welcome_text += "⚔️ • **سیستم نبرد پیشرفته** - با سلاح‌های مختلف به یکدیگر حمله کنید\n"
            welcome_text += "🏆 • **سیستم امتیازدهی** - مدال‌ها و امتیازات کسب کنید\n"
            welcome_text += "🛒 • **فروشگاه پیشرفته** - سلاح‌ها و آیتم‌های قدرتمند بخرید\n"
            welcome_text += "📊 • **آمار کامل** - پیشرفت خود را دنبال کنید\n"
            welcome_text += "🌐 • **پشتیبانی کامل از زبان فارسی** - رابط کاربری کاملاً فارسی\n\n"
            welcome_text += "🚀 **برای شروع:**\n"
            welcome_text += "📚 `/help` - راهنمای کامل\n"
            welcome_text += "🎮 `/start` - شروع بازی\n"
            welcome_text += "📊 `/status` - وضعیت شما\n"
            welcome_text += "⚔️ `/attack` - حمله به دیگران\n\n"
            welcome_text += "🎯 **آماده‌اید برای ماجراجویی؟**"
        else:
            welcome_text = "🤖 **Hello! I'm Trump Bot!** 🎮\n\n"
            welcome_text += "🌟 **I'm an advanced and entertaining group game featuring:**\n\n"
            welcome_text += "⚔️ • **Advanced Battle System** - Attack each other with various weapons\n"
            welcome_text += "🏆 • **Scoring System** - Earn medals and points\n"
            welcome_text += "🛒 • **Advanced Shop** - Buy powerful weapons and items\n"
            welcome_text += "📊 • **Complete Statistics** - Track your progress\n"
            welcome_text += "🌐 • **Full Persian Language Support** - Complete Persian interface\n\n"
            welcome_text += "🚀 **To get started:**\n"
            welcome_text += "📚 `/help` - Complete guide\n"
            welcome_text += "🎮 `/start` - Start playing\n"
            welcome_text += "📊 `/status` - Your status\n"
            welcome_text += "⚔️ `/attack` - Attack others\n\n"
            welcome_text += "🎯 **Ready for adventure?**"
        
        # ایجاد کیبورد پیشرفته - Create advanced keyboard
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        
        if chat_lang == "fa":
            keyboard.add(
                types.InlineKeyboardButton("🎮 شروع بازی", callback_data="go:start"),
                types.InlineKeyboardButton("📚 راهنمای کامل", callback_data="go:help")
            )
            keyboard.add(
                types.InlineKeyboardButton("⚙️ تنظیمات", callback_data="go:settings"),
                types.InlineKeyboardButton("🌐 تغییر زبان", callback_data="lang:en")
            )
            keyboard.add(
                types.InlineKeyboardButton("📊 آمار ربات", callback_data="do:bot_stats"),
                types.InlineKeyboardButton("🆘 پشتیبانی", callback_data="go:support")
            )
        else:
            keyboard.add(
                types.InlineKeyboardButton("🎮 Start Game", callback_data="go:start"),
                types.InlineKeyboardButton("📚 Complete Guide", callback_data="go:help")
            )
            keyboard.add(
                types.InlineKeyboardButton("⚙️ Settings", callback_data="go:settings"),
                types.InlineKeyboardButton("🌐 فارسی", callback_data="lang:fa")
            )
            keyboard.add(
                types.InlineKeyboardButton("📊 Bot Stats", callback_data="do:bot_stats"),
                types.InlineKeyboardButton("🆘 Support", callback_data="go:support")
            )
        
        # ارسال پیام خوشامدگویی - Send welcome message
        await bot.send_message(
            message.chat.id,
            welcome_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        # ثبت لاگ - Log event
        logger.info(f"Bot added to group {message.chat.id} ({message.chat.title})")
        
    except Exception as e:
        logger.error(f"Error handling bot added to group: {e}")

async def handle_new_member_welcome(
    message: Message, 
    bot: AsyncTeleBot, 
    db_manager: DBManager, 
    new_member: User, 
    chat_lang: str
):
    """خوشامدگویی پیشرفته به عضو جدید - Advanced welcome for new member"""
    try:
        # اطمینان از وجود کاربر در پایگاه داده - Ensure user exists in database
        await ensure_player(message.chat.id, new_member, db_manager)
        
        # دریافت زبان ترجیحی کاربر - Get user preferred language
        user_lang = await get_lang(message.chat.id, new_member.id, db_manager)
        if not user_lang:
            user_lang = chat_lang
        
        # تولید پیام خوشامدگویی شخصی‌سازی شده - Generate personalized welcome message
        welcome_messages = await generate_welcome_messages(new_member, user_lang, db_manager)
        selected_welcome = random.choice(welcome_messages)
        
        # ایجاد کیبورد خوشامدگویی - Create welcome keyboard
        keyboard = await create_welcome_keyboard(user_lang)
        
        # ارسال پیام خوشامدگویی - Send welcome message
        await bot.send_message(
            message.chat.id,
            selected_welcome,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        # ثبت آمار کاربر جدید - Log new user statistics
        await db_manager.log_new_user_join(message.chat.id, new_member.id, user_lang)
        
        logger.info(f"New member welcomed: {new_member.id} in chat {message.chat.id}")
        
    except Exception as e:
        logger.error(f"Error welcoming new member: {e}")

async def generate_welcome_messages(user: User, lang: str, db_manager: DBManager) -> List[str]:
    """تولید پیام‌های خوشامدگویی - Generate welcome messages"""
    user_name = user.first_name
    
    if lang == "fa":
        messages = [
            f"🎉 **سلام {user_name} عزیز!**\n\n"
            f"خوش آمدی به دنیای هیجان‌انگیز ترامپ بات! 🚀\n\n"
            f"اینجا می‌تونی:\n"
            f"⚔️ با دیگران نبرد کنی\n"
            f"🛒 سلاح‌های قدرتمند بخری\n"
            f"🏆 مدال‌ها و امتیازات کسب کنی\n"
            f"📊 آمارت رو دنبال کنی\n\n"
            f"🎮 **برای شروع `/start` رو بزن!**",
            
            f"👋 **{user_name} جان خوش اومدی!**\n\n"
            f"🎯 آماده برای ماجراجویی جدید؟\n"
            f"ترامپ بات یه بازی گروهی فوق‌العاده است که توش می‌تونی:\n\n"
            f"💪 قدرتت رو نشون بدی\n"
            f"🔫 با سلاح‌های مختلف نبرد کنی\n"
            f"💰 پول و آیتم جمع کنی\n"
            f"🌟 به لیدربورد برسی\n\n"
            f"📚 `/help` برای راهنمای کامل!",
            
            f"🌟 **{user_name} وارد میدان شد!**\n\n"
            f"🔥 آماده‌ای برای نبرد؟\n"
            f"اینجا قانون جنگله! هر کی قدرتمندتر باشه برنده است! 💪\n\n"
            f"🚀 **چیزهایی که می‌تونی انجام بدی:**\n"
            f"⚔️ `/attack` - حمله به دشمنان\n"
            f"🛡️ `/defend` - دفاع از خودت\n"
            f"🛒 `/shop` - خرید تجهیزات\n"
            f"📊 `/status` - وضعیت فعلی\n\n"
            f"🎯 **بیا شروع کنیم!**"
        ]
    else:
        messages = [
            f"🎉 **Hello dear {user_name}!**\n\n"
            f"Welcome to the exciting world of Trump Bot! 🚀\n\n"
            f"Here you can:\n"
            f"⚔️ Battle with others\n"
            f"🛒 Buy powerful weapons\n"
            f"🏆 Earn medals and points\n"
            f"📊 Track your statistics\n\n"
            f"🎮 **Hit `/start` to begin!**",
            
            f"👋 **Welcome {user_name}!**\n\n"
            f"🎯 Ready for a new adventure?\n"
            f"Trump Bot is an amazing group game where you can:\n\n"
            f"💪 Show your strength\n"
            f"🔫 Battle with various weapons\n"
            f"💰 Collect money and items\n"
            f"🌟 Reach the leaderboard\n\n"
            f"📚 Try `/help` for complete guide!",
            
            f"🌟 **{user_name} entered the battlefield!**\n\n"
            f"🔥 Ready for battle?\n"
            f"This is the law of the jungle! The strongest wins! 💪\n\n"
            f"🚀 **Things you can do:**\n"
            f"⚔️ `/attack` - Attack enemies\n"
            f"🛡️ `/defend` - Defend yourself\n"
            f"🛒 `/shop` - Buy equipment\n"
            f"📊 `/status` - Current status\n\n"
            f"🎯 **Let's get started!**"
        ]
    
    return messages

async def create_welcome_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    """ایجاد کیبورد خوشامدگویی - Create welcome keyboard"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    if lang == "fa":
        keyboard.add(
            types.InlineKeyboardButton("🎮 شروع بازی", callback_data="go:start"),
            types.InlineKeyboardButton("📚 راهنما", callback_data="go:help")
        )
        keyboard.add(
            types.InlineKeyboardButton("📊 وضعیت من", callback_data="go:status"),
            types.InlineKeyboardButton("🛒 فروشگاه", callback_data="go:shop")
        )
        keyboard.add(
            types.InlineKeyboardButton("⚔️ حمله!", callback_data="go:attack"),
            types.InlineKeyboardButton("🏆 لیدربورد", callback_data="go:leaderboard")
        )
    else:
        keyboard.add(
            types.InlineKeyboardButton("🎮 Start Game", callback_data="go:start"),
            types.InlineKeyboardButton("📚 Help", callback_data="go:help")
        )
        keyboard.add(
            types.InlineKeyboardButton("📊 My Status", callback_data="go:status"),
            types.InlineKeyboardButton("🛒 Shop", callback_data="go:shop")
        )
        keyboard.add(
            types.InlineKeyboardButton("⚔️ Attack!", callback_data="go:attack"),
            types.InlineKeyboardButton("🏆 Leaderboard", callback_data="go:leaderboard")
        )
    
    return keyboard

async def handle_left_chat_member(message: Message, bot: AsyncTeleBot, db_manager: DBManager):
    """
    مدیریت پیشرفته خروج اعضا از گروه
    Enhanced handling of members leaving the chat
    
    Args:
        message (Message): Message object containing left member info
        bot (AsyncTeleBot): Bot instance
        db_manager (DBManager): Database manager instance
    """
    if not message.left_chat_member:
        return
    
    try:
        left_member = message.left_chat_member
        bot_info = await bot.get_me()
        
        # بررسی اینکه آیا خود ربات حذف شده - Check if bot itself was removed
        if left_member.id == bot_info.id:
            await handle_bot_removed_from_group(message, bot, db_manager)
            return
        
        # مدیریت خروج کاربر عادی - Handle normal user leaving
        await handle_user_left_group(message, bot, db_manager, left_member)
        
        # ثبت آمار - Log statistics
        await log_member_left_event(message, db_manager, left_member)
        
    except Exception as e:
        logger.error(f"Error handling left chat member: {e}")

async def handle_bot_removed_from_group(message: Message, bot: AsyncTeleBot, db_manager: DBManager):
    """مدیریت حذف ربات از گروه - Handle bot removed from group"""
    try:
        # ثبت لاگ حذف - Log removal
        logger.info(f"Bot removed from group {message.chat.id} ({message.chat.title})")
        
        # به‌روزرسانی وضعیت گروه در پایگاه داده - Update chat status in database
        await db_manager.update_chat_status(message.chat.id, "inactive")
        
        # ثبت آمار حذف - Log removal statistics
        await db_manager.log_bot_removal(message.chat.id, datetime.now())
        
        security_logger.info(f"Bot removed from chat {message.chat.id}")
        
    except Exception as e:
        logger.error(f"Error handling bot removal: {e}")

async def handle_user_left_group(message: Message, bot: AsyncTeleBot, db_manager: DBManager, left_member: User):
    """مدیریت خروج کاربر از گروه - Handle user leaving group"""
    try:
        # دریافت زبان گروه - Get chat language
        chat_lang = await db_manager.get_chat_language(message.chat.id) or "en"
        
        # به‌روزرسانی وضعیت کاربر - Update user status
        await db_manager.update_user_status(message.chat.id, left_member.id, "left")
        
        # ثبت زمان خروج - Log departure time
        await db_manager.log_user_departure(message.chat.id, left_member.id, datetime.now())
        
        # تولید پیام خداحافظی (اختیاری) - Generate farewell message (optional)
        # Note: Many groups prefer not to announce departures to avoid spam
        
        logger.info(f"User {left_member.id} ({left_member.first_name}) left chat {message.chat.id}")
        
    except Exception as e:
        logger.error(f"Error handling user departure: {e}")

async def handle_telegram_stars_payment(message: Message, bot: AsyncTeleBot, db_manager: DBManager):
    """
    مدیریت پیشرفته پرداخت‌های Telegram Stars
    Enhanced Telegram Stars payment handling
    
    Args:
        message (Message): Message object containing payment info
        bot (AsyncTeleBot): Bot instance
        db_manager (DBManager): Database manager instance
    """
    try:
        # بررسی وجود اطلاعات پرداخت - Check payment info existence
        if not message.successful_payment:
            logger.warning("Received payment message without payment info")
            return
        
        payment_info = message.successful_payment
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        # دریافت زبان کاربر - Get user language
        user_lang = await get_lang(chat_id, user_id, db_manager)
        
        # پردازش پرداخت موفق - Process successful payment
        await process_successful_stars_payment(message, bot, db_manager, payment_info, user_lang)
        
        # ثبت آمار پرداخت - Log payment statistics
        await log_payment_statistics(message, db_manager, payment_info)
        
        logger.info(f"Telegram Stars payment processed for user {user_id}: {payment_info}")
        
    except Exception as e:
        logger.error(f"Error handling Telegram Stars payment: {e}")
        await send_payment_error_message(message, bot, db_manager)

async def process_successful_stars_payment(
    message: Message, 
    bot: AsyncTeleBot, 
    db_manager: DBManager, 
    payment_info: types.SuccessfulPayment, 
    user_lang: str
):
    """پردازش پرداخت موفق ستاره‌ها - Process successful stars payment"""
    try:
        # وارد کردن ماژول ستاره‌ها - Import stars module
        from src.commands.stars import handle_successful_stars_payment
        
        # پردازش پرداخت - Process payment
        await handle_successful_stars_payment(message, bot, payment_info, db_manager)
        
        # ارسال پیام تایید پیشرفته - Send advanced confirmation message
        await send_payment_confirmation(message, bot, payment_info, user_lang)
        
    except ImportError:
        logger.error("Stars module not found")
        await send_generic_payment_confirmation(message, bot, payment_info, user_lang)
    except Exception as e:
        logger.error(f"Error processing stars payment: {e}")
        raise

async def send_payment_confirmation(
    message: Message, 
    bot: AsyncTeleBot, 
    payment_info: types.SuccessfulPayment, 
    user_lang: str
):
    """ارسال پیام تایید پرداخت - Send payment confirmation"""
    try:
        stars_amount = payment_info.total_amount  # This should be the stars amount
        
        if user_lang == "fa":
            confirmation_text = f"✅ **پرداخت موفق!**\n\n"
            confirmation_text += f"💫 **مقدار:** {stars_amount} ستاره تلگرام\n"
            confirmation_text += f"🧾 **شناسه تراکنش:** `{payment_info.telegram_payment_charge_id}`\n"
            confirmation_text += f"📅 **تاریخ:** {datetime.now().strftime('%Y/%m/%d %H:%M')}\n\n"
            confirmation_text += f"🎉 ستاره‌های شما با موفقیت به حساب اضافه شدند!"
        else:
            confirmation_text = f"✅ **Payment Successful!**\n\n"
            confirmation_text += f"💫 **Amount:** {stars_amount} Telegram Stars\n"
            confirmation_text += f"🧾 **Transaction ID:** `{payment_info.telegram_payment_charge_id}`\n"
            confirmation_text += f"📅 **Date:** {datetime.now().strftime('%Y/%m/%d %H:%M')}\n\n"
            confirmation_text += f"🎉 Your stars have been successfully added to your account!"
        
        # ایجاد کیبورد - Create keyboard
        keyboard = types.InlineKeyboardMarkup()
        if user_lang == "fa":
            keyboard.add(
                types.InlineKeyboardButton("📊 موجودی من", callback_data="go:status"),
                types.InlineKeyboardButton("🛒 فروشگاه", callback_data="go:shop")
            )
        else:
            keyboard.add(
                types.InlineKeyboardButton("📊 My Balance", callback_data="go:status"),
                types.InlineKeyboardButton("🛒 Shop", callback_data="go:shop")
            )
        
        await bot.send_message(
            message.chat.id,
            confirmation_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error sending payment confirmation: {e}")

async def handle_telegram_stars_payment_callback(message: Message, bot: AsyncTeleBot, db_manager: DBManager):
    """
    مدیریت کالبک‌های پرداخت Telegram Stars
    Handle Telegram Stars payment callbacks (web app data)
    
    Args:
        message (Message): Message object containing web app data
        bot (AsyncTeleBot): Bot instance
        db_manager (DBManager): Database manager instance
    """
    try:
        # بررسی وجود داده‌های وب اپ - Check web app data existence
        if not hasattr(message, 'web_app_data') or not message.web_app_data:
            return
        
        web_app_data = message.web_app_data.data
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        # بررسی نوع کالبک - Check callback type
        if not web_app_data.startswith("stars_payment:"):
            return
        
        # استخراج داده‌های پرداخت - Extract payment data
        payment_data = web_app_data.replace("stars_payment:", "")
        
        # دریافت زبان کاربر - Get user language
        user_lang = await get_lang(chat_id, user_id, db_manager)
        
        # پردازش کالبک پرداخت - Process payment callback
        await process_stars_payment_callback(message, bot, db_manager, payment_data, user_lang)
        
        logger.info(f"Stars payment callback processed for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error handling stars payment callback: {e}")

async def process_stars_payment_callback(
    message: Message, 
    bot: AsyncTeleBot, 
    db_manager: DBManager, 
    payment_data: str, 
    user_lang: str
):
    """پردازش کالبک پرداخت ستاره‌ها - Process stars payment callback"""
    try:
        # وارد کردن ماژول ستاره‌ها - Import stars module
        from src.commands.stars import handle_stars_payment_callback
        
        # پردازش کالبک - Process callback
        await handle_stars_payment_callback(message, bot, payment_data, db_manager)
        
    except ImportError:
        logger.warning("Stars module not available for callback processing")
        # ارسال پیام جایگزین - Send fallback message
        if user_lang == "fa":
            fallback_text = "⚠️ سیستم پرداخت ستاره‌ها در حال حاضر در دسترس نیست."
        else:
            fallback_text = "⚠️ Stars payment system is currently unavailable."
        
        await bot.send_message(message.chat.id, fallback_text)
    except Exception as e:
        logger.error(f"Error processing stars payment callback: {e}")

async def handle_regular_message(message: Message, bot: AsyncTeleBot, db_manager: DBManager):
    """
    مدیریت پیشرفته پیام‌های متنی عادی با تحلیل هوشمند
    Enhanced handling of regular text messages with intelligent analysis
    
    Args:
        message (Message): Message object containing text
        bot (AsyncTeleBot): Bot instance
        db_manager (DBManager): Database manager instance
    """
    try:
        # بررسی اینکه پیام دستور نیست - Skip if this is a command
        if message.text and message.text.startswith('/'):
            return
        
        # اطمینان از وجود کاربر - Ensure user exists
        await ensure_player(message.chat.id, message.from_user, db_manager)
        
        # ایجاد بافت پیام - Create message context
        context = await create_message_context(message, bot, db_manager)
        
        # بررسی انتی‌اسپم - Check anti-spam
        if await anti_spam_manager.check_message_spam(context):
            await handle_spam_message(message, bot, db_manager, context)
            return
        
        # تحلیل پیام - Analyze message
        context = await message_analyzer.analyze_message(context)
        
        # تولید پاسخ هوشمند - Generate smart response
        smart_response = await smart_response_system.generate_smart_response(context)
        
        # بررسی نیاز به پاسخ - Check if response is needed
        should_respond = await should_bot_respond(context)
        
        if should_respond and smart_response:
            # ایجاد کیبورد - Create keyboard
            keyboard = await create_smart_response_keyboard(context)
            
            # ارسال پاسخ - Send response
            await bot.reply_to(
                message,
                smart_response,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
            # ثبت تعامل - Log interaction
            await log_message_interaction(context, smart_response, db_manager)
        
        # به‌روزرسانی آمار کاربر - Update user statistics
        await update_user_message_stats(context, db_manager)
        
    except Exception as e:
        logger.error(f"Error handling regular message: {e}")
        await handle_message_processing_error(message, bot, db_manager, e)

async def create_message_context(message: Message, bot: AsyncTeleBot, db_manager: DBManager) -> MessageContext:
    """ایجاد بافت پیام - Create message context"""
    try:
        # تشخیص نوع پیام - Detect message type
        message_type = detect_message_type(message)
        
        # دریافت زبان‌ها - Get languages
        user_lang = await get_lang(message.chat.id, message.from_user.id, db_manager)
        chat_lang = await db_manager.get_chat_language(message.chat.id) or "en"
        
        # بررسی اشاره به ربات - Check bot mention
        bot_info = await bot.get_me()
        is_bot_mentioned = message.text and f"@{bot_info.username}" in message.text.lower()
        is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user.id == bot_info.id
        
        # تولید هش پیام - Generate message hash
        message_hash = hashlib.md5(
            f"{message.from_user.id}:{message.text or ''}:{message.date}".encode()
        ).hexdigest()
        
        # ایجاد بافت - Create context
        context = MessageContext(
            message=message,
            bot=bot,
            db_manager=db_manager,
            message_type=message_type,
            user_id=message.from_user.id,
            chat_id=message.chat.id,
            user_lang=user_lang,
            chat_lang=chat_lang,
            is_private=message.chat.type == "private",
            is_group=message.chat.type == "group",
            is_supergroup=message.chat.type == "supergroup",
            is_channel=message.chat.type == "channel",
            is_bot_mentioned=is_bot_mentioned,
            is_reply_to_bot=is_reply_to_bot,
            timestamp=datetime.fromtimestamp(message.date),
            message_hash=message_hash
        )
        
        return context
        
    except Exception as e:
        logger.error(f"Error creating message context: {e}")
        # بازگشت بافت پایه - Return basic context
        return MessageContext(
            message=message,
            bot=bot,
            db_manager=db_manager,
            message_type=MessageType.UNKNOWN,
            user_id=message.from_user.id,
            chat_id=message.chat.id,
            user_lang="en",
            chat_lang="en",
            is_private=False,
            is_group=True,
            is_supergroup=False,
            is_channel=False,
            is_bot_mentioned=False,
            is_reply_to_bot=False,
            timestamp=datetime.now(),
            message_hash=""
        )

def detect_message_type(message: Message) -> MessageType:
    """تشخیص نوع پیام - Detect message type"""
    if message.text:
        if message.text.startswith('/'):
            return MessageType.COMMAND
        return MessageType.TEXT
    elif message.photo:
        return MessageType.PHOTO
    elif message.video:
        return MessageType.VIDEO
    elif message.document:
        return MessageType.DOCUMENT
    elif message.audio:
        return MessageType.AUDIO
    elif message.voice:
        return MessageType.VOICE
    elif message.sticker:
        return MessageType.STICKER
    elif message.location:
        return MessageType.LOCATION
    elif message.contact:
        return MessageType.CONTACT
    elif message.new_chat_members:
        return MessageType.NEW_MEMBER
    elif message.left_chat_member:
        return MessageType.LEFT_MEMBER
    elif message.successful_payment:
        return MessageType.PAYMENT
    elif hasattr(message, 'web_app_data'):
        return MessageType.WEB_APP_DATA
    else:
        return MessageType.UNKNOWN

async def should_bot_respond(context: MessageContext) -> bool:
    """تعیین نیاز به پاسخ ربات - Determine if bot should respond"""
    # پاسخ در گفتگوی خصوصی - Always respond in private chats
    if context.is_private:
        return True
    
    # پاسخ به اشاره مستقیم - Respond to direct mentions
    if context.is_bot_mentioned or context.is_reply_to_bot:
        return True
    
    # پاسخ بر اساس قصد - Respond based on intention
    important_intentions = [
        UserIntention.GET_HELP,
        UserIntention.PLAY_GAME,
        UserIntention.SUPPORT
    ]
    
    if context.intention in important_intentions and context.confidence_score > 0.7:
        return True
    
    # پاسخ تصادفی در گروه‌ها (۵٪ احتمال) - Random response in groups (5% chance)
    if context.is_group and random.random() < 0.05:
        return True
    
    return False

async def create_smart_response_keyboard(context: MessageContext) -> types.InlineKeyboardMarkup:
    """ایجاد کیبورد پاسخ هوشمند - Create smart response keyboard"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    lang = context.user_lang
    
    # دکمه‌های بر اساس قصد - Buttons based on intention
    if context.intention == UserIntention.PLAY_GAME:
        if lang == "fa":
            keyboard.add(
                types.InlineKeyboardButton("🎮 شروع", callback_data="go:start"),
                types.InlineKeyboardButton("⚔️ حمله", callback_data="go:attack")
            )
        else:
            keyboard.add(
                types.InlineKeyboardButton("🎮 Start", callback_data="go:start"),
                types.InlineKeyboardButton("⚔️ Attack", callback_data="go:attack")
            )
    elif context.intention == UserIntention.GET_HELP:
        if lang == "fa":
            keyboard.add(
                types.InlineKeyboardButton("📚 راهنمای کامل", callback_data="go:help"),
                types.InlineKeyboardButton("🎯 شروع سریع", callback_data="go:quick_start")
            )
        else:
            keyboard.add(
                types.InlineKeyboardButton("📚 Complete Guide", callback_data="go:help"),
                types.InlineKeyboardButton("🎯 Quick Start", callback_data="go:quick_start")
            )
    elif context.intention == UserIntention.CHECK_STATUS:
        if lang == "fa":
            keyboard.add(
                types.InlineKeyboardButton("📊 وضعیت", callback_data="go:status"),
                types.InlineKeyboardButton("📈 آمار", callback_data="go:stats")
            )
        else:
            keyboard.add(
                types.InlineKeyboardButton("📊 Status", callback_data="go:status"),
                types.InlineKeyboardButton("📈 Stats", callback_data="go:stats")
            )
    else:
        # دکمه‌های عمومی - General buttons
        if lang == "fa":
            keyboard.add(
                types.InlineKeyboardButton("📚 راهنما", callback_data="go:help"),
                types.InlineKeyboardButton("🎮 بازی", callback_data="go:start")
            )
        else:
            keyboard.add(
                types.InlineKeyboardButton("📚 Help", callback_data="go:help"),
                types.InlineKeyboardButton("🎮 Game", callback_data="go:start")
            )
    
    return keyboard

# =============================================================================
# توابع کمکی پیشرفته - Advanced Helper Functions
# =============================================================================

async def handle_spam_message(message: Message, bot: AsyncTeleBot, db_manager: DBManager, context: MessageContext):
    """مدیریت پیام‌های اسپم - Handle spam messages"""
    try:
        spam_score = anti_spam_manager.get_user_spam_score(context.user_id)
        
        # ارسال هشدار خصوصی به کاربر - Send private warning to user
        if context.user_lang == "fa":
            warning_text = f"⚠️ **هشدار اسپم**\n\n"
            warning_text += f"پیام‌های شما به عنوان اسپم تشخیص داده شده‌اند.\n"
            warning_text += f"امتیاز اسپم: {spam_score:.2f}\n\n"
            warning_text += f"لطفاً از ارسال پیام‌های تکراری یا نامناسب خودداری کنید."
        else:
            warning_text = f"⚠️ **Spam Warning**\n\n"
            warning_text += f"Your messages have been detected as spam.\n"
            warning_text += f"Spam score: {spam_score:.2f}\n\n"
            warning_text += f"Please avoid sending repetitive or inappropriate messages."
        
        # ارسال پیام خصوصی - Send private message
        try:
            await bot.send_message(context.user_id, warning_text, parse_mode='Markdown')
        except:
            # اگر نتوانست خصوصی بفرستد، چیزی نمی‌فرستد - If can't send private, don't send anything
            pass
        
        # حذف پیام اسپم - Delete spam message
        try:
            await bot.delete_message(context.chat_id, message.message_id)
        except:
            # اگر نتوانست حذف کند - If can't delete
            pass
        
        # ثبت لاگ امنیتی - Log security event
        security_logger.warning(
            f"Spam detected - User: {context.user_id}, Chat: {context.chat_id}, "
            f"Score: {spam_score:.2f}, Message: {message.text[:50]}..."
        )
        
    except Exception as e:
        logger.error(f"Error handling spam message: {e}")

async def handle_message_processing_error(message: Message, bot: AsyncTeleBot, db_manager: DBManager, error: Exception):
    """مدیریت خطاهای پردازش پیام - Handle message processing errors"""
    try:
        user_lang = await get_lang(message.chat.id, message.from_user.id, db_manager)
        
        # ارسال پیام خطا به کاربر - Send error message to user
        if user_lang == "fa":
            error_text = "❌ متأسفانه در پردازش پیام شما خطایی رخ داد.\n\nلطفاً مجدداً تلاش کنید."
        else:
            error_text = "❌ Sorry, an error occurred while processing your message.\n\nPlease try again."
        
        await bot.reply_to(message, error_text)
        
        # ثبت لاگ خطا - Log error
        logger.error(f"Message processing error for user {message.from_user.id}: {error}")
        
    except Exception as e:
        logger.error(f"Error handling message processing error: {e}")

async def send_payment_error_message(message: Message, bot: AsyncTeleBot, db_manager: DBManager):
    """ارسال پیام خطای پرداخت - Send payment error message"""
    try:
        user_lang = await get_lang(message.chat.id, message.from_user.id, db_manager)
        
        if user_lang == "fa":
            error_text = "❌ خطا در پردازش پرداخت!\n\nلطفاً با پشتیبانی تماس بگیرید."
        else:
            error_text = "❌ Payment processing error!\n\nPlease contact support."
        
        keyboard = types.InlineKeyboardMarkup()
        if user_lang == "fa":
            keyboard.add(types.InlineKeyboardButton("🆘 پشتیبانی", callback_data="go:support"))
        else:
            keyboard.add(types.InlineKeyboardButton("🆘 Support", callback_data="go:support"))
        
        await bot.send_message(message.chat.id, error_text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error sending payment error message: {e}")

async def send_generic_payment_confirmation(
    message: Message, 
    bot: AsyncTeleBot, 
    payment_info: types.SuccessfulPayment, 
    user_lang: str
):
    """ارسال تایید عمومی پرداخت - Send generic payment confirmation"""
    try:
        if user_lang == "fa":
            confirmation_text = "✅ پرداخت با موفقیت انجام شد!\n\nممنون از خرید شما."
        else:
            confirmation_text = "✅ Payment completed successfully!\n\nThank you for your purchase."
        
        await bot.send_message(message.chat.id, confirmation_text)
        
    except Exception as e:
        logger.error(f"Error sending generic payment confirmation: {e}")

async def log_new_members_event(message: Message, db_manager: DBManager):
    """ثبت رویداد عضویت اعضای جدید - Log new members event"""
    try:
        for new_member in message.new_chat_members:
            await db_manager.log_user_event(
                user_id=new_member.id,
                chat_id=message.chat.id,
                event_type="member_joined",
                event_data={
                    "username": new_member.username,
                    "first_name": new_member.first_name,
                    "join_date": datetime.now().isoformat()
                }
            )
        
    except Exception as e:
        logger.error(f"Error logging new members event: {e}")

async def log_member_left_event(message: Message, db_manager: DBManager, left_member: User):
    """ثبت رویداد خروج عضو - Log member left event"""
    try:
        await db_manager.log_user_event(
            user_id=left_member.id,
            chat_id=message.chat.id,
            event_type="member_left",
            event_data={
                "username": left_member.username,
                "first_name": left_member.first_name,
                "left_date": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error logging member left event: {e}")

async def log_payment_statistics(message: Message, db_manager: DBManager, payment_info: types.SuccessfulPayment):
    """ثبت آمار پرداخت - Log payment statistics"""
    try:
        await db_manager.log_payment_event(
            user_id=message.from_user.id,
            chat_id=message.chat.id,
            amount=payment_info.total_amount,
            currency=payment_info.currency,
            provider_payment_charge_id=payment_info.provider_payment_charge_id,
            telegram_payment_charge_id=payment_info.telegram_payment_charge_id,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error logging payment statistics: {e}")

async def log_message_interaction(context: MessageContext, response: str, db_manager: DBManager):
    """ثبت تعامل پیام - Log message interaction"""
    try:
        await db_manager.log_message_interaction(
            user_id=context.user_id,
            chat_id=context.chat_id,
            message_type=context.message_type.value,
            intention=context.intention.value if context.intention else None,
            sentiment=context.sentiment.value if context.sentiment else None,
            confidence_score=context.confidence_score,
            response_generated=bool(response),
            timestamp=context.timestamp
        )
        
    except Exception as e:
        logger.error(f"Error logging message interaction: {e}")

async def update_user_message_stats(context: MessageContext, db_manager: DBManager):
    """به‌روزرسانی آمار پیام کاربر - Update user message statistics"""
    try:
        await db_manager.update_user_activity(
            user_id=context.user_id,
            chat_id=context.chat_id,
            activity_type="message_sent",
            activity_data={
                "message_type": context.message_type.value,
                "has_text": bool(context.message.text),
                "message_length": len(context.message.text) if context.message.text else 0,
                "timestamp": context.timestamp.isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error updating user message stats: {e}")

# =============================================================================
# مدیریت پیشرفته ستاره‌های تلگرام - Advanced Telegram Stars Management
# =============================================================================

async def handle_tg_stars_received(message: Message, bot: AsyncTeleBot, db_manager: DBManager):
    """
    مدیریت پیشرفته دریافت ستاره‌های تلگرام
    Enhanced handling of received TG Stars
    
    Args:
        message (Message): Message object containing stars info
        bot (AsyncTeleBot): Bot instance
        db_manager (DBManager): Database manager instance
    """
    try:
        # بررسی اینکه این پیام فوروارد شده خودکار است - Check if this is an automatic forward
        if not hasattr(message, 'is_automatic_forward') or not message.is_automatic_forward:
            return
        
        # بررسی اینکه از کانال رسمی تلگرام فوروارد شده - Check if forwarded from official Telegram
        if not hasattr(message, 'forward_from_chat') or not message.forward_from_chat:
            return
        
        # تأیید فوروارد از کانال رسمی - Verify forward from official channel
        if message.forward_from_chat.username != "telegram":
            return
        
        # بررسی متن پیام - Check message text
        if not hasattr(message, 'text') or not message.text:
            return
        
        # استخراج مقدار ستاره‌ها - Extract stars amount
        stars_amount = await extract_stars_amount_from_message(message.text)
        if not stars_amount:
            return
        
        # پردازش دریافت ستاره‌ها - Process stars received
        await process_stars_received(message, bot, db_manager, stars_amount)
        
        logger.info(f"TG Stars received processed: {stars_amount} for user {message.chat.id}")
        
    except Exception as e:
        logger.error(f"Error handling TG stars received: {e}")

async def extract_stars_amount_from_message(text: str) -> Optional[int]:
    """استخراج مقدار ستاره از متن پیام - Extract stars amount from message text"""
    try:
        # الگوهای مختلف برای تشخیص ستاره‌ها - Different patterns for stars detection
        patterns = [
            r"You've received (\d+) Telegram Stars",
            r"You received (\d+) Telegram Stars",
            r"(\d+) Telegram Stars received",
            r"شما (\d+) ستاره تلگرام دریافت کرده‌اید",
            r"(\d+) ستاره تلگرام دریافت شد"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
        
    except Exception as e:
        logger.error(f"Error extracting stars amount: {e}")
        return None

async def process_stars_received(message: Message, bot: AsyncTeleBot, db_manager: DBManager, stars_amount: int):
    """پردازش دریافت ستاره‌ها - Process stars received"""
    try:
        user_id = message.chat.id
        
        # تولید شناسه تراکنش - Generate transaction ID
        transaction_id = f"tg_stars_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # ذخیره تراکنش در پایگاه داده - Store transaction in database
        await db_manager.create_stars_transaction(
            user_id=user_id,
            amount=stars_amount,
            transaction_type="received",
            transaction_id=transaction_id,
            source="telegram_official",
            status="pending"
        )
        
        # دریافت زبان کاربر - Get user language
        user_lang = await get_lang(user_id, user_id, db_manager)
        
        # تولید پیام تایید - Generate confirmation message
        await send_stars_received_confirmation(message, bot, stars_amount, transaction_id, user_lang)
        
    except Exception as e:
        logger.error(f"Error processing stars received: {e}")

async def send_stars_received_confirmation(
    message: Message, 
    bot: AsyncTeleBot, 
    stars_amount: int, 
    transaction_id: str, 
    user_lang: str
):
    """ارسال تایید دریافت ستاره‌ها - Send stars received confirmation"""
    try:
        if user_lang == "fa":
            confirmation_text = f"🌟 **ستاره‌های تلگرام دریافت شد!**\n\n"
            confirmation_text += f"💫 **مقدار:** {stars_amount} ستاره\n"
            confirmation_text += f"🔢 **شناسه:** `{transaction_id}`\n"
            confirmation_text += f"📅 **تاریخ:** {datetime.now().strftime('%Y/%m/%d %H:%M')}\n\n"
            confirmation_text += f"🎁 برای اضافه کردن این ستاره‌ها به حساب بازی خود، دکمه زیر را فشار دهید:"
            
            claim_button_text = f"🎁 دریافت {stars_amount} ستاره"
            claim_callback = f"tg_stars_received:{stars_amount}:{transaction_id}"
        else:
            confirmation_text = f"🌟 **Telegram Stars Received!**\n\n"
            confirmation_text += f"💫 **Amount:** {stars_amount} stars\n"
            confirmation_text += f"🔢 **ID:** `{transaction_id}`\n"
            confirmation_text += f"📅 **Date:** {datetime.now().strftime('%Y/%m/%d %H:%M')}\n\n"
            confirmation_text += f"🎁 To add these stars to your game account, press the button below:"
            
            claim_button_text = f"🎁 Claim {stars_amount} Stars"
            claim_callback = f"tg_stars_received:{stars_amount}:{transaction_id}"
        
        # ایجاد کیبورد - Create keyboard
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(claim_button_text, callback_data=claim_callback))
        
        if user_lang == "fa":
            keyboard.add(
                types.InlineKeyboardButton("📊 موجودی من", callback_data="go:status"),
                types.InlineKeyboardButton("🛒 فروشگاه", callback_data="go:shop")
            )
        else:
            keyboard.add(
                types.InlineKeyboardButton("📊 My Balance", callback_data="go:status"),
                types.InlineKeyboardButton("🛒 Shop", callback_data="go:shop")
            )
        
        # ارسال پیام - Send message
        await bot.send_message(
            message.chat.id,
            confirmation_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error sending stars received confirmation: {e}")

# =============================================================================
# سیستم تحلیل و گزارش‌گیری - Analytics and Reporting System
# =============================================================================

class MessageAnalyticsCollector:
    """جمع‌آوری آنالیتیکس پیام - Message Analytics Collector"""
    
    def __init__(self):
        self.daily_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.hourly_stats: Dict[int, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.user_stats: Dict[int, Dict[str, Any]] = defaultdict(lambda: {
            'message_count': 0,
            'last_activity': datetime.now(),
            'languages_used': set(),
            'intentions_detected': defaultdict(int),
            'sentiment_distribution': defaultdict(int)
        })
    
    async def collect_message_analytics(self, context: MessageContext):
        """جمع‌آوری آنالیتیکس پیام - Collect message analytics"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            current_hour = datetime.now().hour
            
            # آمار روزانه - Daily stats
            self.daily_stats[today]['total_messages'] += 1
            self.daily_stats[today][f'type_{context.message_type.value}'] += 1
            self.daily_stats[today][f'lang_{context.user_lang}'] += 1
            
            if context.intention:
                self.daily_stats[today][f'intention_{context.intention.value}'] += 1
            
            if context.sentiment:
                self.daily_stats[today][f'sentiment_{context.sentiment.value}'] += 1
            
            # آمار ساعتی - Hourly stats
            self.hourly_stats[current_hour]['total_messages'] += 1
            self.hourly_stats[current_hour][f'lang_{context.user_lang}'] += 1
            
            # آمار کاربری - User stats
            user_stat = self.user_stats[context.user_id]
            user_stat['message_count'] += 1
            user_stat['last_activity'] = context.timestamp
            user_stat['languages_used'].add(context.user_lang)
            
            if context.intention:
                user_stat['intentions_detected'][context.intention.value] += 1
            
            if context.sentiment:
                user_stat['sentiment_distribution'][context.sentiment.value] += 1
            
        except Exception as e:
            logger.error(f"Error collecting message analytics: {e}")
    
    def get_daily_report(self, date: str = None) -> Dict[str, Any]:
        """دریافت گزارش روزانه - Get daily report"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        return dict(self.daily_stats.get(date, {}))
    
    def get_user_summary(self, user_id: int) -> Dict[str, Any]:
        """دریافت خلاصه کاربر - Get user summary"""
        user_stat = self.user_stats.get(user_id, {})
        
        # تبدیل set به list برای JSON serialization
        if 'languages_used' in user_stat:
            user_stat['languages_used'] = list(user_stat['languages_used'])
        
        return user_stat

# نمونه سراسری جمع‌آوری آنالیتیکس - Global analytics collector instance
analytics_collector = MessageAnalyticsCollector()

# =============================================================================
# سیستم ثبت مدیریت‌کننده‌ها - Handler Registration System
# =============================================================================

def register_message_handlers(bot: AsyncTeleBot, db_manager: DBManager):
    """
    ثبت مدیریت‌کننده‌های پیشرفته پیام
    Register enhanced message handlers with comprehensive functionality
    
    Args:
        bot (AsyncTeleBot): Bot instance with async support
        db_manager (DBManager): Enhanced database manager instance
    """
    logger.info("Registering enhanced message handlers with comprehensive functionality")
    logger.info("ثبت مدیریت‌کننده‌های پیشرفته پیام با عملکرد جامع")
    
    # ثبت مدیریت‌کننده اعضای جدید - Register new members handler
    @bot.message_handler(content_types=['new_chat_members'])
    async def enhanced_new_chat_members_handler(message):
        """مدیریت‌کننده پیشرفته اعضای جدید - Enhanced new members handler"""
        try:
            await handle_new_chat_members(message, bot, db_manager)
        except Exception as e:
            logger.error(f"Error in new chat members handler: {e}")
    
    # ثبت مدیریت‌کننده خروج اعضا - Register left members handler
    @bot.message_handler(content_types=['left_chat_member'])
    async def enhanced_left_chat_member_handler(message):
        """مدیریت‌کننده پیشرفته خروج اعضا - Enhanced left members handler"""
        try:
            await handle_left_chat_member(message, bot, db_manager)
        except Exception as e:
            logger.error(f"Error in left chat member handler: {e}")
    
    # ثبت مدیریت‌کننده پرداخت موفق - Register successful payment handler
    @bot.message_handler(content_types=['successful_payment'])
    async def enhanced_successful_payment_handler(message):
        """مدیریت‌کننده پیشرفته پرداخت موفق - Enhanced successful payment handler"""
        try:
            await handle_telegram_stars_payment(message, bot, db_manager)
        except Exception as e:
            logger.error(f"Error in successful payment handler: {e}")
    
    # ثبت مدیریت‌کننده داده‌های وب اپ - Register web app data handler
    @bot.message_handler(content_types=['web_app_data'])
    async def enhanced_web_app_data_handler(message):
        """مدیریت‌کننده پیشرفته داده‌های وب اپ - Enhanced web app data handler"""
        try:
            await handle_telegram_stars_payment_callback(message, bot, db_manager)
        except Exception as e:
            logger.error(f"Error in web app data handler: {e}")
    
    # ثبت مدیریت‌کننده ستاره‌های دریافتی - Register TG stars received handler
    @bot.message_handler(
        func=lambda m: (
            hasattr(m, 'is_automatic_forward') and m.is_automatic_forward and
            hasattr(m, 'forward_from_chat') and m.forward_from_chat and
            m.forward_from_chat.username == 'telegram'
        )
    )
    async def enhanced_tg_stars_received_handler(message):
        """مدیریت‌کننده پیشرفته ستاره‌های دریافتی - Enhanced TG stars received handler"""
        try:
            await handle_tg_stars_received(message, bot, db_manager)
        except Exception as e:
            logger.error(f"Error in TG stars received handler: {e}")
    
    # ثبت مدیریت‌کننده پیام‌های متنی - Register text messages handler
    @bot.message_handler(func=lambda m: True, content_types=['text'])
    async def enhanced_regular_message_handler(message):
        """مدیریت‌کننده پیشرفته پیام‌های متنی - Enhanced text messages handler"""
        try:
            # جمع‌آوری آنالیتیکس - Collect analytics
            if not (message.text and message.text.startswith('/')):
                context = await create_message_context(message, bot, db_manager)
                await analytics_collector.collect_message_analytics(context)
            
            # پردازش پیام - Process message
            await handle_regular_message(message, bot, db_manager)
            
        except Exception as e:
            logger.error(f"Error in regular message handler: {e}")
            await handle_message_processing_error(message, bot, db_manager, e)
    
    # ثبت مدیریت‌کننده سایر انواع محتوا - Register other content types handlers
    @bot.message_handler(content_types=['photo', 'video', 'document', 'audio', 'voice', 'sticker'])
    async def enhanced_media_message_handler(message):
        """مدیریت‌کننده پیشرفته پیام‌های رسانه‌ای - Enhanced media messages handler"""
        try:
            # اطمینان از وجود کاربر - Ensure user exists
            await ensure_player(message.chat.id, message.from_user, db_manager)
            
            # جمع‌آوری آنالیتیکس - Collect analytics
            context = await create_message_context(message, bot, db_manager)
            await analytics_collector.collect_message_analytics(context)
            
            # به‌روزرسانی آمار فعالیت - Update activity stats
            await update_user_message_stats(context, db_manager)
            
        except Exception as e:
            logger.error(f"Error in media message handler: {e}")
    
    # پیام تأیید ثبت - Registration confirmation message
    logger.info("✅ Enhanced message handlers registered successfully")
    logger.info("✅ مدیریت‌کننده‌های پیشرفته پیام با موفقیت ثبت شدند")
    
    # ثبت آمار ثبت - Log registration stats
    handler_types = [
        "new_chat_members", "left_chat_member", "successful_payment",
        "web_app_data", "tg_stars_received", "text_messages", "media_messages"
    ]
    
    logger.info(f"Registered {len(handler_types)} enhanced message handler types")
    logger.info(f"{len(handler_types)} نوع مدیریت‌کننده پیشرفته ثبت شد")
    
    # فعال‌سازی نظارت عملکرد - Enable performance monitoring
    logger.info(f"Message analytics: {'enabled' if True else 'disabled'}")
    logger.info(f"Anti-spam protection: {'enabled' if True else 'disabled'}")
    logger.info(f"Smart responses: {'enabled' if True else 'disabled'}")
    logger.info(f"آنالیتیکس پیام: {'فعال' if True else 'غیرفعال'}")
    logger.info(f"محافظت انتی‌اسپم: {'فعال' if True else 'غیرفعال'}")
    logger.info(f"پاسخ‌های هوشمند: {'فعال' if True else 'غیرفعال'}")

# =============================================================================
# صادرات ماژول - Module Exports
# =============================================================================

__all__ = [
    # Core message handlers
    'handle_new_chat_members',
    'handle_left_chat_member', 
    'handle_telegram_stars_payment',
    'handle_telegram_stars_payment_callback',
    'handle_regular_message',
    'handle_tg_stars_received',
    
    # Enhanced functionality
    'handle_bot_added_to_group',
    'handle_new_member_welcome',
    'handle_bot_removed_from_group',
    'handle_user_left_group',
    'process_successful_stars_payment',
    'process_stars_payment_callback',
    'process_stars_received',
    
    # Message analysis
    'MessageAnalyzer',
    'message_analyzer',
    'MessageContext',
    'MessageType',
    'MessageSentiment', 
    'UserIntention',
    
    # Anti-spam system
    'AntiSpamManager',
    'anti_spam_manager',
    
    # Smart response system
    'SmartResponseSystem',
    'smart_response_system',
    
    # Analytics system
    'MessageAnalyticsCollector',
    'analytics_collector',
    
    # Helper functions
    'create_message_context',
    'detect_message_type',
    'should_bot_respond',
    'create_smart_response_keyboard',
    'generate_welcome_messages',
    'create_welcome_keyboard',
    'extract_stars_amount_from_message',
    
    # Registration
    'register_message_handlers',
    'register_handlers',  # Alias for compatibility
    
    # Data classes
    'UserProfile',
    'ChatMetrics'
]

# پیام اولیه‌سازی - Initialization message
logger.info("Enhanced Message Handlers Module loaded successfully")
logger.info("ماژول مدیریت‌کننده‌های پیشرفته پیام با موفقیت بارگذاری شد")

# تنظیم نظارت عملکرد - Performance monitoring setup
logger.info("Message analysis system: initialized")
logger.info("Anti-spam protection: initialized") 
logger.info("Smart response system: initialized")
logger.info("Analytics collection: initialized")
logger.info("سیستم تحلیل پیام: راه‌اندازی شد")
logger.info("محافظت انتی‌اسپم: راه‌اندازی شد")
logger.info("سیستم پاسخ هوشمند: راه‌اندازی شد")
logger.info("جمع‌آوری آنالیتیکس: راه‌اندازی شد")

# Alias for compatibility with app.py
def register_handlers(bot: AsyncTeleBot, db_manager: DBManager) -> None:
    """
    Alias for register_message_handlers to maintain compatibility
    نام مستعار برای register_message_handlers برای حفظ سازگاری
    """
    return register_message_handlers(bot, db_manager)
