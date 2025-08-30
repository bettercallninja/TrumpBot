#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Attack commands module
Handles combat mechanics, weapon usage, and damage calculations
"""

import asyncio
import logging
import random
from typing import Optional, Tuple, Dict, Any
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from src.config.bot_config import BotConfig
from src.config.items import ITEMS, get_weapon_items, get_item_display_name, get_item_emoji, is_weapon, get_item_stats
from src.database.db_manager import DBManager
from src.utils import helpers
from src.utils.translations import T

# Set up logging
logger = logging.getLogger(__name__)

class AttackManager:
    """Manages attack mechanics and damage calculations"""
    
    def __init__(self, db_manager: DBManager):
        self.db_manager = db_manager
        self.config = BotConfig()
        
    def calculate_damage(self, weapon: str, attacker_level: int, target_level: int) -> int:
        """Calculate damage based on weapon and level difference"""
        # Get weapon info from items configuration
        weapon_data = ITEMS.get(weapon)
        if not weapon_data or not is_weapon(weapon):
            return 0
        
        base_damage = weapon_data.get("damage", 0)
        if base_damage == 0:
            return 0
        
        # Add variance based on weapon tier
        variance = max(1, base_damage // 4)  # 25% variance
        damage = base_damage + random.randint(-variance, variance)
        
        # Level difference modifier (max 50% reduction to 200% increase)
        level_diff = attacker_level - target_level
        level_modifier = max(0.5, min(1.0 + (level_diff * 0.1), 2.0))
        
        return max(1, int(damage * level_modifier))
    
    async def check_defense(self, target_chat_id: int, target_user_id: int) -> Tuple[bool, Optional[str]]:
        """Check if target has active defense"""
        try:
            defense_row = await self.db_manager.db(
                "SELECT defense_type FROM active_defenses WHERE chat_id=%s AND user_id=%s AND expires_at > %s",
                (target_chat_id, target_user_id, helpers.now()), 
                fetch="one_dict"
            )
            return (True, defense_row['defense_type']) if defense_row else (False, None)
        except Exception as e:
            logger.error(f"Error checking defense: {e}")
            return False, None
    
    async def check_cooldown(self, chat_id: int, user_id: int) -> Optional[int]:
        """Check if user is in attack cooldown"""
        try:
            last_attack = await self.db_manager.db(
                "SELECT MAX(attack_time) as last_attack FROM attacks WHERE chat_id=%s AND attacker_id=%s",
                (chat_id, user_id), 
                fetch="one_dict"
            )
            
            if last_attack and last_attack['last_attack']:
                time_since = helpers.now() - last_attack['last_attack']
                if time_since < self.config.ATTACK_COOLDOWN:
                    return self.config.ATTACK_COOLDOWN - time_since
            return None
        except Exception as e:
            logger.error(f"Error checking cooldown: {e}")
            return None
    
    async def check_weapon_availability(self, chat_id: int, user_id: int, weapon: str) -> bool:
        """Check if user has the specified weapon"""
        # Check if weapon exists and is actually a weapon
        if not is_weapon(weapon):
            return False
            
        # Special case for unlimited missiles
        if self.config.UNLIMITED_MISSILES and weapon == "moab":
            return True
            
        try:
            weapon_qty = await self.db_manager.db(
                "SELECT qty FROM inventories WHERE chat_id=%s AND user_id=%s AND item=%s",
                (chat_id, user_id, weapon), 
                fetch="one_dict"
            )
            return weapon_qty and weapon_qty['qty'] > 0
        except Exception as e:
            logger.error(f"Error checking weapon availability: {e}")
            return False
    
    async def get_available_weapons(self, chat_id: int, user_id: int) -> Dict[str, int]:
        """Get all available weapons for a user"""
        try:
            inventory_rows = await self.db_manager.db(
                "SELECT item, qty FROM inventories WHERE chat_id=%s AND user_id=%s AND qty > 0",
                (chat_id, user_id), 
                fetch="all_dicts"
            )
            
            # Filter only weapons
            weapons = {}
            for row in inventory_rows:
                item_id = row['item']
                if is_weapon(item_id):
                    weapons[item_id] = row['qty']
            
            # Add unlimited missiles if enabled
            if self.config.UNLIMITED_MISSILES:
                weapons['moab'] = float('inf')
            
            return weapons
        except Exception as e:
            logger.error(f"Error getting available weapons: {e}")
            return {}
    
    def calculate_medal_reward(self, weapon: str, is_defeat: bool = False) -> int:
        """Calculate medal reward based on weapon and outcome"""
        weapon_data = ITEMS.get(weapon, {})
        base_reward = 1
        
        # Weapon-specific bonuses
        if weapon == "f22":
            base_reward = 2
        elif weapon in ["nuclear", "mega_nuke", "stealth_bomber"]:
            base_reward = 3
        elif weapon == "moab":
            base_reward = 2
        
        # Premium weapon bonus
        if weapon_data.get("payment") == "tg_stars":
            base_reward += 1
        
        # Defeat bonus
        if is_defeat:
            base_reward += 5
        
        return base_reward
    
    async def get_battle_stats(self, chat_id: int, user_id: int) -> Dict[str, Any]:
        """Get comprehensive battle statistics for a user"""
        try:
            # Get attack stats
            attack_stats = await self.db_manager.db(
                "SELECT COUNT(*) as total_attacks, SUM(damage) as total_damage, AVG(damage) as avg_damage FROM attacks WHERE chat_id=%s AND attacker_id=%s",
                (chat_id, user_id),
                fetch="one_dict"
            )
            
            # Get defense stats (times attacked)
            defense_stats = await self.db_manager.db(
                "SELECT COUNT(*) as times_attacked, SUM(damage) as damage_taken FROM attacks WHERE chat_id=%s AND victim_id=%s",
                (chat_id, user_id),
                fetch="one_dict"
            )
            
            # Get weapon usage stats
            weapon_usage = await self.db_manager.db(
                "SELECT weapon, COUNT(*) as usage_count FROM attacks WHERE chat_id=%s AND attacker_id=%s GROUP BY weapon ORDER BY usage_count DESC",
                (chat_id, user_id),
                fetch="all_dicts"
            )
            
            return {
                "attacks": {
                    "total": attack_stats.get('total_attacks', 0),
                    "total_damage": attack_stats.get('total_damage', 0),
                    "avg_damage": round(attack_stats.get('avg_damage', 0), 1)
                },
                "defense": {
                    "times_attacked": defense_stats.get('times_attacked', 0),
                    "damage_taken": defense_stats.get('damage_taken', 0)
                },
                "weapons": weapon_usage[:5]  # Top 5 most used weapons
            }
        except Exception as e:
            logger.error(f"Error getting battle stats: {e}")
            return {"attacks": {"total": 0, "total_damage": 0, "avg_damage": 0}, "defense": {"times_attacked": 0, "damage_taken": 0}, "weapons": []}

async def show_weapon_comparison(message: types.Message, bot: AsyncTeleBot, db_manager: DBManager, lang: str) -> None:
    """Show weapon comparison table"""
    try:
        weapons = get_weapon_items()
        
        if not weapons:
            await bot.send_message(message.chat.id, "No weapons available for comparison.")
            return
        
        text = f"⚔️ **{T.get('weapon_comparison_title', {}).get(lang, 'Weapon Comparison')}**\n\n"
        text += "```\n"
        text += f"{'Weapon':<15} {'DMG':<4} {'⭐':<2} {'Type':<8}\n"
        text += "─" * 35 + "\n"
        
        # Sort weapons by damage
        sorted_weapons = []
        for weapon_id, weapon_data in weapons.items():
            stats = get_item_stats(weapon_id)
            sorted_weapons.append((weapon_id, stats))
        
        sorted_weapons.sort(key=lambda x: x[1].get('damage', 0), reverse=True)
        
        for weapon_id, stats in sorted_weapons:
            name = stats['name'][:12]  # Truncate long names
            damage = stats.get('damage', 0)
            stars = stats.get('stars', 0)
            payment_type = "⭐" if stats.get('payment') == 'tg_stars' else "🏅"
            
            text += f"{name:<15} {damage:<4} {stars:<2} {payment_type:<8}\n"
        
        text += "```\n"
        text += f"🏅 = {T.get('medals', {}).get(lang, 'Medals')} | ⭐ = {T.get('tg_stars', {}).get(lang, 'TG Stars')}"
        
        await bot.send_message(message.chat.id, text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error showing weapon comparison: {e}")
async def show_battle_stats(message: types.Message, bot: AsyncTeleBot, db_manager: DBManager, lang: str) -> None:
    """Show user's battle statistics"""
    try:
        attack_manager = AttackManager(db_manager)
        stats = await attack_manager.get_battle_stats(message.chat.id, message.from_user.id)
        
        text = f"📊 **{T.get('battle_stats_title', {}).get(lang, 'Battle Statistics')}**\n\n"
        
        # Attack stats
        attack_stats = stats['attacks']
        text += f"⚔️ **{T.get('attack_stats', {}).get(lang, 'Attack Statistics')}:**\n"
        text += f"• {T.get('total_attacks', {}).get(lang, 'Total Attacks')}: {attack_stats['total']}\n"
        text += f"• {T.get('total_damage', {}).get(lang, 'Total Damage')}: {attack_stats['total_damage']}\n"
        text += f"• {T.get('avg_damage', {}).get(lang, 'Average Damage')}: {attack_stats['avg_damage']}\n\n"
        
        # Defense stats
        defense_stats = stats['defense']
        text += f"🛡️ **{T.get('defense_stats', {}).get(lang, 'Defense Statistics')}:**\n"
        text += f"• {T.get('times_attacked', {}).get(lang, 'Times Attacked')}: {defense_stats['times_attacked']}\n"
        text += f"• {T.get('damage_taken', {}).get(lang, 'Damage Taken')}: {defense_stats['damage_taken']}\n\n"
        
        # Top weapons
        if stats['weapons']:
            text += f"🏆 **{T.get('top_weapons', {}).get(lang, 'Most Used Weapons')}:**\n"
            for i, weapon_data in enumerate(stats['weapons'], 1):
                weapon_name = get_item_display_name(weapon_data['weapon'], lang)
                usage_count = weapon_data['usage_count']
                text += f"{i}. {weapon_name}: {usage_count} {T.get('uses', {}).get(lang, 'uses')}\n"
        
        await bot.send_message(message.chat.id, text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error showing battle stats: {e}")
        await bot.send_message(message.chat.id, "Error displaying battle statistics.")
    
    async def get_user_level(self, chat_id: int, user_id: int) -> int:
        """Get user level with fallback"""
        try:
            user_info = await self.db_manager.db(
                "SELECT level FROM players WHERE chat_id=%s AND user_id=%s",
                (chat_id, user_id), 
                fetch="one_dict"
            )
            return user_info['level'] if user_info else 1
        except Exception as e:
            logger.error(f"Error getting user level: {e}")
            return 1

async def show_attack_menu(message: types.Message, bot: AsyncTeleBot, db_manager: DBManager, lang: str) -> None:
    """Shows the attack menu with available weapons"""
    try:
        attack_manager = AttackManager(db_manager)
        weapons = await attack_manager.get_available_weapons(message.chat.id, message.from_user.id)
        
        if not weapons:
            await bot.send_message(
                message.chat.id, 
                T.get('no_weapons_available', {}).get(lang, "You don't have any weapons available!")
            )
            return

        text = T.get('attack_menu_title', {}).get(lang, "🚀 **Choose your weapon:**")
        markup = types.InlineKeyboardMarkup(row_width=1)

        # Sort weapons by damage for better UX
        sorted_weapons = []
        for weapon_id, qty in weapons.items():
            weapon_stats = get_item_stats(weapon_id)
            sorted_weapons.append((weapon_id, qty, weapon_stats.get('damage', 0)))
        
        sorted_weapons.sort(key=lambda x: x[2], reverse=True)  # Sort by damage, highest first

        for weapon_id, qty, damage in sorted_weapons:
            weapon_name = get_item_display_name(weapon_id, lang)
            emoji = get_item_emoji(weapon_id)
            
            # Format quantity display
            qty_text = "∞" if qty == float('inf') else str(qty)
            
            button_text = f"{emoji} {weapon_name} ({damage}💥) x{qty_text}"
            markup.add(types.InlineKeyboardButton(
                button_text, 
                callback_data=f"attack:{weapon_id}:inventory"
            ))
        
        # Add cancel button
        markup.add(types.InlineKeyboardButton(
            T.get('cancel_button', {}).get(lang, "❌ Cancel"),
            callback_data="attack:cancel"
        ))
        
        await bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error showing attack menu: {e}")
        await bot.send_message(message.chat.id, "Error displaying attack menu.")

async def execute_attack(message: types.Message, bot: AsyncTeleBot, db_manager: DBManager, 
                       target_user: types.User, weapon: str, lang: str) -> None:
    """Execute the actual attack"""
    attack_manager = AttackManager(db_manager)
    
    try:
        # Get user levels
        attacker_level = await attack_manager.get_user_level(message.chat.id, message.from_user.id)
        target_level = await attack_manager.get_user_level(message.chat.id, target_user.id)
        
        # Calculate damage
        damage = attack_manager.calculate_damage(weapon, attacker_level, target_level)
        has_defense, defense_type = await attack_manager.check_defense(message.chat.id, target_user.id)
        
        # Apply defense reduction
        final_damage = damage
        if has_defense and defense_type:
            defense_effectiveness = attack_manager.config.DEFENSE_EFFECTIVENESS.get(defense_type, 0)
            final_damage = int(damage * (1 - defense_effectiveness))
        
        # Update target HP
        await db_manager.db(
            "UPDATE players SET hp = GREATEST(0, hp - %s) WHERE chat_id=%s AND user_id=%s",
            (final_damage, message.chat.id, target_user.id)
        )
        
        # Get remaining HP
        remaining_hp_row = await db_manager.db(
            "SELECT hp FROM players WHERE chat_id=%s AND user_id=%s",
            (message.chat.id, target_user.id), 
            fetch="one_dict"
        )
        remaining_hp = remaining_hp_row['hp'] if remaining_hp_row else 0
        
        # Record attack
        await db_manager.db(
            "INSERT INTO attacks (chat_id, attacker_id, victim_id, weapon, damage, attack_time) VALUES (%s, %s, %s, %s, %s, %s)",
            (message.chat.id, message.from_user.id, target_user.id, weapon, final_damage, helpers.now())
        )
        
        # Consume weapon if not unlimited
        if not (attack_manager.config.UNLIMITED_MISSILES and weapon == "moab"):
            await db_manager.db(
                "UPDATE inventories SET qty = qty - 1 WHERE chat_id=%s AND user_id=%s AND item=%s",
                (message.chat.id, message.from_user.id, weapon)
            )
        
        # Award medals with improved calculation
        medal_reward = attack_manager.calculate_medal_reward(weapon, remaining_hp <= 0)
        await db_manager.db(
            "UPDATE players SET score = score + %s WHERE chat_id=%s AND user_id=%s",
            (medal_reward, message.chat.id, message.from_user.id)
        )
        
        # Generate attack report with improved formatting
        weapon_emoji = get_item_emoji(weapon)
        weapon_name = get_item_display_name(weapon, lang)
        weapon_stats = get_item_stats(weapon)
        
        # Create comprehensive attack report
        msg = T.get('attack_report', {}).get(lang, "🎯 **Attack Report**\n").format(
            attacker=message.from_user.first_name or "Unknown",
            target=target_user.first_name or "Unknown",
            emoji=weapon_emoji,
            weapon=weapon_name
        )
        
        # Add weapon stats for premium weapons
        if weapon_stats.get('stars', 0) >= 4:
            msg += f"\n💎 *Premium weapon used*"
        
        if has_defense and defense_type:
            defense_name = T.get('defense_items', {}).get(defense_type, {}).get(lang, defense_type)
            msg += T.get('attack_defended_report', {}).get(lang, "").format(
                target=target_user.first_name or "Unknown", 
                defense=defense_name, 
                original=damage,
                final=final_damage
            )
        else:
            msg += T.get('attack_damage_report', {}).get(lang, "").format(final=final_damage)
            
        msg += T.get('attack_hp_report', {}).get(lang, "").format(
            target=target_user.first_name or "Unknown", 
            hp=remaining_hp
        )
        msg += T.get('attack_medals_report', {}).get(lang, "").format(
            attacker=message.from_user.first_name or "Unknown", 
            medals=medal_reward
        )
        
        # Handle defeat with bonus rewards
        if remaining_hp <= 0:
            await db_manager.db(
                "UPDATE players SET hp = 50 WHERE chat_id=%s AND user_id=%s",
                (message.chat.id, target_user.id)
            )
            msg += T.get('attack_defeat_report', {}).get(lang, "").format(
                target=target_user.first_name or "Unknown"
            )

        # Create enhanced keyboard with multiple options
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        
        # Revenge button
        revenge_btn = types.InlineKeyboardButton(
            T.get('revenge_button', {}).get(lang, "⚔️ Revenge"), 
            callback_data=f"attack:revenge:{message.from_user.id}"
        )
        
        # Show stats button
        stats_btn = types.InlineKeyboardButton(
            T.get('show_stats_button', {}).get(lang, "📊 Stats"),
            callback_data=f"stats:{target_user.id}"
        )
        
        keyboard.add(revenge_btn, stats_btn)
        
        # Add weapon info button for premium weapons
        if weapon_stats.get('payment') == 'tg_stars':
            weapon_info_btn = types.InlineKeyboardButton(
                f"ℹ️ {weapon_name}",
                callback_data=f"weapon_info:{weapon}"
            )
            keyboard.add(weapon_info_btn)
        
        await bot.send_message(message.chat.id, msg, reply_markup=keyboard, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error executing attack: {e}")
        await bot.send_message(message.chat.id, "Error executing attack.")

async def attack_command(message: types.Message, bot: AsyncTeleBot, db_manager: DBManager) -> None:
    """Handle /attack command with improved error handling"""
    try:
        await helpers.ensure_player(message.chat.id, message.from_user, db_manager)
        lang = await helpers.get_lang(message.chat.id, message.from_user.id, db_manager)
        args = helpers.get_args(message)
        
        attack_manager = AttackManager(db_manager)
        target_user = None
        weapon = "moab"

        # Show menu if no arguments
        if not message.reply_to_message and not args:
            await show_attack_menu(message, bot, db_manager, lang)
            return

        # Parse target and weapon
        if message.reply_to_message:
            target_user = message.reply_to_message.from_user
            if args:
                weapon = args[0].lower()
        elif args:
            target_username = args[0].lstrip('@')
            target_data = await db_manager.db(
                "SELECT user_id FROM players WHERE username=%s AND chat_id=%s",
                (target_username, message.chat.id), 
                fetch="one_dict"
            )
            if not target_data:
                await bot.send_message(
                    message.chat.id, 
                    T['target_not_found_error'][lang].format(username=target_username), 
                    parse_mode="HTML"
                )
                return
                
            try:
                target_user = (await bot.get_chat_member(message.chat.id, target_data['user_id'])).user
            except Exception as e:
                logger.error(f"Error getting target user info: {e}")
                await bot.send_message(message.chat.id, T['get_target_info_error'][lang])
                return
                
            if len(args) > 1:
                weapon = args[1].lower()

        # Validate target
        if not target_user:
            await bot.send_message(message.chat.id, T['invalid_target_error'][lang], parse_mode="HTML")
            return

        # Validate weapon
        if not is_weapon(weapon):
            available_weapons = list(get_weapon_items().keys())
            await bot.send_message(
                message.chat.id, 
                T.get('invalid_weapon_error', {}).get(lang, "❌ Invalid weapon!").format(
                    weapon=weapon, 
                    available=", ".join(available_weapons)
                ), 
                parse_mode="Markdown"
            )
            return

        # Check self-attack
        if target_user.id == message.from_user.id:
            await bot.send_message(message.chat.id, T['attack_yourself'][lang])
            return

        # Check weapon availability
        if not await attack_manager.check_weapon_availability(message.chat.id, message.from_user.id, weapon):
            weapon_name = get_item_display_name(weapon, lang)
            await bot.send_message(
                message.chat.id, 
                T.get('no_weapon_error', {}).get(lang, "❌ You don't have this weapon!").format(
                    weapon_name=weapon_name
                ), 
                parse_mode="Markdown"
            )
            return

        # Check cooldown
        wait_time = await attack_manager.check_cooldown(message.chat.id, message.from_user.id)
        if wait_time is not None:
            await bot.send_message(
                message.chat.id, 
                T['attack_cooldown_error'][lang].format(wait_time=wait_time)
            )
            return

        # Ensure target player exists
        await helpers.ensure_player(message.chat.id, target_user, db_manager)
        
        # Execute attack
        await execute_attack(message, bot, db_manager, target_user, weapon, lang)
        
    except Exception as e:
        logger.error(f"Error in attack command: {e}")
        await bot.send_message(message.chat.id, "An error occurred while processing your attack.")

async def handle_attack_callback(call: types.CallbackQuery, bot: AsyncTeleBot, db_manager: DBManager) -> None:
    """Handle attack-related callback queries"""
    try:
        data_parts = call.data.split(':')
        action = data_parts[1] if len(data_parts) > 1 else ""
        
        lang = await helpers.get_lang(call.message.chat.id, call.from_user.id, db_manager)
        
        if action == "cancel":
            await bot.edit_message_text(
                T.get('attack_cancelled', {}).get(lang, "❌ Attack cancelled."),
                call.message.chat.id,
                call.message.message_id
            )
            await bot.answer_callback_query(call.id)
            return
        
        elif action == "revenge":
            if len(data_parts) > 2:
                target_user_id = int(data_parts[2])
                # Create a fake message for attack processing
                fake_message = types.Message(
                    message_id=call.message.message_id,
                    from_user=call.from_user,
                    date=call.message.date,
                    chat=call.message.chat,
                    content_type='text',
                    options={},
                    json_string=""
                )
                fake_message.text = "/attack"
                
                # Get target user info
                try:
                    target_member = await bot.get_chat_member(call.message.chat.id, target_user_id)
                    target_user = target_member.user
                    
                    # Create reply_to_message simulation
                    fake_reply = types.Message(
                        message_id=call.message.message_id - 1,
                        from_user=target_user,
                        date=call.message.date,
                        chat=call.message.chat,
                        content_type='text',
                        options={},
                        json_string=""
                    )
                    fake_message.reply_to_message = fake_reply
                    
                    await attack_command(fake_message, bot, db_manager)
                    
                except Exception as e:
                    logger.error(f"Error in revenge attack: {e}")
                    await bot.answer_callback_query(
                        call.id, 
                        T.get('revenge_error', {}).get(lang, "Error processing revenge attack."),
                        show_alert=True
                    )
                    return
        
        elif action == "weapon_info":
            if len(data_parts) > 2:
                weapon_id = data_parts[2]
                weapon_stats = get_item_stats(weapon_id)
                
                info_text = f"🔫 **{weapon_stats['name']}**\n\n"
                info_text += f"💥 Damage: {weapon_stats.get('damage', 'N/A')}\n"
                info_text += f"⭐ Stars: {weapon_stats.get('stars', 'N/A')}\n"
                info_text += f"💰 Price: {weapon_stats.get('price', 'N/A')}\n"
                info_text += f"📝 {weapon_stats.get('description', 'No description')}"
                
                await bot.answer_callback_query(call.id, info_text, show_alert=True)
                return
        
        await bot.answer_callback_query(call.id)
        
    except Exception as e:
        logger.error(f"Error handling attack callback: {e}")
        await bot.answer_callback_query(call.id, "Error processing request.")

def register_handlers(bot: AsyncTeleBot, db_manager: DBManager) -> None:
    """Registers all command handlers for the attack module"""
    group_only = helpers.ensure_group_command(bot, db_manager)

    @bot.message_handler(commands=['attack'])
    @group_only
    async def attack_handler(message: types.Message) -> None:
        await attack_command(message, bot, db_manager)
    
    @bot.message_handler(commands=['weapons'])
    @group_only
    async def weapons_handler(message: types.Message) -> None:
        lang = await helpers.get_lang(message.chat.id, message.from_user.id, db_manager)
        await show_weapon_comparison(message, bot, db_manager, lang)
    
    @bot.message_handler(commands=['battle_stats'])
    @group_only
    async def battle_stats_handler(message: types.Message) -> None:
        lang = await helpers.get_lang(message.chat.id, message.from_user.id, db_manager)
        await show_battle_stats(message, bot, db_manager, lang)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('attack:'))
    async def attack_callback_handler(call: types.CallbackQuery) -> None:
        await handle_attack_callback(call, bot, db_manager)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('weapon_info:'))
    async def weapon_info_callback_handler(call: types.CallbackQuery) -> None:
        await handle_attack_callback(call, bot, db_manager)
