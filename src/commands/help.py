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
from src.utils import translations
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
            recommendations.append("📚 You're new! Check 'Basic Commands' to get started")

        if user_stats["score"] < 10:
            recommendations.append("⚔️ Learn about 'Combat System' to earn medals")

        if user_stats["items_count"] == 0:
            recommendations.append("🛒 Visit 'Shop & Items' to get better weapons")

        if user_stats["level"] >= 5:
            recommendations.append("⭐ Check 'TG Stars' for premium features")
        
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
🤖 **{T[lang].get('comprehensive_commands', {})}**

⚔️ **{T[lang].get('combat_commands', {})}:**
• `/attack [کاربر] [تسلیحات]` - حمله به بازیکن
• `/weapons` - مقایسه همه تسلیحات
• `/battle_stats` - مشاهده آمار نبرد شما

📊 **{T[lang].get('info_commands', {})}:**
• `/profile` یا `/me` - مشاهده پروفایل تفصیلی
• `/leaderboard` یا `/top` - رتبه‌بندی چت
• `/stats` - نمای کلی آمارها
• `/status` - بررسی وضعیت فعلی

🛒 **{T[lang].get('shop_commands', {})}:**
• `/shop` - مرور آیتم‌های موجود
• `/inventory` یا `/inv` - مشاهده آیتم‌های شما
• `/use` - استفاده از آیتم‌ها

⚙️ **{T[lang].get('utility_commands', {})}:**
• `/menu` یا `/main` - منوی اصلی
• `/help` - این سیستم راهنما
• `/language` یا `/lang` - تغییر زبان

⭐ **{T[lang].get('premium_commands', {})}:**
• `/stars` - اطلاعات ستاره‌های تلگرام
• `/premium` - ویژگی‌های ویژه

💡 **{T[lang].get('tips_section', {})}:**
• برای هدف‌گیری سریع به پیامی ریپلای کرده و `/attack` بزنید
• از دکمه‌های `/menu` برای دسترسی سریع استفاده کنید
• `/weapons` را بررسی کنید تا استراتژی خود را برنامه‌ریزی کنید
• از `/bonus` برای دریافت پاداش روزانه غافل نشوید
        """
    else:
        help_text = f"""
🤖 **{T[lang].get('comprehensive_commands', {})}**

⚔️ **{T[lang].get('combat_commands', {})}:**
• `/attack [user] [weapon]` - Attack a player
• `/weapons` - Compare all weapons
• `/battle_stats` - View your combat statistics

📊 **{T[lang].get('info_commands', {})}:**
• `/profile` or `/me` - View detailed profile
• `/leaderboard` or `/top` - Chat rankings
• `/stats` - Quick statistics overview
• `/status` - Check your current status

🛒 **{T[lang].get('shop_commands', {})}:**
• `/shop` - Browse available items
• `/inventory` or `/inv` - View your items
• `/use` - Use items from inventory

⚙️ **{T[lang].get('utility_commands', {})}:**
• `/menu` or `/main` - Main menu
• `/help` - This help system
• `/language` or `/lang` - Change language

⭐ **{T[lang].get('premium_commands', {})}:**
• `/stars` - TG Stars information
• `/premium` - Premium features

💡 **{T[lang].get('tips_section', {})}:**
• Reply to a message with `/attack` for quick targeting
• Use buttons in `/menu` for fastest access
• Check `/weapons` to plan your strategy
• Don't forget `/bonus` for daily medals
        """
    
    keyboard = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton(
        f"🔙 {translations.get('back_to_help', lang)}",
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
            help_text = f"⚔️ **{T[lang].get('weapons_guide', {})}**\n\n"
        else:
            help_text = f"⚔️ **{T[lang].get('weapons_guide', {})}**\n\n"
        
        for weapon_id, weapon_data in weapons.items():
            stats = get_item_stats(weapon_id)
            emoji = get_item_emoji(weapon_id)
            name = get_item_display_name(weapon_id, lang)
            damage = stats.get('damage', 0)
            
            help_text += f"{emoji} **{name}**: {damage} {T[lang].get('damage', {})}\n"
            if stats.get('description'):
                help_text += f"   ↳ {stats['description']}\n"
            help_text += "\n"
        
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(f"🔙 {T[lang].get('back_to_combat', {})}", callback_data='help:combat'),
            types.InlineKeyboardButton(f"🏠 {T[lang].get('main_help', {})}", callback_data='help:main')
        )
    else:
        # General combat help
        if lang == "fa":
            help_text = f"""
⚔️ **{T[lang].get('combat_system_guide', {})}**

🎯 **{T[lang].get('how_to_attack', {})}:**
1. از `/attack` برای باز کردن انتخاب تسلیحات استفاده کنید
2. یا `/attack @نام_کاربری تسلیحات` برای حمله مستقیم
3. به پیامی ریپلای کرده و `/attack` برای هدف‌گیری سریع

💥 **{T[lang].get('damage_calculation', {})}:**
• آسیب پایه به تسلیحات شما بستگی دارد
• سطح شما بر خروجی آسیب تأثیر می‌گذارد
• سطح هدف بر آسیب دریافتی تأثیر می‌گذارد
• برخی تسلیحات اثرات ویژه دارند

🛡️ **{T[lang].get('defense_system', {})}:**
• آیتم‌های دفاعی آسیب وارده را کاهش می‌دهند
• دفاع فعال در وضعیت شما نشان داده می‌شود
• اثربخشی دفاع بر حسب نوع آیتم متفاوت است

🏅 **{T[lang].get('rewards_system', {})}:**
• برای حملات موفق مدال کسب کنید
• مدال‌های جایزه برای شکست دادن حریفان
• تسلیحات ویژه پاداش اضافی می‌دهند
• سطح بالا ببرید تا به محتوای بهتری دسترسی پیدا کنید

⏰ **{T[lang].get('cooldowns', {})}:**
• زمان انتظار حمله از هرزنامه جلوگیری می‌کند
• برخی تسلیحات استفاده محدود دارند
• HP در طول زمان بازسازی می‌شود
            """
        else:
            help_text = f"""
⚔️ **{T[lang].get('combat_system_guide', {})}**

🎯 **{T[lang].get('how_to_attack', {})}:**
1. Use `/attack` to open weapon selection
2. Or `/attack @username weapon` for direct attack
3. Reply to a message with `/attack` for quick targeting

💥 **{T[lang].get('damage_calculation', {})}:**
• Base damage depends on your weapon
• Your level affects damage output
• Target's level affects damage received
• Some weapons have special effects

🛡️ **{T[lang].get('defense_system', {})}:**
• Defense items reduce incoming damage
• Active defense shows in your status
• Defense effectiveness varies by item type

🏅 **{T[lang].get('rewards_system', {})}:**
• Earn medals for successful attacks
• Bonus medals for defeating opponents
• Premium weapons give extra rewards
• Level up to access better content

⏰ **{T[lang].get('cooldowns', {})}:**
• Attack cooldown prevents spam
• Some weapons have limited uses
• HP regenerates over time
            """
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            types.InlineKeyboardButton(f"⚔️ {T[lang].get('weapons_detail', {})}", callback_data='help:combat:weapons'),
            types.InlineKeyboardButton(f"📊 {T[lang].get('stats_detail', {})}", callback_data='help:stats')
        )
        keyboard.add(
            types.InlineKeyboardButton(f"🔙 {translations.get('back_to_help', lang)}", callback_data='help:main')
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
🛒 **{translations.get('shop_system_guide', lang)}**

💰 **{translations.get('currency_types', lang)}:**
• 🏅 **{translations.get('medals', lang)}**: Earn by attacking and winning battles
• ⭐ **{translations.get('tg_stars', lang)}**: Premium currency for special items

🧭 **{translations.get('item_categories', lang)}:**
• ⚔️ **{translations.get('weapons', lang)}**: Deal damage to opponents
• 🛡️ **{translations.get('defense', lang)}**: Reduce incoming damage
• 🚀 **{translations.get('boosts', lang)}**: Temporary enhancements
• 💎 **Premium**: Exclusive TG Stars items

🛍️ **{translations.get('shopping_guide', lang)}:**
1. Use `/shop` to browse items
2. Check item stats before buying
3. Use `/buy [item_name]` to purchase
4. View your items with `/inventory`

📦 **{translations.get('inventory_management', lang)}:**
• Items stack when you buy multiples
• Some items have usage limits
• Premium items never expire
• Weapons are consumed when used

💡 **{translations.get('shopping_tips', lang)}:**
• Start with basic weapons like missiles
• Invest in defense items for protection
• Save TG Stars for premium weapons
• Check `/weapons` to compare damage
    """
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(f"🛒 {translations.get('open_shop', lang)}", callback_data='quick:shop'),
        types.InlineKeyboardButton(f"📦 {translations.get('view_inventory', lang)}", callback_data='quick:inventory')
    )
    keyboard.add(
        types.InlineKeyboardButton(f"🔙 {translations.get('back_to_help', lang)}", callback_data='help:main')
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
📊 **{T[lang].get('statistics_guide', {})}**

📈 **{T[lang].get('player_stats', {})}:**
• **Level**: Increases with score, affects damage
• **Score**: Total medals earned from battles
• **HP**: Health points, reduced by attacks
• **Rank**: Your position in the chat leaderboard

⚔️ **{T[lang].get('combat_stats', {})}:**
• **Total Attacks**: Number of attacks you've made
• **Total Damage**: Cumulative damage dealt
• **Times Attacked**: How often you've been targeted
• **Damage Taken**: Total damage received

🏆 **{T[lang].get('progression_system', {})}:**
• Earn medals by attacking other players
• Level up automatically based on score
• Higher levels deal more damage
• Unlock better weapons as you progress

📋 **{T[lang].get('available_stats', {})}:**
• `/profile` - Detailed personal statistics
• `/battle_stats` - Combat-focused statistics
• `/leaderboard` - See top players in chat
• `/status` - Quick status overview

🎯 **{T[lang].get('improvement_tips', {})}:**
• Attack regularly to gain experience
• Buy better weapons to deal more damage
• Use defense items to protect yourself
• Study the leaderboard to track progress
    """
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(f"👤 {T[lang].get('view_profile', {})}", callback_data='quick:stats'),
        types.InlineKeyboardButton(f"🏆 {T[lang].get('view_leaderboard', {})}", callback_data='quick:leaderboard')
    )
    keyboard.add(
        types.InlineKeyboardButton(f"🔙 {translations.get('back_to_help', lang)}", callback_data='help:main')
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
    try:
        if lang == "fa":
            help_text = f"""
✓ **{T[lang].get('faq_title', {})}**

• چگونه بازی را شروع کنم؟
با استفاده از `/menu` همه گزینه‌ها را ببینید و با `/attack` نبرد را آغاز کنید.

• چرا نمی‌توانم به کسی حمله کنم؟
بررسی کنید سلاح دارید، در زمان انتظار نیستید، و هدف در چت وجود دارد.

• چگونه سلاح‌های بهتری به دست آورم؟
به `/shop` بروید و با مدال بخرید، یا برای آیتم‌های ویژه TG Stars کسب کنید.

• ستاره‌های تلگرام چیست؟
ارز ویژه‌ای که از طریق تلگرام قابل کسب یا خرید برای آیتم‌های انحصاری است.
            """
        else:
            help_text = f"""
✓ **{T[lang].get('faq_title', {})}**

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
            types.InlineKeyboardButton(f"🆘 {T[lang].get('contact_support', {})}", url="https://t.me/bettercallninja"),
            types.InlineKeyboardButton(f"🔙 {translations.get('back_to_help', lang)}", callback_data='help:main')
        )

        await bot.edit_message_text(
            help_text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error showing FAQ help: {e}")
        await bot.answer_callback_query(call.id, "Error displaying FAQ.")

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
        intro_text = f"📚 **{T[lang].get('help_welcome', {})}**\n\n"

        if recommendations:
            intro_text += f"💡 **{T[lang].get('recommendations_for_you', {})}:**\n"
            for rec in recommendations[:2]:  # Show max 2 recommendations
                intro_text += f"• {rec}\n"
            intro_text += "\n"

        intro_text += T[lang].get('help_intro', {})

        # Create enhanced keyboard with modern categories
        keyboard = types.InlineKeyboardMarkup(row_width=2)

        # First row - Core help
        commands_btn = types.InlineKeyboardButton(
            f"🧠 {T[lang].get('commands_help', {})}",
            callback_data='help:commands'
        )
        combat_btn = types.InlineKeyboardButton(
            f"⚔️ {T[lang].get('combat_help', {})}",
            callback_data='help:combat'
        )
        keyboard.add(commands_btn, combat_btn)

        # Second row - Management
        items_btn = types.InlineKeyboardButton(
            f"🛒 {T[lang].get('items_help', {})}",
            callback_data='help:items'
        )
        stats_btn = types.InlineKeyboardButton(
            f"📊 {T[lang].get('stats_help', {})}",
            callback_data='help:stats'
        )
        keyboard.add(items_btn, stats_btn)

        # Third row - Additional help
        faq_btn = types.InlineKeyboardButton(
            f"✓ {T[lang].get('faq_help', {})}",
            callback_data='help:faq'
        )
        keyboard.add(faq_btn)

        # Fourth row - Quick actions
        menu_btn = types.InlineKeyboardButton(
            f"📋 {T[lang].get('main_menu', {})}",
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
        intro_text = f"📚 **{T[lang].get('help_welcome', {})}**\n\n"

        if recommendations:
            intro_text += f"💡 **{T[lang].get('recommendations_for_you', {})}:**\n"
            for rec in recommendations[:2]:  # Show max 2 recommendations
                intro_text += f"• {rec}\n"
            intro_text += "\n"

        intro_text += T[lang].get('help_intro', {})

        # Create enhanced keyboard
        keyboard = types.InlineKeyboardMarkup(row_width=2)

        # First row - Core help
        commands_btn = types.InlineKeyboardButton(
            f"🧠 {T[lang].get('commands_help', {})}",
            callback_data='help:commands'
        )
        combat_btn = types.InlineKeyboardButton(
            f"⚔️ {T[lang].get('combat_help', {})}",
            callback_data='help:combat'
        )
        keyboard.add(commands_btn, combat_btn)

        # Second row - Management
        items_btn = types.InlineKeyboardButton(
            f"🛒 {T[lang].get('items_help', {})}",
            callback_data='help:items'
        )
        stats_btn = types.InlineKeyboardButton(
            f"📊 {T[lang].get('stats_help', {})}",
            callback_data='help:stats'
        )
        keyboard.add(items_btn, stats_btn)

        # Third row - Additional help
        faq_btn = types.InlineKeyboardButton(
            f"✓ {T[lang].get('faq_help', {})}",
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
                inventory_manager = InventoryManager(db_manager, bot)
                await inventory_manager.show_inventory_overview(bot, call.message)
            
            elif action == "stats":
                # Import and use general manager for stats
                from .general import GeneralManager
                general_manager = GeneralManager(db_manager, bot)
                await general_manager.show_user_profile(bot, call.message)
            
            elif action == "leaderboard":
                # Import and use general manager for leaderboard
                from .general import GeneralManager
                general_manager = GeneralManager(db_manager, bot)
                await general_manager.show_leaderboard(bot, call.message)
            
            elif action == "menu":
                # Import and use general manager for main menu
                from .general import GeneralManager
                general_manager = GeneralManager(db_manager, bot)
                await general_manager.show_main_menu(bot, call.message)
            
            await bot.answer_callback_query(call.id)
            
        except Exception as e:
            logger.error(f"Error handling quick action {call.data}: {e}")
            await bot.answer_callback_query(call.id, "❌ Error processing request.")

