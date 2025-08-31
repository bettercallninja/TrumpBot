#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
General commands module
Handles basic bot commands like start, help, language selection, and user management
"""

import logging
from typing import Optional, Dict, Any
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from src.config.bot_config import BotConfig
from src.config.items import get_item_display_name, get_item_emoji
from src.utils import helpers
from src.database.db_manager import DBManager
from src.utils.translations import T

# Set up logging
logger = logging.getLogger(__name__)

class GeneralManager:
    """Manages general bot operations and user interactions"""
    
    def __init__(self, db_manager: DBManager, bot: AsyncTeleBot):
        self.db_manager = db_manager
        self.bot = bot
        self.config = BotConfig
    
    async def ensure_user_exists(self, chat_id: int, user: types.User) -> None:
        """Ensure user exists in database with enhanced error handling"""
        try:
            await helpers.ensure_player(chat_id, user, self.db_manager)
        except Exception as e:
            logger.error(f"Error ensuring user exists: {e}")
            raise
    
    async def get_user_language(self, chat_id: int, user_id: int) -> str:
        """Get user's preferred language with fallback"""
        try:
            return await helpers.get_lang(chat_id, user_id, self.db_manager)
        except Exception as e:
            logger.warning(f"Error getting user language: {e}")
            return 'en'  # Default fallback
    
    async def get_user_stats(self, chat_id: int, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user statistics"""
        try:
            player_data = await self.db_manager.db(
                "SELECT level, hp, score, created_at FROM players WHERE chat_id=%s AND user_id=%s",
                (chat_id, user_id),
                fetch="one_dict"
            )
            
            if not player_data:
                return {"level": 1, "hp": 100, "score": 0, "created_at": helpers.now()}
            
            # Get attack statistics
            attack_stats = await self.db_manager.db(
                "SELECT COUNT(*) as attacks, COALESCE(SUM(damage), 0) as total_damage FROM attacks WHERE chat_id=%s AND attacker_id=%s",
                (chat_id, user_id),
                fetch="one_dict"
            )
            
            # Get defense statistics
            defense_stats = await self.db_manager.db(
                "SELECT COUNT(*) as times_attacked FROM attacks WHERE chat_id=%s AND victim_id=%s",
                (chat_id, user_id),
                fetch="one_dict"
            )
            
            return {
                **player_data,
                "attacks": attack_stats.get('attacks', 0),
                "total_damage": attack_stats.get('total_damage', 0),
                "times_attacked": defense_stats.get('times_attacked', 0)
            }
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {"level": 1, "hp": 100, "score": 0, "created_at": helpers.now(), "attacks": 0, "total_damage": 0, "times_attacked": 0}
    
    async def get_leaderboard(self, chat_id: int, limit: int = 10) -> list:
        """Get chat leaderboard"""
        try:
            return await self.db_manager.db(
                "SELECT user_id, username, first_name, score, level FROM players WHERE chat_id=%s ORDER BY score DESC LIMIT %s",
                (chat_id, limit),
                fetch="all_dicts"
            )
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
    
    async def get_chat_statistics(self, chat_id: int) -> Dict[str, Any]:
        """Get comprehensive chat statistics"""
        try:
            # Total players
            total_players = await self.db_manager.db(
                "SELECT COUNT(*) as count FROM players WHERE chat_id=%s",
                (chat_id,),
                fetch="one_dict"
            )
            
            # Total attacks
            total_attacks = await self.db_manager.db(
                "SELECT COUNT(*) as count FROM attacks WHERE chat_id=%s",
                (chat_id,),
                fetch="one_dict"
            )
            
            # Most active attacker
            top_attacker = await self.db_manager.db(
                "SELECT attacker_id, COUNT(*) as attacks FROM attacks WHERE chat_id=%s GROUP BY attacker_id ORDER BY attacks DESC LIMIT 1",
                (chat_id,),
                fetch="one_dict"
            )
            
            # Average level
            avg_level = await self.db_manager.db(
                "SELECT AVG(level) as avg_level FROM players WHERE chat_id=%s",
                (chat_id,),
                fetch="one_dict"
            )
            
            return {
                "total_players": total_players.get('count', 0),
                "total_attacks": total_attacks.get('count', 0),
                "top_attacker_id": top_attacker.get('attacker_id') if top_attacker else None,
                "top_attacker_attacks": top_attacker.get('attacks', 0) if top_attacker else 0,
                "average_level": round(avg_level.get('avg_level', 1), 1) if avg_level else 1
            }
        except Exception as e:
            logger.error(f"Error getting chat statistics: {e}")
            return {"total_players": 0, "total_attacks": 0, "top_attacker_id": None, "top_attacker_attacks": 0, "average_level": 1}

async def show_main_menu(message: types.Message, bot: AsyncTeleBot, db_manager: DBManager, lang: str) -> None:
    """Show enhanced main menu with quick access buttons"""
    try:
        general_manager = GeneralManager(db_manager, bot)
        await general_manager.ensure_user_exists(message.chat.id, message.from_user)
        
        bot_info = await bot.get_me()
        text = T[lang].get('start_message', "🤖 Welcome to {bot_name}!\n\nGet ready to play.").format(
            first_name=message.from_user.first_name or "User",
            bot_name=bot_info.first_name or "TrumpBot"
        )
        
        # Add quick stats
        stats = await general_manager.get_user_stats(message.chat.id, message.from_user.id)
        text += f"\n\n📊 **{T[lang].get('quick_stats', 'Quick Stats')}:**"
        text += f"\n• {T[lang].get('level', 'Level')}: {stats['level']}"
        text += f"\n• {T[lang].get('score', 'Score')}: {stats['score']}"
        text += f"\n• {T[lang].get('hp', 'HP')}: {stats['hp']}"
            
        # Create enhanced keyboard
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        # First row - Core commands
        attack_btn = types.InlineKeyboardButton(
            f"⚔️ {T[lang].get('attack_button', 'Attack')}", 
            callback_data='quick:attack'
        )
        stats_btn = types.InlineKeyboardButton(
            f"📊 {T[lang].get('stats_button', 'Stats')}", 
            callback_data='quick:stats'
        )
        markup.add(attack_btn, stats_btn)
        
        # Second row - Management
        shop_btn = types.InlineKeyboardButton(
            f"🛒 {T[lang].get('shop_button', 'Shop')}", 
            callback_data='quick:shop'
        )
        inventory_btn = types.InlineKeyboardButton(
            f"🎒 {T[lang].get('inventory_button', 'Inventory')}", 
            callback_data='quick:inventory'
        )
        markup.add(shop_btn, inventory_btn)
        
        # Third row - Information
        help_btn = types.InlineKeyboardButton(
            f"❓ {T[lang].get('help_button', 'Help')}", 
            callback_data='help:main'
        )
        lang_btn = types.InlineKeyboardButton(
            f"🌐 {T[lang].get('language_button', 'Language')}", 
            callback_data='lang:main'
        )
        markup.add(help_btn, lang_btn)
        
        # Fourth row - Leaderboard
        leaderboard_btn = types.InlineKeyboardButton(
            f"🏆 {T[lang].get('leaderboard_button', 'Leaderboard')}", 
            callback_data='quick:leaderboard'
        )
        markup.add(leaderboard_btn)
        
        await bot.send_message(
            message.chat.id, 
            text, 
            reply_markup=markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error showing main menu: {e}")
        await bot.send_message(
            message.chat.id, 
            T[lang].get('error_generic', {})
        )

async def show_user_profile(message: types.Message, bot: AsyncTeleBot, db_manager: DBManager, lang: str, target_user_id: Optional[int] = None) -> None:
    """Show detailed user profile"""
    try:
        general_manager = GeneralManager(db_manager, bot)
        user_id = target_user_id or message.from_user.id
        
        # Get target user info
        if target_user_id and target_user_id != message.from_user.id:
            try:
                target_member = await bot.get_chat_member(message.chat.id, target_user_id)
                target_user = target_member.user
                display_name = target_user.first_name or "Unknown"
            except Exception:
                display_name = "Unknown User"
        else:
            target_user = message.from_user
            display_name = target_user.first_name or "Unknown"
        
        general_manager = GeneralManager(db_manager, bot)
        await general_manager.ensure_user_exists(message.chat.id, message.from_user)
        lang = await general_manager.get_user_language(message.chat.id, message.from_user.id)
        
        stats = await general_manager.get_user_stats(message.chat.id, user_id)
        
        text = f"👤 **{T[lang].get('profile_title', 'Profile')}:** {display_name}\n\n"
        
        # Basic stats
        text += f"📊 **{T[lang].get('statistics', 'Statistics')}:**\n"
        text += f"• {T[lang].get('level', 'Level')}: {stats['level']}\n"
        text += f"• {T[lang].get('score', 'Score')}: {stats['score']}\n"
        text += f"• {T[lang].get('hp', 'HP')}: {stats['hp']}/100\n\n"
            
        # Combat stats
        text += f"⚔️ **{T[lang].get('combat_stats', 'Combat Stats')}:**\n"
        text += f"• {T[lang].get('total_attacks', 'Total Attacks')}: {stats['attacks']}\n"
        text += f"• {T[lang].get('total_damage', 'Total Damage')}: {stats['total_damage']}\n"
        text += f"• {T[lang].get('times_attacked', 'Times Attacked')}: {stats['times_attacked']}\n\n"
        
        # Join date
        #join_date = stats['created_at'].strftime("%Y-%m-%d") if stats.get('created_at') else "Unknown"
        #text += f"ðŸ“… {T[lang].get('join_date', {})}: {join_date}"
        
        # Add action buttons if viewing own profile
        if user_id == message.from_user.id:
            markup = types.InlineKeyboardMarkup(row_width=2)
            
            attack_btn = types.InlineKeyboardButton(
                f"⚔️ {T[lang].get('attack_button', 'Attack')}", 
                callback_data='quick:attack'
            )
            inventory_btn = types.InlineKeyboardButton(
                f"🎒 {T[lang].get('inventory_button', 'Inventory')}", 
                callback_data='quick:inventory'
            )
            markup.add(attack_btn, inventory_btn)
        else:
            markup = types.InlineKeyboardMarkup()
            attack_btn = types.InlineKeyboardButton(
                f"⚔️ {T[lang].get('attack_user', 'Attack User')}", 
                callback_data=f'attack_user:{user_id}'
            )
            markup.add(attack_btn)
        
        await bot.send_message(
            message.chat.id, 
            text, 
            reply_markup=markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error showing user profile: {e}")
        await bot.send_message(
            message.chat.id, 
            T[lang].get('error_generic', {})
        )

async def show_leaderboard(message: types.Message, bot: AsyncTeleBot, db_manager: DBManager, lang: str) -> None:
    """Show chat leaderboard with rankings"""
    try:
        general_manager = GeneralManager(db_manager, bot)
        leaderboard = await general_manager.get_leaderboard(message.chat.id, 10)
        
        if not leaderboard:
            await bot.send_message(
                message.chat.id, 
                T[lang].get('no_players', {})
            )
            return
        
        text = f"🏆 **{T[lang].get('leaderboard_title', 'Leaderboard')}**\n\n"
        
        medals = ["🥇", "🥈", "🥉"]
        for i, player in enumerate(leaderboard, 1):
            medal = medals[i-1] if i <= 3 else f"{i}."
            name = player.get('first_name') or player.get('username') or "Unknown"
            score = player.get('score', 0)
            level = player.get('level', 1)
            
            text += f"{medal} **{name}** - {score} {T[lang].get('points', {})} (Lv.{level})\n"
        
        # Find current user's position
        try:
            user_position = await db_manager.db(
                """SELECT COUNT(*) + 1 as position FROM players 
                   WHERE chat_id=%s AND score > (
                       SELECT score FROM players WHERE chat_id=%s AND user_id=%s
                   )""",
                (message.chat.id, message.chat.id, message.from_user.id),
                fetch="one_dict"
            )
            
            if user_position:
                pos = user_position.get('position', 'N/A')
                text += f"\n📍 {T[lang].get('your_position', 'Your Position')}: #{pos}"
        except Exception as e:
            logger.warning(f"Error getting user position: {e}")
        
        markup = types.InlineKeyboardMarkup()
        refresh_btn = types.InlineKeyboardButton(
            f"🔄 {T[lang].get('refresh', 'Refresh')}", 
            callback_data='quick:leaderboard'
        )
        markup.add(refresh_btn)
        
        await bot.send_message(
            message.chat.id, 
            text, 
            reply_markup=markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error showing leaderboard: {e}")
        await bot.send_message(
            message.chat.id, 
            T[lang].get('error_generic', {})
        )

async def show_chat_stats(message: types.Message, bot: AsyncTeleBot, db_manager: DBManager, lang: str) -> None:
    """Show comprehensive chat statistics"""
    try:
        general_manager = GeneralManager(db_manager, bot)
        stats = await general_manager.get_chat_statistics(message.chat.id)
        
        text = f"📈 **{T[lang].get('chat_stats_title', 'Chat Statistics')}**\n\n"
        
        text += f"👥 {T[lang].get('total_players', 'Total Players')}: {stats['total_players']}\n"
        text += f"⚔️ {T[lang].get('total_attacks', 'Total Attacks')}: {stats['total_attacks']}\n"
        text += f"📊 {T[lang].get('average_level', 'Average Level')}: {stats['average_level']}\n"
            
        if stats['top_attacker_id']:
            try:
                top_attacker_member = await bot.get_chat_member(message.chat.id, stats['top_attacker_id'])
                attacker_name = top_attacker_member.user.first_name or "Unknown"
                text += f"\n🏆 {T[lang].get('most_active_attacker', 'Most Active Attacker')}: {attacker_name} ({stats['top_attacker_attacks']} attacks)"
            except Exception:
                text += f"\n🏆 {T[lang].get('most_active_attacker', 'Most Active Attacker')}: Unknown ({stats['top_attacker_attacks']} attacks)"
        
        await bot.send_message(
            message.chat.id, 
            text, 
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error showing chat stats: {e}")
        await bot.send_message(
            message.chat.id, 
            T[lang].get('error_generic', {})
        )

async def handle_quick_callback(call: types.CallbackQuery, bot: AsyncTeleBot, db_manager: DBManager) -> None:
    """Handle quick action callbacks from main menu"""
    try:
        action = call.data.replace('quick:', '')
        general_manager = GeneralManager(db_manager, bot)
        await general_manager.ensure_user_exists(call.message.chat.id, call.from_user)
        lang = await general_manager.get_user_language(call.message.chat.id, call.from_user.id)

        if action == 'attack':
            # Import here to avoid circular imports
            from src.commands.attack import show_attack_menu
            fake_message = types.Message(
                message_id=call.message.message_id,
                from_user=call.from_user,
                date=call.message.date,
                chat=call.message.chat,
                content_type='text',
                options={},
                json_string=""
            )
            await show_attack_menu(fake_message, bot, db_manager, lang)
            
        elif action == 'stats':
            fake_message = types.Message(
                message_id=call.message.message_id,
                from_user=call.from_user,
                date=call.message.date,
                chat=call.message.chat,
                content_type='text',
                options={},
                json_string=""
            )
            await show_user_profile(fake_message, bot, db_manager, lang)
            
        elif action == 'shop':
            await bot.answer_callback_query(
                call.id, 
                T[lang].get('shop_coming_soon', {}),
                show_alert=True
            )
            
        elif action == 'inventory':
            await bot.answer_callback_query(
                call.id, 
                T[lang].get('inventory_coming_soon', {}),
                show_alert=True
            )
            
        elif action == 'menu':
            # Show main menu
            fake_message = types.Message(
                message_id=call.message.message_id,
                from_user=call.from_user,
                date=call.message.date,
                chat=call.message.chat,
                content_type='text',
                options={},
                json_string=""
            )
            await show_main_menu(fake_message, bot, db_manager, lang)
            
        elif action == 'leaderboard':
            fake_message = types.Message(
                message_id=call.message.message_id,
                from_user=call.from_user,
                date=call.message.date,
                chat=call.message.chat,
                content_type='text',
                options={},
                json_string=""
            )
            await show_leaderboard(fake_message, bot, db_manager, lang)
        
        elif action == 'menu':
            fake_message = types.Message(
                message_id=call.message.message_id,
                from_user=call.from_user,
                date=call.message.date,
                chat=call.message.chat,
                content_type='text',
                options={},
                json_string=""
            )
            await show_main_menu(fake_message, bot, db_manager, lang)
        
        await bot.answer_callback_query(call.id)
        
    except Exception as e:
        logger.error(f"Error handling quick callback: {e}")
        await bot.answer_callback_query(call.id, "Error processing request.")

async def handle_language_callback(call: types.CallbackQuery, bot: AsyncTeleBot, db_manager: DBManager) -> None:
    """Handle language selection callbacks"""
    try:
        if call.data == 'lang:main':
            # Show language selection menu
            markup = types.InlineKeyboardMarkup(row_width=2)
            en_button = types.InlineKeyboardButton("🇬🇧 English", callback_data='lang:en')
            fa_button = types.InlineKeyboardButton("🇮🇷 فارسی", callback_data='lang:fa')
            markup.add(en_button, fa_button)
            
            current_lang = await helpers.get_lang(call.message.chat.id, call.from_user.id, db_manager)
            await bot.edit_message_text(
                T[current_lang].get('language_selection', "🌐 Select your language:"),
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup
            )
        else:
            # Set language
            new_lang = call.data.split(':')[1]
            if new_lang in ['en', 'fa']:

                await helpers.set_lang(call.message.chat.id, call.from_user.id, new_lang, db_manager)

                success_msg = T[new_lang].get('language_changed', "✅ Language changed successfully!")
                await bot.edit_message_text(
                    success_msg,
                    call.message.chat.id,
                    call.message.message_id
                )
        
        await bot.answer_callback_query(call.id)
        
    except Exception as e:
        logger.error(f"Error handling language callback: {e}")
        await bot.answer_callback_query(call.id, "Error changing language.")

def register_handlers(bot: AsyncTeleBot, db_manager: DBManager) -> None:
    """
    Registers all command handlers for the general module.
    """
    group_only = helpers.ensure_group_command(bot, db_manager)

    @bot.message_handler(commands=['start'])
    async def start_command(message: types.Message) -> None:
        """
        Handles the /start command - welcomes new users and shows main menu.
        """
        try:
            general_manager = GeneralManager(db_manager, bot)
            await general_manager.ensure_user_exists(message.chat.id, message.from_user)
            lang = await general_manager.get_user_language(message.chat.id, message.from_user.id)
            
            await show_main_menu(message, bot, db_manager, lang)
            
        except Exception as e:
            logger.error(f"Error in start command: {e}")
            await bot.send_message(
                message.chat.id, 
                "Sorry, there was an error processing your request."
            )

    @bot.message_handler(commands=['menu', 'main'])
    @group_only
    async def menu_command(message: types.Message) -> None:
        """Show main menu"""
        try:
            general_manager = GeneralManager(db_manager, bot)
            await general_manager.ensure_user_exists(message.chat.id, message.from_user)
            lang = await general_manager.get_user_language(message.chat.id, message.from_user.id)
            
            await show_main_menu(message, bot, db_manager, lang)
            
        except Exception as e:
            logger.error(f"Error in menu command: {e}")
            await bot.send_message(message.chat.id, "Error displaying menu.")

    @bot.message_handler(commands=['profile', 'me'])
    @group_only
    async def profile_command(message: types.Message) -> None:
        """Show user profile"""
        try:
            general_manager = GeneralManager(db_manager, bot)
            await general_manager.ensure_user_exists(message.chat.id, message.from_user)
            lang = await general_manager.get_user_language(message.chat.id, message.from_user.id)
            
            await show_user_profile(message, bot, db_manager, lang)
            
        except Exception as e:
            logger.error(f"Error in profile command: {e}")
            await bot.send_message(message.chat.id, "Error displaying profile.")

    @bot.message_handler(commands=['leaderboard', 'top'])
    @group_only
    async def leaderboard_command(message: types.Message) -> None:
        """Show chat leaderboard"""
        try:
            general_manager = GeneralManager(db_manager, bot)
            await general_manager.ensure_user_exists(message.chat.id, message.from_user)
            lang = await general_manager.get_user_language(message.chat.id, message.from_user.id)
            
            await show_leaderboard(message, bot, db_manager, lang)
            
        except Exception as e:
            logger.error(f"Error in leaderboard command: {e}")
            await bot.send_message(message.chat.id, "Error displaying leaderboard.")

    @bot.message_handler(commands=['chat_stats'])
    @group_only
    async def chat_stats_command(message: types.Message) -> None:
        """Show chat statistics"""
        try:
            general_manager = GeneralManager(db_manager, bot)
            await general_manager.ensure_user_exists(message.chat.id, message.from_user)
            lang = await general_manager.get_user_language(message.chat.id, message.from_user.id)
            
            await show_chat_stats(message, bot, db_manager, lang)
            
        except Exception as e:
            logger.error(f"Error in chat stats command: {e}")
            await bot.send_message(message.chat.id, "Error displaying chat statistics.")

    @bot.message_handler(commands=['help'])
    async def help_command(message: types.Message) -> None:
        """Show help message - delegate to help module"""
        try:
            # Import help module to avoid circular imports
            from src.commands.help import _send_main_help_menu
            
            general_manager = GeneralManager(db_manager, bot)
            await general_manager.ensure_user_exists(message.chat.id, message.from_user)
            lang = await general_manager.get_user_language(message.chat.id, message.from_user.id)
            
            await _send_main_help_menu(message, bot, db_manager, lang)
            
        except Exception as e:
            logger.error(f"Error in help command: {e}")
            await bot.send_message(message.chat.id, "Error displaying help.")

    @bot.message_handler(commands=['language', 'lang'])
    async def language_command(message: types.Message) -> None:
        """
        Handles the /language command - shows language selection menu.
        """
        try:
            general_manager = GeneralManager(db_manager, bot)
            await general_manager.ensure_user_exists(message.chat.id, message.from_user)
            lang = await general_manager.get_user_language(message.chat.id, message.from_user.id)
            
            markup = types.InlineKeyboardMarkup(row_width=2)
            en_button = types.InlineKeyboardButton("🇬🇧 English", callback_data='lang:en')
            fa_button = types.InlineKeyboardButton("🇮🇷 فارسی", callback_data='lang:fa')
            markup.add(en_button, fa_button)
            
            await bot.send_message(
                message.chat.id, 
                T[lang].get('language_selection', "🌐 Select your language:"), 
                reply_markup=markup
            )
            
        except Exception as e:
            logger.error(f"Error in language command: {e}")
            await bot.send_message(
                message.chat.id, 
                "Error setting language. Please try again."
            )
    
    # Callback query handlers
    @bot.callback_query_handler(func=lambda call: call.data.startswith('quick:'))
    async def quick_callback_handler(call: types.CallbackQuery) -> None:
        await handle_quick_callback(call, bot, db_manager)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('lang:'))
    async def language_callback_handler(call: types.CallbackQuery) -> None:
        await handle_language_callback(call, bot, db_manager)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('help:'))
    async def help_callback_handler(call: types.CallbackQuery) -> None:
        """Enhanced help callback handler - delegate to help module"""
        try:
            # Import help module to avoid circular imports
            from src.commands.help import handle_help_callback
            await handle_help_callback(call, bot, db_manager)
            
        except Exception as e:
            logger.error(f"Error in help callback: {e}")
            await bot.answer_callback_query(call.id, "Error displaying help.")


