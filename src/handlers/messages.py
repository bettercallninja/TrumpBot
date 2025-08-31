﻿#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ù…Ø¯ÛŒØ±ÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡â€ŒÙ‡Ø§ÛŒ Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ù¾ÛŒØ§Ù… Ø¨Ø§ Ù¾Ø´ØªÛŒØ¨Ø§Ù†ÛŒ Ú©Ø§Ù…Ù„ Ø§Ø² Ø²Ø¨Ø§Ù† ÙØ§Ø±Ø³ÛŒ
Enhanced Message Handlers with Comprehensive Persian Language Support

Ø§ÛŒÙ† Ù…Ø§Ú˜ÙˆÙ„ Ø´Ø§Ù…Ù„ Ø³ÛŒØ³ØªÙ… Ù…Ø¯ÛŒØ±ÛŒØª Ù¾ÛŒØ§Ù…â€ŒÙ‡Ø§ÛŒ Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ø¨Ø§ ÙˆÛŒÚ˜Ú¯ÛŒâ€ŒÙ‡Ø§ÛŒ Ø²ÛŒØ± Ø§Ø³Øª:
- Ù…Ø¯ÛŒØ±ÛŒØª Ù¾ÛŒØ§Ù…â€ŒÙ‡Ø§ÛŒ Ù…ØªÙ†ÛŒ Ù‡ÙˆØ´Ù…Ù†Ø¯ Ø¨Ø§ ØªØ´Ø®ÛŒØµ Ù‚ØµØ¯
- Ø³ÛŒØ³ØªÙ… Ø®ÙˆØ´Ø§Ù…Ø¯Ú¯ÙˆÛŒÛŒ Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ø¨Ø§ Ø´Ø®ØµÛŒâ€ŒØ³Ø§Ø²ÛŒ
- Ù…Ø¯ÛŒØ±ÛŒØª Ù¾Ø±Ø¯Ø§Ø®Øªâ€ŒÙ‡Ø§ÛŒ Telegram Stars
- ØªØ­Ù„ÛŒÙ„ Ø§Ø­Ø³Ø§Ø³Ø§Øª Ùˆ ØªØ´Ø®ÛŒØµ Ø²Ø¨Ø§Ù† Ø®ÙˆØ¯Ú©Ø§Ø±
- Ø³ÛŒØ³ØªÙ… Ù¾Ø§Ø³Ø®â€ŒÚ¯ÙˆÛŒÛŒ Ù‡ÙˆØ´Ù…Ù†Ø¯ Ø¨Ø§ AI
- Ù…Ø¯ÛŒØ±ÛŒØª Ø§Ø¹Ø¶Ø§ÛŒ Ú¯Ø±ÙˆÙ‡ Ø¨Ø§ ÙˆÛŒÚ˜Ú¯ÛŒâ€ŒÙ‡Ø§ÛŒ Ù¾ÛŒØ´Ø±ÙØªÙ‡
- Ø³ÛŒØ³ØªÙ… Ø§Ù†ØªÛŒâ€ŒØ§Ø³Ù¾Ù… Ùˆ Ù…Ø¯ÛŒØ±ÛŒØª Ù…Ø­ØªÙˆØ§
- Ú¯Ø²Ø§Ø±Ø´â€ŒÚ¯ÛŒØ±ÛŒ Ùˆ ØªØ­Ù„ÛŒÙ„ Ø¹Ù…Ù„Ú©Ø±Ø¯
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

# ØªÙ†Ø¸ÛŒÙ… Ù„Ø§Ú¯ÛŒÙ†Ú¯ Ù¾ÛŒØ´Ø±ÙØªÙ‡ - Enhanced Logging Setup
logger = logging.getLogger(__name__)
message_logger = logging.getLogger(f"{__name__}.messages")
security_logger = logging.getLogger(f"{__name__}.security")
analytics_logger = logging.getLogger(f"{__name__}.analytics")

# =============================================================================
# Ø§Ù†ÙˆØ§Ø¹ Ùˆ Ú©Ù„Ø§Ø³â€ŒÙ‡Ø§ÛŒ Ø¯Ø§Ø¯Ù‡ - Data Types and Classes
# =============================================================================

class MessageType(Enum):
    """Ø§Ù†ÙˆØ§Ø¹ Ù¾ÛŒØ§Ù… - Message Types"""
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
    """Ø§Ø­Ø³Ø§Ø³Ø§Øª Ù¾ÛŒØ§Ù… - Message Sentiment"""
    POSITIVE = "positive"    # Ù…Ø«Ø¨Øª
    NEGATIVE = "negative"    # Ù…Ù†ÙÛŒ
    NEUTRAL = "neutral"      # Ø®Ù†Ø«ÛŒ
    AGGRESSIVE = "aggressive"  # ØªÙ‡Ø§Ø¬Ù…ÛŒ
    FRIENDLY = "friendly"    # Ø¯ÙˆØ³ØªØ§Ù†Ù‡
    QUESTIONING = "questioning"  # Ø³ÙˆØ§Ù„ÛŒ

class UserIntention(Enum):
    """Ù‚ØµØ¯ Ú©Ø§Ø±Ø¨Ø± - User Intention"""
    PLAY_GAME = "play_game"          # Ø¨Ø§Ø²ÛŒ Ú©Ø±Ø¯Ù†
    GET_HELP = "get_help"            # Ø¯Ø±Ø®ÙˆØ§Ø³Øª Ú©Ù…Ú©
    CHECK_STATUS = "check_status"    # Ø¨Ø±Ø±Ø³ÛŒ ÙˆØ¶Ø¹ÛŒØª
    ATTACK_PLAYER = "attack_player"  # Ø­Ù…Ù„Ù‡ Ø¨Ù‡ Ø¨Ø§Ø²ÛŒÚ©Ù†
    BUY_ITEM = "buy_item"            # Ø®Ø±ÛŒØ¯ Ø¢ÛŒØªÙ…
    VIEW_STATS = "view_stats"        # Ù…Ø´Ø§Ù‡Ø¯Ù‡ Ø¢Ù…Ø§Ø±
    CHANGE_SETTINGS = "change_settings"  # ØªØºÛŒÛŒØ± ØªÙ†Ø¸ÛŒÙ…Ø§Øª
    SOCIAL_CHAT = "social_chat"      # Ú¯ÙØªÚ¯ÙˆÛŒ Ø§Ø¬ØªÙ…Ø§Ø¹ÛŒ
    COMPLAINT = "complaint"          # Ø´Ú©Ø§ÛŒØª
    SUPPORT = "support"              # Ù¾Ø´ØªÛŒØ¨Ø§Ù†ÛŒ
    UNKNOWN = "unknown"              # Ù†Ø§Ù…Ø´Ø®Øµ

@dataclass
class MessageContext:
    """Ø¨Ø§ÙØª Ù¾ÛŒØ§Ù… - Message Context"""
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
    """Ù¾Ø±ÙˆÙØ§ÛŒÙ„ Ú©Ø§Ø±Ø¨Ø± - User Profile"""
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
    """Ù…Ø¹ÛŒØ§Ø±Ù‡Ø§ÛŒ Ú¯Ø±ÙˆÙ‡ - Chat Metrics"""
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
# Ø³ÛŒØ³ØªÙ… ØªØ­Ù„ÛŒÙ„ Ù¾ÛŒØ§Ù… - Message Analysis System
# =============================================================================

class MessageAnalyzer:
    """ØªØ­Ù„ÛŒÙ„â€ŒÚ¯Ø± Ù¾ÛŒØ§Ù…â€ŒÙ‡Ø§ÛŒ Ù¾ÛŒØ´Ø±ÙØªÙ‡ - Advanced Message Analyzer"""
    
    def __init__(self):
        # Ø§Ù„Ú¯ÙˆÙ‡Ø§ÛŒ ØªØ´Ø®ÛŒØµ Ù‚ØµØ¯ - Intent Recognition Patterns
        self.intent_patterns = {
            UserIntention.PLAY_GAME: [
                # English patterns
                r'\b(play|game|start|begin|let\'s play)\b',
                r'\b(trump|attack|fight|battle)\b',
                # Persian patterns
                r'\b(Ø¨Ø§Ø²ÛŒ|Ø´Ø±ÙˆØ¹|Ø¨ÛŒØ§|Ø¨Ø§Ø²ÛŒ Ú©Ù†|Ø´Ø±ÙˆØ¹ Ú©Ù†)\b',
                r'\b(ØªØ±Ø§Ù…Ù¾|Ø­Ù…Ù„Ù‡|Ù†Ø¨Ø±Ø¯|Ø¬Ù†Ú¯|Ø¨Ø§Ø²ÛŒ Ú©Ø±Ø¯Ù†)\b'
            ],
            UserIntention.GET_HELP: [
                # English patterns
                r'\b(help|how|guide|explain|tutorial)\b',
                r'\b(what|how do|how to|instruction)\b',
                # Persian patterns
                r'\b(Ú©Ù…Ú©|Ø±Ø§Ù‡Ù†Ù…Ø§|Ú†Ø·ÙˆØ±|Ú†Ú¯ÙˆÙ†Ù‡|Ø¢Ù…ÙˆØ²Ø´)\b',
                r'\b(ØªÙˆØ¶ÛŒØ­|Ø±Ø§Ù‡Ù†Ù…Ø§ÛŒÛŒ|Ú©Ù…Ú© Ú©Ù†|Ø¨Ú¯Ùˆ)\b'
            ],
            UserIntention.CHECK_STATUS: [
                # English patterns
                r'\b(status|stats|level|health|money)\b',
                r'\b(profile|account|balance|score)\b',
                # Persian patterns
                r'\b(ÙˆØ¶Ø¹ÛŒØª|Ø¢Ù…Ø§Ø±|Ø³Ø·Ø­|Ø³Ù„Ø§Ù…ØªÛŒ|Ù¾ÙˆÙ„)\b',
                r'\b(Ù¾Ø±ÙˆÙØ§ÛŒÙ„|Ø­Ø³Ø§Ø¨|Ù…ÙˆØ¬ÙˆØ¯ÛŒ|Ø§Ù…ØªÛŒØ§Ø²)\b'
            ],
            UserIntention.ATTACK_PLAYER: [
                # English patterns
                r'\b(attack|fight|kill|shoot|hit)\b',
                r'\b(weapon|gun|sword|bomb)\b',
                # Persian patterns
                r'\b(Ø­Ù…Ù„Ù‡|Ø¨Ú©Ø´|ØªÛŒØ±Ø§Ù†Ø¯Ø§Ø²ÛŒ|Ø²Ø¯Ù†|Ù†Ø¨Ø±Ø¯)\b',
                r'\b(Ø³Ù„Ø§Ø­|ØªÙÙ†Ú¯|Ø´Ù…Ø´ÛŒØ±|Ø¨Ù…Ø¨)\b'
            ],
            UserIntention.BUY_ITEM: [
                # English patterns
                r'\b(buy|purchase|shop|store|get)\b',
                r'\b(item|weapon|medicine|upgrade)\b',
                # Persian patterns
                r'\b(Ø®Ø±ÛŒØ¯|Ø¨Ø®Ø±|ÙØ±ÙˆØ´Ú¯Ø§Ù‡|Ø¯Ú©Ø§Ù†|Ø¨Ú¯ÛŒØ±)\b',
                r'\b(Ø¢ÛŒØªÙ…|Ø³Ù„Ø§Ø­|Ø¯Ø§Ø±Ùˆ|Ø§Ø±ØªÙ‚Ø§)\b'
            ],
            UserIntention.SOCIAL_CHAT: [
                # English patterns
                r'\b(hello|hi|good|nice|thanks|bye)\b',
                r'\b(how are you|what\'s up|see you)\b',
                # Persian patterns  
                r'\b(Ø³Ù„Ø§Ù…|Ø¯Ø±ÙˆØ¯|Ø®ÙˆØ¨ÛŒ|Ú†Ø·ÙˆØ±ÛŒ|Ù…Ù…Ù†ÙˆÙ†|Ø®Ø¯Ø§Ø­Ø§ÙØ¸)\b',
                r'\b(Ø­Ø§Ù„Øª Ú†Ø·ÙˆØ±Ù‡|Ú†Ù‡ Ø®Ø¨Ø±|ØªØ§ Ø¨Ø¹Ø¯)\b'
            ]
        }
        
        # Ø§Ù„Ú¯ÙˆÙ‡Ø§ÛŒ ØªØ­Ù„ÛŒÙ„ Ø§Ø­Ø³Ø§Ø³Ø§Øª - Sentiment Analysis Patterns
        self.sentiment_patterns = {
            MessageSentiment.POSITIVE: [
                # English
                r'\b(good|great|awesome|nice|love|like|happy|excellent)\b',
                r'\b(thank|thanks|cool|amazing|wonderful|fantastic)\b',
                # Persian
                r'\b(Ø®ÙˆØ¨|Ø¹Ø§Ù„ÛŒ|ÙÙˆÙ‚â€ŒØ§Ù„Ø¹Ø§Ø¯Ù‡|Ù‚Ø´Ù†Ú¯|Ø¯ÙˆØ³Øª Ø¯Ø§Ø±Ù…|Ø®ÙˆØ´Ø­Ø§Ù„|Ù…Ù…Ù†ÙˆÙ†)\b',
                r'\b(Ø¨Ø§Ø­Ø§Ù„|Ø¬Ø§Ù„Ø¨|Ú©ÙˆÙ„|Ù…Ø±Ø³ÛŒ|ØªØ´Ú©Ø±|Ø´Ú¯ÙØªâ€ŒØ§Ù†Ú¯ÛŒØ²)\b'
            ],
            MessageSentiment.NEGATIVE: [
                # English
                r'\b(bad|terrible|awful|hate|suck|worst|annoying)\b',
                r'\b(stupid|dumb|boring|useless|disappointed)\b',
                # Persian
                r'\b(Ø¨Ø¯|Ø§ÙØªØ¶Ø§Ø­|Ù…ØªÙ†ÙØ±|Ú©Ø³Ù„â€ŒÚ©Ù†Ù†Ø¯Ù‡|Ø§Ø­Ù…Ù‚|Ø¨ÛŒØ®ÙˆØ¯)\b',
                r'\b(Ù†Ø§Ø§Ù…ÛŒØ¯|Ø¶Ø§ÛŒØ¹|Ù…Ø²Ø®Ø±Ù|Ú©ÙˆØ¯Ù†|Ø¨ÛŒâ€ŒÙØ§ÛŒØ¯Ù‡)\b'
            ],
            MessageSentiment.AGGRESSIVE: [
                # English
                r'\b(kill|die|shut up|idiot|damn|hell|fuck)\b',
                r'\b(destroy|murder|violence|angry|mad|rage)\b',
                # Persian
                r'\b(Ø¨Ú©Ø´|Ø¨Ù…ÛŒØ±|Ø®ÙÙ‡ Ø´Ùˆ|Ø§Ø­Ù…Ù‚|Ù„Ø¹Ù†Øª|Ø¬Ù‡Ù†Ù…)\b',
                r'\b(Ù†Ø§Ø¨ÙˆØ¯|Ù‚ØªÙ„|Ø®Ø´Ù…Ú¯ÛŒÙ†|Ø¹ØµØ¨Ø§Ù†ÛŒ|Ø®Ø´Ù…)\b'
            ],
            MessageSentiment.FRIENDLY: [
                # English
                r'\b(friend|buddy|pal|mate|welcome|join)\b',
                r'\b(together|team|group|community|help)\b',
                # Persian
                r'\b(Ø¯ÙˆØ³Øª|Ø±ÙÛŒÙ‚|Ù‡Ù…Ø±Ø§Ù‡|Ø®ÙˆØ´ Ø¢Ù…Ø¯ÛŒ|Ø¨Ù¾ÛŒÙˆÙ†Ø¯)\b',
                r'\b(Ø¨Ø§ Ù‡Ù…|ØªÛŒÙ…|Ú¯Ø±ÙˆÙ‡|Ø¬Ø§Ù…Ø¹Ù‡|Ú©Ù…Ú©)\b'
            ]
        }
        
        # Ú©Ù„Ù…Ø§Øª Ú©Ù„ÛŒØ¯ÛŒ Ù…Ù‡Ù… - Important Keywords
        self.important_keywords = {
            'bot_mentions': [
                'trump', 'bot', 'Ø±Ø¨Ø§Øª', 'ØªØ±Ø§Ù…Ù¾'
            ],
            'game_terms': [
                'game', 'play', 'attack', 'weapon', 'Ø¨Ø§Ø²ÛŒ', 'Ø­Ù…Ù„Ù‡', 'Ø³Ù„Ø§Ø­'
            ],
            'help_terms': [
                'help', 'how', 'guide', 'Ú©Ù…Ú©', 'Ø±Ø§Ù‡Ù†Ù…Ø§', 'Ú†Ø·ÙˆØ±'
            ]
        }
    
    async def analyze_message(self, context: MessageContext) -> MessageContext:
        """ØªØ­Ù„ÛŒÙ„ Ø¬Ø§Ù…Ø¹ Ù¾ÛŒØ§Ù… - Comprehensive message analysis"""
        try:
            if not context.message.text:
                return context
            
            message_text = context.message.text.lower()
            
            # ØªØ´Ø®ÛŒØµ Ù‚ØµØ¯ - Intent Recognition
            context.intention = await self._detect_intention(message_text)
            
            # ØªØ­Ù„ÛŒÙ„ Ø§Ø­Ø³Ø§Ø³Ø§Øª - Sentiment Analysis
            context.sentiment = await self._analyze_sentiment(message_text)
            
            # Ù…Ø­Ø§Ø³Ø¨Ù‡ Ø§Ù…ØªÛŒØ§Ø² Ø§Ø·Ù…ÛŒÙ†Ø§Ù† - Calculate Confidence Score
            context.confidence_score = await self._calculate_confidence(
                message_text, context.intention, context.sentiment
            )
            
            # Ø«Ø¨Øª Ø¢Ù†Ø§Ù„ÛŒØªÛŒÚ©Ø³ - Log Analytics
            await self._log_analysis(context)
            
            return context
            
        except Exception as e:
            logger.error(f"Error analyzing message: {e}")
            return context
    
    async def _detect_intention(self, text: str) -> UserIntention:
        """ØªØ´Ø®ÛŒØµ Ù‚ØµØ¯ Ú©Ø§Ø±Ø¨Ø± - Detect user intention"""
        intention_scores = {}
        
        for intention, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                score += matches
            intention_scores[intention] = score
        
        # Ù¾ÛŒØ¯Ø§ Ú©Ø±Ø¯Ù† Ø¨ÛŒØ´ØªØ±ÛŒÙ† Ø§Ù…ØªÛŒØ§Ø² - Find highest score
        if intention_scores and max(intention_scores.values()) > 0:
            return max(intention_scores, key=intention_scores.get)
        
        return UserIntention.UNKNOWN
    
    async def _analyze_sentiment(self, text: str) -> MessageSentiment:
        """ØªØ­Ù„ÛŒÙ„ Ø§Ø­Ø³Ø§Ø³Ø§Øª - Analyze sentiment"""
        sentiment_scores = {}
        
        for sentiment, patterns in self.sentiment_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                score += matches
            sentiment_scores[sentiment] = score
        
        # Ù¾ÛŒØ¯Ø§ Ú©Ø±Ø¯Ù† Ø¨ÛŒØ´ØªØ±ÛŒÙ† Ø§Ù…ØªÛŒØ§Ø² - Find highest score
        if sentiment_scores and max(sentiment_scores.values()) > 0:
            return max(sentiment_scores, key=sentiment_scores.get)
        
        return MessageSentiment.NEUTRAL
    
    async def _calculate_confidence(
        self, 
        text: str, 
        intention: UserIntention, 
        sentiment: MessageSentiment
    ) -> float:
        """Ù…Ø­Ø§Ø³Ø¨Ù‡ Ø§Ù…ØªÛŒØ§Ø² Ø§Ø·Ù…ÛŒÙ†Ø§Ù† - Calculate confidence score"""
        base_score = 0.5
        
        # Ø§ÙØ²Ø§ÛŒØ´ Ø§Ù…ØªÛŒØ§Ø² Ø¨Ø± Ø§Ø³Ø§Ø³ ØªØ·Ø¨ÛŒÙ‚ Ø§Ù„Ú¯Ùˆ - Increase score based on pattern matching
        if intention != UserIntention.UNKNOWN:
            base_score += 0.3
        
        if sentiment != MessageSentiment.NEUTRAL:
            base_score += 0.2
        
        # Ø§ÙØ²Ø§ÛŒØ´ Ø§Ù…ØªÛŒØ§Ø² Ø¨Ø±Ø§ÛŒ Ú©Ù„Ù…Ø§Øª Ú©Ù„ÛŒØ¯ÛŒ - Increase score for keywords
        for category, keywords in self.important_keywords.items():
            for keyword in keywords:
                if keyword in text.lower():
                    base_score += 0.05
        
        return min(base_score, 1.0)
    
    async def _log_analysis(self, context: MessageContext):
        """Ø«Ø¨Øª Ù†ØªØ§ÛŒØ¬ ØªØ­Ù„ÛŒÙ„ - Log analysis results"""
        analytics_logger.info(
            f"Message analysis - User: {context.user_id}, "
            f"Intention: {context.intention.value if context.intention else 'unknown'}, "
            f"Sentiment: {context.sentiment.value if context.sentiment else 'neutral'}, "
            f"Confidence: {context.confidence_score:.2f}"
        )

# Ù†Ù…ÙˆÙ†Ù‡ Ø³Ø±Ø§Ø³Ø±ÛŒ ØªØ­Ù„ÛŒÙ„â€ŒÚ¯Ø± - Global analyzer instance
message_analyzer = MessageAnalyzer()

# =============================================================================
# Ø³ÛŒØ³ØªÙ… Ù…Ø¯ÛŒØ±ÛŒØª Ø§Ù†ØªÛŒâ€ŒØ§Ø³Ù¾Ù… - Anti-Spam Management System  
# =============================================================================

class AntiSpamManager:
    """Ù…Ø¯ÛŒØ± Ø§Ù†ØªÛŒâ€ŒØ§Ø³Ù¾Ù… Ù¾ÛŒØ´Ø±ÙØªÙ‡ - Advanced Anti-Spam Manager"""
    
    def __init__(self):
        self.user_message_history: Dict[int, deque] = defaultdict(lambda: deque(maxlen=20))
        self.spam_scores: Dict[int, float] = defaultdict(float)
        self.blocked_users: Dict[int, datetime] = {}
        
        # ØªÙ†Ø¸ÛŒÙ…Ø§Øª Ø§Ù†ØªÛŒâ€ŒØ§Ø³Ù¾Ù… - Anti-spam settings
        self.max_messages_per_minute = 10
        self.max_duplicate_messages = 3
        self.spam_threshold = 0.8
        self.block_duration = timedelta(minutes=30)
        
        # Ø§Ù„Ú¯ÙˆÙ‡Ø§ÛŒ Ø§Ø³Ù¾Ù… - Spam patterns
        self.spam_patterns = [
            r'(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)',  # URLs
            r'(@[a-zA-Z0-9_]+)',  # Mentions
            r'(\b[A-Z]{5,}\b)',  # All caps words
            r'(.)\1{5,}',  # Repeated characters
            r'(ðŸ’°|ðŸ’µ|ðŸ’¸|ðŸ¤‘|ðŸ’²)',  # Money emojis
        ]
    
    async def check_message_spam(self, context: MessageContext) -> bool:
        """Ø¨Ø±Ø±Ø³ÛŒ Ø§Ø³Ù¾Ù… Ø¨ÙˆØ¯Ù† Ù¾ÛŒØ§Ù… - Check if message is spam"""
        try:
            user_id = context.user_id
            message_text = context.message.text or ""
            current_time = datetime.now()
            
            # Ø¨Ø±Ø±Ø³ÛŒ Ú©Ø§Ø±Ø¨Ø±Ø§Ù† Ù…Ø³Ø¯ÙˆØ¯ Ø´Ø¯Ù‡ - Check blocked users
            if user_id in self.blocked_users:
                if current_time - self.blocked_users[user_id] < self.block_duration:
                    return True  # Still blocked
                else:
                    del self.blocked_users[user_id]  # Unblock user
            
            # Ø§ÙØ²ÙˆØ¯Ù† Ù¾ÛŒØ§Ù… Ø¨Ù‡ ØªØ§Ø±ÛŒØ®Ú†Ù‡ - Add message to history
            self.user_message_history[user_id].append({
                'text': message_text,
                'timestamp': current_time,
                'hash': hashlib.md5(message_text.encode()).hexdigest()
            })
            
            # Ù…Ø­Ø§Ø³Ø¨Ù‡ Ø§Ù…ØªÛŒØ§Ø² Ø§Ø³Ù¾Ù… - Calculate spam score
            spam_score = await self._calculate_spam_score(user_id, message_text, current_time)
            self.spam_scores[user_id] = spam_score
            
            # Ø¨Ø±Ø±Ø³ÛŒ Ø¢Ø³ØªØ§Ù†Ù‡ Ø§Ø³Ù¾Ù… - Check spam threshold
            if spam_score >= self.spam_threshold:
                self.blocked_users[user_id] = current_time
                security_logger.warning(f"User {user_id} blocked for spam (score: {spam_score:.2f})")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking spam: {e}")
            return False
    
    async def _calculate_spam_score(self, user_id: int, message_text: str, current_time: datetime) -> float:
        """Ù…Ø­Ø§Ø³Ø¨Ù‡ Ø§Ù…ØªÛŒØ§Ø² Ø§Ø³Ù¾Ù… - Calculate spam score"""
        score = 0.0
        user_history = self.user_message_history[user_id]
        
        # Ø¨Ø±Ø±Ø³ÛŒ ÙØ±Ú©Ø§Ù†Ø³ Ù¾ÛŒØ§Ù… - Check message frequency
        recent_messages = [
            msg for msg in user_history 
            if (current_time - msg['timestamp']).seconds < 60
        ]
        if len(recent_messages) > self.max_messages_per_minute:
            score += 0.4
        
        # Ø¨Ø±Ø±Ø³ÛŒ Ù¾ÛŒØ§Ù…â€ŒÙ‡Ø§ÛŒ ØªÚ©Ø±Ø§Ø±ÛŒ - Check duplicate messages
        message_hash = hashlib.md5(message_text.encode()).hexdigest()
        duplicate_count = sum(1 for msg in user_history if msg['hash'] == message_hash)
        if duplicate_count > self.max_duplicate_messages:
            score += 0.3
        
        # Ø¨Ø±Ø±Ø³ÛŒ Ø§Ù„Ú¯ÙˆÙ‡Ø§ÛŒ Ø§Ø³Ù¾Ù… - Check spam patterns
        for pattern in self.spam_patterns:
            if re.search(pattern, message_text, re.IGNORECASE):
                score += 0.1
        
        # Ø¨Ø±Ø±Ø³ÛŒ Ø·ÙˆÙ„ Ù¾ÛŒØ§Ù… - Check message length
        if len(message_text) > 500:
            score += 0.1
        
        # Ø¨Ø±Ø±Ø³ÛŒ Ø§ÛŒÙ…ÙˆØ¬ÛŒâ€ŒÙ‡Ø§ÛŒ Ù…Ø´Ú©ÙˆÚ© - Check suspicious emojis
        if len(re.findall(r'[ðŸŽ°ðŸŽ²ðŸ”žðŸ’°ðŸ’µðŸ’¸ðŸ¤‘ðŸ’²]', message_text)) > 3:
            score += 0.2
        
        return min(score, 1.0)
    
    def get_user_spam_score(self, user_id: int) -> float:
        """Ø¯Ø±ÛŒØ§ÙØª Ø§Ù…ØªÛŒØ§Ø² Ø§Ø³Ù¾Ù… Ú©Ø§Ø±Ø¨Ø± - Get user spam score"""
        return self.spam_scores.get(user_id, 0.0)
    
    def is_user_blocked(self, user_id: int) -> bool:
        """Ø¨Ø±Ø±Ø³ÛŒ Ù…Ø³Ø¯ÙˆØ¯ Ø¨ÙˆØ¯Ù† Ú©Ø§Ø±Ø¨Ø± - Check if user is blocked"""
        if user_id not in self.blocked_users:
            return False
        
        if datetime.now() - self.blocked_users[user_id] >= self.block_duration:
            del self.blocked_users[user_id]
            return False
        
        return True

# Ù†Ù…ÙˆÙ†Ù‡ Ø³Ø±Ø§Ø³Ø±ÛŒ Ù…Ø¯ÛŒØ± Ø§Ù†ØªÛŒâ€ŒØ§Ø³Ù¾Ù… - Global anti-spam manager instance
anti_spam_manager = AntiSpamManager()

# =============================================================================
# Ø³ÛŒØ³ØªÙ… Ù¾Ø§Ø³Ø®â€ŒÚ¯ÙˆÛŒÛŒ Ù‡ÙˆØ´Ù…Ù†Ø¯ - Intelligent Response System
# =============================================================================

class SmartResponseSystem:
    """Ø³ÛŒØ³ØªÙ… Ù¾Ø§Ø³Ø®â€ŒÚ¯ÙˆÛŒÛŒ Ù‡ÙˆØ´Ù…Ù†Ø¯ - Smart Response System"""
    
    def __init__(self):
        # Ù¾Ø§Ø³Ø®â€ŒÙ‡Ø§ÛŒ Ù‡ÙˆØ´Ù…Ù†Ø¯ Ø¨Ø± Ø§Ø³Ø§Ø³ Ù‚ØµØ¯ - Smart responses based on intention
        self.intention_responses = {
            UserIntention.PLAY_GAME: {
                'fa': [
                    "ðŸŽ® Ø¹Ø§Ù„ÛŒ! Ø¢Ù…Ø§Ø¯Ù‡â€ŒØ§ÛŒ Ø¨Ø±Ø§ÛŒ Ø´Ø±ÙˆØ¹ Ù†Ø¨Ø±Ø¯ØŸ\n\nØ§Ø² /start Ø¨Ø±Ø§ÛŒ Ø´Ø±ÙˆØ¹ Ø¨Ø§Ø²ÛŒ Ø§Ø³ØªÙØ§Ø¯Ù‡ Ú©Ù†!",
                    "âš”ï¸ ØªØ±Ø§Ù…Ù¾ Ø¨Ø§Øª Ø¢Ù…Ø§Ø¯Ù‡ Ù†Ø¨Ø±Ø¯ Ø§Ø³Øª!\n\nØ¨Ø§ /attack Ù…ÛŒâ€ŒØªÙˆÙ†ÛŒ Ø¨Ù‡ Ø¯ÛŒÚ¯Ø±Ø§Ù† Ø­Ù…Ù„Ù‡ Ú©Ù†ÛŒ!",
                    "ðŸš€ Ø¨ÛŒØ§ Ø´Ø±ÙˆØ¹ Ú©Ù†ÛŒÙ…! Ø¨Ø§ /help Ø±Ø§Ù‡Ù†Ù…Ø§ÛŒ Ú©Ø§Ù…Ù„ Ø±Ùˆ Ø¨Ø¨ÛŒÙ†.",
                    "ðŸ’ª Ø¢Ù…Ø§Ø¯Ù‡ Ø¨Ø±Ø§ÛŒ Ø§Ú©Ø´Ù†ØŸ Ø¨Ø§ /shop Ø³Ù„Ø§Ø­ Ø¨Ø®Ø± Ùˆ Ù‚Ø¯Ø±ØªØª Ø±Ùˆ Ø§ÙØ²Ø§ÛŒØ´ Ø¨Ø¯Ù‡!"
                ],
                'en': [
                    "ðŸŽ® Great! Ready to start the battle?\n\nUse /start to begin playing!",
                    "âš”ï¸ Trump Bot is ready for battle!\n\nUse /attack to attack others!",
                    "ðŸš€ Let's get started! Check /help for complete guide.",
                    "ðŸ’ª Ready for action? Buy weapons with /shop and boost your power!"
                ]
            },
            UserIntention.GET_HELP: {
                'fa': [
                    "ðŸ“š Ø­ØªÙ…Ø§Ù‹ Ú©Ù…Ú©Øª Ù…ÛŒâ€ŒÚ©Ù†Ù…!\n\nØ§Ø² /help Ø¨Ø±Ø§ÛŒ Ø±Ø§Ù‡Ù†Ù…Ø§ÛŒ Ú©Ø§Ù…Ù„ Ø§Ø³ØªÙØ§Ø¯Ù‡ Ú©Ù†.",
                    "ðŸ¤ Ø¯Ø± Ø®Ø¯Ù…ØªÙ…! Ú†Ù‡ Ø³ÙˆØ§Ù„ÛŒ Ø¯Ø§Ø±ÛŒØŸ\n\n/help - Ø±Ø§Ù‡Ù†Ù…Ø§ÛŒ Ú©Ø§Ù…Ù„\n/status - ÙˆØ¶Ø¹ÛŒØª\n/shop - ÙØ±ÙˆØ´Ú¯Ø§Ù‡",
                    "ðŸ’¡ Ø³ÙˆØ§Ù„ Ø¯Ø§Ø±ÛŒØŸ Ù…Ù† Ø§ÛŒÙ†Ø¬Ø§Ù… ØªØ§ Ú©Ù…Ú©Øª Ú©Ù†Ù…!\n\nØ¨Ø§ /help Ù‡Ù…Ù‡ Ú†ÛŒØ² Ø±Ùˆ ÛŒØ§Ø¯ Ø¨Ú¯ÛŒØ±.",
                    "ðŸŽ¯ Ú†Ù‡ Ú©Ø§Ø±ÛŒ Ø¨Ø±Ø§Øª Ø§Ù†Ø¬Ø§Ù… Ø¨Ø¯Ù…ØŸ\n\nØ§Ø² Ù…Ù†ÙˆÛŒ /start Ù…ÛŒâ€ŒØªÙˆÙ†ÛŒ Ù‡Ù…Ù‡ Ø§Ù…Ú©Ø§Ù†Ø§Øª Ø±Ùˆ Ø¨Ø¨ÛŒÙ†ÛŒ."
                ],
                'en': [
                    "ðŸ“š Sure, I'll help you!\n\nUse /help for complete guidance.",
                    "ðŸ¤ At your service! What questions do you have?\n\n/help - Complete guide\n/status - Status\n/shop - Shop",
                    "ðŸ’¡ Have questions? I'm here to help!\n\nLearn everything with /help.",
                    "ðŸŽ¯ What can I do for you?\n\nCheck all features in /start menu."
                ]
            },
            UserIntention.CHECK_STATUS: {
                'fa': [
                    "ðŸ“Š Ø¨ÛŒØ§ ÙˆØ¶Ø¹ÛŒØªØª Ø±Ùˆ Ø¨Ø±Ø±Ø³ÛŒ Ú©Ù†ÛŒÙ…!\n\nØ§Ø² /status Ø§Ø³ØªÙØ§Ø¯Ù‡ Ú©Ù†.",
                    "ðŸ’ª Ù…ÛŒâ€ŒØ®ÙˆØ§ÛŒ Ø¨Ø¨ÛŒÙ†ÛŒ Ú†Ù‚Ø¯Ø± Ù‚Ø¯Ø±ØªÙ…Ù†Ø¯ÛŒØŸ\n\n/status - ÙˆØ¶Ø¹ÛŒØª Ú©Ù„ÛŒ\n/stats - Ø¢Ù…Ø§Ø± Ú©Ø§Ù…Ù„",
                    "ðŸŽ¯ Ø¢Ù…Ø§Ø±Ù‡Ø§Øª Ø±Ùˆ Ø¨Ø¨ÛŒÙ†!\n\nØ¨Ø§ /status ÙˆØ¶Ø¹ÛŒØª ÙØ¹Ù„ÛŒØª Ø±Ùˆ Ú†Ú© Ú©Ù†.",
                    "ðŸ“ˆ Ù¾ÛŒØ´Ø±ÙØªØª Ø±Ùˆ Ø¨Ø±Ø±Ø³ÛŒ Ú©Ù†!\n\n/status Ø¨Ø±Ø§ÛŒ Ø¯ÛŒØ¯Ù† Ø³Ù„Ø§Ù…ØªÛŒ Ùˆ Ù¾ÙˆÙ„\n/stats Ø¨Ø±Ø§ÛŒ Ø¢Ù…Ø§Ø± Ú©Ø§Ù…Ù„"
                ],
                'en': [
                    "ðŸ“Š Let's check your status!\n\nUse /status command.",
                    "ðŸ’ª Want to see how powerful you are?\n\n/status - General status\n/stats - Complete statistics",
                    "ðŸŽ¯ Check your stats!\n\nUse /status to see current condition.",
                    "ðŸ“ˆ Review your progress!\n\n/status for health and money\n/stats for complete statistics"
                ]
            },
            UserIntention.ATTACK_PLAYER: {
                'fa': [
                    "âš”ï¸ Ø¢Ù…Ø§Ø¯Ù‡ Ù†Ø¨Ø±Ø¯ØŸ!\n\nØ¨Ø§ /attack ÛŒÚ© Ù‡Ø¯Ù Ø§Ù†ØªØ®Ø§Ø¨ Ú©Ù† Ùˆ Ø­Ù…Ù„Ù‡ Ú©Ù†!",
                    "ðŸ’¥ Ø²Ù…Ø§Ù† Ù†Ø¨Ø±Ø¯ ÙØ±Ø§ Ø±Ø³ÛŒØ¯Ù‡!\n\nØ§Ø² /attack Ø§Ø³ØªÙØ§Ø¯Ù‡ Ú©Ù† ØªØ§ Ø¨Ù‡ Ø¯Ø´Ù…Ù†Ø§Ù†Øª Ø­Ù…Ù„Ù‡ Ú©Ù†ÛŒ.",
                    "ðŸ”« Ø³Ù„Ø§Ø­â€ŒÙ‡Ø§Øª Ø¢Ù…Ø§Ø¯Ù‡ØŸ\n\nØ¨Ø§ /weapons Ø³Ù„Ø§Ø­â€ŒÙ‡Ø§Øª Ø±Ùˆ Ø¨Ø¨ÛŒÙ† Ùˆ Ø¨Ø§ /attack Ø­Ù…Ù„Ù‡ Ú©Ù†!",
                    "âš¡ Ø§Ù†Ø±Ú˜ÛŒ Ù†Ø¨Ø±Ø¯ Ø±Ùˆ Ø­Ø³ Ù…ÛŒâ€ŒÚ©Ù†Ù…!\n\nØ¨Ø§ /attack Ù…Ø®Ø§Ù„ÙØª Ø±Ùˆ Ø´Ø±ÙˆØ¹ Ú©Ù†!"
                ],
                'en': [
                    "âš”ï¸ Ready for battle?!\n\nUse /attack to select a target and attack!",
                    "ðŸ’¥ Battle time has come!\n\nUse /attack to strike your enemies.",
                    "ðŸ”« Are your weapons ready?\n\nCheck /weapons and attack with /attack!",
                    "âš¡ I can feel the battle energy!\n\nStart the fight with /attack!"
                ]
            },
            UserIntention.BUY_ITEM: {
                'fa': [
                    "ðŸ›’ ÙˆÙ‚Øª Ø®Ø±ÛŒØ¯ Ø±Ø³ÛŒØ¯Ù‡!\n\nØ¨Ø§ /shop Ø¨Ø¨ÛŒÙ† Ú†Ù‡ Ú†ÛŒØ²Ù‡Ø§ÛŒ Ø¨Ø§Ø­Ø§Ù„ÛŒ Ø¯Ø§Ø±ÛŒÙ…!",
                    "ðŸ’° Ù¾ÙˆÙ„Øª Ú©Ø§ÙÛŒÙ‡ØŸ\n\nØ§Ø² /shop Ø¨Ø±Ø§ÛŒ Ø®Ø±ÛŒØ¯ Ø³Ù„Ø§Ø­ Ùˆ Ø¢ÛŒØªÙ… Ø§Ø³ØªÙØ§Ø¯Ù‡ Ú©Ù†.",
                    "ðŸŽ¯ Ù…ÛŒâ€ŒØ®ÙˆØ§ÛŒ Ù‚Ø¯Ø±ØªØª Ø±Ùˆ Ø§ÙØ²Ø§ÛŒØ´ Ø¨Ø¯ÛŒ?\n\nØ¨Ø±Ùˆ /shop Ùˆ Ø¨Ù‡ØªØ±ÛŒÙ†â€ŒÙ‡Ø§ Ø±Ùˆ Ø¨Ø®Ø±!",
                    "âš¡ Ù†ÛŒØ§Ø² Ø¨Ù‡ ØªØ¬Ù‡ÛŒØ²Ø§Øª Ø¨Ù‡ØªØ±ØŸ\n\nÙØ±ÙˆØ´Ú¯Ø§Ù‡ /shop Ù…Ù†ØªØ¸Ø±ØªÙ‡!"
                ],
                'en': [
                    "ðŸ›’ Shopping time!\n\nCheck /shop to see what cool stuff we have!",
                    "ðŸ’° Got enough money?\n\nUse /shop to buy weapons and items.",
                    "ðŸŽ¯ Want to boost your power?\n\nGo to /shop and buy the best items!",
                    "âš¡ Need better equipment?\n\nThe /shop is waiting for you!"
                ]
            },
            UserIntention.SOCIAL_CHAT: {
                'fa': [
                    "ðŸ˜Š Ø³Ù„Ø§Ù…! Ú†Ù‡ Ø­Ø§Ù„ Ø®ÙˆØ¨ÛŒ Ø¯Ø§Ø±ÛŒ!\n\nÙ…ÛŒâ€ŒØ®ÙˆØ§ÛŒ ÛŒÙ‡ Ø¨Ø§Ø²ÛŒ Ú©Ù†ÛŒÙ…ØŸ",
                    "ðŸ¤— Ø¯ÙˆØ³Øª Ø¯Ø§Ø´ØªÙ†ÛŒ! Ø®ÙˆØ´ Ø¢Ù…Ø¯ÛŒ!\n\nØ¨Ø±Ø§ÛŒ Ø´Ø±ÙˆØ¹ Ø§Ø² /start Ø§Ø³ØªÙØ§Ø¯Ù‡ Ú©Ù†.",
                    "ðŸ‘‹ Ú†Ù‡ Ø®Ø¨Ø±ØŸ Ø§Ù…ÛŒØ¯ÙˆØ§Ø±Ù… Ø­Ø§Ù„Øª Ø®ÙˆØ¨ Ø¨Ø§Ø´Ù‡!\n\nÛŒÙ‡ Ø¨Ø§Ø²ÛŒ Ø®ÙÙ† Ø¯Ø§Ø±ÛŒÙ… Ø§ÛŒÙ†Ø¬Ø§!",
                    "ðŸŒŸ Ø³Ù„Ø§Ù… Ú¯Ù„! Ú†Ø·ÙˆØ±ÛŒØŸ\n\nØ¨ÛŒØ§ Ø¨Ø§ ØªØ±Ø§Ù…Ù¾ Ø¨Ø§Øª Ø³Ø±Ú¯Ø±Ù… Ø´ÛŒÙ…!"
                ],
                'en': [
                    "ðŸ˜Š Hello! You seem to be in a good mood!\n\nWant to play a game?",
                    "ðŸ¤— Lovely! Welcome!\n\nUse /start to begin.",
                    "ðŸ‘‹ What's up? Hope you're doing well!\n\nWe have a cool game here!",
                    "ðŸŒŸ Hey there! How are you?\n\nLet's have fun with Trump Bot!"
                ]
            }
        }
        
        # Ù¾Ø§Ø³Ø®â€ŒÙ‡Ø§ÛŒ Ø¨Ø± Ø§Ø³Ø§Ø³ Ø§Ø­Ø³Ø§Ø³Ø§Øª - Responses based on sentiment
        self.sentiment_responses = {
            MessageSentiment.POSITIVE: {
                'fa': [
                    "ðŸ˜Š Ø®ÙˆØ´Ø­Ø§Ù„Ù… Ú©Ù‡ Ø­Ø§Ù„ Ø®ÙˆØ¨ÛŒ Ø¯Ø§Ø±ÛŒ!",
                    "ðŸŒŸ Ø§Ù†Ø±Ú˜ÛŒ Ù…Ø«Ø¨ØªØª ÙÙˆÙ‚â€ŒØ§Ù„Ø¹Ø§Ø¯Ù‡Ù‡!",
                    "ðŸŽ‰ Ø¹Ø§Ù„ÛŒÙ‡! Ù‡Ù…ÛŒÙ† Ø·ÙˆØ± Ø§Ø¯Ø§Ù…Ù‡ Ø¨Ø¯Ù‡!",
                    "ðŸ’« Ø¨Ø§ Ø§ÛŒÙ† Ø§Ù†Ø±Ú˜ÛŒ Ø­ØªÙ…Ø§Ù‹ Ø¨Ø±Ù†Ø¯Ù‡ Ù…ÛŒâ€ŒØ´ÛŒ!"
                ],
                'en': [
                    "ðŸ˜Š Glad you're feeling good!",
                    "ðŸŒŸ Your positive energy is amazing!",
                    "ðŸŽ‰ Awesome! Keep it up!",
                    "ðŸ’« With this energy you'll definitely win!"
                ]
            },
            MessageSentiment.NEGATIVE: {
                'fa': [
                    "ðŸ˜” Ù†Ø§Ø±Ø§Ø­ØªÛŒØŸ Ø´Ø§ÛŒØ¯ ÛŒÙ‡ Ø¨Ø§Ø²ÛŒ Ø­Ø§Ù„Øª Ø±Ùˆ Ø¨Ù‡ØªØ± Ú©Ù†Ù‡!",
                    "ðŸ¤— Ù†Ú¯Ø±Ø§Ù† Ù†Ø¨Ø§Ø´ØŒ Ù‡Ù…Ù‡ Ú†ÛŒØ² Ø¯Ø±Ø³Øª Ù…ÛŒØ´Ù‡!",
                    "ðŸ’ª Ø¨Ø§ ÛŒÙ‡ Ù¾ÛŒØ±ÙˆØ²ÛŒ ØªÙˆ Ø¨Ø§Ø²ÛŒ Ø­Ø§Ù„Øª Ø¨Ù‡ØªØ± Ù…ÛŒØ´Ù‡!",
                    "ðŸŒˆ Ø¨Ø¹Ø¯ Ø§Ø² Ø¨Ø§Ø±Ø§Ù†ØŒ Ø¢ÙØªØ§Ø¨ Ù…ÛŒØ§Ø¯!"
                ],
                'en': [
                    "ðŸ˜” Feeling down? Maybe a game will cheer you up!",
                    "ðŸ¤— Don't worry, everything will be fine!",
                    "ðŸ’ª A victory in the game will make you feel better!",
                    "ðŸŒˆ After rain comes sunshine!"
                ]
            },
            MessageSentiment.AGGRESSIVE: {
                'fa': [
                    "ðŸ˜® Ø§Ù†Ú¯Ø§Ø± Ø¹ØµØ¨Ø§Ù†ÛŒ Ù‡Ø³ØªÛŒ! Ø¨ÛŒØ§ Ø§Ù†Ø±Ú˜ÛŒØª Ø±Ùˆ ØªÙˆ Ø¨Ø§Ø²ÛŒ Ø®Ø§Ù„ÛŒ Ú©Ù†!",
                    "âš”ï¸ Ø§ÛŒÙ† Ø§Ù†Ø±Ú˜ÛŒ Ø±Ùˆ Ù…ÛŒâ€ŒØªÙˆÙ†ÛŒ ØªÙˆ Ù†Ø¨Ø±Ø¯ Ø§Ø³ØªÙØ§Ø¯Ù‡ Ú©Ù†ÛŒ!",
                    "ðŸ”¥ Ø¢Ø±ÙˆÙ… Ø¨Ø§Ø´! Ø¨Ø§Ø²ÛŒ ÛŒÙ‡ Ø±Ø§Ù‡ Ø®ÙˆØ¨ Ø¨Ø±Ø§ÛŒ ØªØ®Ù„ÛŒÙ‡ Ø§Ù†Ø±Ú˜ÛŒÙ‡!",
                    "ðŸŽ¯ Ø¨Ø¬Ø§ÛŒ Ø¹ØµØ¨Ø§Ù†ÛŒØªØŒ Ø¨ÛŒØ§ ØªÙˆÛŒ Ø¨Ø§Ø²ÛŒ Ù‚Ø¯Ø±Øª Ù†Ø´ÙˆÙ† Ø¨Ø¯ÛŒ!"
                ],
                'en': [
                    "ðŸ˜® You seem angry! Let's channel that energy into the game!",
                    "âš”ï¸ You can use this energy in battle!",
                    "ðŸ”¥ Calm down! Gaming is a great way to release energy!",
                    "ðŸŽ¯ Instead of anger, show your power in the game!"
                ]
            },
            MessageSentiment.FRIENDLY: {
                'fa': [
                    "ðŸ¤— Ú†Ù‚Ø¯Ø± Ù…Ù‡Ø±Ø¨ÙˆÙ†ÛŒ! Ø¯ÙˆØ³Øª Ø¯Ø§Ø±Ù… Ø¨Ø§Ù‡Ø§Øª Ø­Ø±Ù Ø¨Ø²Ù†Ù…!",
                    "ðŸ˜ Ú†Ù‡ Ø¢Ø¯Ù… Ø®ÙˆØ¨ÛŒ Ù‡Ø³ØªÛŒ!",
                    "ðŸŒŸ Ø¨Ø§ Ø§ÛŒÙ† Ø¯ÙˆØ³ØªÛŒØŒ Ù‚Ø·Ø¹Ø§Ù‹ ØªÙˆ ØªÛŒÙ… Ø¨Ø±Ù†Ø¯Ù‡â€ŒÙ‡Ø§ Ø¬Ø§Øª Ø¯Ø§Ø±ÛŒ!",
                    "ðŸ’ Ù…Ù…Ù†ÙˆÙ† Ú©Ù‡ Ø§Ù†Ù‚Ø¯Ø± Ù…ÙˆØ¯Ø¨ Ùˆ Ù…Ù‡Ø±Ø¨ÙˆÙ†ÛŒ!"
                ],
                'en': [
                    "ðŸ¤— You're so kind! I love talking with you!",
                    "ðŸ˜ What a good person you are!",
                    "ðŸŒŸ With this friendliness, you definitely belong in the winning team!",
                    "ðŸ’ Thank you for being so polite and kind!"
                ]
            }
        }
        
        # Ù¾Ø§Ø³Ø®â€ŒÙ‡Ø§ÛŒ Ù¾ÛŒØ´â€ŒÙØ±Ø¶ - Default responses
        self.default_responses = {
            'fa': [
                "ðŸ¤– Ø³Ù„Ø§Ù…! Ù…Ù† ØªØ±Ø§Ù…Ù¾ Ø¨Ø§Øª Ù‡Ø³ØªÙ…!\n\nØ¨Ø±Ø§ÛŒ Ø´Ø±ÙˆØ¹ Ø§Ø² /start Ø§Ø³ØªÙØ§Ø¯Ù‡ Ú©Ù†.",
                "ðŸ‘‹ Ú†Ø·ÙˆØ±ÛŒØŸ Ø¢Ù…Ø§Ø¯Ù‡â€ŒØ§ÛŒ Ø¨Ø±Ø§ÛŒ ÛŒÙ‡ Ø¨Ø§Ø²ÛŒ Ø¨Ø§Ø­Ø§Ù„ØŸ\n\n/help Ø±Ùˆ Ø¨Ø²Ù† ØªØ§ Ù‡Ù…Ù‡ Ú†ÛŒØ² Ø±Ùˆ ÛŒØ§Ø¯ Ø¨Ú¯ÛŒØ±ÛŒ!",
                "ðŸŽ® ØªØ±Ø§Ù…Ù¾ Ø¨Ø§Øª Ø¯Ø± Ø®Ø¯Ù…ØªØªÙ‡!\n\nØ¨Ø§ /start Ø¨Ø§Ø²ÛŒ Ø±Ùˆ Ø´Ø±ÙˆØ¹ Ú©Ù†!",
                "âš¡ Ø§Ù†Ø±Ú˜ÛŒ Ø¯Ø§Ø±ÛŒØŸ Ø¨ÛŒØ§ Ù†Ø¨Ø±Ø¯ Ú©Ù†ÛŒÙ…!\n\nØ§Ø² /attack Ø¨Ø±Ø§ÛŒ Ø­Ù…Ù„Ù‡ Ø§Ø³ØªÙØ§Ø¯Ù‡ Ú©Ù†!"
            ],
            'en': [
                "ðŸ¤– Hello! I'm Trump Bot!\n\nUse /start to begin.",
                "ðŸ‘‹ How are you? Ready for a cool game?\n\nTry /help to learn everything!",
                "ðŸŽ® Trump Bot at your service!\n\nStart playing with /start!",
                "âš¡ Got energy? Let's battle!\n\nUse /attack to strike!"
            ]
        }
    
    async def generate_smart_response(self, context: MessageContext) -> Optional[str]:
        """ØªÙˆÙ„ÛŒØ¯ Ù¾Ø§Ø³Ø® Ù‡ÙˆØ´Ù…Ù†Ø¯ - Generate smart response"""
        try:
            lang = context.user_lang
            
            # Ù¾Ø§Ø³Ø® Ø¨Ø± Ø§Ø³Ø§Ø³ Ù‚ØµØ¯ - Response based on intention
            if context.intention and context.intention in self.intention_responses:
                responses = self.intention_responses[context.intention].get(lang, 
                           self.intention_responses[context.intention]['en'])
                if responses:
                    return random.choice(responses)
            
            # Ù¾Ø§Ø³Ø® Ø¨Ø± Ø§Ø³Ø§Ø³ Ø§Ø­Ø³Ø§Ø³Ø§Øª - Response based on sentiment
            if context.sentiment and context.sentiment in self.sentiment_responses:
                responses = self.sentiment_responses[context.sentiment].get(lang,
                           self.sentiment_responses[context.sentiment]['en'])
                if responses:
                    base_response = random.choice(responses)
                    
                    # Ø§ÙØ²ÙˆØ¯Ù† Ù¾ÛŒØ´Ù†Ù‡Ø§Ø¯ Ø¯Ø³ØªÙˆØ± - Add command suggestion
                    if lang == 'fa':
                        suggestion = "\n\nÙ…ÛŒâ€ŒØ®ÙˆØ§ÛŒ Ø¨Ø§Ø²ÛŒ Ú©Ù†ÛŒÙ…ØŸ /start Ø±Ùˆ Ø¨Ø²Ù†!"
                    else:
                        suggestion = "\n\nWant to play? Try /start!"
                    
                    return base_response + suggestion
            
            # Ù¾Ø§Ø³Ø® Ù¾ÛŒØ´â€ŒÙØ±Ø¶ - Default response
            default_responses = self.default_responses.get(lang, self.default_responses['en'])
            return random.choice(default_responses)
            
        except Exception as e:
            logger.error(f"Error generating smart response: {e}")
            return None

# Ù†Ù…ÙˆÙ†Ù‡ Ø³Ø±Ø§Ø³Ø±ÛŒ Ø³ÛŒØ³ØªÙ… Ù¾Ø§Ø³Ø® Ù‡ÙˆØ´Ù…Ù†Ø¯ - Global smart response system instance
smart_response_system = SmartResponseSystem()

# =============================================================================
# Ù…Ø¯ÛŒØ±ÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡â€ŒÙ‡Ø§ÛŒ Ù¾ÛŒØ§Ù… Ù¾ÛŒØ´Ø±ÙØªÙ‡ - Enhanced Message Handlers
# =============================================================================

async def handle_new_chat_members(message: Message, bot: AsyncTeleBot, db_manager: DBManager):
    """
    Ù…Ø¯ÛŒØ±ÛŒØª Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ø¹Ø¶ÙˆÛŒØª Ø§Ø¹Ø¶Ø§ÛŒ Ø¬Ø¯ÛŒØ¯
    Enhanced handling of new chat members
    
    Args:
        message (Message): Message object containing new member info
        bot (AsyncTeleBot): Bot instance
        db_manager (DBManager): Database manager instance
    """
    if not message.new_chat_members:
        return
    
    try:
        # Ø¯Ø±ÛŒØ§ÙØª Ø²Ø¨Ø§Ù† Ú¯Ø±ÙˆÙ‡ - Get chat language
        chat_lang = await db_manager.get_chat_language(message.chat.id)
        if not chat_lang:
            chat_lang = "en"
        
        # Ø¨Ø±Ø±Ø³ÛŒ Ø§ÛŒÙ†Ú©Ù‡ Ø¢ÛŒØ§ Ø®ÙˆØ¯ Ø±Ø¨Ø§Øª Ø§Ø¶Ø§ÙÙ‡ Ø´Ø¯Ù‡ - Check if bot itself was added
        bot_info = await bot.get_me()
        for new_member in message.new_chat_members:
            if new_member.id == bot_info.id:
                await handle_bot_added_to_group(message, bot, db_manager, chat_lang)
                return
        
        # Ù…Ø¯ÛŒØ±ÛŒØª Ø§Ø¹Ø¶Ø§ÛŒ Ø¬Ø¯ÛŒØ¯ - Handle new members
        for new_member in message.new_chat_members:
            await handle_new_member_welcome(message, bot, db_manager, new_member, chat_lang)
            
        # Ø«Ø¨Øª Ø¢Ù…Ø§Ø± - Log statistics
        await log_new_members_event(message, db_manager)
        
    except Exception as e:
        logger.error(f"Error handling new chat members: {e}")

async def handle_bot_added_to_group(message: Message, bot: AsyncTeleBot, db_manager: DBManager, chat_lang: str):
    """Ù…Ø¯ÛŒØ±ÛŒØª Ø§Ø¶Ø§ÙÙ‡ Ø´Ø¯Ù† Ø±Ø¨Ø§Øª Ø¨Ù‡ Ú¯Ø±ÙˆÙ‡ - Handle bot added to group"""
    try:
        # Ø«Ø¨Øª Ú¯Ø±ÙˆÙ‡ Ø¯Ø± Ù¾Ø§ÛŒÚ¯Ø§Ù‡ Ø¯Ø§Ø¯Ù‡ - Register chat in database
        await db_manager.ensure_chat_exists(
            chat_id=message.chat.id,
            title=message.chat.title or "Unknown Group",
            chat_type=message.chat.type,
            language=chat_lang
        )
        
        # Ù¾ÛŒØ§Ù… Ø®ÙˆØ´Ø§Ù…Ø¯Ú¯ÙˆÛŒÛŒ Ù¾ÛŒØ´Ø±ÙØªÙ‡ - Advanced welcome message
        if chat_lang == "fa":
            welcome_text = "ðŸ¤– **Ø³Ù„Ø§Ù…! Ù…Ù† ØªØ±Ø§Ù…Ù¾ Ø¨Ø§Øª Ù‡Ø³ØªÙ…!** ðŸŽ®\n\n"
            welcome_text += "ðŸŒŸ **Ù…Ù† ÛŒÚ© Ø¨Ø§Ø²ÛŒ Ú¯Ø±ÙˆÙ‡ÛŒ Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ùˆ Ø³Ø±Ú¯Ø±Ù…â€ŒÚ©Ù†Ù†Ø¯Ù‡ Ù‡Ø³ØªÙ… Ú©Ù‡ Ø´Ø§Ù…Ù„:**\n\n"
            welcome_text += "âš”ï¸ â€¢ **Ø³ÛŒØ³ØªÙ… Ù†Ø¨Ø±Ø¯ Ù¾ÛŒØ´Ø±ÙØªÙ‡** - Ø¨Ø§ Ø³Ù„Ø§Ø­â€ŒÙ‡Ø§ÛŒ Ù…Ø®ØªÙ„Ù Ø¨Ù‡ ÛŒÚ©Ø¯ÛŒÚ¯Ø± Ø­Ù…Ù„Ù‡ Ú©Ù†ÛŒØ¯\n"
            welcome_text += "ðŸ† â€¢ **Ø³ÛŒØ³ØªÙ… Ø§Ù…ØªÛŒØ§Ø²Ø¯Ù‡ÛŒ** - Ù…Ø¯Ø§Ù„â€ŒÙ‡Ø§ Ùˆ Ø§Ù…ØªÛŒØ§Ø²Ø§Øª Ú©Ø³Ø¨ Ú©Ù†ÛŒØ¯\n"
            welcome_text += "ðŸ›’ â€¢ **ÙØ±ÙˆØ´Ú¯Ø§Ù‡ Ù¾ÛŒØ´Ø±ÙØªÙ‡** - Ø³Ù„Ø§Ø­â€ŒÙ‡Ø§ Ùˆ Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ÛŒ Ù‚Ø¯Ø±ØªÙ…Ù†Ø¯ Ø¨Ø®Ø±ÛŒØ¯\n"
            welcome_text += "ðŸ“Š â€¢ **Ø¢Ù…Ø§Ø± Ú©Ø§Ù…Ù„** - Ù¾ÛŒØ´Ø±ÙØª Ø®ÙˆØ¯ Ø±Ø§ Ø¯Ù†Ø¨Ø§Ù„ Ú©Ù†ÛŒØ¯\n"
            welcome_text += "ðŸŒ â€¢ **Ù¾Ø´ØªÛŒØ¨Ø§Ù†ÛŒ Ú©Ø§Ù…Ù„ Ø§Ø² Ø²Ø¨Ø§Ù† ÙØ§Ø±Ø³ÛŒ** - Ø±Ø§Ø¨Ø· Ú©Ø§Ø±Ø¨Ø±ÛŒ Ú©Ø§Ù…Ù„Ø§Ù‹ ÙØ§Ø±Ø³ÛŒ\n\n"
            welcome_text += "ðŸš€ **Ø¨Ø±Ø§ÛŒ Ø´Ø±ÙˆØ¹:**\n"
            welcome_text += "ðŸ“š `/help` - Ø±Ø§Ù‡Ù†Ù…Ø§ÛŒ Ú©Ø§Ù…Ù„\n"
            welcome_text += "ðŸŽ® `/start` - Ø´Ø±ÙˆØ¹ Ø¨Ø§Ø²ÛŒ\n"
            welcome_text += "ðŸ“Š `/status` - ÙˆØ¶Ø¹ÛŒØª Ø´Ù…Ø§\n"
            welcome_text += "âš”ï¸ `/attack` - Ø­Ù…Ù„Ù‡ Ø¨Ù‡ Ø¯ÛŒÚ¯Ø±Ø§Ù†\n\n"
            welcome_text += "ðŸŽ¯ **Ø¢Ù…Ø§Ø¯Ù‡â€ŒØ§ÛŒØ¯ Ø¨Ø±Ø§ÛŒ Ù…Ø§Ø¬Ø±Ø§Ø¬ÙˆÛŒÛŒØŸ**"
        else:
            welcome_text = "ðŸ¤– **Hello! I'm Trump Bot!** ðŸŽ®\n\n"
            welcome_text += "ðŸŒŸ **I'm an advanced and entertaining group game featuring:**\n\n"
            welcome_text += "âš”ï¸ â€¢ **Advanced Battle System** - Attack each other with various weapons\n"
            welcome_text += "ðŸ† â€¢ **Scoring System** - Earn medals and points\n"
            welcome_text += "ðŸ›’ â€¢ **Advanced Shop** - Buy powerful weapons and items\n"
            welcome_text += "ðŸ“Š â€¢ **Complete Statistics** - Track your progress\n"
            welcome_text += "ðŸŒ â€¢ **Full Persian Language Support** - Complete Persian interface\n\n"
            welcome_text += "ðŸš€ **To get started:**\n"
            welcome_text += "ðŸ“š `/help` - Complete guide\n"
            welcome_text += "ðŸŽ® `/start` - Start playing\n"
            welcome_text += "ðŸ“Š `/status` - Your status\n"
            welcome_text += "âš”ï¸ `/attack` - Attack others\n\n"
            welcome_text += "ðŸŽ¯ **Ready for adventure?**"
        
        # Ø§ÛŒØ¬Ø§Ø¯ Ú©ÛŒØ¨ÙˆØ±Ø¯ Ù¾ÛŒØ´Ø±ÙØªÙ‡ - Create advanced keyboard
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        
        if chat_lang == "fa":
            keyboard.add(
                types.InlineKeyboardButton("ðŸŽ® Ø´Ø±ÙˆØ¹ Ø¨Ø§Ø²ÛŒ", callback_data="go:start"),
                types.InlineKeyboardButton("ðŸ“š Ø±Ø§Ù‡Ù†Ù…Ø§ÛŒ Ú©Ø§Ù…Ù„", callback_data="go:help")
            )
            keyboard.add(
                types.InlineKeyboardButton("âš™ï¸ ØªÙ†Ø¸ÛŒÙ…Ø§Øª", callback_data="go:settings"),
                types.InlineKeyboardButton("ðŸŒ ØªØºÛŒÛŒØ± Ø²Ø¨Ø§Ù†", callback_data="lang:en")
            )
            keyboard.add(
                types.InlineKeyboardButton("ðŸ“Š Ø¢Ù…Ø§Ø± Ø±Ø¨Ø§Øª", callback_data="do:bot_stats"),
                types.InlineKeyboardButton("ðŸ†˜ Ù¾Ø´ØªÛŒØ¨Ø§Ù†ÛŒ", callback_data="go:support")
            )
        else:
            keyboard.add(
                types.InlineKeyboardButton("ðŸŽ® Start Game", callback_data="go:start"),
                types.InlineKeyboardButton("ðŸ“š Complete Guide", callback_data="go:help")
            )
            keyboard.add(
                types.InlineKeyboardButton("âš™ï¸ Settings", callback_data="go:settings"),
                types.InlineKeyboardButton("ðŸŒ ÙØ§Ø±Ø³ÛŒ", callback_data="lang:fa")
            )
            keyboard.add(
                types.InlineKeyboardButton("ðŸ“Š Bot Stats", callback_data="do:bot_stats"),
                types.InlineKeyboardButton("ðŸ†˜ Support", callback_data="go:support")
            )
        
        # Ø§Ø±Ø³Ø§Ù„ Ù¾ÛŒØ§Ù… Ø®ÙˆØ´Ø§Ù…Ø¯Ú¯ÙˆÛŒÛŒ - Send welcome message
        await bot.send_message(
            message.chat.id,
            welcome_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        # Ø«Ø¨Øª Ù„Ø§Ú¯ - Log event
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
    """Ø®ÙˆØ´Ø§Ù…Ø¯Ú¯ÙˆÛŒÛŒ Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ø¨Ù‡ Ø¹Ø¶Ùˆ Ø¬Ø¯ÛŒØ¯ - Advanced welcome for new member"""
    try:
        # Ø§Ø·Ù…ÛŒÙ†Ø§Ù† Ø§Ø² ÙˆØ¬ÙˆØ¯ Ú©Ø§Ø±Ø¨Ø± Ø¯Ø± Ù¾Ø§ÛŒÚ¯Ø§Ù‡ Ø¯Ø§Ø¯Ù‡ - Ensure user exists in database
        await ensure_player(message.chat.id, new_member, db_manager)
        
        # Ø¯Ø±ÛŒØ§ÙØª Ø²Ø¨Ø§Ù† ØªØ±Ø¬ÛŒØ­ÛŒ Ú©Ø§Ø±Ø¨Ø± - Get user preferred language
        user_lang = await get_lang(message.chat.id, new_member.id, db_manager)
        if not user_lang:
            user_lang = chat_lang
        
        # ØªÙˆÙ„ÛŒØ¯ Ù¾ÛŒØ§Ù… Ø®ÙˆØ´Ø§Ù…Ø¯Ú¯ÙˆÛŒÛŒ Ø´Ø®ØµÛŒâ€ŒØ³Ø§Ø²ÛŒ Ø´Ø¯Ù‡ - Generate personalized welcome message
        welcome_messages = await generate_welcome_messages(new_member, user_lang, db_manager)
        selected_welcome = random.choice(welcome_messages)
        
        # Ø§ÛŒØ¬Ø§Ø¯ Ú©ÛŒØ¨ÙˆØ±Ø¯ Ø®ÙˆØ´Ø§Ù…Ø¯Ú¯ÙˆÛŒÛŒ - Create welcome keyboard
        keyboard = await create_welcome_keyboard(user_lang)
        
        # Ø§Ø±Ø³Ø§Ù„ Ù¾ÛŒØ§Ù… Ø®ÙˆØ´Ø§Ù…Ø¯Ú¯ÙˆÛŒÛŒ - Send welcome message
        await bot.send_message(
            message.chat.id,
            selected_welcome,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        # Ø«Ø¨Øª Ø¢Ù…Ø§Ø± Ú©Ø§Ø±Ø¨Ø± Ø¬Ø¯ÛŒØ¯ - Log new user statistics
        await db_manager.log_new_user_join(message.chat.id, new_member.id, user_lang)
        
        logger.info(f"New member welcomed: {new_member.id} in chat {message.chat.id}")
        
    except Exception as e:
        logger.error(f"Error welcoming new member: {e}")

async def generate_welcome_messages(user: User, lang: str, db_manager: DBManager) -> List[str]:
    """ØªÙˆÙ„ÛŒØ¯ Ù¾ÛŒØ§Ù…â€ŒÙ‡Ø§ÛŒ Ø®ÙˆØ´Ø§Ù…Ø¯Ú¯ÙˆÛŒÛŒ - Generate welcome messages"""
    user_name = user.first_name
    
    if lang == "fa":
        messages = [
            f"ðŸŽ‰ **Ø³Ù„Ø§Ù… {user_name} Ø¹Ø²ÛŒØ²!**\n\n"
            f"Ø®ÙˆØ´ Ø¢Ù…Ø¯ÛŒ Ø¨Ù‡ Ø¯Ù†ÛŒØ§ÛŒ Ù‡ÛŒØ¬Ø§Ù†â€ŒØ§Ù†Ú¯ÛŒØ² ØªØ±Ø§Ù…Ù¾ Ø¨Ø§Øª! ðŸš€\n\n"
            f"Ø§ÛŒÙ†Ø¬Ø§ Ù…ÛŒâ€ŒØªÙˆÙ†ÛŒ:\n"
            f"âš”ï¸ Ø¨Ø§ Ø¯ÛŒÚ¯Ø±Ø§Ù† Ù†Ø¨Ø±Ø¯ Ú©Ù†ÛŒ\n"
            f"ðŸ›’ Ø³Ù„Ø§Ø­â€ŒÙ‡Ø§ÛŒ Ù‚Ø¯Ø±ØªÙ…Ù†Ø¯ Ø¨Ø®Ø±ÛŒ\n"
            f"ðŸ† Ù…Ø¯Ø§Ù„â€ŒÙ‡Ø§ Ùˆ Ø§Ù…ØªÛŒØ§Ø² Ú©Ø³Ø¨ Ú©Ù†ÛŒ\n"
            f"ðŸ“Š Ø¢Ù…Ø§Ø±Øª Ø±Ùˆ Ø¯Ù†Ø¨Ø§Ù„ Ú©Ù†ÛŒ\n\n"
            f"ðŸŽ® **Ø¨Ø±Ø§ÛŒ Ø´Ø±ÙˆØ¹ `/start` Ø±Ùˆ Ø¨Ø²Ù†!**",
            
            f"ðŸ‘‹ **{user_name} Ø¬Ø§Ù† Ø®ÙˆØ´ Ø§ÙˆÙ…Ø¯ÛŒ!**\n\n"
            f"ðŸŽ¯ Ø¢Ù…Ø§Ø¯Ù‡ Ø¨Ø±Ø§ÛŒ Ù…Ø§Ø¬Ø±Ø§Ø¬ÙˆÛŒÛŒ Ø¬Ø¯ÛŒØ¯ØŸ\n"
            f"ØªØ±Ø§Ù…Ù¾ Ø¨Ø§Øª ÛŒÙ‡ Ø¨Ø§Ø²ÛŒ Ú¯Ø±ÙˆÙ‡ÛŒ ÙÙˆÙ‚â€ŒØ§Ù„Ø¹Ø§Ø¯Ù‡ Ø§Ø³Øª Ú©Ù‡ ØªÙˆØ´ Ù…ÛŒâ€ŒØªÙˆÙ†ÛŒ:\n\n"
            f"ðŸ’ª Ù‚Ø¯Ø±ØªØª Ø±Ùˆ Ù†Ø´ÙˆÙ† Ø¨Ø¯ÛŒ\n"
            f"ðŸ”« Ø¨Ø§ Ø³Ù„Ø§Ø­â€ŒÙ‡Ø§ÛŒ Ù…Ø®ØªÙ„Ù Ù†Ø¨Ø±Ø¯ Ú©Ù†ÛŒ\n"
            f"ðŸ’° Ù¾ÙˆÙ„ Ùˆ Ø¢ÛŒØªÙ… Ø¬Ù…Ø¹ Ú©Ù†ÛŒ\n"
            f"ðŸŒŸ Ø¨Ù‡ Ù„ÛŒØ¯Ø±Ø¨ÙˆØ±Ø¯ Ø¨Ø±Ø³ÛŒ\n\n"
            f"ðŸ“š `/help` Ø¨Ø±Ø§ÛŒ Ø±Ø§Ù‡Ù†Ù…Ø§ÛŒ Ú©Ø§Ù…Ù„!",
            
            f"ðŸŒŸ **{user_name} ÙˆØ§Ø±Ø¯ Ù…ÛŒØ¯Ø§Ù† Ø´Ø¯!**\n\n"
            f"ðŸ”¥ Ø¢Ù…Ø§Ø¯Ù‡â€ŒØ§ÛŒ Ø¨Ø±Ø§ÛŒ Ù†Ø¨Ø±Ø¯ØŸ\n"
            f"Ø§ÛŒÙ†Ø¬Ø§ Ù‚Ø§Ù†ÙˆÙ† Ø¬Ù†Ú¯Ù„Ù‡! Ù‡Ø± Ú©ÛŒ Ù‚Ø¯Ø±ØªÙ…Ù†Ø¯ØªØ± Ø¨Ø§Ø´Ù‡ Ø¨Ø±Ù†Ø¯Ù‡ Ø§Ø³Øª! ðŸ’ª\n\n"
            f"ðŸš€ **Ú†ÛŒØ²Ù‡Ø§ÛŒÛŒ Ú©Ù‡ Ù…ÛŒâ€ŒØªÙˆÙ†ÛŒ Ø§Ù†Ø¬Ø§Ù… Ø¨Ø¯ÛŒ:**\n"
            f"âš”ï¸ `/attack` - Ø­Ù…Ù„Ù‡ Ø¨Ù‡ Ø¯Ø´Ù…Ù†Ø§Ù†\n"
            f"ðŸ›¡ï¸ `/defend` - Ø¯ÙØ§Ø¹ Ø§Ø² Ø®ÙˆØ¯Øª\n"
            f"ðŸ›’ `/shop` - Ø®Ø±ÛŒØ¯ ØªØ¬Ù‡ÛŒØ²Ø§Øª\n"
            f"ðŸ“Š `/status` - ÙˆØ¶Ø¹ÛŒØª ÙØ¹Ù„ÛŒ\n\n"
            f"ðŸŽ¯ **Ø¨ÛŒØ§ Ø´Ø±ÙˆØ¹ Ú©Ù†ÛŒÙ…!**"
        ]
    else:
        messages = [
            f"ðŸŽ‰ **Hello dear {user_name}!**\n\n"
            f"Welcome to the exciting world of Trump Bot! ðŸš€\n\n"
            f"Here you can:\n"
            f"âš”ï¸ Battle with others\n"
            f"ðŸ›’ Buy powerful weapons\n"
            f"ðŸ† Earn medals and points\n"
            f"ðŸ“Š Track your statistics\n\n"
            f"ðŸŽ® **Hit `/start` to begin!**",
            
            f"ðŸ‘‹ **Welcome {user_name}!**\n\n"
            f"ðŸŽ¯ Ready for a new adventure?\n"
            f"Trump Bot is an amazing group game where you can:\n\n"
            f"ðŸ’ª Show your strength\n"
            f"ðŸ”« Battle with various weapons\n"
            f"ðŸ’° Collect money and items\n"
            f"ðŸŒŸ Reach the leaderboard\n\n"
            f"ðŸ“š Try `/help` for complete guide!",
            
            f"ðŸŒŸ **{user_name} entered the battlefield!**\n\n"
            f"ðŸ”¥ Ready for battle?\n"
            f"This is the law of the jungle! The strongest wins! ðŸ’ª\n\n"
            f"ðŸš€ **Things you can do:**\n"
            f"âš”ï¸ `/attack` - Attack enemies\n"
            f"ðŸ›¡ï¸ `/defend` - Defend yourself\n"
            f"ðŸ›’ `/shop` - Buy equipment\n"
            f"ðŸ“Š `/status` - Current status\n\n"
            f"ðŸŽ¯ **Let's get started!**"
        ]
    
    return messages

async def create_welcome_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    """Ø§ÛŒØ¬Ø§Ø¯ Ú©ÛŒØ¨ÙˆØ±Ø¯ Ø®ÙˆØ´Ø§Ù…Ø¯Ú¯ÙˆÛŒÛŒ - Create welcome keyboard"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    if lang == "fa":
        keyboard.add(
            types.InlineKeyboardButton("ðŸŽ® Ø´Ø±ÙˆØ¹ Ø¨Ø§Ø²ÛŒ", callback_data="go:start"),
            types.InlineKeyboardButton("ðŸ“š Ø±Ø§Ù‡Ù†Ù…Ø§", callback_data="go:help")
        )
        keyboard.add(
            types.InlineKeyboardButton("ðŸ“Š ÙˆØ¶Ø¹ÛŒØª Ù…Ù†", callback_data="go:status"),
            types.InlineKeyboardButton("ðŸ›’ ÙØ±ÙˆØ´Ú¯Ø§Ù‡", callback_data="go:shop")
        )
        keyboard.add(
            types.InlineKeyboardButton("âš”ï¸ Ø­Ù…Ù„Ù‡!", callback_data="go:attack"),
            types.InlineKeyboardButton("ðŸ† Ù„ÛŒØ¯Ø±Ø¨ÙˆØ±Ø¯", callback_data="go:leaderboard")
        )
    else:
        keyboard.add(
            types.InlineKeyboardButton("ðŸŽ® Start Game", callback_data="go:start"),
            types.InlineKeyboardButton("ðŸ“š Help", callback_data="go:help")
        )
        keyboard.add(
            types.InlineKeyboardButton("ðŸ“Š My Status", callback_data="go:status"),
            types.InlineKeyboardButton("ðŸ›’ Shop", callback_data="go:shop")
        )
        keyboard.add(
            types.InlineKeyboardButton("âš”ï¸ Attack!", callback_data="go:attack"),
            types.InlineKeyboardButton("ðŸ† Leaderboard", callback_data="go:leaderboard")
        )
    
    return keyboard

async def handle_left_chat_member(message: Message, bot: AsyncTeleBot, db_manager: DBManager):
    """
    Ù…Ø¯ÛŒØ±ÛŒØª Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ø®Ø±ÙˆØ¬ Ø§Ø¹Ø¶Ø§ Ø§Ø² Ú¯Ø±ÙˆÙ‡
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
        
        # Ø¨Ø±Ø±Ø³ÛŒ Ø§ÛŒÙ†Ú©Ù‡ Ø¢ÛŒØ§ Ø®ÙˆØ¯ Ø±Ø¨Ø§Øª Ø­Ø°Ù Ø´Ø¯Ù‡ - Check if bot itself was removed
        if left_member.id == bot_info.id:
            await handle_bot_removed_from_group(message, bot, db_manager)
            return
        
        # Ù…Ø¯ÛŒØ±ÛŒØª Ø®Ø±ÙˆØ¬ Ú©Ø§Ø±Ø¨Ø± Ø¹Ø§Ø¯ÛŒ - Handle normal user leaving
        await handle_user_left_group(message, bot, db_manager, left_member)
        
        # Ø«Ø¨Øª Ø¢Ù…Ø§Ø± - Log statistics
        await log_member_left_event(message, db_manager, left_member)
        
    except Exception as e:
        logger.error(f"Error handling left chat member: {e}")

async def handle_bot_removed_from_group(message: Message, bot: AsyncTeleBot, db_manager: DBManager):
    """Ù…Ø¯ÛŒØ±ÛŒØª Ø­Ø°Ù Ø±Ø¨Ø§Øª Ø§Ø² Ú¯Ø±ÙˆÙ‡ - Handle bot removed from group"""
    try:
        # Ø«Ø¨Øª Ù„Ø§Ú¯ Ø­Ø°Ù - Log removal
        logger.info(f"Bot removed from group {message.chat.id} ({message.chat.title})")
        
        # Ø¨Ù‡â€ŒØ±ÙˆØ²Ø±Ø³Ø§Ù†ÛŒ ÙˆØ¶Ø¹ÛŒØª Ú¯Ø±ÙˆÙ‡ Ø¯Ø± Ù¾Ø§ÛŒÚ¯Ø§Ù‡ Ø¯Ø§Ø¯Ù‡ - Update chat status in database
        await db_manager.update_chat_status(message.chat.id, "inactive")
        
        # Ø«Ø¨Øª Ø¢Ù…Ø§Ø± Ø­Ø°Ù - Log removal statistics
        await db_manager.log_bot_removal(message.chat.id, datetime.now())
        
        security_logger.info(f"Bot removed from chat {message.chat.id}")
        
    except Exception as e:
        logger.error(f"Error handling bot removal: {e}")

async def handle_user_left_group(message: Message, bot: AsyncTeleBot, db_manager: DBManager, left_member: User):
    """Ù…Ø¯ÛŒØ±ÛŒØª Ø®Ø±ÙˆØ¬ Ú©Ø§Ø±Ø¨Ø± Ø§Ø² Ú¯Ø±ÙˆÙ‡ - Handle user leaving group"""
    try:
        # Ø¯Ø±ÛŒØ§ÙØª Ø²Ø¨Ø§Ù† Ú¯Ø±ÙˆÙ‡ - Get chat language
        chat_lang = await db_manager.get_chat_language(message.chat.id) or "en"
        
        # Ø¨Ù‡â€ŒØ±ÙˆØ²Ø±Ø³Ø§Ù†ÛŒ ÙˆØ¶Ø¹ÛŒØª Ú©Ø§Ø±Ø¨Ø± - Update user status
        await db_manager.update_user_status(message.chat.id, left_member.id, "left")
        
        # Ø«Ø¨Øª Ø²Ù…Ø§Ù† Ø®Ø±ÙˆØ¬ - Log departure time
        await db_manager.log_user_departure(message.chat.id, left_member.id, datetime.now())
        
        # ØªÙˆÙ„ÛŒØ¯ Ù¾ÛŒØ§Ù… Ø®Ø¯Ø§Ø­Ø§ÙØ¸ÛŒ (Ø§Ø®ØªÛŒØ§Ø±ÛŒ) - Generate farewell message (optional)
        # Note: Many groups prefer not to announce departures to avoid spam
        
        logger.info(f"User {left_member.id} ({left_member.first_name}) left chat {message.chat.id}")
        
    except Exception as e:
        logger.error(f"Error handling user departure: {e}")

async def handle_telegram_stars_payment(message: Message, bot: AsyncTeleBot, db_manager: DBManager):
    """
    Ù…Ø¯ÛŒØ±ÛŒØª Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ù¾Ø±Ø¯Ø§Ø®Øªâ€ŒÙ‡Ø§ÛŒ Telegram Stars
    Enhanced Telegram Stars payment handling
    
    Args:
        message (Message): Message object containing payment info
        bot (AsyncTeleBot): Bot instance
        db_manager (DBManager): Database manager instance
    """
    try:
        # Ø¨Ø±Ø±Ø³ÛŒ ÙˆØ¬ÙˆØ¯ Ø§Ø·Ù„Ø§Ø¹Ø§Øª Ù¾Ø±Ø¯Ø§Ø®Øª - Check payment info existence
        if not message.successful_payment:
            logger.warning("Received payment message without payment info")
            return
        
        payment_info = message.successful_payment
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        # Ø¯Ø±ÛŒØ§ÙØª Ø²Ø¨Ø§Ù† Ú©Ø§Ø±Ø¨Ø± - Get user language
        user_lang = await get_lang(chat_id, user_id, db_manager)
        
        # Ù¾Ø±Ø¯Ø§Ø²Ø´ Ù¾Ø±Ø¯Ø§Ø®Øª Ù…ÙˆÙÙ‚ - Process successful payment
        await process_successful_stars_payment(message, bot, db_manager, payment_info, user_lang)
        
        # Ø«Ø¨Øª Ø¢Ù…Ø§Ø± Ù¾Ø±Ø¯Ø§Ø®Øª - Log payment statistics
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
    """Ù¾Ø±Ø¯Ø§Ø²Ø´ Ù¾Ø±Ø¯Ø§Ø®Øª Ù…ÙˆÙÙ‚ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ - Process successful stars payment"""
    try:
        # ÙˆØ§Ø±Ø¯ Ú©Ø±Ø¯Ù† Ù…Ø§Ú˜ÙˆÙ„ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ - Import stars module
        from src.commands.stars import handle_successful_stars_payment
        
        # Ù¾Ø±Ø¯Ø§Ø²Ø´ Ù¾Ø±Ø¯Ø§Ø®Øª - Process payment
        await handle_successful_stars_payment(message, bot, payment_info, db_manager)
        
        # Ø§Ø±Ø³Ø§Ù„ Ù¾ÛŒØ§Ù… ØªØ§ÛŒÛŒØ¯ Ù¾ÛŒØ´Ø±ÙØªÙ‡ - Send advanced confirmation message
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
    """Ø§Ø±Ø³Ø§Ù„ Ù¾ÛŒØ§Ù… ØªØ§ÛŒÛŒØ¯ Ù¾Ø±Ø¯Ø§Ø®Øª - Send payment confirmation"""
    try:
        stars_amount = payment_info.total_amount  # This should be the stars amount
        
        if user_lang == "fa":
            confirmation_text = f"âœ… **Ù¾Ø±Ø¯Ø§Ø®Øª Ù…ÙˆÙÙ‚!**\n\n"
            confirmation_text += f"ðŸ’« **Ù…Ù‚Ø¯Ø§Ø±:** {stars_amount} Ø³ØªØ§Ø±Ù‡ ØªÙ„Ú¯Ø±Ø§Ù…\n"
            confirmation_text += f"ðŸ§¾ **Ø´Ù†Ø§Ø³Ù‡ ØªØ±Ø§Ú©Ù†Ø´:** `{payment_info.telegram_payment_charge_id}`\n"
            confirmation_text += f"ðŸ“… **ØªØ§Ø±ÛŒØ®:** {datetime.now().strftime('%Y/%m/%d %H:%M')}\n\n"
            confirmation_text += f"ðŸŽ‰ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ Ø´Ù…Ø§ Ø¨Ø§ Ù…ÙˆÙÙ‚ÛŒØª Ø¨Ù‡ Ø­Ø³Ø§Ø¨ Ø§Ø¶Ø§ÙÙ‡ Ø´Ø¯Ù†Ø¯!"
        else:
            confirmation_text = f"âœ… **Payment Successful!**\n\n"
            confirmation_text += f"ðŸ’« **Amount:** {stars_amount} Telegram Stars\n"
            confirmation_text += f"ðŸ§¾ **Transaction ID:** `{payment_info.telegram_payment_charge_id}`\n"
            confirmation_text += f"ðŸ“… **Date:** {datetime.now().strftime('%Y/%m/%d %H:%M')}\n\n"
            confirmation_text += f"ðŸŽ‰ Your stars have been successfully added to your account!"
        
        # Ø§ÛŒØ¬Ø§Ø¯ Ú©ÛŒØ¨ÙˆØ±Ø¯ - Create keyboard
        keyboard = types.InlineKeyboardMarkup()
        if user_lang == "fa":
            keyboard.add(
                types.InlineKeyboardButton("ðŸ“Š Ù…ÙˆØ¬ÙˆØ¯ÛŒ Ù…Ù†", callback_data="go:status"),
                types.InlineKeyboardButton("ðŸ›’ ÙØ±ÙˆØ´Ú¯Ø§Ù‡", callback_data="go:shop")
            )
        else:
            keyboard.add(
                types.InlineKeyboardButton("ðŸ“Š My Balance", callback_data="go:status"),
                types.InlineKeyboardButton("ðŸ›’ Shop", callback_data="go:shop")
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
    Ù…Ø¯ÛŒØ±ÛŒØª Ú©Ø§Ù„Ø¨Ú©â€ŒÙ‡Ø§ÛŒ Ù¾Ø±Ø¯Ø§Ø®Øª Telegram Stars
    Handle Telegram Stars payment callbacks (web app data)
    
    Args:
        message (Message): Message object containing web app data
        bot (AsyncTeleBot): Bot instance
        db_manager (DBManager): Database manager instance
    """
    try:
        # Ø¨Ø±Ø±Ø³ÛŒ ÙˆØ¬ÙˆØ¯ Ø¯Ø§Ø¯Ù‡â€ŒÙ‡Ø§ÛŒ ÙˆØ¨ Ø§Ù¾ - Check web app data existence
        if not hasattr(message, 'web_app_data') or not message.web_app_data:
            return
        
        web_app_data = message.web_app_data.data
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        # Ø¨Ø±Ø±Ø³ÛŒ Ù†ÙˆØ¹ Ú©Ø§Ù„Ø¨Ú© - Check callback type
        if not web_app_data.startswith("stars_payment:"):
            return
        
        # Ø§Ø³ØªØ®Ø±Ø§Ø¬ Ø¯Ø§Ø¯Ù‡â€ŒÙ‡Ø§ÛŒ Ù¾Ø±Ø¯Ø§Ø®Øª - Extract payment data
        payment_data = web_app_data.replace("stars_payment:", "")
        
        # Ø¯Ø±ÛŒØ§ÙØª Ø²Ø¨Ø§Ù† Ú©Ø§Ø±Ø¨Ø± - Get user language
        user_lang = await get_lang(chat_id, user_id, db_manager)
        
        # Ù¾Ø±Ø¯Ø§Ø²Ø´ Ú©Ø§Ù„Ø¨Ú© Ù¾Ø±Ø¯Ø§Ø®Øª - Process payment callback
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
    """Ù¾Ø±Ø¯Ø§Ø²Ø´ Ú©Ø§Ù„Ø¨Ú© Ù¾Ø±Ø¯Ø§Ø®Øª Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ - Process stars payment callback"""
    try:
        # ÙˆØ§Ø±Ø¯ Ú©Ø±Ø¯Ù† Ù…Ø§Ú˜ÙˆÙ„ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ - Import stars module
        from src.commands.stars import handle_stars_payment_callback
        
        # Ù¾Ø±Ø¯Ø§Ø²Ø´ Ú©Ø§Ù„Ø¨Ú© - Process callback
        await handle_stars_payment_callback(message, bot, payment_data, db_manager)
        
    except ImportError:
        logger.warning("Stars module not available for callback processing")
        # Ø§Ø±Ø³Ø§Ù„ Ù¾ÛŒØ§Ù… Ø¬Ø§ÛŒÚ¯Ø²ÛŒÙ† - Send fallback message
        if user_lang == "fa":
            fallback_text = "âš ï¸ Ø³ÛŒØ³ØªÙ… Ù¾Ø±Ø¯Ø§Ø®Øª Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ Ø¯Ø± Ø­Ø§Ù„ Ø­Ø§Ø¶Ø± Ø¯Ø± Ø¯Ø³ØªØ±Ø³ Ù†ÛŒØ³Øª."
        else:
            fallback_text = "âš ï¸ Stars payment system is currently unavailable."
        
        await bot.send_message(message.chat.id, fallback_text)
    except Exception as e:
        logger.error(f"Error processing stars payment callback: {e}")

async def handle_regular_message(message: Message, bot: AsyncTeleBot, db_manager: DBManager):
    """
    Ù…Ø¯ÛŒØ±ÛŒØª Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ù¾ÛŒØ§Ù…â€ŒÙ‡Ø§ÛŒ Ù…ØªÙ†ÛŒ Ø¹Ø§Ø¯ÛŒ Ø¨Ø§ ØªØ­Ù„ÛŒÙ„ Ù‡ÙˆØ´Ù…Ù†Ø¯
    Enhanced handling of regular text messages with intelligent analysis
    
    Args:
        message (Message): Message object containing text
        bot (AsyncTeleBot): Bot instance
        db_manager (DBManager): Database manager instance
    """
    try:
        # Ø¨Ø±Ø±Ø³ÛŒ Ø§ÛŒÙ†Ú©Ù‡ Ù¾ÛŒØ§Ù… Ø¯Ø³ØªÙˆØ± Ù†ÛŒØ³Øª - Skip if this is a command
        if message.text and message.text.startswith('/'):
            return
        
        # Ø§Ø·Ù…ÛŒÙ†Ø§Ù† Ø§Ø² ÙˆØ¬ÙˆØ¯ Ú©Ø§Ø±Ø¨Ø± - Ensure user exists
        await ensure_player(message.chat.id, message.from_user, db_manager)
        
        # Ø§ÛŒØ¬Ø§Ø¯ Ø¨Ø§ÙØª Ù¾ÛŒØ§Ù… - Create message context
        context = await create_message_context(message, bot, db_manager)
        
        # Ø¨Ø±Ø±Ø³ÛŒ Ø§Ù†ØªÛŒâ€ŒØ§Ø³Ù¾Ù… - Check anti-spam
        if await anti_spam_manager.check_message_spam(context):
            await handle_spam_message(message, bot, db_manager, context)
            return
        
        # ØªØ­Ù„ÛŒÙ„ Ù¾ÛŒØ§Ù… - Analyze message
        context = await message_analyzer.analyze_message(context)
        
        # ØªÙˆÙ„ÛŒØ¯ Ù¾Ø§Ø³Ø® Ù‡ÙˆØ´Ù…Ù†Ø¯ - Generate smart response
        smart_response = await smart_response_system.generate_smart_response(context)
        
        # Ø¨Ø±Ø±Ø³ÛŒ Ù†ÛŒØ§Ø² Ø¨Ù‡ Ù¾Ø§Ø³Ø® - Check if response is needed
        should_respond = await should_bot_respond(context)
        
        if should_respond and smart_response:
            # Ø§ÛŒØ¬Ø§Ø¯ Ú©ÛŒØ¨ÙˆØ±Ø¯ - Create keyboard
            keyboard = await create_smart_response_keyboard(context)
            
            # Ø§Ø±Ø³Ø§Ù„ Ù¾Ø§Ø³Ø® - Send response
            await bot.reply_to(
                message,
                smart_response,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
            # Ø«Ø¨Øª ØªØ¹Ø§Ù…Ù„ - Log interaction
            await log_message_interaction(context, smart_response, db_manager)
        
        # Ø¨Ù‡â€ŒØ±ÙˆØ²Ø±Ø³Ø§Ù†ÛŒ Ø¢Ù…Ø§Ø± Ú©Ø§Ø±Ø¨Ø± - Update user statistics
        await update_user_message_stats(context, db_manager)
        
    except Exception as e:
        logger.error(f"Error handling regular message: {e}")
        await handle_message_processing_error(message, bot, db_manager, e)

async def create_message_context(message: Message, bot: AsyncTeleBot, db_manager: DBManager) -> MessageContext:
    """Ø§ÛŒØ¬Ø§Ø¯ Ø¨Ø§ÙØª Ù¾ÛŒØ§Ù… - Create message context"""
    try:
        # ØªØ´Ø®ÛŒØµ Ù†ÙˆØ¹ Ù¾ÛŒØ§Ù… - Detect message type
        message_type = detect_message_type(message)
        
        # Ø¯Ø±ÛŒØ§ÙØª Ø²Ø¨Ø§Ù†â€ŒÙ‡Ø§ - Get languages
        user_lang = await get_lang(message.chat.id, message.from_user.id, db_manager)
        chat_lang = await db_manager.get_chat_language(message.chat.id) or "en"
        
        # Ø¨Ø±Ø±Ø³ÛŒ Ø§Ø´Ø§Ø±Ù‡ Ø¨Ù‡ Ø±Ø¨Ø§Øª - Check bot mention
        bot_info = await bot.get_me()
        is_bot_mentioned = message.text and f"@{bot_info.username}" in message.text.lower()
        is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user.id == bot_info.id
        
        # ØªÙˆÙ„ÛŒØ¯ Ù‡Ø´ Ù¾ÛŒØ§Ù… - Generate message hash
        message_hash = hashlib.md5(
            f"{message.from_user.id}:{message.text or ''}:{message.date}".encode()
        ).hexdigest()
        
        # Ø§ÛŒØ¬Ø§Ø¯ Ø¨Ø§ÙØª - Create context
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
        # Ø¨Ø§Ø²Ú¯Ø´Øª Ø¨Ø§ÙØª Ù¾Ø§ÛŒÙ‡ - Return basic context
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
    """ØªØ´Ø®ÛŒØµ Ù†ÙˆØ¹ Ù¾ÛŒØ§Ù… - Detect message type"""
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
    """ØªØ¹ÛŒÛŒÙ† Ù†ÛŒØ§Ø² Ø¨Ù‡ Ù¾Ø§Ø³Ø® Ø±Ø¨Ø§Øª - Determine if bot should respond"""
    # Ù¾Ø§Ø³Ø® Ø¯Ø± Ú¯ÙØªÚ¯ÙˆÛŒ Ø®ØµÙˆØµÛŒ - Always respond in private chats
    if context.is_private:
        return True
    
    # Ù¾Ø§Ø³Ø® Ø¨Ù‡ Ø§Ø´Ø§Ø±Ù‡ Ù…Ø³ØªÙ‚ÛŒÙ… - Respond to direct mentions
    if context.is_bot_mentioned or context.is_reply_to_bot:
        return True
    
    # Ù¾Ø§Ø³Ø® Ø¨Ø± Ø§Ø³Ø§Ø³ Ù‚ØµØ¯ - Respond based on intention
    important_intentions = [
        UserIntention.GET_HELP,
        UserIntention.PLAY_GAME,
        UserIntention.SUPPORT
    ]
    
    if context.intention in important_intentions and context.confidence_score > 0.7:
        return True
    
    # Ù¾Ø§Ø³Ø® ØªØµØ§Ø¯ÙÛŒ Ø¯Ø± Ú¯Ø±ÙˆÙ‡â€ŒÙ‡Ø§ (ÛµÙª Ø§Ø­ØªÙ…Ø§Ù„) - Random response in groups (5% chance)
    if context.is_group and random.random() < 0.05:
        return True
    
    return False

async def create_smart_response_keyboard(context: MessageContext) -> types.InlineKeyboardMarkup:
    """Ø§ÛŒØ¬Ø§Ø¯ Ú©ÛŒØ¨ÙˆØ±Ø¯ Ù¾Ø§Ø³Ø® Ù‡ÙˆØ´Ù…Ù†Ø¯ - Create smart response keyboard"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    lang = context.user_lang
    
    # Ø¯Ú©Ù…Ù‡â€ŒÙ‡Ø§ÛŒ Ø¨Ø± Ø§Ø³Ø§Ø³ Ù‚ØµØ¯ - Buttons based on intention
    if context.intention == UserIntention.PLAY_GAME:
        if lang == "fa":
            keyboard.add(
                types.InlineKeyboardButton("ðŸŽ® Ø´Ø±ÙˆØ¹", callback_data="go:start"),
                types.InlineKeyboardButton("âš”ï¸ Ø­Ù…Ù„Ù‡", callback_data="go:attack")
            )
        else:
            keyboard.add(
                types.InlineKeyboardButton("ðŸŽ® Start", callback_data="go:start"),
                types.InlineKeyboardButton("âš”ï¸ Attack", callback_data="go:attack")
            )
    elif context.intention == UserIntention.GET_HELP:
        if lang == "fa":
            keyboard.add(
                types.InlineKeyboardButton("ðŸ“š Ø±Ø§Ù‡Ù†Ù…Ø§ÛŒ Ú©Ø§Ù…Ù„", callback_data="go:help"),
                types.InlineKeyboardButton("ðŸŽ¯ Ø´Ø±ÙˆØ¹ Ø³Ø±ÛŒØ¹", callback_data="go:quick_start")
            )
        else:
            keyboard.add(
                types.InlineKeyboardButton("ðŸ“š Complete Guide", callback_data="go:help"),
                types.InlineKeyboardButton("ðŸŽ¯ Quick Start", callback_data="go:quick_start")
            )
    elif context.intention == UserIntention.CHECK_STATUS:
        if lang == "fa":
            keyboard.add(
                types.InlineKeyboardButton("ðŸ“Š ÙˆØ¶Ø¹ÛŒØª", callback_data="go:status"),
                types.InlineKeyboardButton("ðŸ“ˆ Ø¢Ù…Ø§Ø±", callback_data="go:stats")
            )
        else:
            keyboard.add(
                types.InlineKeyboardButton("ðŸ“Š Status", callback_data="go:status"),
                types.InlineKeyboardButton("ðŸ“ˆ Stats", callback_data="go:stats")
            )
    else:
        # Ø¯Ú©Ù…Ù‡â€ŒÙ‡Ø§ÛŒ Ø¹Ù…ÙˆÙ…ÛŒ - General buttons
        if lang == "fa":
            keyboard.add(
                types.InlineKeyboardButton("ðŸ“š Ø±Ø§Ù‡Ù†Ù…Ø§", callback_data="go:help"),
                types.InlineKeyboardButton("ðŸŽ® Ø¨Ø§Ø²ÛŒ", callback_data="go:start")
            )
        else:
            keyboard.add(
                types.InlineKeyboardButton("ðŸ“š Help", callback_data="go:help"),
                types.InlineKeyboardButton("ðŸŽ® Game", callback_data="go:start")
            )
    
    return keyboard

# =============================================================================
# ØªÙˆØ§Ø¨Ø¹ Ú©Ù…Ú©ÛŒ Ù¾ÛŒØ´Ø±ÙØªÙ‡ - Advanced Helper Functions
# =============================================================================

async def handle_spam_message(message: Message, bot: AsyncTeleBot, db_manager: DBManager, context: MessageContext):
    """Ù…Ø¯ÛŒØ±ÛŒØª Ù¾ÛŒØ§Ù…â€ŒÙ‡Ø§ÛŒ Ø§Ø³Ù¾Ù… - Handle spam messages"""
    try:
        spam_score = anti_spam_manager.get_user_spam_score(context.user_id)
        
        # Ø§Ø±Ø³Ø§Ù„ Ù‡Ø´Ø¯Ø§Ø± Ø®ØµÙˆØµÛŒ Ø¨Ù‡ Ú©Ø§Ø±Ø¨Ø± - Send private warning to user
        if context.user_lang == "fa":
            warning_text = f"âš ï¸ **Ù‡Ø´Ø¯Ø§Ø± Ø§Ø³Ù¾Ù…**\n\n"
            warning_text += f"Ù¾ÛŒØ§Ù…â€ŒÙ‡Ø§ÛŒ Ø´Ù…Ø§ Ø¨Ù‡ Ø¹Ù†ÙˆØ§Ù† Ø§Ø³Ù¾Ù… ØªØ´Ø®ÛŒØµ Ø¯Ø§Ø¯Ù‡ Ø´Ø¯Ù‡â€ŒØ§Ù†Ø¯.\n"
            warning_text += f"Ø§Ù…ØªÛŒØ§Ø² Ø§Ø³Ù¾Ù…: {spam_score:.2f}\n\n"
            warning_text += f"Ù„Ø·ÙØ§Ù‹ Ø§Ø² Ø§Ø±Ø³Ø§Ù„ Ù¾ÛŒØ§Ù…â€ŒÙ‡Ø§ÛŒ ØªÚ©Ø±Ø§Ø±ÛŒ ÛŒØ§ Ù†Ø§Ù…Ù†Ø§Ø³Ø¨ Ø®ÙˆØ¯Ø¯Ø§Ø±ÛŒ Ú©Ù†ÛŒØ¯."
        else:
            warning_text = f"âš ï¸ **Spam Warning**\n\n"
            warning_text += f"Your messages have been detected as spam.\n"
            warning_text += f"Spam score: {spam_score:.2f}\n\n"
            warning_text += f"Please avoid sending repetitive or inappropriate messages."
        
        # Ø§Ø±Ø³Ø§Ù„ Ù¾ÛŒØ§Ù… Ø®ØµÙˆØµÛŒ - Send private message
        try:
            await bot.send_message(context.user_id, warning_text, parse_mode='Markdown')
        except:
            # Ø§Ú¯Ø± Ù†ØªÙˆØ§Ù†Ø³Øª Ø®ØµÙˆØµÛŒ Ø¨ÙØ±Ø³ØªØ¯ØŒ Ú†ÛŒØ²ÛŒ Ù†Ù…ÛŒâ€ŒÙØ±Ø³ØªØ¯ - If can't send private, don't send anything
            pass
        
        # Ø­Ø°Ù Ù¾ÛŒØ§Ù… Ø§Ø³Ù¾Ù… - Delete spam message
        try:
            await bot.delete_message(context.chat_id, message.message_id)
        except:
            # Ø§Ú¯Ø± Ù†ØªÙˆØ§Ù†Ø³Øª Ø­Ø°Ù Ú©Ù†Ø¯ - If can't delete
            pass
        
        # Ø«Ø¨Øª Ù„Ø§Ú¯ Ø§Ù…Ù†ÛŒØªÛŒ - Log security event
        security_logger.warning(
            f"Spam detected - User: {context.user_id}, Chat: {context.chat_id}, "
            f"Score: {spam_score:.2f}, Message: {message.text[:50]}..."
        )
        
    except Exception as e:
        logger.error(f"Error handling spam message: {e}")

async def handle_message_processing_error(message: Message, bot: AsyncTeleBot, db_manager: DBManager, error: Exception):
    """Ù…Ø¯ÛŒØ±ÛŒØª Ø®Ø·Ø§Ù‡Ø§ÛŒ Ù¾Ø±Ø¯Ø§Ø²Ø´ Ù¾ÛŒØ§Ù… - Handle message processing errors"""
    try:
        user_lang = await get_lang(message.chat.id, message.from_user.id, db_manager)
        
        # Ø§Ø±Ø³Ø§Ù„ Ù¾ÛŒØ§Ù… Ø®Ø·Ø§ Ø¨Ù‡ Ú©Ø§Ø±Ø¨Ø± - Send error message to user
        if user_lang == "fa":
            error_text = "âŒ Ù…ØªØ£Ø³ÙØ§Ù†Ù‡ Ø¯Ø± Ù¾Ø±Ø¯Ø§Ø²Ø´ Ù¾ÛŒØ§Ù… Ø´Ù…Ø§ Ø®Ø·Ø§ÛŒÛŒ Ø±Ø® Ø¯Ø§Ø¯.\n\nÙ„Ø·ÙØ§Ù‹ Ù…Ø¬Ø¯Ø¯Ø§Ù‹ ØªÙ„Ø§Ø´ Ú©Ù†ÛŒØ¯."
        else:
            error_text = "âŒ Sorry, an error occurred while processing your message.\n\nPlease try again."
        
        await bot.reply_to(message, error_text)
        
        # Ø«Ø¨Øª Ù„Ø§Ú¯ Ø®Ø·Ø§ - Log error
        logger.error(f"Message processing error for user {message.from_user.id}: {error}")
        
    except Exception as e:
        logger.error(f"Error handling message processing error: {e}")

async def send_payment_error_message(message: Message, bot: AsyncTeleBot, db_manager: DBManager):
    """Ø§Ø±Ø³Ø§Ù„ Ù¾ÛŒØ§Ù… Ø®Ø·Ø§ÛŒ Ù¾Ø±Ø¯Ø§Ø®Øª - Send payment error message"""
    try:
        user_lang = await get_lang(message.chat.id, message.from_user.id, db_manager)
        
        if user_lang == "fa":
            error_text = "âŒ Ø®Ø·Ø§ Ø¯Ø± Ù¾Ø±Ø¯Ø§Ø²Ø´ Ù¾Ø±Ø¯Ø§Ø®Øª!\n\nÙ„Ø·ÙØ§Ù‹ Ø¨Ø§ Ù¾Ø´ØªÛŒØ¨Ø§Ù†ÛŒ ØªÙ…Ø§Ø³ Ø¨Ú¯ÛŒØ±ÛŒØ¯."
        else:
            error_text = "âŒ Payment processing error!\n\nPlease contact support."
        
        keyboard = types.InlineKeyboardMarkup()
        if user_lang == "fa":
            keyboard.add(types.InlineKeyboardButton("ðŸ†˜ Ù¾Ø´ØªÛŒØ¨Ø§Ù†ÛŒ", callback_data="go:support"))
        else:
            keyboard.add(types.InlineKeyboardButton("ðŸ†˜ Support", callback_data="go:support"))
        
        await bot.send_message(message.chat.id, error_text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error sending payment error message: {e}")

async def send_generic_payment_confirmation(
    message: Message, 
    bot: AsyncTeleBot, 
    payment_info: types.SuccessfulPayment, 
    user_lang: str
):
    """Ø§Ø±Ø³Ø§Ù„ ØªØ§ÛŒÛŒØ¯ Ø¹Ù…ÙˆÙ…ÛŒ Ù¾Ø±Ø¯Ø§Ø®Øª - Send generic payment confirmation"""
    try:
        if user_lang == "fa":
            confirmation_text = "âœ… Ù¾Ø±Ø¯Ø§Ø®Øª Ø¨Ø§ Ù…ÙˆÙÙ‚ÛŒØª Ø§Ù†Ø¬Ø§Ù… Ø´Ø¯!\n\nÙ…Ù…Ù†ÙˆÙ† Ø§Ø² Ø®Ø±ÛŒØ¯ Ø´Ù…Ø§."
        else:
            confirmation_text = "âœ… Payment completed successfully!\n\nThank you for your purchase."
        
        await bot.send_message(message.chat.id, confirmation_text)
        
    except Exception as e:
        logger.error(f"Error sending generic payment confirmation: {e}")

async def log_new_members_event(message: Message, db_manager: DBManager):
    """Ø«Ø¨Øª Ø±ÙˆÛŒØ¯Ø§Ø¯ Ø¹Ø¶ÙˆÛŒØª Ø§Ø¹Ø¶Ø§ÛŒ Ø¬Ø¯ÛŒØ¯ - Log new members event"""
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
    """Ø«Ø¨Øª Ø±ÙˆÛŒØ¯Ø§Ø¯ Ø®Ø±ÙˆØ¬ Ø¹Ø¶Ùˆ - Log member left event"""
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
    """Ø«Ø¨Øª Ø¢Ù…Ø§Ø± Ù¾Ø±Ø¯Ø§Ø®Øª - Log payment statistics"""
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
    """Ø«Ø¨Øª ØªØ¹Ø§Ù…Ù„ Ù¾ÛŒØ§Ù… - Log message interaction"""
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
    """Ø¨Ù‡â€ŒØ±ÙˆØ²Ø±Ø³Ø§Ù†ÛŒ Ø¢Ù…Ø§Ø± Ù¾ÛŒØ§Ù… Ú©Ø§Ø±Ø¨Ø± - Update user message statistics"""
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
# Ù…Ø¯ÛŒØ±ÛŒØª Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù… - Advanced Telegram Stars Management
# =============================================================================

async def handle_tg_stars_received(message: Message, bot: AsyncTeleBot, db_manager: DBManager):
    """
    Ù…Ø¯ÛŒØ±ÛŒØª Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ø¯Ø±ÛŒØ§ÙØª Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù…
    Enhanced handling of received TG Stars
    
    Args:
        message (Message): Message object containing stars info
        bot (AsyncTeleBot): Bot instance
        db_manager (DBManager): Database manager instance
    """
    try:
        # Ø¨Ø±Ø±Ø³ÛŒ Ø§ÛŒÙ†Ú©Ù‡ Ø§ÛŒÙ† Ù¾ÛŒØ§Ù… ÙÙˆØ±ÙˆØ§Ø±Ø¯ Ø´Ø¯Ù‡ Ø®ÙˆØ¯Ú©Ø§Ø± Ø§Ø³Øª - Check if this is an automatic forward
        if not hasattr(message, 'is_automatic_forward') or not message.is_automatic_forward:
            return
        
        # Ø¨Ø±Ø±Ø³ÛŒ Ø§ÛŒÙ†Ú©Ù‡ Ø§Ø² Ú©Ø§Ù†Ø§Ù„ Ø±Ø³Ù…ÛŒ ØªÙ„Ú¯Ø±Ø§Ù… ÙÙˆØ±ÙˆØ§Ø±Ø¯ Ø´Ø¯Ù‡ - Check if forwarded from official Telegram
        if not hasattr(message, 'forward_from_chat') or not message.forward_from_chat:
            return
        
        # ØªØ£ÛŒÛŒØ¯ ÙÙˆØ±ÙˆØ§Ø±Ø¯ Ø§Ø² Ú©Ø§Ù†Ø§Ù„ Ø±Ø³Ù…ÛŒ - Verify forward from official channel
        if message.forward_from_chat.username != "telegram":
            return
        
        # Ø¨Ø±Ø±Ø³ÛŒ Ù…ØªÙ† Ù¾ÛŒØ§Ù… - Check message text
        if not hasattr(message, 'text') or not message.text:
            return
        
        # Ø§Ø³ØªØ®Ø±Ø§Ø¬ Ù…Ù‚Ø¯Ø§Ø± Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ - Extract stars amount
        stars_amount = await extract_stars_amount_from_message(message.text)
        if not stars_amount:
            return
        
        # Ù¾Ø±Ø¯Ø§Ø²Ø´ Ø¯Ø±ÛŒØ§ÙØª Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ - Process stars received
        await process_stars_received(message, bot, db_manager, stars_amount)
        
        logger.info(f"TG Stars received processed: {stars_amount} for user {message.chat.id}")
        
    except Exception as e:
        logger.error(f"Error handling TG stars received: {e}")

async def extract_stars_amount_from_message(text: str) -> Optional[int]:
    """Ø§Ø³ØªØ®Ø±Ø§Ø¬ Ù…Ù‚Ø¯Ø§Ø± Ø³ØªØ§Ø±Ù‡ Ø§Ø² Ù…ØªÙ† Ù¾ÛŒØ§Ù… - Extract stars amount from message text"""
    try:
        # Ø§Ù„Ú¯ÙˆÙ‡Ø§ÛŒ Ù…Ø®ØªÙ„Ù Ø¨Ø±Ø§ÛŒ ØªØ´Ø®ÛŒØµ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ - Different patterns for stars detection
        patterns = [
            r"You've received (\d+) Telegram Stars",
            r"You received (\d+) Telegram Stars",
            r"(\d+) Telegram Stars received",
            r"Ø´Ù…Ø§ (\d+) Ø³ØªØ§Ø±Ù‡ ØªÙ„Ú¯Ø±Ø§Ù… Ø¯Ø±ÛŒØ§ÙØª Ú©Ø±Ø¯Ù‡â€ŒØ§ÛŒØ¯",
            r"(\d+) Ø³ØªØ§Ø±Ù‡ ØªÙ„Ú¯Ø±Ø§Ù… Ø¯Ø±ÛŒØ§ÙØª Ø´Ø¯"
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
    """Ù¾Ø±Ø¯Ø§Ø²Ø´ Ø¯Ø±ÛŒØ§ÙØª Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ - Process stars received"""
    try:
        user_id = message.chat.id
        
        # ØªÙˆÙ„ÛŒØ¯ Ø´Ù†Ø§Ø³Ù‡ ØªØ±Ø§Ú©Ù†Ø´ - Generate transaction ID
        transaction_id = f"tg_stars_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Ø°Ø®ÛŒØ±Ù‡ ØªØ±Ø§Ú©Ù†Ø´ Ø¯Ø± Ù¾Ø§ÛŒÚ¯Ø§Ù‡ Ø¯Ø§Ø¯Ù‡ - Store transaction in database
        await db_manager.create_stars_transaction(
            user_id=user_id,
            amount=stars_amount,
            transaction_type="received",
            transaction_id=transaction_id,
            source="telegram_official",
            status="pending"
        )
        
        # Ø¯Ø±ÛŒØ§ÙØª Ø²Ø¨Ø§Ù† Ú©Ø§Ø±Ø¨Ø± - Get user language
        user_lang = await get_lang(user_id, user_id, db_manager)
        
        # ØªÙˆÙ„ÛŒØ¯ Ù¾ÛŒØ§Ù… ØªØ§ÛŒÛŒØ¯ - Generate confirmation message
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
    """Ø§Ø±Ø³Ø§Ù„ ØªØ§ÛŒÛŒØ¯ Ø¯Ø±ÛŒØ§ÙØª Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ - Send stars received confirmation"""
    try:
        if user_lang == "fa":
            confirmation_text = f"ðŸŒŸ **Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù… Ø¯Ø±ÛŒØ§ÙØª Ø´Ø¯!**\n\n"
            confirmation_text += f"ðŸ’« **Ù…Ù‚Ø¯Ø§Ø±:** {stars_amount} Ø³ØªØ§Ø±Ù‡\n"
            confirmation_text += f"ðŸ”¢ **Ø´Ù†Ø§Ø³Ù‡:** `{transaction_id}`\n"
            confirmation_text += f"ðŸ“… **ØªØ§Ø±ÛŒØ®:** {datetime.now().strftime('%Y/%m/%d %H:%M')}\n\n"
            confirmation_text += f"ðŸŽ Ø¨Ø±Ø§ÛŒ Ø§Ø¶Ø§ÙÙ‡ Ú©Ø±Ø¯Ù† Ø§ÛŒÙ† Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ Ø¨Ù‡ Ø­Ø³Ø§Ø¨ Ø¨Ø§Ø²ÛŒ Ø®ÙˆØ¯ØŒ Ø¯Ú©Ù…Ù‡ Ø²ÛŒØ± Ø±Ø§ ÙØ´Ø§Ø± Ø¯Ù‡ÛŒØ¯:"
            
            claim_button_text = f"ðŸŽ Ø¯Ø±ÛŒØ§ÙØª {stars_amount} Ø³ØªØ§Ø±Ù‡"
            claim_callback = f"tg_stars_received:{stars_amount}:{transaction_id}"
        else:
            confirmation_text = f"ðŸŒŸ **Telegram Stars Received!**\n\n"
            confirmation_text += f"ðŸ’« **Amount:** {stars_amount} stars\n"
            confirmation_text += f"ðŸ”¢ **ID:** `{transaction_id}`\n"
            confirmation_text += f"ðŸ“… **Date:** {datetime.now().strftime('%Y/%m/%d %H:%M')}\n\n"
            confirmation_text += f"ðŸŽ To add these stars to your game account, press the button below:"
            
            claim_button_text = f"ðŸŽ Claim {stars_amount} Stars"
            claim_callback = f"tg_stars_received:{stars_amount}:{transaction_id}"
        
        # Ø§ÛŒØ¬Ø§Ø¯ Ú©ÛŒØ¨ÙˆØ±Ø¯ - Create keyboard
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(claim_button_text, callback_data=claim_callback))
        
        if user_lang == "fa":
            keyboard.add(
                types.InlineKeyboardButton("ðŸ“Š Ù…ÙˆØ¬ÙˆØ¯ÛŒ Ù…Ù†", callback_data="go:status"),
                types.InlineKeyboardButton("ðŸ›’ ÙØ±ÙˆØ´Ú¯Ø§Ù‡", callback_data="go:shop")
            )
        else:
            keyboard.add(
                types.InlineKeyboardButton("ðŸ“Š My Balance", callback_data="go:status"),
                types.InlineKeyboardButton("ðŸ›’ Shop", callback_data="go:shop")
            )
        
        # Ø§Ø±Ø³Ø§Ù„ Ù¾ÛŒØ§Ù… - Send message
        await bot.send_message(
            message.chat.id,
            confirmation_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error sending stars received confirmation: {e}")

# =============================================================================
# Ø³ÛŒØ³ØªÙ… ØªØ­Ù„ÛŒÙ„ Ùˆ Ú¯Ø²Ø§Ø±Ø´â€ŒÚ¯ÛŒØ±ÛŒ - Analytics and Reporting System
# =============================================================================

class MessageAnalyticsCollector:
    """Ø¬Ù…Ø¹â€ŒØ¢ÙˆØ±ÛŒ Ø¢Ù†Ø§Ù„ÛŒØªÛŒÚ©Ø³ Ù¾ÛŒØ§Ù… - Message Analytics Collector"""
    
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
        """Ø¬Ù…Ø¹â€ŒØ¢ÙˆØ±ÛŒ Ø¢Ù†Ø§Ù„ÛŒØªÛŒÚ©Ø³ Ù¾ÛŒØ§Ù… - Collect message analytics"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            current_hour = datetime.now().hour
            
            # Ø¢Ù…Ø§Ø± Ø±ÙˆØ²Ø§Ù†Ù‡ - Daily stats
            self.daily_stats[today]['total_messages'] += 1
            self.daily_stats[today][f'type_{context.message_type.value}'] += 1
            self.daily_stats[today][f'lang_{context.user_lang}'] += 1
            
            if context.intention:
                self.daily_stats[today][f'intention_{context.intention.value}'] += 1
            
            if context.sentiment:
                self.daily_stats[today][f'sentiment_{context.sentiment.value}'] += 1
            
            # Ø¢Ù…Ø§Ø± Ø³Ø§Ø¹ØªÛŒ - Hourly stats
            self.hourly_stats[current_hour]['total_messages'] += 1
            self.hourly_stats[current_hour][f'lang_{context.user_lang}'] += 1
            
            # Ø¢Ù…Ø§Ø± Ú©Ø§Ø±Ø¨Ø±ÛŒ - User stats
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
        """Ø¯Ø±ÛŒØ§ÙØª Ú¯Ø²Ø§Ø±Ø´ Ø±ÙˆØ²Ø§Ù†Ù‡ - Get daily report"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        return dict(self.daily_stats.get(date, {}))
    
    def get_user_summary(self, user_id: int) -> Dict[str, Any]:
        """Ø¯Ø±ÛŒØ§ÙØª Ø®Ù„Ø§ØµÙ‡ Ú©Ø§Ø±Ø¨Ø± - Get user summary"""
        user_stat = self.user_stats.get(user_id, {})
        
        # ØªØ¨Ø¯ÛŒÙ„ set Ø¨Ù‡ list Ø¨Ø±Ø§ÛŒ JSON serialization
        if 'languages_used' in user_stat:
            user_stat['languages_used'] = list(user_stat['languages_used'])
        
        return user_stat

# Ù†Ù…ÙˆÙ†Ù‡ Ø³Ø±Ø§Ø³Ø±ÛŒ Ø¬Ù…Ø¹â€ŒØ¢ÙˆØ±ÛŒ Ø¢Ù†Ø§Ù„ÛŒØªÛŒÚ©Ø³ - Global analytics collector instance
analytics_collector = MessageAnalyticsCollector()

# =============================================================================
# Ø³ÛŒØ³ØªÙ… Ø«Ø¨Øª Ù…Ø¯ÛŒØ±ÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡â€ŒÙ‡Ø§ - Handler Registration System
# =============================================================================

def register_message_handlers(bot: AsyncTeleBot, db_manager: DBManager):
    """
    Ø«Ø¨Øª Ù…Ø¯ÛŒØ±ÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡â€ŒÙ‡Ø§ÛŒ Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ù¾ÛŒØ§Ù…
    Register enhanced message handlers with comprehensive functionality
    
    Args:
        bot (AsyncTeleBot): Bot instance with async support
        db_manager (DBManager): Enhanced database manager instance
    """
    logger.info("Registering enhanced message handlers with comprehensive functionality")
    logger.info("Ø«Ø¨Øª Ù…Ø¯ÛŒØ±ÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡â€ŒÙ‡Ø§ÛŒ Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ù¾ÛŒØ§Ù… Ø¨Ø§ Ø¹Ù…Ù„Ú©Ø±Ø¯ Ø¬Ø§Ù…Ø¹")
    
    # Ø«Ø¨Øª Ù…Ø¯ÛŒØ±ÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡ Ø§Ø¹Ø¶Ø§ÛŒ Ø¬Ø¯ÛŒØ¯ - Register new members handler
    @bot.message_handler(content_types=['new_chat_members'])
    async def enhanced_new_chat_members_handler(message):
        """Ù…Ø¯ÛŒØ±ÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡ Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ø§Ø¹Ø¶Ø§ÛŒ Ø¬Ø¯ÛŒØ¯ - Enhanced new members handler"""
        try:
            await handle_new_chat_members(message, bot, db_manager)
        except Exception as e:
            logger.error(f"Error in new chat members handler: {e}")
    
    # Ø«Ø¨Øª Ù…Ø¯ÛŒØ±ÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡ Ø®Ø±ÙˆØ¬ Ø§Ø¹Ø¶Ø§ - Register left members handler
    @bot.message_handler(content_types=['left_chat_member'])
    async def enhanced_left_chat_member_handler(message):
        """Ù…Ø¯ÛŒØ±ÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡ Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ø®Ø±ÙˆØ¬ Ø§Ø¹Ø¶Ø§ - Enhanced left members handler"""
        try:
            await handle_left_chat_member(message, bot, db_manager)
        except Exception as e:
            logger.error(f"Error in left chat member handler: {e}")
    
    # Ø«Ø¨Øª Ù…Ø¯ÛŒØ±ÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡ Ù¾Ø±Ø¯Ø§Ø®Øª Ù…ÙˆÙÙ‚ - Register successful payment handler
    @bot.message_handler(content_types=['successful_payment'])
    async def enhanced_successful_payment_handler(message):
        """Ù…Ø¯ÛŒØ±ÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡ Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ù¾Ø±Ø¯Ø§Ø®Øª Ù…ÙˆÙÙ‚ - Enhanced successful payment handler"""
        try:
            await handle_telegram_stars_payment(message, bot, db_manager)
        except Exception as e:
            logger.error(f"Error in successful payment handler: {e}")
    
    # Ø«Ø¨Øª Ù…Ø¯ÛŒØ±ÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡ Ø¯Ø§Ø¯Ù‡â€ŒÙ‡Ø§ÛŒ ÙˆØ¨ Ø§Ù¾ - Register web app data handler
    @bot.message_handler(content_types=['web_app_data'])
    async def enhanced_web_app_data_handler(message):
        """Ù…Ø¯ÛŒØ±ÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡ Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ø¯Ø§Ø¯Ù‡â€ŒÙ‡Ø§ÛŒ ÙˆØ¨ Ø§Ù¾ - Enhanced web app data handler"""
        try:
            await handle_telegram_stars_payment_callback(message, bot, db_manager)
        except Exception as e:
            logger.error(f"Error in web app data handler: {e}")
    
    # Ø«Ø¨Øª Ù…Ø¯ÛŒØ±ÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ Ø¯Ø±ÛŒØ§ÙØªÛŒ - Register TG stars received handler
    @bot.message_handler(
        func=lambda m: (
            hasattr(m, 'is_automatic_forward') and m.is_automatic_forward and
            hasattr(m, 'forward_from_chat') and m.forward_from_chat and
            m.forward_from_chat.username == 'telegram'
        )
    )
    async def enhanced_tg_stars_received_handler(message):
        """Ù…Ø¯ÛŒØ±ÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡ Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ Ø¯Ø±ÛŒØ§ÙØªÛŒ - Enhanced TG stars received handler"""
        try:
            await handle_tg_stars_received(message, bot, db_manager)
        except Exception as e:
            logger.error(f"Error in TG stars received handler: {e}")
    
    # Ø«Ø¨Øª Ù…Ø¯ÛŒØ±ÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡ Ù¾ÛŒØ§Ù…â€ŒÙ‡Ø§ÛŒ Ù…ØªÙ†ÛŒ - Register text messages handler
    @bot.message_handler(func=lambda m: True, content_types=['text'])
    async def enhanced_regular_message_handler(message):
        """Ù…Ø¯ÛŒØ±ÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡ Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ù¾ÛŒØ§Ù…â€ŒÙ‡Ø§ÛŒ Ù…ØªÙ†ÛŒ - Enhanced text messages handler"""
        try:
            # Ø¬Ù…Ø¹â€ŒØ¢ÙˆØ±ÛŒ Ø¢Ù†Ø§Ù„ÛŒØªÛŒÚ©Ø³ - Collect analytics
            if not (message.text and message.text.startswith('/')):
                context = await create_message_context(message, bot, db_manager)
                await analytics_collector.collect_message_analytics(context)
            
            # Ù¾Ø±Ø¯Ø§Ø²Ø´ Ù¾ÛŒØ§Ù… - Process message
            await handle_regular_message(message, bot, db_manager)
            
        except Exception as e:
            logger.error(f"Error in regular message handler: {e}")
            await handle_message_processing_error(message, bot, db_manager, e)
    
    # Ø«Ø¨Øª Ù…Ø¯ÛŒØ±ÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡ Ø³Ø§ÛŒØ± Ø§Ù†ÙˆØ§Ø¹ Ù…Ø­ØªÙˆØ§ - Register other content types handlers
    @bot.message_handler(content_types=['photo', 'video', 'document', 'audio', 'voice', 'sticker'])
    async def enhanced_media_message_handler(message):
        """Ù…Ø¯ÛŒØ±ÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡ Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ù¾ÛŒØ§Ù…â€ŒÙ‡Ø§ÛŒ Ø±Ø³Ø§Ù†Ù‡â€ŒØ§ÛŒ - Enhanced media messages handler"""
        try:
            # Ø§Ø·Ù…ÛŒÙ†Ø§Ù† Ø§Ø² ÙˆØ¬ÙˆØ¯ Ú©Ø§Ø±Ø¨Ø± - Ensure user exists
            await ensure_player(message.chat.id, message.from_user, db_manager)
            
            # Ø¬Ù…Ø¹â€ŒØ¢ÙˆØ±ÛŒ Ø¢Ù†Ø§Ù„ÛŒØªÛŒÚ©Ø³ - Collect analytics
            context = await create_message_context(message, bot, db_manager)
            await analytics_collector.collect_message_analytics(context)
            
            # Ø¨Ù‡â€ŒØ±ÙˆØ²Ø±Ø³Ø§Ù†ÛŒ Ø¢Ù…Ø§Ø± ÙØ¹Ø§Ù„ÛŒØª - Update activity stats
            await update_user_message_stats(context, db_manager)
            
        except Exception as e:
            logger.error(f"Error in media message handler: {e}")
    
    # Ù¾ÛŒØ§Ù… ØªØ£ÛŒÛŒØ¯ Ø«Ø¨Øª - Registration confirmation message
    logger.info("âœ… Enhanced message handlers registered successfully")
    logger.info("âœ… Ù…Ø¯ÛŒØ±ÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡â€ŒÙ‡Ø§ÛŒ Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ù¾ÛŒØ§Ù… Ø¨Ø§ Ù…ÙˆÙÙ‚ÛŒØª Ø«Ø¨Øª Ø´Ø¯Ù†Ø¯")
    
    # Ø«Ø¨Øª Ø¢Ù…Ø§Ø± Ø«Ø¨Øª - Log registration stats
    handler_types = [
        "new_chat_members", "left_chat_member", "successful_payment",
        "web_app_data", "tg_stars_received", "text_messages", "media_messages"
    ]
    
    logger.info(f"Registered {len(handler_types)} enhanced message handler types")
    logger.info(f"{len(handler_types)} Ù†ÙˆØ¹ Ù…Ø¯ÛŒØ±ÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡ Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ø«Ø¨Øª Ø´Ø¯")
    
    # ÙØ¹Ø§Ù„â€ŒØ³Ø§Ø²ÛŒ Ù†Ø¸Ø§Ø±Øª Ø¹Ù…Ù„Ú©Ø±Ø¯ - Enable performance monitoring
    logger.info(f"Message analytics: {'enabled' if True else 'disabled'}")
    logger.info(f"Anti-spam protection: {'enabled' if True else 'disabled'}")
    logger.info(f"Smart responses: {'enabled' if True else 'disabled'}")
    logger.info(f"Ø¢Ù†Ø§Ù„ÛŒØªÛŒÚ©Ø³ Ù¾ÛŒØ§Ù…: {'ÙØ¹Ø§Ù„' if True else 'ØºÛŒØ±ÙØ¹Ø§Ù„'}")
    logger.info(f"Ù…Ø­Ø§ÙØ¸Øª Ø§Ù†ØªÛŒâ€ŒØ§Ø³Ù¾Ù…: {'ÙØ¹Ø§Ù„' if True else 'ØºÛŒØ±ÙØ¹Ø§Ù„'}")
    logger.info(f"Ù¾Ø§Ø³Ø®â€ŒÙ‡Ø§ÛŒ Ù‡ÙˆØ´Ù…Ù†Ø¯: {'ÙØ¹Ø§Ù„' if True else 'ØºÛŒØ±ÙØ¹Ø§Ù„'}")

# =============================================================================
# ØµØ§Ø¯Ø±Ø§Øª Ù…Ø§Ú˜ÙˆÙ„ - Module Exports
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

# Ù¾ÛŒØ§Ù… Ø§ÙˆÙ„ÛŒÙ‡â€ŒØ³Ø§Ø²ÛŒ - Initialization message
logger.info("Enhanced Message Handlers Module loaded successfully")
logger.info("Ù…Ø§Ú˜ÙˆÙ„ Ù…Ø¯ÛŒØ±ÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡â€ŒÙ‡Ø§ÛŒ Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ù¾ÛŒØ§Ù… Ø¨Ø§ Ù…ÙˆÙÙ‚ÛŒØª Ø¨Ø§Ø±Ú¯Ø°Ø§Ø±ÛŒ Ø´Ø¯")

# ØªÙ†Ø¸ÛŒÙ… Ù†Ø¸Ø§Ø±Øª Ø¹Ù…Ù„Ú©Ø±Ø¯ - Performance monitoring setup
logger.info("Message analysis system: initialized")
logger.info("Anti-spam protection: initialized") 
logger.info("Smart response system: initialized")
logger.info("Analytics collection: initialized")
logger.info("Ø³ÛŒØ³ØªÙ… ØªØ­Ù„ÛŒÙ„ Ù¾ÛŒØ§Ù…: Ø±Ø§Ù‡â€ŒØ§Ù†Ø¯Ø§Ø²ÛŒ Ø´Ø¯")
logger.info("Ù…Ø­Ø§ÙØ¸Øª Ø§Ù†ØªÛŒâ€ŒØ§Ø³Ù¾Ù…: Ø±Ø§Ù‡â€ŒØ§Ù†Ø¯Ø§Ø²ÛŒ Ø´Ø¯")
logger.info("Ø³ÛŒØ³ØªÙ… Ù¾Ø§Ø³Ø® Ù‡ÙˆØ´Ù…Ù†Ø¯: Ø±Ø§Ù‡â€ŒØ§Ù†Ø¯Ø§Ø²ÛŒ Ø´Ø¯")
logger.info("Ø¬Ù…Ø¹â€ŒØ¢ÙˆØ±ÛŒ Ø¢Ù†Ø§Ù„ÛŒØªÛŒÚ©Ø³: Ø±Ø§Ù‡â€ŒØ§Ù†Ø¯Ø§Ø²ÛŒ Ø´Ø¯")

# Alias for compatibility with app.py
def register_handlers(bot: AsyncTeleBot, db_manager: DBManager) -> None:
    """
    Alias for register_message_handlers to maintain compatibility
    Ù†Ø§Ù… Ù…Ø³ØªØ¹Ø§Ø± Ø¨Ø±Ø§ÛŒ register_message_handlers Ø¨Ø±Ø§ÛŒ Ø­ÙØ¸ Ø³Ø§Ø²Ú¯Ø§Ø±ÛŒ
    """
    return register_message_handlers(bot, db_manager)

