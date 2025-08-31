#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TG Stars commands and handling module with comprehensive functionality
Provides complete TG Stars management, premium features, and bilingual support
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from src.utils import helpers
from src.utils.translations import T
from src.database.db_manager import DBManager
from src.config.items import ITEMS, PaymentType, get_items_by_payment_type, get_item_display_name, get_item_emoji, get_item_stats

# Set up logging
logger = logging.getLogger(__name__)

class StarsManager:
    """Manages comprehensive TG Stars system with premium features"""
    
    def __init__(self, db_manager: DBManager):
        self.db_manager = db_manager
    
    async def get_user_stars_balance(self, chat_id: int, user_id: int) -> int:
        """Get user's TG Stars balance"""
        try:
            result = await self.db_manager.db(
                "SELECT tg_stars FROM players WHERE chat_id=%s AND user_id=%s",
                (chat_id, user_id),
                fetch="one"
            )
            return result[0] if result else 0
        except Exception as e:
            logger.error(f"Error getting stars balance: {e}")
            return 0
    
    async def get_premium_items(self) -> Dict[str, Any]:
        """Get all premium items that can be purchased with TG Stars"""
        try:
            return get_items_by_payment_type(PaymentType.TG_STARS)
        except Exception as e:
            logger.error(f"Error getting premium items: {e}")
            return {}
    
    async def get_transaction_history(self, chat_id: int, user_id: int, limit: int = 10) -> List[Dict]:
        """Get user's TG Stars transaction history"""
        try:
            transactions = await self.db_manager.db(
                """SELECT payment_id, item_id, stars_amount, purchase_time, status 
                   FROM tg_stars_purchases 
                   WHERE chat_id=%s AND user_id=%s 
                   ORDER BY purchase_time DESC LIMIT %s""",
                (chat_id, user_id, limit),
                fetch="all"
            )
            return [
                {
                    'payment_id': tx[0],
                    'item_id': tx[1],
                    'amount': tx[2],
                    'date': tx[3],
                    'status': tx[4]
                }
                for tx in transactions
            ] if transactions else []
        except Exception as e:
            logger.error(f"Error getting transaction history: {e}")
            return []
    
    async def can_afford_premium_item(self, chat_id: int, user_id: int, item_id: str) -> bool:
        """Check if user can afford a premium item"""
        try:
            if item_id not in ITEMS:
                return False
            
            item = ITEMS[item_id]
            if item.get('payment') != PaymentType.TG_STARS.value:
                return False
                
            price = item.get('stars_price', 0)
            user_stars = await self.get_user_stars_balance(chat_id, user_id)
            
            return user_stars >= price
        except Exception as e:
            logger.error(f"Error checking affordability: {e}")
            return False
    
    async def show_stars_dashboard(self, bot: AsyncTeleBot, message: types.Message):
        """Display comprehensive TG Stars dashboard"""
        try:
            lang = await helpers.get_lang(message.chat.id, message.from_user.id, self.db_manager)
            stars_balance = await self.get_user_stars_balance(message.chat.id, message.from_user.id)
            
            # Build dashboard message
            dashboard_text = f"ðŸ’Ž <b>{T[lang]['stars_welcome'][lang]}</b>\n\n"
            dashboard_text += f"â­ <b>{T[lang]['stars_balance_overview'][lang]}</b>\n"
            dashboard_text += f"{T[lang]['current_stars_balance'][lang].format(stars=stars_balance)}\n\n"
            dashboard_text += f"ðŸ“ <b>{T[lang]['stars_description'][lang]}</b>\n\n"
            
            # Add features section
            dashboard_text += f"ðŸŒŸ <b>{T[lang]['premium_features'][lang]}</b>\n"
            dashboard_text += f"{T[lang]['feature_exclusive_weapons'][lang]}\n"
            dashboard_text += f"{T[lang]['feature_special_abilities'][lang]}\n"
            dashboard_text += f"{T[lang]['feature_premium_support'][lang]}\n"
            dashboard_text += f"{T[lang]['feature_advanced_stats'][lang]}\n"
            dashboard_text += f"{T[lang]['feature_custom_themes'][lang]}\n"
            dashboard_text += f"{T[lang]['feature_early_access'][lang]}"
            
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            
            # Main action buttons
            premium_shop_btn = types.InlineKeyboardButton(
                f"ðŸ›’ {T[lang]['view_premium_shop'][lang]}", 
                callback_data="stars:premium_shop"
            )
            history_btn = types.InlineKeyboardButton(
                f"ðŸ“Š {T[lang]['view_history'][lang]}", 
                callback_data="stars:history"
            )
            keyboard.add(premium_shop_btn, history_btn)
            
            # Additional features
            buy_stars_btn = types.InlineKeyboardButton(
                f"ðŸ’° {T[lang]['buy_stars'][lang]}", 
                callback_data="stars:buy_stars"
            )
            help_btn = types.InlineKeyboardButton(
                f"ðŸ†˜ {T[lang]['stars_help'][lang]}", 
                callback_data="stars:help"
            )
            keyboard.add(buy_stars_btn, help_btn)
            
            # Utility buttons
            refresh_btn = types.InlineKeyboardButton(
                f"ðŸ”„ {T[lang]['refresh_balance'][lang]}", 
                callback_data="stars:refresh"
            )
            close_btn = types.InlineKeyboardButton(
                f"âŒ {T[lang]['close_stars_menu'][lang]}", 
                callback_data="stars:close"
            )
            keyboard.add(refresh_btn, close_btn)
            
            await bot.send_message(
                message.chat.id, 
                dashboard_text, 
                reply_markup=keyboard, 
                parse_mode="HTML"
            )
            
        except Exception as e:
            logger.error(f"Error showing stars dashboard: {e}")
            await bot.send_message(
                message.chat.id, 
                "âŒ Error displaying TG Stars dashboard. Please try again."
            )
    
    async def show_premium_shop(self, bot: AsyncTeleBot, call: types.CallbackQuery):
        """Display premium items shop"""
        try:
            lang = await helpers.get_lang(call.message.chat.id, call.from_user.id, self.db_manager)
            stars_balance = await self.get_user_stars_balance(call.message.chat.id, call.from_user.id)
            premium_items = await self.get_premium_items()
            
            if not premium_items:
                await bot.answer_callback_query(
                    call.id, 
                    T[lang]['stars_error_item_unavailable'][lang], 
                    show_alert=True
                )
                return
            
            # Build premium shop message
            shop_text = f"ðŸ›’ <b>{T[lang]['premium_catalog'][lang]}</b>\n\n"
            shop_text += f"â­ {T[lang]['current_stars_balance'][lang].format(stars=stars_balance)}\n\n"
            shop_text += f"ðŸ’Ž <b>{T[lang]['exclusive_items'][lang]}</b>:\n\n"
            
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            
            # Add premium items
            for item_id, item_data in premium_items.items():
                item_name = get_item_display_name(item_id, lang)
                emoji = get_item_emoji(item_id)
                price = item_data.get('stars_price', 0)
                stats = get_item_stats(item_id)
                
                # Build item description
                item_desc = f"{emoji} <b>{item_name}</b>\n"
                if stats.get('damage'):
                    item_desc += f"âš”ï¸ {T[lang]['damage'][lang]}: {stats['damage']}\n"
                if stats.get('duration_seconds'):
                    hours = stats['duration_seconds'] // 3600
                    item_desc += f"â±ï¸ {T[lang]['duration'][lang]}: {hours} {T[lang]['hours'][lang]}\n"
                
                shop_text += item_desc
                shop_text += f"ðŸ’° {T[lang]['item_requires_stars'][lang].format(price=price)}\n"
                
                # Can afford check
                can_afford = await self.can_afford_premium_item(call.message.chat.id, call.from_user.id, item_id)
                if can_afford:
                    button_text = f"âœ… {emoji} {item_name} - â­{price}"
                    callback_data = f"stars:buy:{item_id}"
                else:
                    button_text = f"âŒ {emoji} {item_name} - â­{price}"
                    callback_data = f"stars:insufficient:{item_id}"
                
                item_btn = types.InlineKeyboardButton(button_text, callback_data=callback_data)
                keyboard.add(item_btn)
                shop_text += "\n"
            
            # Navigation buttons
            back_btn = types.InlineKeyboardButton(
                f"ðŸ”™ {T[lang]['back_btn'][lang]}", 
                callback_data="stars:main"
            )
            close_btn = types.InlineKeyboardButton(
                f"âŒ {T[lang]['close_stars_menu'][lang]}", 
                callback_data="stars:close"
            )
            keyboard.add(back_btn, close_btn)
            
            await bot.edit_message_text(
                shop_text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            
        except Exception as e:
            logger.error(f"Error showing premium shop: {e}")
            await bot.answer_callback_query(call.id, T[lang]['stars_error_generic'][lang])
    
    async def show_transaction_history(self, bot: AsyncTeleBot, call: types.CallbackQuery):
        """Display user's transaction history"""
        try:
            lang = await helpers.get_lang(call.message.chat.id, call.from_user.id, self.db_manager)
            transactions = await self.get_transaction_history(call.message.chat.id, call.from_user.id)
            
            history_text = f"ðŸ“Š <b>{T[lang]['transaction_history'][lang]}</b>\n\n"
            
            if not transactions:
                history_text += f"{T[lang]['no_transactions'][lang]}\n\n"
                history_text += f"ðŸ’¡ {T[lang]['stars_purchase_info'][lang]}"
            else:
                for tx in transactions:
                    item_name = get_item_display_name(tx['item_id'], lang)
                    emoji = get_item_emoji(tx['item_id'])
                    status_emoji = "âœ…" if tx['status'] == 'completed' else "â³" if tx['status'] == 'pending' else "âŒ"
                    
                    history_text += f"{status_emoji} {emoji} <b>{item_name}</b>\n"
                    history_text += f"ðŸ’° {tx['amount']} â­ | {tx['date'].strftime('%Y-%m-%d %H:%M')}\n"
                    history_text += f"ðŸ“‹ {T[lang][f'transaction_{tx["status"]}'][lang]}\n\n"
            
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(
                types.InlineKeyboardButton(f"ðŸ”™ {T[lang]['back_btn'][lang]}", callback_data="stars:main"),
                types.InlineKeyboardButton(f"âŒ {T[lang]['close_stars_menu'][lang]}", callback_data="stars:close")
            )
            
            await bot.edit_message_text(
                history_text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            
        except Exception as e:
            logger.error(f"Error showing transaction history: {e}")
            await bot.answer_callback_query(call.id, T[lang]['stars_error_generic'][lang])
    
    async def show_stars_help(self, bot: AsyncTeleBot, call: types.CallbackQuery):
        """Display TG Stars help and FAQ"""
        try:
            lang = await helpers.get_lang(call.message.chat.id, call.from_user.id, self.db_manager)
            
            help_text = f"ðŸ†˜ <b>{T[lang]['stars_help'][lang]}</b>\n\n"
            help_text += f"â“ <b>{T[lang]['stars_faq'][lang]}</b>\n\n"
            
            if lang == "fa":
                help_text += """
<b>ðŸŒŸ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù… Ú†ÛŒØ³ØªØŸ</b>
Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù… Ø§Ø±Ø² ÙˆÛŒÚ˜Ù‡â€ŒØ§ÛŒ Ù‡Ø³ØªÙ†Ø¯ Ú©Ù‡ ØªÙˆØ³Ø· ØªÙ„Ú¯Ø±Ø§Ù… Ø§Ø±Ø§Ø¦Ù‡ Ù…ÛŒâ€ŒØ´ÙˆÙ†Ø¯ Ùˆ Ø¨Ø±Ø§ÛŒ Ø®Ø±ÛŒØ¯ Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ Ùˆ ÙˆÛŒÚ˜Ú¯ÛŒâ€ŒÙ‡Ø§ÛŒ ÙˆÛŒÚ˜Ù‡ Ø§Ø³ØªÙØ§Ø¯Ù‡ Ù…ÛŒâ€ŒØ´ÙˆÙ†Ø¯.

<b>ðŸ’° Ú†Ú¯ÙˆÙ†Ù‡ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù… Ø®Ø±ÛŒØ¯Ø§Ø±ÛŒ Ú©Ù†Ù…ØŸ</b>
Ù…ÛŒâ€ŒØªÙˆØ§Ù†ÛŒØ¯ Ù…Ø³ØªÙ‚ÛŒÙ…Ø§Ù‹ Ø§Ø² Ø·Ø±ÛŒÙ‚ Ø³ÛŒØ³ØªÙ… Ù¾Ø±Ø¯Ø§Ø®Øª ØªÙ„Ú¯Ø±Ø§Ù… Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù… Ø®Ø±ÛŒØ¯Ø§Ø±ÛŒ Ú©Ù†ÛŒØ¯.

<b>ðŸ›’ Ú†Ù‡ Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ÛŒÛŒ Ø¨Ø§ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù… Ù‚Ø§Ø¨Ù„ Ø®Ø±ÛŒØ¯ Ù‡Ø³ØªÙ†Ø¯ØŸ</b>
Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ÛŒ ÙˆÛŒÚ˜Ù‡ Ùˆ Ø§Ù†Ø­ØµØ§Ø±ÛŒ Ú©Ù‡ Ø¯Ø± ÙØ±ÙˆØ´Ú¯Ø§Ù‡ ÙˆÛŒÚ˜Ù‡ Ù…ÙˆØ¬ÙˆØ¯ Ù‡Ø³ØªÙ†Ø¯ØŒ Ø´Ø§Ù…Ù„ ØªØ³Ù„ÛŒØ­Ø§Øª Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ùˆ ØªÙˆØ§Ù†Ø§ÛŒÛŒâ€ŒÙ‡Ø§ÛŒ ÙˆÛŒÚ˜Ù‡.

<b>ðŸ”„ Ø¢ÛŒØ§ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù… Ù‚Ø§Ø¨Ù„ Ø¨Ø§Ø²Ú¯Ø´Øª Ù‡Ø³ØªÙ†Ø¯ØŸ</b>
Ø¨Ø± Ø§Ø³Ø§Ø³ Ø³ÛŒØ§Ø³Øªâ€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù…ØŒ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù… Ù…Ø¹Ù…ÙˆÙ„Ø§Ù‹ Ù‚Ø§Ø¨Ù„ Ø¨Ø§Ø²Ú¯Ø´Øª Ù†ÛŒØ³ØªÙ†Ø¯.

<b>ðŸ“± Ø¢ÛŒØ§ Ù…ÛŒâ€ŒØªÙˆØ§Ù†Ù… Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù… Ø±Ø§ Ø§Ù†ØªÙ‚Ø§Ù„ Ø¯Ù‡Ù…ØŸ</b>
Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù… Ù‚Ø§Ø¨Ù„ Ø§Ù†ØªÙ‚Ø§Ù„ Ø¨Ù‡ Ø³Ø§ÛŒØ± Ú©Ø§Ø±Ø¨Ø±Ø§Ù† Ù†ÛŒØ³ØªÙ†Ø¯.
                """
            else:
                help_text += """
<b>ðŸŒŸ What are TG Stars?</b>
TG Stars are a premium currency provided by Telegram for purchasing special items and features.

<b>ðŸ’° How do I buy TG Stars?</b>
You can purchase TG Stars directly through Telegram's payment system.

<b>ðŸ›’ What can I buy with TG Stars?</b>
Exclusive premium items available in the premium shop, including advanced weapons and special abilities.

<b>ðŸ”„ Are TG Stars refundable?</b>
According to Telegram's policies, TG Stars are generally non-refundable.

<b>ðŸ“± Can I transfer TG Stars?</b>
TG Stars cannot be transferred to other users.
                """
            
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(
                types.InlineKeyboardButton(f"ðŸ“ž {T[lang]['stars_support'][lang]}", url="https://t.me/TrumpBotSupport"),
                types.InlineKeyboardButton(f"ðŸ“œ {T[lang]['stars_terms'][lang]}", callback_data="stars:terms")
            )
            keyboard.add(
                types.InlineKeyboardButton(f"ðŸ”™ {T[lang]['back_btn'][lang]}", callback_data="stars:main"),
                types.InlineKeyboardButton(f"âŒ {T[lang]['close_stars_menu'][lang]}", callback_data="stars:close")
            )
            
            await bot.edit_message_text(
                help_text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            
        except Exception as e:
            logger.error(f"Error showing stars help: {e}")
            await bot.answer_callback_query(call.id, T[lang]['stars_error_generic'][lang])
    
    async def handle_stars_callback(self, bot: AsyncTeleBot, call: types.CallbackQuery):
        """Handle all TG Stars related callbacks"""
        try:
            data_parts = call.data.split(':')
            action = data_parts[1] if len(data_parts) > 1 else "main"
            lang = await helpers.get_lang(call.message.chat.id, call.from_user.id, self.db_manager)

            if action == "main":
                # Refresh the main dashboard
                stars_balance = await self.get_user_stars_balance(call.message.chat.id, call.from_user.id)
                dashboard_text = f"ðŸ’Ž <b>{T[lang]['stars_welcome'][lang]}</b>\n\n"
                dashboard_text += f"â­ <b>{T[lang]['stars_balance_overview'][lang]}</b>\n"
                dashboard_text += f"{T[lang]['current_stars_balance'][lang].format(stars=stars_balance)}\n\n"
                dashboard_text += f"ðŸ“ <b>{T[lang]['stars_description'][lang]}</b>\n\n"
                dashboard_text += f"ðŸŒŸ <b>{T[lang]['premium_features'][lang]}</b>\n"
                dashboard_text += f"{T[lang]['feature_exclusive_weapons'][lang]}\n"
                dashboard_text += f"{T[lang]['feature_special_abilities'][lang]}\n"
                dashboard_text += f"{T[lang]['feature_premium_support'][lang]}\n"
                dashboard_text += f"{T[lang]['feature_advanced_stats'][lang]}\n"
                dashboard_text += f"{T[lang]['feature_custom_themes'][lang]}\n"
                dashboard_text += f"{T[lang]['feature_early_access'][lang]}"

                keyboard = types.InlineKeyboardMarkup(row_width=2)
                keyboard.add(
                    types.InlineKeyboardButton(f"ðŸ›’ {T[lang]['view_premium_shop'][lang]}", callback_data="stars:premium_shop"),
                    types.InlineKeyboardButton(f"ðŸ“Š {T[lang]['view_history'][lang]}", callback_data="stars:history")
                )
                keyboard.add(
                    types.InlineKeyboardButton(f"ðŸ’° {T[lang]['buy_stars'][lang]}", callback_data="stars:buy_stars"),
                    types.InlineKeyboardButton(f"ðŸ†˜ {T[lang]['stars_help'][lang]}", callback_data="stars:help")
                )
                keyboard.add(
                    types.InlineKeyboardButton(f"ðŸ”„ {T[lang]['refresh_balance'][lang]}", callback_data="stars:refresh"),
                    types.InlineKeyboardButton(f"âŒ {T[lang]['close_stars_menu'][lang]}", callback_data="stars:close")
                )

                await bot.edit_message_text(
                    dashboard_text,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            
            elif action == "premium_shop":
                await self.show_premium_shop(bot, call)
            
            elif action == "history":
                await self.show_transaction_history(bot, call)
            
            elif action == "help":
                await self.show_stars_help(bot, call)
            
            elif action == "buy":
                item_id = data_parts[2] if len(data_parts) > 2 else ""
                await self._initiate_purchase(call, bot, lang, item_id)
            
            elif action == "insufficient":
                item_id = data_parts[2] if len(data_parts) > 2 else ""
                item = ITEMS.get(item_id, {})
                price = item.get('stars_price', 0)
                user_stars = await self.get_user_stars_balance(call.message.chat.id, call.from_user.id)
                needed = price - user_stars
                
                await bot.answer_callback_query(
                    call.id,
                    T[lang]['insufficient_stars'][lang].format(required=needed),
                    show_alert=True
                )
            
            elif action == "buy_stars":
                await bot.answer_callback_query(
                    call.id,
                    T[lang]['stars_purchase_info'][lang],
                    show_alert=True
                )
            
            elif action == "refresh":
                await bot.answer_callback_query(call.id, "ðŸ”„ Balance refreshed!")
                # Trigger main dashboard refresh
                await self.handle_stars_callback(bot, types.CallbackQuery(
                    id=call.id,
                    from_user=call.from_user,
                    message=call.message,
                    data="stars:main"
                ))
            
            elif action == "close":
                await bot.delete_message(call.message.chat.id, call.message.message_id)
            
            await bot.answer_callback_query(call.id)
            
        except Exception as e:
            logger.error(f"Error handling stars callback: {e}")
            await bot.answer_callback_query(call.id, "âŒ Error processing request.")
    
    async def _initiate_purchase(self, call: types.CallbackQuery, bot: AsyncTeleBot, lang: str, item_id: str):
        """Creates an invoice for a TG Stars purchase."""
        try:
            item = ITEMS.get(item_id)
            if not item or item.get('payment') != 'tg_stars':
                await bot.answer_callback_query(
                    call.id, 
                    T[lang]['item_not_found'][lang] if lang == 'fa' else "âŒ Item not found or not available for TG Stars purchase.",
                    show_alert=True
                )
                return

            price = item.get('stars_price', 0)
            if price <= 0:
                await bot.answer_callback_query(
                    call.id, 
                    T[lang]['item_not_for_sale'][lang] if lang == 'fa' else "âŒ This item is not for sale.",
                    show_alert=True
                )
                return

            # Create an invoice
            item_name = get_item_display_name(item_id, lang)
            invoice = types.LabeledPrice(label=item_name, amount=price)
            
            # The payload should contain information to identify the purchase later
            payload = f"purchase:{item_id}:{call.from_user.id}"

            # Invoice titles and descriptions in both languages
            if lang == 'fa':
                title = f"ðŸŒŸ Ø®Ø±ÛŒØ¯ {item_name}"
                description = f"Ø®Ø±ÛŒØ¯ {item_name} Ø¨Ø§ {price} Ø³ØªØ§Ø±Ù‡ ØªÙ„Ú¯Ø±Ø§Ù…\n\nðŸ’Ž Ø¢ÛŒØªÙ… Ù¾Ø±ÛŒÙ…ÛŒÙˆÙ… Ø§Ù†Ø­ØµØ§Ø±ÛŒ\nðŸ”¥ Ø¯Ø³ØªØ±Ø³ÛŒ ÙÙˆØ±ÛŒ Ù¾Ø³ Ø§Ø² Ù¾Ø±Ø¯Ø§Ø®Øª"
            else:
                title = f"ðŸŒŸ Purchase {item_name}"
                description = f"Purchase {item_name} for {price} Telegram Stars\n\nðŸ’Ž Exclusive premium item\nðŸ”¥ Instant access after payment"

            await bot.send_invoice(
                chat_id=call.message.chat.id,
                title=title,
                description=description,
                invoice_payload=payload,
                provider_token='',  # No provider token needed for Stars
                currency='XTR',
                prices=[invoice]
            )
            
            # Send confirmation message
            confirmation_msg = (
                f"âœ¨ {T[lang]['invoice_sent'][lang] if lang == 'fa' else 'Invoice sent successfully!'}\n\n"
                f"ðŸ’° {T[lang]['total_cost'][lang] if lang == 'fa' else 'Total cost'}: {price} â­\n"
                f"ðŸ›’ {T[lang]['item'][lang] if lang == 'fa' else 'Item'}: {item_name}\n\n"
                f"ðŸ“‹ {T[lang]['payment_instructions'][lang] if lang == 'fa' else 'Click the invoice above to complete your purchase.'}"
            )
            
            await bot.answer_callback_query(call.id, "âœ… Invoice created!")
            
        except Exception as e:
            logger.error(f"Failed to create TG Stars invoice: {e}")
            error_msg = (
                "âŒ Ø®Ø·Ø§ Ø¯Ø± Ø§ÛŒØ¬Ø§Ø¯ ØµÙˆØ±ØªØ­Ø³Ø§Ø¨. Ù„Ø·ÙØ§Ù‹ Ù…Ø¬Ø¯Ø¯Ø§Ù‹ ØªÙ„Ø§Ø´ Ú©Ù†ÛŒØ¯." if lang == 'fa' 
                else "âŒ Failed to create invoice. Please try again."
            )
            await bot.answer_callback_query(call.id, error_msg, show_alert=True)


async def handle_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery, bot: AsyncTeleBot, db_manager: DBManager):
    """Handles the pre-checkout query to validate the purchase with bilingual support."""
    try:
        # Get user language for error messages
        lang = await helpers.get_lang(pre_checkout_query.from_user.id, pre_checkout_query.from_user.id, db_manager)
        
        # The payload was set during invoice creation
        payload_parts = pre_checkout_query.invoice_payload.split(':')
        if len(payload_parts) != 3:
            error_msg = "Ù¾ÛŒÙ„ÙˆØ¯ Ù†Ø§Ù…Ø¹ØªØ¨Ø±" if lang == 'fa' else "Invalid payload"
            await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=False, error_message=error_msg)
            return
            
        item_id = payload_parts[1]
        user_id = int(payload_parts[2])

        # Basic validation
        if pre_checkout_query.from_user.id != user_id:
            error_msg = "Ø¹Ø¯Ù… ØªØ·Ø¨ÛŒÙ‚ Ø´Ù†Ø§Ø³Ù‡ Ú©Ø§Ø±Ø¨Ø±" if lang == 'fa' else "User ID mismatch"
            await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=False, error_message=error_msg)
            return

        item = ITEMS.get(item_id)
        if not item or item.get('stars_price') != pre_checkout_query.total_amount:
            error_msg = "Ø¹Ø¯Ù… ØªØ·Ø¨ÛŒÙ‚ Ø¢ÛŒØªÙ… ÛŒØ§ Ù‚ÛŒÙ…Øª" if lang == 'fa' else "Item or price mismatch"
            await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=False, error_message=error_msg)
            return

        # Everything is okay, confirm the transaction
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
        
    except Exception as e:
        logger.error(f"Error in pre-checkout validation: {e}")
        error_msg = "Ø®Ø·Ø§ Ø¯Ø± Ø§Ø¹ØªØ¨Ø§Ø±Ø³Ù†Ø¬ÛŒ Ù¾Ø±Ø¯Ø§Ø®Øª" if lang == 'fa' else "Payment validation error"
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=False, error_message=error_msg)


async def handle_successful_payment(message: types.Message, bot: AsyncTeleBot, db_manager: DBManager):
    """Handles a successful payment and grants the item to the user with bilingual support."""
    try:
        lang = await helpers.get_lang(message.chat.id, message.from_user.id, db_manager)
        payment_info = message.successful_payment
        payload_parts = payment_info.invoice_payload.split(':')
        
        if len(payload_parts) != 3:
            logger.error(f"Invalid payment payload: {payment_info.invoice_payload}")
            return
            
        item_id = payload_parts[1]
        
        # Verify the item exists
        item = ITEMS.get(item_id)
        if not item:
            logger.error(f"Unknown item purchased: {item_id}")
            return
        
        # Add the item to the user's inventory
        await db_manager.db("""
            INSERT INTO inventories (chat_id, user_id, item, qty)
            VALUES (%s, %s, %s, 1)
            ON CONFLICT (chat_id, user_id, item) DO UPDATE
            SET qty = inventories.qty + 1
        """, (message.chat.id, message.from_user.id, item_id))

        # Log the successful transaction
        await db_manager.db("""
            INSERT INTO tg_stars_purchases (chat_id, user_id, payment_id, item_id, stars_amount, purchase_time, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'completed')
        """, (
            message.chat.id, 
            message.from_user.id, 
            payment_info.telegram_payment_charge_id, 
            item_id, 
            payment_info.total_amount, 
            helpers.now()
        ))

        # Send success message with both languages
        item_name = get_item_display_name(item_id, lang)
        emoji = get_item_emoji(item_id)
        
        if lang == 'fa':
            success_msg = f"""ðŸŽ‰ <b>Ø®Ø±ÛŒØ¯ Ù…ÙˆÙÙ‚!</b>

âœ… {emoji} <b>{item_name}</b> Ø¨Ø§ Ù…ÙˆÙÙ‚ÛŒØª Ø¨Ù‡ Ø§Ù†Ø¨Ø§Ø± Ø´Ù…Ø§ Ø§Ø¶Ø§ÙÙ‡ Ø´Ø¯!

ðŸ’° Ù…Ø¨Ù„Øº Ù¾Ø±Ø¯Ø§Ø®ØªÛŒ: {payment_info.total_amount} â­
ðŸ†” Ø´Ù†Ø§Ø³Ù‡ ØªØ±Ø§Ú©Ù†Ø´: <code>{payment_info.telegram_payment_charge_id}</code>

ðŸŽ® Ø§Ø² Ø¢ÛŒØªÙ… Ø¬Ø¯ÛŒØ¯ Ø®ÙˆØ¯ Ø§Ø³ØªÙØ§Ø¯Ù‡ Ú©Ù†ÛŒØ¯!
ðŸª Ø¨Ø±Ø§ÛŒ Ø®Ø±ÛŒØ¯ Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ÛŒ Ø¨ÛŒØ´ØªØ± Ø§Ø² Ø¯Ø³ØªÙˆØ± /stars Ø§Ø³ØªÙØ§Ø¯Ù‡ Ú©Ù†ÛŒØ¯."""
        else:
            success_msg = f"""ðŸŽ‰ <b>Purchase Successful!</b>

âœ… {emoji} <b>{item_name}</b> has been added to your inventory!

ðŸ’° Amount paid: {payment_info.total_amount} â­
ðŸ†” Transaction ID: <code>{payment_info.telegram_payment_charge_id}</code>

ðŸŽ® Enjoy your new item!
ðŸª Use /stars command to purchase more items."""

        # Create a keyboard with relevant actions
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        
        # View inventory button
        inventory_btn = types.InlineKeyboardButton(
            f"ðŸ“¦ {('Ù…Ø´Ø§Ù‡Ø¯Ù‡ Ø§Ù†Ø¨Ø§Ø±' if lang == 'fa' else 'View Inventory')}", 
            callback_data="inventory:show"
        )
        
        # View more premium items button
        shop_btn = types.InlineKeyboardButton(
            f"ðŸ›’ {('ÙØ±ÙˆØ´Ú¯Ø§Ù‡ ÙˆÛŒÚ˜Ù‡' if lang == 'fa' else 'Premium Shop')}", 
            callback_data="stars:premium_shop"
        )
        
        keyboard.add(inventory_btn, shop_btn)
        
        await bot.send_message(
            message.chat.id, 
            success_msg, 
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        # Log successful purchase
        logger.info(f"Successful TG Stars purchase: User {message.from_user.id} bought {item_id} for {payment_info.total_amount} stars")
        
    except Exception as e:
        logger.error(f"Error handling successful payment: {e}")
        # Send error message in user's language
        lang = await helpers.get_lang(message.chat.id, message.from_user.id, db_manager)
        error_msg = (
            "âŒ Ø®Ø·Ø§ÛŒÛŒ Ø¯Ø± Ù¾Ø±Ø¯Ø§Ø²Ø´ Ù¾Ø±Ø¯Ø§Ø®Øª Ø´Ù…Ø§ Ø±Ø® Ø¯Ø§Ø¯. Ù„Ø·ÙØ§Ù‹ Ø¨Ø§ Ù¾Ø´ØªÛŒØ¨Ø§Ù†ÛŒ ØªÙ…Ø§Ø³ Ø¨Ú¯ÛŒØ±ÛŒØ¯." if lang == 'fa'
            else "âŒ An error occurred processing your payment. Please contact support."
        )
        await bot.send_message(message.chat.id, error_msg)


def register_handlers(bot: AsyncTeleBot, db_manager: DBManager):
    """Registers all TG Stars related handlers."""
    
    # Initialize StarsManager
    stars_manager = StarsManager(db_manager)
    
    @bot.message_handler(commands=['stars'])
    async def handle_stars_command(message):
        """Handle /stars command to show TG Stars dashboard"""
        await stars_manager.show_stars_dashboard(bot, message)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('stars:'))
    async def handle_stars_callbacks(call):
        """Handle all TG Stars related callback queries"""
        await stars_manager.handle_stars_callback(bot, call)

    # This handler confirms the transaction before the user's stars are charged
    @bot.pre_checkout_query_handler(func=lambda query: True)
    async def pre_checkout_handler(query: types.PreCheckoutQuery):
        await handle_pre_checkout_query(query, bot, db_manager)

    # This handler runs after the payment is successfully processed by Telegram
    @bot.message_handler(content_types=['successful_payment'])
    async def successful_payment_handler(message: types.Message):
        await handle_successful_payment(message, bot, db_manager)


# Legacy compatibility functions
async def handle_stars_callback(call: types.CallbackQuery, bot: AsyncTeleBot, db_manager: DBManager):
    """Legacy callback handler for backward compatibility"""
    stars_manager = StarsManager(db_manager)
    await stars_manager.handle_stars_callback(bot, call)

