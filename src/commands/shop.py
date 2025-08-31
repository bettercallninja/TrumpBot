#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Shop commands module with comprehensive shopping system
Provides advanced shop functionality with categories, TG Stars, and bilingual support
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from src.utils import helpers
from src.utils.translations import T
from src.database.db_manager import DBManager
from src.config.items import (
    ITEMS, ItemType, PaymentType, ItemCategory,
    get_item_display_name, get_item_description, get_item_emoji,
    get_item_stats, get_items_by_category, get_items_by_payment_type
)

# Set up logging
logger = logging.getLogger(__name__)

class ShopManager:
    """Manages comprehensive shop system with categories and payment types"""
    
    def __init__(self, db_manager: DBManager):
        self.db_manager = db_manager
    
    async def get_user_currency(self, chat_id: int, user_id: int) -> Dict[str, int]:
        """Get user's available currencies"""
        try:
            # Get medals from helpers
            medals = await helpers.medals(user_id, chat_id, self.db_manager)
            
            # Get TG Stars from database
            tg_stars = await self.db_manager.db(
                "SELECT tg_stars FROM players WHERE chat_id=%s AND user_id=%s",
                (chat_id, user_id),
                fetch="one"
            )
            
            return {
                'medals': medals,
                'tg_stars': tg_stars[0] if tg_stars else 0
            }
        except Exception as e:
            logger.error(f"Error getting user currency: {e}")
            return {'medals': 0, 'tg_stars': 0}
    
    async def get_item_price(self, item_id: str) -> Tuple[int, str]:
        """Get item price and payment type"""
        try:
            item = ITEMS.get(item_id, {})
            payment_type = item.get('payment', PaymentType.MEDALS.value)
            
            if payment_type == PaymentType.TG_STARS.value:
                price = item.get('stars_price', 1)
                return price, 'tg_stars'
            else:
                # Calculate medal price based on stars
                stars = item.get('stars', 1)
                base_price = 50
                price = base_price * (2 ** (stars - 1))
                return price, 'medals'
        except Exception as e:
            logger.error(f"Error getting item price for {item_id}: {e}")
            return 0, 'medals'
    
    async def can_afford_item(self, chat_id: int, user_id: int, item_id: str) -> bool:
        """Check if user can afford the item"""
        try:
            price, payment_type = await self.get_item_price(item_id)
            user_currency = await self.get_user_currency(chat_id, user_id)
            
            return user_currency.get(payment_type, 0) >= price
        except Exception as e:
            logger.error(f"Error checking affordability: {e}")
            return False
    
    async def purchase_item(self, chat_id: int, user_id: int, item_id: str) -> bool:
        """Purchase an item and add to inventory"""
        try:
            price, payment_type = await self.get_item_price(item_id)
            
            # Check if user can afford it
            if not await self.can_afford_item(chat_id, user_id, item_id):
                return False
            
            # Start transaction
            async with self.db_manager.get_connection() as conn:
                async with conn.transaction():
                    # Deduct currency
                    if payment_type == 'medals':
                        await helpers.add_medals(chat_id, user_id, -price, self.db_manager)
                    else:  # TG Stars
                        await conn.execute(
                            "UPDATE players SET tg_stars = tg_stars - $1 WHERE chat_id=$2 AND user_id=$3",
                            price, chat_id, user_id
                        )
                    
                    # Add item to inventory
                    await conn.execute("""
                        INSERT INTO inventories (chat_id, user_id, item, qty)
                        VALUES ($1, $2, $3, 1)
                        ON CONFLICT (chat_id, user_id, item) DO UPDATE
                        SET qty = inventories.qty + 1
                    """, chat_id, user_id, item_id)
            
            return True
        except Exception as e:
            logger.error(f"Error purchasing item {item_id}: {e}")
            return False
    
    async def show_shop_overview(self, bot: AsyncTeleBot, message: types.Message):
        """Display comprehensive shop overview with categories"""
        try:
            lang = await helpers.get_lang(message.chat.id, message.from_user.id, self.db_manager)
            user_currency = await self.get_user_currency(message.chat.id, message.from_user.id)
            
            # Build shop overview message
            shop_text = f"🛍️ <b>{T[lang]['shop_welcome']}</b>\n\n"
            shop_text += f"💰 <b>{T[lang]['your_balance']}:</b>\n"
            shop_text += f"🏅 {T[lang]['medals']}: <b>{user_currency['medals']}</b>\n"
            shop_text += f"⭐ {T[lang]['tg_stars']}: <b>{user_currency['tg_stars']}</b>\n\n"
            shop_text += f"{T[lang]['shop_categories_intro']}"
            
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            
            # Category buttons
            weapons_btn = types.InlineKeyboardButton(
                f"⚔️ {T[lang]['category_weapons']}", 
                callback_data="shop:category:weapons"
            )
            defense_btn = types.InlineKeyboardButton(
                f"🛡️ {T[lang]['category_defense']}", 
                callback_data="shop:category:defense"
            )
            keyboard.add(weapons_btn, defense_btn)
            
            other_btn = types.InlineKeyboardButton(
                f"📦 {T[lang]['category_other']}", 
                callback_data="shop:category:other"
            )
            premium_btn = types.InlineKeyboardButton(
                f"💎 {T[lang]['premium_items']}", 
                callback_data="shop:payment:tg_stars"
            )
            keyboard.add(other_btn, premium_btn)
            
            # Quick access buttons
            all_items_btn = types.InlineKeyboardButton(
                f"📋 {T[lang]['all_items']}", 
                callback_data="shop:all"
            )
            close_btn = types.InlineKeyboardButton(
                f"❌ {T[lang]['close_button']}", 
                callback_data="shop:close"
            )
            keyboard.add(all_items_btn, close_btn)
            
            await bot.send_message(
                message.chat.id, 
                shop_text, 
                reply_markup=keyboard, 
                parse_mode="HTML"
            )
            
        except Exception as e:
            logger.error(f"Error showing shop overview: {e}")
            await bot.send_message(
                message.chat.id, 
                "❌ Error displaying shop. Please try again."
            )
    
    async def show_shop_category(self, bot: AsyncTeleBot, call: types.CallbackQuery, category: str):
        """Display items in a specific category"""
        try:
            lang = await helpers.get_lang(call.message.chat.id, call.from_user.id, self.db_manager)
            user_currency = await self.get_user_currency(call.message.chat.id, call.from_user.id)
            
            # Get items by category
            if category == "all":
                items = ITEMS
                title = T[lang]['all_items']
            else:
                items = get_items_by_category(ItemCategory(category))
                title = T[lang][f'category_{category}']
            
            if not items:
                await bot.answer_callback_query(
                    call.id, 
                    T[lang]['no_items_in_category'], 
                    show_alert=True
                )
                return
            
            # Build category message
            shop_text = f"🛍️ <b>{title}</b>\n\n"
            shop_text += f"💰 {T[lang]['medals']}: <b>{user_currency['medals']}</b> | "
            shop_text += f"⭐ {T[lang]['tg_stars']}: <b>{user_currency['tg_stars']}</b>\n\n"
            
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            
            # Add item buttons
            for item_id, item_data in items.items():
                item_name = get_item_display_name(item_id, lang)
                emoji = get_item_emoji(item_id)
                price, payment_type = await self.get_item_price(item_id)
                
                # Format price with appropriate currency
                if payment_type == 'medals':
                    price_text = f"{price} 🏅"
                else:
                    price_text = f"{price} ⭐"
                
                # Check affordability
                can_afford = await self.can_afford_item(call.message.chat.id, call.from_user.id, item_id)
                prefix = "✅" if can_afford else "❌"
                
                button_text = f"{prefix} {emoji} {item_name} - {price_text}"
                keyboard.add(types.InlineKeyboardButton(
                    button_text, 
                    callback_data=f"shop:item:{item_id}"
                ))
            
            # Navigation buttons
            back_btn = types.InlineKeyboardButton(
                f"🔙 {T[lang]['back_to_shop']}", 
                callback_data="shop:main"
            )
            close_btn = types.InlineKeyboardButton(
                f"❌ {T[lang]['close_button']}", 
                callback_data="shop:close"
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
            logger.error(f"Error showing shop category {category}: {e}")
            await bot.answer_callback_query(call.id, "❌ Error loading category.")
    
    async def show_shop_payment_type(self, bot: AsyncTeleBot, call: types.CallbackQuery, payment_type: str):
        """Display items by payment type (medals/TG Stars)"""
        try:
            lang = await helpers.get_lang(call.message.chat.id, call.from_user.id, self.db_manager)
            user_currency = await self.get_user_currency(call.message.chat.id, call.from_user.id)
            
            # Get items by payment type
            items = get_items_by_payment_type(PaymentType(payment_type))
            title = T[lang]['premium_items'] if payment_type == 'tg_stars' else T[lang]['medal_items']
            
            if not items:
                await bot.answer_callback_query(
                    call.id, 
                    T[lang]['no_items_in_category'], 
                    show_alert=True
                )
                return
            
            # Build message
            shop_text = f"🛍️ <b>{title}</b>\n\n"
            if payment_type == 'tg_stars':
                shop_text += f"⭐ {T[lang]['tg_stars']}: <b>{user_currency['tg_stars']}</b>\n"
                shop_text += f"{T[lang]['premium_info']}\n\n"
            else:
                shop_text += f"🏅 {T[lang]['medals']}: <b>{user_currency['medals']}</b>\n\n"
            
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            
            # Add item buttons
            for item_id, item_data in items.items():
                item_name = get_item_display_name(item_id, lang)
                emoji = get_item_emoji(item_id)
                price, _ = await self.get_item_price(item_id)
                
                # Format price
                if payment_type == 'medals':
                    price_text = f"{price} 🏅"
                else:
                    price_text = f"{price} ⭐"
                
                # Check affordability
                can_afford = await self.can_afford_item(call.message.chat.id, call.from_user.id, item_id)
                prefix = "✅" if can_afford else "❌"
                
                button_text = f"{prefix} {emoji} {item_name} - {price_text}"
                keyboard.add(types.InlineKeyboardButton(
                    button_text, 
                    callback_data=f"shop:item:{item_id}"
                ))
            
            # Navigation buttons
            back_btn = types.InlineKeyboardButton(
                f"🔙 {T[lang]['back_to_shop']}", 
                callback_data="shop:main"
            )
            close_btn = types.InlineKeyboardButton(
                f"❌ {T[lang]['close_button']}", 
                callback_data="shop:close"
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
            logger.error(f"Error showing shop payment type {payment_type}: {e}")
            await bot.answer_callback_query(call.id, "❌ Error loading items.")
    
    async def show_item_details(self, bot: AsyncTeleBot, call: types.CallbackQuery, item_id: str):
        """Display detailed item information with purchase option"""
        try:
            lang = await helpers.get_lang(call.message.chat.id, call.from_user.id, self.db_manager)
            user_currency = await self.get_user_currency(call.message.chat.id, call.from_user.id)
            
            if item_id not in ITEMS:
                await bot.answer_callback_query(call.id, T[lang]['item_not_found'], show_alert=True)
                return
            
            item_data = ITEMS[item_id]
            item_name = get_item_display_name(item_id, lang)
            emoji = get_item_emoji(item_id)
            description = get_item_description(item_id, lang)
            stats = get_item_stats(item_id)
            price, payment_type = await self.get_item_price(item_id)
            
            # Build detailed message
            item_text = f"{emoji} <b>{item_name}</b>\n\n"
            item_text += f"📝 <b>{T[lang]['description']}:</b>\n{description}\n\n"
            
            # Add stats
            if stats.get('damage'):
                item_text += f"⚔️ {T[lang]['damage']}: <b>+{stats['damage']}</b>\n"
            if stats.get('duration_seconds'):
                hours = stats['duration_seconds'] // 3600
                item_text += f"⏱️ {T[lang]['duration']}: <b>{hours} {T[lang]['hours']}</b>\n"
            if stats.get('effectiveness'):
                effectiveness = int(stats['effectiveness'] * 100)
                item_text += f"🛡️ {T[lang]['effectiveness']}: <b>{effectiveness}%</b>\n"
            if stats.get('capacity'):
                item_text += f"📦 {T[lang]['capacity']}: <b>+{stats['capacity']}</b>\n"
            if stats.get('medals'):
                item_text += f"🏅 {T[lang]['medal_bonus']}: <b>+{stats['medals']}</b>\n"
            
            # Price and affordability
            item_text += f"\n💰 <b>{T[lang]['price']}:</b> "
            if payment_type == 'medals':
                item_text += f"{price} 🏅 {T[lang]['medals']}\n"
                current_balance = user_currency['medals']
            else:
                item_text += f"{price} ⭐ {T[lang]['tg_stars']}\n"
                current_balance = user_currency['tg_stars']
            
            can_afford = await self.can_afford_item(call.message.chat.id, call.from_user.id, item_id)
            
            if can_afford:
                item_text += f"✅ {T[lang]['you_can_afford']}"
            else:
                needed = price - current_balance
                currency_name = T[lang]['medals'] if payment_type == 'medals' else T[lang]['tg_stars']
                item_text += f"❌ {T[lang]['need_more_currency'].format(amount=needed, currency=currency_name)}"
            
            keyboard = types.InlineKeyboardMarkup()
            
            # Purchase button
            if can_afford:
                buy_btn = types.InlineKeyboardButton(
                    f"💳 {T[lang]['buy_item']}", 
                    callback_data=f"shop:buy:{item_id}"
                )
                keyboard.add(buy_btn)
            
            # Navigation buttons
            back_btn = types.InlineKeyboardButton(
                f"🔙 {T[lang]['back_to_category']}", 
                callback_data="shop:main"
            )
            close_btn = types.InlineKeyboardButton(
                f"❌ {T[lang]['close_button']}", 
                callback_data="shop:close"
            )
            keyboard.add(back_btn, close_btn)
            
            await bot.edit_message_text(
                item_text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            
        except Exception as e:
            logger.error(f"Error showing item details for {item_id}: {e}")
            await bot.answer_callback_query(call.id, "❌ Error loading item details.")
    
    async def handle_item_purchase(self, bot: AsyncTeleBot, call: types.CallbackQuery, item_id: str):
        """Handle the actual item purchase"""
        try:
            lang = await helpers.get_lang(call.message.chat.id, call.from_user.id, self.db_manager)
            
            # Attempt purchase
            success = await self.purchase_item(call.message.chat.id, call.from_user.id, item_id)
            
            if success:
                item_name = get_item_display_name(item_id, lang)
                price, payment_type = await self.get_item_price(item_id)
                currency_name = T[lang]['medals'] if payment_type == 'medals' else T[lang]['tg_stars']
                
                success_msg = T[lang]['purchase_successful'].format(
                    item_name=item_name, 
                    price=price, 
                    currency=currency_name
                )
                await bot.answer_callback_query(call.id, success_msg, show_alert=True)
                
                # Return to shop main
                await self.show_shop_overview(bot, call.message)
            else:
                await bot.answer_callback_query(
                    call.id, 
                    T[lang]['purchase_failed'], 
                    show_alert=True
                )
                
        except Exception as e:
            logger.error(f"Error handling purchase for {item_id}: {e}")
            await bot.answer_callback_query(call.id, T[lang]['purchase_error'], show_alert=True)
    
    async def handle_shop_callback(self, bot: AsyncTeleBot, call: types.CallbackQuery):
        """Handle all shop-related callbacks"""
        try:
            data_parts = call.data.split(':')
            action = data_parts[1] if len(data_parts) > 1 else "main"
            
            if action == "close":
                await bot.delete_message(call.message.chat.id, call.message.message_id)
                await bot.answer_callback_query(call.id)
                return
            
            elif action == "main":
                await self.show_shop_overview(bot, call.message)
            
            elif action == "category":
                category = data_parts[2] if len(data_parts) > 2 else "weapons"
                await self.show_shop_category(bot, call, category)
            
            elif action == "payment":
                payment_type = data_parts[2] if len(data_parts) > 2 else "medals"
                await self.show_shop_payment_type(bot, call, payment_type)
            
            elif action == "item":
                item_id = data_parts[2] if len(data_parts) > 2 else ""
                await self.show_item_details(bot, call, item_id)
            
            elif action == "buy":
                item_id = data_parts[2] if len(data_parts) > 2 else ""
                await self.handle_item_purchase(bot, call, item_id)
            
            elif action == "all":
                await self.show_shop_category(bot, call, "all")
            
            await bot.answer_callback_query(call.id)
            
        except Exception as e:
            logger.error(f"Error handling shop callback: {e}")
            await bot.answer_callback_query(call.id, "❌ Error processing request.")

def register_handlers(bot: AsyncTeleBot, db_manager: DBManager):
    """Register all shop-related handlers"""
    
    # Initialize ShopManager
    shop_manager = ShopManager(db_manager)
    
    @bot.message_handler(commands=['shop', 'store'])
    async def handle_shop_command(message):
        """Handle /shop command with enhanced features"""
        await shop_manager.show_shop_overview(bot, message)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('shop:'))
    async def handle_shop_callbacks(call):
        """Handle all shop-related callbacks"""
        await shop_manager.handle_shop_callback(bot, call)


# Legacy compatibility functions
async def _get_item_price(item_id: str, db_manager: DBManager) -> int:
    """Legacy function for backward compatibility"""
    shop_manager = ShopManager(db_manager)
    price, _ = await shop_manager.get_item_price(item_id)
    return price

async def handle_shop_callback(call: types.CallbackQuery, bot: AsyncTeleBot, db_manager: DBManager):
    """Legacy callback handler for backward compatibility"""
    shop_manager = ShopManager(db_manager)
    await shop_manager.handle_shop_callback(bot, call)

