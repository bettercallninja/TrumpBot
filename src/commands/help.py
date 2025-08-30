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
            recommendations.append("📚 You're new! Check 'Basic Commands' to get started")
        
        if user_stats["score"] < 10:
            recommendations.append("⚔️ Learn about 'Combat System' to earn medals")
        
        if user_stats["items_count"] == 0:
            recommendations.append("🛒 Visit 'Shop & Items' to get better weapons")
        
        if user_stats["level"] >= 5:
            recommendations.append("💰 Check 'TG Stars' for premium features")
        
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
🤖 **{T.get('comprehensive_commands', {}).get(lang, 'راهنمای کامل دستورات')}**

⚔️ **{T.get('combat_commands', {}).get(lang, 'دستورات نبرد')}:**
• `/attack [کاربر] [تسلیحات]` - حمله به بازیکن
• `/weapons` - مقایسه همه تسلیحات
• `/battle_stats` - مشاهده آمار نبرد شما

📊 **{T.get('info_commands', {}).get(lang, 'دستورات اطلاعاتی')}:**
• `/profile` یا `/me` - مشاهده پروفایل تفصیلی
• `/leaderboard` یا `/top` - رتبه‌بندی چت
• `/stats` - نمای کلی آمارها
• `/status` - بررسی وضعیت فعلی

🛒 **{T.get('shop_commands', {}).get(lang, 'دستورات فروشگاه')}:**
• `/shop` - مرور آیتم‌های موجود
• `/inventory` یا `/inv` - مشاهده آیتم‌های شما
• `/use` - استفاده از آیتم‌ها

⚙️ **{T.get('utility_commands', {}).get(lang, 'دستورات کاربردی')}:**
• `/menu` یا `/main` - منوی اصلی
• `/help` - این سیستم راهنما
• `/language` یا `/lang` - تغییر زبان

⭐ **{T.get('premium_commands', {}).get(lang, 'دستورات ویژه')}:**
• `/stars` - اطلاعات ستاره‌های تلگرام
• `/premium` - ویژگی‌های ویژه

💡 **{T.get('tips_section', {}).get(lang, 'نکات سریع')}:**
• برای هدف‌گیری سریع به پیامی ریپلای کرده و `/attack` بزنید
• از دکمه‌های `/menu` برای دسترسی سریع استفاده کنید
• `/weapons` را بررسی کنید تا استراتژی خود را برنامه‌ریزی کنید
• از `/bonus` برای دریافت پاداش روزانه غافل نشوید
        """
    else:
        help_text = f"""
🤖 **{T.get('comprehensive_commands', {}).get(lang, 'Complete Command Reference')}**

⚔️ **{T.get('combat_commands', {}).get(lang, 'Combat Commands')}:**
• `/attack [user] [weapon]` - Attack a player
• `/weapons` - Compare all weapons
• `/battle_stats` - View your combat statistics

📊 **{T.get('info_commands', {}).get(lang, 'Information Commands')}:**
• `/profile` or `/me` - View detailed profile
• `/leaderboard` or `/top` - Chat rankings
• `/stats` - Quick statistics overview
• `/status` - Check your current status

🛒 **{T.get('shop_commands', {}).get(lang, 'Shop Commands')}:**
• `/shop` - Browse available items
• `/inventory` or `/inv` - View your items
• `/use` - Use items from inventory

⚙️ **{T.get('utility_commands', {}).get(lang, 'Utility Commands')}:**
• `/menu` or `/main` - Main menu
• `/help` - This help system
• `/language` or `/lang` - Change language

⭐ **{T.get('premium_commands', {}).get(lang, 'Premium Commands')}:**
• `/stars` - TG Stars information
• `/premium` - Premium features

💡 **{T.get('tips_section', {}).get(lang, 'Quick Tips')}:**
• Reply to a message with `/attack` for quick targeting
• Use buttons in `/menu` for fastest access
• Check `/weapons` to plan your strategy
• Don't forget `/bonus` for daily medals
        """
    
    keyboard = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton(
        f"🔙 {T.get('back_to_help', {}).get(lang, 'Back to Help Menu')}", 
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
            help_text = f"⚔️ **{T.get('weapons_guide', {}).get(lang, 'راهنمای تسلیحات')}**\n\n"
        else:
            help_text = f"⚔️ **{T.get('weapons_guide', {}).get(lang, 'Weapons Guide')}**\n\n"
        
        for weapon_id, weapon_data in weapons.items():
            stats = get_item_stats(weapon_id)
            emoji = get_item_emoji(weapon_id)
            name = get_item_display_name(weapon_id, lang)
            damage = stats.get('damage', 0)
            
            help_text += f"{emoji} **{name}**: {damage} {T.get('damage', {}).get(lang, 'damage')}\n"
            if stats.get('description'):
                help_text += f"   ↳ {stats['description']}\n"
            help_text += "\n"
        
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(f"🔙 {T.get('back_to_combat', {}).get(lang, 'Back to Combat')}", callback_data='help:combat'),
            types.InlineKeyboardButton(f"🏠 {T.get('main_help', {}).get(lang, 'Main Help')}", callback_data='help:main')
        )
    else:
        # General combat help
        if lang == "fa":
            help_text = f"""
⚔️ **{T.get('combat_system_guide', {}).get(lang, 'راهنمای سیستم نبرد')}**

🎯 **{T.get('how_to_attack', {}).get(lang, 'نحوه حمله کردن')}:**
1. از `/attack` برای باز کردن انتخاب تسلیحات استفاده کنید
2. یا `/attack @نام_کاربری تسلیحات` برای حمله مستقیم
3. به پیامی ریپلای کرده و `/attack` برای هدف‌گیری سریع

💥 **{T.get('damage_calculation', {}).get(lang, 'سیستم آسیب')}:**
• آسیب پایه به تسلیحات شما بستگی دارد
• سطح شما بر خروجی آسیب تأثیر می‌گذارد
• سطح هدف بر آسیب دریافتی تأثیر می‌گذارد
• برخی تسلیحات اثرات ویژه دارند

🛡️ **{T.get('defense_system', {}).get(lang, 'سیستم دفاعی')}:**
• آیتم‌های دفاعی آسیب وارده را کاهش می‌دهند
• دفاع فعال در وضعیت شما نشان داده می‌شود
• اثربخشی دفاع بر حسب نوع آیتم متفاوت است

🏅 **{T.get('rewards_system', {}).get(lang, 'سیستم پاداش')}:**
• برای حملات موفق مدال کسب کنید
• مدال‌های جایزه برای شکست دادن حریفان
• تسلیحات ویژه پاداش اضافی می‌دهند
• سطح بالا ببرید تا به محتوای بهتری دسترسی پیدا کنید

⏰ **{T.get('cooldowns', {}).get(lang, 'محدودیت‌ها و زمان انتظار')}:**
• زمان انتظار حمله از هرزنامه جلوگیری می‌کند
• برخی تسلیحات استفاده محدود دارند
• HP در طول زمان بازسازی می‌شود
            """
        else:
            help_text = f"""
⚔️ **{T.get('combat_system_guide', {}).get(lang, 'Combat System Guide')}**

🎯 **{T.get('how_to_attack', {}).get(lang, 'How to Attack')}:**
1. Use `/attack` to open weapon selection
2. Or `/attack @username weapon` for direct attack
3. Reply to a message with `/attack` for quick targeting

💥 **{T.get('damage_calculation', {}).get(lang, 'Damage System')}:**
• Base damage depends on your weapon
• Your level affects damage output
• Target's level affects damage received
• Some weapons have special effects

🛡️ **{T.get('defense_system', {}).get(lang, 'Defense System')}:**
• Defense items reduce incoming damage
• Active defense shows in your status
• Defense effectiveness varies by item type

🏅 **{T.get('rewards_system', {}).get(lang, 'Reward System')}:**
• Earn medals for successful attacks
• Bonus medals for defeating opponents
• Premium weapons give extra rewards
• Level up to access better content

⏰ **{T.get('cooldowns', {}).get(lang, 'Cooldowns & Limits')}:**
• Attack cooldown prevents spam
• Some weapons have limited uses
• HP regenerates over time
            """
        
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            types.InlineKeyboardButton(f"🔫 {T.get('weapons_detail', {}).get(lang, 'Weapons')}", callback_data='help:combat:weapons'),
            types.InlineKeyboardButton(f"📊 {T.get('stats_detail', {}).get(lang, 'Statistics')}", callback_data='help:stats')
        )
        keyboard.add(
            types.InlineKeyboardButton(f"🔙 {T.get('back_to_help', {}).get(lang, 'Back to Help')}", callback_data='help:main')
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
🛒 **{T.get('shop_system_guide', {}).get(lang, 'Shop & Items System')}**

💰 **{T.get('currency_types', {}).get(lang, 'Currency Types')}:**
• 🏅 **Medals**: Earn by attacking and winning battles
• ⭐ **TG Stars**: Premium currency for special items

🗂️ **{T.get('item_categories', {}).get(lang, 'Item Categories')}:**
• ⚔️ **Weapons**: Deal damage to opponents
• 🛡️ **Defense**: Reduce incoming damage
• 🚀 **Boost**: Temporary enhancements
• 💎 **Premium**: Exclusive TG Stars items

🛍️ **{T.get('shopping_guide', {}).get(lang, 'How to Shop')}:**
1. Use `/shop` to browse items
2. Check item stats before buying
3. Use `/buy [item_name]` to purchase
4. View your items with `/inventory`

📦 **{T.get('inventory_management', {}).get(lang, 'Managing Inventory')}:**
• Items stack when you buy multiples
• Some items have usage limits
• Premium items never expire
• Weapons are consumed when used

💡 **{T.get('shopping_tips', {}).get(lang, 'Shopping Tips')}:**
• Start with basic weapons like missiles
• Invest in defense items for protection
• Save TG Stars for premium weapons
• Check `/weapons` to compare damage
    """
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(f"🛒 {T.get('open_shop', {}).get(lang, 'Open Shop')}", callback_data='quick:shop'),
        types.InlineKeyboardButton(f"📦 {T.get('view_inventory', {}).get(lang, 'View Inventory')}", callback_data='quick:inventory')
    )
    keyboard.add(
        types.InlineKeyboardButton(f"🔙 {T.get('back_to_help', {}).get(lang, 'Back to Help')}", callback_data='help:main')
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
📊 **{T.get('statistics_guide', {}).get(lang, 'Statistics & Progression Guide')}**

📈 **{T.get('player_stats', {}).get(lang, 'Player Statistics')}:**
• **Level**: Increases with score, affects damage
• **Score**: Total medals earned from battles
• **HP**: Health points, reduced by attacks
• **Rank**: Your position in the chat leaderboard

⚔️ **{T.get('combat_stats', {}).get(lang, 'Combat Statistics')}:**
• **Total Attacks**: Number of attacks you've made
• **Total Damage**: Cumulative damage dealt
• **Times Attacked**: How often you've been targeted
• **Damage Taken**: Total damage received

🏆 **{T.get('progression_system', {}).get(lang, 'Progression System')}:**
• Earn medals by attacking other players
• Level up automatically based on score
• Higher levels deal more damage
• Unlock better weapons as you progress

📋 **{T.get('available_stats', {}).get(lang, 'Available Commands')}:**
• `/profile` - Detailed personal statistics
• `/battle_stats` - Combat-focused statistics
• `/leaderboard` - See top players in chat
• `/status` - Quick status overview

🎯 **{T.get('improvement_tips', {}).get(lang, 'Improvement Tips')}:**
• Attack regularly to gain experience
• Buy better weapons to deal more damage
• Use defense items to protect yourself
• Study the leaderboard to track progress
    """
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(f"👤 {T.get('view_profile', {}).get(lang, 'View Profile')}", callback_data='quick:stats'),
        types.InlineKeyboardButton(f"🏆 {T.get('view_leaderboard', {}).get(lang, 'Leaderboard')}", callback_data='quick:leaderboard')
    )
    keyboard.add(
        types.InlineKeyboardButton(f"🔙 {T.get('back_to_help', {}).get(lang, 'Back to Help')}", callback_data='help:main')
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
❓ **{T.get('faq_title', {}).get(lang, 'سوالات متداول')}**

**س: چگونه بازی را شروع کنم؟**
ج: از `/menu` برای مشاهده همه گزینه‌ها استفاده کنید و با `/attack` نبرد را آغاز کنید.

**س: چرا نمی‌توانم به کسی حمله کنم؟**
ج: بررسی کنید که آیا تسلیحات دارید، در زمان انتظار هستید، یا هدف در چت وجود دارد.

**س: چگونه تسلیحات بهتری به دست آورم؟**
ج: از `/shop` برای خرید تسلیحات با مدال بازدید کنید، یا ستاره‌های تلگرام برای آیتم‌های ویژه کسب کنید.

**س: ستاره‌های تلگرام چیست؟**
ج: ارز ویژه‌ای که از طریق تلگرام قابل کسب یا خرید برای آیتم‌های انحصاری است.

**س: چرا حمله‌ام آسیب کمتری زد؟**
ج: هدف ممکن است آیتم‌های دفاعی داشته باشد، یا تفاوت سطح بر محاسبه آسیب تأثیر می‌گذارد.

**س: چگونه HP خود را درمان کنم؟**
ج: HP به طور خودکار در طول زمان بازسازی می‌شود، یا می‌توانید از آیتم‌های درمانی فروشگاه استفاده کنید.

**س: آیا می‌توانم زبان خود را تغییر دهم؟**
ج: بله! از `/language` برای تغییر بین انگلیسی و فارسی استفاده کنید.

**س: سیستم رتبه‌بندی چگونه کار می‌کند؟**
ج: رتبه‌بندی بر اساس امتیاز کل (مدال‌های کسب شده) است. از `/leaderboard` برای مشاهده رده‌بندی فعلی استفاده کنید.

**س: وقتی HP من به صفر می‌رسد چه اتفاقی می‌افتد؟**
ج: شما شکست می‌خورید اما خودکار 50 HP برمی‌گردانید. مهاجم مدال‌های جایزه دریافت می‌کند.

**س: آیا محدودیتی برای حملات وجود دارد؟**
ج: بله، زمان انتظار بین حملات برای جلوگیری از هرزنامه وجود دارد.
        """
    else:
        help_text = f"""
❓ **{T.get('faq_title', {}).get(lang, 'Frequently Asked Questions')}**

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
        types.InlineKeyboardButton(f"🆘 {T.get('contact_support', {}).get(lang, 'More Help')}", url="https://t.me/YourSupportBot"),
        types.InlineKeyboardButton(f"🔙 {T.get('back_to_help', {}).get(lang, 'Back to Help')}", callback_data='help:main')
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
        help_text = T.get('help_sections', {}).get(help_section, {}).get(lang, f"Help section '{help_section}' not found.")
        
        # Create a "Back" button to return to the main help menu
        keyboard = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton(
            T.get('back_button', {}).get(lang, "🔙 Back"),
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
        intro_text = f"📚 **{T.get('help_welcome', {}).get(lang, 'TrumpBot Help Center')}**\n\n"
        
        if recommendations:
            intro_text += f"💡 **{T.get('recommendations_for_you', {}).get(lang, 'Recommendations for you')}:**\n"
            for rec in recommendations[:2]:  # Show max 2 recommendations
                intro_text += f"• {rec}\n"
            intro_text += "\n"
        
        intro_text += T.get('help_intro', {}).get(lang, "Select a category to get detailed help:")
        
        # Create enhanced keyboard with modern categories
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        
        # First row - Core help
        commands_btn = types.InlineKeyboardButton(
            f"🤖 {T.get('commands_help', {}).get(lang, 'Commands')}", 
            callback_data='help:commands'
        )
        combat_btn = types.InlineKeyboardButton(
            f"⚔️ {T.get('combat_help', {}).get(lang, 'Combat')}", 
            callback_data='help:combat'
        )
        keyboard.add(commands_btn, combat_btn)
        
        # Second row - Management
        items_btn = types.InlineKeyboardButton(
            f"🛒 {T.get('items_help', {}).get(lang, 'Shop & Items')}", 
            callback_data='help:items'
        )
        stats_btn = types.InlineKeyboardButton(
            f"📊 {T.get('stats_help', {}).get(lang, 'Statistics')}", 
            callback_data='help:stats'
        )
        keyboard.add(items_btn, stats_btn)
        
        # Third row - Additional help
        faq_btn = types.InlineKeyboardButton(
            f"❓ {T.get('faq_help', {}).get(lang, 'FAQ')}", 
            callback_data='help:faq'
        )
        keyboard.add(faq_btn)
        
        # Fourth row - Quick actions
        menu_btn = types.InlineKeyboardButton(
            f"📋 {T.get('main_menu', {}).get(lang, 'Main Menu')}", 
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
            T.get('help_intro', {}).get(lang, "Help system temporarily unavailable.")
        )

async def _edit_to_main_help_menu(message: types.Message, bot: AsyncTeleBot, db_manager: DBManager, lang: str):
    """Edits an existing message to show the enhanced main help menu."""
    try:
        help_manager = HelpManager(db_manager, bot)
        user_stats = await help_manager.get_user_stats_for_help(message.chat.id, message.from_user.id)
        recommendations = help_manager.get_contextual_help_recommendations(user_stats)
        
        # Build contextual intro
        intro_text = f"📚 **{T.get('help_welcome', {}).get(lang, 'TrumpBot Help Center')}**\n\n"
        
        if recommendations:
            intro_text += f"💡 **{T.get('recommendations_for_you', {}).get(lang, 'Recommendations for you')}:**\n"
            for rec in recommendations[:2]:  # Show max 2 recommendations
                intro_text += f"• {rec}\n"
            intro_text += "\n"
        
        intro_text += T.get('help_intro', {}).get(lang, "Select a category to get detailed help:")
        
        # Create enhanced keyboard
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        
        # First row - Core help
        commands_btn = types.InlineKeyboardButton(
            f"🤖 {T.get('commands_help', {}).get(lang, 'Commands')}", 
            callback_data='help:commands'
        )
        combat_btn = types.InlineKeyboardButton(
            f"⚔️ {T.get('combat_help', {}).get(lang, 'Combat')}", 
            callback_data='help:combat'
        )
        keyboard.add(commands_btn, combat_btn)
        
        # Second row - Management
        items_btn = types.InlineKeyboardButton(
            f"🛒 {T.get('items_help', {}).get(lang, 'Shop & Items')}", 
            callback_data='help:items'
        )
        stats_btn = types.InlineKeyboardButton(
            f"📊 {T.get('stats_help', {}).get(lang, 'Statistics')}", 
            callback_data='help:stats'
        )
        keyboard.add(items_btn, stats_btn)
        
        # Third row - Additional help
        faq_btn = types.InlineKeyboardButton(
            f"❓ {T.get('faq_help', {}).get(lang, 'FAQ')}", 
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
            await bot.answer_callback_query(call.id, "❌ Error processing request.")