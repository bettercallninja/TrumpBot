#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Enhanced Status and Defense Management System
Provides comprehensive player status tracking, defense management, and performance analytics
"""

import logging
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from src.utils import helpers
from src.utils.translations import T
from src.database.db_manager import DBManager
from src.config.items import ITEMS, ItemType, get_item_display_name, get_item_emoji
from src.config.bot_config import BotConfig

# Set up logging
logger = logging.getLogger(__name__)

class StatusManager:
    """Enhanced player status and defense management system"""
    
    def __init__(self, db_manager: DBManager):
        self.db_manager = db_manager
    
    async def get_comprehensive_player_data(self, chat_id: int, user_id: int) -> Dict[str, Any]:
        """Get comprehensive player data with analytics"""
        try:
            # Get basic player data
            player_data = await self.db_manager.db(
                "SELECT score, tg_stars, hp, level, last_attack_time, created_at FROM players WHERE chat_id=%s AND user_id=%s",
                (chat_id, user_id), 
                fetch="one_dict"
            )
            
            if not player_data:
                return {
                    'score': 0, 'tg_stars': 0, 'hp': 100, 'level': 1,
                    'last_attack_time': None, 'created_at': helpers.now(),
                    'combat_stats': {'total_attacks': 0, 'times_attacked': 0, 'total_damage_dealt': 0, 'total_damage_taken': 0},
                    'rank_info': {'rank': 0, 'total_players': 0},
                    'activity_stats': {'days_active': 0, 'last_active': helpers.now()}
                }
            
            # Get combat statistics
            combat_stats = await self.get_combat_statistics(chat_id, user_id)
            
            # Get rank information
            rank_info = await self.get_player_rank(chat_id, user_id)
            
            # Get activity statistics
            activity_stats = await self.get_activity_statistics(chat_id, user_id)
            
            return {
                'score': player_data.get('score', 0),
                'tg_stars': player_data.get('tg_stars', 0),
                'hp': player_data.get('hp', 100),
                'level': player_data.get('level', 1),
                'last_attack_time': player_data.get('last_attack_time'),
                'created_at': player_data.get('created_at', helpers.now()),
                'combat_stats': combat_stats,
                'rank_info': rank_info,
                'activity_stats': activity_stats
            }
        except Exception as e:
            logger.error(f"Error getting comprehensive player data: {e}")
            return {
                'score': 0, 'tg_stars': 0, 'hp': 100, 'level': 1,
                'last_attack_time': None, 'created_at': helpers.now(),
                'combat_stats': {'total_attacks': 0, 'times_attacked': 0, 'total_damage_dealt': 0, 'total_damage_taken': 0},
                'rank_info': {'rank': 0, 'total_players': 0},
                'activity_stats': {'days_active': 0, 'last_active': helpers.now()}
            }
    
    async def get_combat_statistics(self, chat_id: int, user_id: int) -> Dict[str, int]:
        """Get detailed combat statistics"""
        try:
            attack_stats = await self.db_manager.db(
                "SELECT COUNT(*) as total_attacks, COALESCE(SUM(damage), 0) as total_damage_dealt FROM attacks WHERE chat_id=%s AND attacker_id=%s",
                (chat_id, user_id),
                fetch="one_dict"
            )
            
            defense_stats = await self.db_manager.db(
                "SELECT COUNT(*) as times_attacked, COALESCE(SUM(damage), 0) as total_damage_taken FROM attacks WHERE chat_id=%s AND victim_id=%s",
                (chat_id, user_id),
                fetch="one_dict"
            )
            
            return {
                'total_attacks': attack_stats.get('total_attacks', 0) if attack_stats else 0,
                'total_damage_dealt': attack_stats.get('total_damage_dealt', 0) if attack_stats else 0,
                'times_attacked': defense_stats.get('times_attacked', 0) if defense_stats else 0,
                'total_damage_taken': defense_stats.get('total_damage_taken', 0) if defense_stats else 0
            }
        except Exception as e:
            logger.error(f"Error getting combat statistics: {e}")
            return {'total_attacks': 0, 'times_attacked': 0, 'total_damage_dealt': 0, 'total_damage_taken': 0}
    
    async def get_player_rank(self, chat_id: int, user_id: int) -> Dict[str, int]:
        """Get player rank in chat"""
        try:
            rank_data = await self.db_manager.db(
                "SELECT COUNT(*) + 1 as rank FROM players WHERE chat_id=%s AND score > (SELECT score FROM players WHERE chat_id=%s AND user_id=%s)",
                (chat_id, chat_id, user_id),
                fetch="one_dict"
            )
            
            total_players = await self.db_manager.db(
                "SELECT COUNT(*) as total FROM players WHERE chat_id=%s",
                (chat_id,),
                fetch="one_dict"
            )
            
            return {
                'rank': rank_data.get('rank', 0) if rank_data else 0,
                'total_players': total_players.get('total', 0) if total_players else 0
            }
        except Exception as e:
            logger.error(f"Error getting player rank: {e}")
            return {'rank': 0, 'total_players': 0}
    
    async def get_activity_statistics(self, chat_id: int, user_id: int) -> Dict[str, Any]:
        """Get activity-related statistics"""
        try:
            # Calculate days since registration
            player_data = await self.db_manager.db(
                "SELECT created_at FROM players WHERE chat_id=%s AND user_id=%s",
                (chat_id, user_id),
                fetch="one_dict"
            )
            
            if player_data and player_data['created_at']:
                # Calculate days since join (timestamps are in seconds)
                seconds_since_join = helpers.now() - player_data['created_at']
                days_since_join = max(1, seconds_since_join // 86400)  # 86400 seconds in a day
            else:
                days_since_join = 1
            
            # Get last activity (most recent attack)
            last_activity = await self.db_manager.db(
                "SELECT MAX(attack_time) as last_active FROM attacks WHERE chat_id=%s AND attacker_id=%s",
                (chat_id, user_id),
                fetch="one_dict"
            )
            
            last_active_time = last_activity.get('last_active') if last_activity else helpers.now()
            
            return {
                'days_active': max(1, days_since_join),
                'last_active': last_active_time or helpers.now()
            }
        except Exception as e:
            logger.error(f"Error getting activity statistics: {e}")
            return {'days_active': 1, 'last_active': helpers.now()}
    
    async def get_active_defense(self, chat_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get active defense information with enhanced details"""
        try:
            defense = await self.db_manager.db(
                "SELECT defense_type, expires_at, activated_at FROM active_defenses WHERE chat_id=%s AND user_id=%s AND expires_at > %s ORDER BY expires_at DESC LIMIT 1",
                (chat_id, user_id, helpers.now()), 
                fetch="one_dict"
            )
            
            if defense:
                remaining_seconds = max(0, defense['expires_at'] - helpers.now())
                defense['remaining_minutes'] = remaining_seconds // 60
                defense['remaining_hours'] = remaining_seconds // 3600
                
            return defense
        except Exception as e:
            logger.error(f"Error getting active defense: {e}")
            return None
    
    async def get_active_boosts(self, chat_id: int, user_id: int) -> List[Dict[str, Any]]:
        """Get active temporary boosts"""
        try:
            boosts = await self.db_manager.db(
                """SELECT boost_type, boost_value, expires_at, activated_at 
                   FROM active_boosts 
                   WHERE chat_id=%s AND user_id=%s AND expires_at > %s 
                   ORDER BY expires_at DESC""",
                (chat_id, user_id, helpers.now()),
                fetch="all_dicts"
            )
            
            enhanced_boosts = []
            for boost in (boosts or []):
                remaining_seconds = max(0, boost['expires_at'] - helpers.now())
                boost_name = {
                    'cooldown_reduction': '⚡ Cooldown Reduction',
                    'experience_multiplier': '📈 Experience Boost',
                    'vip_experience': '⭐ VIP Experience',
                    'vip_damage': '⚔️ VIP Damage',
                    'vip_cooldown': '🔥 VIP Cooldown'
                }.get(boost['boost_type'], boost['boost_type'])
                
                enhanced_boosts.append({
                    'type': boost['boost_type'],
                    'name': boost_name,
                    'value': boost['boost_value'],
                    'remaining_minutes': remaining_seconds // 60,
                    'remaining_hours': remaining_seconds // 3600,
                    'expires_at': boost['expires_at']
                })
            
            return enhanced_boosts
        except Exception as e:
            logger.error(f"Error getting active boosts: {e}")
            return []
    
    async def get_defense_items(self, chat_id: int, user_id: int) -> List[Dict[str, Any]]:
        """Get available defense items with detailed information"""
        try:
            defense_items = await self.db_manager.db(
                "SELECT item, qty FROM inventories WHERE chat_id=%s AND user_id=%s AND item IN ('shield', 'intercept', 'super_aegis') AND qty > 0",
                (chat_id, user_id), 
                fetch="all_dicts"
            )
            
            enhanced_items = []
            for item in (defense_items or []):
                item_id = item['item']
                item_details = ITEMS.get(item_id, {})
                
                enhanced_items.append({
                    'id': item_id,
                    'quantity': item['qty'],
                    'name': get_item_display_name(item_id),
                    'emoji': get_item_emoji(item_id),
                    'duration_hours': item_details.get('duration_seconds', 3600) // 3600,
                    'effectiveness': item_details.get('effectiveness', 'Standard')
                })
            
            return enhanced_items
        except Exception as e:
            logger.error(f"Error getting defense items: {e}")
            return []
    
    async def get_inventory_summary(self, chat_id: int, user_id: int) -> Dict[str, Any]:
        """Get comprehensive inventory summary"""
        try:
            inventory_data = await self.db_manager.db(
                "SELECT COUNT(DISTINCT item) as unique_items, SUM(qty) as total_items FROM inventories WHERE chat_id=%s AND user_id=%s AND qty > 0",
                (chat_id, user_id),
                fetch="one_dict"
            )
            
            weapons_count = await self.db_manager.db(
                "SELECT COALESCE(SUM(qty), 0) as weapons FROM inventories WHERE chat_id=%s AND user_id=%s AND item IN ('f22', 'moab', 'nuclear', 'carrier', 'stealth_bomber', 'mega_nuke') AND qty > 0",
                (chat_id, user_id),
                fetch="one_dict"
            )
            
            defense_count = await self.db_manager.db(
                "SELECT COALESCE(SUM(qty), 0) as defense FROM inventories WHERE chat_id=%s AND user_id=%s AND item IN ('shield', 'intercept', 'super_aegis') AND qty > 0",
                (chat_id, user_id),
                fetch="one_dict"
            )
            
            return {
                'unique_items': inventory_data.get('unique_items', 0) if inventory_data else 0,
                'total_items': inventory_data.get('total_items', 0) if inventory_data else 0,
                'weapons_count': weapons_count.get('weapons', 0) if weapons_count else 0,
                'defense_count': defense_count.get('defense', 0) if defense_count else 0
            }
        except Exception as e:
            logger.error(f"Error getting inventory summary: {e}")
            return {'unique_items': 0, 'total_items': 0, 'weapons_count': 0, 'defense_count': 0}
    
    async def check_item_availability(self, chat_id: int, user_id: int, item_id: str) -> bool:
        """Check if user has the specified item"""
        try:
            inventory = await self.db_manager.db(
                "SELECT qty FROM inventories WHERE chat_id=%s AND user_id=%s AND item=%s",
                (chat_id, user_id, item_id), 
                fetch="one_dict"
            )
            return inventory and inventory['qty'] > 0
        except Exception as e:
            logger.error(f"Error checking item availability: {e}")
            return False
    
    async def has_active_defense(self, chat_id: int, user_id: int) -> bool:
        """Check if user has an active defense"""
        try:
            active_defense = await self.db_manager.db(
                "SELECT 1 FROM active_defenses WHERE chat_id=%s AND user_id=%s AND expires_at > %s",
                (chat_id, user_id, helpers.now()), 
                fetch="one"
            )
            return bool(active_defense)
        except Exception as e:
            logger.error(f"Error checking active defense: {e}")
            return False
    
    async def activate_defense(self, chat_id: int, user_id: int, item_id: str) -> bool:
        """Activate a defense item with enhanced functionality"""
        try:
            # Deactivate any existing defense first
            await self.db_manager.db(
                "DELETE FROM active_defenses WHERE chat_id=%s AND user_id=%s",
                (chat_id, user_id)
            )
            
            # Use one item
            await self.db_manager.db(
                "UPDATE inventories SET qty = qty - 1 WHERE chat_id=%s AND user_id=%s AND item=%s",
                (chat_id, user_id, item_id)
            )
            
            # Get item details
            item_details = ITEMS.get(item_id, {})
            duration = item_details.get('duration_seconds', 3600)
            expires_at = helpers.now() + duration
            
            # Activate defense
            await self.db_manager.db(
                "INSERT INTO active_defenses (chat_id, user_id, defense_type, expires_at, activated_at) VALUES (%s, %s, %s, %s, %s)",
                (chat_id, user_id, item_id, expires_at, helpers.now())
            )
            
            return True
        except Exception as e:
            logger.error(f"Error activating defense: {e}")
            return False
    
    async def calculate_status_score(self, player_data: Dict[str, Any]) -> int:
        """Calculate overall status score for comparison"""
        try:
            combat_stats = player_data.get('combat_stats', {})
            rank_info = player_data.get('rank_info', {})
            
            # Base score components
            level_score = player_data.get('level', 1) * 100
            medals_score = min(player_data.get('score', 0) // 10, 1000)  # Cap at 1000
            hp_score = player_data.get('hp', 100)
            
            # Combat effectiveness
            attacks = combat_stats.get('total_attacks', 0)
            damage_dealt = combat_stats.get('total_damage_dealt', 0)
            combat_score = min((attacks * 10) + (damage_dealt // 100), 500)  # Cap at 500
            
            # Rank bonus (higher rank = lower number = higher bonus)
            total_players = rank_info.get('total_players', 1)
            rank = rank_info.get('rank', total_players)
            rank_score = max(0, ((total_players - rank) / total_players) * 200) if total_players > 0 else 0
            
            return int(level_score + medals_score + hp_score + combat_score + rank_score)
        except Exception as e:
            logger.error(f"Error calculating status score: {e}")
            return 0

async def handle_status_callback(call: types.CallbackQuery, bot: AsyncTeleBot, db_manager: DBManager) -> None:
    """Enhanced callback handler for status interactions"""
    try:
        lang = await helpers.get_lang(call.message.chat.id, call.from_user.id, db_manager)
        data_parts = call.data.split(':')
        action = data_parts[1] if len(data_parts) > 1 else 'main'

        if action == 'close':
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            await bot.answer_callback_query(call.id)
            return
        
        if action == 'refresh':
            await send_status_message(call.message, bot, db_manager, call.from_user, lang, edit=True)
            await bot.answer_callback_query(call.id, T[lang].get('refresh_status', {}))
            return
        
        if action == 'detailed':
            await send_detailed_status(call.message, bot, db_manager, call.from_user, lang, edit=True)
            await bot.answer_callback_query(call.id)
            return
        
        if action == 'quick':
            await send_status_message(call.message, bot, db_manager, call.from_user, lang, edit=True)
            await bot.answer_callback_query(call.id)
            return

        # Handle defense activation
        item_id = action
        item_details = ITEMS.get(item_id)
        
        # Validate item
        if not item_details or item_details.get('type') != ItemType.SHIELD.value:
            await bot.answer_callback_query(
                call.id, 
                T[lang].get('item_not_found', {}), 
                show_alert=True
            )
            return

        status_manager = StatusManager(db_manager)
        
        # Check if player has the item
        if not await status_manager.check_item_availability(call.message.chat.id, call.from_user.id, item_id):
            await bot.answer_callback_query(
                call.id, 
                T[lang].get('item_not_owned', {}).format(item_name=T[lang].get('items', {}).get(item_id, item_id)), 
                show_alert=True
            )
            return

        # Check if a defense is already active
        if await status_manager.has_active_defense(call.message.chat.id, call.from_user.id):
            await bot.answer_callback_query(
                call.id, 
                T[lang].get('defense_already_active', {}), 
                show_alert=True
            )
            return

        # Activate defense
        if await status_manager.activate_defense(call.message.chat.id, call.from_user.id, item_id):
            item_name = T[lang].get('items', {}).get(item_id, item_id)
            duration_hours = item_details.get('duration_seconds', 3600) // 3600
            await bot.answer_callback_query(
                call.id, 
                T[lang].get('defense_activated', {}).format(item_name=item_name, hours=duration_hours), 
                show_alert=True
            )

            # Refresh the status message
            await send_status_message(call.message, bot, db_manager, call.from_user, lang, edit=True)
        else:
            await bot.answer_callback_query(
                call.id, 
                "Error activating defense. Please try again.", 
                show_alert=True
            )

    except Exception as e:
        logger.error(f"Error handling status callback: {e}")
        await bot.answer_callback_query(call.id, "An error occurred.", show_alert=True)

async def send_status_message(message: types.Message, bot: AsyncTeleBot, db_manager: DBManager, 
                             user: types.User, lang: str, edit: bool = False) -> None:
    """Send comprehensive status message with enhanced analytics"""
    try:
        status_manager = StatusManager(db_manager)
        
        # Get comprehensive player data
        player_data = await status_manager.get_comprehensive_player_data(message.chat.id, user.id)
        
        # Get active defense
        active_defense = await status_manager.get_active_defense(message.chat.id, user.id)
        
        # Get active boosts
        active_boosts = await status_manager.get_active_boosts(message.chat.id, user.id)
        
        # Get inventory summary
        inventory_summary = await status_manager.get_inventory_summary(message.chat.id, user.id)
        
        # Format defense status
        defense_text = T[lang].get('defense_status_none', {})
        if active_defense:
            item_name = T[lang].get('items', {}).get(active_defense['defense_type'], active_defense['defense_type'])
            remaining_time = active_defense.get('remaining_minutes', 0)
            defense_text = T[lang].get('defense_status_active', {}).format(
                item_name=item_name, 
                time_left=max(0, remaining_time)
            )

        # Format comprehensive status message
        combat_stats = player_data.get('combat_stats', {})
        rank_info = player_data.get('rank_info', {})
        activity_stats = player_data.get('activity_stats', {})
        
        # Calculate efficiency metrics
        total_attacks = combat_stats.get('total_attacks', 0)
        damage_dealt = combat_stats.get('total_damage_dealt', 0)
        avg_damage = (damage_dealt / total_attacks) if total_attacks > 0 else 0
        
        status_text = T[lang].get('status_message', {}).format(
            first_name=user.first_name or "Unknown",
            medals=player_data.get('score', 0),
            tg_stars=player_data.get('tg_stars', 0),
            hp=player_data.get('hp', 100),
            level=player_data.get('level', 1),
            defense_status=defense_text
        )
        
    # Add analytics section
        if lang == "fa":
            # Format active boosts
            boosts_text = ""
            if active_boosts:
                boosts_text = "\n🚀 <b>تقویت‌های فعال:</b>\n"
                for boost in active_boosts:
                    hours = boost['remaining_hours']
                    minutes = boost['remaining_minutes'] % 60
                    time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                    
                    if boost['type'] in ['cooldown_reduction', 'vip_cooldown']:
                        value_str = f"{int(boost['value'] * 100)}% کاهش"
                    elif boost['type'] in ['experience_multiplier', 'vip_experience']:
                        value_str = f"x{boost['value']:.1f}"
                    elif boost['type'] == 'vip_damage':
                        value_str = f"+{int(boost['value'] * 100)}% آسیب"
                    else:
                        value_str = f"{boost['value']:.1f}"
                    
                    boosts_text += f"• {boost['name']}: {value_str} ({time_str})\n"
                    
            analytics_text = f"""
📊 <b>تحلیل‌های عملکرد:</b>
• رتبه در چت: #{rank_info.get('rank', 0)} از {rank_info.get('total_players', 0)}
• کل حملات انجام شده: {total_attacks:,}
• متوسط آسیب هر حمله: {avg_damage:.1f}
• تعداد دفعات هدف قرار گرفتن: {combat_stats.get('times_attacked', 0):,}

📦 <b>خلاصه انبار:</b>
• تسلیحات: {inventory_summary.get('weapons_count', 0)}
• آیتم‌های دفاعی: {inventory_summary.get('defense_count', 0)}
• کل آیتم‌ها: {inventory_summary.get('total_items', 0)}

⏱️ <b>فعالیت:</b>
• روزهای بازی: {activity_stats.get('days_active', 0)}{boosts_text}
            """
        else:
            # Format active boosts for English
            boosts_text = ""
            if active_boosts:
                boosts_text = "\n🚀 <b>Active Boosts:</b>\n"
                for boost in active_boosts:
                    hours = boost['remaining_hours']
                    minutes = boost['remaining_minutes'] % 60
                    time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                    
                    if boost['type'] in ['cooldown_reduction', 'vip_cooldown']:
                        value_str = f"{int(boost['value'] * 100)}% reduction"
                    elif boost['type'] in ['experience_multiplier', 'vip_experience']:
                        value_str = f"x{boost['value']:.1f}"
                    elif boost['type'] == 'vip_damage':
                        value_str = f"+{int(boost['value'] * 100)}% damage"
                    else:
                        value_str = f"{boost['value']:.1f}"
                    
                    boosts_text += f"• {boost['name']}: {value_str} ({time_str})\n"
                    
            analytics_text = f"""
📊 <b>Performance Analytics:</b>
• Chat Rank: #{rank_info.get('rank', 0)} of {rank_info.get('total_players', 0)}
• Total Attacks Made: {total_attacks:,}
• Average Damage per Attack: {avg_damage:.1f}
• Times Targeted: {combat_stats.get('times_attacked', 0):,}

📦 <b>Inventory Summary:</b>
• Weapons: {inventory_summary.get('weapons_count', 0)}
• Defense Items: {inventory_summary.get('defense_count', 0)}
• Total Items: {inventory_summary.get('total_items', 0)}

⏱️ <b>Activity:</b>
• Days Playing: {activity_stats.get('days_active', 0)}{boosts_text}
            """
        
        full_status_text = status_text + analytics_text

        # Create enhanced keyboard
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        
        # Defense activation buttons
        defense_items = await status_manager.get_defense_items(message.chat.id, user.id)
        if defense_items and not await status_manager.has_active_defense(message.chat.id, user.id):
            # Add a header for defense items
            defense_header = T[lang].get('activate_defense_header', '🛡️ Activate Defense:')
            full_status_text += f"\n\n<b>{defense_header}</b>"
            
            for item in defense_items:
                button_text = T[lang].get('activate_button', 'Use {item_name}').format(
                    item_name=item['name']
                )
                keyboard.add(types.InlineKeyboardButton(
                    f"{item['emoji']} {button_text} ({item['quantity']})", 
                    callback_data=f"status:{item['id']}"
                ))
        elif await status_manager.has_active_defense(message.chat.id, user.id):
            # Add info about active defense
            full_status_text += f"\n\n<b>🛡️ {T[lang].get('active_defense_info', 'You have an active defense!')}</b>"
        else:
            # No defense items available
            full_status_text += f"\n\n<b>⚠️ {T[lang].get('no_defense_items', 'You have no defense items. Buy some in the shop!')}</b>"
        
        # Navigation buttons
        detailed_btn = types.InlineKeyboardButton(
            f"📊 {T[lang].get('view_detailed_status', 'Detailed')}", 
            callback_data="status:detailed"
        )
        refresh_btn = types.InlineKeyboardButton(
            f"🔄 {T[lang].get('refresh_status', 'Refresh')}", 
            callback_data="status:refresh"
        )
        keyboard.add(detailed_btn, refresh_btn)
        
        # Add shop button for buying defenses
        shop_btn = types.InlineKeyboardButton(
            f"🛒 {T[lang].get('shop_button', 'Shop')}", 
            callback_data="shop:defense"
        )
        inventory_btn = types.InlineKeyboardButton(
            f"📦 {T[lang].get('inventory_button', 'Inventory')}", 
            callback_data="inventory:main"
        )
        keyboard.add(shop_btn, inventory_btn)
        
        # Close button
        keyboard.add(types.InlineKeyboardButton(
            T[lang].get('close_button', 'Close'), 
            callback_data="status:close"
        ))

        # Send or edit message
        if edit:
            await bot.edit_message_text(
                full_status_text, 
                message.chat.id, 
                message.message_id, 
                reply_markup=keyboard, 
                parse_mode="HTML"
            )
        else:
            await bot.send_message(
                message.chat.id, 
                full_status_text, 
                reply_markup=keyboard, 
                parse_mode="HTML"
            )

    except Exception as e:
        logger.error(f"Error sending status message: {e}")
        error_msg = "Error displaying status. Please try again."
        if edit:
            await bot.edit_message_text(error_msg, message.chat.id, message.message_id)
        else:
            await bot.send_message(message.chat.id, error_msg)

async def send_detailed_status(message: types.Message, bot: AsyncTeleBot, db_manager: DBManager, 
                              user: types.User, lang: str, edit: bool = False) -> None:
    """Send detailed status with comprehensive analytics"""
    try:
        status_manager = StatusManager(db_manager)
        
        # Get comprehensive player data
        player_data = await status_manager.get_comprehensive_player_data(message.chat.id, user.id)
        
        # Calculate status score
        status_score = await status_manager.calculate_status_score(player_data)
        
        combat_stats = player_data.get('combat_stats', {})
        rank_info = player_data.get('rank_info', {})
        activity_stats = player_data.get('activity_stats', {})
        
        # Calculate advanced metrics
        total_attacks = combat_stats.get('total_attacks', 0)
        times_attacked = combat_stats.get('times_attacked', 0)
        damage_dealt = combat_stats.get('total_damage_dealt', 0)
        damage_taken = combat_stats.get('total_damage_taken', 0)
        
        survival_rate = ((times_attacked - combat_stats.get('deaths', 0)) / times_attacked * 100) if times_attacked > 0 else 100
        damage_efficiency = (damage_dealt / damage_taken) if damage_taken > 0 else float('inf') if damage_dealt > 0 else 0
        
        if lang == "fa":
            detailed_text = f"""
    🎯 <b>وضعیت تفصیلی {user.first_name or 'Unknown'}</b>

    📊 <b>امتیاز کلی وضعیت:</b> {status_score:,}

    🏆 <b>آمار رتبه‌بندی:</b>
    • رتبه فعلی: #{rank_info.get('rank', 0)} از {rank_info.get('total_players', 0)}
    • درصد رتبه: {((rank_info.get('total_players', 1) - rank_info.get('rank', 0)) / rank_info.get('total_players', 1) * 100):.1f}%

    ⚔️ <b>تحلیل‌های نبرد پیشرفته:</b>
    • کل حملات: {total_attacks:,}
    • کل آسیب وارد شده: {damage_dealt:,}
    • متوسط آسیب هر حمله: {(damage_dealt / total_attacks):.1f} (اگر > 0)
    • نرخ بقا: {survival_rate:.1f}%
    • کارایی آسیب: {damage_efficiency:.2f}

    📈 <b>رونده‌های عملکرد:</b>
    • میانگین حمله روزانه: {(total_attacks / activity_stats.get('days_active', 1)):.1f}
    • میانگین آسیب روزانه: {(damage_dealt / activity_stats.get('days_active', 1)):.1f}

    💰 <b>منابع:</b>
    • مدال‌ها: {player_data.get('score', 0):,}
    • ستاره‌های تلگرام: {player_data.get('tg_stars', 0)}
    • نرخ کسب مدال: {(player_data.get('score', 0) / total_attacks):.1f} (اگر > 0)

    ❤️ <b>وضعیت سلامت:</b>
    • HP فعلی: {player_data.get('hp', 100)}/100
    • سطح: {player_data.get('level', 1)}
    • پیشرفت تا سطح بعد: در حال محاسبه...
            """
        else:
            detailed_text = f"""
    🎯 <b>Detailed Status for {user.first_name or 'Unknown'}</b>

    📊 <b>Overall Status Score:</b> {status_score:,}

    🏆 <b>Ranking Statistics:</b>
    • Current Rank: #{rank_info.get('rank', 0)} of {rank_info.get('total_players', 0)}
    • Percentile: {((rank_info.get('total_players', 1) - rank_info.get('rank', 0)) / rank_info.get('total_players', 1) * 100):.1f}%

    ⚔️ <b>Advanced Combat Analytics:</b>
    • Total Attacks: {total_attacks:,}
    • Total Damage Dealt: {damage_dealt:,}
    • Average Damage per Attack: {(damage_dealt / total_attacks):.1f} (if > 0)
    • Survival Rate: {survival_rate:.1f}%
    • Damage Efficiency: {damage_efficiency:.2f}

    📈 <b>Performance Trends:</b>
    • Average Attacks per Day: {(total_attacks / activity_stats.get('days_active', 1)):.1f}
    • Average Damage per Day: {(damage_dealt / activity_stats.get('days_active', 1)):.1f}

    💰 <b>Resources:</b>
    • Medals: {player_data.get('score', 0):,}
    • TG Stars: {player_data.get('tg_stars', 0)}
    • Medal Earn Rate: {(player_data.get('score', 0) / total_attacks):.1f} (if > 0)

    ❤️ <b>Health Status:</b>
    • Current HP: {player_data.get('hp', 100)}/100
    • Level: {player_data.get('level', 1)}
    • Progress to Next Level: Calculating...
            """
        
        # Create simplified keyboard for detailed view
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        
        quick_btn = types.InlineKeyboardButton(
            f"⚡ {T[lang].get('quick_status', {})}", 
            callback_data="status:quick"
        )
        refresh_btn = types.InlineKeyboardButton(
            f"🔄 {T[lang].get('refresh_status', {})}", 
            callback_data="status:refresh"
        )
        keyboard.add(quick_btn, refresh_btn)
        
        keyboard.add(types.InlineKeyboardButton(
            T[lang].get('close_button', {}), 
            callback_data="status:close"
        ))

        # Send or edit message
        if edit:
            await bot.edit_message_text(
                detailed_text, 
                message.chat.id, 
                message.message_id, 
                reply_markup=keyboard, 
                parse_mode="HTML"
            )
        else:
            await bot.send_message(
                message.chat.id, 
                detailed_text, 
                reply_markup=keyboard, 
                parse_mode="HTML"
            )

    except Exception as e:
        logger.error(f"Error sending detailed status: {e}")
        error_msg = "Error displaying detailed status. Please try again."
        if edit:
            await bot.edit_message_text(error_msg, message.chat.id, message.message_id)
        else:
            await bot.send_message(message.chat.id, error_msg)

def register_handlers(bot: AsyncTeleBot, db_manager: DBManager) -> None:
    """Registers enhanced command handlers for the status module"""
    group_only = helpers.ensure_group_command(bot, db_manager)

    @bot.message_handler(commands=['status'])
    @group_only
    async def status_command(message: types.Message) -> None:
        """Enhanced status command with comprehensive analytics"""
        try:
            await helpers.ensure_player(message.chat.id, message.from_user, db_manager)
            lang = await helpers.get_lang(message.chat.id, message.from_user.id, db_manager)
            await send_status_message(message, bot, db_manager, message.from_user, lang)
        except Exception as e:
            logger.error(f"Error in status command: {e}")
            await bot.send_message(message.chat.id, "Error displaying status. Please try again.")
    
    @bot.message_handler(commands=['shield', 'defense'])
    @group_only
    async def shield_command(message: types.Message) -> None:
        """Shortcut command to activate shields"""
        try:
            await helpers.ensure_player(message.chat.id, message.from_user, db_manager)
            lang = await helpers.get_lang(message.chat.id, message.from_user.id, db_manager)
            
            # Check if user already has an active defense
            status_manager = StatusManager(db_manager)
            if await status_manager.has_active_defense(message.chat.id, message.from_user.id):
                await bot.send_message(
                    message.chat.id,
                    T[lang].get('defense_already_active', 'You already have an active defense system!')
                )
                return
                
            # Get available defense items
            defense_items = await status_manager.get_defense_items(message.chat.id, message.from_user.id)
            
            if not defense_items:
                # No defense items - show message with shop link
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(types.InlineKeyboardButton(
                    f"🛒 {T[lang].get('shop_defense_items', 'Buy defense items')}",
                    callback_data="shop:defense"
                ))
                
                await bot.send_message(
                    message.chat.id,
                    T[lang].get('no_defense_items', 'You have no defense items. Buy some in the shop!'),
                    reply_markup=keyboard
                )
                return
                
            # Show defense activation menu
            text = T[lang].get('select_defense_activation', 'Select a defense item to activate:')
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            
            for item in defense_items:
                button_text = T[lang].get('activate_button', 'Use {item_name}').format(
                    item_name=item['name']
                )
                keyboard.add(types.InlineKeyboardButton(
                    f"{item['emoji']} {button_text} ({item['quantity']})", 
                    callback_data=f"status:{item['id']}"
                ))
                
            keyboard.add(types.InlineKeyboardButton(
                T[lang].get('cancel_button', 'Cancel'),
                callback_data="status:close"
            ))
            
            await bot.send_message(
                message.chat.id,
                text,
                reply_markup=keyboard
            )
            
        except Exception as e:
            logger.error(f"Error in shield command: {e}")
            await bot.send_message(message.chat.id, "Error processing defense activation. Please try again.")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('status:'))
    async def status_callback_handler(call: types.CallbackQuery):
        """Enhanced callback handler for status interactions"""
        await handle_status_callback(call, bot, db_manager)

