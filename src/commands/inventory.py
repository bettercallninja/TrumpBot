#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Inventory commands module
Handles player inventory management, item viewing, usage, and organization
"""

import logging
from typing import Dict, List, Any, Optional
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from src.utils import helpers
from src.utils.translations import T
from src.database.db_manager import DBManager
from src.config.items import (
    ITEMS, get_item_display_name, get_item_emoji, get_item_stats, 
    get_item_description, ItemCategory, is_weapon, is_defense_item,
    is_boost_item, is_premium_item, is_utility_item,
    get_items_by_category
)

# Set up logging
logger = logging.getLogger(__name__)

class InventoryManager:
    """Manages inventory operations and item handling"""
    
    def __init__(self, db_manager: DBManager):
        self.db_manager = db_manager
    
    async def get_user_inventory(self, chat_id: int, user_id: int) -> Dict[str, int]:
        """Get user's inventory items with quantities"""
        try:
            # Improved query with better error handling
            inventory_rows = await self.db_manager.db(
                "SELECT item, qty FROM inventories WHERE chat_id=%s AND user_id=%s AND qty > 0 ORDER BY item",
                (chat_id, user_id), 
                fetch="all_dicts"
            )
            
            # Debug logging to verify data is being returned
            logger.info(f"Retrieved {len(inventory_rows) if inventory_rows else 0} inventory items for user {user_id}")
            
            # Return formatted dictionary or empty dict if no items
            return {row['item']: row['qty'] for row in inventory_rows} if inventory_rows else {}
        except Exception as e:
            logger.error(f"Error getting user inventory: {e}")
            return {}
    
    async def get_inventory_stats(self, chat_id: int, user_id: int) -> Dict[str, Any]:
        """Get inventory statistics and summary"""
        try:
            inventory = await self.get_user_inventory(chat_id, user_id)
            
            stats = {
                "total_items": len(inventory),
                "total_quantity": sum(inventory.values()),
                "categories": {
                    "weapons": 0,
                    "defense": 0,
                    "boost": 0,
                    "premium": 0
                },
                "most_valuable": None,
                "total_value": 0
            }
            
            max_value = 0
            for item_id, qty in inventory.items():
                item_stats = get_item_stats(item_id)
                category = item_stats.get('category', 'other')
                
                if category in stats["categories"]:
                    stats["categories"][category] += qty
                
                # Calculate total value
                if 'price' in item_stats:
                    item_value = item_stats['price'] * qty
                elif 'stars_price' in item_stats:
                    item_value = item_stats['stars_price'] * qty * 100  # TG Stars worth more
                else:
                    stars = item_stats.get('stars', 1)
                    base_price = 50
                    item_value = (base_price * (2 ** (stars - 1))) * qty
                
                stats["total_value"] += item_value
                
                # Track most valuable item
                if item_value > max_value:
                    max_value = item_value
                    stats["most_valuable"] = item_id
            
            return stats
        except Exception as e:
            logger.error(f"Error getting inventory stats: {e}")
            return {"total_items": 0, "total_quantity": 0, "categories": {}, "most_valuable": None, "total_value": 0}
    
    async def use_item(self, chat_id: int, user_id: int, item_id: str) -> bool:
        """Use an item from inventory with comprehensive effects"""
        try:
            # Check if user has the item
            item_row = await self.db_manager.db(
                "SELECT qty FROM inventories WHERE chat_id=%s AND user_id=%s AND item=%s",
                (chat_id, user_id, item_id),
                fetch="one_dict"
            )
            
            if not item_row or item_row['qty'] <= 0:
                logger.warning(f"User {user_id} tried to use item {item_id} but has none")
                return False
            
            # Get item data
            item_stats = get_item_stats(item_id)
            item_type = item_stats.get('type', '')
            
            # Start transaction
            queries = []
            
            # Consume the item (if consumable)
            if item_stats.get('consumable', True):  # Default to consumable unless specified
                queries.append((
                    "UPDATE inventories SET qty = qty - 1 WHERE chat_id=%s AND user_id=%s AND item=%s AND qty > 0",
                    (chat_id, user_id, item_id)
                ))
            
            # Apply item effects based on type
            if item_type == 'shield' or item_type == 'intercept':
                # DEFENSE ITEMS - Activate shield/intercept protection
                
                # Remove any existing defense
                queries.append((
                    "DELETE FROM active_defenses WHERE chat_id=%s AND user_id=%s",
                    (chat_id, user_id)
                ))
                
                # Calculate expiration time based on item duration
                duration = item_stats.get('duration_seconds', 14400)  # Default 4 hours
                expires_at = helpers.now() + duration
                
                # Insert new defense
                queries.append((
                    "INSERT INTO active_defenses (chat_id, user_id, defense_type, expires_at, activated_at) VALUES (%s, %s, %s, %s, %s)",
                    (chat_id, user_id, item_id, expires_at, helpers.now())
                ))
                
            elif item_type == 'boost':
                # BOOST ITEMS - Various temporary effects
                
                if item_id in ['medal_boost_small', 'medal_boost', 'mega_medal_boost']:
                    # Medal boost items - instant medal reward
                    medal_reward = item_stats.get('medals_reward', 250)
                    queries.append((
                        "UPDATE players SET score = score + %s WHERE chat_id=%s AND user_id=%s",
                        (medal_reward, chat_id, user_id)
                    ))
                    
                elif item_id in ['energy_drink', 'adrenaline_shot']:
                    # Cooldown reduction items - add to active boosts table
                    duration = item_stats.get('duration_seconds', 3600)
                    expires_at = helpers.now() + duration
                    
                    # Remove existing cooldown boost
                    queries.append((
                        "DELETE FROM active_boosts WHERE chat_id=%s AND user_id=%s AND boost_type='cooldown_reduction'",
                        (chat_id, user_id)
                    ))
                    
                    # Add new cooldown boost
                    cooldown_reduction = item_stats.get('cooldown_reduction', 0.5)
                    queries.append((
                        """INSERT INTO active_boosts (chat_id, user_id, boost_type, boost_value, expires_at, activated_at) 
                           VALUES (%s, %s, 'cooldown_reduction', %s, %s, %s)
                           ON CONFLICT (chat_id, user_id, boost_type) 
                           DO UPDATE SET boost_value = %s, expires_at = %s, activated_at = %s""",
                        (chat_id, user_id, cooldown_reduction, expires_at, helpers.now(), 
                         cooldown_reduction, expires_at, helpers.now())
                    ))
                    
                elif item_id == 'experience_boost':
                    # Experience multiplier boost
                    duration = item_stats.get('duration_seconds', 14400)  # 4 hours
                    expires_at = helpers.now() + duration
                    multiplier = item_stats.get('experience_multiplier', 2.0)
                    
                    queries.append((
                        """INSERT INTO active_boosts (chat_id, user_id, boost_type, boost_value, expires_at, activated_at) 
                           VALUES (%s, %s, 'experience_multiplier', %s, %s, %s)
                           ON CONFLICT (chat_id, user_id, boost_type) 
                           DO UPDATE SET boost_value = %s, expires_at = %s, activated_at = %s""",
                        (chat_id, user_id, multiplier, expires_at, helpers.now(), 
                         multiplier, expires_at, helpers.now())
                    ))
                    
            elif item_type == 'utility':
                # UTILITY ITEMS - Instant effects
                
                if item_id in ['repair_kit', 'nano_repair']:
                    # HP restoration items
                    hp_restore = item_stats.get('hp_restore', 100)
                    
                    if item_id == 'nano_repair':
                        # Nano repair can overheal beyond max_hp
                        queries.append((
                            "UPDATE players SET hp = LEAST(hp + %s, max_hp + 50) WHERE chat_id=%s AND user_id=%s",
                            (hp_restore, chat_id, user_id)
                        ))
                    else:
                        # Regular repair kit restores to max_hp
                        queries.append((
                            "UPDATE players SET hp = LEAST(hp + %s, max_hp) WHERE chat_id=%s AND user_id=%s",
                            (hp_restore, chat_id, user_id)
                        ))
                        
            elif item_type == 'status':
                # STATUS ITEMS - Long-term effects (VIP, Elite membership)
                
                if item_id in ['vip_status', 'elite_membership']:
                    # VIP/Elite membership activation
                    days = item_stats.get('days', 30)
                    expires_at = helpers.now() + (days * 24 * 60 * 60)  # Convert days to seconds
                    
                    # Remove existing VIP status
                    queries.append((
                        "DELETE FROM active_boosts WHERE chat_id=%s AND user_id=%s AND boost_type IN ('vip_status', 'elite_membership')",
                        (chat_id, user_id)
                    ))
                    
                    # Add VIP/Elite status
                    experience_mult = item_stats.get('experience_multiplier', 1.5)
                    damage_bonus = item_stats.get('damage_bonus', 0.2)
                    
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
                        cooldown_reduction = item_stats.get('cooldown_reduction', 0.25)
                        queries.append((
                            """INSERT INTO active_boosts (chat_id, user_id, boost_type, boost_value, expires_at, activated_at) 
                               VALUES (%s, %s, 'vip_cooldown', %s, %s, %s)""",
                            (chat_id, user_id, cooldown_reduction, expires_at, helpers.now())
                        ))
                        
            elif item_type == 'arsenal':
                # ARSENAL ITEMS - Increase weapon capacity (persistent effect)
                
                if item_id in ['carrier', 'military_base']:
                    capacity_increase = item_stats.get('capacity', 10)
                    
                    # Add to player's arsenal capacity (stored in settings)
                    queries.append((
                        """UPDATE players SET settings = COALESCE(settings, '{}') || jsonb_build_object('arsenal_capacity', 
                           COALESCE((settings->>'arsenal_capacity')::int, 0) + %s) 
                           WHERE chat_id=%s AND user_id=%s""",
                        (capacity_increase, chat_id, user_id)
                    ))
            
            # Execute transaction
            success = await self.db_manager.transaction(queries)
            
            if success:
                logger.info(f"User {user_id} used item {item_id} successfully")
                return True
            else:
                logger.error(f"Transaction failed for user {user_id} using item {item_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error using item {item_id}: {e}")
            return False
    
    async def show_inventory_overview(self, bot: AsyncTeleBot, message: types.Message):
        """Show comprehensive inventory overview"""
        try:
            # Ensure user exists
            await helpers.ensure_player(message.chat.id, message.from_user, self.db_manager)
            
            lang = await helpers.get_lang(message.chat.id, message.from_user.id, self.db_manager)
            inventory = await self.get_user_inventory(message.chat.id, message.from_user.id)
            stats = await self.get_inventory_stats(message.chat.id, message.from_user.id)
            level = await self.db_manager.get_user_level(message.chat.id, message.from_user.id)

            if not inventory:
                # Empty inventory message
                text = f"📦 **{T[lang].get('inventory_empty_title', 'Empty Inventory')}**\n\n"
                text += T[lang].get('inventory_empty_message', "You don't have any items yet.")
                text += f"\n\n💡 {T[lang].get('inventory_tip', 'Visit the shop to buy items')}"
                
                markup = types.InlineKeyboardMarkup()
                shop_btn = types.InlineKeyboardButton(
                    f"🛒 {T[lang].get('open_shop', 'Open Shop')}", 
                    callback_data='shop:main'
                )
                markup.add(shop_btn)
                
                await bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
                return
            
            # Build comprehensive inventory display with safer user_name handling
            user_name = "Player"  # Default fallback
            try:
                if hasattr(message, 'from_user') and message.from_user is not None:
                    # Try different ways to get the name with fallbacks
                    if hasattr(message.from_user, 'first_name') and message.from_user.first_name:
                        user_name = message.from_user.first_name
                    elif hasattr(message.from_user, 'username') and message.from_user.username:
                        user_name = message.from_user.username
            except Exception as name_error:
                logger.warning(f"Could not get user name: {name_error}")

            # Fix inventory title formatting issue - keep consistent Markdown formatting
            text = f"🎒 **{T[lang].get('inventory_title', '{name}\'s Inventory (Level {level})').format(name=user_name, level=level)}**\n\n"

            # Inventory statistics
            text += f"📊 **{T[lang].get('inventory_stats', 'Inventory Stats')}:**\n"
            text += f"• {T[lang].get('total_items', 'Total Items')}: {stats['total_items']}\n"
            text += f"• {T[lang].get('total_quantity', 'Total Quantity')}: {stats['total_quantity']}\n"
            text += f"• {T[lang].get('total_value', 'Total Value')}: {stats['total_value']} 🏅\n"
            
            if stats['most_valuable']:
                valuable_name = get_item_display_name(stats['most_valuable'], lang)
                text += f"• {T[lang].get('most_valuable', 'Most Valuable')}: {valuable_name}\n"
            text += "\n"
            
            # Category breakdown
            text += f"🗂️ **{T[lang].get('categories', 'Categories')}:**\n"
            for category, count in stats['categories'].items():
                if count > 0:
                    category_name = T[lang].get(f'category_{category}', category.capitalize())
                    text += f"• {category_name}: {count}\n"
            text += "\n"
            
            # Create navigation keyboard
            markup = types.InlineKeyboardMarkup(row_width=2)
            
            status_btn = types.InlineKeyboardButton(
                f"🛡️ {T[lang].get('activate_defense', 'Activate Shield')}", 
                callback_data='inventory:status'
            )
            markup.add(status_btn)
            
            # Category buttons
            weapons_btn = types.InlineKeyboardButton(
                f"⚔️ {T[lang].get('category_weapons', 'Weapons')}", 
                callback_data='inventory:category:weapons'
            )
            defense_btn = types.InlineKeyboardButton(
                f"🛡️ {T[lang].get('category_defense', 'Defense')}", 
                callback_data='inventory:category:defense'
            )
            markup.add(weapons_btn, defense_btn)
            
            boost_btn = types.InlineKeyboardButton(
                f"🚀 {T[lang].get('category_boost', 'Boosts')}", 
                callback_data='inventory:category:boost'
            )
            premium_btn = types.InlineKeyboardButton(
                f"💎 {T[lang].get('category_premium', 'Premium')}", 
                callback_data='inventory:category:premium'
            )
            markup.add(boost_btn, premium_btn)
            
            # Functionality buttons
            use_btn = types.InlineKeyboardButton(
                f"🛠️ {T[lang].get('use_items', 'Use Items')}", 
                callback_data='inventory:use'
            )
            
            all_btn = types.InlineKeyboardButton(
                f"📋 {T[lang].get('all_items', 'All Items')}", 
                callback_data='inventory:category:all'
            )
            markup.add(use_btn, all_btn)
            
            # Additional options
            
            close_btn = types.InlineKeyboardButton(
                f"❌ {T[lang].get('close_button', 'Close')}", 
                callback_data='inventory:close'
            )
            markup.add(close_btn)
            
            await bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Error showing inventory overview: {e}")
            await bot.send_message(
                message.chat.id, 
                T[lang].get('inventory_error', "❌ Error displaying inventory.")
            )
    
    async def show_inventory_category(self, bot: AsyncTeleBot, call: types.CallbackQuery, category: str):
        """Show items from specific category"""
        try:
            lang = await helpers.get_lang(call.message.chat.id, call.from_user.id, self.db_manager)
            inventory = await self.get_user_inventory(call.message.chat.id, call.from_user.id)
            
            # Debug logging
            logger.info(f"Showing inventory category {category} for user {call.from_user.id}")
            logger.info(f"User has {len(inventory)} total items")
            
            # Filter items by category
            if category == "all":
                filtered_items = inventory
                category_title = T[lang].get('all_items', 'All Items')
                category_emoji = "📋"
            else:
                filtered_items = {}
                for item_id, qty in inventory.items():
                    if item_id in ITEMS:  # Make sure item exists in the config
                        # Use appropriate function to check item category
                        should_include = False
                        
                        # Debug logging for this specific item
                        logger.info(f"Checking item {item_id}: is_weapon={is_weapon(item_id)}, is_defense_item={is_defense_item(item_id)}, is_boost_item={is_boost_item(item_id)}, is_premium_item={is_premium_item(item_id)}, is_utility_item={is_utility_item(item_id)}")
                        
                        if category == "weapons" and is_weapon(item_id):
                            should_include = True
                        elif category == "defense" and is_defense_item(item_id):
                            should_include = True
                        elif category == "boost" and is_boost_item(item_id):
                            should_include = True
                        elif category == "premium" and is_premium_item(item_id):
                            should_include = True
                        elif category == "utilities" and is_utility_item(item_id):
                            should_include = True
                        
                        logger.info(f"Item {item_id} for category {category}: should_include={should_include}")
                        
                        if should_include:
                            filtered_items[item_id] = qty

                category_title = T[lang].get(f'category_{category}', category.capitalize())
                category_emoji = {"weapons": "⚔️", "defense": "🛡️", "boost": "🚀", "premium": "💎", "utilities": "🔧"}.get(category, "📦")
            
            # Debug logging
            logger.info(f"Filtered to {len(filtered_items)} items for category {category}")
            
            if not filtered_items:
                text = f"{category_emoji} **{category_title}**\n\n"
                text += T[lang].get('category_empty', "You don't have any items in this category.")
            else:
                text = f"{category_emoji} **{category_title}** ({len(filtered_items)} {T[lang].get('items', 'items')})\n\n"
                
                # Sort items by value/rarity
                sorted_items = []
                for item_id, qty in filtered_items.items():
                    if item_id in ITEMS:  # Ensure item exists in config
                        item_stats = get_item_stats(item_id)
                        # Get item value (either price or calculated from stars)
                        if 'price' in item_stats:
                            price = item_stats['price']
                        elif 'stars_price' in item_stats:
                            price = item_stats['stars_price'] * 100  # TG Stars worth more
                        else:
                            stars = item_stats.get('stars', 1)
                            base_price = 50
                            price = base_price * (2 ** (stars - 1))
                        
                        sorted_items.append((item_id, qty, price))
                
                sorted_items.sort(key=lambda x: x[2], reverse=True)  # Sort by price descending
                
                for item_id, qty, price in sorted_items:
                    emoji = get_item_emoji(item_id)
                    name = get_item_display_name(item_id, lang)
                    description = get_item_description(item_id, lang)
                    
                    # Escape markdown characters to prevent parsing errors
                    safe_name = name.replace('*', '\\*').replace('_', '\\_').replace('[', '\\[').replace(']', '\\]')
                    safe_description = description.replace('*', '\\*').replace('_', '\\_').replace('[', '\\[').replace(']', '\\]') if description else ""
                    
                    text += f"{emoji} **{safe_name}** x{qty}\n"
                    if safe_description:
                        text += f"   ↳ {safe_description[:50]}{'...' if len(safe_description) > 50 else ''}\n"
                    
                    # Add item stats for weapons/defense
                    if category == "weapons" or category == "all":
                        if is_weapon(item_id):
                            weapon_stats = get_item_stats(item_id)
                            damage = weapon_stats.get('damage', 0)
                            text += f"   💥 {T[lang].get('damage', 'Damage')}: {damage}\n"
                    
                    if category == "defense" or category == "all":
                        if is_defense_item(item_id):
                            # Add defense effectiveness info
                            defense_stats = get_item_stats(item_id)
                            effectiveness = defense_stats.get('effectiveness', 0.5) * 100
                            text += f"   🛡️ {T[lang].get('protection', 'Protection')}: {effectiveness}%\n"
                    
                    text += "\n"
            
            # Navigation keyboard
            markup = types.InlineKeyboardMarkup(row_width=3)
            
            # Category navigation
            categories = [
                ("weapons", "⚔️", T[lang].get('category_weapons', 'Weapons')),
                ("defense", "🛡️", T[lang].get('category_defense', 'Defense')),
                ("boost", "🚀", T[lang].get('category_boost', 'Boosts')),
                ("premium", "💎", T[lang].get('premium_items', 'Premium Items')),
                ("all", "📋", T[lang].get('all_items', 'All Items'))
            ]
            
            buttons = []
            for cat_id, cat_emoji, cat_name in categories:
                if cat_id != category:  # Don't show current category
                    buttons.append(types.InlineKeyboardButton(
                        f"{cat_emoji} {cat_name}", 
                        callback_data=f'inventory:category:{cat_id}'
                    ))
            
            # Add buttons in rows of 2
            for i in range(0, len(buttons), 2):
                if i + 1 < len(buttons):
                    markup.add(buttons[i], buttons[i+1])
                else:
                    markup.add(buttons[i])
            
            # Back to overview and close
            back_btn = types.InlineKeyboardButton(
                f"🔙 {T[lang].get('back_to_overview', 'Back to Overview')}", 
                callback_data='inventory:overview'
            )
            close_btn = types.InlineKeyboardButton(
                f"❌ {T[lang].get('close_button', 'Close')}", 
                callback_data='inventory:close'
            )
            markup.add(back_btn, close_btn)
            
            await bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error showing inventory category: {e}")
            await bot.answer_callback_query(call.id, "Error displaying category.")
    
    async def show_use_item_menu(self, bot: AsyncTeleBot, call: types.CallbackQuery):
        """Show menu for using items"""
        try:
            lang = await helpers.get_lang(call.message.chat.id, call.from_user.id, self.db_manager)
            inventory = await self.get_user_inventory(call.message.chat.id, call.from_user.id)
            
            # Filter usable items (defense and boost items)
            usable_items = {}
            for item_id, qty in inventory.items():
                item_stats = get_item_stats(item_id)
                category = item_stats.get('category')
                if category in ['defense', 'boost']:
                    usable_items[item_id] = qty
            
            if not usable_items:
                text = f"🛠️ **{T[lang].get('use_items_title', 'Use Items')}**\n\n"
                text += T[lang].get('no_usable_items', "You don't have any usable items.")
                text += f"\n\n💡 {T[lang].get('usable_items_tip', 'Defense and boost items can be used.')}"

                markup = types.InlineKeyboardMarkup()
                back_btn = types.InlineKeyboardButton(
                    f"🔙 {T[lang].get('back', 'Back')}", 
                    callback_data='inventory:overview'
                )
                markup.add(back_btn)
            else:
                text = f"🛠️ **{T[lang].get('use_items_title', 'Use Items')}**\n\n"
                text += T[lang].get('select_item_to_use', "Select an item to use:")
                
                markup = types.InlineKeyboardMarkup(row_width=1)
                
                # Sort by category and price
                sorted_items = []
                for item_id, qty in usable_items.items():
                    item_stats = get_item_stats(item_id)
                    category = item_stats.get('category', 'other')
                    if 'price' in item_stats:
                        price = item_stats['price']
                    elif 'stars_price' in item_stats:
                        price = item_stats['stars_price'] * 100
                    else:
                        stars = item_stats.get('stars', 1)
                        base_price = 50
                        price = base_price * (2 ** (stars - 1))
                        
                    sorted_items.append((item_id, qty, category, price))
                
                sorted_items.sort(key=lambda x: (x[2], -x[3]))  # Sort by category, then price desc
                
                for item_id, qty, category, price in sorted_items:
                    emoji = get_item_emoji(item_id)
                    name = get_item_display_name(item_id, lang)
                    
                    button_text = f"{emoji} {name} (x{qty})"
                    markup.add(types.InlineKeyboardButton(
                        button_text, 
                        callback_data=f'inventory:use_item:{item_id}'
                    ))
                
                # Back button
                back_btn = types.InlineKeyboardButton(
                    f"🔙 {T[lang].get('back', 'Back')}", 
                    callback_data='inventory:overview'
                )
                markup.add(back_btn)
            
            await bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error showing use item menu: {e}")
            await bot.answer_callback_query(call.id, "Error displaying use menu.")
    
    async def handle_item_usage(self, bot: AsyncTeleBot, call: types.CallbackQuery, item_id: str):
        """Handle using a specific item"""
        try:
            lang = await helpers.get_lang(call.message.chat.id, call.from_user.id, self.db_manager)
            
            # Use the item
            success = await self.use_item(call.message.chat.id, call.from_user.id, item_id)
            
            if success:
                item_name = get_item_display_name(item_id, lang)
                emoji = get_item_emoji(item_id)
                
                # Get item effects for the message
                item_stats = get_item_stats(item_id)
                category = item_stats.get('category')
                
                if category == 'defense':
                    message = T[lang].get('defense_activated', "{item} activated! You are now protected.").format(
                        item=f"{emoji} {item_name}"
                    )
                elif category == 'boost':
                    if item_id == 'energy_drink':
                        message = T[lang].get('energy_drink_used', "You used {item} and recovered 25 HP!").format(
                            item=f"{emoji} {item_name}"
                        )
                    else:
                        message = T[lang].get('boost_activated', "{item} activated!").format(
                            item=f"{emoji} {item_name}"
                        )
                else:
                    message = T[lang].get('item_used_success', "You used {item} successfully!").format(
                        item=f"{emoji} {item_name}"
                    )
                
                await bot.answer_callback_query(call.id, message, show_alert=True)
                
                # After using item, show usage confirmation
                usage_text = f"✅ **{T[lang].get('item_used', 'Item Used')}**\n\n"
                usage_text += f"{emoji} **{item_name}** {T[lang].get('has_been_used', 'has been used')}\n\n"
                
                # Add effect description
                if category == 'defense':
                    duration_hours = 24  # Standard defense duration
                    usage_text += f"🛡️ {T[lang].get('defense_active_for', 'Defense active for {hours} hours').format(hours=duration_hours)}\n"
                    effectiveness = item_stats.get('effectiveness', 0.5) * 100
                    usage_text += f"🔰 {T[lang].get('damage_reduction', 'Damage reduction')}: {effectiveness}%\n"
                elif category == 'boost' and item_id == 'energy_drink':
                    usage_text += f"❤️ {T[lang].get('hp_recovered', 'HP recovered')}: +25\n"
                
                # Show what's next options
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                inventory_btn = types.InlineKeyboardButton(
                    f"🎒 {T[lang].get('back_to_inventory', 'Back to Inventory')}", 
                    callback_data='inventory:overview'
                )
                status_btn = types.InlineKeyboardButton(
                    f"📊 {T[lang].get('check_status', 'Check Status')}", 
                    callback_data='quick:stats'
                )
                keyboard.add(inventory_btn, status_btn)
                
                await bot.edit_message_text(
                    usage_text,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
            else:
                await bot.answer_callback_query(
                    call.id, 
                    T[lang].get('item_use_failed', "❌ Failed to use item."),
                    show_alert=True
                )
                
                # Refresh the use item menu
                await self.show_use_item_menu(bot, call)
            
        except Exception as e:
            logger.error(f"Error handling item usage: {e}")
            await bot.answer_callback_query(call.id, "Error using item.")
    
    async def handle_inventory_callback(self, bot: AsyncTeleBot, call: types.CallbackQuery):
        """Enhanced inventory callback handler"""
        try:
            lang = await helpers.get_lang(call.message.chat.id, call.from_user.id, self.db_manager)
            
            data_parts = call.data.split(':')
            action = data_parts[1] if len(data_parts) > 1 else "overview"
            
            # Debug logging
            logger.info(f"Handling inventory callback: {call.data} for user {call.from_user.id}")
            
            if action == 'close':
                await bot.delete_message(call.message.chat.id, call.message.message_id)
                await bot.answer_callback_query(call.id)
                return
                
            elif action == 'overview':
                # Convert callback to fake message for overview
                fake_message = types.Message(
                    message_id=call.message.message_id,
                    from_user=call.from_user,
                    date=call.message.date,
                    chat=call.message.chat,
                    content_type='text',
                    options={},
                    json_string=""
                )
                
                # Delete current message and send new overview
                await bot.delete_message(call.message.chat.id, call.message.message_id)
                await self.show_inventory_overview(bot, fake_message)
                await bot.answer_callback_query(call.id)
                
            elif action == 'category':
                category = data_parts[2] if len(data_parts) > 2 else "all"
                await self.show_inventory_category(bot, call, category)
                await bot.answer_callback_query(call.id)
                
            elif action == 'use':
                await self.show_use_item_menu(bot, call)
                await bot.answer_callback_query(call.id)
                
            elif action == 'status':
                # Show status screen for shield activation
                from src.commands.status import send_status_message
                # Create a fake message to simulate status command
                fake_message = types.Message(
                    message_id=call.message.message_id,
                    from_user=call.from_user,
                    date=call.message.date,
                    chat=call.message.chat,
                    content_type='text',
                    options={},
                    json_string=""
                )
                await bot.delete_message(call.message.chat.id, call.message.message_id)
                await send_status_message(fake_message, bot, self.db_manager, call.from_user, lang)
                await bot.answer_callback_query(call.id, T[lang].get('status_loaded', 'Status screen loaded'))
                
            elif action == 'use_item':
                item_id = data_parts[2] if len(data_parts) > 2 else ""
                if item_id:
                    await self.handle_item_usage(bot, call, item_id)
                else:
                    await bot.answer_callback_query(call.id, "Invalid item.")
            
            else:
                await bot.answer_callback_query(call.id, "Unknown action.")
                
        except Exception as e:
            logger.error(f"Error handling inventory callback: {e}")
            await bot.answer_callback_query(call.id, "Error processing request.")


def register_handlers(bot: AsyncTeleBot, db_manager: DBManager) -> None:
    """Register all inventory-related handlers"""
    
    # Initialize InventoryManager
    inventory_manager = InventoryManager(db_manager)
    
    @bot.message_handler(commands=['inventory', 'inv'])
    async def handle_inventory_command(message):
        """Handle /inventory command with enhanced features"""
        await inventory_manager.show_inventory_overview(bot, message)
    
    @bot.message_handler(commands=['use'])
    async def handle_use_command(message):
        """Handle /use command for item usage"""
        try:
            # First, send a placeholder message
            placeholder = await bot.send_message(message.chat.id, "Loading use menu...")
            
            # Create a properly formatted fake callback query with all required parameters
            fake_callback = types.CallbackQuery(
                id=f"fake_use_{message.from_user.id}",
                from_user=message.from_user,
                chat_instance=str(message.chat.id),
                message=placeholder,
                data="inventory:use",
                json_string="{}"  # Add the missing required json_string parameter
            )
            
            # Show the use menu
            await inventory_manager.show_use_item_menu(bot, fake_callback)
            
        except Exception as e:
            logger.error(f"Error handling use command: {e}")
            await bot.send_message(message.chat.id, "Error showing use menu.")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('inventory:'))
    async def handle_inventory_callbacks(call):
        """Handle all inventory-related callbacks"""
        await inventory_manager.handle_inventory_callback(bot, call)
    
    # Legacy support for direct item usage
    @bot.callback_query_handler(func=lambda call: call.data.startswith('use_item:'))
    async def handle_use_item_callbacks(call):
        """Handle item usage callbacks (legacy support)"""
        item_id = call.data.replace('use_item:', '')
        await inventory_manager.handle_item_usage(bot, call, item_id)

