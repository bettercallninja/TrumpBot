#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Help system module
Provides comprehensive help and documentation for all bot features
"""

import logging
from typing import Dict, List, Optional
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from src.utils.translations import T
from src.utils import helpers
from src.database.db_manager import DBManager
from src.config.items import get_weapon_items, get_item_display_name, get_item_emoji, get_item_stats

# Set up logging
logger = logging.getLogger(__name__)

class HelpManager:
    """Manages help system and documentation"""
    
    def __init__(self, db_manager: DBManager, bot: AsyncTeleBot):
        self.db_manager = db_manager
        self.bot = bot
    
    async def get_user_stats_for_help(self, chat_id: int, user_id: int) -> Dict:
        """Get basic user stats for contextual help"""
        try:
            stats = await self.db_manager.db(
                "SELECT level, score, (SELECT COUNT(*) FROM inventories WHERE chat_id=%s AND user_id=%s AND qty > 0) as items_count FROM players WHERE chat_id=%s AND user_id=%s",
                (chat_id, user_id, chat_id, user_id),
                fetch="one_dict"
            )
            return stats if stats else {"level": 1, "score": 0, "items_count": 0}
        except Exception as e:
            logger.error(f"Error getting user stats for help: {e}")
            return {"level": 1, "score": 0, "items_count": 0}
    
    def get_contextual_help_recommendations(self, user_stats: Dict) -> List[str]:
        """Generate contextual help recommendations based on user progress"""
        recommendations = []
        
        if user_stats["level"] <= 2:
            recommendations.append("ðŸ“š You're new! Check 'Basic Commands' to get started")
        
        if user_stats["score"] < 10:
            recommendations.append("âš”ï¸ Learn about 'Combat System' to earn medals")
        
        if user_stats["items_count"] == 0:
            recommendations.append("ðŸ›’ Visit 'Shop & Items' to get better weapons")
        
        if user_stats["level"] >= 5:
            recommendations.append("ðŸ’° Check 'TG Stars' for premium features")
        
        return recommendations

async def handle_help_callback(call: types.CallbackQuery, bot: AsyncTeleBot, db_manager: DBManager):
    """Process help menu callback queries with enhanced functionality"""
    try:
        lang = await helpers.get_lang(call.message.chat.id, call.from_user.id, db_manager)
        help_manager = HelpManager(db_manager, bot)
        
        # The full callback data is "help:section" or "help:section:subsection"
        data_parts = call.data.split(':')
        help_section = data_parts[1] if len(data_parts) > 1 else "main"
        subsection = data_parts[2] if len(data_parts) > 2 else None
        
        # If the user wants to go back to the main help menu
        if help_section == "main":
            await _edit_to_main_help_menu(call.message, bot, db_manager, lang)
            await bot.answer_callback_query(call.id)
            return
        
        # Handle special sections
        if help_section == "commands":
            await _show_commands_help(call, bot, db_manager, lang)
        elif help_section == "combat":
            await _show_combat_help(call, bot, db_manager, lang, subsection)
        elif help_section == "items":
            await _show_items_help(call, bot, db_manager, lang, subsection)
        elif help_section == "stats":
            await _show_stats_help(call, bot, db_manager, lang)
        elif help_section == "faq":
            await _show_faq_help(call, bot, db_manager, lang)
        else:
            # Fallback to traditional help sections
            await _show_traditional_help(call, bot, db_manager, lang, help_section)
        
        await bot.answer_callback_query(call.id)
        
    except Exception as e:
        logger.error(f"Error handling help callback: {e}")
        await bot.answer_callback_query(call.id, "Error displaying help.")

async def _show_commands_help(call: types.CallbackQuery, bot: AsyncTeleBot, db_manager: DBManager, lang: str):
    """Show comprehensive commands help"""
    if lang == "fa":
        help_text = f"""
ðŸ¤– **{T[lang].get('comprehensive_commands', {})}**

âš”ï¸ **{T[lang].get('combat_commands', {})}:**
â€¢ `/attack [Ú©Ø§Ø±Ø¨Ø±] [ØªØ³Ù„ÛŒØ­Ø§Øª]` - Ø­Ù…Ù„Ù‡ Ø¨Ù‡ Ø¨Ø§Ø²ÛŒÚ©Ù†
â€¢ `/weapons` - Ù…Ù‚Ø§ÛŒØ³Ù‡ Ù‡Ù…Ù‡ ØªØ³Ù„ÛŒØ­Ø§Øª
â€¢ `/battle_stats` - Ù…Ø´Ø§Ù‡Ø¯Ù‡ Ø¢Ù…Ø§Ø± Ù†Ø¨Ø±Ø¯ Ø´Ù…Ø§

ðŸ“Š **{T[lang].get('info_commands', {})}:**
â€¢ `/profile` ÛŒØ§ `/me` - Ù…Ø´Ø§Ù‡Ø¯Ù‡ Ù¾Ø±ÙˆÙØ§ÛŒÙ„ ØªÙØµÛŒÙ„ÛŒ
â€¢ `/leaderboard` ÛŒØ§ `/top` - Ø±ØªØ¨Ù‡â€ŒØ¨Ù†Ø¯ÛŒ Ú†Øª
â€¢ `/stats` - Ù†Ù…Ø§ÛŒ Ú©Ù„ÛŒ Ø¢Ù…Ø§Ø±Ù‡Ø§
â€¢ `/status` - Ø¨Ø±Ø±Ø³ÛŒ ÙˆØ¶Ø¹ÛŒØª ÙØ¹Ù„ÛŒ

ðŸ›’ **{T[lang].get('shop_commands', {})}:**
â€¢ `/shop` - Ù…Ø±ÙˆØ± Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ÛŒ Ù…ÙˆØ¬ÙˆØ¯
â€¢ `/inventory` ÛŒØ§ `/inv` - Ù…Ø´Ø§Ù‡Ø¯Ù‡ Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ÛŒ Ø´Ù…Ø§
â€¢ `/use` - Ø§Ø³ØªÙØ§Ø¯Ù‡ Ø§Ø² Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§

âš™ï¸ **{T[lang].get('utility_commands', {})}:**
â€¢ `/menu` ÛŒØ§ `/main` - Ù…Ù†ÙˆÛŒ Ø§ØµÙ„ÛŒ
â€¢ `/help` - Ø§ÛŒÙ† Ø³ÛŒØ³ØªÙ… Ø±Ø§Ù‡Ù†Ù…Ø§
â€¢ `/language` ÛŒØ§ `/lang` - ØªØºÛŒÛŒØ± Ø²Ø¨Ø§Ù†

â­ **{T[lang].get('premium_commands', {})}:**
â€¢ `/stars` - Ø§Ø·Ù„Ø§Ø¹Ø§Øª Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù…
â€¢ `/premium` - ÙˆÛŒÚ˜Ú¯ÛŒâ€ŒÙ‡Ø§ÛŒ ÙˆÛŒÚ˜Ù‡

ðŸ’¡ **{T[lang].get('tips_section', {})}:**
â€¢ Ø¨Ø±Ø§ÛŒ Ù‡Ø¯Ùâ€ŒÚ¯ÛŒØ±ÛŒ Ø³Ø±ÛŒØ¹ Ø¨Ù‡ Ù¾ÛŒØ§Ù…ÛŒ Ø±ÛŒÙ¾Ù„Ø§ÛŒ Ú©Ø±Ø¯Ù‡ Ùˆ `/attack` Ø¨Ø²Ù†ÛŒØ¯
â€¢ Ø§Ø² Ø¯Ú©Ù…Ù‡â€ŒÙ‡Ø§ÛŒ `/menu` Ø¨Ø±Ø§ÛŒ Ø¯Ø³ØªØ±Ø³ÛŒ Ø³Ø±ÛŒØ¹ Ø§Ø³ØªÙØ§Ø¯Ù‡ Ú©Ù†ÛŒØ¯
â€¢ `/weapons` Ø±Ø§ Ø¨Ø±Ø±Ø³ÛŒ Ú©Ù†ÛŒØ¯ ØªØ§ Ø§Ø³ØªØ±Ø§ØªÚ˜ÛŒ Ø®ÙˆØ¯ Ø±Ø§ Ø¨Ø±Ù†Ø§Ù…Ù‡â€ŒØ±ÛŒØ²ÛŒ Ú©Ù†ÛŒØ¯
â€¢ Ø§Ø² `/bonus` Ø¨Ø±Ø§ÛŒ Ø¯Ø±ÛŒØ§ÙØª Ù¾Ø§Ø¯Ø§Ø´ Ø±ÙˆØ²Ø§Ù†Ù‡ ØºØ§ÙÙ„ Ù†Ø´ÙˆÛŒØ¯
        """
    else:
        help_text = f"""
ðŸ¤– **{T[lang].get('comprehensive_commands', {})}**

âš”ï¸ **{T[lang].get('combat_commands', {})}:**
â€¢ `/attack [user] [weapon]` - Attack a player
â€¢ `/weapons` - Compare all weapons
â€¢ `/battle_stats` - View your combat statistics

ðŸ“Š **{T[lang].get('info_commands', {})}:**
â€¢ `/profile` or `/me` - View detailed profile
â€¢ `/leaderboard` or `/top` - Chat rankings
â€¢ `/stats` - Quick statistics overview
â€¢ `/status` - Check your current status

ðŸ›’ **{T[lang].get('shop_commands', {})}:**
â€¢ `/shop` - Browse available items
â€¢ `/inventory` or `/inv` - View your items
â€¢ `/use` - Use items from inventory

âš™ï¸ **{T[lang].get('utility_commands', {})}:**
â€¢ `/menu` or `/main` - Main menu
â€¢ `/help` - This help system
â€¢ `/language` or `/lang` - Change language

â­ **{T[lang].get('premium_commands', {})}:**
â€¢ `/stars` - TG Stars information
â€¢ `/premium` - Premium features

ðŸ’¡ **{T[lang].get('tips_section', {})}:**
â€¢ Reply to a message with `/attack` for quick targeting
â€¢ Use buttons in `/menu` for fastest access
â€¢ Check `/weapons` to plan your strategy
â€¢ Don't forget `/bonus` for daily medals
        """
    
    keyboard = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton(
        f"ðŸ”™ {T[lang].get('back_to_help', {})}", 
        callback_data='help:main'
    )
    keyboard.add(back_btn)
    
    await bot.edit_message_text(
        help_text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

async def _show_combat_help(call: types.CallbackQuery, bot: AsyncTeleBot, db_manager: DBManager, lang: str, subsection: Optional[str]):
    """Show detailed combat help"""
    if subsection == "weapons":
        # Show weapon-specific help
        weapons = get_weapon_items()
        
        if lang == "fa":
            help_text = f"âš”ï¸ **{T[lang].get('weapons_guide', {})}**\n\n"
        else:
            help_text = f"âš”ï¸ **{T[lang].get('weapons_guide', {})}**\n\n"
        
        for weapon_id, weapon_data in weapons.items():
            stats = get_item_stats(weapon_id)
            emoji = get_item_emoji(weapon_id)
            name = get_item_display_name(weapon_id, lang)
            damage = stats.get('damage', 0)
            
            help_text += f"{emoji} **{name}**: {damage} {T[lang].get('damage', {})}\n"
            if stats.get('description'):
                help_text += f"   â†³ {stats['description']}\n"
            help_text += "\n"
        
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(f"ðŸ”™ {T[lang].get('back_to_combat', {})}", callback_data='help:combat'),
            types.InlineKeyboardButton(f"ðŸ  {T[lang].get('main_help', {})}", callback_data='help:main')
        )
    else:
        # General combat help
        if lang == "fa":
            help_text = f"""
âš”ï¸ **{T[lang].get('combat_system_guide', {})}**

ðŸŽ¯ **{T[lang].get('how_to_attack', {})}:**
1. Ø§Ø² `/attack` Ø¨Ø±Ø§ÛŒ Ø¨Ø§Ø² Ú©Ø±Ø¯Ù† Ø§Ù†ØªØ®Ø§Ø¨ ØªØ³Ù„ÛŒØ­Ø§Øª Ø§Ø³ØªÙØ§Ø¯Ù‡ Ú©Ù†ÛŒØ¯
2. ÛŒØ§ `/attack @Ù†Ø§Ù…_Ú©Ø§Ø±Ø¨Ø±ÛŒ ØªØ³Ù„ÛŒØ­Ø§Øª` Ø¨Ø±Ø§ÛŒ Ø­Ù…Ù„Ù‡ Ù…Ø³ØªÙ‚ÛŒÙ…
3. Ø¨Ù‡ Ù¾ÛŒØ§Ù…ÛŒ Ø±ÛŒÙ¾Ù„Ø§ÛŒ Ú©Ø±Ø¯Ù‡ Ùˆ `/attack` Ø¨Ø±Ø§ÛŒ Ù‡Ø¯Ùâ€ŒÚ¯ÛŒØ±ÛŒ Ø³Ø±ÛŒØ¹

ðŸ’¥ **{T[lang].get('damage_calculation', {})}:**
â€¢ Ø¢Ø³ÛŒØ¨ Ù¾Ø§ÛŒÙ‡ Ø¨Ù‡ ØªØ³Ù„ÛŒØ­Ø§Øª Ø´Ù…Ø§ Ø¨Ø³ØªÚ¯ÛŒ Ø¯Ø§Ø±Ø¯
â€¢ Ø³Ø·Ø­ Ø´Ù…Ø§ Ø¨Ø± Ø®Ø±ÙˆØ¬ÛŒ Ø¢Ø³ÛŒØ¨ ØªØ£Ø«ÛŒØ± Ù…ÛŒâ€ŒÚ¯Ø°Ø§Ø±Ø¯
â€¢ Ø³Ø·Ø­ Ù‡Ø¯Ù Ø¨Ø± Ø¢Ø³ÛŒØ¨ Ø¯Ø±ÛŒØ§ÙØªÛŒ ØªØ£Ø«ÛŒØ± Ù…ÛŒâ€ŒÚ¯Ø°Ø§Ø±Ø¯
â€¢ Ø¨Ø±Ø®ÛŒ ØªØ³Ù„ÛŒØ­Ø§Øª Ø§Ø«Ø±Ø§Øª ÙˆÛŒÚ˜Ù‡ Ø¯Ø§Ø±Ù†Ø¯

ðŸ›¡ï¸ **{T[lang].get('defense_system', {})}:**
â€¢ Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ÛŒ Ø¯ÙØ§Ø¹ÛŒ Ø¢Ø³ÛŒØ¨ ÙˆØ§Ø±Ø¯Ù‡ Ø±Ø§ Ú©Ø§Ù‡Ø´ Ù…ÛŒâ€ŒØ¯Ù‡Ù†Ø¯
â€¢ Ø¯ÙØ§Ø¹ ÙØ¹Ø§Ù„ Ø¯Ø± ÙˆØ¶Ø¹ÛŒØª Ø´Ù…Ø§ Ù†Ø´Ø§Ù† Ø¯Ø§Ø¯Ù‡ Ù…ÛŒâ€ŒØ´ÙˆØ¯
â€¢ Ø§Ø«Ø±Ø¨Ø®Ø´ÛŒ Ø¯ÙØ§Ø¹ Ø¨Ø± Ø­Ø³Ø¨ Ù†ÙˆØ¹ Ø¢ÛŒØªÙ… Ù…ØªÙØ§ÙˆØª Ø§Ø³Øª

ðŸ… **{T[lang].get('rewards_system', {})}:**
â€¢ Ø¨Ø±Ø§ÛŒ Ø­Ù…Ù„Ø§Øª Ù…ÙˆÙÙ‚ Ù…Ø¯Ø§Ù„ Ú©Ø³Ø¨ Ú©Ù†ÛŒØ¯
â€¢ Ù…Ø¯Ø§Ù„â€ŒÙ‡Ø§ÛŒ Ø¬Ø§ÛŒØ²Ù‡ Ø¨Ø±Ø§ÛŒ Ø´Ú©Ø³Øª Ø¯Ø§Ø¯Ù† Ø­Ø±ÛŒÙØ§Ù†
â€¢ ØªØ³Ù„ÛŒØ­Ø§Øª ÙˆÛŒÚ˜Ù‡ Ù¾Ø§Ø¯Ø§Ø´ Ø§Ø¶Ø§ÙÛŒ Ù…ÛŒâ€ŒØ¯Ù‡Ù†Ø¯
â€¢ Ø³Ø·Ø­ Ø¨Ø§Ù„Ø§ Ø¨Ø¨Ø±ÛŒØ¯ ØªØ§ Ø¨Ù‡ Ù…Ø­ØªÙˆØ§ÛŒ Ø¨Ù‡ØªØ±ÛŒ Ø¯Ø³ØªØ±Ø³ÛŒ Ù¾ÛŒØ¯Ø§ Ú©Ù†ÛŒØ¯

â° **{T[lang].get('cooldowns', {})}:**
â€¢ Ø²Ù…Ø§Ù† Ø§Ù†ØªØ¸Ø§Ø± Ø­Ù…Ù„Ù‡ Ø§Ø² Ù‡Ø±Ø²Ù†Ø§Ù…Ù‡ Ø¬Ù„ÙˆÚ¯ÛŒØ±ÛŒ Ù…ÛŒâ€ŒÚ©Ù†Ø¯
â€¢ Ø¨Ø±Ø®ÛŒ ØªØ³Ù„ÛŒØ­Ø§Øª Ø§Ø³ØªÙØ§Ø¯Ù‡ Ù…Ø­Ø¯ÙˆØ¯ Ø¯Ø§Ø±Ù†Ø¯
â€¢ HP Ø¯Ø± Ø·ÙˆÙ„ Ø²Ù…Ø§Ù† Ø¨Ø§Ø²Ø³Ø§Ø²ÛŒ Ù…ÛŒâ€ŒØ´ÙˆØ¯
            """
        else:
            help_text = f"""
âš”ï¸ **{T[lang].get('combat_system_guide', {})}**

ðŸŽ¯ **{T[lang].get('how_to_attack', {})}:**
1. Use `/attack` to open weapon selection
2. Or `/attack @username weapon` for direct attack
3. Reply to a message with `/attack` for quick targeting

ðŸ’¥ **{T[lang].get('damage_calculation', {})}:**
â€¢ Base damage depends on your weapon
â€¢ Your level affects damage output
â€¢ Target's level affects damage received
â€¢ Some weapons have special effects

ðŸ›¡ï¸ **{T[lang].get('defense_system', {})}:**
â€¢ Defense items reduce incoming damage
â€¢ Active defense shows in your status
â€¢ Defense effectiveness varies by item type

ðŸ… **{T[lang].get('rewards_system', {})}:**
â€¢ Earn medals for successful attacks
â€¢ Bonus medals for defeating opponents
â€¢ Premium weapons give extra rewards
â€¢ Level up to access better content

â° **{T[lang].get('cooldowns', {})}:**
â€¢ Attack cooldown prevents spam
â€¢ Some weapons have limited uses
â€¢ HP regenerates over time
            """
        
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            types.InlineKeyboardButton(f"ðŸ”« {T[lang].get('weapons_detail', {})}", callback_data='help:combat:weapons'),
            types.InlineKeyboardButton(f"ðŸ“Š {T[lang].get('stats_detail', {})}", callback_data='help:stats')
        )
        keyboard.add(
            types.InlineKeyboardButton(f"ðŸ”™ {T[lang].get('back_to_help', {})}", callback_data='help:main')
        )
    
    await bot.edit_message_text(
        help_text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

async def _show_items_help(call: types.CallbackQuery, bot: AsyncTeleBot, db_manager: DBManager, lang: str, subsection: Optional[str]):
    """Show items and shop help"""
    help_text = f"""
ðŸ›’ **{T[lang].get('shop_system_guide', {})}**

ðŸ’° **{T[lang].get('currency_types', {})}:**
â€¢ ðŸ… **Medals**: Earn by attacking and winning battles
â€¢ â­ **TG Stars**: Premium currency for special items

ðŸ—‚ï¸ **{T[lang].get('item_categories', {})}:**
â€¢ âš”ï¸ **Weapons**: Deal damage to opponents
â€¢ ðŸ›¡ï¸ **Defense**: Reduce incoming damage
â€¢ ðŸš€ **Boost**: Temporary enhancements
â€¢ ðŸ’Ž **Premium**: Exclusive TG Stars items

ðŸ›ï¸ **{T[lang].get('shopping_guide', {})}:**
1. Use `/shop` to browse items
2. Check item stats before buying
3. Use `/buy [item_name]` to purchase
4. View your items with `/inventory`

ðŸ“¦ **{T[lang].get('inventory_management', {})}:**
â€¢ Items stack when you buy multiples
â€¢ Some items have usage limits
â€¢ Premium items never expire
â€¢ Weapons are consumed when used

ðŸ’¡ **{T[lang].get('shopping_tips', {})}:**
â€¢ Start with basic weapons like missiles
â€¢ Invest in defense items for protection
â€¢ Save TG Stars for premium weapons
â€¢ Check `/weapons` to compare damage
    """
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(f"ðŸ›’ {T[lang].get('open_shop', {})}", callback_data='quick:shop'),
        types.InlineKeyboardButton(f"ðŸ“¦ {T[lang].get('view_inventory', {})}", callback_data='quick:inventory')
    )
    keyboard.add(
        types.InlineKeyboardButton(f"ðŸ”™ {T[lang].get('back_to_help', {})}", callback_data='help:main')
    )
    
    await bot.edit_message_text(
        help_text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

async def _show_stats_help(call: types.CallbackQuery, bot: AsyncTeleBot, db_manager: DBManager, lang: str):
    """Show statistics and progression help"""
    help_text = f"""
ðŸ“Š **{T[lang].get('statistics_guide', {})}**

ðŸ“ˆ **{T[lang].get('player_stats', {})}:**
â€¢ **Level**: Increases with score, affects damage
â€¢ **Score**: Total medals earned from battles
â€¢ **HP**: Health points, reduced by attacks
â€¢ **Rank**: Your position in the chat leaderboard

âš”ï¸ **{T[lang].get('combat_stats', {})}:**
â€¢ **Total Attacks**: Number of attacks you've made
â€¢ **Total Damage**: Cumulative damage dealt
â€¢ **Times Attacked**: How often you've been targeted
â€¢ **Damage Taken**: Total damage received

ðŸ† **{T[lang].get('progression_system', {})}:**
â€¢ Earn medals by attacking other players
â€¢ Level up automatically based on score
â€¢ Higher levels deal more damage
â€¢ Unlock better weapons as you progress

ðŸ“‹ **{T[lang].get('available_stats', {})}:**
â€¢ `/profile` - Detailed personal statistics
â€¢ `/battle_stats` - Combat-focused statistics
â€¢ `/leaderboard` - See top players in chat
â€¢ `/status` - Quick status overview

ðŸŽ¯ **{T[lang].get('improvement_tips', {})}:**
â€¢ Attack regularly to gain experience
â€¢ Buy better weapons to deal more damage
â€¢ Use defense items to protect yourself
â€¢ Study the leaderboard to track progress
    """
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(f"ðŸ‘¤ {T[lang].get('view_profile', {})}", callback_data='quick:stats'),
        types.InlineKeyboardButton(f"ðŸ† {T[lang].get('view_leaderboard', {})}", callback_data='quick:leaderboard')
    )
    keyboard.add(
        types.InlineKeyboardButton(f"ðŸ”™ {T[lang].get('back_to_help', {})}", callback_data='help:main')
    )
    
    await bot.edit_message_text(
        help_text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

async def _show_faq_help(call: types.CallbackQuery, bot: AsyncTeleBot, db_manager: DBManager, lang: str):
    """Show frequently asked questions"""
    if lang == "fa":
        help_text = f"""
â“ **{T[lang].get('faq_title', {})}**

**Ø³: Ú†Ú¯ÙˆÙ†Ù‡ Ø¨Ø§Ø²ÛŒ Ø±Ø§ Ø´Ø±ÙˆØ¹ Ú©Ù†Ù…ØŸ**
Ø¬: Ø§Ø² `/menu` Ø¨Ø±Ø§ÛŒ Ù…Ø´Ø§Ù‡Ø¯Ù‡ Ù‡Ù…Ù‡ Ú¯Ø²ÛŒÙ†Ù‡â€ŒÙ‡Ø§ Ø§Ø³ØªÙØ§Ø¯Ù‡ Ú©Ù†ÛŒØ¯ Ùˆ Ø¨Ø§ `/attack` Ù†Ø¨Ø±Ø¯ Ø±Ø§ Ø¢ØºØ§Ø² Ú©Ù†ÛŒØ¯.

**Ø³: Ú†Ø±Ø§ Ù†Ù…ÛŒâ€ŒØªÙˆØ§Ù†Ù… Ø¨Ù‡ Ú©Ø³ÛŒ Ø­Ù…Ù„Ù‡ Ú©Ù†Ù…ØŸ**
Ø¬: Ø¨Ø±Ø±Ø³ÛŒ Ú©Ù†ÛŒØ¯ Ú©Ù‡ Ø¢ÛŒØ§ ØªØ³Ù„ÛŒØ­Ø§Øª Ø¯Ø§Ø±ÛŒØ¯ØŒ Ø¯Ø± Ø²Ù…Ø§Ù† Ø§Ù†ØªØ¸Ø§Ø± Ù‡Ø³ØªÛŒØ¯ØŒ ÛŒØ§ Ù‡Ø¯Ù Ø¯Ø± Ú†Øª ÙˆØ¬ÙˆØ¯ Ø¯Ø§Ø±Ø¯.

**Ø³: Ú†Ú¯ÙˆÙ†Ù‡ ØªØ³Ù„ÛŒØ­Ø§Øª Ø¨Ù‡ØªØ±ÛŒ Ø¨Ù‡ Ø¯Ø³Øª Ø¢ÙˆØ±Ù…ØŸ**
Ø¬: Ø§Ø² `/shop` Ø¨Ø±Ø§ÛŒ Ø®Ø±ÛŒØ¯ ØªØ³Ù„ÛŒØ­Ø§Øª Ø¨Ø§ Ù…Ø¯Ø§Ù„ Ø¨Ø§Ø²Ø¯ÛŒØ¯ Ú©Ù†ÛŒØ¯ØŒ ÛŒØ§ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù… Ø¨Ø±Ø§ÛŒ Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ÛŒ ÙˆÛŒÚ˜Ù‡ Ú©Ø³Ø¨ Ú©Ù†ÛŒØ¯.

**Ø³: Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù… Ú†ÛŒØ³ØªØŸ**
Ø¬: Ø§Ø±Ø² ÙˆÛŒÚ˜Ù‡â€ŒØ§ÛŒ Ú©Ù‡ Ø§Ø² Ø·Ø±ÛŒÙ‚ ØªÙ„Ú¯Ø±Ø§Ù… Ù‚Ø§Ø¨Ù„ Ú©Ø³Ø¨ ÛŒØ§ Ø®Ø±ÛŒØ¯ Ø¨Ø±Ø§ÛŒ Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ÛŒ Ø§Ù†Ø­ØµØ§Ø±ÛŒ Ø§Ø³Øª.

**Ø³: Ú†Ø±Ø§ Ø­Ù…Ù„Ù‡â€ŒØ§Ù… Ø¢Ø³ÛŒØ¨ Ú©Ù…ØªØ±ÛŒ Ø²Ø¯ØŸ**
Ø¬: Ù‡Ø¯Ù Ù…Ù…Ú©Ù† Ø§Ø³Øª Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ÛŒ Ø¯ÙØ§Ø¹ÛŒ Ø¯Ø§Ø´ØªÙ‡ Ø¨Ø§Ø´Ø¯ØŒ ÛŒØ§ ØªÙØ§ÙˆØª Ø³Ø·Ø­ Ø¨Ø± Ù…Ø­Ø§Ø³Ø¨Ù‡ Ø¢Ø³ÛŒØ¨ ØªØ£Ø«ÛŒØ± Ù…ÛŒâ€ŒÚ¯Ø°Ø§Ø±Ø¯.

**Ø³: Ú†Ú¯ÙˆÙ†Ù‡ HP Ø®ÙˆØ¯ Ø±Ø§ Ø¯Ø±Ù…Ø§Ù† Ú©Ù†Ù…ØŸ**
Ø¬: HP Ø¨Ù‡ Ø·ÙˆØ± Ø®ÙˆØ¯Ú©Ø§Ø± Ø¯Ø± Ø·ÙˆÙ„ Ø²Ù…Ø§Ù† Ø¨Ø§Ø²Ø³Ø§Ø²ÛŒ Ù…ÛŒâ€ŒØ´ÙˆØ¯ØŒ ÛŒØ§ Ù…ÛŒâ€ŒØªÙˆØ§Ù†ÛŒØ¯ Ø§Ø² Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ÛŒ Ø¯Ø±Ù…Ø§Ù†ÛŒ ÙØ±ÙˆØ´Ú¯Ø§Ù‡ Ø§Ø³ØªÙØ§Ø¯Ù‡ Ú©Ù†ÛŒØ¯.

**Ø³: Ø¢ÛŒØ§ Ù…ÛŒâ€ŒØªÙˆØ§Ù†Ù… Ø²Ø¨Ø§Ù† Ø®ÙˆØ¯ Ø±Ø§ ØªØºÛŒÛŒØ± Ø¯Ù‡Ù…ØŸ**
Ø¬: Ø¨Ù„Ù‡! Ø§Ø² `/language` Ø¨Ø±Ø§ÛŒ ØªØºÛŒÛŒØ± Ø¨ÛŒÙ† Ø§Ù†Ú¯Ù„ÛŒØ³ÛŒ Ùˆ ÙØ§Ø±Ø³ÛŒ Ø§Ø³ØªÙØ§Ø¯Ù‡ Ú©Ù†ÛŒØ¯.

**Ø³: Ø³ÛŒØ³ØªÙ… Ø±ØªØ¨Ù‡â€ŒØ¨Ù†Ø¯ÛŒ Ú†Ú¯ÙˆÙ†Ù‡ Ú©Ø§Ø± Ù…ÛŒâ€ŒÚ©Ù†Ø¯ØŸ**
Ø¬: Ø±ØªØ¨Ù‡â€ŒØ¨Ù†Ø¯ÛŒ Ø¨Ø± Ø§Ø³Ø§Ø³ Ø§Ù…ØªÛŒØ§Ø² Ú©Ù„ (Ù…Ø¯Ø§Ù„â€ŒÙ‡Ø§ÛŒ Ú©Ø³Ø¨ Ø´Ø¯Ù‡) Ø§Ø³Øª. Ø§Ø² `/leaderboard` Ø¨Ø±Ø§ÛŒ Ù…Ø´Ø§Ù‡Ø¯Ù‡ Ø±Ø¯Ù‡â€ŒØ¨Ù†Ø¯ÛŒ ÙØ¹Ù„ÛŒ Ø§Ø³ØªÙØ§Ø¯Ù‡ Ú©Ù†ÛŒØ¯.

**Ø³: ÙˆÙ‚ØªÛŒ HP Ù…Ù† Ø¨Ù‡ ØµÙØ± Ù…ÛŒâ€ŒØ±Ø³Ø¯ Ú†Ù‡ Ø§ØªÙØ§Ù‚ÛŒ Ù…ÛŒâ€ŒØ§ÙØªØ¯ØŸ**
Ø¬: Ø´Ù…Ø§ Ø´Ú©Ø³Øª Ù…ÛŒâ€ŒØ®ÙˆØ±ÛŒØ¯ Ø§Ù…Ø§ Ø®ÙˆØ¯Ú©Ø§Ø± 50 HP Ø¨Ø±Ù…ÛŒâ€ŒÚ¯Ø±Ø¯Ø§Ù†ÛŒØ¯. Ù…Ù‡Ø§Ø¬Ù… Ù…Ø¯Ø§Ù„â€ŒÙ‡Ø§ÛŒ Ø¬Ø§ÛŒØ²Ù‡ Ø¯Ø±ÛŒØ§ÙØª Ù…ÛŒâ€ŒÚ©Ù†Ø¯.

**Ø³: Ø¢ÛŒØ§ Ù…Ø­Ø¯ÙˆØ¯ÛŒØªÛŒ Ø¨Ø±Ø§ÛŒ Ø­Ù…Ù„Ø§Øª ÙˆØ¬ÙˆØ¯ Ø¯Ø§Ø±Ø¯ØŸ**
Ø¬: Ø¨Ù„Ù‡ØŒ Ø²Ù…Ø§Ù† Ø§Ù†ØªØ¸Ø§Ø± Ø¨ÛŒÙ† Ø­Ù…Ù„Ø§Øª Ø¨Ø±Ø§ÛŒ Ø¬Ù„ÙˆÚ¯ÛŒØ±ÛŒ Ø§Ø² Ù‡Ø±Ø²Ù†Ø§Ù…Ù‡ ÙˆØ¬ÙˆØ¯ Ø¯Ø§Ø±Ø¯.
        """
    else:
        help_text = f"""
â“ **{T[lang].get('faq_title', {})}**

**Q: How do I start playing?**
A: Use `/menu` to see all available options and start with `/attack` to begin combat.

**Q: Why can't I attack someone?**
A: Check if you have weapons, if you're in cooldown, or if the target exists in the chat.

**Q: How do I get better weapons?**
A: Visit `/shop` to buy weapons with medals, or earn TG Stars for premium items.

**Q: What are TG Stars?**
A: Premium currency that can be earned through Telegram or purchased for exclusive items.

**Q: Why did my attack do less damage?**
A: Target may have defense items, or level differences affect damage calculation.

**Q: How do I heal my HP?**
A: HP regenerates automatically over time, or you can use healing items from the shop.

**Q: Can I change my language?**
A: Yes! Use `/language` to switch between English and Persian.

**Q: How does the ranking system work?**
A: Rankings are based on total score (medals earned). Use `/leaderboard` to see current standings.

**Q: What happens when my HP reaches 0?**
A: You're defeated but automatically get 50 HP back. The attacker gets bonus medals.

**Q: Are there any limits on attacks?**
A: Yes, there's a cooldown period between attacks to prevent spam.

**Q: How do I use items from my inventory?**
A: Use `/use` command or browse your `/inventory` for item usage options.

**Q: What's the difference between weapons and defense items?**
A: Weapons increase attack damage, while defense items reduce incoming damage or provide protection.
        """
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(f"ðŸ†˜ {T[lang].get('contact_support', {})}", url="https://t.me/bettercallninja"),
        types.InlineKeyboardButton(f"ðŸ”™ {T[lang].get('back_to_help', {})}", callback_data='help:main')
    )
    
    await bot.edit_message_text(
        help_text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

async def _show_traditional_help(call: types.CallbackQuery, bot: AsyncTeleBot, db_manager: DBManager, lang: str, help_section: str):
    """Show traditional help sections for backward compatibility"""

async def _show_traditional_help(call: types.CallbackQuery, bot: AsyncTeleBot, db_manager: DBManager, lang: str, help_section: str):
    """Show traditional help sections for backward compatibility"""
    try:
        # Get the appropriate help text for the requested section
        help_text = T[lang].get('help_sections', {}).get(help_section, f"Help section '{help_section}' not found.")
        
        # Create a "Back" button to return to the main help menu
        keyboard = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton(
            T[lang].get('back_button', {}),
            callback_data='help:main'
        )
        keyboard.add(back_btn)
        
        # Update the message with the selected help section's text
        await bot.edit_message_text(
            help_text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Error showing traditional help: {e}")

async def _send_main_help_menu(message: types.Message, bot: AsyncTeleBot, db_manager: DBManager, lang: str):
    """Sends the enhanced main help menu as a new message."""
    try:
        help_manager = HelpManager(db_manager, bot)
        user_stats = await help_manager.get_user_stats_for_help(message.chat.id, message.from_user.id)
        recommendations = help_manager.get_contextual_help_recommendations(user_stats)
        
        # Build contextual intro
        intro_text = f"ðŸ“š **{T[lang].get('help_welcome', {})}**\n\n"
        
        if recommendations:
            intro_text += f"ðŸ’¡ **{T[lang].get('recommendations_for_you', {})}:**\n"
            for rec in recommendations[:2]:  # Show max 2 recommendations
                intro_text += f"â€¢ {rec}\n"
            intro_text += "\n"
        
        intro_text += T[lang].get('help_intro', {})
        
        # Create enhanced keyboard with modern categories
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        
        # First row - Core help
        commands_btn = types.InlineKeyboardButton(
            f"ðŸ¤– {T[lang].get('commands_help', {})}", 
            callback_data='help:commands'
        )
        combat_btn = types.InlineKeyboardButton(
            f"âš”ï¸ {T[lang].get('combat_help', {})}", 
            callback_data='help:combat'
        )
        keyboard.add(commands_btn, combat_btn)
        
        # Second row - Management
        items_btn = types.InlineKeyboardButton(
            f"ðŸ›’ {T[lang].get('items_help', {})}", 
            callback_data='help:items'
        )
        stats_btn = types.InlineKeyboardButton(
            f"ðŸ“Š {T[lang].get('stats_help', {})}", 
            callback_data='help:stats'
        )
        keyboard.add(items_btn, stats_btn)
        
        # Third row - Additional help
        faq_btn = types.InlineKeyboardButton(
            f"â“ {T[lang].get('faq_help', {})}", 
            callback_data='help:faq'
        )
        keyboard.add(faq_btn)
        
        # Fourth row - Quick actions
        menu_btn = types.InlineKeyboardButton(
            f"ðŸ“‹ {T[lang].get('main_menu', {})}", 
            callback_data='quick:menu'
        )
        keyboard.add(menu_btn)
        
        await bot.send_message(
            message.chat.id,
            intro_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error sending help menu: {e}")
        # Fallback to simple help
        await bot.send_message(
            message.chat.id,
            T[lang].get('help_intro', {})
        )

async def _edit_to_main_help_menu(message: types.Message, bot: AsyncTeleBot, db_manager: DBManager, lang: str):
    """Edits an existing message to show the enhanced main help menu."""
    try:
        help_manager = HelpManager(db_manager, bot)
        user_stats = await help_manager.get_user_stats_for_help(message.chat.id, message.from_user.id)
        recommendations = help_manager.get_contextual_help_recommendations(user_stats)
        
        # Build contextual intro
        intro_text = f"ðŸ“š **{T[lang].get('help_welcome', {})}**\n\n"
        
        if recommendations:
            intro_text += f"ðŸ’¡ **{T[lang].get('recommendations_for_you', {})}:**\n"
            for rec in recommendations[:2]:  # Show max 2 recommendations
                intro_text += f"â€¢ {rec}\n"
            intro_text += "\n"
        
        intro_text += T[lang].get('help_intro', {})
        
        # Create enhanced keyboard
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        
        # First row - Core help
        commands_btn = types.InlineKeyboardButton(
            f"ðŸ¤– {T[lang].get('commands_help', {})}", 
            callback_data='help:commands'
        )
        combat_btn = types.InlineKeyboardButton(
            f"âš”ï¸ {T[lang].get('combat_help', {})}", 
            callback_data='help:combat'
        )
        keyboard.add(commands_btn, combat_btn)
        
        # Second row - Management
        items_btn = types.InlineKeyboardButton(
            f"ðŸ›’ {T[lang].get('items_help', {})}", 
            callback_data='help:items'
        )
        stats_btn = types.InlineKeyboardButton(
            f"ðŸ“Š {T[lang].get('stats_help', {})}", 
            callback_data='help:stats'
        )
        keyboard.add(items_btn, stats_btn)
        
        # Third row - Additional help
        faq_btn = types.InlineKeyboardButton(
            f"â“ {T[lang].get('faq_help', {})}", 
            callback_data='help:faq'
        )
        keyboard.add(faq_btn)
        
        await bot.edit_message_text(
            intro_text,
            message.chat.id,
            message.message_id,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error editing to help menu: {e}")

def register_handlers(bot: AsyncTeleBot, db_manager: DBManager):
    """Registers enhanced command handlers for the help module."""

    @bot.message_handler(commands=['help'])
    async def help_command(message: types.Message):
        """Enhanced help command with contextual recommendations"""
        try:
            await helpers.ensure_player(message.chat.id, message.from_user, db_manager)
            lang = await helpers.get_lang(message.chat.id, message.from_user.id, db_manager)
            await _send_main_help_menu(message, bot, db_manager, lang)
        except Exception as e:
            logger.error(f"Error in help command: {e}")
            await bot.send_message(message.chat.id, "Error displaying help.")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('help:'))
    async def help_callback_handler(call: types.CallbackQuery):
        """Enhanced help callback handler"""
        await handle_help_callback(call, bot, db_manager)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('quick:'))
    async def quick_action_handler(call: types.CallbackQuery):
        """Handle quick action callbacks from help system"""
        try:
            lang = await helpers.get_lang(call.message.chat.id, call.from_user.id, db_manager)
            action = call.data.split(':')[1] if ':' in call.data else ""
            
            if action == "shop":
                # Import and use shop manager
                from .shop import ShopManager
                shop_manager = ShopManager(db_manager)
                await shop_manager.show_shop_overview(bot, call.message)
            
            elif action == "inventory":
                # Import and use inventory manager
                from .inventory import InventoryManager
                inventory_manager = InventoryManager(db_manager)
                await inventory_manager.show_inventory_overview(bot, call.message)
            
            elif action == "stats":
                # Import and use general manager for stats
                from .general import GeneralManager
                general_manager = GeneralManager(db_manager)
                await general_manager.show_user_profile(bot, call.message)
            
            elif action == "leaderboard":
                # Import and use general manager for leaderboard
                from .general import GeneralManager
                general_manager = GeneralManager(db_manager)
                await general_manager.show_leaderboard(bot, call.message)
            
            elif action == "menu":
                # Import and use general manager for main menu
                from .general import GeneralManager
                general_manager = GeneralManager(db_manager)
                await general_manager.show_main_menu(bot, call.message)
            
            await bot.answer_callback_query(call.id)
            
        except Exception as e:
            logger.error(f"Error handling quick action {call.data}: {e}")
            await bot.answer_callback_query(call.id, "âŒ Error processing request.")

