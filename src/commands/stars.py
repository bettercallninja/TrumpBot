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
from src.config.bot_config import BotConfig

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
    
    async def add_stars_to_user(self, chat_id: int, user_id: int, amount: int) -> bool:
        """Add TG Stars to user's balance"""
        try:
            await self.db_manager.db(
                "UPDATE players SET tg_stars = tg_stars + %s WHERE chat_id=%s AND user_id=%s",
                (amount, chat_id, user_id)
            )
            logger.info(f"Added {amount} TG Stars to user {user_id} in chat {chat_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding stars to user: {e}")
            return False
    
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
    
    async def process_free_stars(self, chat_id: int, user_id: int, bot: AsyncTeleBot, lang: str) -> None:
        """Process free stars when the feature is enabled"""
        try:
            if not BotConfig.feature_flags.free_stars_enabled:
                return
                
            # Add 10 free stars
            free_stars_amount = 10
            await self.add_stars_to_user(chat_id, user_id, free_stars_amount)
            
            # Get updated balance
            new_balance = await self.get_user_stars_balance(chat_id, user_id)
            
            # Notify user
            if lang == "fa":
                message = f"✨ تبریک! {free_stars_amount} ستاره تلگرام رایگان به حساب شما اضافه شد!\n\n⭐ موجودی فعلی: {new_balance} ستاره تلگرام"
            else:
                message = f"✨ Congratulations! {free_stars_amount} free TG Stars have been added to your account!\n\n⭐ Current balance: {new_balance} TG Stars"
            
            await bot.send_message(chat_id, message)
            
            logger.info(f"Added {free_stars_amount} free TG Stars to user {user_id} in chat {chat_id}")
            
        except Exception as e:
            logger.error(f"Error processing free stars: {e}")
    
    async def purchase_premium_item(self, chat_id: int, user_id: int, item_id: str) -> bool:
        """Process a premium item purchase"""
        try:
            # Check if the item exists and is a premium item
            if item_id not in ITEMS:
                return False
                
            item = ITEMS[item_id]
            if item.get('payment') != PaymentType.TG_STARS.value:
                return False
                
            # Get item price
            price = item.get('stars_price', 0)
            
            # Check if user can afford it
            user_stars = await self.get_user_stars_balance(chat_id, user_id)
            if user_stars < price:
                return False
                
            # Deduct stars from user's balance
            await self.db_manager.db(
                "UPDATE players SET tg_stars = tg_stars - %s WHERE chat_id=%s AND user_id=%s",
                (price, chat_id, user_id)
            )
            
            # Add item to user's inventory
            await self.db_manager.db(
                """INSERT INTO inventories (chat_id, user_id, item, qty) 
                   VALUES (%s, %s, %s, 1) 
                   ON CONFLICT (chat_id, user_id, item) 
                   DO UPDATE SET qty = inventories.qty + 1""",
                (chat_id, user_id, item_id)
            )
            
            # Record transaction
            payment_id = f"stars_{helpers.now().strftime('%Y%m%d%H%M%S')}_{user_id}"
            await self.db_manager.db(
                """INSERT INTO tg_stars_purchases 
                   (payment_id, chat_id, user_id, item_id, stars_amount, purchase_time, status)
                   VALUES (%s, %s, %s, %s, %s, %s, 'completed')""",
                (payment_id, chat_id, user_id, item_id, price, helpers.now())
            )
            
            logger.info(f"User {user_id} purchased {item_id} for {price} TG Stars")
            return True
            
        except Exception as e:
            logger.error(f"Error processing premium purchase: {e}")
            return False
    
    async def show_stars_dashboard(self, bot: AsyncTeleBot, message: types.Message):
        """Display comprehensive TG Stars dashboard"""
        try:
            lang = await helpers.get_lang(message.chat.id, message.from_user.id, self.db_manager)
            stars_balance = await self.get_user_stars_balance(message.chat.id, message.from_user.id)
            
            # Build dashboard message
            dashboard_text = f"💎 <b>{T[lang].get('stars_welcome', 'TG Stars Dashboard')}</b>\n\n"
            dashboard_text += f"⭐ <b>{T[lang].get('stars_balance_overview', 'Your TG Stars Balance')}</b>\n"
            dashboard_text += f"{T[lang].get('current_stars_balance', 'Current Balance: ⭐ {stars} TG Stars').format(stars=stars_balance)}\n\n"
            dashboard_text += f"📝 <b>{T[lang].get('stars_description', 'TG Stars are premium currency that can be used to purchase exclusive items and features.')}</b>\n\n"
            
            # Add features section
            dashboard_text += f"🌟 <b>{T[lang].get('premium_features', 'Premium Features')}</b>\n"
            dashboard_text += f"{T[lang].get('feature_exclusive_weapons', '• Access to exclusive premium weapons')}\n"
            dashboard_text += f"{T[lang].get('feature_special_abilities', '• Unlock special combat abilities')}\n"
            dashboard_text += f"{T[lang].get('feature_premium_support', '• Priority customer support')}\n"
            dashboard_text += f"{T[lang].get('feature_advanced_stats', '• Advanced statistics and analytics')}\n"
            dashboard_text += f"{T[lang].get('feature_custom_themes', '• Custom themes and personalization')}\n"
            dashboard_text += f"{T[lang].get('feature_early_access', '• Early access to new features')}"
            
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            
            # Main action buttons
            premium_shop_btn = types.InlineKeyboardButton(
                f"🛒 {T[lang].get('view_premium_shop', 'View Premium Shop')}", 
                callback_data="stars:premium_shop"
            )
            history_btn = types.InlineKeyboardButton(
                f"📊 {T[lang].get('view_history', 'View History')}", 
                callback_data="stars:history"
            )
            keyboard.add(premium_shop_btn, history_btn)
            
            # Additional features
            buy_stars_btn = types.InlineKeyboardButton(
                f"💰 {T[lang].get('buy_stars', 'Buy TG Stars')}", 
                callback_data="stars:buy_stars"
            )
            help_btn = types.InlineKeyboardButton(
                f"🆘 {T[lang].get('stars_help', 'Help')}", 
                callback_data="stars:help"
            )
            keyboard.add(buy_stars_btn, help_btn)
            
            # Free stars button if feature is enabled
            if BotConfig.feature_flags.free_stars_enabled:
                free_stars_btn = types.InlineKeyboardButton(
                    f"✨ {T[lang].get('free_stars', 'Free Stars')}", 
                    callback_data="stars:free_stars"
                )
                keyboard.add(free_stars_btn)
            
            # Utility buttons
            refresh_btn = types.InlineKeyboardButton(
                f"🔄 {T[lang].get('refresh_balance', 'Refresh Balance')}", 
                callback_data="stars:refresh"
            )
            close_btn = types.InlineKeyboardButton(
                f"❌ {T[lang].get('close_stars_menu', 'Close')}", 
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
                "❌ Error displaying TG Stars dashboard. Please try again."
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
                    T[lang].get('stars_error_item_unavailable', '❌ This item is currently unavailable.'), 
                    show_alert=True
                )
                return
            
            # Build premium shop message
            shop_text = f"🛒 <b>{T[lang].get('premium_catalog', 'Premium Catalog')}</b>\n\n"
            shop_text += f"⭐ {T[lang].get('current_stars_balance', 'Current Balance: ⭐ {stars} TG Stars').format(stars=stars_balance)}\n\n"
            shop_text += f"💎 <b>{T[lang].get('exclusive_items', 'Exclusive Items')}</b>:\n\n"
            
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
                    item_desc += f"⚔️ {T[lang].get('damage', 'Damage')}: {stats['damage']}\n"
                if stats.get('duration_seconds'):
                    hours = stats['duration_seconds'] // 3600
                    item_desc += f"⏱️ {T[lang].get('duration', 'Duration')}: {hours} {T[lang].get('hours', 'hours')}\n"
                
                shop_text += item_desc
                shop_text += f"💰 {T[lang].get('item_requires_stars', 'Requires ⭐ {price} TG Stars').format(price=price)}\n\n"
                
                # Can afford check
                can_afford = await self.can_afford_premium_item(call.message.chat.id, call.from_user.id, item_id)
                if can_afford:
                    button_text = f"✅ {emoji} {item_name} - ⭐{price}"
                    callback_data = f"stars:buy:{item_id}"
                else:
                    button_text = f"❌ {emoji} {item_name} - ⭐{price}"
                    callback_data = f"stars:insufficient:{item_id}"
                
                item_btn = types.InlineKeyboardButton(button_text, callback_data=callback_data)
                keyboard.add(item_btn)
            
            # Navigation buttons
            back_btn = types.InlineKeyboardButton(
                f"🔙 {T[lang].get('back_btn', 'Back')}", 
                callback_data="stars:main"
            )
            close_btn = types.InlineKeyboardButton(
                f"❌ {T[lang].get('close_stars_menu', 'Close')}", 
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
            await bot.answer_callback_query(
                call.id, 
                T[lang].get('stars_error_generic', '❌ An error occurred with TG Stars system.')
            )
    
    async def show_transaction_history(self, bot: AsyncTeleBot, call: types.CallbackQuery):
        """Display user's transaction history"""
        try:
            lang = await helpers.get_lang(call.message.chat.id, call.from_user.id, self.db_manager)
            transactions = await self.get_transaction_history(call.message.chat.id, call.from_user.id)
            
            history_text = f"📊 <b>{T[lang].get('transaction_history', 'Transaction History')}</b>\n\n"
            
            if not transactions:
                history_text += f"{T[lang].get('no_transactions', 'No transactions found.')}\n\n"
                history_text += f"💡 {T[lang].get('stars_purchase_info', 'You can purchase TG Stars directly through Telegram\'s payment system.')}"
            else:
                for tx in transactions:
                    item_name = get_item_display_name(tx['item_id'], lang)
                    emoji = get_item_emoji(tx['item_id'])
                    status_emoji = "✅" if tx['status'] == 'completed' else "⏳" if tx['status'] == 'pending' else "❌"
                    
                    history_text += f"{status_emoji} {emoji} <b>{item_name}</b>\n"
                    history_text += f"💰 {tx['amount']} ⭐ | {tx['date'].strftime('%Y-%m-%d %H:%M')}\n"
                    history_text += f"📝 {T[lang].get(f'transaction_{tx['status']}', tx['status'])}\n\n"
            
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(
                types.InlineKeyboardButton(f"🔙 {T[lang].get('back_btn', 'Back')}", callback_data="stars:main"),
                types.InlineKeyboardButton(f"❌ {T[lang].get('close_stars_menu', 'Close')}", callback_data="stars:close")
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
            await bot.answer_callback_query(
                call.id, 
                T[lang].get('stars_error_generic', '❌ An error occurred with TG Stars system.')
            )
    
    async def show_stars_help(self, bot: AsyncTeleBot, call: types.CallbackQuery):
        """Display TG Stars help and FAQ"""
        try:
            lang = await helpers.get_lang(call.message.chat.id, call.from_user.id, self.db_manager)
            
            help_text = f"🆘 <b>{T[lang].get('stars_help', 'TG Stars Help')}</b>\n\n"
            help_text += f"❓ <b>{T[lang].get('stars_faq', 'Frequently Asked Questions')}</b>\n\n"
            
            if lang == "fa":
                help_text += """
<b>🌟 ستاره‌های تلگرام چیست؟</b>
ستاره‌های تلگرام ارز ویژه‌ای هستند که توسط تلگرام ارائه می‌شوند و برای خرید آیتم‌ها و ویژگی‌های ویژه استفاده می‌شوند.

<b>💰 چگونه ستاره‌های تلگرام خریداری کنم؟</b>
می‌توانید مستقیماً از طریق سیستم پرداخت تلگرام ستاره‌های تلگرام خریداری کنید.

<b>🛒 چه آیتم‌هایی با ستاره‌های تلگرام قابل خرید هستند؟</b>
آیتم‌های ویژه و انحصاری که در فروشگاه ویژه موجود هستند، شامل تسلیحات پیشرفته و توانایی‌های ویژه.

<b>🔄 آیا ستاره‌های تلگرام قابل بازگشت هستند؟</b>
بر اساس سیاست‌های تلگرام، ستاره‌های تلگرام معمولاً قابل بازگشت نیستند.

<b>📱 آیا می‌توانم ستاره‌های تلگرام را انتقال دهم؟</b>
ستاره‌های تلگرام قابل انتقال به سایر کاربران نیستند.
                """
            else:
                help_text += """
<b>🌟 What are TG Stars?</b>
TG Stars are a premium currency provided by Telegram for purchasing special items and features.

<b>💰 How do I buy TG Stars?</b>
You can purchase TG Stars directly through Telegram's payment system.

<b>🛒 What can I buy with TG Stars?</b>
Exclusive premium items available in the premium shop, including advanced weapons and special abilities.

<b>🔄 Are TG Stars refundable?</b>
According to Telegram's policies, TG Stars are generally non-refundable.

<b>📱 Can I transfer TG Stars?</b>
TG Stars cannot be transferred to other users.
                """
            
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(
                types.InlineKeyboardButton(f"📞 {T[lang].get('stars_support', 'Contact Support')}", url="https://t.me/bettercallninja"),
                types.InlineKeyboardButton(f"📜 {T[lang].get('stars_terms', 'Terms of Service')}", callback_data="stars:terms")
            )
            keyboard.add(
                types.InlineKeyboardButton(f"🔙 {T[lang].get('back_btn', 'Back')}", callback_data="stars:main"),
                types.InlineKeyboardButton(f"❌ {T[lang].get('close_stars_menu', 'Close')}", callback_data="stars:close")
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
            await bot.answer_callback_query(
                call.id, 
                T[lang].get('stars_error_generic', '❌ An error occurred with TG Stars system.')
            )
    
    async def handle_stars_callback(self, bot: AsyncTeleBot, call: types.CallbackQuery):
        """Handle all TG Stars related callbacks"""
        try:
            data_parts = call.data.split(':')
            action = data_parts[1] if len(data_parts) > 1 else "main"
            lang = await helpers.get_lang(call.message.chat.id, call.from_user.id, self.db_manager)

            if action == "main":
                # Refresh the main dashboard
                stars_balance = await self.get_user_stars_balance(call.message.chat.id, call.from_user.id)
                dashboard_text = f"💎 <b>{T[lang].get('stars_welcome', 'TG Stars Dashboard')}</b>\n\n"
                dashboard_text += f"⭐ <b>{T[lang].get('stars_balance_overview', 'Your TG Stars Balance')}</b>\n"
                dashboard_text += f"{T[lang].get('current_stars_balance', 'Current Balance: ⭐ {stars} TG Stars').format(stars=stars_balance)}\n\n"
                dashboard_text += f"📝 <b>{T[lang].get('stars_description', 'TG Stars are premium currency that can be used to purchase exclusive items and features.')}</b>\n\n"
                dashboard_text += f"🌟 <b>{T[lang].get('premium_features', 'Premium Features')}</b>\n"
                dashboard_text += f"{T[lang].get('feature_exclusive_weapons', '• Access to exclusive premium weapons')}\n"
                dashboard_text += f"{T[lang].get('feature_special_abilities', '• Unlock special combat abilities')}\n"
                dashboard_text += f"{T[lang].get('feature_premium_support', '• Priority customer support')}\n"
                dashboard_text += f"{T[lang].get('feature_advanced_stats', '• Advanced statistics and analytics')}\n"
                dashboard_text += f"{T[lang].get('feature_custom_themes', '• Custom themes and personalization')}\n"
                dashboard_text += f"{T[lang].get('feature_early_access', '• Early access to new features')}"
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                keyboard.add(
                    types.InlineKeyboardButton(f"🛒 {T[lang].get('view_premium_shop', 'View Premium Shop')}", callback_data="stars:premium_shop"),
                    types.InlineKeyboardButton(f"📊 {T[lang].get('view_history', 'View History')}", callback_data="stars:history")
                )
                keyboard.add(
                    types.InlineKeyboardButton(f"💰 {T[lang].get('buy_stars', 'Buy TG Stars')}", callback_data="stars:buy_stars"),
                    types.InlineKeyboardButton(f"🆘 {T[lang].get('stars_help', 'Help')}", callback_data="stars:help")
                )
                
                # Free stars button if feature is enabled
                if BotConfig.feature_flags.free_stars_enabled:
                    free_stars_btn = types.InlineKeyboardButton(
                        f"✨ {T[lang].get('free_stars', 'Free Stars')}", 
                        callback_data="stars:free_stars"
                    )
                    keyboard.add(free_stars_btn)
                
                keyboard.add(
                    types.InlineKeyboardButton(f"🔄 {T[lang].get('refresh_balance', 'Refresh Balance')}", callback_data="stars:refresh"),
                    types.InlineKeyboardButton(f"❌ {T[lang].get('close_stars_menu', 'Close')}", callback_data="stars:close")
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
                if not item_id:
                    await bot.answer_callback_query(
                        call.id,
                        T[lang].get('stars_error_item_unavailable', '❌ This item is currently unavailable.'),
                        show_alert=True
                    )
                    return
                
                # Process the purchase
                success = await self.purchase_premium_item(
                    call.message.chat.id, 
                    call.from_user.id, 
                    item_id
                )
                
                if success:
                    item_name = get_item_display_name(item_id, lang)
                    price = ITEMS.get(item_id, {}).get('stars_price', 0)
                    
                    # Success message
                    if lang == "fa":
                        success_msg = f"✅ <b>خرید موفق!</b>\n\n{item_name} با موفقیت به انبار شما اضافه شد!\n\n💰 هزینه: {price} ستاره تلگرام"
                    else:
                        success_msg = f"✅ <b>Purchase Successful!</b>\n\n{item_name} has been added to your inventory!\n\n💰 Cost: {price} TG Stars"
                    
                    # Show success message
                    await bot.answer_callback_query(
                        call.id,
                        T[lang].get('purchase_successful', '✅ Purchase successful!'),
                        show_alert=True
                    )
                    
                    # Update message text with success
                    await bot.edit_message_text(
                        success_msg,
                        call.message.chat.id,
                        call.message.message_id,
                        parse_mode="HTML"
                    )
                    
                    # Send a keyboard to return to shop or inventory
                    keyboard = types.InlineKeyboardMarkup(row_width=2)
                    keyboard.add(
                        types.InlineKeyboardButton(
                            f"🛒 {T[lang].get('view_premium_shop', 'View Premium Shop')}", 
                            callback_data="stars:premium_shop"
                        ),
                        types.InlineKeyboardButton(
                            f"📦 {T[lang].get('view_inventory', 'View Inventory')}", 
                            callback_data="quick:inventory"
                        )
                    )
                    keyboard.add(
                        types.InlineKeyboardButton(
                            f"🔙 {T[lang].get('back_to_stars', 'Back to Stars')}", 
                            callback_data="stars:main"
                        )
                    )
                    
                    # Update with new keyboard
                    await bot.edit_message_reply_markup(
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=keyboard
                    )
                else:
                    # Purchase failed
                    await bot.answer_callback_query(
                        call.id,
                        T[lang].get('purchase_failed', '❌ Purchase failed. Please try again.'),
                        show_alert=True
                    )
            
            elif action == "insufficient":
                item_id = data_parts[2] if len(data_parts) > 2 else ""
                item = ITEMS.get(item_id, {})
                price = item.get('stars_price', 0)
                user_stars = await self.get_user_stars_balance(call.message.chat.id, call.from_user.id)
                needed = price - user_stars
                
                await bot.answer_callback_query(
                    call.id,
                    T[lang].get('insufficient_stars', '❌ Not enough TG Stars! You need {required} more.').format(required=needed),
                    show_alert=True
                )
            
            elif action == "buy_stars":
                if BotConfig.feature_flags.free_stars_enabled:
                    # Inform about free stars
                    if lang == "fa":
                        message = "✨ در حال حاضر، ستاره‌های تلگرام رایگان هستند! برای دریافت ستاره‌های رایگان، از دکمه 'ستاره‌های رایگان' استفاده کنید."
                    else:
                        message = "✨ Currently, TG Stars are free! Use the 'Free Stars' button to get free stars."
                    
                    await bot.answer_callback_query(
                        call.id,
                        message,
                        show_alert=True
                    )
                else:
                    # Regular stars purchase info
                    await bot.answer_callback_query(
                        call.id,
                        T[lang].get('stars_purchase_info', 'You can purchase TG Stars directly through Telegram\'s payment system.'),
                        show_alert=True
                    )
            
            elif action == "free_stars":
                if BotConfig.feature_flags.free_stars_enabled:
                    # Process free stars
                    await self.process_free_stars(call.message.chat.id, call.from_user.id, bot, lang)
                    
                    # Show confirmation
                    if lang == "fa":
                        success_msg = "✅ ستاره‌های رایگان به حساب شما اضافه شدند!"
                    else:
                        success_msg = "✅ Free stars have been added to your account!"
                    
                    await bot.answer_callback_query(
                        call.id,
                        success_msg,
                        show_alert=True
                    )
                    
                    # Refresh main stars dashboard
                    # Create a modified call object for the main dashboard
                    main_call = call
                    main_call.data = "stars:main"
                    await self.handle_stars_callback(bot, main_call)
                else:
                    await bot.answer_callback_query(
                        call.id,
                        T[lang].get('feature_disabled', '❌ This feature is currently disabled.'),
                        show_alert=True
                    )
            
            elif action == "refresh":
                await bot.answer_callback_query(call.id, "🔄 Balance refreshed!")
                # Trigger main dashboard refresh
                main_call = call
                main_call.data = "stars:main"
                await self.handle_stars_callback(bot, main_call)
            
            elif action == "close":
                await bot.delete_message(call.message.chat.id, call.message.message_id)
                await bot.answer_callback_query(call.id)
                return
            
            await bot.answer_callback_query(call.id)
            
        except Exception as e:
            logger.error(f"Error handling stars callback: {e}")
            await bot.answer_callback_query(call.id, "❌ Error processing request.")
    
    async def _initiate_purchase(self, call: types.CallbackQuery, bot: AsyncTeleBot, lang: str, item_id: str):
        """Creates an invoice for a TG Stars purchase."""
        try:
            item = ITEMS.get(item_id)
            if not item or item.get('payment') != 'tg_stars':
                await bot.answer_callback_query(
                    call.id, 
                    T[lang].get('item_not_found', '❌ Item not found or not available for TG Stars purchase.'), 
                    show_alert=True
                )
                return

            price = item.get('stars_price', 0)
            if price <= 0:
                await bot.answer_callback_query(
                    call.id, 
                    T[lang].get('item_not_for_sale', '❌ This item is not for sale.'), 
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
                title = f"🌟 خرید {item_name}"
                description = f"خرید {item_name} با {price} ستاره تلگرام\n\n💎 آیتم پریمیوم انحصاری\n🔥 دسترسی فوری پس از پرداخت"
            else:
                title = f"🌟 Purchase {item_name}"
                description = f"Purchase {item_name} for {price} Telegram Stars\n\n💎 Exclusive premium item\n🔥 Instant access after payment"

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
                f"✨ {T[lang].get('invoice_sent', 'Invoice sent successfully!')}\n\n"
                f"💰 {T[lang].get('total_cost', 'Total cost')}: {price} ⭐\n"
                f"🛒 {T[lang].get('item', 'Item')}: {item_name}\n\n"
                f"📝 {T[lang].get('payment_instructions', 'Click the invoice above to complete your purchase.')}"
            )
            
            await bot.answer_callback_query(call.id, "✅ Invoice created!")
            
        except Exception as e:
            logger.error(f"Failed to create TG Stars invoice: {e}")
            error_msg = (
                "❌ خطا در ایجاد صورتحساب. لطفاً مجدداً تلاش کنید." if lang == 'fa' 
                else "❌ Failed to create invoice. Please try again."
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
            error_msg = "پیلود نامعتبر" if lang == 'fa' else "Invalid payload"
            await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=False, error_message=error_msg)
            return
            
        item_id = payload_parts[1]
        user_id = int(payload_parts[2])

        # Basic validation
        if pre_checkout_query.from_user.id != user_id:
            error_msg = "عدم تطبیق شناسه کاربر" if lang == 'fa' else "User ID mismatch"
            await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=False, error_message=error_msg)
            return

        item = ITEMS.get(item_id)
        if not item or item.get('stars_price') != pre_checkout_query.total_amount:
            error_msg = "عدم تطبیق آیتم یا قیمت" if lang == 'fa' else "Item or price mismatch"
            await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=False, error_message=error_msg)
            return

        # Everything is okay, confirm the transaction
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
        
    except Exception as e:
        logger.error(f"Error in pre-checkout validation: {e}")
        error_msg = "خطا در اعتبارسنجی پرداخت" if lang == 'fa' else "Payment validation error"
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
            success_msg = f"""🎉 <b>خرید موفق!</b>

✅ {emoji} <b>{item_name}</b> با موفقیت به انبار شما اضافه شد!

💰 مبلغ پرداختی: {payment_info.total_amount} ⭐
🆔 شناسه تراکنش: <code>{payment_info.telegram_payment_charge_id}</code>

🎮 از آیتم جدید خود استفاده کنید!
🪄 برای خرید آیتم‌های بیشتر از دستور /stars استفاده کنید."""
        else:
            success_msg = f"""🎉 <b>Purchase Successful!</b>

✅ {emoji} <b>{item_name}</b> has been added to your inventory!

💰 Amount paid: {payment_info.total_amount} ⭐
🆔 Transaction ID: <code>{payment_info.telegram_payment_charge_id}</code>

🎮 Enjoy your new item!
🪄 Use /stars command to purchase more items."""

        # Create a keyboard with relevant actions
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        
        # View inventory button
        inventory_btn = types.InlineKeyboardButton(
            f"📦 {('مشاهده انبار' if lang == 'fa' else 'View Inventory')}", 
            callback_data="inventory:show"
        )
        
        # View more premium items button
        shop_btn = types.InlineKeyboardButton(
            f"🛒 {('فروشگاه ویژه' if lang == 'fa' else 'Premium Shop')}", 
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
            "❌ خطایی در پردازش پرداخت شما رخ داد. لطفاً با پشتیبانی تماس بگیرید." if lang == 'fa'
            else "❌ An error occurred processing your payment. Please contact support."
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

