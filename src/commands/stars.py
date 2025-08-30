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
            dashboard_text = f"💎 <b>{T['stars_welcome'][lang]}</b>\n\n"
            dashboard_text += f"⭐ <b>{T['stars_balance_overview'][lang]}</b>\n"
            dashboard_text += f"{T['current_stars_balance'][lang].format(stars=stars_balance)}\n\n"
            dashboard_text += f"📝 <b>{T['stars_description'][lang]}</b>\n\n"
            
            # Add features section
            dashboard_text += f"🌟 <b>{T['premium_features'][lang]}</b>\n"
            dashboard_text += f"{T['feature_exclusive_weapons'][lang]}\n"
            dashboard_text += f"{T['feature_special_abilities'][lang]}\n"
            dashboard_text += f"{T['feature_premium_support'][lang]}\n"
            dashboard_text += f"{T['feature_advanced_stats'][lang]}\n"
            dashboard_text += f"{T['feature_custom_themes'][lang]}\n"
            dashboard_text += f"{T['feature_early_access'][lang]}"
            
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            
            # Main action buttons
            premium_shop_btn = types.InlineKeyboardButton(
                f"🛒 {T['view_premium_shop'][lang]}", 
                callback_data="stars:premium_shop"
            )
            history_btn = types.InlineKeyboardButton(
                f"📊 {T['view_history'][lang]}", 
                callback_data="stars:history"
            )
            keyboard.add(premium_shop_btn, history_btn)
            
            # Additional features
            buy_stars_btn = types.InlineKeyboardButton(
                f"💰 {T['buy_stars'][lang]}", 
                callback_data="stars:buy_stars"
            )
            help_btn = types.InlineKeyboardButton(
                f"🆘 {T['stars_help'][lang]}", 
                callback_data="stars:help"
            )
            keyboard.add(buy_stars_btn, help_btn)
            
            # Utility buttons
            refresh_btn = types.InlineKeyboardButton(
                f"🔄 {T['refresh_balance'][lang]}", 
                callback_data="stars:refresh"
            )
            close_btn = types.InlineKeyboardButton(
                f"❌ {T['close_stars_menu'][lang]}", 
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
                    T['stars_error_item_unavailable'][lang], 
                    show_alert=True
                )
                return
            
            # Build premium shop message
            shop_text = f"🛒 <b>{T['premium_catalog'][lang]}</b>\n\n"
            shop_text += f"⭐ {T['current_stars_balance'][lang].format(stars=stars_balance)}\n\n"
            shop_text += f"💎 <b>{T['exclusive_items'][lang]}</b>:\n\n"
            
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
                    item_desc += f"⚔️ {T['damage'][lang]}: {stats['damage']}\n"
                if stats.get('duration_seconds'):
                    hours = stats['duration_seconds'] // 3600
                    item_desc += f"⏱️ {T['duration'][lang]}: {hours} {T['hours'][lang]}\n"
                
                shop_text += item_desc
                shop_text += f"💰 {T['item_requires_stars'][lang].format(price=price)}\n"
                
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
                shop_text += "\n"
            
            # Navigation buttons
            back_btn = types.InlineKeyboardButton(
                f"🔙 {T['back_btn'][lang]}", 
                callback_data="stars:main"
            )
            close_btn = types.InlineKeyboardButton(
                f"❌ {T['close_stars_menu'][lang]}", 
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
            await bot.answer_callback_query(call.id, T['stars_error_generic'][lang])
    
    async def show_transaction_history(self, bot: AsyncTeleBot, call: types.CallbackQuery):
        """Display user's transaction history"""
        try:
            lang = await helpers.get_lang(call.message.chat.id, call.from_user.id, self.db_manager)
            transactions = await self.get_transaction_history(call.message.chat.id, call.from_user.id)
            
            history_text = f"📊 <b>{T['transaction_history'][lang]}</b>\n\n"
            
            if not transactions:
                history_text += f"{T['no_transactions'][lang]}\n\n"
                history_text += f"💡 {T['stars_purchase_info'][lang]}"
            else:
                for tx in transactions:
                    item_name = get_item_display_name(tx['item_id'], lang)
                    emoji = get_item_emoji(tx['item_id'])
                    status_emoji = "✅" if tx['status'] == 'completed' else "⏳" if tx['status'] == 'pending' else "❌"
                    
                    history_text += f"{status_emoji} {emoji} <b>{item_name}</b>\n"
                    history_text += f"💰 {tx['amount']} ⭐ | {tx['date'].strftime('%Y-%m-%d %H:%M')}\n"
                    history_text += f"📋 {T[f'transaction_{tx["status"]}'][lang]}\n\n"
            
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(
                types.InlineKeyboardButton(f"🔙 {T['back_btn'][lang]}", callback_data="stars:main"),
                types.InlineKeyboardButton(f"❌ {T['close_stars_menu'][lang]}", callback_data="stars:close")
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
            await bot.answer_callback_query(call.id, T['stars_error_generic'][lang])
    
    async def show_stars_help(self, bot: AsyncTeleBot, call: types.CallbackQuery):
        """Display TG Stars help and FAQ"""
        try:
            lang = await helpers.get_lang(call.message.chat.id, call.from_user.id, self.db_manager)
            
            help_text = f"🆘 <b>{T['stars_help'][lang]}</b>\n\n"
            help_text += f"❓ <b>{T['stars_faq'][lang]}</b>\n\n"
            
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
                types.InlineKeyboardButton(f"📞 {T['stars_support'][lang]}", url="https://t.me/TrumpBotSupport"),
                types.InlineKeyboardButton(f"📜 {T['stars_terms'][lang]}", callback_data="stars:terms")
            )
            keyboard.add(
                types.InlineKeyboardButton(f"🔙 {T['back_btn'][lang]}", callback_data="stars:main"),
                types.InlineKeyboardButton(f"❌ {T['close_stars_menu'][lang]}", callback_data="stars:close")
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
            await bot.answer_callback_query(call.id, T['stars_error_generic'][lang])
    
    async def handle_stars_callback(self, bot: AsyncTeleBot, call: types.CallbackQuery):
        """Handle all TG Stars related callbacks"""
        try:
            data_parts = call.data.split(':')
            action = data_parts[1] if len(data_parts) > 1 else "main"
            lang = await helpers.get_lang(call.message.chat.id, call.from_user.id, self.db_manager)

            if action == "main":
                # Refresh the main dashboard
                stars_balance = await self.get_user_stars_balance(call.message.chat.id, call.from_user.id)
                dashboard_text = f"💎 <b>{T['stars_welcome'][lang]}</b>\n\n"
                dashboard_text += f"⭐ <b>{T['stars_balance_overview'][lang]}</b>\n"
                dashboard_text += f"{T['current_stars_balance'][lang].format(stars=stars_balance)}\n\n"
                dashboard_text += f"📝 <b>{T['stars_description'][lang]}</b>\n\n"
                dashboard_text += f"🌟 <b>{T['premium_features'][lang]}</b>\n"
                dashboard_text += f"{T['feature_exclusive_weapons'][lang]}\n"
                dashboard_text += f"{T['feature_special_abilities'][lang]}\n"
                dashboard_text += f"{T['feature_premium_support'][lang]}\n"
                dashboard_text += f"{T['feature_advanced_stats'][lang]}\n"
                dashboard_text += f"{T['feature_custom_themes'][lang]}\n"
                dashboard_text += f"{T['feature_early_access'][lang]}"

                keyboard = types.InlineKeyboardMarkup(row_width=2)
                keyboard.add(
                    types.InlineKeyboardButton(f"🛒 {T['view_premium_shop'][lang]}", callback_data="stars:premium_shop"),
                    types.InlineKeyboardButton(f"📊 {T['view_history'][lang]}", callback_data="stars:history")
                )
                keyboard.add(
                    types.InlineKeyboardButton(f"💰 {T['buy_stars'][lang]}", callback_data="stars:buy_stars"),
                    types.InlineKeyboardButton(f"🆘 {T['stars_help'][lang]}", callback_data="stars:help")
                )
                keyboard.add(
                    types.InlineKeyboardButton(f"🔄 {T['refresh_balance'][lang]}", callback_data="stars:refresh"),
                    types.InlineKeyboardButton(f"❌ {T['close_stars_menu'][lang]}", callback_data="stars:close")
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
                await self._initiate_purchase(call, bot, self.db_manager, lang, item_id)
            
            elif action == "insufficient":
                item_id = data_parts[2] if len(data_parts) > 2 else ""
                item = ITEMS.get(item_id, {})
                price = item.get('stars_price', 0)
                user_stars = await self.get_user_stars_balance(call.message.chat.id, call.from_user.id)
                needed = price - user_stars
                
                await bot.answer_callback_query(
                    call.id,
                    T['insufficient_stars'][lang].format(required=needed),
                    show_alert=True
                )
            
            elif action == "buy_stars":
                await bot.answer_callback_query(
                    call.id,
                    T['stars_purchase_info'][lang],
                    show_alert=True
                )
            
            elif action == "refresh":
                await bot.answer_callback_query(call.id, "🔄 Balance refreshed!")
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
            await bot.answer_callback_query(call.id, "❌ Error processing request.")


async def _initiate_purchase(call: types.CallbackQuery, bot: AsyncTeleBot, db_manager: DBManager, lang: str, item_id: str):
    """Creates an invoice for a TG Stars purchase."""
    item = ITEMS.get(item_id)
    if not item or item.get('payment') != 'tg_stars':
        await bot.answer_callback_query(call.id, T['item_not_found'][lang], show_alert=True)
        return

    price = item.get('stars_price', 0)
    if price <= 0:
        await bot.answer_callback_query(call.id, T['item_not_for_sale'][lang], show_alert=True)
        return

    # Create an invoice
    item_name = get_item_display_name(item_id, lang)
    invoice = types.LabeledPrice(label=item_name, amount=price)
    
    # The payload should contain information to identify the purchase later
    payload = f"purchase:{item_id}:{call.from_user.id}"

    try:
        await bot.send_invoice(
            chat_id=call.message.chat.id,
            title=T['invoice_title'][lang],
            description=T['invoice_description'][lang].format(item_name=item_name),
            invoice_payload=payload,
            provider_token='',  # No provider token needed for Stars
            currency='XTR',
            prices=[invoice]
        )
    except Exception as e:
        logger.error(f"Failed to create TG Stars invoice: {e}")
        await bot.answer_callback_query(call.id, T['invoice_creation_failed'][lang], show_alert=True)


async def handle_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery, bot: AsyncTeleBot, db_manager: DBManager):
    """Handles the pre-checkout query to validate the purchase."""
    # The payload was set during invoice creation
    payload_parts = pre_checkout_query.invoice_payload.split(':')
    item_id = payload_parts[1]
    user_id = int(payload_parts[2])

    # Basic validation
    if pre_checkout_query.from_user.id != user_id:
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=False, error_message="User ID mismatch.")
        return

    item = ITEMS.get(item_id)
    if not item or item.get('stars_price') != pre_checkout_query.total_amount:
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=False, error_message="Item or price mismatch.")
        return

    # Everything is okay, confirm the transaction
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


async def handle_successful_payment(message: types.Message, bot: AsyncTeleBot, db_manager: DBManager):
    """Handles a successful payment and grants the item to the user."""
    payment_info = message.successful_payment
    payload_parts = payment_info.invoice_payload.split(':')
    item_id = payload_parts[1]
    
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
    """, (message.chat.id, message.from_user.id, payment_info.telegram_payment_charge_id, item_id, payment_info.total_amount, helpers.now()))

    lang = await helpers.get_lang(message.chat.id, message.from_user.id, db_manager)
    item_name = get_item_display_name(item_id, lang)
    await bot.send_message(message.chat.id, T['purchase_successful_stars'][lang].format(item_name=item_name))


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
