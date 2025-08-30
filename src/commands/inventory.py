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
    get_items_by_category
)

# Set up logging
logger = logging.getLogger(__name__)

class InventoryManager:
    """Manages inventory operations and item handling"""
    
    def __init__(self, db_manager: DBManager, bot: AsyncTeleBot):
        self.db_manager = db_manager
        self.bot = bot
    
    async def get_user_inventory(self, chat_id: int, user_id: int) -> Dict[str, int]:
        """Get user's inventory items with quantities"""
        try:
            inventory_rows = await self.db_manager.db(
                "SELECT item, qty FROM inventories WHERE chat_id=%s AND user_id=%s AND qty > 0 ORDER BY item",
                (chat_id, user_id), 
                fetch="all_dicts"
            )
            return {row['item']: row['qty'] for row in inventory_rows}
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
                item_value = item_stats.get('price', 0) * qty
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
        """Use an item from inventory"""
        try:
            # Check if user has the item
            item_row = await self.db_manager.db(
                "SELECT qty FROM inventories WHERE chat_id=%s AND user_id=%s AND item=%s",
                (chat_id, user_id, item_id),
                fetch="one_dict"
            )
            
            if not item_row or item_row['qty'] <= 0:
                return False
            
            # Consume the item
            await self.db_manager.db(
                "UPDATE inventories SET qty = qty - 1 WHERE chat_id=%s AND user_id=%s AND item=%s",
                (chat_id, user_id, item_id)
            )
            
            # Apply item effects based on type
            item_stats = get_item_stats(item_id)
            category = item_stats.get('category')
            
            if category == 'defense':
                # Activate defense
                await self._activate_defense(chat_id, user_id, item_id)
            elif category == 'boost':
                # Apply boost effects
                await self._apply_boost(chat_id, user_id, item_id)
            
            return True
        except Exception as e:
            logger.error(f"Error using item: {e}")
            return False
    
    async def _activate_defense(self, chat_id: int, user_id: int, defense_item: str):
        """Activate defense item"""
        try:
            # Remove any existing defense
            await self.db_manager.db(
                "DELETE FROM active_defenses WHERE chat_id=%s AND user_id=%s",
                (chat_id, user_id)
            )
            
            # Calculate expiration time (24 hours)
            expires_at = helpers.now() + helpers.timedelta(hours=24)
            
            # Insert new defense
            await self.db_manager.db(
                "INSERT INTO active_defenses (chat_id, user_id, defense_type, expires_at) VALUES (%s, %s, %s, %s)",
                (chat_id, user_id, defense_item, expires_at)
            )
        except Exception as e:
            logger.error(f"Error activating defense: {e}")
    
    async def _apply_boost(self, chat_id: int, user_id: int, boost_item: str):
        """Apply boost item effects"""
        try:
            item_stats = get_item_stats(boost_item)
            
            # Different boosts have different effects
            if boost_item == 'energy_drink':
                # Restore HP
                await self.db_manager.db(
                    "UPDATE players SET hp = LEAST(100, hp + 25) WHERE chat_id=%s AND user_id=%s",
                    (chat_id, user_id)
                )
            elif boost_item == 'medal_multiplier':
                # Set temporary medal multiplier (implement if needed)
                pass
        except Exception as e:
            logger.error(f"Error applying boost: {e}")

async def show_inventory_overview(message: types.Message, bot: AsyncTeleBot, db_manager: DBManager, lang: str) -> None:
    """Show comprehensive inventory overview"""
    try:
        inventory_manager = InventoryManager(db_manager, bot)
        inventory = await inventory_manager.get_user_inventory(message.chat.id, message.from_user.id)
        stats = await inventory_manager.get_inventory_stats(message.chat.id, message.from_user.id)
        
        if not inventory:
            # Empty inventory message
            text = f"📦 **{T.get('inventory_empty_title', {}).get(lang, 'Empty Inventory')}**\n\n"
            text += T.get('inventory_empty_message', {}).get(lang, 
                "Your inventory is empty! Visit the shop to buy weapons and items.")
            text += f"\n\n💡 {T.get('inventory_tip', {}).get(lang, 'Tip: Use /shop to browse available items')}"
            
            markup = types.InlineKeyboardMarkup()
            shop_btn = types.InlineKeyboardButton(
                f"🛒 {T.get('open_shop', {}).get(lang, 'Open Shop')}", 
                callback_data='quick:shop'
            )
            markup.add(shop_btn)
            
            await bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
            return
        
        # Build comprehensive inventory display
        user_name = message.from_user.first_name or "Player"
        text = f"🎒 **{T.get('inventory_title', {}).get(lang, '{name}\'s Inventory').format(name=user_name)}**\n\n"
        
        # Inventory statistics
        text += f"📊 **{T.get('inventory_stats', {}).get(lang, 'Statistics')}:**\n"
        text += f"• {T.get('total_items', {}).get(lang, 'Total Items')}: {stats['total_items']}\n"
        text += f"• {T.get('total_quantity', {}).get(lang, 'Total Quantity')}: {stats['total_quantity']}\n"
        text += f"• {T.get('total_value', {}).get(lang, 'Total Value')}: {stats['total_value']} 🏅\n"
        
        if stats['most_valuable']:
            valuable_name = get_item_display_name(stats['most_valuable'], lang)
            text += f"• {T.get('most_valuable', {}).get(lang, 'Most Valuable')}: {valuable_name}\n"
        text += "\n"
        
        # Category breakdown
        text += f"📂 **{T.get('categories', {}).get(lang, 'Categories')}:**\n"
        for category, count in stats['categories'].items():
            if count > 0:
                category_name = T.get(f'category_{category}', {}).get(lang, category.title())
                text += f"• {category_name}: {count}\n"
        text += "\n"
        
        # Create navigation keyboard
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        # Category buttons
        weapons_btn = types.InlineKeyboardButton(
            f"⚔️ {T.get('weapons', {}).get(lang, 'Weapons')}", 
            callback_data='inventory:category:weapons'
        )
        defense_btn = types.InlineKeyboardButton(
            f"🛡️ {T.get('defense', {}).get(lang, 'Defense')}", 
            callback_data='inventory:category:defense'
        )
        markup.add(weapons_btn, defense_btn)
        
        boost_btn = types.InlineKeyboardButton(
            f"🚀 {T.get('boosts', {}).get(lang, 'Boosts')}", 
            callback_data='inventory:category:boost'
        )
        all_btn = types.InlineKeyboardButton(
            f"📋 {T.get('all_items', {}).get(lang, 'All Items')}", 
            callback_data='inventory:category:all'
        )
        markup.add(boost_btn, all_btn)
        
        # Additional options
        use_btn = types.InlineKeyboardButton(
            f"🔧 {T.get('use_item', {}).get(lang, 'Use Item')}", 
            callback_data='inventory:use'
        )
        close_btn = types.InlineKeyboardButton(
            f"❌ {T.get('close', {}).get(lang, 'Close')}", 
            callback_data='inventory:close'
        )
        markup.add(use_btn, close_btn)
        
        await bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error showing inventory overview: {e}")
        await bot.send_message(
            message.chat.id, 
            T.get('inventory_error', {}).get(lang, "Error displaying inventory.")
        )

async def show_inventory_category(call: types.CallbackQuery, bot: AsyncTeleBot, db_manager: DBManager, 
                                category: str, lang: str) -> None:
    """Show items from specific category"""
    try:
        inventory_manager = InventoryManager(db_manager, bot)
        inventory = await inventory_manager.get_user_inventory(call.message.chat.id, call.from_user.id)
        
        # Filter items by category
        if category == "all":
            filtered_items = inventory
            category_title = T.get('all_items', {}).get(lang, 'All Items')
            category_emoji = "📋"
        else:
            filtered_items = {}
            for item_id, qty in inventory.items():
                item_stats = get_item_stats(item_id)
                if item_stats.get('category') == category:
                    filtered_items[item_id] = qty
            
            category_title = T.get(f'category_{category}', {}).get(lang, category.title())
            category_emoji = {"weapons": "⚔️", "defense": "🛡️", "boost": "🚀"}.get(category, "📦")
        
        if not filtered_items:
            text = f"{category_emoji} **{category_title}**\n\n"
            text += T.get('category_empty', {}).get(lang, "No items in this category.")
        else:
            text = f"{category_emoji} **{category_title}** ({len(filtered_items)} {T.get('items', {}).get(lang, 'items')})\n\n"
            
            # Sort items by value/rarity
            sorted_items = []
            for item_id, qty in filtered_items.items():
                item_stats = get_item_stats(item_id)
                sorted_items.append((item_id, qty, item_stats.get('price', 0)))
            
            sorted_items.sort(key=lambda x: x[2], reverse=True)  # Sort by price descending
            
            for item_id, qty, price in sorted_items:
                emoji = get_item_emoji(item_id)
                name = get_item_display_name(item_id, lang)
                description = get_item_description(item_id, lang)
                
                text += f"{emoji} **{name}** x{qty}\n"
                if description:
                    text += f"   ↳ {description[:50]}{'...' if len(description) > 50 else ''}\n"
                
                # Add item stats for weapons/defense
                if category == "weapons" or category == "all":
                    if is_weapon(item_id):
                        weapon_stats = get_item_stats(item_id)
                        damage = weapon_stats.get('damage', 0)
                        text += f"   💥 {T.get('damage', {}).get(lang, 'Damage')}: {damage}\n"
                
                if category == "defense" or category == "all":
                    if is_defense_item(item_id):
                        # Add defense effectiveness info
                        text += f"   🛡️ {T.get('protection', {}).get(lang, 'Protection')}\n"
                
                text += "\n"
        
        # Navigation keyboard
        markup = types.InlineKeyboardMarkup(row_width=3)
        
        # Category navigation
        categories = [
            ("weapons", "⚔️"), ("defense", "🛡️"), ("boost", "🚀"), ("all", "📋")
        ]
        
        buttons = []
        for cat, emoji in categories:
            if cat != category:  # Don't show current category
                cat_name = T.get(f'category_{cat}', {}).get(lang, cat.title()) if cat != "all" else T.get('all_items', {}).get(lang, 'All')
                buttons.append(types.InlineKeyboardButton(
                    f"{emoji} {cat_name}", 
                    callback_data=f'inventory:category:{cat}'
                ))
        
        # Add buttons in rows of 2
        for i in range(0, len(buttons), 2):
            markup.add(*buttons[i:i+2])
        
        # Back to overview and close
        back_btn = types.InlineKeyboardButton(
            f"🔙 {T.get('back_to_overview', {}).get(lang, 'Overview')}", 
            callback_data='inventory:overview'
        )
        close_btn = types.InlineKeyboardButton(
            f"❌ {T.get('close', {}).get(lang, 'Close')}", 
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

async def show_use_item_menu(call: types.CallbackQuery, bot: AsyncTeleBot, db_manager: DBManager, lang: str) -> None:
    """Show menu for using items"""
    try:
        inventory_manager = InventoryManager(db_manager, bot)
        inventory = await inventory_manager.get_user_inventory(call.message.chat.id, call.from_user.id)
        
        # Filter usable items (defense and boost items)
        usable_items = {}
        for item_id, qty in inventory.items():
            item_stats = get_item_stats(item_id)
            category = item_stats.get('category')
            if category in ['defense', 'boost']:
                usable_items[item_id] = qty
        
        if not usable_items:
            text = f"🔧 **{T.get('use_items_title', {}).get(lang, 'Use Items')}**\n\n"
            text += T.get('no_usable_items', {}).get(lang, "You don't have any usable items.")
            text += f"\n\n💡 {T.get('usable_items_tip', {}).get(lang, 'Tip: Defense and boost items can be used.')}"
            
            markup = types.InlineKeyboardMarkup()
            back_btn = types.InlineKeyboardButton(
                f"🔙 {T.get('back', {}).get(lang, 'Back')}", 
                callback_data='inventory:overview'
            )
            markup.add(back_btn)
        else:
            text = f"🔧 **{T.get('use_items_title', {}).get(lang, 'Use Items')}**\n\n"
            text += T.get('select_item_to_use', {}).get(lang, "Select an item to use:")
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            
            # Sort by category and price
            sorted_items = []
            for item_id, qty in usable_items.items():
                item_stats = get_item_stats(item_id)
                category = item_stats.get('category', 'other')
                price = item_stats.get('price', 0)
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
                f"🔙 {T.get('back', {}).get(lang, 'Back')}", 
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

async def handle_item_usage(call: types.CallbackQuery, bot: AsyncTeleBot, db_manager: DBManager, 
                          item_id: str, lang: str) -> None:
    """Handle using a specific item"""
    try:
        inventory_manager = InventoryManager(db_manager, bot)
        
        # Use the item
        success = await inventory_manager.use_item(call.message.chat.id, call.from_user.id, item_id)
        
        if success:
            item_name = get_item_display_name(item_id, lang)
            emoji = get_item_emoji(item_id)
            
            # Get item effects for the message
            item_stats = get_item_stats(item_id)
            category = item_stats.get('category')
            
            if category == 'defense':
                message = T.get('defense_activated', {}).get(lang, 
                    "🛡️ {item} activated! You are now protected from attacks for 24 hours.").format(item=f"{emoji} {item_name}")
            elif category == 'boost':
                if item_id == 'energy_drink':
                    message = T.get('energy_drink_used', {}).get(lang, 
                        "⚡ {item} consumed! Your HP has been restored.").format(item=f"{emoji} {item_name}")
                else:
                    message = T.get('boost_activated', {}).get(lang, 
                        "🚀 {item} activated! Boost effects applied.").format(item=f"{emoji} {item_name}")
            else:
                message = T.get('item_used_success', {}).get(lang, 
                    "✅ {item} used successfully!").format(item=f"{emoji} {item_name}")
            
            await bot.answer_callback_query(call.id, message, show_alert=True)
            
            # Refresh the inventory display
            await show_use_item_menu(call, bot, db_manager, lang)
        else:
            await bot.answer_callback_query(
                call.id, 
                T.get('item_use_failed', {}).get(lang, "Failed to use item. You may not have this item."),
                show_alert=True
            )
        
    except Exception as e:
        logger.error(f"Error handling item usage: {e}")
        await bot.answer_callback_query(call.id, "Error using item.")

async def handle_inventory_callback(call: types.CallbackQuery, bot: AsyncTeleBot, db_manager: DBManager) -> None:
    """Enhanced inventory callback handler"""
    try:
        lang = await helpers.get_lang(call.message.chat.id, call.from_user.id, db_manager)
        
        data_parts = call.data.split(':')
        action = data_parts[1] if len(data_parts) > 1 else "overview"
        
        if action == 'close':
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            await bot.answer_callback_query(call.id)
            
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
            await show_inventory_overview(fake_message, bot, db_manager, lang)
            await bot.answer_callback_query(call.id)
            
        elif action == 'category':
            category = data_parts[2] if len(data_parts) > 2 else "all"
            await show_inventory_category(call, bot, db_manager, category, lang)
            await bot.answer_callback_query(call.id)
            
        elif action == 'use':
            await show_use_item_menu(call, bot, db_manager, lang)
            await bot.answer_callback_query(call.id)
            
        elif action == 'use_item':
            item_id = data_parts[2] if len(data_parts) > 2 else ""
            if item_id:
                await handle_item_usage(call, bot, db_manager, item_id, lang)
            else:
                await bot.answer_callback_query(call.id, "Invalid item.")
        
        else:
            await bot.answer_callback_query(call.id, "Unknown action.")
            
    except Exception as e:
        logger.error(f"Error handling inventory callback: {e}")
        await bot.answer_callback_query(call.id, "Error processing request.")

def register_handlers(bot: AsyncTeleBot, db_manager: DBManager) -> None:
    """Registers command handlers for the inventory module."""

    @bot.message_handler(commands=['inventory', 'inv'])
    async def inventory_command(message: types.Message):
        """Displays the player's inventory."""
        await helpers.ensure_player(message.chat.id, message.from_user, db_manager)
        lang = await helpers.get_lang(message.chat.id, message.from_user.id, db_manager)

        inventory_rows = await db_manager.db(
            "SELECT item, qty FROM inventories WHERE chat_id=%s AND user_id=%s AND qty > 0 ORDER BY item",
            (message.chat.id, message.from_user.id), fetch="all_dicts"
        )
        
        level_info = await helpers.get_player_level_info(message.chat.id, message.from_user.id, db_manager)

        if not inventory_rows:
            msg = T['inventory_empty'][lang].format(first_name=message.from_user.first_name)
        else:
            inventory_map = {item['item']: item['qty'] for item in inventory_rows}
            
            categories = {'weapons': [], 'defense': [], 'other': []}
            for item_id, qty in inventory_map.items():
                item_details = ITEMS.get(item_id, {})
                category = item_details.get('category', 'other')
                categories[category].append((item_id, qty))

            msg = T['inventory_title'][lang].format(first_name=message.from_user.first_name, level=level_info['level'])
            
            for category, items in categories.items():
                if items:
                    msg += f"\n<b>{T['inventory_categories'][category][lang]}</b>\n"
                    for item_id, qty in sorted(items):
                        item_name = T['items'][item_id][lang]
                        emoji = T['item_emojis'].get(item_id, '📦')
                        msg += f"• {emoji} {item_name}: <b>x{qty}</b>\n"

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(T['close_button'][lang], callback_data="inventory:close"))
        
        await bot.send_message(message.chat.id, msg, reply_markup=keyboard, parse_mode="HTML")


def register_handlers(bot: AsyncTeleBot, db_manager=None):
    """Register all inventory-related handlers"""
    
    # Initialize InventoryManager with provided db_manager or create new one
    if db_manager is None:
        from ..database.db_manager import DBManager
        db_manager = DBManager()
    
    inventory_manager = InventoryManager(db_manager)
    
    @bot.message_handler(commands=['inventory', 'inv'])
    async def handle_inventory_command(message):
        """Handle /inventory command with enhanced features"""
        await inventory_manager.show_inventory_overview(bot, message)
    
    @bot.message_handler(commands=['use'])
    async def handle_use_command(message):
        """Handle /use command for item usage"""
        await inventory_manager.show_use_item_menu(bot, message)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('inventory:'))
    async def handle_inventory_callbacks(call):
        """Handle all inventory-related callbacks"""
        await inventory_manager.handle_inventory_callback(bot, call)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('use_item:'))
    async def handle_use_item_callbacks(call):
        """Handle item usage callbacks"""
        await inventory_manager.handle_item_usage(bot, call)
