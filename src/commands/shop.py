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
            # Get medals from database
            result = await self.db_manager.db(
                "SELECT score, tg_stars FROM players WHERE chat_id=%s AND user_id=%s",
                (chat_id, user_id),
                fetch="one_dict"
            )
            
            if result:
                return {
                    'medals': result.get('score', 0),
                    'tg_stars': result.get('tg_stars', 0)
                }
            return {'medals': 0, 'tg_stars': 0}
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
                # Calculate medal price - prefer medals_price over stars calculation
                if 'medals_price' in item:
                    price = item['medals_price']
                elif 'price' in item:
                    price = item['price']
                else:
                    # Fallback calculation based on stars
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
        """Purchase an item and add to inventory or auto-use if it's a boost"""
        try:
            price, payment_type = await self.get_item_price(item_id)
            
            # Check if user can afford it
            if not await self.can_afford_item(chat_id, user_id, item_id):
                logger.warning(f"User {user_id} cannot afford item {item_id}")
                return False
            
            # Check if the item exists
            if item_id not in ITEMS:
                logger.warning(f"Item {item_id} does not exist")
                return False
            
            item_data = ITEMS[item_id]
            item_type = item_data.get('type', '')
            
            # Check if this is an auto-use item (medal boosts, instant utility items)
            auto_use_items = [
                'medal_boost_small', 'medal_boost', 'mega_medal_boost',  # Medal boost items
                'energy_drink', 'adrenaline_shot',  # Cooldown reduction items  
                'experience_boost',  # Experience multiplier
                'repair_kit', 'nano_repair',  # HP restoration items
                'first_aid', 'field_medic',  # Basic healing items
                'vip_status', 'elite_membership'  # Status items - activate immediately
            ]
            
            # Start transaction
            queries = []
            
            # Deduct currency
            if payment_type == 'medals':
                queries.append((
                    "UPDATE players SET score = score - %s WHERE chat_id=%s AND user_id=%s AND score >= %s",
                    (price, chat_id, user_id, price)
                ))
            else:  # TG Stars
                queries.append((
                    "UPDATE players SET tg_stars = tg_stars - %s WHERE chat_id=%s AND user_id=%s AND tg_stars >= %s",
                    (price, chat_id, user_id, price)
                ))
            
            # Apply immediate effects for auto-use items
            if item_id in auto_use_items:
                # Apply the item's effect immediately without adding to inventory
                
                if item_id in ['medal_boost_small', 'medal_boost', 'mega_medal_boost']:
                    # Medal boost items - instant medal reward
                    medal_reward = item_data.get('medals_reward', 250)
                    queries.append((
                        "UPDATE players SET score = score + %s WHERE chat_id=%s AND user_id=%s",
                        (medal_reward, chat_id, user_id)
                    ))
                    
                elif item_id in ['energy_drink', 'adrenaline_shot']:
                    # Cooldown reduction items - add to active boosts table
                    duration = item_data.get('duration_seconds', 3600)
                    expires_at = helpers.now() + duration
                    cooldown_reduction = item_data.get('cooldown_reduction', 0.5)
                    
                    # Remove existing cooldown boost
                    queries.append((
                        "DELETE FROM active_boosts WHERE chat_id=%s AND user_id=%s AND boost_type='cooldown_reduction'",
                        (chat_id, user_id)
                    ))
                    
                    # Add new cooldown boost
                    queries.append((
                        """INSERT INTO active_boosts (chat_id, user_id, boost_type, boost_value, expires_at, activated_at) 
                           VALUES (%s, %s, 'cooldown_reduction', %s, %s, %s)""",
                        (chat_id, user_id, cooldown_reduction, expires_at, helpers.now())
                    ))
                    
                elif item_id == 'experience_boost':
                    # Experience multiplier boost
                    duration = item_data.get('duration_seconds', 14400)  # 4 hours
                    expires_at = helpers.now() + duration
                    multiplier = item_data.get('experience_multiplier', 2.0)
                    
                    # Remove existing experience boost
                    queries.append((
                        "DELETE FROM active_boosts WHERE chat_id=%s AND user_id=%s AND boost_type='experience_multiplier'",
                        (chat_id, user_id)
                    ))
                    
                    queries.append((
                        """INSERT INTO active_boosts (chat_id, user_id, boost_type, boost_value, expires_at, activated_at) 
                           VALUES (%s, %s, 'experience_multiplier', %s, %s, %s)""",
                        (chat_id, user_id, multiplier, expires_at, helpers.now())
                    ))
                    
                elif item_id in ['repair_kit', 'nano_repair', 'first_aid', 'field_medic']:
                    # HP restoration items
                    hp_restore = item_data.get('hp_restore', 100)
                    
                    if item_id == 'nano_repair':
                        # Nano repair can overheal beyond max_hp
                        queries.append((
                            "UPDATE players SET hp = LEAST(hp + %s, max_hp + 50) WHERE chat_id=%s AND user_id=%s",
                            (hp_restore, chat_id, user_id)
                        ))
                    else:
                        # Regular repair items restore to max_hp
                        queries.append((
                            "UPDATE players SET hp = LEAST(hp + %s, max_hp) WHERE chat_id=%s AND user_id=%s",
                            (hp_restore, chat_id, user_id)
                        ))
                        
                elif item_id in ['vip_status', 'elite_membership']:
                    # VIP/Elite membership activation
                    days = item_data.get('days', 30)
                    expires_at = helpers.now() + (days * 24 * 60 * 60)  # Convert days to seconds
                    
                    # Remove existing VIP status
                    queries.append((
                        "DELETE FROM active_boosts WHERE chat_id=%s AND user_id=%s AND boost_type IN ('vip_experience', 'vip_damage', 'vip_cooldown')",
                        (chat_id, user_id)
                    ))
                    
                    # Add VIP/Elite status
                    experience_mult = item_data.get('experience_multiplier', 1.5)
                    damage_bonus = item_data.get('damage_bonus', 0.2)
                    
                    # Add experience multiplier
                    queries.append((
                        """INSERT INTO active_boosts (chat_id, user_id, boost_type, boost_value, expires_at, activated_at) 
                           VALUES (%s, %s, 'vip_experience', %s, %s, %s)""",
                        (chat_id, user_id, experience_mult, expires_at, helpers.now())
                    ))
                    
                    # Add damage bonus
                    queries.append((
                        """INSERT INTO active_boosts (chat_id, user_id, boost_type, boost_value, expires_at, activated_at) 
                           VALUES (%s, %s, 'vip_damage', %s, %s, %s)""",
                        (chat_id, user_id, damage_bonus, expires_at, helpers.now())
                    ))
                    
                    # Add cooldown reduction if elite
                    if item_id == 'elite_membership':
                        cooldown_reduction = item_data.get('cooldown_reduction', 0.25)
                        queries.append((
                            """INSERT INTO active_boosts (chat_id, user_id, boost_type, boost_value, expires_at, activated_at) 
                               VALUES (%s, %s, 'vip_cooldown', %s, %s, %s)""",
                            (chat_id, user_id, cooldown_reduction, expires_at, helpers.now())
                        ))
            else:
                # For non-auto-use items (weapons, shields, status items), add to inventory
                queries.append((
                    """INSERT INTO inventories (chat_id, user_id, item, qty)
                       VALUES (%s, %s, %s, 1)
                       ON CONFLICT (chat_id, user_id, item) 
                       DO UPDATE SET qty = inventories.qty + 1""",
                    (chat_id, user_id, item_id)
                ))
            
            # Record purchase in purchase history
            current_time = helpers.now()
            queries.append((
                "INSERT INTO purchases (chat_id, user_id, item, price, purchase_time) VALUES (%s, %s, %s, %s, %s)",
                (chat_id, user_id, item_id, price, current_time)
            ))
            
            # Execute transaction
            success = await self.db_manager.transaction(queries)
            
            if success:
                logger.info(f"User {user_id} purchased item {item_id} for {price} {payment_type}")
                return True
            else:
                logger.error(f"Transaction failed for user {user_id} purchasing item {item_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error purchasing item {item_id}: {e}")
            return False
    
    async def show_shop_overview(self, bot: AsyncTeleBot, message: types.Message):
        """Display comprehensive shop overview with categories"""
        try:
            # Ensure user exists
            await helpers.ensure_player(message.chat.id, message.from_user, self.db_manager)
            
            lang = await helpers.get_lang(message.chat.id, message.from_user.id, self.db_manager)
            user_currency = await self.get_user_currency(message.chat.id, message.from_user.id)
            
            # Build shop overview message
            shop_text = f"🛍️ <b>{T[lang].get('shop_welcome', 'Welcome to the Shop!')}</b>\n\n"
            shop_text += f"💰 <b>{T[lang].get('your_balance', 'Your Balance')}:</b>\n"
            shop_text += f"🏅 {T[lang].get('medals', 'Medals')}: <b>{user_currency['medals']}</b>\n"
            shop_text += f"⭐ {T[lang].get('tg_stars', 'TG Stars')}: <b>{user_currency['tg_stars']}</b>\n\n"
            shop_text += f"{T[lang].get('shop_categories_intro', 'Choose a category to browse items:')}"
            
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            
            # Category buttons
            weapons_btn = types.InlineKeyboardButton(
                f"⚔️ {T[lang].get('category_weapons', 'Weapons')}", 
                callback_data="shop:category:weapons"
            )
            defense_btn = types.InlineKeyboardButton(
                f"🛡️ {T[lang].get('category_defense', 'Defense')}", 
                callback_data="shop:category:defense"
            )
            keyboard.add(weapons_btn, defense_btn)
            
            other_btn = types.InlineKeyboardButton(
                f"📦 {T[lang].get('category_utilities', 'Utilities')}", 
                callback_data="shop:category:utilities"
            )
            premium_btn = types.InlineKeyboardButton(
                f"💎 {T[lang].get('premium_items', 'Premium')}", 
                callback_data="shop:payment:tg_stars"
            )
            keyboard.add(other_btn, premium_btn)
            
            # Quick access buttons
            all_items_btn = types.InlineKeyboardButton(
                f"📋 {T[lang].get('all_items', 'All Items')}", 
                callback_data="shop:all"
            )
            close_btn = types.InlineKeyboardButton(
                f"❌ {T[lang].get('close_button', 'Close')}", 
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
                title = T[lang].get('all_items', 'All Items')
            else:
                items = get_items_by_category(category)  # Pass string directly, not enum
                title = T[lang].get(f'category_{category}', category.capitalize())
            
            if not items:
                await bot.answer_callback_query(
                    call.id, 
                    T[lang].get('no_items_in_category', 'No items in this category'), 
                    show_alert=True
                )
                return
            
            # Build category message
            shop_text = f"🛍️ <b>{title}</b>\n\n"
            shop_text += f"💰 {T[lang].get('medals', 'Medals')}: <b>{user_currency['medals']}</b> | "
            shop_text += f"⭐ {T[lang].get('tg_stars', 'TG Stars')}: <b>{user_currency['tg_stars']}</b>\n\n"
            
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
                f"🔙 {T[lang].get('back_to_shop', 'Back to Shop')}", 
                callback_data="shop:main"
            )
            close_btn = types.InlineKeyboardButton(
                f"❌ {T[lang].get('close_button', 'Close')}", 
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
            title = T[lang].get('premium_items', 'Premium Items') if payment_type == 'tg_stars' else T[lang].get('medal_items', 'Medal Items')
            
            if not items:
                await bot.answer_callback_query(
                    call.id, 
                    T[lang].get('no_items_in_category', 'No items in this category'), 
                    show_alert=True
                )
                return
            
            # Build message
            shop_text = f"🛍️ <b>{title}</b>\n\n"
            if payment_type == 'tg_stars':
                shop_text += f"⭐ {T[lang].get('tg_stars', 'TG Stars')}: <b>{user_currency['tg_stars']}</b>\n"
                shop_text += f"{T[lang].get('premium_info', 'Premium items offer unique advantages')}\n\n"
            else:
                shop_text += f"🏅 {T[lang].get('medals', 'Medals')}: <b>{user_currency['medals']}</b>\n\n"
            
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
                f"🔙 {T[lang].get('back_to_shop', 'Back to Shop')}", 
                callback_data="shop:main"
            )
            close_btn = types.InlineKeyboardButton(
                f"❌ {T[lang].get('close_button', 'Close')}", 
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
                await bot.answer_callback_query(call.id, T[lang].get('item_not_found', 'Item not found'), show_alert=True)
                return
            
            item_data = ITEMS[item_id]
            item_name = get_item_display_name(item_id, lang)
            emoji = get_item_emoji(item_id)
            description = get_item_description(item_id, lang)
            stats = get_item_stats(item_id)
            price, payment_type = await self.get_item_price(item_id)
            
            # Build detailed message
            item_text = f"{emoji} <b>{item_name}</b>\n\n"
            item_text += f"📝 <b>{T[lang].get('description', 'Description')}:</b>\n{description}\n\n"
            
            # Add stats
            if stats.get('damage'):
                item_text += f"⚔️ {T[lang].get('damage', 'Damage')}: <b>+{stats['damage']}</b>\n"
            if stats.get('duration_seconds'):
                hours = stats['duration_seconds'] // 3600
                item_text += f"⏱️ {T[lang].get('duration', 'Duration')}: <b>{hours} {T[lang].get('hours', 'hours')}</b>\n"
            if stats.get('effectiveness'):
                effectiveness = int(stats['effectiveness'] * 100)
                item_text += f"🛡️ {T[lang].get('effectiveness', 'Effectiveness')}: <b>{effectiveness}%</b>\n"
            if stats.get('capacity'):
                item_text += f"📦 {T[lang].get('capacity', 'Capacity')}: <b>+{stats['capacity']}</b>\n"
            if stats.get('medals'):
                item_text += f"🏅 {T[lang].get('medal_bonus', 'Medal Bonus')}: <b>+{stats['medals']}</b>\n"
            
            # Price and affordability
            item_text += f"\n💰 <b>{T[lang].get('price', 'Price')}:</b> "
            if payment_type == 'medals':
                item_text += f"{price} 🏅 {T[lang].get('medals', 'Medals')}\n"
                current_balance = user_currency['medals']
            else:
                item_text += f"{price} ⭐ {T[lang].get('tg_stars', 'TG Stars')}\n"
                current_balance = user_currency['tg_stars']
            
            can_afford = await self.can_afford_item(call.message.chat.id, call.from_user.id, item_id)
            
            if can_afford:
                item_text += f"✅ {T[lang].get('you_can_afford', 'You can afford this item')}"
            else:
                needed = price - current_balance
                currency_name = T[lang].get('medals', 'Medals') if payment_type == 'medals' else T[lang].get('tg_stars', 'TG Stars')
                item_text += f"❌ {T[lang].get('need_more_currency', 'You need {amount} more {currency').format(amount=needed, currency=currency_name)}"
            
            keyboard = types.InlineKeyboardMarkup()
            
            # Purchase button
            if can_afford:
                buy_btn = types.InlineKeyboardButton(
                    f"💳 {T[lang].get('buy_item', 'Buy Item')}", 
                    callback_data=f"shop:buy:{item_id}"
                )
                keyboard.add(buy_btn)
            
            # Navigation buttons
            back_btn = types.InlineKeyboardButton(
                f"🔙 {T[lang].get('back_to_category', 'Back')}", 
                callback_data="shop:main"
            )
            close_btn = types.InlineKeyboardButton(
                f"❌ {T[lang].get('close_button', 'Close')}", 
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
                emoji = get_item_emoji(item_id)
                price, payment_type = await self.get_item_price(item_id)
                currency_name = T[lang].get('medals', 'Medals') if payment_type == 'medals' else T[lang].get('tg_stars', 'TG Stars')
                
                # Check if this was an auto-use item
                auto_use_items = [
                    'medal_boost_small', 'medal_boost', 'mega_medal_boost',
                    'energy_drink', 'adrenaline_shot', 'experience_boost',
                    'repair_kit', 'nano_repair', 'first_aid', 'field_medic',
                    'vip_status', 'elite_membership'
                ]
                
                is_auto_use = item_id in auto_use_items
                
                # Create success message with appropriate effect description
                if is_auto_use:
                    if item_id in ['medal_boost_small', 'medal_boost', 'mega_medal_boost']:
                        item_data = ITEMS[item_id]
                        medal_reward = item_data.get('medals_reward', 250)
                        effect_text = f"💰 +{medal_reward} medals added to your balance!"
                    elif item_id in ['energy_drink', 'adrenaline_shot']:
                        item_data = ITEMS[item_id]
                        reduction = int(item_data.get('cooldown_reduction', 0.5) * 100)
                        duration = item_data.get('duration_seconds', 3600) // 3600
                        effect_text = f"⚡ Attack cooldown reduced by {reduction}% for {duration} hour(s)!"
                    elif item_id == 'experience_boost':
                        effect_text = f"📈 Experience gain doubled for 4 hours!"
                    elif item_id in ['repair_kit', 'nano_repair', 'first_aid', 'field_medic']:
                        item_data = ITEMS[item_id]
                        hp_restore = item_data.get('hp_restore', 100)
                        effect_text = f"❤️ +{hp_restore} HP restored!"
                    elif item_id == 'vip_status':
                        effect_text = f"👑 VIP Status activated for 30 days! (+50% XP, +20% damage)"
                    elif item_id == 'elite_membership':
                        effect_text = f"💎 Elite Membership activated for 90 days! (+100% XP, +35% damage, +25% faster cooldowns)"
                    else:
                        effect_text = f"✨ Item effect applied immediately!"
                        
                    success_msg = f"✅ {item_name} purchased and used! {effect_text}"
                else:
                    success_msg = f"✅ {item_name} purchased and added to inventory!"
                
                # Show success popup
                await bot.answer_callback_query(call.id, success_msg, show_alert=True)
                
                # Update message with purchase confirmation
                purchase_text = f"🛍️ <b>{T[lang].get('purchase_complete', 'Purchase Complete')}</b>\n\n"
                purchase_text += f"{emoji} <b>{item_name}</b>\n"
                purchase_text += f"💰 {T[lang].get('price_paid', 'Price Paid')}: {price} "
                purchase_text += f"{'🏅' if payment_type == 'medals' else '⭐'}\n\n"
                
                if is_auto_use:
                    purchase_text += f"⚡ <b>Effect Applied:</b>\n{effect_text}"
                else:
                    purchase_text += f"✅ {T[lang].get('added_to_inventory', 'Added to your inventory!')}"
                
                # Show options after purchase
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                
                shop_btn = types.InlineKeyboardButton(
                    f"🛒 {T[lang].get('continue_shopping', 'Continue Shopping')}", 
                    callback_data="shop:main"
                )
                inventory_btn = types.InlineKeyboardButton(
                    f"🎒 {T[lang].get('view_inventory', 'View Inventory')}", 
                    callback_data="inventory:overview"
                )
                keyboard.add(shop_btn, inventory_btn)
                
                # Show what category the item was from
                category = ITEMS.get(item_id, {}).get('category', 'other')
                category_btn = types.InlineKeyboardButton(
                    f"📂 {T[lang].get(f'category_{category}', category.capitalize())}", 
                    callback_data=f"shop:category:{category}"
                )
                close_btn = types.InlineKeyboardButton(
                    f"❌ {T[lang].get('close_button', 'Close')}", 
                    callback_data="shop:close"
                )
                keyboard.add(category_btn, close_btn)
                
                await bot.edit_message_text(
                    purchase_text,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            else:
                error_msg = T[lang].get('purchase_failed', '❌ Purchase failed. Please try again.')
                await bot.answer_callback_query(call.id, error_msg, show_alert=True)
                
                # Return to item details to try again
                await self.show_item_details(bot, call, item_id)
                
        except Exception as e:
            logger.error(f"Error handling purchase for {item_id}: {e}")
            await bot.answer_callback_query(call.id, T[lang].get('purchase_error', '❌ Error processing purchase'), show_alert=True)
    
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
                # Convert callback to message for overview
                fake_message = types.Message(
                    message_id=call.message.message_id,
                    from_user=call.from_user,
                    date=call.message.date,
                    chat=call.message.chat,
                    content_type='text',
                    options={},
                    json_string=""
                )
                await self.show_shop_overview(bot, fake_message)
            
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

