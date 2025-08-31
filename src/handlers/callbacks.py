#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ù¾Ø±Ø¯Ø§Ø²Ø´â€ŒÚ©Ù†Ù†Ø¯Ù‡â€ŒÙ‡Ø§ÛŒ Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ú©Ø§Ù„Ø¨Ú© Ø¨Ø§ Ù¾Ø´ØªÛŒØ¨Ø§Ù†ÛŒ Ú©Ø§Ù…Ù„ Ø§Ø² Ø²Ø¨Ø§Ù† ÙØ§Ø±Ø³ÛŒ
Enhanced Callback Query Handlers with Comprehensive Persian Language Support
"""

import logging
import asyncio
import time
import json
from functools import wraps
from typing import Dict, List, Optional, Callable, Any, Tuple
from enum import Enum
from dataclasses import dataclass
from telebot import types
from telebot.async_telebot import AsyncTeleBot

from src.database.db_manager import DBManager
from src.utils.helpers import ensure_player, get_lang, set_lang
from src.utils.translations import T
from src.commands import help, shop, stats, status, inventory, attack, general
from src.commands.stars import handle_stars_callback

# Set up logging
logger = logging.getLogger(__name__)

class CallbackAction(Enum):
    """Ø§Ù†ÙˆØ§Ø¹ Ø¹Ù…Ù„ÛŒØ§Øª Ú©Ø§Ù„Ø¨Ú© - Callback Action Types"""
    NAVIGATION = "go"          # Ù†Ø§ÙˆØ¨Ø±ÛŒ - Navigation
    ACTION = "do"              # Ø¹Ù…Ù„ - Action
    PURCHASE = "buy"           # Ø®Ø±ÛŒØ¯ - Purchase
    CONFIRM = "confirm"        # ØªØ§ÛŒÛŒØ¯ - Confirmation
    CANCEL = "cancel"          # Ù„ØºÙˆ - Cancel
    PAGINATION = "page"        # ØµÙØ­Ù‡â€ŒØ¨Ù†Ø¯ÛŒ - Pagination
    LANGUAGE = "lang"          # Ø²Ø¨Ø§Ù† - Language
    FILTER = "filter"          # ÙÛŒÙ„ØªØ± - Filter
    SORT = "sort"              # Ù…Ø±ØªØ¨â€ŒØ³Ø§Ø²ÛŒ - Sort
    HELP = "help"              # Ø±Ø§Ù‡Ù†Ù…Ø§ - Help
    SETTINGS = "settings"      # ØªÙ†Ø¸ÛŒÙ…Ø§Øª - Settings
    ADMIN = "admin"            # Ù…Ø¯ÛŒØ±ÛŒØª - Admin
    STARS = "stars"            # Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ - Stars
    ATTACK = "attack"          # Ø­Ù…Ù„Ù‡ - Attack
    DEFEND = "defend"          # Ø¯ÙØ§Ø¹ - Defense
    INVENTORY = "inv"          # Ù…ÙˆØ¬ÙˆØ¯ÛŒ - Inventory
    LEADERBOARD = "lead"       # Ù„ÛŒØ¯Ø±Ø¨ÙˆØ±Ø¯ - Leaderboard

@dataclass
class CallbackContext:
    """Ø¨Ø§ÙØª Ú©Ø§Ù„Ø¨Ú© - Callback Context"""
    call: types.CallbackQuery
    bot: AsyncTeleBot
    db_manager: DBManager
    action: str
    data: str
    lang: str
    user_id: int
    chat_id: int
    message_id: int
    timestamp: float

class CallbackSecurity:
    """Ø§Ù…Ù†ÛŒØª Ú©Ø§Ù„Ø¨Ú© - Callback Security Manager"""
    
    def __init__(self):
        self.rate_limits: Dict[int, List[float]] = {}
        self.max_requests_per_minute = 30
        self.blocked_users: Dict[int, float] = {}
        self.block_duration = 300  # 5 minutes
    
    def is_rate_limited(self, user_id: int) -> bool:
        """Ø¨Ø±Ø±Ø³ÛŒ Ù…Ø­Ø¯ÙˆØ¯ÛŒØª Ù†Ø±Ø® - Check rate limiting"""
        current_time = time.time()
        
        # Clean old requests
        if user_id in self.rate_limits:
            self.rate_limits[user_id] = [
                t for t in self.rate_limits[user_id] 
                if current_time - t < 60
            ]
        
        # Check if user is blocked
        if user_id in self.blocked_users:
            if current_time - self.blocked_users[user_id] > self.block_duration:
                del self.blocked_users[user_id]
            else:
                return True
        
        # Check rate limit
        user_requests = self.rate_limits.get(user_id, [])
        if len(user_requests) >= self.max_requests_per_minute:
            self.blocked_users[user_id] = current_time
            logger.warning(f"User {user_id} blocked for rate limiting")
            logger.warning(f"Ú©Ø§Ø±Ø¨Ø± {user_id} Ø¨Ù‡ Ø¯Ù„ÛŒÙ„ Ù…Ø­Ø¯ÙˆØ¯ÛŒØª Ù†Ø±Ø® Ù…Ø³Ø¯ÙˆØ¯ Ø´Ø¯")
            return True
        
        # Add current request
        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = []
        self.rate_limits[user_id].append(current_time)
        
        return False
    
    def validate_callback_data(self, data: str) -> bool:
        """Ø§Ø¹ØªØ¨Ø§Ø±Ø³Ù†Ø¬ÛŒ Ø¯Ø§Ø¯Ù‡ Ú©Ø§Ù„Ø¨Ú© - Validate callback data"""
        if not data or len(data) > 64:  # Telegram limit
            return False
        
        # Check for malicious patterns
        malicious_patterns = ['<script', 'javascript:', 'data:', 'vbscript:']
        return not any(pattern in data.lower() for pattern in malicious_patterns)

# Global security instance
callback_security = CallbackSecurity()

def owner_only(func):
    """
    Ø¯Ú©ÙˆØ±ÛŒØªØ± Ø¨Ø±Ø§ÛŒ Ø§Ø·Ù…ÛŒÙ†Ø§Ù† Ø§Ø² Ø§ÛŒÙ†Ú©Ù‡ ÙÙ‚Ø· ØµØ§Ø­Ø¨ Ù¾ÛŒØ§Ù… Ù…ÛŒâ€ŒØªÙˆØ§Ù†Ø¯ Ø§Ø² Ú©Ø§Ù„Ø¨Ú© Ø§Ø³ØªÙØ§Ø¯Ù‡ Ú©Ù†Ø¯
    Decorator to ensure only the message owner can use the callback
    """
    @wraps(func)
    async def wrapper(call, bot, data, lang, db_manager):
        calling_user = call.from_user
        original_sender_id = call.message.reply_to_message.from_user.id if call.message.reply_to_message else None

        if original_sender_id and original_sender_id != calling_user.id:
            if lang == "fa":
                await bot.answer_callback_query(
                    call.id, 
                    "âš ï¸ Ø§ÛŒÙ† Ø¯Ú©Ù…Ù‡â€ŒÙ‡Ø§ ÙÙ‚Ø· Ø¨Ø±Ø§ÛŒ Ú©Ø§Ø±Ø¨Ø±ÛŒ Ø§Ø³Øª Ú©Ù‡ Ù¾ÛŒØ§Ù… Ø±Ø§ Ø§Ø±Ø³Ø§Ù„ Ú©Ø±Ø¯Ù‡!", 
                    show_alert=True
                )
            else:
                await bot.answer_callback_query(
                    call.id, 
                    "âš ï¸ These buttons are only for the user who sent the message!", 
                    show_alert=True
                )
            return
            
        return await func(call, bot, data, lang, db_manager)
    return wrapper

def rate_limit(func):
    """
    Ø¯Ú©ÙˆØ±ÛŒØªØ± Ù…Ø­Ø¯ÙˆØ¯ÛŒØª Ù†Ø±Ø® Ø¨Ø±Ø§ÛŒ Ø¬Ù„ÙˆÚ¯ÛŒØ±ÛŒ Ø§Ø² Ø³ÙˆØ¡Ø§Ø³ØªÙØ§Ø¯Ù‡
    Rate limiting decorator to prevent abuse
    """
    @wraps(func)
    async def wrapper(call, bot, data, lang, db_manager):
        if callback_security.is_rate_limited(call.from_user.id):
            if lang == "fa":
                await bot.answer_callback_query(
                    call.id,
                    "âš ï¸ Ø´Ù…Ø§ Ø®ÛŒÙ„ÛŒ Ø³Ø±ÛŒØ¹ Ø¯Ø±Ø®ÙˆØ§Ø³Øª Ù…ÛŒâ€ŒØ¯Ù‡ÛŒØ¯! Ù„Ø·ÙØ§Ù‹ Ú©Ù…ÛŒ ØµØ¨Ø± Ú©Ù†ÛŒØ¯.",
                    show_alert=True
                )
            else:
                await bot.answer_callback_query(
                    call.id,
                    "âš ï¸ You're making requests too quickly! Please wait a moment.",
                    show_alert=True
                )
            return
        
        return await func(call, bot, data, lang, db_manager)
    return wrapper

def validate_data(func):
    """
    Ø¯Ú©ÙˆØ±ÛŒØªØ± Ø§Ø¹ØªØ¨Ø§Ø±Ø³Ù†Ø¬ÛŒ Ø¯Ø§Ø¯Ù‡â€ŒÙ‡Ø§ÛŒ Ú©Ø§Ù„Ø¨Ú©
    Callback data validation decorator
    """
    @wraps(func)
    async def wrapper(call, bot, data, lang, db_manager):
        if not callback_security.validate_callback_data(data):
            logger.warning(f"Invalid callback data from user {call.from_user.id}: {data}")
            logger.warning(f"Ø¯Ø§Ø¯Ù‡ Ú©Ø§Ù„Ø¨Ú© Ù†Ø§Ù…Ø¹ØªØ¨Ø± Ø§Ø² Ú©Ø§Ø±Ø¨Ø± {call.from_user.id}: {data}")
            
            if lang == "fa":
                await bot.answer_callback_query(call.id, "âš ï¸ Ø¯Ø§Ø¯Ù‡ Ù†Ø§Ù…Ø¹ØªØ¨Ø±!", show_alert=True)
            else:
                await bot.answer_callback_query(call.id, "âš ï¸ Invalid data!", show_alert=True)
            return
        
        return await func(call, bot, data, lang, db_manager)
    return wrapper

async def handle_language_callback(call: types.CallbackQuery, bot: AsyncTeleBot, data: str, db_manager: DBManager):
    """
    Ù…Ø¯ÛŒØ±ÛŒØª Ø§Ù†ØªØ®Ø§Ø¨ Ø²Ø¨Ø§Ù† Ø§Ø² Ú©ÛŒØ¨ÙˆØ±Ø¯ Ø¯Ø±ÙˆÙ†â€ŒØ®Ø·ÛŒ
    Handles language selection from inline keyboard
    """
    try:
        new_lang = data
        old_lang = await get_lang(call.message.chat.id, call.from_user.id, db_manager)
        
        # Update language preference
        await set_lang(call.message.chat.id, call.from_user.id, new_lang, db_manager)
        
        # Get localized response
        if new_lang == "fa":
            response = "âœ… Ø²Ø¨Ø§Ù† Ø¨Ù‡ ÙØ§Ø±Ø³ÛŒ ØªØºÛŒÛŒØ± ÛŒØ§ÙØª"
            success_text = f"ðŸŒ **Ø§Ù†ØªØ®Ø§Ø¨ Ø²Ø¨Ø§Ù†**\n\nâœ… Ø²Ø¨Ø§Ù† Ø´Ù…Ø§ Ø¨Ø§ Ù…ÙˆÙÙ‚ÛŒØª Ø¨Ù‡ **ÙØ§Ø±Ø³ÛŒ** ØªØºÛŒÛŒØ± ÛŒØ§ÙØª!\n\nØ§Ú©Ù†ÙˆÙ† ØªÙ…Ø§Ù… Ù¾ÛŒØ§Ù…â€ŒÙ‡Ø§ Ùˆ Ù…Ù†ÙˆÙ‡Ø§ Ø¨Ù‡ Ø²Ø¨Ø§Ù† ÙØ§Ø±Ø³ÛŒ Ù†Ù…Ø§ÛŒØ´ Ø¯Ø§Ø¯Ù‡ Ø®ÙˆØ§Ù‡Ù†Ø¯ Ø´Ø¯."
        else:
            response = "âœ… Language changed to English"
            success_text = f"ðŸŒ **Language Selection**\n\nâœ… Your language has been successfully changed to **English**!\n\nAll messages and menus will now be displayed in English."
        
        await bot.answer_callback_query(call.id, text=response)
        
        # Create new language selection keyboard
        keyboard = types.InlineKeyboardMarkup()
        
        # Language options with flags and native names
        languages = [
            ("ðŸ‡ºðŸ‡¸ English", "en"),
            ("ðŸ‡®ðŸ‡· ÙØ§Ø±Ø³ÛŒ", "fa")
        ]
        
        for lang_display, lang_code in languages:
            if lang_code == new_lang:
                lang_display = f"âœ… {lang_display}"
            
            keyboard.add(types.InlineKeyboardButton(
                lang_display,
                callback_data=f"lang:{lang_code}"
            ))
        
        # Add close button
        if new_lang == "fa":
            keyboard.add(types.InlineKeyboardButton("âŒ Ø¨Ø³ØªÙ†", callback_data="do:delete_message"))
        else:
            keyboard.add(types.InlineKeyboardButton("âŒ Close", callback_data="do:delete_message"))
        
        # Update message
        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=success_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        logger.info(f"Language changed for user {call.from_user.id}: {old_lang} -> {new_lang}")
        logger.info(f"Ø²Ø¨Ø§Ù† Ú©Ø§Ø±Ø¨Ø± {call.from_user.id} ØªØºÛŒÛŒØ± ÛŒØ§ÙØª: {old_lang} -> {new_lang}")
        
    except Exception as e:
        logger.error(f"Error handling language callback: {e}")
        logger.error(f"Ø®Ø·Ø§ Ø¯Ø± Ù…Ø¯ÛŒØ±ÛŒØª Ú©Ø§Ù„Ø¨Ú© Ø²Ø¨Ø§Ù†: {e}")
        
        error_msg = "Ø®Ø·Ø§ Ø¯Ø± ØªØºÛŒÛŒØ± Ø²Ø¨Ø§Ù†!" if call.data == "fa" else "Error changing language!"
        await bot.answer_callback_query(call.id, error_msg, show_alert=True)
async def handle_callback_query(call, bot, db_manager: DBManager):
    """
    Ù…Ø¯ÛŒØ± Ø§ØµÙ„ÛŒ Ú©Ø§Ù„Ø¨Ú©â€ŒÙ‡Ø§ÛŒ Ú©ÙˆØ¦Ø±ÛŒ Ø¨Ø§ Ù‚Ø§Ø¨Ù„ÛŒØªâ€ŒÙ‡Ø§ÛŒ Ù¾ÛŒØ´Ø±ÙØªÙ‡
    Main callback query handler with enhanced functionality
    
    Args:
        call (telebot.types.CallbackQuery): Callback query
        bot (telebot.async_telebot.AsyncTeleBot): Bot instance
        db_manager (DBManager): Database manager instance
    """
    if not call.message:
        logger.warning("Callback query without message received")
        return
        
    logger.info(f"Callback query: {call.data} from {call.from_user.id} in {call.message.chat.id}")
    logger.info(f"Ú©Ø§Ù„Ø¨Ú© Ú©ÙˆØ¦Ø±ÛŒ: {call.data} Ø§Ø² {call.from_user.id} Ø¯Ø± {call.message.chat.id}")
    
    try:
        # Validate callback data format
        if ":" not in call.data:
            logger.warning(f"Invalid callback data format: {call.data}")
            await bot.answer_callback_query(call.id, "âš ï¸ Invalid format!")
            return
            
        action, data = call.data.split(":", 1)
        
        # Ensure user exists and get language
        await ensure_player(call.message.chat.id, call.from_user, db_manager)
        lang = await get_lang(call.message.chat.id, call.from_user.id, db_manager)
        
        # Create callback context
        context = CallbackContext(
            call=call,
            bot=bot,
            db_manager=db_manager,
            action=action,
            data=data,
            lang=lang,
            user_id=call.from_user.id,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            timestamp=time.time()
        )
        
        # Enhanced routing system with comprehensive handlers
        handlers = {
            "go": handle_navigation_action,           # Ù†Ø§ÙˆØ¨Ø±ÛŒ
            "do": handle_action_callback,             # Ø¹Ù…Ù„
            "buy": handle_purchase_callback,          # Ø®Ø±ÛŒØ¯
            "confirm": handle_confirmation_callback,   # ØªØ§ÛŒÛŒØ¯
            "cancel": handle_cancel_action,           # Ù„ØºÙˆ
            "page": handle_pagination_callback,       # ØµÙØ­Ù‡â€ŒØ¨Ù†Ø¯ÛŒ
            "lang": handle_language_callback,         # Ø²Ø¨Ø§Ù†
            "filter": handle_filter_callback,         # ÙÛŒÙ„ØªØ±
            "sort": handle_sort_callback,             # Ù…Ø±ØªØ¨â€ŒØ³Ø§Ø²ÛŒ
            "help": handle_help_callback,             # Ø±Ø§Ù‡Ù†Ù…Ø§
            "settings": handle_settings_callback,     # ØªÙ†Ø¸ÛŒÙ…Ø§Øª
            "admin": handle_admin_callback,           # Ù…Ø¯ÛŒØ±ÛŒØª
            "stars": handle_stars_callback,           # TG Stars system
            "attack": handle_attack_callback,         # Ø­Ù…Ù„Ù‡
            "defend": handle_defense_callback,        # Ø¯ÙØ§Ø¹
            "inv": handle_inventory_callback,         # Ù…ÙˆØ¬ÙˆØ¯ÛŒ
            "lead": handle_leaderboard_callback,      # Ù„ÛŒØ¯Ø±Ø¨ÙˆØ±Ø¯
            "profile": handle_profile_callback,       # Ù¾Ø±ÙˆÙØ§ÛŒÙ„
            "weapon": handle_weapon_callback,         # Ø³Ù„Ø§Ø­
            "item": handle_item_callback,             # Ø¢ÛŒØªÙ…
            "quick": handle_quick_action,             # Ø§Ù‚Ø¯Ø§Ù… Ø³Ø±ÛŒØ¹
        }
        
        handler = handlers.get(action)
        if handler:
            # Special handling for language callback
            if action == 'lang':
                await handler(call, bot, data, db_manager)
            else:
                await handler(call, bot, data, lang, db_manager)
        else:
            logger.warning(f"Unknown callback action: {action}")
            logger.warning(f"Ø¹Ù…Ù„ÛŒØ§Øª Ú©Ø§Ù„Ø¨Ú© Ù†Ø§Ø´Ù†Ø§Ø®ØªÙ‡: {action}")
            
            if lang == "fa":
                await bot.answer_callback_query(call.id, "âš ï¸ Ø¹Ù…Ù„ÛŒØ§Øª Ù†Ø§Ø´Ù†Ø§Ø®ØªÙ‡!", show_alert=True)
            else:
                await bot.answer_callback_query(call.id, "âš ï¸ Unknown action!", show_alert=True)
                
    except Exception as e:
        logger.error(f"Error handling callback query: {e}")
        logger.error(f"Ø®Ø·Ø§ Ø¯Ø± Ù…Ø¯ÛŒØ±ÛŒØª Ú©Ø§Ù„Ø¨Ú© Ú©ÙˆØ¦Ø±ÛŒ: {e}")
        
        try:
            lang = await get_lang(call.message.chat.id, call.from_user.id, db_manager)
            if lang == "fa":
                await bot.answer_callback_query(call.id, "âŒ Ø®Ø·Ø§ Ø¯Ø± Ù¾Ø±Ø¯Ø§Ø²Ø´ Ø¯Ø±Ø®ÙˆØ§Ø³Øª!", show_alert=True)
            else:
                await bot.answer_callback_query(call.id, "âŒ Error processing request!", show_alert=True)
        except:
            await bot.answer_callback_query(call.id, "âŒ Internal error!")

@owner_only
@rate_limit
@validate_data
async def handle_navigation_action(call, bot, data, lang, db_manager: DBManager):
    """
    Ù…Ø¯ÛŒØ±ÛŒØª Ø§Ù‚Ø¯Ø§Ù…Ø§Øª Ù†Ø§ÙˆØ¨Ø±ÛŒ Ù¾ÛŒØ´Ø±ÙØªÙ‡
    Handle enhanced navigation actions (go:xxx)
    """
    await bot.answer_callback_query(call.id)
    
    try:
        # Enhanced navigation mapping with module paths
        nav_actions = {
            "shop": ("src.commands.shop", "shop_command"),
            "inventory": ("src.commands.inventory", "inventory_command"),
            "inv": ("src.commands.inventory", "inventory_command"),
            "status": ("src.commands.status", "status_command"),
            "stars": ("src.commands.stars", "stars_command"),
            "stats": ("src.commands.stats", "stats_command"),
            "help": ("src.commands.help", "help_command"),
            "start": ("src.commands.general", "start_command"),
            "attack": ("src.commands.attack", "attack_command"),
            "profile": ("src.commands.general", "profile_command"),
            "leaderboard": ("src.commands.general", "leaderboard_command"),
            "settings": ("src.commands.general", "settings_command"),
            "weapons": ("src.commands.attack", "weapons_command"),
            "battle_stats": ("src.commands.attack", "battle_stats_command"),
            "main": ("src.commands.general", "start_command"),
            "menu": ("src.commands.general", "start_command"),
        }
        
        if data in nav_actions:
            module_path, func_name = nav_actions[data]
            
            try:
                module = __import__(module_path, fromlist=[func_name])
                command_func = getattr(module, func_name)
                
                # Handle special cases with different signatures
                if data in ["shop"]:
                    await command_func(call.message, bot, db_manager, is_callback=True)
                elif data in ["help"]:
                    await command_func(call.message, bot, db_manager, lang)
                else:
                    await command_func(call.message, bot, db_manager)
                    
                logger.info(f"Navigation to {data} completed for user {call.from_user.id}")
                logger.info(f"Ù†Ø§ÙˆØ¨Ø±ÛŒ Ø¨Ù‡ {data} Ø¨Ø±Ø§ÛŒ Ú©Ø§Ø±Ø¨Ø± {call.from_user.id} Ú©Ø§Ù…Ù„ Ø´Ø¯")
                
            except ImportError as e:
                logger.error(f"Failed to import module {module_path}: {e}")
                if lang == "fa":
                    await bot.answer_callback_query(call.id, "âŒ Ù…Ø§Ú˜ÙˆÙ„ Ø¯Ø± Ø¯Ø³ØªØ±Ø³ Ù†ÛŒØ³Øª!", show_alert=True)
                else:
                    await bot.answer_callback_query(call.id, "âŒ Module not available!", show_alert=True)
                    
            except AttributeError as e:
                logger.error(f"Function {func_name} not found in {module_path}: {e}")
                if lang == "fa":
                    await bot.answer_callback_query(call.id, "âŒ ØªØ§Ø¨Ø¹ Ø¯Ø± Ø¯Ø³ØªØ±Ø³ Ù†ÛŒØ³Øª!", show_alert=True)
                else:
                    await bot.answer_callback_query(call.id, "âŒ Function not available!", show_alert=True)
        else:
            logger.warning(f"Unknown navigation destination: {data}")
            logger.warning(f"Ù…Ù‚ØµØ¯ Ù†Ø§ÙˆØ¨Ø±ÛŒ Ù†Ø§Ø´Ù†Ø§Ø®ØªÙ‡: {data}")
            
            if lang == "fa":
                await bot.answer_callback_query(call.id, "âš ï¸ Ù…Ù‚ØµØ¯ Ù†Ø§Ø´Ù†Ø§Ø®ØªÙ‡!", show_alert=True)
            else:
                await bot.answer_callback_query(call.id, "âš ï¸ Unknown destination!", show_alert=True)
                
    except Exception as e:
        logger.error(f"Error in navigation action: {e}")
        logger.error(f"Ø®Ø·Ø§ Ø¯Ø± Ø§Ù‚Ø¯Ø§Ù… Ù†Ø§ÙˆØ¨Ø±ÛŒ: {e}")

@owner_only
@rate_limit 
@validate_data
async def handle_action_callback(call, bot, data, lang, db_manager: DBManager):
    """
    Ù…Ø¯ÛŒØ±ÛŒØª Ú©Ø§Ù„Ø¨Ú©â€ŒÙ‡Ø§ÛŒ Ø§Ù‚Ø¯Ø§Ù… Ù¾ÛŒØ´Ø±ÙØªÙ‡
    Handle enhanced action callbacks (do:xxx)
    """
    await bot.answer_callback_query(call.id)
    
    try:
        # Enhanced action handlers with comprehensive functionality
        action_handlers = {
            "attack": ("src.commands.attack", "attack_cmd"),
            "refresh_status": ("src.commands.status", "status_cmd"),
            "refresh_stars": ("src.commands.stars", "stars_cmd"),
            "refresh_inventory": ("src.commands.inventory", "inventory_cmd"),
            "refresh_stats": ("src.commands.stats", "stats_cmd"),
            "refresh_shop": ("src.commands.shop", "shop_cmd"),
            "refresh_help": ("src.commands.help", "help_cmd"),
            "refresh_leaderboard": ("src.commands.general", "leaderboard_cmd"),
            "heal": ("src.commands.status", "heal_cmd"),
            "use_defense": ("src.commands.inventory", "use_defense_cmd"),
            "show_profile": ("src.commands.general", "profile_cmd"),
            "change_language": ("src.commands.general", "language_cmd"),
        }
        
        if data in action_handlers:
            module_path, func_name = action_handlers[data]
            
            try:
                module = __import__(module_path, fromlist=[func_name])
                command_func = getattr(module, func_name)
                
                # Execute the command function
                if data.startswith("refresh_"):
                    if data == "refresh_shop":
                        await command_func(call.message, bot, db_manager, is_callback=True)
                    elif data == "refresh_help":
                        await command_func(call.message, bot, db_manager, lang)
                    else:
                        await command_func(call.message, bot, db_manager)
                else:
                    await command_func(call.message, bot, db_manager)
                    
                logger.info(f"Action {data} executed for user {call.from_user.id}")
                logger.info(f"Ø§Ù‚Ø¯Ø§Ù… {data} Ø¨Ø±Ø§ÛŒ Ú©Ø§Ø±Ø¨Ø± {call.from_user.id} Ø§Ø¬Ø±Ø§ Ø´Ø¯")
                
            except Exception as e:
                logger.error(f"Error executing action {data}: {e}")
                if lang == "fa":
                    await bot.answer_callback_query(call.id, "âŒ Ø®Ø·Ø§ Ø¯Ø± Ø§Ø¬Ø±Ø§ÛŒ Ø¹Ù…Ù„ÛŒØ§Øª!", show_alert=True)
                else:
                    await bot.answer_callback_query(call.id, "âŒ Error executing action!", show_alert=True)
                    
        elif data == "delete_message":
            try:
                await bot.delete_message(call.message.chat.id, call.message.message_id)
                logger.info(f"Message deleted by user {call.from_user.id}")
                logger.info(f"Ù¾ÛŒØ§Ù… ØªÙˆØ³Ø· Ú©Ø§Ø±Ø¨Ø± {call.from_user.id} Ø­Ø°Ù Ø´Ø¯")
            except Exception as e:
                logger.error(f"Error deleting message: {e}")
                logger.error(f"Ø®Ø·Ø§ Ø¯Ø± Ø­Ø°Ù Ù¾ÛŒØ§Ù…: {e}")
                
        elif data == "close_menu":
            try:
                if lang == "fa":
                    close_text = "âŒ Ù…Ù†Ùˆ Ø¨Ø³ØªÙ‡ Ø´Ø¯"
                else:
                    close_text = "âŒ Menu closed"
                    
                await bot.edit_message_text(
                    close_text,
                    call.message.chat.id,
                    call.message.message_id
                )
            except Exception as e:
                logger.error(f"Error closing menu: {e}")
                
        elif data == "back_to_main":
            from src.commands.general import start_cmd
            await start_cmd(call.message, bot, db_manager)
            
        else:
            logger.warning(f"Unknown action: {data}")
            logger.warning(f"Ø§Ù‚Ø¯Ø§Ù… Ù†Ø§Ø´Ù†Ø§Ø®ØªÙ‡: {data}")
            
            if lang == "fa":
                await bot.answer_callback_query(call.id, "âš ï¸ Ø§Ù‚Ø¯Ø§Ù… Ù†Ø§Ø´Ù†Ø§Ø®ØªÙ‡!", show_alert=True)
            else:
                await bot.answer_callback_query(call.id, "âš ï¸ Unknown action!", show_alert=True)
                
    except Exception as e:
        logger.error(f"Error in action callback: {e}")
        logger.error(f"Ø®Ø·Ø§ Ø¯Ø± Ú©Ø§Ù„Ø¨Ú© Ø§Ù‚Ø¯Ø§Ù…: {e}")

@rate_limit
@validate_data
async def handle_purchase_callback(call, bot, data, lang, db_manager: DBManager):
    """
    Ù…Ø¯ÛŒØ±ÛŒØª Ú©Ø§Ù„Ø¨Ú©â€ŒÙ‡Ø§ÛŒ Ø®Ø±ÛŒØ¯ Ù¾ÛŒØ´Ø±ÙØªÙ‡
    Handle enhanced purchase callbacks (buy:xxx)
    """
    try:
        from src.commands.shop import process_purchase
        await process_purchase(call, bot, data, lang, db_manager)
        
        logger.info(f"Purchase callback handled for user {call.from_user.id}: {data}")
        logger.info(f"Ú©Ø§Ù„Ø¨Ú© Ø®Ø±ÛŒØ¯ Ø¨Ø±Ø§ÛŒ Ú©Ø§Ø±Ø¨Ø± {call.from_user.id} Ù…Ø¯ÛŒØ±ÛŒØª Ø´Ø¯: {data}")
        
    except Exception as e:
        logger.error(f"Error in purchase callback: {e}")
        logger.error(f"Ø®Ø·Ø§ Ø¯Ø± Ú©Ø§Ù„Ø¨Ú© Ø®Ø±ÛŒØ¯: {e}")
        
        if lang == "fa":
            await bot.answer_callback_query(call.id, "âŒ Ø®Ø·Ø§ Ø¯Ø± Ù¾Ø±Ø¯Ø§Ø²Ø´ Ø®Ø±ÛŒØ¯!", show_alert=True)
        else:
            await bot.answer_callback_query(call.id, "âŒ Error processing purchase!", show_alert=True)

@owner_only
@rate_limit
@validate_data
async def handle_confirmation_callback(call, bot, data, lang, db_manager: DBManager):
    """
    Ù…Ø¯ÛŒØ±ÛŒØª Ú©Ø§Ù„Ø¨Ú©â€ŒÙ‡Ø§ÛŒ ØªØ§ÛŒÛŒØ¯ Ù¾ÛŒØ´Ø±ÙØªÙ‡
    Handle enhanced confirmation callbacks (confirm:xxx)
    """
    if ":" in data:
        action, item = data.split(":", 1)
        
        try:
            if action == "buy":
                from src.commands.shop import confirm_purchase
                await confirm_purchase(call, bot, item, lang, db_manager)
                
            elif action == "use":
                from src.commands.inventory import use_item
                await use_item(call, bot, item, lang, db_manager)
                
            elif action == "attack":
                from src.commands.attack import confirm_attack
                await confirm_attack(call, bot, item, lang, db_manager)
                
            elif action == "heal":
                from src.commands.status import confirm_heal
                await confirm_heal(call, bot, item, lang, db_manager)
                
            elif action == "delete_account":
                await handle_delete_account_confirmation(call, bot, lang, db_manager)
                
            else:
                logger.warning(f"Unknown confirmation action: {action}")
                logger.warning(f"Ø§Ù‚Ø¯Ø§Ù… ØªØ§ÛŒÛŒØ¯ Ù†Ø§Ø´Ù†Ø§Ø®ØªÙ‡: {action}")
                
                if lang == "fa":
                    await bot.answer_callback_query(call.id, "âš ï¸ Ø§Ù‚Ø¯Ø§Ù… ØªØ§ÛŒÛŒØ¯ Ù†Ø§Ø´Ù†Ø§Ø®ØªÙ‡!", show_alert=True)
                else:
                    await bot.answer_callback_query(call.id, "âš ï¸ Unknown confirmation action!", show_alert=True)
                    
        except Exception as e:
            logger.error(f"Error in confirmation action {action}: {e}")
            logger.error(f"Ø®Ø·Ø§ Ø¯Ø± Ø§Ù‚Ø¯Ø§Ù… ØªØ§ÛŒÛŒØ¯ {action}: {e}")
            
            if lang == "fa":
                await bot.answer_callback_query(call.id, "âŒ Ø®Ø·Ø§ Ø¯Ø± ØªØ§ÛŒÛŒØ¯ Ø¹Ù…Ù„ÛŒØ§Øª!", show_alert=True)
            else:
                await bot.answer_callback_query(call.id, "âŒ Error confirming operation!", show_alert=True)
    else:
        logger.warning(f"Invalid confirmation data format: {data}")
        logger.warning(f"ÙØ±Ù…Øª Ø¯Ø§Ø¯Ù‡ ØªØ§ÛŒÛŒØ¯ Ù†Ø§Ù…Ø¹ØªØ¨Ø±: {data}")
        
        if lang == "fa":
            await bot.answer_callback_query(call.id, "âš ï¸ ÙØ±Ù…Øª Ø¯Ø§Ø¯Ù‡ Ù†Ø§Ù…Ø¹ØªØ¨Ø±!", show_alert=True)
        else:
            await bot.answer_callback_query(call.id, "âš ï¸ Invalid data format!", show_alert=True)

@owner_only
@rate_limit
@validate_data
async def handle_cancel_action(call, bot, data, lang, db_manager: DBManager):
    """
    Ù…Ø¯ÛŒØ±ÛŒØª Ø§Ù‚Ø¯Ø§Ù…Ø§Øª Ù„ØºÙˆ Ù¾ÛŒØ´Ø±ÙØªÙ‡
    Handle enhanced cancel actions (cancel:xxx)
    """
    if lang == "fa":
        await bot.answer_callback_query(call.id, "âŒ Ø¹Ù…Ù„ÛŒØ§Øª Ù„ØºÙˆ Ø´Ø¯")
    else:
        await bot.answer_callback_query(call.id, "âŒ Operation cancelled")
    
    try:
        if data == "purchase":
            from src.commands.shop import shop_cmd
            await shop_cmd(call.message, bot, db_manager, is_callback=True)
            
        elif data == "stars_payment":
            from src.commands.stars import stars_cmd
            await stars_cmd(call.message, bot, db_manager)
            
        elif data == "attack":
            from src.commands.attack import attack_cmd
            await attack_cmd(call.message, bot, db_manager)
            
        elif data == "use_item":
            from src.commands.inventory import inventory_cmd
            await inventory_cmd(call.message, bot, db_manager)
            
        elif data == "settings":
            from src.commands.general import settings_cmd
            await settings_cmd(call.message, bot, db_manager)
            
        else:
            text = "âŒ Ø¹Ù…Ù„ÛŒØ§Øª Ù„ØºÙˆ Ø´Ø¯." if lang == "fa" else "âŒ Operation cancelled."
            try:
                await bot.edit_message_text(text, call.message.chat.id, call.message.message_id)
            except Exception as e:
                logger.error(f"Error editing message: {e}")
                
        logger.info(f"Cancel action {data} handled for user {call.from_user.id}")
        logger.info(f"Ø§Ù‚Ø¯Ø§Ù… Ù„ØºÙˆ {data} Ø¨Ø±Ø§ÛŒ Ú©Ø§Ø±Ø¨Ø± {call.from_user.id} Ù…Ø¯ÛŒØ±ÛŒØª Ø´Ø¯")
        
    except Exception as e:
        logger.error(f"Error in cancel action: {e}")
        logger.error(f"Ø®Ø·Ø§ Ø¯Ø± Ø§Ù‚Ø¯Ø§Ù… Ù„ØºÙˆ: {e}")

@rate_limit
@validate_data
async def handle_pagination_callback(call, bot, data, lang, db_manager: DBManager):
    """
    Ù…Ø¯ÛŒØ±ÛŒØª Ú©Ø§Ù„Ø¨Ú©â€ŒÙ‡Ø§ÛŒ ØµÙØ­Ù‡â€ŒØ¨Ù†Ø¯ÛŒ Ù¾ÛŒØ´Ø±ÙØªÙ‡
    Handle enhanced pagination callbacks (page:xxx)
    """
    parts = data.split(":")
    if len(parts) != 2:
        logger.warning(f"Invalid pagination data format: {data}")
        logger.warning(f"ÙØ±Ù…Øª Ø¯Ø§Ø¯Ù‡ ØµÙØ­Ù‡â€ŒØ¨Ù†Ø¯ÛŒ Ù†Ø§Ù…Ø¹ØªØ¨Ø±: {data}")
        
        if lang == "fa":
            await bot.answer_callback_query(call.id, "âš ï¸ ÙØ±Ù…Øª ØµÙØ­Ù‡â€ŒØ¨Ù†Ø¯ÛŒ Ù†Ø§Ù…Ø¹ØªØ¨Ø±!", show_alert=True)
        else:
            await bot.answer_callback_query(call.id, "âš ï¸ Invalid pagination format!", show_alert=True)
        return
    
    section, page_num_str = parts
    try:
        page_num = int(page_num_str)
    except ValueError:
        logger.warning(f"Invalid page number: {page_num_str}")
        logger.warning(f"Ø´Ù…Ø§Ø±Ù‡ ØµÙØ­Ù‡ Ù†Ø§Ù…Ø¹ØªØ¨Ø±: {page_num_str}")
        
        if lang == "fa":
            await bot.answer_callback_query(call.id, "âš ï¸ Ø´Ù…Ø§Ø±Ù‡ ØµÙØ­Ù‡ Ù†Ø§Ù…Ø¹ØªØ¨Ø±!", show_alert=True)
        else:
            await bot.answer_callback_query(call.id, "âš ï¸ Invalid page number!", show_alert=True)
        return
    
    await bot.answer_callback_query(call.id)
    
    try:
        if section == "shop":
            from src.commands.shop import show_shop_page
            await show_shop_page(call.message, bot, page_num, lang, db_manager)
            
        elif section == "inventory":
            from src.commands.inventory import show_inventory_page
            await show_inventory_page(call.message, bot, page_num, lang, db_manager)
            
        elif section == "leaderboard":
            from src.commands.general import show_leaderboard_page
            await show_leaderboard_page(call.message, bot, page_num, lang, db_manager)
            
        elif section == "help":
            from src.commands.help import show_help_page
            await show_help_page(call.message, bot, page_num, lang, db_manager)
            
        elif section == "weapons":
            from src.commands.attack import show_weapons_page
            await show_weapons_page(call.message, bot, page_num, lang, db_manager)
            
        else:
            logger.warning(f"Unknown pagination section: {section}")
            logger.warning(f"Ø¨Ø®Ø´ ØµÙØ­Ù‡â€ŒØ¨Ù†Ø¯ÛŒ Ù†Ø§Ø´Ù†Ø§Ø®ØªÙ‡: {section}")
            
    except Exception as e:
        logger.error(f"Error in pagination callback: {e}")
        logger.error(f"Ø®Ø·Ø§ Ø¯Ø± Ú©Ø§Ù„Ø¨Ú© ØµÙØ­Ù‡â€ŒØ¨Ù†Ø¯ÛŒ: {e}")

# =============================================================================
# Ù…Ø¯ÛŒØ±ÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡â€ŒÙ‡Ø§ÛŒ Ú©Ø§Ù„Ø¨Ú© Ø§Ø¶Ø§ÙÛŒ - Additional Callback Handlers
# =============================================================================

@rate_limit
@validate_data
async def handle_filter_callback(call, bot, data, lang, db_manager: DBManager):
    """Ù…Ø¯ÛŒØ±ÛŒØª ÙÛŒÙ„ØªØ±Ù‡Ø§ - Handle filters"""
    await bot.answer_callback_query(call.id)
    
    try:
        if data.startswith("shop_"):
            filter_type = data.replace("shop_", "")
            from src.commands.shop import apply_shop_filter
            await apply_shop_filter(call.message, bot, filter_type, lang, db_manager)
            
        elif data.startswith("inv_"):
            filter_type = data.replace("inv_", "")
            from src.commands.inventory import apply_inventory_filter
            await apply_inventory_filter(call.message, bot, filter_type, lang, db_manager)
            
    except Exception as e:
        logger.error(f"Error in filter callback: {e}")

@rate_limit
@validate_data
async def handle_sort_callback(call, bot, data, lang, db_manager: DBManager):
    """Ù…Ø¯ÛŒØ±ÛŒØª Ù…Ø±ØªØ¨â€ŒØ³Ø§Ø²ÛŒ - Handle sorting"""
    await bot.answer_callback_query(call.id)
    
    try:
        if data.startswith("leaderboard_"):
            sort_type = data.replace("leaderboard_", "")
            from src.commands.general import sort_leaderboard
            await sort_leaderboard(call.message, bot, sort_type, lang, db_manager)
            
    except Exception as e:
        logger.error(f"Error in sort callback: {e}")

@rate_limit
@validate_data
async def handle_help_callback(call, bot, data, lang, db_manager: DBManager):
    """Ù…Ø¯ÛŒØ±ÛŒØª Ø±Ø§Ù‡Ù†Ù…Ø§ - Handle help"""
    await bot.answer_callback_query(call.id)
    
    try:
        from src.commands.help import show_help_section
        await show_help_section(call.message, bot, data, lang, db_manager)
    except Exception as e:
        logger.error(f"Error in help callback: {e}")

@owner_only
@rate_limit
@validate_data
async def handle_settings_callback(call, bot, data, lang, db_manager: DBManager):
    """Ù…Ø¯ÛŒØ±ÛŒØª ØªÙ†Ø¸ÛŒÙ…Ø§Øª - Handle settings"""
    await bot.answer_callback_query(call.id)
    
    try:
        from src.commands.general import handle_settings
        await handle_settings(call.message, bot, data, lang, db_manager)
    except Exception as e:
        logger.error(f"Error in settings callback: {e}")

@rate_limit
@validate_data
async def handle_admin_callback(call, bot, data, lang, db_manager: DBManager):
    """Ù…Ø¯ÛŒØ±ÛŒØª Ø§Ø¯Ù…ÛŒÙ† - Handle admin actions"""
    # Check if user is admin
    if not await is_user_admin(call.from_user.id, call.message.chat.id, db_manager):
        if lang == "fa":
            await bot.answer_callback_query(call.id, "âš ï¸ Ø´Ù…Ø§ Ù…Ø¬Ø§Ø² Ø¨Ù‡ Ø§ÛŒÙ† Ø¹Ù…Ù„ÛŒØ§Øª Ù†ÛŒØ³ØªÛŒØ¯!", show_alert=True)
        else:
            await bot.answer_callback_query(call.id, "âš ï¸ You're not authorized for this action!", show_alert=True)
        return
    
    await bot.answer_callback_query(call.id)
    
    try:
        # Admin functionality placeholder - implement when admin module is available
        if lang == "fa":
            await bot.send_message(call.message.chat.id, "âš™ï¸ Ø¹Ù…Ù„Ú©Ø±Ø¯ Ø§Ø¯Ù…ÛŒÙ† Ø¯Ø± Ø­Ø§Ù„ ØªÙˆØ³Ø¹Ù‡ Ø§Ø³Øª...")
        else:
            await bot.send_message(call.message.chat.id, "âš™ï¸ Admin functionality under development...")
    except Exception as e:
        logger.error(f"Error in admin callback: {e}")

@owner_only
@rate_limit
@validate_data
async def handle_attack_callback(call, bot, data, lang, db_manager: DBManager):
    """Ù…Ø¯ÛŒØ±ÛŒØª Ø­Ù…Ù„Ù‡ - Handle attack actions"""
    await bot.answer_callback_query(call.id)
    
    try:
        from src.commands.attack import handle_attack_action
        await handle_attack_action(call.message, bot, data, lang, db_manager)
    except Exception as e:
        logger.error(f"Error in attack callback: {e}")

@owner_only
@rate_limit
@validate_data
async def handle_defense_callback(call, bot, data, lang, db_manager: DBManager):
    """Ù…Ø¯ÛŒØ±ÛŒØª Ø¯ÙØ§Ø¹ - Handle defense actions"""
    await bot.answer_callback_query(call.id)
    
    try:
        from src.commands.inventory import handle_defense_action
        await handle_defense_action(call.message, bot, data, lang, db_manager)
    except Exception as e:
        logger.error(f"Error in defense callback: {e}")

@owner_only
@rate_limit
@validate_data
async def handle_inventory_callback(call, bot, data, lang, db_manager: DBManager):
    """Ù…Ø¯ÛŒØ±ÛŒØª Ù…ÙˆØ¬ÙˆØ¯ÛŒ - Handle inventory actions"""
    await bot.answer_callback_query(call.id)
    
    try:
        from src.commands.inventory import handle_inventory_action
        await handle_inventory_action(call.message, bot, data, lang, db_manager)
    except Exception as e:
        logger.error(f"Error in inventory callback: {e}")

@rate_limit
@validate_data
async def handle_leaderboard_callback(call, bot, data, lang, db_manager: DBManager):
    """Ù…Ø¯ÛŒØ±ÛŒØª Ù„ÛŒØ¯Ø±Ø¨ÙˆØ±Ø¯ - Handle leaderboard actions"""
    await bot.answer_callback_query(call.id)
    
    try:
        from src.commands.general import handle_leaderboard_action
        await handle_leaderboard_action(call.message, bot, data, lang, db_manager)
    except Exception as e:
        logger.error(f"Error in leaderboard callback: {e}")

@owner_only
@rate_limit
@validate_data
async def handle_profile_callback(call, bot, data, lang, db_manager: DBManager):
    """Ù…Ø¯ÛŒØ±ÛŒØª Ù¾Ø±ÙˆÙØ§ÛŒÙ„ - Handle profile actions"""
    await bot.answer_callback_query(call.id)
    
    try:
        from src.commands.general import handle_profile_action
        await handle_profile_action(call.message, bot, data, lang, db_manager)
    except Exception as e:
        logger.error(f"Error in profile callback: {e}")

@rate_limit
@validate_data
async def handle_weapon_callback(call, bot, data, lang, db_manager: DBManager):
    """Ù…Ø¯ÛŒØ±ÛŒØª Ø³Ù„Ø§Ø­ - Handle weapon actions"""
    await bot.answer_callback_query(call.id)
    
    try:
        from src.commands.attack import handle_weapon_action
        await handle_weapon_action(call.message, bot, data, lang, db_manager)
    except Exception as e:
        logger.error(f"Error in weapon callback: {e}")

@rate_limit
@validate_data
async def handle_item_callback(call, bot, data, lang, db_manager: DBManager):
    """Ù…Ø¯ÛŒØ±ÛŒØª Ø¢ÛŒØªÙ… - Handle item actions"""
    await bot.answer_callback_query(call.id)
    
    try:
        from src.commands.inventory import handle_item_action
        await handle_item_action(call.message, bot, data, lang, db_manager)
    except Exception as e:
        logger.error(f"Error in item callback: {e}")

@owner_only
@rate_limit
@validate_data
async def handle_quick_action(call, bot, data, lang, db_manager: DBManager):
    """Ù…Ø¯ÛŒØ±ÛŒØª Ø§Ù‚Ø¯Ø§Ù…Ø§Øª Ø³Ø±ÛŒØ¹ - Handle quick actions"""
    await bot.answer_callback_query(call.id)
    
    try:
        quick_actions = {
            "stats": ("src.commands.stats", "stats_cmd"),
            "status": ("src.commands.status", "status_cmd"),
            "shop": ("src.commands.shop", "shop_cmd"),
            "inventory": ("src.commands.inventory", "inventory_cmd"),
            "attack": ("src.commands.attack", "attack_cmd"),
            "leaderboard": ("src.commands.general", "leaderboard_cmd"),
        }
        
        if data in quick_actions:
            module_path, func_name = quick_actions[data]
            module = __import__(module_path, fromlist=[func_name])
            command_func = getattr(module, func_name)
            
            if data == "shop":
                await command_func(call.message, bot, db_manager, is_callback=True)
            else:
                await command_func(call.message, bot, db_manager)
                
    except Exception as e:
        logger.error(f"Error in quick action: {e}")

async def handle_delete_account_confirmation(call, bot, lang, db_manager: DBManager):
    """Ù…Ø¯ÛŒØ±ÛŒØª ØªØ§ÛŒÛŒØ¯ Ø­Ø°Ù Ø­Ø³Ø§Ø¨ - Handle account deletion confirmation"""
    try:
        # Delete user data
        await db_manager.db(
            "DELETE FROM players WHERE chat_id = %s AND user_id = %s",
            (call.message.chat.id, call.from_user.id)
        )
        
        if lang == "fa":
            success_text = "âœ… Ø­Ø³Ø§Ø¨ Ø´Ù…Ø§ Ø¨Ø§ Ù…ÙˆÙÙ‚ÛŒØª Ø­Ø°Ù Ø´Ø¯!"
        else:
            success_text = "âœ… Your account has been successfully deleted!"
            
        await bot.edit_message_text(
            success_text,
            call.message.chat.id,
            call.message.message_id
        )
        
        logger.info(f"Account deleted for user {call.from_user.id}")
        logger.info(f"Ø­Ø³Ø§Ø¨ Ú©Ø§Ø±Ø¨Ø± {call.from_user.id} Ø­Ø°Ù Ø´Ø¯")
        
    except Exception as e:
        logger.error(f"Error deleting account: {e}")
        logger.error(f"Ø®Ø·Ø§ Ø¯Ø± Ø­Ø°Ù Ø­Ø³Ø§Ø¨: {e}")

# =============================================================================
# ØªÙˆØ§Ø¨Ø¹ Ú©Ù…Ú©ÛŒ - Helper Functions
# =============================================================================

async def is_user_admin(user_id: int, chat_id: int, db_manager: DBManager) -> bool:
    """Ø¨Ø±Ø±Ø³ÛŒ Ø§Ø¯Ù…ÛŒÙ† Ø¨ÙˆØ¯Ù† Ú©Ø§Ø±Ø¨Ø± - Check if user is admin"""
    try:
        # Check if user is bot admin (you can customize this)
        admin_ids = [123456789]  # Add your admin IDs here
        return user_id in admin_ids
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False

async def log_callback_usage(call: types.CallbackQuery, action: str, data: str):
    """Ø«Ø¨Øª Ø§Ø³ØªÙØ§Ø¯Ù‡ Ø§Ø² Ú©Ø§Ù„Ø¨Ú© - Log callback usage"""
    try:
        usage_data = {
            'user_id': call.from_user.id,
            'chat_id': call.message.chat.id,
            'action': action,
            'data': data,
            'timestamp': time.time()
        }
        
        # You can save this to database or file for analytics
        logger.info(f"Callback usage: {usage_data}")
        logger.info(f"Ø§Ø³ØªÙØ§Ø¯Ù‡ Ø§Ø² Ú©Ø§Ù„Ø¨Ú©: {usage_data}")
        
    except Exception as e:
        logger.error(f"Error logging callback usage: {e}")

async def create_error_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    """Ø§ÛŒØ¬Ø§Ø¯ Ú©ÛŒØ¨ÙˆØ±Ø¯ Ø®Ø·Ø§ - Create error keyboard"""
    keyboard = types.InlineKeyboardMarkup()
    
    if lang == "fa":
        keyboard.add(
            types.InlineKeyboardButton("ðŸ”„ ØªÙ„Ø§Ø´ Ù…Ø¬Ø¯Ø¯", callback_data="do:retry"),
            types.InlineKeyboardButton("ðŸ  Ù…Ù†ÙˆÛŒ Ø§ØµÙ„ÛŒ", callback_data="go:main")
        )
        keyboard.add(types.InlineKeyboardButton("âŒ Ø¨Ø³ØªÙ†", callback_data="do:delete_message"))
    else:
        keyboard.add(
            types.InlineKeyboardButton("ðŸ”„ Retry", callback_data="do:retry"),
            types.InlineKeyboardButton("ðŸ  Main Menu", callback_data="go:main")
        )
        keyboard.add(types.InlineKeyboardButton("âŒ Close", callback_data="do:delete_message"))
    
    return keyboard

def register_callback_handlers(bot, db_manager: DBManager):
    """
    Ø«Ø¨Øª Ù…Ø¯ÛŒØ±ÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡â€ŒÙ‡Ø§ÛŒ Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ú©Ø§Ù„Ø¨Ú© Ú©ÙˆØ¦Ø±ÛŒ
    Register enhanced callback query handlers with comprehensive functionality
    
    Args:
        bot (telebot.async_telebot.AsyncTeleBot): Bot instance
        db_manager (DBManager): Database manager instance
    """
    logger.info("Registering enhanced callback query handlers")
    logger.info("Ø«Ø¨Øª Ù…Ø¯ÛŒØ±ÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡â€ŒÙ‡Ø§ÛŒ Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ú©Ø§Ù„Ø¨Ú© Ú©ÙˆØ¦Ø±ÛŒ")
    
    # Register global callback handler with comprehensive error handling
    @bot.callback_query_handler(func=lambda call: True)
    async def main_callback_handler(call):
        """
        Ù…Ø¯ÛŒØ±ÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡ Ø§ØµÙ„ÛŒ Ú©Ø§Ù„Ø¨Ú© Ø¨Ø§ Ù…Ø¯ÛŒØ±ÛŒØª Ø®Ø·Ø§ÛŒ Ù¾ÛŒØ´Ø±ÙØªÙ‡
        Main callback handler with advanced error management
        """
        try:
            # Log callback usage for analytics
            await log_callback_usage(call, call.data.split(':')[0] if ':' in call.data else 'unknown', call.data)
            
            # Handle the callback
            await handle_callback_query(call, bot, db_manager)
            
        except Exception as e:
            logger.error(f"Critical error in callback handler: {e}")
            logger.error(f"Ø®Ø·Ø§ÛŒ Ø­Ø§Ø¯ Ø¯Ø± Ù…Ø¯ÛŒØ±ÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡ Ú©Ø§Ù„Ø¨Ú©: {e}")
            
            # Try to send error message to user
            try:
                lang = await get_lang(call.message.chat.id, call.from_user.id, db_manager)
                
                if lang == "fa":
                    error_text = "âŒ Ø®Ø·Ø§ÛŒ Ø¯Ø§Ø®Ù„ÛŒ Ø³ÛŒØ³ØªÙ…!\n\nÙ„Ø·ÙØ§Ù‹ Ù…Ø¬Ø¯Ø¯Ø§Ù‹ ØªÙ„Ø§Ø´ Ú©Ù†ÛŒØ¯ ÛŒØ§ Ø¨Ø§ Ù¾Ø´ØªÛŒØ¨Ø§Ù†ÛŒ ØªÙ…Ø§Ø³ Ø¨Ú¯ÛŒØ±ÛŒØ¯."
                else:
                    error_text = "âŒ Internal system error!\n\nPlease try again or contact support."
                
                error_keyboard = await create_error_keyboard(lang)
                
                await bot.edit_message_text(
                    error_text,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=error_keyboard
                )
                
            except Exception as edit_error:
                logger.error(f"Failed to edit message with error: {edit_error}")
                
                # Last resort - answer callback query
                try:
                    await bot.answer_callback_query(
                        call.id, 
                        "âŒ System error!", 
                        show_alert=True
                    )
                except Exception as answer_error:
                    logger.error(f"Failed to answer callback query: {answer_error}")

# =============================================================================
# Ù…Ø§Ú˜ÙˆÙ„ ØªØ­Ù„ÛŒÙ„ Ø¹Ù…Ù„Ú©Ø±Ø¯ Ú©Ø§Ù„Ø¨Ú© - Callback Performance Analytics Module
# =============================================================================

class CallbackAnalytics:
    """ØªØ­Ù„ÛŒÙ„â€ŒÚ¯Ø± Ø¹Ù…Ù„Ú©Ø±Ø¯ Ú©Ø§Ù„Ø¨Ú© - Callback Performance Analyzer"""
    
    def __init__(self):
        self.callback_stats: Dict[str, Dict[str, Any]] = {}
        self.response_times: Dict[str, List[float]] = {}
        self.error_counts: Dict[str, int] = {}
        
    def record_callback(self, action: str, response_time: float, success: bool):
        """Ø«Ø¨Øª Ø¢Ù…Ø§Ø± Ú©Ø§Ù„Ø¨Ú© - Record callback statistics"""
        if action not in self.callback_stats:
            self.callback_stats[action] = {
                'total_calls': 0,
                'successful_calls': 0,
                'failed_calls': 0,
                'avg_response_time': 0.0
            }
        
        if action not in self.response_times:
            self.response_times[action] = []
        
        # Update statistics
        self.callback_stats[action]['total_calls'] += 1
        if success:
            self.callback_stats[action]['successful_calls'] += 1
        else:
            self.callback_stats[action]['failed_calls'] += 1
            self.error_counts[action] = self.error_counts.get(action, 0) + 1
        
        # Record response time
        self.response_times[action].append(response_time)
        
        # Keep only last 100 response times
        if len(self.response_times[action]) > 100:
            self.response_times[action] = self.response_times[action][-100:]
        
        # Update average response time
        self.callback_stats[action]['avg_response_time'] = sum(self.response_times[action]) / len(self.response_times[action])
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Ø¯Ø±ÛŒØ§ÙØª Ú¯Ø²Ø§Ø±Ø´ Ø¹Ù…Ù„Ú©Ø±Ø¯ - Get performance report"""
        report = {
            'total_callbacks': sum(stats['total_calls'] for stats in self.callback_stats.values()),
            'total_errors': sum(self.error_counts.values()),
            'actions': {}
        }
        
        for action, stats in self.callback_stats.items():
            success_rate = (stats['successful_calls'] / stats['total_calls']) * 100 if stats['total_calls'] > 0 else 0
            
            report['actions'][action] = {
                'total_calls': stats['total_calls'],
                'success_rate': round(success_rate, 2),
                'avg_response_time': round(stats['avg_response_time'], 3),
                'error_count': self.error_counts.get(action, 0)
            }
        
        return report

# Global analytics instance
callback_analytics = CallbackAnalytics()

# =============================================================================
# Ù…Ø¯ÛŒØ±ÛŒØª Ú©Ø´ Ú©Ø§Ù„Ø¨Ú© - Callback Cache Management
# =============================================================================

class CallbackCache:
    """Ù…Ø¯ÛŒØ± Ú©Ø´ Ú©Ø§Ù„Ø¨Ú© - Callback Cache Manager"""
    
    def __init__(self, ttl: int = 300):  # 5 minutes TTL
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Ø¯Ø±ÛŒØ§ÙØª Ø§Ø² Ú©Ø´ - Get from cache"""
        if key in self.cache:
            if time.time() - self.cache[key]['timestamp'] < self.ttl:
                return self.cache[key]['data']
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, data: Any):
        """ØªÙ†Ø¸ÛŒÙ… Ø¯Ø± Ú©Ø´ - Set in cache"""
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def clear_expired(self):
        """Ù¾Ø§Ú©â€ŒØ³Ø§Ø²ÛŒ Ú©Ø´ Ù…Ù†Ù‚Ø¶ÛŒ - Clear expired cache"""
        current_time = time.time()
        expired_keys = [
            key for key, value in self.cache.items()
            if current_time - value['timestamp'] >= self.ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Ø¯Ø±ÛŒØ§ÙØª Ø¢Ù…Ø§Ø± Ú©Ø´ - Get cache statistics"""
        return {
            'total_entries': len(self.cache),
            'memory_usage': sum(len(str(value)) for value in self.cache.values()),
            'cache_keys': list(self.cache.keys())
        }

# Global cache instance
callback_cache = CallbackCache()

# =============================================================================
# ØªÙ†Ø¸ÛŒÙ…Ø§Øª Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ú©Ø§Ù„Ø¨Ú© - Advanced Callback Configuration
# =============================================================================

class CallbackConfig:
    """Ù¾ÛŒÚ©Ø±Ø¨Ù†Ø¯ÛŒ Ú©Ø§Ù„Ø¨Ú© - Callback Configuration"""
    
    # Rate limiting settings
    MAX_CALLBACKS_PER_MINUTE = 30
    RATE_LIMIT_BLOCK_DURATION = 300  # 5 minutes
    
    # Cache settings
    CACHE_TTL = 300  # 5 minutes
    CACHE_MAX_ENTRIES = 1000
    
    # Security settings
    MAX_CALLBACK_DATA_LENGTH = 64
    ALLOWED_CALLBACK_PATTERNS = [
        r'^[a-zA-Z0-9_:.-]+$'  # Alphanumeric with specific special chars
    ]
    
    # Performance settings
    MAX_RESPONSE_TIME = 5.0  # seconds
    ENABLE_ANALYTICS = True
    ENABLE_CACHING = True
    
    # Language settings
    DEFAULT_LANGUAGE = 'en'
    SUPPORTED_LANGUAGES = ['en', 'fa']
    
    # Error handling
    MAX_RETRY_ATTEMPTS = 3
    ERROR_COOLDOWN = 60  # seconds

# Global configuration
callback_config = CallbackConfig()

# =============================================================================
# ÙˆØ§Ø¨ØµØ§Ø¯Ø±Ø§Øª Ù…Ø§Ú˜ÙˆÙ„ - Module Exports
# =============================================================================

__all__ = [
    # Core handlers
    'handle_callback_query',
    'handle_language_callback',
    'handle_navigation_action',
    'handle_action_callback',
    'handle_purchase_callback',
    'handle_confirmation_callback',
    'handle_cancel_action',
    'handle_pagination_callback',
    
    # Specialized handlers
    'handle_filter_callback',
    'handle_sort_callback',
    'handle_help_callback',
    'handle_settings_callback',
    'handle_admin_callback',
    'handle_attack_callback',
    'handle_defense_callback',
    'handle_inventory_callback',
    'handle_leaderboard_callback',
    'handle_profile_callback',
    'handle_weapon_callback',
    'handle_item_callback',
    'handle_quick_action',
    
    # Security and decorators
    'owner_only',
    'rate_limit',
    'validate_data',
    'CallbackSecurity',
    
    # Analytics and caching
    'CallbackAnalytics',
    'CallbackCache',
    'callback_analytics',
    'callback_cache',
    
    # Configuration
    'CallbackConfig',
    'callback_config',
    
    # Registration
    'register_callback_handlers',
    'register_handlers',  # Alias for compatibility
    
    # Data classes
    'CallbackAction',
    'CallbackContext'
]

# Initialization message
logger.info("Enhanced Callback Handlers Module loaded successfully")
logger.info("Ù…Ø§Ú˜ÙˆÙ„ Ù…Ø¯ÛŒØ±ÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡â€ŒÙ‡Ø§ÛŒ Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ú©Ø§Ù„Ø¨Ú© Ø¨Ø§ Ù…ÙˆÙÙ‚ÛŒØª Ø¨Ø§Ø±Ú¯Ø°Ø§Ø±ÛŒ Ø´Ø¯")

# Performance monitoring setup
logger.info(f"Callback performance monitoring: {'enabled' if callback_config.ENABLE_ANALYTICS else 'disabled'}")
logger.info(f"Callback caching: {'enabled' if callback_config.ENABLE_CACHING else 'disabled'}")
logger.info(f"Ù†Ø¸Ø§Ø±Øª Ø¨Ø± Ø¹Ù…Ù„Ú©Ø±Ø¯ Ú©Ø§Ù„Ø¨Ú©: {'ÙØ¹Ø§Ù„' if callback_config.ENABLE_ANALYTICS else 'ØºÛŒØ±ÙØ¹Ø§Ù„'}")
logger.info(f"Ú©Ø´ Ú©Ø§Ù„Ø¨Ú©: {'ÙØ¹Ø§Ù„' if callback_config.ENABLE_CACHING else 'ØºÛŒØ±ÙØ¹Ø§Ù„'}")

# Alias for compatibility with app.py
def register_handlers(bot: AsyncTeleBot, db_manager) -> None:
    """
    Alias for register_callback_handlers to maintain compatibility
    Ù†Ø§Ù… Ù…Ø³ØªØ¹Ø§Ø± Ø¨Ø±Ø§ÛŒ register_callback_handlers Ø¨Ø±Ø§ÛŒ Ø­ÙØ¸ Ø³Ø§Ø²Ú¯Ø§Ø±ÛŒ
    """
    return register_callback_handlers(bot, db_manager)

