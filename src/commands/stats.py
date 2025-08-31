#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Statistics commands module with comprehensive analytics and bilingual support
Provides detailed statistics, rankings, and performance analytics for players and groups
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from src.utils import helpers
from src.utils.translations import T
from src.database.db_manager import DBManager
from src.config.items import ITEMS, get_item_display_name, get_item_emoji

# Set up logging
logger = logging.getLogger(__name__)

class StatsManager:
    """Manages comprehensive statistics system with analytics and rankings"""
    
    def __init__(self, db_manager: DBManager):
        self.db_manager = db_manager
    
    async def get_player_stats(self, chat_id: int, user_id: int) -> Dict[str, Any]:
        """Get comprehensive player statistics"""
        try:
            # Basic player info
            player_data = await self.db_manager.db(
                """SELECT first_name, level, score, hp, max_hp, tg_stars, 
                          last_attack, created_at 
                   FROM players WHERE chat_id=%s AND user_id=%s""",
                (chat_id, user_id),
                fetch="one_dict"
            )
            
            if not player_data:
                return {}
            
            # Combat statistics
            combat_stats = await self.db_manager.db(
                """SELECT COUNT(*) as total_attacks,
                          SUM(CASE WHEN damage > 0 THEN 1 ELSE 0 END) as successful_attacks,
                          SUM(damage) as total_damage_dealt,
                          AVG(damage) as avg_damage
                   FROM attacks WHERE chat_id=%s AND attacker_id=%s""",
                (chat_id, user_id),
                fetch="one_dict"
            )
            
            # Times attacked
            defense_stats = await self.db_manager.db(
                """SELECT COUNT(*) as times_attacked,
                          SUM(damage) as total_damage_taken,
                          SUM(CASE WHEN damage = 0 THEN 1 ELSE 0 END) as successful_defenses
                   FROM attacks WHERE chat_id=%s AND victim_id=%s""",
                (chat_id, user_id),
                fetch="one_dict"
            )
            
            # Inventory value
            inventory_stats = await self.db_manager.db(
                """SELECT COUNT(DISTINCT item) as unique_items,
                          SUM(qty) as total_items
                   FROM inventories WHERE chat_id=%s AND user_id=%s AND qty > 0""",
                (chat_id, user_id),
                fetch="one_dict"
            )
            
            # Rank in group
            rank_data = await self.db_manager.db(
                """SELECT COUNT(*) + 1 as rank
                   FROM players 
                   WHERE chat_id=%s AND score > (
                       SELECT score FROM players WHERE chat_id=%s AND user_id=%s
                   )""",
                (chat_id, chat_id, user_id),
                fetch="one_dict"
            )
            
            # Most used weapon
            favorite_weapon = await self.db_manager.db(
                """SELECT weapon, COUNT(*) as usage_count
                   FROM attacks WHERE chat_id=%s AND attacker_id=%s AND weapon IS NOT NULL
                   GROUP BY weapon ORDER BY usage_count DESC LIMIT 1""",
                (chat_id, user_id),
                fetch="one_dict"
            )
            
            # Calculate additional metrics
            total_attacks = combat_stats.get('total_attacks', 0)
            successful_attacks = combat_stats.get('successful_attacks', 0)
            times_attacked = defense_stats.get('times_attacked', 0)
            successful_defenses = defense_stats.get('successful_defenses', 0)
            
            win_rate = (successful_attacks / total_attacks * 100) if total_attacks > 0 else 0
            survival_rate = (successful_defenses / times_attacked * 100) if times_attacked > 0 else 100
            
            return {
                **player_data,
                **combat_stats,
                **defense_stats,
                **inventory_stats,
                'rank': rank_data.get('rank', 1) if rank_data else 1,
                'win_rate': round(win_rate, 1),
                'survival_rate': round(survival_rate, 1),
                'favorite_weapon': favorite_weapon.get('weapon') if favorite_weapon else None,
                'kd_ratio': round(successful_attacks / max(times_attacked - successful_defenses, 1), 2)
            }
        except Exception as e:
            logger.error(f"Error getting player stats: {e}")
            return {}
    
    async def get_group_stats(self, chat_id: int) -> Dict[str, Any]:
        """Get comprehensive group statistics"""
        try:
            # Basic group stats
            group_stats = await self.db_manager.db(
                """SELECT COUNT(*) as total_players,
                          SUM(CASE WHEN last_attack > NOW() - INTERVAL '7 days' THEN 1 ELSE 0 END) as active_players,
                          MAX(score) as highest_score,
                          AVG(score) as avg_score
                   FROM players WHERE chat_id=%s""",
                (chat_id,),
                fetch="one_dict"
            )
            
            # Top players
            top_players = await self.db_manager.db(
                """SELECT user_id, first_name, score, level
                   FROM players WHERE chat_id=%s 
                   ORDER BY score DESC LIMIT 10""",
                (chat_id,),
                fetch="all_dicts"
            )
            
            # Combat activity
            combat_stats = await self.db_manager.db(
                """SELECT COUNT(*) as total_battles,
                          COUNT(DISTINCT attacker_id) as active_attackers,
                          SUM(damage) as total_damage,
                          AVG(damage) as avg_damage
                   FROM attacks WHERE chat_id=%s""",
                (chat_id,),
                fetch="one_dict"
            )
            
            # Most active player
            most_active = await self.db_manager.db(
                """SELECT p.user_id, p.first_name, COUNT(a.id) as attack_count
                   FROM players p 
                   LEFT JOIN attacks a ON p.user_id = a.attacker_id AND p.chat_id = a.chat_id
                   WHERE p.chat_id=%s 
                   GROUP BY p.user_id, p.first_name
                   ORDER BY attack_count DESC LIMIT 1""",
                (chat_id,),
                fetch="one_dict"
            )
            
            # Most used weapon
            popular_weapon = await self.db_manager.db(
                """SELECT weapon, COUNT(*) as usage_count
                   FROM attacks WHERE chat_id=%s AND weapon IS NOT NULL
                   GROUP BY weapon ORDER BY usage_count DESC LIMIT 1""",
                (chat_id,),
                fetch="one_dict"
            )
            
            return {
                **group_stats,
                **combat_stats,
                'top_players': top_players or [],
                'most_active_player': most_active,
                'popular_weapon': popular_weapon.get('weapon') if popular_weapon else None
            }
        except Exception as e:
            logger.error(f"Error getting group stats: {e}")
            return {}
    
    async def get_leaderboard(self, chat_id: int, limit: int = 10) -> List[Dict]:
        """Get detailed leaderboard with rankings"""
        try:
            leaderboard = await self.db_manager.db(
                """SELECT user_id, first_name, score, level, hp, max_hp,
                          (SELECT COUNT(*) FROM attacks WHERE attacker_id = p.user_id AND chat_id = p.chat_id) as attacks,
                          (SELECT COUNT(*) FROM attacks WHERE victim_id = p.user_id AND chat_id = p.chat_id) as times_attacked,
                          ROW_NUMBER() OVER (ORDER BY score DESC) as rank
                   FROM players p WHERE chat_id=%s 
                   ORDER BY score DESC LIMIT %s""",
                (chat_id, limit),
                fetch="all_dicts"
            )
            return leaderboard or []
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
    
    async def show_stats_dashboard(self, bot: AsyncTeleBot, message: types.Message):
        """Display comprehensive statistics dashboard"""
        try:
            lang = await helpers.get_lang(message.chat.id, message.from_user.id, self.db_manager)
            
            # Build dashboard message
            dashboard_text = f"ðŸ“Š <b>{T[lang]['stats_dashboard'][lang]}</b>\n\n"
            dashboard_text += f"ðŸ“ˆ <b>{T[lang]['stats_overview'][lang]}</b>\n"
            dashboard_text += f"{T[lang].get('help_intro', {})}"
            
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            
            # Main statistics categories
            personal_btn = types.InlineKeyboardButton(
                f"ðŸ‘¤ {T[lang]['personal_stats'][lang]}", 
                callback_data="stats:personal"
            )
            combat_btn = types.InlineKeyboardButton(
                f"âš”ï¸ {T[lang]['combat_analytics'][lang]}", 
                callback_data="stats:combat"
            )
            keyboard.add(personal_btn, combat_btn)
            
            # Group and ranking
            group_btn = types.InlineKeyboardButton(
                f"ðŸ‘¥ {T[lang]['group_stats'][lang]}", 
                callback_data="stats:group"
            )
            leaderboard_btn = types.InlineKeyboardButton(
                f"ðŸ† {T[lang]['leaderboard_ranking'][lang]}", 
                callback_data="stats:leaderboard"
            )
            keyboard.add(group_btn, leaderboard_btn)
            
            # Additional features
            weapons_btn = types.InlineKeyboardButton(
                f"ðŸ”« {T[lang]['view_weapons'][lang]}", 
                callback_data="stats:weapons"
            )
            trends_btn = types.InlineKeyboardButton(
                f"ðŸ“ˆ {T[lang]['view_trends'][lang]}", 
                callback_data="stats:trends"
            )
            keyboard.add(weapons_btn, trends_btn)
            
            # Utility buttons
            refresh_btn = types.InlineKeyboardButton(
                f"ðŸ”„ {T[lang]['refresh_stats'][lang]}", 
                callback_data="stats:refresh"
            )
            close_btn = types.InlineKeyboardButton(
                f"âŒ {T[lang]['close_stats'][lang]}", 
                callback_data="stats:close"
            )
            keyboard.add(refresh_btn, close_btn)
            
            await bot.send_message(
                message.chat.id, 
                dashboard_text, 
                reply_markup=keyboard, 
                parse_mode="HTML"
            )
            
        except Exception as e:
            logger.error(f"Error showing stats dashboard: {e}")
            await bot.send_message(
                message.chat.id, 
                "âŒ Error displaying statistics dashboard. Please try again."
            )
    
    async def show_personal_stats(self, bot: AsyncTeleBot, call: types.CallbackQuery):
        """Display detailed personal statistics"""
        try:
            lang = await helpers.get_lang(call.message.chat.id, call.from_user.id, self.db_manager)
            player_stats = await self.get_player_stats(call.message.chat.id, call.from_user.id)
            
            if not player_stats:
                await bot.answer_callback_query(
                    call.id, 
                    T[lang]['stats_no_data'][lang], 
                    show_alert=True
                )
                return
            
            # Build personal stats message
            stats_text = f"ðŸ‘¤ <b>{T[lang]['personal_stats'][lang]}</b>\n"
            stats_text += f"<b>{player_stats.get('first_name', 'Player')}</b>\n\n"
            
            # Basic info
            stats_text += f"ðŸ“Š <b>{T[lang]['stats_overview'][lang]}:</b>\n"
            stats_text += f"ðŸ† {T[lang]['your_rank'][lang]}: <b>#{player_stats.get('rank', 'N/A')}</b>\n"
            stats_text += f"ðŸ“ˆ {T[lang]['current_level'][lang]}: <b>{player_stats.get('level', 1)}</b>\n"
            stats_text += f"ðŸ… {T[lang]['total_score'][lang]}: <b>{player_stats.get('score', 0)}</b>\n"
            stats_text += f"â¤ï¸ {T[lang]['current_hp'][lang]}: <b>{player_stats.get('hp', 0)}/{player_stats.get('max_hp', 100)}</b>\n\n"
            
            # Combat stats
            stats_text += f"âš”ï¸ <b>{T[lang]['combat_analytics'][lang]}:</b>\n"
            stats_text += f"ðŸ—¡ï¸ {T[lang]['battles_fought'][lang]}: <b>{player_stats.get('total_attacks', 0)}</b>\n"
            stats_text += f"âœ… {T[lang]['battles_won'][lang]}: <b>{player_stats.get('successful_attacks', 0)}</b>\n"
            stats_text += f"ðŸ“Š {T[lang]['win_rate'][lang]}: <b>{player_stats.get('win_rate', 0)}%</b>\n"
            stats_text += f"ðŸ’¥ {T[lang]['total_damage_dealt'][lang]}: <b>{player_stats.get('total_damage_dealt', 0) or 0}</b>\n"
            stats_text += f"ðŸ›¡ï¸ {T[lang]['times_attacked'][lang]}: <b>{player_stats.get('times_attacked', 0)}</b>\n"
            stats_text += f"ðŸ”’ {T[lang]['successful_defenses'][lang]}: <b>{player_stats.get('successful_defenses', 0)}</b>\n"
            stats_text += f"ðŸ“ˆ {T[lang]['survival_rate'][lang]}: <b>{player_stats.get('survival_rate', 100)}%</b>\n\n"
            
            # Additional metrics
            stats_text += f"ðŸ“‹ <b>{T[lang].get('additional_metrics', {})}:</b>\n"
            stats_text += f"âš–ï¸ K/D {T[lang]['kill_death_ratio'][lang]}: <b>{player_stats.get('kd_ratio', 0)}</b>\n"
            stats_text += f"ðŸ“¦ {T[lang]['weapons_owned'][lang]}: <b>{player_stats.get('unique_items', 0)}</b>\n"
            
            if player_stats.get('favorite_weapon'):
                weapon_name = get_item_display_name(player_stats['favorite_weapon'], lang)
                emoji = get_item_emoji(player_stats['favorite_weapon'])
                stats_text += f"ðŸ”« {T[lang]['favorite_weapon'][lang]}: <b>{emoji} {weapon_name}</b>\n"
            
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(
                types.InlineKeyboardButton(f"âš”ï¸ {T[lang]['view_combat'][lang]}", callback_data="stats:combat"),
                types.InlineKeyboardButton(f"ðŸ† {T[lang]['view_leaderboard'][lang]}", callback_data="stats:leaderboard")
            )
            keyboard.add(
                types.InlineKeyboardButton(f"ðŸ”™ {T[lang]['back_btn'][lang]}", callback_data="stats:main"),
                types.InlineKeyboardButton(f"âŒ {T[lang]['close_stats'][lang]}", callback_data="stats:close")
            )
            
            await bot.edit_message_text(
                stats_text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            
        except Exception as e:
            logger.error(f"Error showing personal stats: {e}")
            await bot.answer_callback_query(call.id, T[lang]['stats_error'][lang])
    
    async def show_group_stats(self, bot: AsyncTeleBot, call: types.CallbackQuery):
        """Display comprehensive group statistics"""
        try:
            lang = await helpers.get_lang(call.message.chat.id, call.from_user.id, self.db_manager)
            group_stats = await self.get_group_stats(call.message.chat.id)
            
            if not group_stats:
                await bot.answer_callback_query(
                    call.id, 
                    T[lang]['stats_no_data'][lang], 
                    show_alert=True
                )
                return
            
            # Build group stats message
            stats_text = f"ðŸ‘¥ <b>{T[lang]['group_stats'][lang]}</b>\n\n"
            
            # Player statistics
            stats_text += f"ðŸ‘¨â€ðŸ‘©â€ðŸ‘§â€ðŸ‘¦ <b>{T[lang].get('player_overview', {})}:</b>\n"
            stats_text += f"ðŸ‘¤ {T[lang]['total_players'][lang]}: <b>{group_stats.get('total_players', 0)}</b>\n"
            stats_text += f"ðŸŸ¢ {T[lang]['active_players'][lang]}: <b>{group_stats.get('active_players', 0)}</b>\n"
            stats_text += f"ðŸ† {T[lang].get('highest_score', {})}: <b>{group_stats.get('highest_score', 0) or 0}</b>\n"
            stats_text += f"ðŸ“Š {T[lang].get('average_score', {})}: <b>{round(group_stats.get('avg_score', 0) or 0)}</b>\n\n"
            
            # Combat statistics
            stats_text += f"âš”ï¸ <b>{T[lang]['combat_analytics'][lang]}:</b>\n"
            stats_text += f"ðŸ—¡ï¸ {T[lang]['total_battles'][lang]}: <b>{group_stats.get('total_battles', 0)}</b>\n"
            stats_text += f"ðŸ‘¥ {T[lang].get('active_fighters', {})}: <b>{group_stats.get('active_attackers', 0)}</b>\n"
            stats_text += f"ðŸ’¥ {T[lang].get('total_damage', {})}: <b>{group_stats.get('total_damage', 0) or 0}</b>\n"
            stats_text += f"ðŸ“Š {T[lang]['average_damage'][lang]}: <b>{round(group_stats.get('avg_damage', 0) or 0)}</b>\n\n"
            
            # Most active player
            if group_stats.get('most_active_player'):
                most_active = group_stats['most_active_player']
                stats_text += f"ðŸ¥‡ {T[lang]['most_active_player'][lang]}: <b>{most_active.get('first_name', 'Unknown')}</b>\n"
                stats_text += f"   {T[lang].get('attacks_made', {})}: <b>{most_active.get('attack_count', 0)}</b>\n\n"
            
            # Popular weapon
            if group_stats.get('popular_weapon'):
                weapon_name = get_item_display_name(group_stats['popular_weapon'], lang)
                emoji = get_item_emoji(group_stats['popular_weapon'])
                stats_text += f"ðŸ”« {T[lang].get('most_popular_weapon', {})}: <b>{emoji} {weapon_name}</b>\n\n"
            
            # Top 3 players preview
            if group_stats.get('top_players'):
                stats_text += f"ðŸ† <b>{T[lang].get('top_players_preview', {})}:</b>\n"
                for i, player in enumerate(group_stats['top_players'][:3], 1):
                    medal = "ðŸ¥‡" if i == 1 else "ðŸ¥ˆ" if i == 2 else "ðŸ¥‰"
                    stats_text += f"{medal} <b>{player.get('first_name', 'Unknown')}</b> - {player.get('score', 0)} ðŸ…\n"
            
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(
                types.InlineKeyboardButton(f"ðŸ† {T[lang]['view_leaderboard'][lang]}", callback_data="stats:leaderboard"),
                types.InlineKeyboardButton(f"ðŸ‘¤ {T[lang]['view_personal'][lang]}", callback_data="stats:personal")
            )
            keyboard.add(
                types.InlineKeyboardButton(f"ðŸ”™ {T[lang]['back_btn'][lang]}", callback_data="stats:main"),
                types.InlineKeyboardButton(f"âŒ {T[lang]['close_stats'][lang]}", callback_data="stats:close")
            )
            
            await bot.edit_message_text(
                stats_text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            
        except Exception as e:
            logger.error(f"Error showing group stats: {e}")
            await bot.answer_callback_query(call.id, T[lang]['stats_error'][lang])
    
    async def show_leaderboard(self, bot: AsyncTeleBot, call: types.CallbackQuery):
        """Display detailed leaderboard with rankings"""
        try:
            lang = await helpers.get_lang(call.message.chat.id, call.from_user.id, self.db_manager)
            leaderboard = await self.get_leaderboard(call.message.chat.id)
            
            if not leaderboard:
                await bot.answer_callback_query(
                    call.id, 
                    T[lang]['stats_no_data'][lang], 
                    show_alert=True
                )
                return
            
            # Build leaderboard message
            leaderboard_text = f"ðŸ† <b>{T[lang]['leaderboard_ranking'][lang]}</b>\n\n"
            
            for player in leaderboard:
                rank = int(player.get('rank', 0))
                name = player.get('first_name', 'Unknown')
                score = player.get('score', 0)
                level = player.get('level', 1)
                attacks = player.get('attacks', 0)
                
                # Rank emoji
                if rank == 1:
                    rank_emoji = "ðŸ¥‡"
                elif rank == 2:
                    rank_emoji = "ðŸ¥ˆ"
                elif rank == 3:
                    rank_emoji = "ðŸ¥‰"
                else:
                    rank_emoji = f"{rank}."
                
                leaderboard_text += f"{rank_emoji} <b>{name}</b>\n"
                leaderboard_text += f"   ðŸ“Š {T[lang]['total_score'][lang]}: <b>{score}</b> ðŸ…\n"
                leaderboard_text += f"   ðŸ“ˆ {T[lang]['current_level'][lang]}: <b>{level}</b> | ðŸ—¡ï¸ {T[lang].get('attacks', {})}: <b>{attacks}</b>\n\n"
            
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(
                types.InlineKeyboardButton(f"ðŸ‘¤ {T[lang]['view_personal'][lang]}", callback_data="stats:personal"),
                types.InlineKeyboardButton(f"ðŸ‘¥ {T[lang]['view_group'][lang]}", callback_data="stats:group")
            )
            keyboard.add(
                types.InlineKeyboardButton(f"ðŸ”™ {T[lang]['back_btn'][lang]}", callback_data="stats:main"),
                types.InlineKeyboardButton(f"âŒ {T[lang]['close_stats'][lang]}", callback_data="stats:close")
            )
            
            await bot.edit_message_text(
                leaderboard_text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            
        except Exception as e:
            logger.error(f"Error showing leaderboard: {e}")
            await bot.answer_callback_query(call.id, T[lang]['stats_error'][lang])
    
    async def handle_stats_callback(self, bot: AsyncTeleBot, call: types.CallbackQuery):
        """Handle all statistics related callbacks"""
        try:
            data_parts = call.data.split(':')
            action = data_parts[1] if len(data_parts) > 1 else "main"
            lang = await helpers.get_lang(call.message.chat.id, call.from_user.id, self.db_manager)

            if action == "main":
                # Refresh the main dashboard
                dashboard_text = f"ðŸ“Š <b>{T[lang]['stats_dashboard'][lang]}</b>\n\n"
                dashboard_text += f"ðŸ“ˆ <b>{T[lang]['stats_overview'][lang]}</b>\n"
                dashboard_text += f"{T[lang].get('help_intro', {})}"

                keyboard = types.InlineKeyboardMarkup(row_width=2)
                keyboard.add(
                    types.InlineKeyboardButton(f"ðŸ‘¤ {T[lang]['personal_stats'][lang]}", callback_data="stats:personal"),
                    types.InlineKeyboardButton(f"âš”ï¸ {T[lang]['combat_analytics'][lang]}", callback_data="stats:combat")
                )
                keyboard.add(
                    types.InlineKeyboardButton(f"ðŸ‘¥ {T[lang]['group_stats'][lang]}", callback_data="stats:group"),
                    types.InlineKeyboardButton(f"ðŸ† {T[lang]['leaderboard_ranking'][lang]}", callback_data="stats:leaderboard")
                )
                keyboard.add(
                    types.InlineKeyboardButton(f"ðŸ”« {T[lang]['view_weapons'][lang]}", callback_data="stats:weapons"),
                    types.InlineKeyboardButton(f"ðŸ“ˆ {T[lang]['view_trends'][lang]}", callback_data="stats:trends")
                )
                keyboard.add(
                    types.InlineKeyboardButton(f"ðŸ”„ {T[lang]['refresh_stats'][lang]}", callback_data="stats:refresh"),
                    types.InlineKeyboardButton(f"âŒ {T[lang]['close_stats'][lang]}", callback_data="stats:close")
                )

                await bot.edit_message_text(
                    dashboard_text,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            
            elif action == "personal":
                await self.show_personal_stats(bot, call)
            
            elif action == "combat":
                await self.show_personal_stats(bot, call)  # Combat stats are part of personal stats
            
            elif action == "group":
                await self.show_group_stats(bot, call)
            
            elif action == "leaderboard":
                await self.show_leaderboard(bot, call)
            
            elif action == "weapons":
                # Show weapon statistics (placeholder for future enhancement)
                await bot.answer_callback_query(call.id, f"ðŸ”« {T[lang].get('coming_soon', {})}")
            
            elif action == "trends":
                # Show trend analysis (placeholder for future enhancement)
                await bot.answer_callback_query(call.id, f"ðŸ“ˆ {T[lang].get('coming_soon', {})}")
            
            elif action == "refresh":
                await bot.answer_callback_query(call.id, T[lang]['stats_updated'][lang])
                # Trigger main dashboard refresh
                await self.handle_stats_callback(bot, types.CallbackQuery(
                    id=call.id,
                    from_user=call.from_user,
                    message=call.message,
                    data="stats:main"
                ))
            
            elif action == "close":
                await bot.delete_message(call.message.chat.id, call.message.message_id)
            
            await bot.answer_callback_query(call.id)
            
        except Exception as e:
            logger.error(f"Error handling stats callback: {e}")
            await bot.answer_callback_query(call.id, "âŒ Error processing request.")


def register_handlers(bot: AsyncTeleBot, db_manager: DBManager):
    """Registers all statistics related handlers."""
    
    # Initialize StatsManager
    stats_manager = StatsManager(db_manager)
    group_only = helpers.ensure_group_command(bot, db_manager)

    @bot.message_handler(commands=['stats'])
    @group_only
    async def handle_stats_command(message):
        """Handle /stats command to show statistics dashboard"""
        await stats_manager.show_stats_dashboard(bot, message)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('stats:'))
    async def handle_stats_callbacks(call):
        """Handle all statistics related callback queries"""
        await stats_manager.handle_stats_callback(bot, call)


# Legacy compatibility functions
async def handle_stats_callback(call: types.CallbackQuery, bot: AsyncTeleBot, db_manager: DBManager):
    """Legacy callback handler for backward compatibility"""
    stats_manager = StatsManager(db_manager)
    await stats_manager.handle_stats_callback(bot, call)


