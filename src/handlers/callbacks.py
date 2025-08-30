#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
پردازش‌کننده‌های پیشرفته کالبک با پشتیبانی کامل از زبان فارسی
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
from src.commands.stars import handle_stars_amount_selection, handle_stars_payment_processing, handle_tg_stars_received

# Set up logging
logger = logging.getLogger(__name__)

class CallbackAction(Enum):
    """انواع عملیات کالبک - Callback Action Types"""
    NAVIGATION = "go"          # ناوبری - Navigation
    ACTION = "do"              # عمل - Action
    PURCHASE = "buy"           # خرید - Purchase
    CONFIRM = "confirm"        # تایید - Confirmation
    CANCEL = "cancel"          # لغو - Cancel
    PAGINATION = "page"        # صفحه‌بندی - Pagination
    LANGUAGE = "lang"          # زبان - Language
    FILTER = "filter"          # فیلتر - Filter
    SORT = "sort"              # مرتب‌سازی - Sort
    HELP = "help"              # راهنما - Help
    SETTINGS = "settings"      # تنظیمات - Settings
    ADMIN = "admin"            # مدیریت - Admin
    STARS = "stars"            # ستاره‌ها - Stars
    ATTACK = "attack"          # حمله - Attack
    DEFEND = "defend"          # دفاع - Defense
    INVENTORY = "inv"          # موجودی - Inventory
    LEADERBOARD = "lead"       # لیدربورد - Leaderboard

@dataclass
class CallbackContext:
    """بافت کالبک - Callback Context"""
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
    """امنیت کالبک - Callback Security Manager"""
    
    def __init__(self):
        self.rate_limits: Dict[int, List[float]] = {}
        self.max_requests_per_minute = 30
        self.blocked_users: Dict[int, float] = {}
        self.block_duration = 300  # 5 minutes
    
    def is_rate_limited(self, user_id: int) -> bool:
        """بررسی محدودیت نرخ - Check rate limiting"""
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
            logger.warning(f"کاربر {user_id} به دلیل محدودیت نرخ مسدود شد")
            return True
        
        # Add current request
        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = []
        self.rate_limits[user_id].append(current_time)
        
        return False
    
    def validate_callback_data(self, data: str) -> bool:
        """اعتبارسنجی داده کالبک - Validate callback data"""
        if not data or len(data) > 64:  # Telegram limit
            return False
        
        # Check for malicious patterns
        malicious_patterns = ['<script', 'javascript:', 'data:', 'vbscript:']
        return not any(pattern in data.lower() for pattern in malicious_patterns)

# Global security instance
callback_security = CallbackSecurity()

def owner_only(func):
    """
    دکوریتر برای اطمینان از اینکه فقط صاحب پیام می‌تواند از کالبک استفاده کند
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
                    "⚠️ این دکمه‌ها فقط برای کاربری است که پیام را ارسال کرده!", 
                    show_alert=True
                )
            else:
                await bot.answer_callback_query(
                    call.id, 
                    "⚠️ These buttons are only for the user who sent the message!", 
                    show_alert=True
                )
            return
            
        return await func(call, bot, data, lang, db_manager)
    return wrapper

def rate_limit(func):
    """
    دکوریتر محدودیت نرخ برای جلوگیری از سوءاستفاده
    Rate limiting decorator to prevent abuse
    """
    @wraps(func)
    async def wrapper(call, bot, data, lang, db_manager):
        if callback_security.is_rate_limited(call.from_user.id):
            if lang == "fa":
                await bot.answer_callback_query(
                    call.id,
                    "⚠️ شما خیلی سریع درخواست می‌دهید! لطفاً کمی صبر کنید.",
                    show_alert=True
                )
            else:
                await bot.answer_callback_query(
                    call.id,
                    "⚠️ You're making requests too quickly! Please wait a moment.",
                    show_alert=True
                )
            return
        
        return await func(call, bot, data, lang, db_manager)
    return wrapper

def validate_data(func):
    """
    دکوریتر اعتبارسنجی داده‌های کالبک
    Callback data validation decorator
    """
    @wraps(func)
    async def wrapper(call, bot, data, lang, db_manager):
        if not callback_security.validate_callback_data(data):
            logger.warning(f"Invalid callback data from user {call.from_user.id}: {data}")
            logger.warning(f"داده کالبک نامعتبر از کاربر {call.from_user.id}: {data}")
            
            if lang == "fa":
                await bot.answer_callback_query(call.id, "⚠️ داده نامعتبر!", show_alert=True)
            else:
                await bot.answer_callback_query(call.id, "⚠️ Invalid data!", show_alert=True)
            return
        
        return await func(call, bot, data, lang, db_manager)
    return wrapper

async def handle_language_callback(call: types.CallbackQuery, bot: AsyncTeleBot, data: str, db_manager: DBManager):
    """
    مدیریت انتخاب زبان از کیبورد درون‌خطی
    Handles language selection from inline keyboard
    """
    try:
        new_lang = data
        old_lang = await get_lang(call.message.chat.id, call.from_user.id, db_manager)
        
        # Update language preference
        await set_lang(call.message.chat.id, call.from_user.id, new_lang, db_manager)
        
        # Get localized response
        if new_lang == "fa":
            response = "✅ زبان به فارسی تغییر یافت"
            success_text = f"🌐 **انتخاب زبان**\n\n✅ زبان شما با موفقیت به **فارسی** تغییر یافت!\n\nاکنون تمام پیام‌ها و منوها به زبان فارسی نمایش داده خواهند شد."
        else:
            response = "✅ Language changed to English"
            success_text = f"🌐 **Language Selection**\n\n✅ Your language has been successfully changed to **English**!\n\nAll messages and menus will now be displayed in English."
        
        await bot.answer_callback_query(call.id, text=response)
        
        # Create new language selection keyboard
        keyboard = types.InlineKeyboardMarkup()
        
        # Language options with flags and native names
        languages = [
            ("🇺🇸 English", "en"),
            ("🇮🇷 فارسی", "fa")
        ]
        
        for lang_display, lang_code in languages:
            if lang_code == new_lang:
                lang_display = f"✅ {lang_display}"
            
            keyboard.add(types.InlineKeyboardButton(
                lang_display,
                callback_data=f"lang:{lang_code}"
            ))
        
        # Add close button
        if new_lang == "fa":
            keyboard.add(types.InlineKeyboardButton("❌ بستن", callback_data="do:delete_message"))
        else:
            keyboard.add(types.InlineKeyboardButton("❌ Close", callback_data="do:delete_message"))
        
        # Update message
        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=success_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        logger.info(f"Language changed for user {call.from_user.id}: {old_lang} -> {new_lang}")
        logger.info(f"زبان کاربر {call.from_user.id} تغییر یافت: {old_lang} -> {new_lang}")
        
    except Exception as e:
        logger.error(f"Error handling language callback: {e}")
        logger.error(f"خطا در مدیریت کالبک زبان: {e}")
        
        error_msg = "خطا در تغییر زبان!" if call.data == "fa" else "Error changing language!"
        await bot.answer_callback_query(call.id, error_msg, show_alert=True)
async def handle_callback_query(call, bot, db_manager: DBManager):
    """
    مدیر اصلی کالبک‌های کوئری با قابلیت‌های پیشرفته
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
    logger.info(f"کالبک کوئری: {call.data} از {call.from_user.id} در {call.message.chat.id}")
    
    try:
        # Validate callback data format
        if ":" not in call.data:
            logger.warning(f"Invalid callback data format: {call.data}")
            await bot.answer_callback_query(call.id, "⚠️ Invalid format!")
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
            "go": handle_navigation_action,           # ناوبری
            "do": handle_action_callback,             # عمل
            "buy": handle_purchase_callback,          # خرید
            "confirm": handle_confirmation_callback,   # تایید
            "cancel": handle_cancel_action,           # لغو
            "page": handle_pagination_callback,       # صفحه‌بندی
            "lang": handle_language_callback,         # زبان
            "filter": handle_filter_callback,         # فیلتر
            "sort": handle_sort_callback,             # مرتب‌سازی
            "help": handle_help_callback,             # راهنما
            "settings": handle_settings_callback,     # تنظیمات
            "admin": handle_admin_callback,           # مدیریت
            "stars_amount": handle_stars_amount_selection,
            "stars_payment": handle_stars_payment_processing,
            "tg_stars_received": handle_tg_stars_received,
            "attack": handle_attack_callback,         # حمله
            "defend": handle_defense_callback,        # دفاع
            "inv": handle_inventory_callback,         # موجودی
            "lead": handle_leaderboard_callback,      # لیدربورد
            "profile": handle_profile_callback,       # پروفایل
            "weapon": handle_weapon_callback,         # سلاح
            "item": handle_item_callback,             # آیتم
            "quick": handle_quick_action,             # اقدام سریع
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
            logger.warning(f"عملیات کالبک ناشناخته: {action}")
            
            if lang == "fa":
                await bot.answer_callback_query(call.id, "⚠️ عملیات ناشناخته!", show_alert=True)
            else:
                await bot.answer_callback_query(call.id, "⚠️ Unknown action!", show_alert=True)
                
    except Exception as e:
        logger.error(f"Error handling callback query: {e}")
        logger.error(f"خطا در مدیریت کالبک کوئری: {e}")
        
        try:
            lang = await get_lang(call.message.chat.id, call.from_user.id, db_manager)
            if lang == "fa":
                await bot.answer_callback_query(call.id, "❌ خطا در پردازش درخواست!", show_alert=True)
            else:
                await bot.answer_callback_query(call.id, "❌ Error processing request!", show_alert=True)
        except:
            await bot.answer_callback_query(call.id, "❌ Internal error!")

@owner_only
@rate_limit
@validate_data
async def handle_navigation_action(call, bot, data, lang, db_manager: DBManager):
    """
    مدیریت اقدامات ناوبری پیشرفته
    Handle enhanced navigation actions (go:xxx)
    """
    await bot.answer_callback_query(call.id)
    
    try:
        # Enhanced navigation mapping with module paths
        nav_actions = {
            "shop": ("src.commands.shop", "shop_cmd"),
            "inventory": ("src.commands.inventory", "inventory_cmd"),
            "inv": ("src.commands.inventory", "inventory_cmd"),
            "status": ("src.commands.status", "status_cmd"),
            "stars": ("src.commands.stars", "stars_cmd"),
            "stats": ("src.commands.stats", "stats_cmd"),
            "help": ("src.commands.help", "help_cmd"),
            "start": ("src.commands.general", "start_cmd"),
            "attack": ("src.commands.attack", "attack_cmd"),
            "profile": ("src.commands.general", "profile_cmd"),
            "leaderboard": ("src.commands.general", "leaderboard_cmd"),
            "settings": ("src.commands.general", "settings_cmd"),
            "weapons": ("src.commands.attack", "weapons_cmd"),
            "battle_stats": ("src.commands.attack", "battle_stats_cmd"),
            "main": ("src.commands.general", "start_cmd"),
            "menu": ("src.commands.general", "start_cmd"),
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
                logger.info(f"ناوبری به {data} برای کاربر {call.from_user.id} کامل شد")
                
            except ImportError as e:
                logger.error(f"Failed to import module {module_path}: {e}")
                if lang == "fa":
                    await bot.answer_callback_query(call.id, "❌ ماژول در دسترس نیست!", show_alert=True)
                else:
                    await bot.answer_callback_query(call.id, "❌ Module not available!", show_alert=True)
                    
            except AttributeError as e:
                logger.error(f"Function {func_name} not found in {module_path}: {e}")
                if lang == "fa":
                    await bot.answer_callback_query(call.id, "❌ تابع در دسترس نیست!", show_alert=True)
                else:
                    await bot.answer_callback_query(call.id, "❌ Function not available!", show_alert=True)
        else:
            logger.warning(f"Unknown navigation destination: {data}")
            logger.warning(f"مقصد ناوبری ناشناخته: {data}")
            
            if lang == "fa":
                await bot.answer_callback_query(call.id, "⚠️ مقصد ناشناخته!", show_alert=True)
            else:
                await bot.answer_callback_query(call.id, "⚠️ Unknown destination!", show_alert=True)
                
    except Exception as e:
        logger.error(f"Error in navigation action: {e}")
        logger.error(f"خطا در اقدام ناوبری: {e}")

@owner_only
@rate_limit 
@validate_data
async def handle_action_callback(call, bot, data, lang, db_manager: DBManager):
    """
    مدیریت کالبک‌های اقدام پیشرفته
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
                logger.info(f"اقدام {data} برای کاربر {call.from_user.id} اجرا شد")
                
            except Exception as e:
                logger.error(f"Error executing action {data}: {e}")
                if lang == "fa":
                    await bot.answer_callback_query(call.id, "❌ خطا در اجرای عملیات!", show_alert=True)
                else:
                    await bot.answer_callback_query(call.id, "❌ Error executing action!", show_alert=True)
                    
        elif data == "delete_message":
            try:
                await bot.delete_message(call.message.chat.id, call.message.message_id)
                logger.info(f"Message deleted by user {call.from_user.id}")
                logger.info(f"پیام توسط کاربر {call.from_user.id} حذف شد")
            except Exception as e:
                logger.error(f"Error deleting message: {e}")
                logger.error(f"خطا در حذف پیام: {e}")
                
        elif data == "close_menu":
            try:
                if lang == "fa":
                    close_text = "❌ منو بسته شد"
                else:
                    close_text = "❌ Menu closed"
                    
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
            logger.warning(f"اقدام ناشناخته: {data}")
            
            if lang == "fa":
                await bot.answer_callback_query(call.id, "⚠️ اقدام ناشناخته!", show_alert=True)
            else:
                await bot.answer_callback_query(call.id, "⚠️ Unknown action!", show_alert=True)
                
    except Exception as e:
        logger.error(f"Error in action callback: {e}")
        logger.error(f"خطا در کالبک اقدام: {e}")

@rate_limit
@validate_data
async def handle_purchase_callback(call, bot, data, lang, db_manager: DBManager):
    """
    مدیریت کالبک‌های خرید پیشرفته
    Handle enhanced purchase callbacks (buy:xxx)
    """
    try:
        from src.commands.shop import process_purchase
        await process_purchase(call, bot, data, lang, db_manager)
        
        logger.info(f"Purchase callback handled for user {call.from_user.id}: {data}")
        logger.info(f"کالبک خرید برای کاربر {call.from_user.id} مدیریت شد: {data}")
        
    except Exception as e:
        logger.error(f"Error in purchase callback: {e}")
        logger.error(f"خطا در کالبک خرید: {e}")
        
        if lang == "fa":
            await bot.answer_callback_query(call.id, "❌ خطا در پردازش خرید!", show_alert=True)
        else:
            await bot.answer_callback_query(call.id, "❌ Error processing purchase!", show_alert=True)

@owner_only
@rate_limit
@validate_data
async def handle_confirmation_callback(call, bot, data, lang, db_manager: DBManager):
    """
    مدیریت کالبک‌های تایید پیشرفته
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
                logger.warning(f"اقدام تایید ناشناخته: {action}")
                
                if lang == "fa":
                    await bot.answer_callback_query(call.id, "⚠️ اقدام تایید ناشناخته!", show_alert=True)
                else:
                    await bot.answer_callback_query(call.id, "⚠️ Unknown confirmation action!", show_alert=True)
                    
        except Exception as e:
            logger.error(f"Error in confirmation action {action}: {e}")
            logger.error(f"خطا در اقدام تایید {action}: {e}")
            
            if lang == "fa":
                await bot.answer_callback_query(call.id, "❌ خطا در تایید عملیات!", show_alert=True)
            else:
                await bot.answer_callback_query(call.id, "❌ Error confirming operation!", show_alert=True)
    else:
        logger.warning(f"Invalid confirmation data format: {data}")
        logger.warning(f"فرمت داده تایید نامعتبر: {data}")
        
        if lang == "fa":
            await bot.answer_callback_query(call.id, "⚠️ فرمت داده نامعتبر!", show_alert=True)
        else:
            await bot.answer_callback_query(call.id, "⚠️ Invalid data format!", show_alert=True)

@owner_only
@rate_limit
@validate_data
async def handle_cancel_action(call, bot, data, lang, db_manager: DBManager):
    """
    مدیریت اقدامات لغو پیشرفته
    Handle enhanced cancel actions (cancel:xxx)
    """
    if lang == "fa":
        await bot.answer_callback_query(call.id, "❌ عملیات لغو شد")
    else:
        await bot.answer_callback_query(call.id, "❌ Operation cancelled")
    
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
            text = "❌ عملیات لغو شد." if lang == "fa" else "❌ Operation cancelled."
            try:
                await bot.edit_message_text(text, call.message.chat.id, call.message.message_id)
            except Exception as e:
                logger.error(f"Error editing message: {e}")
                
        logger.info(f"Cancel action {data} handled for user {call.from_user.id}")
        logger.info(f"اقدام لغو {data} برای کاربر {call.from_user.id} مدیریت شد")
        
    except Exception as e:
        logger.error(f"Error in cancel action: {e}")
        logger.error(f"خطا در اقدام لغو: {e}")

@rate_limit
@validate_data
async def handle_pagination_callback(call, bot, data, lang, db_manager: DBManager):
    """
    مدیریت کالبک‌های صفحه‌بندی پیشرفته
    Handle enhanced pagination callbacks (page:xxx)
    """
    parts = data.split(":")
    if len(parts) != 2:
        logger.warning(f"Invalid pagination data format: {data}")
        logger.warning(f"فرمت داده صفحه‌بندی نامعتبر: {data}")
        
        if lang == "fa":
            await bot.answer_callback_query(call.id, "⚠️ فرمت صفحه‌بندی نامعتبر!", show_alert=True)
        else:
            await bot.answer_callback_query(call.id, "⚠️ Invalid pagination format!", show_alert=True)
        return
    
    section, page_num_str = parts
    try:
        page_num = int(page_num_str)
    except ValueError:
        logger.warning(f"Invalid page number: {page_num_str}")
        logger.warning(f"شماره صفحه نامعتبر: {page_num_str}")
        
        if lang == "fa":
            await bot.answer_callback_query(call.id, "⚠️ شماره صفحه نامعتبر!", show_alert=True)
        else:
            await bot.answer_callback_query(call.id, "⚠️ Invalid page number!", show_alert=True)
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
            logger.warning(f"بخش صفحه‌بندی ناشناخته: {section}")
            
    except Exception as e:
        logger.error(f"Error in pagination callback: {e}")
        logger.error(f"خطا در کالبک صفحه‌بندی: {e}")

# =============================================================================
# مدیریت‌کننده‌های کالبک اضافی - Additional Callback Handlers
# =============================================================================

@rate_limit
@validate_data
async def handle_filter_callback(call, bot, data, lang, db_manager: DBManager):
    """مدیریت فیلترها - Handle filters"""
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
    """مدیریت مرتب‌سازی - Handle sorting"""
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
    """مدیریت راهنما - Handle help"""
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
    """مدیریت تنظیمات - Handle settings"""
    await bot.answer_callback_query(call.id)
    
    try:
        from src.commands.general import handle_settings
        await handle_settings(call.message, bot, data, lang, db_manager)
    except Exception as e:
        logger.error(f"Error in settings callback: {e}")

@rate_limit
@validate_data
async def handle_admin_callback(call, bot, data, lang, db_manager: DBManager):
    """مدیریت ادمین - Handle admin actions"""
    # Check if user is admin
    if not await is_user_admin(call.from_user.id, call.message.chat.id, db_manager):
        if lang == "fa":
            await bot.answer_callback_query(call.id, "⚠️ شما مجاز به این عملیات نیستید!", show_alert=True)
        else:
            await bot.answer_callback_query(call.id, "⚠️ You're not authorized for this action!", show_alert=True)
        return
    
    await bot.answer_callback_query(call.id)
    
    try:
        # Admin functionality placeholder - implement when admin module is available
        if lang == "fa":
            await bot.send_message(call.message.chat.id, "⚙️ عملکرد ادمین در حال توسعه است...")
        else:
            await bot.send_message(call.message.chat.id, "⚙️ Admin functionality under development...")
    except Exception as e:
        logger.error(f"Error in admin callback: {e}")

@owner_only
@rate_limit
@validate_data
async def handle_attack_callback(call, bot, data, lang, db_manager: DBManager):
    """مدیریت حمله - Handle attack actions"""
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
    """مدیریت دفاع - Handle defense actions"""
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
    """مدیریت موجودی - Handle inventory actions"""
    await bot.answer_callback_query(call.id)
    
    try:
        from src.commands.inventory import handle_inventory_action
        await handle_inventory_action(call.message, bot, data, lang, db_manager)
    except Exception as e:
        logger.error(f"Error in inventory callback: {e}")

@rate_limit
@validate_data
async def handle_leaderboard_callback(call, bot, data, lang, db_manager: DBManager):
    """مدیریت لیدربورد - Handle leaderboard actions"""
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
    """مدیریت پروفایل - Handle profile actions"""
    await bot.answer_callback_query(call.id)
    
    try:
        from src.commands.general import handle_profile_action
        await handle_profile_action(call.message, bot, data, lang, db_manager)
    except Exception as e:
        logger.error(f"Error in profile callback: {e}")

@rate_limit
@validate_data
async def handle_weapon_callback(call, bot, data, lang, db_manager: DBManager):
    """مدیریت سلاح - Handle weapon actions"""
    await bot.answer_callback_query(call.id)
    
    try:
        from src.commands.attack import handle_weapon_action
        await handle_weapon_action(call.message, bot, data, lang, db_manager)
    except Exception as e:
        logger.error(f"Error in weapon callback: {e}")

@rate_limit
@validate_data
async def handle_item_callback(call, bot, data, lang, db_manager: DBManager):
    """مدیریت آیتم - Handle item actions"""
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
    """مدیریت اقدامات سریع - Handle quick actions"""
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
    """مدیریت تایید حذف حساب - Handle account deletion confirmation"""
    try:
        # Delete user data
        await db_manager.db(
            "DELETE FROM players WHERE chat_id = %s AND user_id = %s",
            (call.message.chat.id, call.from_user.id)
        )
        
        if lang == "fa":
            success_text = "✅ حساب شما با موفقیت حذف شد!"
        else:
            success_text = "✅ Your account has been successfully deleted!"
            
        await bot.edit_message_text(
            success_text,
            call.message.chat.id,
            call.message.message_id
        )
        
        logger.info(f"Account deleted for user {call.from_user.id}")
        logger.info(f"حساب کاربر {call.from_user.id} حذف شد")
        
    except Exception as e:
        logger.error(f"Error deleting account: {e}")
        logger.error(f"خطا در حذف حساب: {e}")

# =============================================================================
# توابع کمکی - Helper Functions
# =============================================================================

async def is_user_admin(user_id: int, chat_id: int, db_manager: DBManager) -> bool:
    """بررسی ادمین بودن کاربر - Check if user is admin"""
    try:
        # Check if user is bot admin (you can customize this)
        admin_ids = [123456789]  # Add your admin IDs here
        return user_id in admin_ids
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False

async def log_callback_usage(call: types.CallbackQuery, action: str, data: str):
    """ثبت استفاده از کالبک - Log callback usage"""
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
        logger.info(f"استفاده از کالبک: {usage_data}")
        
    except Exception as e:
        logger.error(f"Error logging callback usage: {e}")

async def create_error_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    """ایجاد کیبورد خطا - Create error keyboard"""
    keyboard = types.InlineKeyboardMarkup()
    
    if lang == "fa":
        keyboard.add(
            types.InlineKeyboardButton("🔄 تلاش مجدد", callback_data="do:retry"),
            types.InlineKeyboardButton("🏠 منوی اصلی", callback_data="go:main")
        )
        keyboard.add(types.InlineKeyboardButton("❌ بستن", callback_data="do:delete_message"))
    else:
        keyboard.add(
            types.InlineKeyboardButton("🔄 Retry", callback_data="do:retry"),
            types.InlineKeyboardButton("🏠 Main Menu", callback_data="go:main")
        )
        keyboard.add(types.InlineKeyboardButton("❌ Close", callback_data="do:delete_message"))
    
    return keyboard

def register_callback_handlers(bot, db_manager: DBManager):
    """
    ثبت مدیریت‌کننده‌های پیشرفته کالبک کوئری
    Register enhanced callback query handlers with comprehensive functionality
    
    Args:
        bot (telebot.async_telebot.AsyncTeleBot): Bot instance
        db_manager (DBManager): Database manager instance
    """
    logger.info("Registering enhanced callback query handlers")
    logger.info("ثبت مدیریت‌کننده‌های پیشرفته کالبک کوئری")
    
    # Register global callback handler with comprehensive error handling
    @bot.callback_query_handler(func=lambda call: True)
    async def main_callback_handler(call):
        """
        مدیریت‌کننده اصلی کالبک با مدیریت خطای پیشرفته
        Main callback handler with advanced error management
        """
        try:
            # Log callback usage for analytics
            await log_callback_usage(call, call.data.split(':')[0] if ':' in call.data else 'unknown', call.data)
            
            # Handle the callback
            await handle_callback_query(call, bot, db_manager)
            
        except Exception as e:
            logger.error(f"Critical error in callback handler: {e}")
            logger.error(f"خطای حاد در مدیریت‌کننده کالبک: {e}")
            
            # Try to send error message to user
            try:
                lang = await get_lang(call.message.chat.id, call.from_user.id, db_manager)
                
                if lang == "fa":
                    error_text = "❌ خطای داخلی سیستم!\n\nلطفاً مجدداً تلاش کنید یا با پشتیبانی تماس بگیرید."
                else:
                    error_text = "❌ Internal system error!\n\nPlease try again or contact support."
                
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
                        "❌ System error!", 
                        show_alert=True
                    )
                except Exception as answer_error:
                    logger.error(f"Failed to answer callback query: {answer_error}")

# =============================================================================
# ماژول تحلیل عملکرد کالبک - Callback Performance Analytics Module
# =============================================================================

class CallbackAnalytics:
    """تحلیل‌گر عملکرد کالبک - Callback Performance Analyzer"""
    
    def __init__(self):
        self.callback_stats: Dict[str, Dict[str, Any]] = {}
        self.response_times: Dict[str, List[float]] = {}
        self.error_counts: Dict[str, int] = {}
        
    def record_callback(self, action: str, response_time: float, success: bool):
        """ثبت آمار کالبک - Record callback statistics"""
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
        """دریافت گزارش عملکرد - Get performance report"""
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
# مدیریت کش کالبک - Callback Cache Management
# =============================================================================

class CallbackCache:
    """مدیر کش کالبک - Callback Cache Manager"""
    
    def __init__(self, ttl: int = 300):  # 5 minutes TTL
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        """دریافت از کش - Get from cache"""
        if key in self.cache:
            if time.time() - self.cache[key]['timestamp'] < self.ttl:
                return self.cache[key]['data']
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, data: Any):
        """تنظیم در کش - Set in cache"""
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def clear_expired(self):
        """پاک‌سازی کش منقضی - Clear expired cache"""
        current_time = time.time()
        expired_keys = [
            key for key, value in self.cache.items()
            if current_time - value['timestamp'] >= self.ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """دریافت آمار کش - Get cache statistics"""
        return {
            'total_entries': len(self.cache),
            'memory_usage': sum(len(str(value)) for value in self.cache.values()),
            'cache_keys': list(self.cache.keys())
        }

# Global cache instance
callback_cache = CallbackCache()

# =============================================================================
# تنظیمات پیشرفته کالبک - Advanced Callback Configuration
# =============================================================================

class CallbackConfig:
    """پیکربندی کالبک - Callback Configuration"""
    
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
# وابصادرات ماژول - Module Exports
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
    
    # Data classes
    'CallbackAction',
    'CallbackContext'
]

# Initialization message
logger.info("Enhanced Callback Handlers Module loaded successfully")
logger.info("ماژول مدیریت‌کننده‌های پیشرفته کالبک با موفقیت بارگذاری شد")

# Performance monitoring setup
logger.info(f"Callback performance monitoring: {'enabled' if callback_config.ENABLE_ANALYTICS else 'disabled'}")
logger.info(f"Callback caching: {'enabled' if callback_config.ENABLE_CACHING else 'disabled'}")
logger.info(f"نظارت بر عملکرد کالبک: {'فعال' if callback_config.ENABLE_ANALYTICS else 'غیرفعال'}")
logger.info(f"کش کالبک: {'فعال' if callback_config.ENABLE_CACHING else 'غیرفعال'}")
