#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Translations module for multilingual support
"""

import logging
from typing import Dict, Any

# Set up logging
logger = logging.getLogger(__name__)

# Global translations dictionary
T: Dict[str, Dict[str, Any]] = {}

def load_translations() -> None:
    """Load translations for all supported languages"""
    logger.info("Loading translations")
    
    # English translations
    T["en"] = {
        "welcome": "ðŸŽ® PvP missile fights inside your group. Use /help to learn how to collect ðŸ… medals.",
        "help": (
          "ðŸŽ® <b>How to play</b>\n"
          "â€¢ Reply to someone and send /attack â€” launch a missile\n"
          "â€¢ /defend â€” bring Patriot interceptors online\n"
          "â€¢ /shield â€” full Aegis shield for hours\n"
          "â€¢ /status â€” your stats & defenses\n"
          "â€¢ /shop â€” buy equipment with Medals\n"
          "â€¢ /stars â€” view TG Stars balance and premium items ðŸ’Ž\n"
          "â€¢ /bonus â€” daily medals\n"
          "â€¢ /inv â€” your weapons arsenal\n"
          "â€¢ /top â€” group leaderboard\n"
          "â€¢ /score â€” view your activity level\n"
          "â€¢ /quiz â€” participate in quizzes to earn rewards\n"
          "â€¢ /lang â€” switch language\n\n"
          "ðŸš« You cannot target the bot itself."
        ),
        "lang_choose": "Choose language:",
        "lang_set_en": "Language set to English.",
        "lang_set_fa": "Ø²Ø¨Ø§Ù† Ø¨Ù‡ ÙØ§Ø±Ø³ÛŒ ØªØºÛŒÛŒØ± Ú©Ø±Ø¯.",
        "status_self": "<b>{name}</b>\nðŸ… Medals: <b>{medals}</b> | ðŸ† Score: <b>{score}</b>\nðŸ›¡ï¸ Shield: {shield} | ðŸ›°ï¸ Intercept: {intercept}",
        "status_hint": "Reply to someone with /attack to strike!",
        "bonus_received": "ðŸŽ You received your daily bonus: <b>{amount}</b> medals!",
        "bonus_already": "â³ You already claimed your daily bonus. Try again tomorrow!",
        "shield_activated": "ðŸ›¡ï¸ Aegis shield activated for <b>{hours}</b> hours!",
        "shield_no_medals": "âŒ Not enough medals! You need <b>{cost}</b> medals to activate shield.",
        "shield_already": "âš ï¸ You already have an active shield ({time_left}m remaining).",
        "intercept_activated": "ðŸ›°ï¸ Patriot defense system activated for <b>{hours}</b> hours!",
        "intercept_no_medals": "âŒ Not enough medals! You need <b>{cost}</b> medals to activate defense system.",
        "intercept_already": "âš ï¸ You already have an active defense system ({time_left}m remaining).",
        "attack_yourself": "ðŸ¤¦â€â™‚ï¸ You can't attack yourself!",
        "attack_bot": "ðŸ¤– You can't attack the bot!",
        "attack_quota": "âš ï¸ You've reached your attack limit for today. Try again tomorrow!",
        "attack_shielded": "ðŸ›¡ï¸ Your attack was blocked by {name}'s Aegis Shield!",
        "attack_intercepted": "ðŸ›°ï¸ Your attack was intercepted by {name}'s Patriot Defense System! They gained <b>{bonus}%</b> of your attack power!",
        "attack_success": "ðŸ’¥ You hit {name} for <b>{damage}</b> damage!",
        
        # Additional attack system translations
        "attack_menu_header": "âš”ï¸ **Select a weapon to attack with:**\n\n",
        "no_weapons_message": "âŒ You don't have any weapons! Visit the shop to buy some.",
        "no_weapons_available": "You don't have any weapons available!",
        "attack_menu_title": "ðŸš€ **Choose your weapon:**",
        "cancel_button": "âŒ Cancel",
        "attack_cancelled": "âŒ Attack cancelled.",
        "error_attack_menu": "âŒ Error displaying attack menu.",
        "target_not_found_error": "âŒ Target user @{username} not found in this group.",
        "get_target_info_error": "âŒ Error getting target user information.",
        "invalid_target_error": "âŒ Invalid target specified.",
        "invalid_weapon_error": "âŒ Invalid weapon '{weapon}'! Available weapons: {available}",
        "no_weapon_error": "âŒ You don't have {weapon_name}!",
        "attack_cooldown_error": "â³ You must wait {wait_time} seconds before attacking again.",
        "attack_report": "ðŸŽ¯ **Attack Report**\n{attacker} attacked {target} with {emoji} {weapon}!",
        "attack_defended_report": "\nðŸ›¡ï¸ {target} defended with {defense}!\nDamage reduced from {original} to {final}",
        "attack_damage_report": "\nðŸ’¥ Dealt {final} damage!",
        "attack_hp_report": "\nâ¤ï¸ {target} has {hp} HP remaining",
        "attack_medals_report": "\nðŸ… {attacker} earned {medals} medals!",
        "attack_defeat_report": "\nðŸ’€ {target} was defeated and respawned with 50 HP!",
        "revenge_button": "âš”ï¸ Revenge",
        "show_stats_button": "ðŸ“Š Stats",
        "revenge_error": "Error processing revenge attack.",
        "weapon_comparison_title": "Weapon Comparison",
        "battle_stats_title": "Battle Statistics",
        "attack_stats": "Attack Statistics",
        "total_attacks": "Total Attacks",
        "total_damage": "Total Damage",
        "avg_damage": "Average Damage",
        "defense_stats": "Defense Statistics",
        "times_attacked": "Times Attacked",
        "damage_taken": "Damage Taken",
        "top_weapons": "Most Used Weapons",
        "uses": "uses",
        "defense_items": {
            "patriot": {"en": "Patriot Defense", "fa": "Ø¯ÙØ§Ø¹ Ù¾Ø§ØªØ±ÛŒÙˆØª"},
            "aegis": {"en": "Aegis Shield", "fa": "Ø³Ù¾Ø± Ø¢Ø¦Ú¯ÛŒØ³"}
        },
        
        "shop": "ðŸ›ï¸ <b>Military Equipment Shop</b> â€” pick an item:",
        "shop_item": "{stars} {name} â€” {price} medals",
        "shop_premium_item": "ðŸ’Ž {name} â€” {price} TG Stars",
        "shop_no_medals": "âŒ Not enough medals! You need <b>{price}</b> medals to buy this item.",
        "shop_no_stars": "âŒ Not enough TG Stars! You need <b>{price}</b> TG Stars to buy this item.",
        "shop_purchased": "âœ… You purchased {name} for <b>{price}</b> medals!",
        "shop_premium_purchased": "âœ… You purchased {name} for <b>{price}</b> TG Stars!",
        "stars_balance": "<b>ðŸ’Ž TG Stars Balance</b>\n\nYou have <b>{stars}</b> TG Stars in your account.\n\nTG Stars can be used to purchase premium items in the shop.\nUse /shop to browse available items.",
        
        # Enhanced shop translations
        "shop_welcome": "Military Equipment Shop",
        "your_balance": "Your Balance",
        "medals": "Medals",
        "tg_stars": "TG Stars",
        "shop_categories_intro": "Choose a category to browse items:",
        "premium_items": "Premium Items",
        "medal_items": "Medal Items", 
        "all_items": "All Items",
        "back_to_shop": "Back to Shop",
        "no_items_in_category": "No items available in this category.",
        "description": "Description",
        "damage": "Damage",
        "duration": "Duration",
        "hours": "hours",
        "effectiveness": "Effectiveness",
        "capacity": "Capacity",
        "medal_bonus": "Medal Bonus",
        "price": "Price",
        "you_can_afford": "You can afford this item!",
        "need_more_currency": "You need {amount} more {currency}",
        "buy_item": "Buy Item",
        "back_to_category": "Back to Category",
        "purchase_successful": "âœ… Successfully purchased {item_name} for {price} {currency}!",
        "purchase_failed": "âŒ Purchase failed. Please try again.",
        "purchase_error": "âŒ Error processing purchase.",
        "item_not_found": "âŒ Item not found.",
        "insufficient_medals": "âŒ Not enough medals!",
        "premium_info": "ðŸ’Ž Premium items available with TG Stars",
        
        "help_intro": "Select a category to get help:",
        "help_basic_btn": "Basic Commands",
        "help_attack_btn": "Attacking",
        "help_defense_btn": "Defending",
        "help_items_btn": "Items & Shop",
        "help_stars_btn": "TG Stars",
        "back_btn": "Back",

        "help_basic": (
            "<b>Basic Commands</b>\n"
            "/status - Your stats & defenses\n"
            "/inv - Your weapons arsenal\n"
            "/top - Group leaderboard\n"
            "/bonus - Claim your daily bonus medals"
        ),
        "help_attack": (
            "<b>Attacking</b>\n"
            "To attack another user, reply to their message and use the /attack command.\n"
            "Example: Reply to a user and send `/attack`"
        ),
        "help_defense": (
            "<b>Defending</b>\n"
            "/shield - Activate a shield to block incoming attacks.\n"
            "/defend - Activate an intercept system to reduce hit chance."
        ),
        "help_items": (
            "<b>Items & Shop</b>\n"
            "/shop - Buy items like shields and special bombs using medals.\n"
            "Items are stored in your /inv."
        ),
        "help_stars": (
            "<b>Telegram Stars</b>\n"
            "/stars - View your Telegram Stars balance and purchase premium items.\n"
            "For now, adding stars is free!"
        ),
        
        # Comprehensive help system translations
        "help_welcome": "TrumpBot Help Center",
        "recommendations_for_you": "Recommendations for you",
        "commands_help": "Commands",
        "combat_help": "Combat",
        "items_help": "Shop & Items",
        "stats_help": "Statistics",
        "faq_help": "FAQ",
        "main_menu": "Main Menu",
        "back_to_help": "Back to Help Menu",
        "comprehensive_commands": "Complete Command Reference",
        "combat_commands": "Combat Commands",
        "info_commands": "Information Commands",
        "shop_commands": "Shop Commands",
        "utility_commands": "Utility Commands",
        "premium_commands": "Premium Commands",
        "tips_section": "Quick Tips",
        "weapons_guide": "Weapons Guide",
        "back_to_combat": "Back to Combat",
        "main_help": "Main Help",
        "combat_system_guide": "Combat System Guide",
        "how_to_attack": "How to Attack",
        "damage_calculation": "Damage System",
        "defense_system": "Defense System",
        "rewards_system": "Reward System",
        "cooldowns": "Cooldowns & Limits",
        "weapons_detail": "Weapons",
        "stats_detail": "Statistics",
        "shop_system_guide": "Shop & Items System",
        "currency_types": "Currency Types",
        "item_categories": "Item Categories",
        "shopping_guide": "How to Shop",
        "inventory_management": "Managing Inventory",
        "shopping_tips": "Shopping Tips",
        "open_shop": "Open Shop",
        "view_inventory": "View Inventory",
        "statistics_guide": "Statistics & Progression Guide",
        "player_stats": "Player Statistics",
        "combat_stats": "Combat Statistics",
        "progression_system": "Progression System",
        "available_stats": "Available Commands",
        "improvement_tips": "Improvement Tips",
        "view_profile": "View Profile",
        "view_leaderboard": "Leaderboard",
        "faq_title": "Frequently Asked Questions",
        "contact_support": "More Help",
        "back_button": "Back",

        "private_chat_error": "âš ï¸ This command only works in groups. Please use it in a group chat.",
        
        # Inventory translations
        "inventory_title": "ðŸŽ’ <b>{first_name}'s Arsenal</b> (Level {level})",
        "inventory_empty": "Your arsenal is empty! Visit the /shop to get some equipment.",
        "inventory_stats": "ðŸ“Š <b>Arsenal Statistics:</b>\nâ€¢ Total Items: {total_items}\nâ€¢ Categories: {categories}\nâ€¢ Total Value: {total_value} medals",
        "inventory_categories": {
            "weapons": "ðŸ—¡ï¸ Weapons",
            "defense": "ðŸ›¡ï¸ Defense Items",
            "other": "ðŸ“¦ Other Items"
        },
        "use_item_menu": "ðŸ”§ <b>Use Item</b>\n\nSelect an item to use:",
        "item_used_success": "âœ… You used {item_name} successfully!",
        "item_used_defense": "ðŸ›¡ï¸ {item_name} activated! Protection active for 24 hours.",
        "item_used_boost": "âš¡ {item_name} used! {effect}",
        "item_not_found": "âŒ Item not found in your inventory.",
        "item_already_active": "âš ï¸ You already have this effect active.",
        "close_button": "âŒ Close",
        "back_to_inventory": "ðŸ”™ Back to Inventory",
        "use_item_button": "ðŸ”§ Use Item",
        "category_weapons": "ðŸ—¡ï¸ Weapons",
        "category_defense": "ðŸ›¡ï¸ Defense",
        "category_other": "ðŸ“¦ Other",
        "hp_restored": "â¤ï¸ HP restored to full!",
        "no_items_category": "No items in this category.",
        
        # Enhanced Status System Translations
        "status_dashboard": "ðŸ“Š Player Status Dashboard",
        "comprehensive_status": "ðŸŽ¯ Comprehensive Status",
        "player_overview": "ðŸ‘¤ Player Overview",
        "combat_status": "âš”ï¸ Combat Status",
        "defense_status": "ðŸ›¡ï¸ Defense Status",
        "inventory_status": "ðŸ“¦ Inventory Status",
        "achievements_status": "ðŸ† Achievements",
        "detailed_analytics": "ðŸ“ˆ Detailed Analytics",
        "status_message": "ðŸ‘¤ <b>{first_name}'s Status</b>\n\nðŸ’° <b>Resources:</b>\nðŸ… Medals: <b>{medals:,}</b>\nâ­ TG Stars: <b>{tg_stars}</b>\n\nâ¤ï¸ <b>Health:</b> <b>{hp}/100</b>\nðŸ”¥ <b>Level:</b> <b>{level}</b>\n\nðŸ›¡ï¸ <b>Defense:</b> {defense_status}",
        "defense_status_none": "âŒ No active defense",
        "defense_status_active": "âœ… {item_name} ({time_left} min remaining)",
        "activate_button": "ðŸ›¡ï¸ Activate {item_name}",
        "defense_already_active": "âš ï¸ You already have an active defense!",
        "defense_activated": "âœ… {item_name} activated for {hours} hours!",
        "item_not_owned": "âŒ You don't have {item_name}",
        "view_detailed_status": "ðŸ“Š View Detailed Status",
        "quick_status": "âš¡ Quick Status",
        "status_analytics": "ðŸ“ˆ Status Analytics",
        "refresh_status": "ðŸ”„ Refresh Status",
        "status_history": "ðŸ“œ Status History",
        "performance_overview": "ðŸŽ¯ Performance Overview",
        "current_streak": "ðŸ”¥ Current Streak",
        "best_streak": "ðŸ† Best Streak",
        "total_playtime": "â±ï¸ Total Playtime",
        "rank_in_chat": "ðŸ† Rank in Chat",
        "activity_level": "ðŸ“Š Activity Level",
        "last_active": "â° Last Active",
        "status_comparison": "ðŸ“Š Compare with Others",
        "status_trends": "ðŸ“ˆ Status Trends",
        "weekly_progress": "ðŸ“… Weekly Progress",
        "monthly_progress": "ðŸ“… Monthly Progress",
        "status_summary": "ðŸ“‹ Status Summary",
        "status_breakdown": "ðŸ” Status Breakdown",
        
        # Item names
        "items": {
            "f22": "F22 Raptor Heavy Attack",
            "moab": "MOAB Heavy Bomb",
            "nuclear": "Nuclear Warhead",
            "shield": "Aegis Shield",
            "intercept": "Patriot System",
            "carrier": "Aircraft Carrier",
            "stealth_bomber": "Stealth Bomber",
            "mega_nuke": "Mega Nuclear Warhead",
            "super_aegis": "Super Aegis Shield",
            "medal_boost": "Medal Boost",
            "vip_status": "VIP Status",
            "energy_drink": "Energy Drink",
            "repair_kit": "Repair Kit"
        },
        
        # Item emojis
        "item_emojis": {
            "f22": "âœˆï¸",
            "moab": "ðŸ’£",
            "nuclear": "â˜¢ï¸",
            "shield": "ðŸ›¡ï¸",
            "intercept": "ðŸš€",
            "carrier": "ðŸš¢",
            "stealth_bomber": "ðŸ›©ï¸",
            "mega_nuke": "ðŸ’¥",
            "super_aegis": "ðŸ›¡ï¸âœ¨",
            "medal_boost": "ðŸ…",
            "vip_status": "ðŸ‘‘",
            "energy_drink": "âš¡",
            "repair_kit": "ðŸ”§"
        },
        
        # TG Stars System Translations
        "stars_welcome": "ðŸ’Ž TG Stars Dashboard",
        "stars_balance_overview": "Your TG Stars Balance",
        "current_stars_balance": "Current Balance: â­ {stars} TG Stars",
        "stars_description": "TG Stars are premium currency that can be used to purchase exclusive items and features.",
        "how_to_get_stars": "How to Get TG Stars",
        "stars_purchase_info": "You can purchase TG Stars directly through Telegram's payment system.",
        "premium_features": "Premium Features",
        "exclusive_items": "Exclusive Items",
        "purchase_history": "Purchase History",
        "transaction_history": "Transaction History",
        "no_transactions": "No transactions found.",
        "transaction_date": "Date",
        "transaction_amount": "Amount",
        "transaction_item": "Item",
        "transaction_status": "Status",
        "transaction_completed": "Completed",
        "transaction_pending": "Pending",
        "transaction_failed": "Failed",
        
        # Invoice and Payment
        "invoice_title": "Premium Item Purchase",
        "invoice_description": "Purchase {item_name} with TG Stars",
        "invoice_creation_failed": "Failed to create payment invoice",
        "payment_processing": "Processing your payment...",
        "payment_successful": "Payment completed successfully!",
        "payment_failed": "Payment failed. Please try again.",
        "payment_cancelled": "Payment was cancelled.",
        "item_not_for_sale": "This item is not available for purchase.",
        "purchase_successful_stars": "âœ… Successfully purchased {item_name} with TG Stars!",
        
        # Stars Shop Integration
        "view_premium_shop": "ðŸ›’ View Premium Shop",
        "premium_catalog": "Premium Catalog",
        "exclusive_weapons": "Exclusive Weapons",
        "special_abilities": "Special Abilities",
        "item_requires_stars": "Requires â­ {price} TG Stars",
        "insufficient_stars": "âŒ Not enough TG Stars! You need {required} more.",
        "confirm_purchase": "Confirm Purchase",
        "purchase_confirmation": "Are you sure you want to purchase {item_name} for â­ {price} TG Stars?",
        "confirm_yes": "âœ… Yes, Purchase",
        "confirm_no": "âŒ Cancel",
        
        # Stars Features
        "stars_features_list": "ðŸŒŸ TG Stars Features:",
        "feature_exclusive_weapons": "â€¢ Access to exclusive premium weapons",
        "feature_special_abilities": "â€¢ Unlock special combat abilities", 
        "feature_premium_support": "â€¢ Priority customer support",
        "feature_advanced_stats": "â€¢ Advanced statistics and analytics",
        "feature_custom_themes": "â€¢ Custom themes and personalization",
        "feature_early_access": "â€¢ Early access to new features",
        
        # Error Messages
        "stars_error_generic": "âŒ An error occurred with TG Stars system.",
        "stars_error_insufficient": "âŒ Insufficient TG Stars balance.",
        "stars_error_item_unavailable": "âŒ This item is currently unavailable.",
        "stars_error_payment": "âŒ Payment processing failed.",
        "stars_error_network": "âŒ Network error. Please try again.",
        
        # Help and Support
        "stars_help": "ðŸ†˜ TG Stars Help",
        "stars_support": "ðŸ“ž Contact Support",
        "stars_faq": "â“ Frequently Asked Questions",
        "stars_terms": "ðŸ“œ Terms of Service",
        "refresh_balance": "ðŸ”„ Refresh Balance",
        "close_stars_menu": "âŒ Close",
        
        # Additional Stars Translations
        "invoice_sent": "âœ… Invoice sent successfully!",
        "total_cost": "Total Cost",
        "item": "Item",
        "payment_instructions": "Click the invoice above to complete your purchase.",
        "back_btn": "ðŸ”™ Back",
        
        # Quick Actions
        "buy_stars": "ðŸ’° Buy TG Stars",
        "view_history": "ðŸ“Š View History",
        "browse_premium": "ðŸ›’ Browse Premium Items",
        "stars_settings": "âš™ï¸ Settings",
        
        # Statistics System Translations
        "stats_dashboard": "ðŸ“Š Statistics Dashboard",
        "stats_overview": "Statistics Overview",
        "personal_stats": "Personal Statistics",
        "group_stats": "Group Statistics",
        "combat_analytics": "Combat Analytics",
        "leaderboard_ranking": "Leaderboard & Rankings",
        
        # Personal Stats
        "your_rank": "Your Rank",
        "current_level": "Current Level",
        "total_score": "Total Score",
        "current_hp": "Current HP",
        "max_hp": "Max HP",
        "attack_power": "Attack Power",
        "defense_rating": "Defense Rating",
        "accuracy_rate": "Accuracy Rate",
        "survival_rate": "Survival Rate",
        
        # Combat Statistics
        "battles_fought": "Battles Fought",
        "battles_won": "Battles Won",
        "battles_lost": "Battles Lost",
        "win_rate": "Win Rate",
        "total_damage_dealt": "Total Damage Dealt",
        "total_damage_taken": "Total Damage Taken",
        "average_damage": "Average Damage",
        "critical_hits": "Critical Hits",
        "successful_defenses": "Successful Defenses",
        "times_defeated": "Times Defeated",
        
        # Advanced Metrics
        "kill_death_ratio": "K/D Ratio",
        "damage_efficiency": "Damage Efficiency",
        "active_time": "Active Time",
        "last_activity": "Last Activity",
        "streak_current": "Current Streak",
        "streak_best": "Best Streak",
        "medals_earned": "Medals Earned",
        "medals_spent": "Medals Spent",
        "net_medals": "Net Medals",
        
        # Group Statistics
        "total_players": "Total Players",
        "active_players": "Active Players",
        "total_battles": "Total Battles",
        "most_active_player": "Most Active Player",
        "strongest_player": "Strongest Player",
        "most_battles": "Most Battles",
        "highest_damage": "Highest Damage",
        "group_activity": "Group Activity",
        
        # Weapon Statistics
        "favorite_weapon": "Favorite Weapon",
        "most_effective_weapon": "Most Effective Weapon",
        "weapon_usage": "Weapon Usage",
        "weapon_effectiveness": "Weapon Effectiveness",
        "weapons_owned": "Weapons Owned",
        "premium_items": "Premium Items",
        
        # Time-based Stats
        "daily_activity": "Daily Activity",
        "weekly_summary": "Weekly Summary",
        "monthly_progress": "Monthly Progress",
        "session_duration": "Session Duration",
        "peak_activity_time": "Peak Activity Time",
        
        # Achievements & Milestones
        "achievements_unlocked": "Achievements Unlocked",
        "milestones_reached": "Milestones Reached",
        "badges_earned": "Badges Earned",
        "special_titles": "Special Titles",
        "progression_rate": "Progression Rate",
        
        # Comparison Stats
        "vs_group_average": "vs Group Average",
        "percentile_ranking": "Percentile Ranking",
        "performance_trend": "Performance Trend",
        "improvement_rate": "Improvement Rate",
        
        # Stats Navigation
        "view_personal": "ðŸ‘¤ Personal Stats",
        "view_combat": "âš”ï¸ Combat Stats",
        "view_weapons": "ðŸ”« Weapon Stats",
        "view_achievements": "ðŸ† Achievements",
        "view_leaderboard": "ðŸ“Š Leaderboard",
        "view_trends": "ðŸ“ˆ Trends",
        "refresh_stats": "ðŸ”„ Refresh",
        "export_stats": "ðŸ“¤ Export",
        "stats_help": "ðŸ†˜ Help",
        "close_stats": "âŒ Close",
        
        # Enhanced Configuration System Translations
        "bot_configuration": "ðŸ”§ Bot Configuration",
        "configuration_dashboard": "ðŸ“Š Configuration Dashboard",
        "game_mechanics": "ðŸŽ® Game Mechanics",
        "feature_flags": "ðŸš© Feature Flags",
        "security_settings": "ðŸ” Security Settings",
        "notification_settings": "ðŸ”” Notification Settings",
        "performance_settings": "âš¡ Performance Settings",
        "multilingual_settings": "ðŸŒ Multilingual Settings",
        "bot_information": "ðŸ¤– Bot Information",
        "bot_version": "Version",
        "bot_description": "Description",
        "supported_languages": "Supported Languages",
        "current_language": "Current Language",
        "change_language": "ðŸŒ Change Language",
        "language_changed": "âœ… Language changed successfully!",
        "configuration_updated": "âœ… Configuration updated successfully!",
        "configuration_error": "âŒ Configuration update failed",
        "invalid_setting": "âŒ Invalid setting value",
        "setting_saved": "âœ… Setting saved: {setting_name}",
        "setting_reset": "ðŸ”„ Setting reset to default: {setting_name}",
        "export_configuration": "ðŸ“¤ Export Configuration",
        "import_configuration": "ðŸ“¥ Import Configuration",
        "configuration_exported": "âœ… Configuration exported successfully",
        "configuration_imported": "âœ… Configuration imported successfully",
        "reset_to_defaults": "ðŸ”„ Reset to Defaults",
        "confirm_reset": "âš ï¸ This will reset all settings to default values. Continue?",
        "reset_confirmed": "âœ… Configuration reset to defaults",
        "game_mode_settings": "ðŸŽ® Game Mode Settings",
        "difficulty_settings": "ðŸ“Š Difficulty Settings",
        "economy_settings": "ðŸ’° Economy Settings",
        "combat_settings": "âš”ï¸ Combat Settings",
        "weapon_multipliers": "ðŸ”« Weapon Damage Multipliers",
        "defense_effectiveness": "ðŸ›¡ï¸ Defense Effectiveness",
        "level_system": "ðŸ“ˆ Level System",
        "experience_settings": "â­ Experience Settings",
        "feature_enabled": "âœ… Enabled",
        "feature_disabled": "âŒ Disabled",
        "toggle_feature": "ðŸ”„ Toggle Feature",
        "advanced_settings": "âš™ï¸ Advanced Settings",
        "developer_mode": "ðŸ‘¨â€ðŸ’» Developer Mode",
        "debug_information": "ðŸ› Debug Information",
        "system_status": "ðŸ“Š System Status",
        "performance_metrics": "ðŸ“ˆ Performance Metrics",
        "configuration_validation": "âœ… Configuration Validation",
        "validation_passed": "âœ… All settings are valid",
        "validation_failed": "âŒ Configuration validation failed",
        "backup_configuration": "ðŸ’¾ Backup Configuration",
        "restore_configuration": "ðŸ”„ Restore Configuration",
        "configuration_help": "â“ Configuration Help",
        "setting_description": "ðŸ“ Setting Description",
        "recommended_value": "ðŸ’¡ Recommended Value",
        "current_value": "ðŸ“Š Current Value",
        "default_value": "ðŸ”§ Default Value",
        "apply_changes": "âœ… Apply Changes",
        "cancel_changes": "âŒ Cancel Changes",
        "unsaved_changes": "âš ï¸ You have unsaved changes",
        "save_before_exit": "ðŸ’¾ Save changes before exiting?",
        
        # Stats Messages
        "stats_loading": "Loading statistics...",
        "stats_error": "âŒ Error loading statistics.",
        "stats_no_data": "No data available yet. Start playing to see your stats!",
        "stats_updated": "âœ… Statistics updated!",
        "rank_improved": "ðŸŽ‰ Your rank has improved!",
        "new_achievement": "ðŸ† New achievement unlocked!",
        "milestone_reached": "ðŸŽ¯ Milestone reached!",
        
        # Legacy Stats (maintaining compatibility)
        "stats_title": "Group Statistics",
        "stats_top_players": "Top Players",
        "stats_no_players": "No players found",
        "stats_general": "General Statistics",
        "stats_total_attacks": "Total Attacks",
        "stats_most_used_weapon": "Most Used Weapon",
        "medals_emoji": "ðŸ…",
    }
    
    # Persian (Farsi) translations
    T["fa"] = {
        "welcome": "ðŸŽ® Ù†Ø¨Ø±Ø¯ Ù…ÙˆØ´Ú©ÛŒ Ø¨ÛŒÙ† Ø§Ø¹Ø¶Ø§ÛŒ Ú¯Ø±ÙˆÙ‡! Ø¨Ø±Ø§ÛŒ ÛŒØ§Ø¯Ú¯ÛŒØ±ÛŒ Ù†Ø­ÙˆÙ‡â€ŒÛŒ Ø¬Ù…Ø¹â€ŒØ¢ÙˆØ±ÛŒ ðŸ… Ù…Ø¯Ø§Ù„ØŒ Ø¯Ø³ØªÙˆØ± /help Ø±Ø§ Ø§Ø±Ø³Ø§Ù„ Ú©Ù†ÛŒØ¯.",
        "help": (
          "ðŸŽ® <b>Ø±Ø§Ù‡Ù†Ù…Ø§ÛŒ Ø¨Ø§Ø²ÛŒ</b>\n"
          "â€¢ Ø±ÙˆÛŒ Ù¾ÛŒØ§Ù… ÙØ±Ø¯ Ù…ÙˆØ±Ø¯ Ù†Ø¸Ø± Ø±ÛŒÙ¾Ù„Ø§ÛŒ Ú©Ø±Ø¯Ù‡ Ùˆ /attack Ø±Ø§ Ø¨Ø²Ù†ÛŒØ¯ â€” Ø¨Ø±Ø§ÛŒ Ø­Ù…Ù„Ù‡ Ù…ÙˆØ´Ú©ÛŒ\n"
          "â€¢ /defend â€” ÙØ¹Ø§Ù„â€ŒØ³Ø§Ø²ÛŒ Ø³Ø§Ù…Ø§Ù†Ù‡ Ø¯ÙØ§Ø¹ Ù¾Ø§ØªØ±ÛŒÙˆØª (Ø±Ù‡Ú¯ÛŒØ±ÛŒ Û±Û² Ø³Ø§Ø¹Øª)\n"
          "â€¢ /shield â€” Ø³Ù¾Ø± Ù…Ø­Ø§ÙØ¸ Ø§ÛŒØ¬ÛŒØ³ (Û³ Ø³Ø§Ø¹Øª)\n"
          "â€¢ /status â€” Ù…Ø´Ø§Ù‡Ø¯Ù‡ ÙˆØ¶Ø¹ÛŒØª Ùˆ Ø³ÛŒØ³ØªÙ…â€ŒÙ‡Ø§ÛŒ Ø¯ÙØ§Ø¹ÛŒ\n"
          "â€¢ /shop â€” Ø®Ø±ÛŒØ¯ ØªØ¬Ù‡ÛŒØ²Ø§Øª Ø¨Ø§ Ù…Ø¯Ø§Ù„\n"
          "â€¢ /stars â€” Ù…Ø´Ø§Ù‡Ø¯Ù‡ Ù…ÙˆØ¬ÙˆØ¯ÛŒ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù… Ùˆ Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ÛŒ ÙˆÛŒÚ˜Ù‡ ðŸ’Ž\n"
          "â€¢ /bonus â€” Ø¯Ø±ÛŒØ§ÙØª Ù¾Ø§Ø¯Ø§Ø´ Ø±ÙˆØ²Ø§Ù†Ù‡\n"
          "â€¢ /inv â€” Ù…Ø´Ø§Ù‡Ø¯Ù‡ Ù…ÙˆØ¬ÙˆØ¯ÛŒ Ø§Ù†Ø¨Ø§Ø± ØªØ³Ù„ÛŒØ­Ø§Øª\n"
          "â€¢ /top â€” Ù…Ø´Ø§Ù‡Ø¯Ù‡ Ø¬Ø¯ÙˆÙ„ Ø¨Ø±ØªØ±ÛŒÙ†â€ŒÙ‡Ø§ÛŒ Ú¯Ø±ÙˆÙ‡\n"
          "â€¢ /score â€” Ù…Ø´Ø§Ù‡Ø¯Ù‡ Ø§Ù…ØªÛŒØ§Ø² Ùˆ Ø³Ø·Ø­ ÙØ¹Ø§Ù„ÛŒØª Ø´Ù…Ø§\n"
          "â€¢ /quiz â€” Ø´Ø±Ú©Øª Ø¯Ø± Ú©ÙˆÛŒÛŒØ² Ùˆ Ø¯Ø±ÛŒØ§ÙØª Ø¬Ø§ÛŒØ²Ù‡\n"
          "â€¢ /lang â€” ØªØºÛŒÛŒØ± Ø²Ø¨Ø§Ù†\n\n"
          "ðŸš« Ù‡Ø¯Ù Ù‚Ø±Ø§Ø± Ø¯Ø§Ø¯Ù† Ø®ÙˆØ¯ Ø¨Ø§Øª Ù…Ù…Ù†ÙˆØ¹ Ø§Ø³Øª."
        ),
        "lang_choose": "Ù„Ø·ÙØ§Ù‹ Ø²Ø¨Ø§Ù† Ù…ÙˆØ±Ø¯ Ù†Ø¸Ø± Ø®ÙˆØ¯ Ø±Ø§ Ø§Ù†ØªØ®Ø§Ø¨ Ú©Ù†ÛŒØ¯:",
        "lang_set_en": "Language set to English.",
        "lang_set_fa": "Ø²Ø¨Ø§Ù† Ø¨Ù‡ ÙØ§Ø±Ø³ÛŒ ØªØºÛŒÛŒØ± Ú©Ø±Ø¯.",
        "status_self": "<b>{name}</b>\nðŸ… Ù…Ø¯Ø§Ù„â€ŒÙ‡Ø§: <b>{medals}</b> | ðŸ† Ø§Ù…ØªÛŒØ§Ø²: <b>{score}</b>\nðŸ›¡ï¸ Ø³Ù¾Ø± Ù…Ø­Ø§ÙØ¸: {shield} | ðŸ›°ï¸ Ø³ÛŒØ³ØªÙ… Ù¾Ø¯Ø§ÙÙ†Ø¯: {intercept}",
        "status_hint": "Ø¨Ø±Ø§ÛŒ Ø­Ù…Ù„Ù‡ØŒ Ø±ÙˆÛŒ Ù¾ÛŒØ§Ù… ÙØ±Ø¯ Ù…ÙˆØ±Ø¯ Ù†Ø¸Ø± Ø±ÛŒÙ¾Ù„Ø§ÛŒ Ú©Ø±Ø¯Ù‡ Ùˆ Ø¯Ø³ØªÙˆØ± /attack Ø±Ø§ Ø¨Ø²Ù†ÛŒØ¯!",
        "bonus_received": "ðŸŽ Ø´Ù…Ø§ Ù¾Ø§Ø¯Ø§Ø´ Ø±ÙˆØ²Ø§Ù†Ù‡ Ø®ÙˆØ¯ Ø±Ø§ Ø¯Ø±ÛŒØ§ÙØª Ú©Ø±Ø¯ÛŒØ¯: <b>{amount}</b> Ù…Ø¯Ø§Ù„!",
        "bonus_already": "â³ Ø´Ù…Ø§ Ø§Ù…Ø±ÙˆØ² Ù¾Ø§Ø¯Ø§Ø´ Ø±ÙˆØ²Ø§Ù†Ù‡ Ø®ÙˆØ¯ Ø±Ø§ Ø¯Ø±ÛŒØ§ÙØª Ú©Ø±Ø¯Ù‡â€ŒØ§ÛŒØ¯. ÙØ±Ø¯Ø§ Ø¯ÙˆØ¨Ø§Ø±Ù‡ ØªÙ„Ø§Ø´ Ú©Ù†ÛŒØ¯!",
        "shield_activated": "ðŸ›¡ï¸ Ø³Ù¾Ø± Ø¯ÙØ§Ø¹ÛŒ Ø§ÛŒØ¬ÛŒØ³ Ø¨Ø±Ø§ÛŒ <b>{hours}</b> Ø³Ø§Ø¹Øª ÙØ¹Ø§Ù„ Ø´Ø¯!",
        "shield_no_medals": "âŒ Ù…Ø¯Ø§Ù„ Ú©Ø§ÙÛŒ Ù†Ø¯Ø§Ø±ÛŒØ¯! Ø¨Ø±Ø§ÛŒ ÙØ¹Ø§Ù„â€ŒØ³Ø§Ø²ÛŒ Ø³Ù¾Ø± Ø¨Ù‡ <b>{cost}</b> Ù…Ø¯Ø§Ù„ Ù†ÛŒØ§Ø² Ø¯Ø§Ø±ÛŒØ¯.",
        "shield_already": "âš ï¸ Ø´Ù…Ø§ Ø¯Ø± Ø­Ø§Ù„ Ø­Ø§Ø¶Ø± ÛŒÚ© Ø³Ù¾Ø± ÙØ¹Ø§Ù„ Ø¯Ø§Ø±ÛŒØ¯ ({time_left} Ø¯Ù‚ÛŒÙ‚Ù‡ Ø¨Ø§Ù‚ÛŒâ€ŒÙ…Ø§Ù†Ø¯Ù‡).",
        "intercept_activated": "ðŸ›°ï¸ Ø³ÛŒØ³ØªÙ… Ø¯ÙØ§Ø¹ÛŒ Ù¾Ø§ØªØ±ÛŒÙˆØª Ø¨Ø±Ø§ÛŒ <b>{hours}</b> Ø³Ø§Ø¹Øª ÙØ¹Ø§Ù„ Ø´Ø¯!",
        "intercept_no_medals": "âŒ Ù…Ø¯Ø§Ù„ Ú©Ø§ÙÛŒ Ù†Ø¯Ø§Ø±ÛŒØ¯! Ø¨Ø±Ø§ÛŒ ÙØ¹Ø§Ù„â€ŒØ³Ø§Ø²ÛŒ Ø³ÛŒØ³ØªÙ… Ø¯ÙØ§Ø¹ÛŒ Ø¨Ù‡ <b>{cost}</b> Ù…Ø¯Ø§Ù„ Ù†ÛŒØ§Ø² Ø¯Ø§Ø±ÛŒØ¯.",
        "intercept_already": "âš ï¸ Ø´Ù…Ø§ Ø¯Ø± Ø­Ø§Ù„ Ø­Ø§Ø¶Ø± ÛŒÚ© Ø³ÛŒØ³ØªÙ… Ø¯ÙØ§Ø¹ÛŒ ÙØ¹Ø§Ù„ Ø¯Ø§Ø±ÛŒØ¯ ({time_left} Ø¯Ù‚ÛŒÙ‚Ù‡ Ø¨Ø§Ù‚ÛŒâ€ŒÙ…Ø§Ù†Ø¯Ù‡).",
        "attack_yourself": "ðŸ¤¦â€â™‚ï¸ Ø´Ù…Ø§ Ù†Ù…ÛŒâ€ŒØªÙˆØ§Ù†ÛŒØ¯ Ø¨Ù‡ Ø®ÙˆØ¯ØªØ§Ù† Ø­Ù…Ù„Ù‡ Ú©Ù†ÛŒØ¯!",
        "attack_bot": "ðŸ¤– Ø´Ù…Ø§ Ù†Ù…ÛŒâ€ŒØªÙˆØ§Ù†ÛŒØ¯ Ø¨Ù‡ Ø¨Ø§Øª Ø­Ù…Ù„Ù‡ Ú©Ù†ÛŒØ¯!",
        "attack_quota": "âš ï¸ Ø´Ù…Ø§ Ø¨Ù‡ Ø³Ù‚Ù Ø­Ù…Ù„Ø§Øª Ø±ÙˆØ²Ø§Ù†Ù‡ Ø®ÙˆØ¯ Ø±Ø³ÛŒØ¯Ù‡â€ŒØ§ÛŒØ¯. ÙØ±Ø¯Ø§ Ø¯ÙˆØ¨Ø§Ø±Ù‡ ØªÙ„Ø§Ø´ Ú©Ù†ÛŒØ¯!",
        "attack_shielded": "ðŸ›¡ï¸ Ø­Ù…Ù„Ù‡ Ø´Ù…Ø§ ØªÙˆØ³Ø· Ø³Ù¾Ø± Ø§ÛŒØ¬ÛŒØ³ {name} Ø¯ÙØ¹ Ø´Ø¯!",
        "attack_intercepted": "ðŸ›°ï¸ Ø­Ù…Ù„Ù‡ Ø´Ù…Ø§ ØªÙˆØ³Ø· Ø³ÛŒØ³ØªÙ… Ø¯ÙØ§Ø¹ÛŒ Ù¾Ø§ØªØ±ÛŒÙˆØª {name} Ø±Ù‡Ú¯ÛŒØ±ÛŒ Ø´Ø¯! Ø¢Ù†Ù‡Ø§ <b>{bonus}%</b> Ø§Ø² Ù‚Ø¯Ø±Øª Ø­Ù…Ù„Ù‡ Ø´Ù…Ø§ Ø±Ø§ Ø¯Ø±ÛŒØ§ÙØª Ú©Ø±Ø¯Ù†Ø¯!",
        "attack_success": "ðŸ’¥ Ø´Ù…Ø§ {name} Ø±Ø§ Ø¨Ø§ <b>{damage}</b> Ø¢Ø³ÛŒØ¨ Ù…ÙˆØ±Ø¯ Ø§ØµØ§Ø¨Øª Ù‚Ø±Ø§Ø± Ø¯Ø§Ø¯ÛŒØ¯!",
        
        # Additional attack system translations (Persian)
        "attack_menu_header": "âš”ï¸ **Ø³Ù„Ø§Ø­ Ù…ÙˆØ±Ø¯ Ù†Ø¸Ø± Ø¨Ø±Ø§ÛŒ Ø­Ù…Ù„Ù‡ Ø±Ø§ Ø§Ù†ØªØ®Ø§Ø¨ Ú©Ù†ÛŒØ¯:**\n\n",
        "no_weapons_message": "âŒ Ø´Ù…Ø§ Ù‡ÛŒÚ† Ø³Ù„Ø§Ø­ÛŒ Ù†Ø¯Ø§Ø±ÛŒØ¯! Ø¨Ø±Ø§ÛŒ Ø®Ø±ÛŒØ¯ Ø¨Ù‡ ÙØ±ÙˆØ´Ú¯Ø§Ù‡ Ù…Ø±Ø§Ø¬Ø¹Ù‡ Ú©Ù†ÛŒØ¯.",
        "no_weapons_available": "Ø´Ù…Ø§ Ù‡ÛŒÚ† Ø³Ù„Ø§Ø­ÛŒ Ø¯Ø± Ø¯Ø³ØªØ±Ø³ Ù†Ø¯Ø§Ø±ÛŒØ¯!",
        "attack_menu_title": "ðŸš€ **Ø³Ù„Ø§Ø­ Ø®ÙˆØ¯ Ø±Ø§ Ø§Ù†ØªØ®Ø§Ø¨ Ú©Ù†ÛŒØ¯:**",
        "cancel_button": "âŒ Ù„ØºÙˆ",
        "attack_cancelled": "âŒ Ø­Ù…Ù„Ù‡ Ù„ØºÙˆ Ø´Ø¯.",
        "error_attack_menu": "âŒ Ø®Ø·Ø§ Ø¯Ø± Ù†Ù…Ø§ÛŒØ´ Ù…Ù†ÙˆÛŒ Ø­Ù…Ù„Ù‡.",
        "target_not_found_error": "âŒ Ú©Ø§Ø±Ø¨Ø± Ù‡Ø¯Ù @{username} Ø¯Ø± Ø§ÛŒÙ† Ú¯Ø±ÙˆÙ‡ ÛŒØ§ÙØª Ù†Ø´Ø¯.",
        "get_target_info_error": "âŒ Ø®Ø·Ø§ Ø¯Ø± Ø¯Ø±ÛŒØ§ÙØª Ø§Ø·Ù„Ø§Ø¹Ø§Øª Ú©Ø§Ø±Ø¨Ø± Ù‡Ø¯Ù.",
        "invalid_target_error": "âŒ Ù‡Ø¯Ù Ù†Ø§Ù…Ø¹ØªØ¨Ø± Ù…Ø´Ø®Øµ Ø´Ø¯Ù‡ Ø§Ø³Øª.",
        "invalid_weapon_error": "âŒ Ø³Ù„Ø§Ø­ Ù†Ø§Ù…Ø¹ØªØ¨Ø± '{weapon}'! Ø³Ù„Ø§Ø­â€ŒÙ‡Ø§ÛŒ Ù…ÙˆØ¬ÙˆØ¯: {available}",
        "no_weapon_error": "âŒ Ø´Ù…Ø§ {weapon_name} Ù†Ø¯Ø§Ø±ÛŒØ¯!",
        "attack_cooldown_error": "â³ Ø¨Ø§ÛŒØ¯ {wait_time} Ø«Ø§Ù†ÛŒÙ‡ Ù‚Ø¨Ù„ Ø§Ø² Ø­Ù…Ù„Ù‡ Ø¨Ø¹Ø¯ÛŒ Ù…Ù†ØªØ¸Ø± Ø¨Ù…Ø§Ù†ÛŒØ¯.",
        "attack_report": "ðŸŽ¯ **Ú¯Ø²Ø§Ø±Ø´ Ø­Ù…Ù„Ù‡**\n{attacker} Ø¨Ø§ {emoji} {weapon} Ø¨Ù‡ {target} Ø­Ù…Ù„Ù‡ Ú©Ø±Ø¯!",
        "attack_defended_report": "\nðŸ›¡ï¸ {target} Ø¨Ø§ {defense} Ø¯ÙØ§Ø¹ Ú©Ø±Ø¯!\nØ¢Ø³ÛŒØ¨ Ø§Ø² {original} Ø¨Ù‡ {final} Ú©Ø§Ù‡Ø´ ÛŒØ§ÙØª",
        "attack_damage_report": "\nðŸ’¥ {final} Ø¢Ø³ÛŒØ¨ ÙˆØ§Ø±Ø¯ Ø´Ø¯!",
        "attack_hp_report": "\nâ¤ï¸ {target} Ø¯Ø§Ø±Ø§ÛŒ {hp} Ù†Ù‚Ø·Ù‡ Ø³Ù„Ø§Ù…Øª Ø¨Ø§Ù‚ÛŒâ€ŒÙ…Ø§Ù†Ø¯Ù‡ Ø§Ø³Øª",
        "attack_medals_report": "\nðŸ… {attacker} {medals} Ù…Ø¯Ø§Ù„ Ú©Ø³Ø¨ Ú©Ø±Ø¯!",
        "attack_defeat_report": "\nðŸ’€ {target} Ø´Ú©Ø³Øª Ø®ÙˆØ±Ø¯ Ùˆ Ø¨Ø§ 50 Ù†Ù‚Ø·Ù‡ Ø³Ù„Ø§Ù…Øª Ø§Ø­ÛŒØ§ Ø´Ø¯!",
        "revenge_button": "âš”ï¸ Ø§Ù†ØªÙ‚Ø§Ù…",
        "show_stats_button": "ðŸ“Š Ø¢Ù…Ø§Ø±",
        "revenge_error": "Ø®Ø·Ø§ Ø¯Ø± Ù¾Ø±Ø¯Ø§Ø²Ø´ Ø­Ù…Ù„Ù‡ Ø§Ù†ØªÙ‚Ø§Ù…ÛŒ.",
        "weapon_comparison_title": "Ù…Ù‚Ø§ÛŒØ³Ù‡ Ø³Ù„Ø§Ø­â€ŒÙ‡Ø§",
        "battle_stats_title": "Ø¢Ù…Ø§Ø± Ù†Ø¨Ø±Ø¯",
        "attack_stats": "Ø¢Ù…Ø§Ø± Ø­Ù…Ù„Ù‡",
        "total_attacks": "Ù…Ø¬Ù…ÙˆØ¹ Ø­Ù…Ù„Ø§Øª",
        "total_damage": "Ù…Ø¬Ù…ÙˆØ¹ Ø¢Ø³ÛŒØ¨",
        "avg_damage": "Ù…ØªÙˆØ³Ø· Ø¢Ø³ÛŒØ¨",
        "defense_stats": "Ø¢Ù…Ø§Ø± Ø¯ÙØ§Ø¹ÛŒ",
        "times_attacked": "Ø¯ÙØ¹Ø§Øª Ù…ÙˆØ±Ø¯ Ø­Ù…Ù„Ù‡ Ù‚Ø±Ø§Ø± Ú¯ÛŒØ±ÛŒ",
        "damage_taken": "Ø¢Ø³ÛŒØ¨ Ø¯Ø±ÛŒØ§ÙØªÛŒ",
        "top_weapons": "Ù¾Ø±Ø§Ø³ØªÙØ§Ø¯Ù‡â€ŒØªØ±ÛŒÙ† Ø³Ù„Ø§Ø­â€ŒÙ‡Ø§",
        "uses": "Ø§Ø³ØªÙØ§Ø¯Ù‡",
        
        "shop": "ðŸ›ï¸ <b>ÙØ±ÙˆØ´Ú¯Ø§Ù‡ ØªØ¬Ù‡ÛŒØ²Ø§Øª Ù†Ø¸Ø§Ù…ÛŒ</b> â€” ÛŒÚ© Ø¢ÛŒØªÙ… Ø§Ù†ØªØ®Ø§Ø¨ Ú©Ù†ÛŒØ¯:",
        "shop_item": "{stars} {name} â€” {price} Ù…Ø¯Ø§Ù„",
        "shop_premium_item": "ðŸ’Ž {name} â€” {price} Ø³ØªØ§Ø±Ù‡ ØªÙ„Ú¯Ø±Ø§Ù…",
        "shop_no_medals": "âŒ Ù…Ø¯Ø§Ù„ Ú©Ø§ÙÛŒ Ù†Ø¯Ø§Ø±ÛŒØ¯! Ø¨Ø±Ø§ÛŒ Ø®Ø±ÛŒØ¯ Ø§ÛŒÙ† Ø¢ÛŒØªÙ… Ø¨Ù‡ <b>{price}</b> Ù…Ø¯Ø§Ù„ Ù†ÛŒØ§Ø² Ø¯Ø§Ø±ÛŒØ¯.",
        "shop_no_stars": "âŒ Ø³ØªØ§Ø±Ù‡ ØªÙ„Ú¯Ø±Ø§Ù… Ú©Ø§ÙÛŒ Ù†Ø¯Ø§Ø±ÛŒØ¯! Ø¨Ø±Ø§ÛŒ Ø®Ø±ÛŒØ¯ Ø§ÛŒÙ† Ø¢ÛŒØªÙ… Ø¨Ù‡ <b>{price}</b> Ø³ØªØ§Ø±Ù‡ ØªÙ„Ú¯Ø±Ø§Ù… Ù†ÛŒØ§Ø² Ø¯Ø§Ø±ÛŒØ¯.",
        "shop_purchased": "âœ… Ø´Ù…Ø§ {name} Ø±Ø§ Ø¨Ø§ <b>{price}</b> Ù…Ø¯Ø§Ù„ Ø®Ø±ÛŒØ¯Ø§Ø±ÛŒ Ú©Ø±Ø¯ÛŒØ¯!",
        "shop_premium_purchased": "âœ… Ø´Ù…Ø§ {name} Ø±Ø§ Ø¨Ø§ <b>{price}</b> Ø³ØªØ§Ø±Ù‡ ØªÙ„Ú¯Ø±Ø§Ù… Ø®Ø±ÛŒØ¯Ø§Ø±ÛŒ Ú©Ø±Ø¯ÛŒØ¯!",
        "stars_balance": "<b>ðŸ’Ž Ù…ÙˆØ¬ÙˆØ¯ÛŒ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù…</b>\n\nØ´Ù…Ø§ <b>{stars}</b> Ø³ØªØ§Ø±Ù‡ ØªÙ„Ú¯Ø±Ø§Ù… Ø¯Ø± Ø­Ø³Ø§Ø¨ Ø®ÙˆØ¯ Ø¯Ø§Ø±ÛŒØ¯.\n\nØ³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù… Ø¨Ø±Ø§ÛŒ Ø®Ø±ÛŒØ¯ Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ÛŒ ÙˆÛŒÚ˜Ù‡ Ø¯Ø± ÙØ±ÙˆØ´Ú¯Ø§Ù‡ Ø§Ø³ØªÙØ§Ø¯Ù‡ Ù…ÛŒâ€ŒØ´ÙˆÙ†Ø¯.\nØ§Ø² Ø¯Ø³ØªÙˆØ± /shop Ø¨Ø±Ø§ÛŒ Ù…Ø´Ø§Ù‡Ø¯Ù‡ Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ÛŒ Ù…ÙˆØ¬ÙˆØ¯ Ø§Ø³ØªÙØ§Ø¯Ù‡ Ú©Ù†ÛŒØ¯.",
        
        # Enhanced shop translations (Persian)
        "shop_welcome": "ÙØ±ÙˆØ´Ú¯Ø§Ù‡ ØªØ¬Ù‡ÛŒØ²Ø§Øª Ù†Ø¸Ø§Ù…ÛŒ",
        "your_balance": "Ù…ÙˆØ¬ÙˆØ¯ÛŒ Ø´Ù…Ø§",
        "medals": "Ù…Ø¯Ø§Ù„â€ŒÙ‡Ø§",
        "tg_stars": "Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù…",
        "shop_categories_intro": "ÛŒÚ© Ø¯Ø³ØªÙ‡â€ŒØ¨Ù†Ø¯ÛŒ Ø±Ø§ Ø¨Ø±Ø§ÛŒ Ù…Ø´Ø§Ù‡Ø¯Ù‡ Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ Ø§Ù†ØªØ®Ø§Ø¨ Ú©Ù†ÛŒØ¯:",
        "premium_items": "Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ÛŒ ÙˆÛŒÚ˜Ù‡",
        "medal_items": "Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ÛŒ Ù…Ø¯Ø§Ù„ÛŒ",
        "all_items": "Ù‡Ù…Ù‡ Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§",
        "back_to_shop": "Ø¨Ø§Ø²Ú¯Ø´Øª Ø¨Ù‡ ÙØ±ÙˆØ´Ú¯Ø§Ù‡",
        "no_items_in_category": "Ù‡ÛŒÚ† Ø¢ÛŒØªÙ…ÛŒ Ø¯Ø± Ø§ÛŒÙ† Ø¯Ø³ØªÙ‡ Ù…ÙˆØ¬ÙˆØ¯ Ù†ÛŒØ³Øª.",
        "description": "ØªÙˆØ¶ÛŒØ­Ø§Øª",
        "damage": "Ø¢Ø³ÛŒØ¨",
        "duration": "Ù…Ø¯Øª Ø²Ù…Ø§Ù†",
        "hours": "Ø³Ø§Ø¹Øª",
        "effectiveness": "ØªØ§Ø«ÛŒØ±Ú¯Ø°Ø§Ø±ÛŒ",
        "capacity": "Ø¸Ø±ÙÛŒØª",
        "medal_bonus": "Ø¬Ø§ÛŒØ²Ù‡ Ù…Ø¯Ø§Ù„",
        "price": "Ù‚ÛŒÙ…Øª",
        "you_can_afford": "Ø´Ù…Ø§ Ù…ÛŒâ€ŒØªÙˆØ§Ù†ÛŒØ¯ Ø§ÛŒÙ† Ø¢ÛŒØªÙ… Ø±Ø§ Ø®Ø±ÛŒØ¯Ø§Ø±ÛŒ Ú©Ù†ÛŒØ¯!",
        "need_more_currency": "Ø´Ù…Ø§ Ø¨Ù‡ {amount} {currency} Ø¨ÛŒØ´ØªØ± Ù†ÛŒØ§Ø² Ø¯Ø§Ø±ÛŒØ¯",
        "buy_item": "Ø®Ø±ÛŒØ¯ Ø¢ÛŒØªÙ…",
        "back_to_category": "Ø¨Ø§Ø²Ú¯Ø´Øª Ø¨Ù‡ Ø¯Ø³ØªÙ‡â€ŒØ¨Ù†Ø¯ÛŒ",
        "purchase_successful": "âœ… {item_name} Ø¨Ø§ Ù…ÙˆÙÙ‚ÛŒØª Ø¨Ù‡ Ù‚ÛŒÙ…Øª {price} {currency} Ø®Ø±ÛŒØ¯Ø§Ø±ÛŒ Ø´Ø¯!",
        "purchase_failed": "âŒ Ø®Ø±ÛŒØ¯ Ù†Ø§Ù…ÙˆÙÙ‚ Ø¨ÙˆØ¯. Ù„Ø·ÙØ§Ù‹ Ø¯ÙˆØ¨Ø§Ø±Ù‡ ØªÙ„Ø§Ø´ Ú©Ù†ÛŒØ¯.",
        "purchase_error": "âŒ Ø®Ø·Ø§ Ø¯Ø± Ù¾Ø±Ø¯Ø§Ø²Ø´ Ø®Ø±ÛŒØ¯.",
        "item_not_found": "âŒ Ø¢ÛŒØªÙ… ÛŒØ§ÙØª Ù†Ø´Ø¯.",
        "insufficient_medals": "âŒ Ù…Ø¯Ø§Ù„ Ú©Ø§ÙÛŒ Ù†Ø¯Ø§Ø±ÛŒØ¯!",
        "premium_info": "ðŸ’Ž Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ÛŒ ÙˆÛŒÚ˜Ù‡ Ø¨Ø§ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù…",
        
        "help_intro": "Ø¨Ø±Ø§ÛŒ Ø¯Ø±ÛŒØ§ÙØª Ø±Ø§Ù‡Ù†Ù…Ø§ÛŒÛŒØŒ ÛŒÚ© Ø¯Ø³ØªÙ‡ Ø±Ø§ Ø§Ù†ØªØ®Ø§Ø¨ Ú©Ù†ÛŒØ¯:",
        "help_basic_btn": "Ø¯Ø³ØªÙˆØ±Ø§Øª Ø§ØµÙ„ÛŒ",
        "help_attack_btn": "Ø­Ù…Ù„Ù‡ Ú©Ø±Ø¯Ù†",
        "help_defense_btn": "Ø¯ÙØ§Ø¹ Ú©Ø±Ø¯Ù†",
        "help_items_btn": "Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ Ùˆ ÙØ±ÙˆØ´Ú¯Ø§Ù‡",
        "help_stars_btn": "Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù…",
        "back_btn": "Ø¨Ø§Ø²Ú¯Ø´Øª",

        "help_basic": (
            "<b>Ø¯Ø³ØªÙˆØ±Ø§Øª Ø§ØµÙ„ÛŒ</b>\n"
            "/status - ÙˆØ¶Ø¹ÛŒØª Ùˆ Ø¯ÙØ§Ø¹â€ŒÙ‡Ø§ÛŒ Ø´Ù…Ø§\n"
            "/inv - Ø§Ù†Ø¨Ø§Ø± ØªØ³Ù„ÛŒØ­Ø§Øª Ø´Ù…Ø§\n"
            "/top - Ø¬Ø¯ÙˆÙ„ Ø¨Ø±ØªØ±ÛŒÙ†â€ŒÙ‡Ø§ÛŒ Ú¯Ø±ÙˆÙ‡\n"
            "/bonus - Ø¯Ø±ÛŒØ§ÙØª Ù¾Ø§Ø¯Ø§Ø´ Ø±ÙˆØ²Ø§Ù†Ù‡"
        ),
        "help_attack": (
            "<b>Ø­Ù…Ù„Ù‡ Ú©Ø±Ø¯Ù†</b>\n"
            "Ø¨Ø±Ø§ÛŒ Ø­Ù…Ù„Ù‡ Ø¨Ù‡ Ú©Ø§Ø±Ø¨Ø± Ø¯ÛŒÚ¯Ø±ØŒ Ø¨Ù‡ Ù¾ÛŒØ§Ù… Ø§Ùˆ Ø±ÛŒÙ¾Ù„Ø§ÛŒ Ú©Ø±Ø¯Ù‡ Ùˆ Ø§Ø² Ø¯Ø³ØªÙˆØ± /attack Ø§Ø³ØªÙØ§Ø¯Ù‡ Ú©Ù†ÛŒØ¯.\n"
            "Ù…Ø«Ø§Ù„: Ø¨Ù‡ Ù¾ÛŒØ§Ù… ÛŒÚ© Ú©Ø§Ø±Ø¨Ø± Ø±ÛŒÙ¾Ù„Ø§ÛŒ Ú©Ø±Ø¯Ù‡ Ùˆ `/attack` Ø±Ø§ Ø§Ø±Ø³Ø§Ù„ Ú©Ù†ÛŒØ¯."
        ),
        "help_defense": (
            "<b>Ø¯ÙØ§Ø¹ Ú©Ø±Ø¯Ù†</b>\n"
            "/shield - ÙØ¹Ø§Ù„ Ú©Ø±Ø¯Ù† Ø³Ù¾Ø± Ø¨Ø±Ø§ÛŒ Ø¬Ù„ÙˆÚ¯ÛŒØ±ÛŒ Ø§Ø² Ø­Ù…Ù„Ø§Øª.\n"
            "/defend - ÙØ¹Ø§Ù„ Ú©Ø±Ø¯Ù† Ø³ÛŒØ³ØªÙ… Ø±Ù‡Ú¯ÛŒØ±ÛŒ Ø¨Ø±Ø§ÛŒ Ú©Ø§Ù‡Ø´ Ø´Ø§Ù†Ø³ Ø§ØµØ§Ø¨Øª."
        ),
        "help_items": (
            "<b>Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ Ùˆ ÙØ±ÙˆØ´Ú¯Ø§Ù‡</b>\n"
            "/shop - Ø®Ø±ÛŒØ¯ Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ÛŒÛŒ Ù…Ø§Ù†Ù†Ø¯ Ø³Ù¾Ø± Ùˆ Ø¨Ù…Ø¨â€ŒÙ‡Ø§ÛŒ ÙˆÛŒÚ˜Ù‡ Ø¨Ø§ Ø§Ø³ØªÙØ§Ø¯Ù‡ Ø§Ø² Ù…Ø¯Ø§Ù„.\n"
            "Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ Ø¯Ø± /inv Ø´Ù…Ø§ Ø°Ø®ÛŒØ±Ù‡ Ù…ÛŒâ€ŒØ´ÙˆÙ†Ø¯."
        ),
        "help_stars": (
            "<b>Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù…</b>\n"
            "/stars - Ù…Ø´Ø§Ù‡Ø¯Ù‡ Ù…ÙˆØ¬ÙˆØ¯ÛŒ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù… Ùˆ Ø®Ø±ÛŒØ¯ Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ÛŒ ÙˆÛŒÚ˜Ù‡.\n"
            "Ø¯Ø± Ø­Ø§Ù„ Ø­Ø§Ø¶Ø±ØŒ Ø§Ø¶Ø§ÙÙ‡ Ú©Ø±Ø¯Ù† Ø³ØªØ§Ø±Ù‡ Ø±Ø§ÛŒÚ¯Ø§Ù† Ø§Ø³Øª!"
        ),
        
        # Comprehensive help system translations (Persian)
        "help_welcome": "Ù…Ø±Ú©Ø² Ø±Ø§Ù‡Ù†Ù…Ø§ÛŒ ØªØ±Ø§Ù…Ù¾â€ŒØ¨Ø§Øª",
        "recommendations_for_you": "Ù¾ÛŒØ´Ù†Ù‡Ø§Ø¯Ø§Øª Ø¨Ø±Ø§ÛŒ Ø´Ù…Ø§",
        "commands_help": "Ø¯Ø³ØªÙˆØ±Ø§Øª",
        "combat_help": "Ù†Ø¨Ø±Ø¯",
        "items_help": "ÙØ±ÙˆØ´Ú¯Ø§Ù‡ Ùˆ Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§",
        "stats_help": "Ø¢Ù…Ø§Ø±Ù‡Ø§",
        "faq_help": "Ø³ÙˆØ§Ù„Ø§Øª Ù…ØªØ¯Ø§ÙˆÙ„",
        "main_menu": "Ù…Ù†ÙˆÛŒ Ø§ØµÙ„ÛŒ",
        "back_to_help": "Ø¨Ø§Ø²Ú¯Ø´Øª Ø¨Ù‡ Ù…Ù†ÙˆÛŒ Ø±Ø§Ù‡Ù†Ù…Ø§",
        "comprehensive_commands": "Ø±Ø§Ù‡Ù†Ù…Ø§ÛŒ Ú©Ø§Ù…Ù„ Ø¯Ø³ØªÙˆØ±Ø§Øª",
        "combat_commands": "Ø¯Ø³ØªÙˆØ±Ø§Øª Ù†Ø¨Ø±Ø¯",
        "info_commands": "Ø¯Ø³ØªÙˆØ±Ø§Øª Ø§Ø·Ù„Ø§Ø¹Ø§ØªÛŒ",
        "shop_commands": "Ø¯Ø³ØªÙˆØ±Ø§Øª ÙØ±ÙˆØ´Ú¯Ø§Ù‡",
        "utility_commands": "Ø¯Ø³ØªÙˆØ±Ø§Øª Ú©Ø§Ø±Ø¨Ø±Ø¯ÛŒ",
        "premium_commands": "Ø¯Ø³ØªÙˆØ±Ø§Øª ÙˆÛŒÚ˜Ù‡",
        "tips_section": "Ù†Ú©Ø§Øª Ø³Ø±ÛŒØ¹",
        "weapons_guide": "Ø±Ø§Ù‡Ù†Ù…Ø§ÛŒ ØªØ³Ù„ÛŒØ­Ø§Øª",
        "back_to_combat": "Ø¨Ø§Ø²Ú¯Ø´Øª Ø¨Ù‡ Ù†Ø¨Ø±Ø¯",
        "main_help": "Ø±Ø§Ù‡Ù†Ù…Ø§ÛŒ Ø§ØµÙ„ÛŒ",
        "combat_system_guide": "Ø±Ø§Ù‡Ù†Ù…Ø§ÛŒ Ø³ÛŒØ³ØªÙ… Ù†Ø¨Ø±Ø¯",
        "how_to_attack": "Ù†Ø­ÙˆÙ‡ Ø­Ù…Ù„Ù‡ Ú©Ø±Ø¯Ù†",
        "damage_calculation": "Ø³ÛŒØ³ØªÙ… Ø¢Ø³ÛŒØ¨",
        "defense_system": "Ø³ÛŒØ³ØªÙ… Ø¯ÙØ§Ø¹ÛŒ",
        "rewards_system": "Ø³ÛŒØ³ØªÙ… Ù¾Ø§Ø¯Ø§Ø´",
        "cooldowns": "Ù…Ø­Ø¯ÙˆØ¯ÛŒØªâ€ŒÙ‡Ø§ Ùˆ Ø²Ù…Ø§Ù† Ø§Ù†ØªØ¸Ø§Ø±",
        "weapons_detail": "ØªØ³Ù„ÛŒØ­Ø§Øª",
        "stats_detail": "Ø¢Ù…Ø§Ø±Ù‡Ø§",
        "shop_system_guide": "Ø±Ø§Ù‡Ù†Ù…Ø§ÛŒ ÙØ±ÙˆØ´Ú¯Ø§Ù‡ Ùˆ Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§",
        "currency_types": "Ø§Ù†ÙˆØ§Ø¹ Ø§Ø±Ø²",
        "item_categories": "Ø¯Ø³ØªÙ‡â€ŒØ¨Ù†Ø¯ÛŒ Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§",
        "shopping_guide": "Ø±Ø§Ù‡Ù†Ù…Ø§ÛŒ Ø®Ø±ÛŒØ¯",
        "inventory_management": "Ù…Ø¯ÛŒØ±ÛŒØª Ø§Ù†Ø¨Ø§Ø±",
        "shopping_tips": "Ù†Ú©Ø§Øª Ø®Ø±ÛŒØ¯",
        "open_shop": "Ø¨Ø§Ø² Ú©Ø±Ø¯Ù† ÙØ±ÙˆØ´Ú¯Ø§Ù‡",
        "view_inventory": "Ù…Ø´Ø§Ù‡Ø¯Ù‡ Ø§Ù†Ø¨Ø§Ø±",
        "statistics_guide": "Ø±Ø§Ù‡Ù†Ù…Ø§ÛŒ Ø¢Ù…Ø§Ø± Ùˆ Ù¾ÛŒØ´Ø±ÙØª",
        "player_stats": "Ø¢Ù…Ø§Ø± Ø¨Ø§Ø²ÛŒÚ©Ù†",
        "combat_stats": "Ø¢Ù…Ø§Ø± Ù†Ø¨Ø±Ø¯",
        "progression_system": "Ø³ÛŒØ³ØªÙ… Ù¾ÛŒØ´Ø±ÙØª",
        "available_stats": "Ø¯Ø³ØªÙˆØ±Ø§Øª Ù…ÙˆØ¬ÙˆØ¯",
        "improvement_tips": "Ù†Ú©Ø§Øª Ø¨Ù‡Ø¨ÙˆØ¯",
        "view_profile": "Ù…Ø´Ø§Ù‡Ø¯Ù‡ Ù¾Ø±ÙˆÙØ§ÛŒÙ„",
        "view_leaderboard": "Ø¬Ø¯ÙˆÙ„ Ø§Ù…ØªÛŒØ§Ø²Ø§Øª",
        "faq_title": "Ø³ÙˆØ§Ù„Ø§Øª Ù…ØªØ¯Ø§ÙˆÙ„",
        "contact_support": "Ø±Ø§Ù‡Ù†Ù…Ø§ÛŒÛŒ Ø¨ÛŒØ´ØªØ±",
        "back_button": "Ø¨Ø§Ø²Ú¯Ø´Øª",
        
        "private_chat_error": "âš ï¸ Ø§ÛŒÙ† Ø¯Ø³ØªÙˆØ± ÙÙ‚Ø· Ø¯Ø± Ú¯Ø±ÙˆÙ‡â€ŒÙ‡Ø§ Ú©Ø§Ø± Ù…ÛŒâ€ŒÚ©Ù†Ø¯. Ù„Ø·ÙØ§Ù‹ Ø¢Ù† Ø±Ø§ Ø¯Ø± ÛŒÚ© Ú¯Ø±ÙˆÙ‡ Ø§Ø³ØªÙØ§Ø¯Ù‡ Ú©Ù†ÛŒØ¯.",
        
        # Inventory translations
        "inventory_title": "ðŸŽ’ <b>Ø§Ù†Ø¨Ø§Ø± ØªØ³Ù„ÛŒØ­Ø§Øª {first_name}</b> (Ø³Ø·Ø­ {level})",
        "inventory_empty": "Ø§Ù†Ø¨Ø§Ø± ØªØ³Ù„ÛŒØ­Ø§Øª Ø´Ù…Ø§ Ø®Ø§Ù„ÛŒ Ø§Ø³Øª! Ø§Ø² /shop Ø¨Ø§Ø²Ø¯ÛŒØ¯ Ú©Ù†ÛŒØ¯ ØªØ§ ØªØ¬Ù‡ÛŒØ²Ø§Øª ØªÙ‡ÛŒÙ‡ Ú©Ù†ÛŒØ¯.",
        "inventory_stats": "ðŸ“Š <b>Ø¢Ù…Ø§Ø± Ø§Ù†Ø¨Ø§Ø± ØªØ³Ù„ÛŒØ­Ø§Øª:</b>\nâ€¢ Ú©Ù„ Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§: {total_items}\nâ€¢ Ø¯Ø³ØªÙ‡â€ŒØ¨Ù†Ø¯ÛŒâ€ŒÙ‡Ø§: {categories}\nâ€¢ Ø§Ø±Ø²Ø´ Ú©Ù„: {total_value} Ù…Ø¯Ø§Ù„",
        "inventory_categories": {
            "weapons": "ðŸ—¡ï¸ ØªØ³Ù„ÛŒØ­Ø§Øª",
            "defense": "ðŸ›¡ï¸ Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ÛŒ Ø¯ÙØ§Ø¹ÛŒ",
            "other": "ðŸ“¦ Ø³Ø§ÛŒØ± Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§"
        },
        "use_item_menu": "ðŸ”§ <b>Ø§Ø³ØªÙØ§Ø¯Ù‡ Ø§Ø² Ø¢ÛŒØªÙ…</b>\n\nÛŒÚ© Ø¢ÛŒØªÙ… Ø¨Ø±Ø§ÛŒ Ø§Ø³ØªÙØ§Ø¯Ù‡ Ø§Ù†ØªØ®Ø§Ø¨ Ú©Ù†ÛŒØ¯:",
        "item_used_success": "âœ… Ø´Ù…Ø§ Ø¨Ø§ Ù…ÙˆÙÙ‚ÛŒØª Ø§Ø² {item_name} Ø§Ø³ØªÙØ§Ø¯Ù‡ Ú©Ø±Ø¯ÛŒØ¯!",
        "item_used_defense": "ðŸ›¡ï¸ {item_name} ÙØ¹Ø§Ù„ Ø´Ø¯! Ù…Ø­Ø§ÙØ¸Øª Ø¨Ø±Ø§ÛŒ Û²Û´ Ø³Ø§Ø¹Øª ÙØ¹Ø§Ù„ Ø§Ø³Øª.",
        "item_used_boost": "âš¡ {item_name} Ø§Ø³ØªÙØ§Ø¯Ù‡ Ø´Ø¯! {effect}",
        "item_not_found": "âŒ Ø¢ÛŒØªÙ… Ø¯Ø± Ø§Ù†Ø¨Ø§Ø± Ø´Ù…Ø§ ÛŒØ§ÙØª Ù†Ø´Ø¯.",
        "item_already_active": "âš ï¸ Ø´Ù…Ø§ Ù‚Ø¨Ù„Ø§Ù‹ Ø§ÛŒÙ† Ø§Ø«Ø± Ø±Ø§ ÙØ¹Ø§Ù„ Ø¯Ø§Ø±ÛŒØ¯.",
        "close_button": "âŒ Ø¨Ø³ØªÙ†",
        "back_to_inventory": "ðŸ”™ Ø¨Ø§Ø²Ú¯Ø´Øª Ø¨Ù‡ Ø§Ù†Ø¨Ø§Ø±",
        "use_item_button": "ðŸ”§ Ø§Ø³ØªÙØ§Ø¯Ù‡ Ø§Ø² Ø¢ÛŒØªÙ…",
        "category_weapons": "ðŸ—¡ï¸ ØªØ³Ù„ÛŒØ­Ø§Øª",
        "category_defense": "ðŸ›¡ï¸ Ø¯ÙØ§Ø¹ÛŒ",
        "category_other": "ðŸ“¦ Ø³Ø§ÛŒØ±",
        "hp_restored": "â¤ï¸ Ù†Ù‚Ø§Ø· Ø²Ù†Ø¯Ú¯ÛŒ Ø¨Ù‡ Ø­Ø§Ù„Øª Ú©Ø§Ù…Ù„ Ø¨Ø§Ø²Ú¯Ø±Ø¯Ø§Ù†Ø¯Ù‡ Ø´Ø¯!",
        "no_items_category": "Ù‡ÛŒÚ† Ø¢ÛŒØªÙ…ÛŒ Ø¯Ø± Ø§ÛŒÙ† Ø¯Ø³ØªÙ‡ ÙˆØ¬ÙˆØ¯ Ù†Ø¯Ø§Ø±Ø¯.",
        
        # Enhanced Status System Translations (Persian)
        "status_dashboard": "ðŸ“Š Ø¯Ø§Ø´Ø¨ÙˆØ±Ø¯ ÙˆØ¶Ø¹ÛŒØª Ø¨Ø§Ø²ÛŒÚ©Ù†",
        "comprehensive_status": "ðŸŽ¯ ÙˆØ¶Ø¹ÛŒØª Ø¬Ø§Ù…Ø¹",
        "player_overview": "ðŸ‘¤ Ù†Ù…Ø§ÛŒ Ú©Ù„ÛŒ Ø¨Ø§Ø²ÛŒÚ©Ù†",
        "combat_status": "âš”ï¸ ÙˆØ¶Ø¹ÛŒØª Ù†Ø¨Ø±Ø¯",
        "defense_status": "ðŸ›¡ï¸ ÙˆØ¶Ø¹ÛŒØª Ø¯ÙØ§Ø¹",
        "inventory_status": "ðŸ“¦ ÙˆØ¶Ø¹ÛŒØª Ø§Ù†Ø¨Ø§Ø±",
        "achievements_status": "ðŸ† Ø¯Ø³ØªØ§ÙˆØ±Ø¯Ù‡Ø§",
        "detailed_analytics": "ðŸ“ˆ ØªØ­Ù„ÛŒÙ„â€ŒÙ‡Ø§ÛŒ ØªÙØµÛŒÙ„ÛŒ",
        "status_message": "ðŸ‘¤ <b>ÙˆØ¶Ø¹ÛŒØª {first_name}</b>\n\nðŸ’° <b>Ù…Ù†Ø§Ø¨Ø¹:</b>\nðŸ… Ù…Ø¯Ø§Ù„â€ŒÙ‡Ø§: <b>{medals:,}</b>\nâ­ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù…: <b>{tg_stars}</b>\n\nâ¤ï¸ <b>Ø³Ù„Ø§Ù…Øª:</b> <b>{hp}/100</b>\nðŸ”¥ <b>Ø³Ø·Ø­:</b> <b>{level}</b>\n\nðŸ›¡ï¸ <b>Ø¯ÙØ§Ø¹:</b> {defense_status}",
        "defense_status_none": "âŒ Ù‡ÛŒÚ† Ø¯ÙØ§Ø¹ ÙØ¹Ø§Ù„ÛŒ ÙˆØ¬ÙˆØ¯ Ù†Ø¯Ø§Ø±Ø¯",
        "defense_status_active": "âœ… {item_name} ({time_left} Ø¯Ù‚ÛŒÙ‚Ù‡ Ø¨Ø§Ù‚ÛŒâ€ŒÙ…Ø§Ù†Ø¯Ù‡)",
        "activate_button": "ðŸ›¡ï¸ ÙØ¹Ø§Ù„â€ŒØ³Ø§Ø²ÛŒ {item_name}",
        "defense_already_active": "âš ï¸ Ø´Ù…Ø§ Ù‚Ø¨Ù„Ø§Ù‹ ÛŒÚ© Ø¯ÙØ§Ø¹ ÙØ¹Ø§Ù„ Ø¯Ø§Ø±ÛŒØ¯!",
        "defense_activated": "âœ… {item_name} Ø¨Ø±Ø§ÛŒ {hours} Ø³Ø§Ø¹Øª ÙØ¹Ø§Ù„ Ø´Ø¯!",
        "item_not_owned": "âŒ Ø´Ù…Ø§ {item_name} Ù†Ø¯Ø§Ø±ÛŒØ¯",
        "view_detailed_status": "ðŸ“Š Ù…Ø´Ø§Ù‡Ø¯Ù‡ ÙˆØ¶Ø¹ÛŒØª ØªÙØµÛŒÙ„ÛŒ",
        "quick_status": "âš¡ ÙˆØ¶Ø¹ÛŒØª Ø³Ø±ÛŒØ¹",
        "status_analytics": "ðŸ“ˆ ØªØ­Ù„ÛŒÙ„â€ŒÙ‡Ø§ÛŒ ÙˆØ¶Ø¹ÛŒØª",
        "refresh_status": "ðŸ”„ Ø¨Ù‡â€ŒØ±ÙˆØ²Ø±Ø³Ø§Ù†ÛŒ ÙˆØ¶Ø¹ÛŒØª",
        "status_history": "ðŸ“œ ØªØ§Ø±ÛŒØ®Ú†Ù‡ ÙˆØ¶Ø¹ÛŒØª",
        "performance_overview": "ðŸŽ¯ Ù†Ù…Ø§ÛŒ Ú©Ù„ÛŒ Ø¹Ù…Ù„Ú©Ø±Ø¯",
        "current_streak": "ðŸ”¥ Ø³Ø±ÛŒ ÙØ¹Ù„ÛŒ",
        "best_streak": "ðŸ† Ø¨Ù‡ØªØ±ÛŒÙ† Ø³Ø±ÛŒ",
        "total_playtime": "â±ï¸ Ú©Ù„ Ø²Ù…Ø§Ù† Ø¨Ø§Ø²ÛŒ",
        "rank_in_chat": "ðŸ† Ø±ØªØ¨Ù‡ Ø¯Ø± Ú†Øª",
        "activity_level": "ðŸ“Š Ø³Ø·Ø­ ÙØ¹Ø§Ù„ÛŒØª",
        "last_active": "â° Ø¢Ø®Ø±ÛŒÙ† ÙØ¹Ø§Ù„ÛŒØª",
        "status_comparison": "ðŸ“Š Ù…Ù‚Ø§ÛŒØ³Ù‡ Ø¨Ø§ Ø³Ø§ÛŒØ±ÛŒÙ†",
        "status_trends": "ðŸ“ˆ Ø±ÙˆÙ†Ø¯Ù‡Ø§ÛŒ ÙˆØ¶Ø¹ÛŒØª",
        "weekly_progress": "ðŸ“… Ù¾ÛŒØ´Ø±ÙØª Ù‡ÙØªÚ¯ÛŒ",
        "monthly_progress": "ðŸ“… Ù¾ÛŒØ´Ø±ÙØª Ù…Ø§Ù‡Ø§Ù†Ù‡",
        "status_summary": "ðŸ“‹ Ø®Ù„Ø§ØµÙ‡ ÙˆØ¶Ø¹ÛŒØª",
        "status_breakdown": "ðŸ” ØªØ¬Ø²ÛŒÙ‡ ÙˆØ¶Ø¹ÛŒØª",
        
        # Item names (Persian)
        "items": {
            "f22": "Ø­Ù…Ù„Ù‡ Ø³Ù†Ú¯ÛŒÙ† F22 Ø±Ù¾ØªÙˆØ±",
            "moab": "Ø¨Ù…Ø¨ Ø³Ù†Ú¯ÛŒÙ† MOAB",
            "nuclear": "Ú©Ù„Ø§Ù‡Ú© Ù‡Ø³ØªÙ‡â€ŒØ§ÛŒ",
            "shield": "Ø³Ù¾Ø± Ø§ÛŒØ¬ÛŒØ³",
            "intercept": "Ø³ÛŒØ³ØªÙ… Ù¾Ø§ØªØ±ÛŒÙˆØª",
            "carrier": "Ù†Ø§Ùˆ Ù‡ÙˆØ§Ù¾ÛŒÙ…Ø§Ø¨Ø±",
            "stealth_bomber": "Ø¨Ù…Ø¨â€ŒØ§ÙÚ©Ù† Ù†Ø§Ù…Ø±Ø¦ÛŒ",
            "mega_nuke": "Ú©Ù„Ø§Ù‡Ú© Ù‡Ø³ØªÙ‡â€ŒØ§ÛŒ ÙÙˆÙ‚â€ŒØ§Ù„Ø¹Ø§Ø¯Ù‡",
            "super_aegis": "Ø³Ù¾Ø± ÙÙˆÙ‚â€ŒØ§Ù„Ø¹Ø§Ø¯Ù‡ Ø§ÛŒØ¬ÛŒØ³",
            "medal_boost": "ØªÙ‚ÙˆÛŒØª Ù…Ø¯Ø§Ù„",
            "vip_status": "ÙˆØ¶Ø¹ÛŒØª VIP",
            "energy_drink": "Ù†ÙˆØ´ÛŒØ¯Ù†ÛŒ Ø§Ù†Ø±Ú˜ÛŒâ€ŒØ²Ø§",
            "repair_kit": "Ú©ÛŒØª ØªØ¹Ù…ÛŒØ±"
        },
        
        # Defense items (Persian)
        "defense_items": {
            "patriot": {"en": "Patriot Defense", "fa": "Ø¯ÙØ§Ø¹ Ù¾Ø§ØªØ±ÛŒÙˆØª"},
            "aegis": {"en": "Aegis Shield", "fa": "Ø³Ù¾Ø± Ø§ÛŒØ¬ÛŒØ³"}
        },
        
        # Item emojis (same for all languages)
        "item_emojis": {
            "f22": "âœˆï¸",
            "moab": "ðŸ’£",
            "nuclear": "â˜¢ï¸",
            "shield": "ðŸ›¡ï¸",
            "intercept": "ðŸš€",
            "carrier": "ðŸš¢",
            "stealth_bomber": "ðŸ›©ï¸",
            "mega_nuke": "ðŸ’¥",
            "super_aegis": "ðŸ›¡ï¸âœ¨",
            "medal_boost": "ðŸ…",
            "vip_status": "ðŸ‘‘",
            "energy_drink": "âš¡",
            "repair_kit": "ðŸ”§"
        },
        
        # TG Stars System Translations (Persian)
        "stars_welcome": "ðŸ’Ž Ø¯Ø§Ø´Ø¨ÙˆØ±Ø¯ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù…",
        "stars_balance_overview": "Ù…ÙˆØ¬ÙˆØ¯ÛŒ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù… Ø´Ù…Ø§",
        "current_stars_balance": "Ù…ÙˆØ¬ÙˆØ¯ÛŒ ÙØ¹Ù„ÛŒ: â­ {stars} Ø³ØªØ§Ø±Ù‡ ØªÙ„Ú¯Ø±Ø§Ù…",
        "stars_description": "Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù… Ø§Ø±Ø² ÙˆÛŒÚ˜Ù‡ Ù‡Ø³ØªÙ†Ø¯ Ú©Ù‡ Ø¨Ø±Ø§ÛŒ Ø®Ø±ÛŒØ¯ Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ Ùˆ ÙˆÛŒÚ˜Ú¯ÛŒâ€ŒÙ‡Ø§ÛŒ Ø§Ù†Ø­ØµØ§Ø±ÛŒ Ø§Ø³ØªÙØ§Ø¯Ù‡ Ù…ÛŒâ€ŒØ´ÙˆÙ†Ø¯.",
        "how_to_get_stars": "Ù†Ø­ÙˆÙ‡ Ø¯Ø±ÛŒØ§ÙØª Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù…",
        "stars_purchase_info": "Ù…ÛŒâ€ŒØªÙˆØ§Ù†ÛŒØ¯ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù… Ø±Ø§ Ù…Ø³ØªÙ‚ÛŒÙ…Ø§Ù‹ Ø§Ø² Ø·Ø±ÛŒÙ‚ Ø³ÛŒØ³ØªÙ… Ù¾Ø±Ø¯Ø§Ø®Øª ØªÙ„Ú¯Ø±Ø§Ù… Ø®Ø±ÛŒØ¯Ø§Ø±ÛŒ Ú©Ù†ÛŒØ¯.",
        "premium_features": "ÙˆÛŒÚ˜Ú¯ÛŒâ€ŒÙ‡Ø§ÛŒ ÙˆÛŒÚ˜Ù‡",
        "exclusive_items": "Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ÛŒ Ø§Ù†Ø­ØµØ§Ø±ÛŒ",
        "purchase_history": "ØªØ§Ø±ÛŒØ®Ú†Ù‡ Ø®Ø±ÛŒØ¯Ù‡Ø§",
        "transaction_history": "ØªØ§Ø±ÛŒØ®Ú†Ù‡ ØªØ±Ø§Ú©Ù†Ø´â€ŒÙ‡Ø§",
        "no_transactions": "Ù‡ÛŒÚ† ØªØ±Ø§Ú©Ù†Ø´ÛŒ Ù¾ÛŒØ¯Ø§ Ù†Ø´Ø¯.",
        "transaction_date": "ØªØ§Ø±ÛŒØ®",
        "transaction_amount": "Ù…Ù‚Ø¯Ø§Ø±",
        "transaction_item": "Ø¢ÛŒØªÙ…",
        "transaction_status": "ÙˆØ¶Ø¹ÛŒØª",
        "transaction_completed": "ØªÚ©Ù…ÛŒÙ„ Ø´Ø¯Ù‡",
        "transaction_pending": "Ø¯Ø± Ø§Ù†ØªØ¸Ø§Ø±",
        "transaction_failed": "Ù†Ø§Ù…ÙˆÙÙ‚",
        
        # Invoice and Payment (Persian)
        "invoice_title": "Ø®Ø±ÛŒØ¯ Ø¢ÛŒØªÙ… ÙˆÛŒÚ˜Ù‡",
        "invoice_description": "Ø®Ø±ÛŒØ¯ {item_name} Ø¨Ø§ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù…",
        "invoice_creation_failed": "Ø§ÛŒØ¬Ø§Ø¯ ÙØ§Ú©ØªÙˆØ± Ù¾Ø±Ø¯Ø§Ø®Øª Ù†Ø§Ù…ÙˆÙÙ‚ Ø¨ÙˆØ¯",
        "payment_processing": "Ø¯Ø± Ø­Ø§Ù„ Ù¾Ø±Ø¯Ø§Ø²Ø´ Ù¾Ø±Ø¯Ø§Ø®Øª Ø´Ù…Ø§...",
        "payment_successful": "Ù¾Ø±Ø¯Ø§Ø®Øª Ø¨Ø§ Ù…ÙˆÙÙ‚ÛŒØª Ø§Ù†Ø¬Ø§Ù… Ø´Ø¯!",
        "payment_failed": "Ù¾Ø±Ø¯Ø§Ø®Øª Ù†Ø§Ù…ÙˆÙÙ‚ Ø¨ÙˆØ¯. Ù„Ø·ÙØ§Ù‹ Ø¯ÙˆØ¨Ø§Ø±Ù‡ ØªÙ„Ø§Ø´ Ú©Ù†ÛŒØ¯.",
        "payment_cancelled": "Ù¾Ø±Ø¯Ø§Ø®Øª Ù„ØºÙˆ Ø´Ø¯.",
        "item_not_for_sale": "Ø§ÛŒÙ† Ø¢ÛŒØªÙ… Ø¨Ø±Ø§ÛŒ ÙØ±ÙˆØ´ Ø¯Ø± Ø¯Ø³ØªØ±Ø³ Ù†ÛŒØ³Øª.",
        "purchase_successful_stars": "âœ… Ø®Ø±ÛŒØ¯ {item_name} Ø¨Ø§ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù… Ù…ÙˆÙÙ‚ÛŒØªâ€ŒØ¢Ù…ÛŒØ² Ø¨ÙˆØ¯!",
        
        # Stars Shop Integration (Persian)
        "view_premium_shop": "ðŸ›’ Ù…Ø´Ø§Ù‡Ø¯Ù‡ ÙØ±ÙˆØ´Ú¯Ø§Ù‡ ÙˆÛŒÚ˜Ù‡",
        "premium_catalog": "Ú©Ø§ØªØ§Ù„ÙˆÚ¯ ÙˆÛŒÚ˜Ù‡",
        "exclusive_weapons": "ØªØ³Ù„ÛŒØ­Ø§Øª Ø§Ù†Ø­ØµØ§Ø±ÛŒ",
        "special_abilities": "ØªÙˆØ§Ù†Ø§ÛŒÛŒâ€ŒÙ‡Ø§ÛŒ ÙˆÛŒÚ˜Ù‡",
        "item_requires_stars": "Ù†ÛŒØ§Ø² Ø¨Ù‡ â­ {price} Ø³ØªØ§Ø±Ù‡ ØªÙ„Ú¯Ø±Ø§Ù…",
        "insufficient_stars": "âŒ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù… Ú©Ø§ÙÛŒ Ù†ÛŒØ³Øª! {required} Ø³ØªØ§Ø±Ù‡ Ø¨ÛŒØ´ØªØ± Ù†ÛŒØ§Ø² Ø¯Ø§Ø±ÛŒØ¯.",
        "confirm_purchase": "ØªØ£ÛŒÛŒØ¯ Ø®Ø±ÛŒØ¯",
        "purchase_confirmation": "Ø¢ÛŒØ§ Ù…Ø·Ù…Ø¦Ù† Ù‡Ø³ØªÛŒØ¯ Ú©Ù‡ Ù…ÛŒâ€ŒØ®ÙˆØ§Ù‡ÛŒØ¯ {item_name} Ø±Ø§ Ø¨Ù‡ Ù‚ÛŒÙ…Øª â­ {price} Ø³ØªØ§Ø±Ù‡ ØªÙ„Ú¯Ø±Ø§Ù… Ø®Ø±ÛŒØ¯Ø§Ø±ÛŒ Ú©Ù†ÛŒØ¯ØŸ",
        "confirm_yes": "âœ… Ø¨Ù„Ù‡ØŒ Ø®Ø±ÛŒØ¯ Ú©Ù†",
        "confirm_no": "âŒ Ù„ØºÙˆ",
        
        # Stars Features (Persian)
        "stars_features_list": "ðŸŒŸ ÙˆÛŒÚ˜Ú¯ÛŒâ€ŒÙ‡Ø§ÛŒ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù…:",
        "feature_exclusive_weapons": "â€¢ Ø¯Ø³ØªØ±Ø³ÛŒ Ø¨Ù‡ ØªØ³Ù„ÛŒØ­Ø§Øª ÙˆÛŒÚ˜Ù‡ Ø§Ù†Ø­ØµØ§Ø±ÛŒ",
        "feature_special_abilities": "â€¢ Ø¨Ø§Ø² Ú©Ø±Ø¯Ù† ØªÙˆØ§Ù†Ø§ÛŒÛŒâ€ŒÙ‡Ø§ÛŒ ÙˆÛŒÚ˜Ù‡ Ù†Ø¨Ø±Ø¯",
        "feature_premium_support": "â€¢ Ù¾Ø´ØªÛŒØ¨Ø§Ù†ÛŒ Ø§ÙˆÙ„ÙˆÛŒØªâ€ŒØ¯Ø§Ø± Ù…Ø´ØªØ±ÛŒØ§Ù†",
        "feature_advanced_stats": "â€¢ Ø¢Ù…Ø§Ø± Ùˆ ØªØ­Ù„ÛŒÙ„â€ŒÙ‡Ø§ÛŒ Ù¾ÛŒØ´Ø±ÙØªÙ‡",
        "feature_custom_themes": "â€¢ ØªÙ…â€ŒÙ‡Ø§ Ùˆ Ø´Ø®ØµÛŒâ€ŒØ³Ø§Ø²ÛŒ Ø³ÙØ§Ø±Ø´ÛŒ",
        "feature_early_access": "â€¢ Ø¯Ø³ØªØ±Ø³ÛŒ Ø²ÙˆØ¯Ù‡Ù†Ú¯Ø§Ù… Ø¨Ù‡ ÙˆÛŒÚ˜Ú¯ÛŒâ€ŒÙ‡Ø§ÛŒ Ø¬Ø¯ÛŒØ¯",
        
        # Error Messages (Persian)
        "stars_error_generic": "âŒ Ø®Ø·Ø§ÛŒÛŒ Ø¯Ø± Ø³ÛŒØ³ØªÙ… Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù… Ø±Ø® Ø¯Ø§Ø¯.",
        "stars_error_insufficient": "âŒ Ù…ÙˆØ¬ÙˆØ¯ÛŒ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù… Ù†Ø§Ú©Ø§ÙÛŒ Ø§Ø³Øª.",
        "stars_error_item_unavailable": "âŒ Ø§ÛŒÙ† Ø¢ÛŒØªÙ… Ø¯Ø± Ø­Ø§Ù„ Ø­Ø§Ø¶Ø± Ø¯Ø± Ø¯Ø³ØªØ±Ø³ Ù†ÛŒØ³Øª.",
        "stars_error_payment": "âŒ Ù¾Ø±Ø¯Ø§Ø²Ø´ Ù¾Ø±Ø¯Ø§Ø®Øª Ù†Ø§Ù…ÙˆÙÙ‚ Ø¨ÙˆØ¯.",
        "stars_error_network": "âŒ Ø®Ø·Ø§ÛŒ Ø´Ø¨Ú©Ù‡. Ù„Ø·ÙØ§Ù‹ Ø¯ÙˆØ¨Ø§Ø±Ù‡ ØªÙ„Ø§Ø´ Ú©Ù†ÛŒØ¯.",
        
        # Help and Support (Persian)
        "stars_help": "ðŸ†˜ Ø±Ø§Ù‡Ù†Ù…Ø§ÛŒ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù…",
        "stars_support": "ðŸ“ž ØªÙ…Ø§Ø³ Ø¨Ø§ Ù¾Ø´ØªÛŒØ¨Ø§Ù†ÛŒ",
        "stars_faq": "â“ Ø³ÙˆØ§Ù„Ø§Øª Ù…ØªØ¯Ø§ÙˆÙ„",
        "stars_terms": "ðŸ“œ Ø´Ø±Ø§ÛŒØ· Ø§Ø³ØªÙØ§Ø¯Ù‡",
        "refresh_balance": "ðŸ”„ Ø¨Ø±ÙˆØ²Ø±Ø³Ø§Ù†ÛŒ Ù…ÙˆØ¬ÙˆØ¯ÛŒ",
        "close_stars_menu": "âŒ Ø¨Ø³ØªÙ†",
        
        # Additional Stars Translations (Persian)
        "invoice_sent": "âœ… ÙØ§Ú©ØªÙˆØ± Ø¨Ø§ Ù…ÙˆÙÙ‚ÛŒØª Ø§Ø±Ø³Ø§Ù„ Ø´Ø¯!",
        "total_cost": "Ù‡Ø²ÛŒÙ†Ù‡ Ú©Ù„",
        "item": "Ø¢ÛŒØªÙ…",
        "payment_instructions": "Ø±ÙˆÛŒ ÙØ§Ú©ØªÙˆØ± Ø¨Ø§Ù„Ø§ Ú©Ù„ÛŒÚ© Ú©Ù†ÛŒØ¯ ØªØ§ Ø®Ø±ÛŒØ¯ Ø®ÙˆØ¯ Ø±Ø§ ØªÚ©Ù…ÛŒÙ„ Ú©Ù†ÛŒØ¯.",
        "back_btn": "ðŸ”™ Ø¨Ø§Ø²Ú¯Ø´Øª",
        
        # Quick Actions (Persian)
        "buy_stars": "ðŸ’° Ø®Ø±ÛŒØ¯ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù…",
        "view_history": "ðŸ“Š Ù…Ø´Ø§Ù‡Ø¯Ù‡ ØªØ§Ø±ÛŒØ®Ú†Ù‡",
        "browse_premium": "ðŸ›’ Ù…Ø±ÙˆØ± Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ÛŒ ÙˆÛŒÚ˜Ù‡",
        "stars_settings": "âš™ï¸ ØªÙ†Ø¸ÛŒÙ…Ø§Øª",
        
        # Statistics System Translations (Persian)
        "stats_dashboard": "ðŸ“Š Ø¯Ø§Ø´Ø¨ÙˆØ±Ø¯ Ø¢Ù…Ø§Ø±",
        "stats_overview": "Ù†Ù…Ø§ÛŒ Ú©Ù„ÛŒ Ø¢Ù…Ø§Ø±",
        "personal_stats": "Ø¢Ù…Ø§Ø± Ø´Ø®ØµÛŒ",
        "group_stats": "Ø¢Ù…Ø§Ø± Ú¯Ø±ÙˆÙ‡",
        "combat_analytics": "ØªØ­Ù„ÛŒÙ„â€ŒÙ‡Ø§ÛŒ Ù†Ø¨Ø±Ø¯",
        "leaderboard_ranking": "Ø¬Ø¯ÙˆÙ„ Ø§Ù…ØªÛŒØ§Ø²Ø§Øª Ùˆ Ø±Ø¯Ù‡â€ŒØ¨Ù†Ø¯ÛŒ",
        
        # Personal Stats (Persian)
        "your_rank": "Ø±ØªØ¨Ù‡ Ø´Ù…Ø§",
        "current_level": "Ø³Ø·Ø­ ÙØ¹Ù„ÛŒ",
        "total_score": "Ø§Ù…ØªÛŒØ§Ø² Ú©Ù„",
        "current_hp": "HP ÙØ¹Ù„ÛŒ",
        "max_hp": "Ø­Ø¯Ø§Ú©Ø«Ø± HP",
        "attack_power": "Ù‚Ø¯Ø±Øª Ø­Ù…Ù„Ù‡",
        "defense_rating": "Ø§Ù…ØªÛŒØ§Ø² Ø¯ÙØ§Ø¹",
        "accuracy_rate": "Ù†Ø±Ø® Ø¯Ù‚Øª",
        "survival_rate": "Ù†Ø±Ø® Ø¨Ù‚Ø§",
        
        # Combat Statistics (Persian)
        "battles_fought": "Ù†Ø¨Ø±Ø¯Ù‡Ø§ÛŒ Ø§Ù†Ø¬Ø§Ù… Ø´Ø¯Ù‡",
        "battles_won": "Ù†Ø¨Ø±Ø¯Ù‡Ø§ÛŒ Ø¨Ø±Ø¯Ù‡ Ø´Ø¯Ù‡",
        "battles_lost": "Ù†Ø¨Ø±Ø¯Ù‡Ø§ÛŒ Ø¨Ø§Ø®ØªÙ‡ Ø´Ø¯Ù‡",
        "win_rate": "Ù†Ø±Ø® Ù¾ÛŒØ±ÙˆØ²ÛŒ",
        "total_damage_dealt": "Ú©Ù„ Ø¢Ø³ÛŒØ¨ ÙˆØ§Ø±Ø¯ Ø´Ø¯Ù‡",
        "total_damage_taken": "Ú©Ù„ Ø¢Ø³ÛŒØ¨ Ø¯Ø±ÛŒØ§ÙØªÛŒ",
        "average_damage": "Ù…ÛŒØ§Ù†Ú¯ÛŒÙ† Ø¢Ø³ÛŒØ¨",
        "critical_hits": "Ø¶Ø±Ø¨Ø§Øª Ø¨Ø­Ø±Ø§Ù†ÛŒ",
        "successful_defenses": "Ø¯ÙØ§Ø¹â€ŒÙ‡Ø§ÛŒ Ù…ÙˆÙÙ‚",
        "times_defeated": "Ø¯ÙØ¹Ø§Øª Ø´Ú©Ø³Øª",
        
        # Advanced Metrics (Persian)
        "kill_death_ratio": "Ù†Ø³Ø¨Øª Ú©Ø´ØªÙ†/Ù…Ø±Ú¯",
        "damage_efficiency": "Ú©Ø§Ø±Ø§ÛŒÛŒ Ø¢Ø³ÛŒØ¨",
        "active_time": "Ø²Ù…Ø§Ù† ÙØ¹Ø§Ù„ÛŒØª",
        "last_activity": "Ø¢Ø®Ø±ÛŒÙ† ÙØ¹Ø§Ù„ÛŒØª",
        "streak_current": "Ø±Ú©ÙˆØ±Ø¯ ÙØ¹Ù„ÛŒ",
        "streak_best": "Ø¨Ù‡ØªØ±ÛŒÙ† Ø±Ú©ÙˆØ±Ø¯",
        "medals_earned": "Ù…Ø¯Ø§Ù„â€ŒÙ‡Ø§ÛŒ Ú©Ø³Ø¨ Ø´Ø¯Ù‡",
        "medals_spent": "Ù…Ø¯Ø§Ù„â€ŒÙ‡Ø§ÛŒ Ø®Ø±Ø¬ Ø´Ø¯Ù‡",
        "net_medals": "Ù…Ø¯Ø§Ù„â€ŒÙ‡Ø§ÛŒ Ø®Ø§Ù„Øµ",
        
        # Group Statistics (Persian)
        "total_players": "Ú©Ù„ Ø¨Ø§Ø²ÛŒÚ©Ù†Ø§Ù†",
        "active_players": "Ø¨Ø§Ø²ÛŒÚ©Ù†Ø§Ù† ÙØ¹Ø§Ù„",
        "total_battles": "Ú©Ù„ Ù†Ø¨Ø±Ø¯Ù‡Ø§",
        "most_active_player": "ÙØ¹Ø§Ù„â€ŒØªØ±ÛŒÙ† Ø¨Ø§Ø²ÛŒÚ©Ù†",
        "strongest_player": "Ù‚ÙˆÛŒâ€ŒØªØ±ÛŒÙ† Ø¨Ø§Ø²ÛŒÚ©Ù†",
        "most_battles": "Ø¨ÛŒØ´ØªØ±ÛŒÙ† Ù†Ø¨Ø±Ø¯",
        "highest_damage": "Ø¨Ø§Ù„Ø§ØªØ±ÛŒÙ† Ø¢Ø³ÛŒØ¨",
        "group_activity": "ÙØ¹Ø§Ù„ÛŒØª Ú¯Ø±ÙˆÙ‡",
        
        # Weapon Statistics (Persian)
        "favorite_weapon": "ØªØ³Ù„ÛŒØ­ Ù…ÙˆØ±Ø¯ Ø¹Ù„Ø§Ù‚Ù‡",
        "most_effective_weapon": "Ù…Ø¤Ø«Ø±ØªØ±ÛŒÙ† ØªØ³Ù„ÛŒØ­",
        "weapon_usage": "Ø§Ø³ØªÙØ§Ø¯Ù‡ Ø§Ø² ØªØ³Ù„ÛŒØ­Ø§Øª",
        "weapon_effectiveness": "Ú©Ø§Ø±Ø§ÛŒÛŒ ØªØ³Ù„ÛŒØ­Ø§Øª",
        "weapons_owned": "ØªØ³Ù„ÛŒØ­Ø§Øª Ù…ÙˆØ¬ÙˆØ¯",
        "premium_items": "Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ÛŒ ÙˆÛŒÚ˜Ù‡",
        
        # Time-based Stats (Persian)
        "daily_activity": "ÙØ¹Ø§Ù„ÛŒØª Ø±ÙˆØ²Ø§Ù†Ù‡",
        "weekly_summary": "Ø®Ù„Ø§ØµÙ‡ Ù‡ÙØªÚ¯ÛŒ",
        "monthly_progress": "Ù¾ÛŒØ´Ø±ÙØª Ù…Ø§Ù‡Ø§Ù†Ù‡",
        "session_duration": "Ù…Ø¯Øª Ø¬Ù„Ø³Ù‡",
        "peak_activity_time": "Ø²Ù…Ø§Ù† Ø§ÙˆØ¬ ÙØ¹Ø§Ù„ÛŒØª",
        
        # Achievements & Milestones (Persian)
        "achievements_unlocked": "Ø¯Ø³ØªØ§ÙˆØ±Ø¯Ù‡Ø§ÛŒ Ø¨Ø§Ø² Ø´Ø¯Ù‡",
        "milestones_reached": "Ù†Ù‚Ø§Ø· Ø¹Ø·Ù Ø±Ø³ÛŒØ¯Ù‡",
        "badges_earned": "Ù†Ø´Ø§Ù†â€ŒÙ‡Ø§ÛŒ Ú©Ø³Ø¨ Ø´Ø¯Ù‡",
        "special_titles": "Ø¹Ù†Ø§ÙˆÛŒÙ† ÙˆÛŒÚ˜Ù‡",
        "progression_rate": "Ù†Ø±Ø® Ù¾ÛŒØ´Ø±ÙØª",
        
        # Comparison Stats (Persian)
        "vs_group_average": "Ø¯Ø± Ù…Ù‚Ø§Ø¨Ù„ Ù…ÛŒØ§Ù†Ú¯ÛŒÙ† Ú¯Ø±ÙˆÙ‡",
        "percentile_ranking": "Ø±Ø¯Ù‡â€ŒØ¨Ù†Ø¯ÛŒ ØµØ¯Ú©ÛŒ",
        "performance_trend": "Ø±ÙˆÙ†Ø¯ Ø¹Ù…Ù„Ú©Ø±Ø¯",
        "improvement_rate": "Ù†Ø±Ø® Ø¨Ù‡Ø¨ÙˆØ¯",
        
        # Stats Navigation (Persian)
        "view_personal": "ðŸ‘¤ Ø¢Ù…Ø§Ø± Ø´Ø®ØµÛŒ",
        "view_combat": "âš”ï¸ Ø¢Ù…Ø§Ø± Ù†Ø¨Ø±Ø¯",
        "view_weapons": "ðŸ”« Ø¢Ù…Ø§Ø± ØªØ³Ù„ÛŒØ­Ø§Øª",
        "view_achievements": "ðŸ† Ø¯Ø³ØªØ§ÙˆØ±Ø¯Ù‡Ø§",
        "view_leaderboard": "ðŸ“Š Ø¬Ø¯ÙˆÙ„ Ø§Ù…ØªÛŒØ§Ø²Ø§Øª",
        "view_trends": "ðŸ“ˆ Ø±ÙˆÙ†Ø¯Ù‡Ø§",
        "refresh_stats": "ðŸ”„ Ø¨Ø±ÙˆØ²Ø±Ø³Ø§Ù†ÛŒ",
        "export_stats": "ðŸ“¤ Ø®Ø±ÙˆØ¬ÛŒ",
        "stats_help": "ðŸ†˜ Ø±Ø§Ù‡Ù†Ù…Ø§",
        "close_stats": "âŒ Ø¨Ø³ØªÙ†",
        
        # Enhanced Configuration System Translations (Persian)
        "bot_configuration": "ðŸ”§ Ù¾ÛŒÚ©Ø±Ø¨Ù†Ø¯ÛŒ Ø±Ø¨Ø§Øª",
        "configuration_dashboard": "ðŸ“Š Ø¯Ø§Ø´Ø¨ÙˆØ±Ø¯ Ù¾ÛŒÚ©Ø±Ø¨Ù†Ø¯ÛŒ",
        "game_mechanics": "ðŸŽ® Ù…Ú©Ø§Ù†ÛŒÚ©â€ŒÙ‡Ø§ÛŒ Ø¨Ø§Ø²ÛŒ",
        "feature_flags": "ðŸš© Ù¾Ø±Ú†Ù…â€ŒÙ‡Ø§ÛŒ ÙˆÛŒÚ˜Ú¯ÛŒ",
        "security_settings": "ðŸ” ØªÙ†Ø¸ÛŒÙ…Ø§Øª Ø§Ù…Ù†ÛŒØªÛŒ",
        "notification_settings": "ðŸ”” ØªÙ†Ø¸ÛŒÙ…Ø§Øª Ø§Ø¹Ù„Ø§Ù†Ø§Øª",
        "performance_settings": "âš¡ ØªÙ†Ø¸ÛŒÙ…Ø§Øª Ø¹Ù…Ù„Ú©Ø±Ø¯",
        "multilingual_settings": "ðŸŒ ØªÙ†Ø¸ÛŒÙ…Ø§Øª Ú†Ù†Ø¯Ø²Ø¨Ø§Ù†Ù‡",
        "bot_information": "ðŸ¤– Ø§Ø·Ù„Ø§Ø¹Ø§Øª Ø±Ø¨Ø§Øª",
        "bot_version": "Ù†Ø³Ø®Ù‡",
        "bot_description": "ØªÙˆØ¶ÛŒØ­Ø§Øª",
        "supported_languages": "Ø²Ø¨Ø§Ù†â€ŒÙ‡Ø§ÛŒ Ù¾Ø´ØªÛŒØ¨Ø§Ù†ÛŒ Ø´Ø¯Ù‡",
        "current_language": "Ø²Ø¨Ø§Ù† ÙØ¹Ù„ÛŒ",
        "change_language": "ðŸŒ ØªØºÛŒÛŒØ± Ø²Ø¨Ø§Ù†",
        "language_changed": "âœ… Ø²Ø¨Ø§Ù† Ø¨Ø§ Ù…ÙˆÙÙ‚ÛŒØª ØªØºÛŒÛŒØ± Ú©Ø±Ø¯!",
        "configuration_updated": "âœ… Ù¾ÛŒÚ©Ø±Ø¨Ù†Ø¯ÛŒ Ø¨Ø§ Ù…ÙˆÙÙ‚ÛŒØª Ø¨Ù‡â€ŒØ±ÙˆØ²Ø±Ø³Ø§Ù†ÛŒ Ø´Ø¯!",
        "configuration_error": "âŒ Ø¨Ù‡â€ŒØ±ÙˆØ²Ø±Ø³Ø§Ù†ÛŒ Ù¾ÛŒÚ©Ø±Ø¨Ù†Ø¯ÛŒ Ù†Ø§Ù…ÙˆÙÙ‚ Ø¨ÙˆØ¯",
        "invalid_setting": "âŒ Ù…Ù‚Ø¯Ø§Ø± ØªÙ†Ø¸ÛŒÙ…Ø§Øª Ù†Ø§Ù…Ø¹ØªØ¨Ø±",
        "setting_saved": "âœ… ØªÙ†Ø¸ÛŒÙ…Ø§Øª Ø°Ø®ÛŒØ±Ù‡ Ø´Ø¯: {setting_name}",
        "setting_reset": "ðŸ”„ ØªÙ†Ø¸ÛŒÙ…Ø§Øª Ø¨Ù‡ Ø­Ø§Ù„Øª Ù¾ÛŒØ´â€ŒÙØ±Ø¶ Ø¨Ø§Ø²Ú¯Ø±Ø¯Ø§Ù†Ø¯Ù‡ Ø´Ø¯: {setting_name}",
        "export_configuration": "ðŸ“¤ ØµØ§Ø¯Ø±Ø§Øª Ù¾ÛŒÚ©Ø±Ø¨Ù†Ø¯ÛŒ",
        "import_configuration": "ðŸ“¥ ÙˆØ§Ø±Ø¯ Ú©Ø±Ø¯Ù† Ù¾ÛŒÚ©Ø±Ø¨Ù†Ø¯ÛŒ",
        "configuration_exported": "âœ… Ù¾ÛŒÚ©Ø±Ø¨Ù†Ø¯ÛŒ Ø¨Ø§ Ù…ÙˆÙÙ‚ÛŒØª ØµØ§Ø¯Ø± Ø´Ø¯",
        "configuration_imported": "âœ… Ù¾ÛŒÚ©Ø±Ø¨Ù†Ø¯ÛŒ Ø¨Ø§ Ù…ÙˆÙÙ‚ÛŒØª ÙˆØ§Ø±Ø¯ Ø´Ø¯",
        "reset_to_defaults": "ðŸ”„ Ø¨Ø§Ø²Ú¯Ø±Ø¯Ø§Ù†ÛŒ Ø¨Ù‡ Ø­Ø§Ù„Øª Ù¾ÛŒØ´â€ŒÙØ±Ø¶",
        "confirm_reset": "âš ï¸ Ø§ÛŒÙ† Ø¹Ù…Ù„ Ù‡Ù…Ù‡ ØªÙ†Ø¸ÛŒÙ…Ø§Øª Ø±Ø§ Ø¨Ù‡ Ù…Ù‚Ø§Ø¯ÛŒØ± Ù¾ÛŒØ´â€ŒÙØ±Ø¶ Ø¨Ø§Ø²Ù…ÛŒâ€ŒÚ¯Ø±Ø¯Ø§Ù†Ø¯. Ø§Ø¯Ø§Ù…Ù‡ØŸ",
        "reset_confirmed": "âœ… Ù¾ÛŒÚ©Ø±Ø¨Ù†Ø¯ÛŒ Ø¨Ù‡ Ø­Ø§Ù„Øª Ù¾ÛŒØ´â€ŒÙØ±Ø¶ Ø¨Ø§Ø²Ú¯Ø±Ø¯Ø§Ù†Ø¯Ù‡ Ø´Ø¯",
        "game_mode_settings": "ðŸŽ® ØªÙ†Ø¸ÛŒÙ…Ø§Øª Ø­Ø§Ù„Øª Ø¨Ø§Ø²ÛŒ",
        "difficulty_settings": "ðŸ“Š ØªÙ†Ø¸ÛŒÙ…Ø§Øª Ø³Ø®ØªÛŒ",
        "economy_settings": "ðŸ’° ØªÙ†Ø¸ÛŒÙ…Ø§Øª Ø§Ù‚ØªØµØ§Ø¯ÛŒ",
        "combat_settings": "âš”ï¸ ØªÙ†Ø¸ÛŒÙ…Ø§Øª Ù†Ø¨Ø±Ø¯",
        "weapon_multipliers": "ðŸ”« Ø¶Ø±Ø§ÛŒØ¨ Ø¢Ø³ÛŒØ¨ ØªØ³Ù„ÛŒØ­Ø§Øª",
        "defense_effectiveness": "ðŸ›¡ï¸ Ø§Ø«Ø±Ø¨Ø®Ø´ÛŒ Ø¯ÙØ§Ø¹",
        "level_system": "ðŸ“ˆ Ø³ÛŒØ³ØªÙ… Ø³Ø·Ø­",
        "experience_settings": "â­ ØªÙ†Ø¸ÛŒÙ…Ø§Øª ØªØ¬Ø±Ø¨Ù‡",
        "feature_enabled": "âœ… ÙØ¹Ø§Ù„",
        "feature_disabled": "âŒ ØºÛŒØ±ÙØ¹Ø§Ù„",
        "toggle_feature": "ðŸ”„ ØªØºÛŒÛŒØ± ÙˆØ¶Ø¹ÛŒØª ÙˆÛŒÚ˜Ú¯ÛŒ",
        "advanced_settings": "âš™ï¸ ØªÙ†Ø¸ÛŒÙ…Ø§Øª Ù¾ÛŒØ´Ø±ÙØªÙ‡",
        "developer_mode": "ðŸ‘¨â€ðŸ’» Ø­Ø§Ù„Øª ØªÙˆØ³Ø¹Ù‡â€ŒØ¯Ù‡Ù†Ø¯Ù‡",
        "debug_information": "ðŸ› Ø§Ø·Ù„Ø§Ø¹Ø§Øª Ø¯ÛŒØ¨Ø§Ú¯",
        "system_status": "ðŸ“Š ÙˆØ¶Ø¹ÛŒØª Ø³ÛŒØ³ØªÙ…",
        "performance_metrics": "ðŸ“ˆ Ù…Ø¹ÛŒØ§Ø±Ù‡Ø§ÛŒ Ø¹Ù…Ù„Ú©Ø±Ø¯",
        "configuration_validation": "âœ… Ø§Ø¹ØªØ¨Ø§Ø±Ø³Ù†Ø¬ÛŒ Ù¾ÛŒÚ©Ø±Ø¨Ù†Ø¯ÛŒ",
        "validation_passed": "âœ… Ù‡Ù…Ù‡ ØªÙ†Ø¸ÛŒÙ…Ø§Øª Ù…Ø¹ØªØ¨Ø± Ù‡Ø³ØªÙ†Ø¯",
        "validation_failed": "âŒ Ø§Ø¹ØªØ¨Ø§Ø±Ø³Ù†Ø¬ÛŒ Ù¾ÛŒÚ©Ø±Ø¨Ù†Ø¯ÛŒ Ù†Ø§Ù…ÙˆÙÙ‚ Ø¨ÙˆØ¯",
        "backup_configuration": "ðŸ’¾ Ù¾Ø´ØªÛŒØ¨Ø§Ù†â€ŒÚ¯ÛŒØ±ÛŒ Ø§Ø² Ù¾ÛŒÚ©Ø±Ø¨Ù†Ø¯ÛŒ",
        "restore_configuration": "ðŸ”„ Ø¨Ø§Ø²ÛŒØ§Ø¨ÛŒ Ù¾ÛŒÚ©Ø±Ø¨Ù†Ø¯ÛŒ",
        "configuration_help": "â“ Ø±Ø§Ù‡Ù†Ù…Ø§ÛŒ Ù¾ÛŒÚ©Ø±Ø¨Ù†Ø¯ÛŒ",
        "setting_description": "ðŸ“ ØªÙˆØ¶ÛŒØ­Ø§Øª ØªÙ†Ø¸ÛŒÙ…Ø§Øª",
        "recommended_value": "ðŸ’¡ Ù…Ù‚Ø¯Ø§Ø± ØªÙˆØµÛŒÙ‡ Ø´Ø¯Ù‡",
        "current_value": "ðŸ“Š Ù…Ù‚Ø¯Ø§Ø± ÙØ¹Ù„ÛŒ",
        "default_value": "ðŸ”§ Ù…Ù‚Ø¯Ø§Ø± Ù¾ÛŒØ´â€ŒÙØ±Ø¶",
        "apply_changes": "âœ… Ø§Ø¹Ù…Ø§Ù„ ØªØºÛŒÛŒØ±Ø§Øª",
        "cancel_changes": "âŒ Ù„ØºÙˆ ØªØºÛŒÛŒØ±Ø§Øª",
        "unsaved_changes": "âš ï¸ Ø´Ù…Ø§ ØªØºÛŒÛŒØ±Ø§Øª Ø°Ø®ÛŒØ±Ù‡ Ù†Ø´Ø¯Ù‡â€ŒØ§ÛŒ Ø¯Ø§Ø±ÛŒØ¯",
        "save_before_exit": "ðŸ’¾ Ù‚Ø¨Ù„ Ø§Ø² Ø®Ø±ÙˆØ¬ ØªØºÛŒÛŒØ±Ø§Øª Ø±Ø§ Ø°Ø®ÛŒØ±Ù‡ Ú©Ù†ÛŒØ¯ØŸ",
        
        # Stats Messages (Persian)
        "stats_loading": "Ø¯Ø± Ø­Ø§Ù„ Ø¨Ø§Ø±Ú¯Ø°Ø§Ø±ÛŒ Ø¢Ù…Ø§Ø±...",
        "stats_error": "âŒ Ø®Ø·Ø§ Ø¯Ø± Ø¨Ø§Ø±Ú¯Ø°Ø§Ø±ÛŒ Ø¢Ù…Ø§Ø±.",
        "stats_no_data": "Ù‡Ù†ÙˆØ² Ø¯Ø§Ø¯Ù‡â€ŒØ§ÛŒ Ù…ÙˆØ¬ÙˆØ¯ Ù†ÛŒØ³Øª. Ø´Ø±ÙˆØ¹ Ø¨Ù‡ Ø¨Ø§Ø²ÛŒ Ú©Ù†ÛŒØ¯ ØªØ§ Ø¢Ù…Ø§Ø±ØªØ§Ù† Ø±Ø§ Ø¨Ø¨ÛŒÙ†ÛŒØ¯!",
        "stats_updated": "âœ… Ø¢Ù…Ø§Ø± Ø¨Ø±ÙˆØ²Ø±Ø³Ø§Ù†ÛŒ Ø´Ø¯!",
        "rank_improved": "ðŸŽ‰ Ø±ØªØ¨Ù‡ Ø´Ù…Ø§ Ø¨Ù‡Ø¨ÙˆØ¯ ÛŒØ§ÙØª!",
        "new_achievement": "ðŸ† Ø¯Ø³ØªØ§ÙˆØ±Ø¯ Ø¬Ø¯ÛŒØ¯ Ø¨Ø§Ø² Ø´Ø¯!",
        "milestone_reached": "ðŸŽ¯ Ù†Ù‚Ø·Ù‡ Ø¹Ø·Ù Ø­Ø§ØµÙ„ Ø´Ø¯!",
        
        # Legacy Stats (maintaining compatibility) (Persian)
        "stats_title": "Ø¢Ù…Ø§Ø± Ú¯Ø±ÙˆÙ‡",
        "stats_top_players": "Ø¨Ø±ØªØ±ÛŒÙ† Ø¨Ø§Ø²ÛŒÚ©Ù†Ø§Ù†",
        "stats_no_players": "Ù‡ÛŒÚ† Ø¨Ø§Ø²ÛŒÚ©Ù†ÛŒ Ù¾ÛŒØ¯Ø§ Ù†Ø´Ø¯",
        "stats_general": "Ø¢Ù…Ø§Ø± Ø¹Ù…ÙˆÙ…ÛŒ",
        "stats_total_attacks": "Ú©Ù„ Ø­Ù…Ù„Ø§Øª",
        "stats_most_used_weapon": "Ù¾Ø±Ú©Ø§Ø±Ø¨Ø±Ø¯ØªØ±ÛŒÙ† ØªØ³Ù„ÛŒØ­",
        "medals_emoji": "ðŸ…",
        
        # General.py Persian translations
        "start_message": "ðŸ¤– Ø¨Ù‡ {bot_name} Ø®ÙˆØ´ Ø¢Ù…Ø¯ÛŒØ¯!\n\nðŸŽ® Ø´Ù…Ø§ Ø¢Ù…Ø§Ø¯Ù‡â€ŒØ§ÛŒØ¯ ØªØ§ Ø¯Ø± Ø¨Ø²Ø±Ú¯ØªØ±ÛŒÙ† Ù†Ø¨Ø±Ø¯ ØªÙ„Ú¯Ø±Ø§Ù…ÛŒ Ø´Ø±Ú©Øª Ú©Ù†ÛŒØ¯! Ø¨Ø§ Ø³Ù„Ø§Ø­â€ŒÙ‡Ø§ÛŒ Ù¾ÛŒØ´Ø±ÙØªÙ‡ØŒ Ø§Ø³ØªØ±Ø§ØªÚ˜ÛŒâ€ŒÙ‡Ø§ÛŒ Ù‡ÙˆØ´Ù…Ù†Ø¯Ø§Ù†Ù‡ Ùˆ ØªÛŒÙ…â€ŒØ³Ø§Ø²ÛŒ Ù‚Ø¯Ø±ØªÙ…Ù†Ø¯ØŒ Ø±Ø§Ù‡ Ø®ÙˆØ¯ Ø±Ø§ ØªØ§ Ù‚Ù„Ù‡ Ù¾ÛŒØ¯Ø§ Ú©Ù†ÛŒØ¯.\n\nðŸ’Ž ÙˆÛŒÚ˜Ú¯ÛŒâ€ŒÙ‡Ø§ÛŒ Ø¬Ø¯ÛŒØ¯ Ù†Ø³Ø®Ù‡ 2.0:\nâ€¢ ðŸ… Ø³ÛŒØ³ØªÙ… Ø§Ù‚ØªØµØ§Ø¯ Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ø¨Ø§ Ù…Ø¯Ø§Ù„â€ŒÙ‡Ø§\nâ€¢ â­ Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§ÛŒ ÙˆÛŒÚ˜Ù‡ Ø¨Ø§ Ø³ØªØ§Ø±Ù‡â€ŒÙ‡Ø§ÛŒ ØªÙ„Ú¯Ø±Ø§Ù…\nâ€¢ ðŸ›¡ï¸ Ø³ÛŒØ³ØªÙ… Ø¯ÙØ§Ø¹ÛŒ Ú†Ù†Ø¯Ù„Ø§ÛŒÙ‡\nâ€¢ ðŸŒ Ù¾Ø´ØªÛŒØ¨Ø§Ù†ÛŒ Ú©Ø§Ù…Ù„ Ø§Ø² Ø²Ø¨Ø§Ù† ÙØ§Ø±Ø³ÛŒ\nâ€¢ ðŸ“Š Ø¢Ù…Ø§Ø± Ùˆ ØªØ­Ù„ÛŒÙ„â€ŒÙ‡Ø§ÛŒ Ù¾ÛŒØ´Ø±ÙØªÙ‡",
        "quick_stats": "Ø¢Ù…Ø§Ø± Ø³Ø±ÛŒØ¹",
        "level": "Ø³Ø·Ø­", 
        "score": "Ø§Ù…ØªÛŒØ§Ø²",
        "hp": "HP",
        "attack_button": "Ø­Ù…Ù„Ù‡",
        "stats_button": "Ø¢Ù…Ø§Ø±",
        "shop_button": "ÙØ±ÙˆØ´Ú¯Ø§Ù‡",
        "inventory_button": "Ø§Ù†Ø¨Ø§Ø±",
        "help_button": "Ø±Ø§Ù‡Ù†Ù…Ø§",
        "language_button": "Ø²Ø¨Ø§Ù†",
        "leaderboard_button": "Ø¬Ø¯ÙˆÙ„ Ø§Ù…ØªÛŒØ§Ø²Ø§Øª",
        "error_generic": "Ù…ØªØ£Ø³ÙÛŒÙ…ØŒ Ø¯Ø± Ù¾Ø±Ø¯Ø§Ø²Ø´ Ø¯Ø±Ø®ÙˆØ§Ø³Øª Ø´Ù…Ø§ Ø®Ø·Ø§ÛŒÛŒ Ø±Ø® Ø¯Ø§Ø¯.",
        "profile_title": "Ù¾Ø±ÙˆÙØ§ÛŒÙ„ Ú©Ø§Ø±Ø¨Ø±",
        "statistics": "Ø¢Ù…Ø§Ø±Ù‡Ø§",
        "combat_stats": "Ø¢Ù…Ø§Ø± Ù†Ø¨Ø±Ø¯",
        "total_attacks": "Ú©Ù„ Ø­Ù…Ù„Ø§Øª",
        "total_damage": "Ú©Ù„ Ø¢Ø³ÛŒØ¨",
        "times_attacked": "Ø¯ÙØ¹Ø§Øª Ù…ÙˆØ±Ø¯ Ø­Ù…Ù„Ù‡ Ù‚Ø±Ø§Ø± Ú¯ÛŒØ±ÛŒ",
        "join_date": "ØªØ§Ø±ÛŒØ® Ø¹Ø¶ÙˆÛŒØª",
        "attack_user": "Ø­Ù…Ù„Ù‡ Ø¨Ù‡ Ú©Ø§Ø±Ø¨Ø±",
        "no_players": "Ù‡ÛŒÚ† Ø¨Ø§Ø²ÛŒÚ©Ù†ÛŒ Ø¯Ø± Ø§ÛŒÙ† Ú†Øª ÛŒØ§ÙØª Ù†Ø´Ø¯.",
        "leaderboard_title": "Ø¬Ø¯ÙˆÙ„ Ø§Ù…ØªÛŒØ§Ø²Ø§Øª Ú†Øª",
        "points": "Ø§Ù…ØªÛŒØ§Ø²",
        "your_position": "Ù…ÙˆÙ‚Ø¹ÛŒØª Ø´Ù…Ø§",
        "refresh": "ØªØ§Ø²Ù‡â€ŒØ³Ø§Ø²ÛŒ",
        "chat_stats_title": "Ø¢Ù…Ø§Ø± Ú†Øª",
        "total_players": "Ú©Ù„ Ø¨Ø§Ø²ÛŒÚ©Ù†Ø§Ù†",
        "average_level": "Ù…ÛŒØ§Ù†Ú¯ÛŒÙ† Ø³Ø·Ø­",
        "most_active_attacker": "ÙØ¹Ø§Ù„â€ŒØªØ±ÛŒÙ† Ù…Ù‡Ø§Ø¬Ù…",
        "shop_coming_soon": "ÙØ±ÙˆØ´Ú¯Ø§Ù‡ Ø¨Ù‡ Ø²ÙˆØ¯ÛŒ!",
        "inventory_coming_soon": "Ø§Ù†Ø¨Ø§Ø± Ø¨Ù‡ Ø²ÙˆØ¯ÛŒ!",
        "language_selection": "ðŸŒ Ø²Ø¨Ø§Ù† Ø®ÙˆØ¯ Ø±Ø§ Ø§Ù†ØªØ®Ø§Ø¨ Ú©Ù†ÛŒØ¯:",
        "language_changed": "âœ… Ø²Ø¨Ø§Ù† Ø¨Ø§ Ù…ÙˆÙÙ‚ÛŒØª ØªØºÛŒÛŒØ± Ú©Ø±Ø¯!",
        
        # Help.py Persian translations  
        "comprehensive_commands": "Ø±Ø§Ù‡Ù†Ù…Ø§ÛŒ Ú©Ø§Ù…Ù„ Ø¯Ø³ØªÙˆØ±Ø§Øª",
        "combat_commands": "Ø¯Ø³ØªÙˆØ±Ø§Øª Ù†Ø¨Ø±Ø¯",
        "info_commands": "Ø¯Ø³ØªÙˆØ±Ø§Øª Ø§Ø·Ù„Ø§Ø¹Ø§ØªÛŒ", 
        "shop_commands": "Ø¯Ø³ØªÙˆØ±Ø§Øª ÙØ±ÙˆØ´Ú¯Ø§Ù‡",
        "utility_commands": "Ø¯Ø³ØªÙˆØ±Ø§Øª Ú©Ø§Ø±Ø¨Ø±Ø¯ÛŒ",
        "premium_commands": "Ø¯Ø³ØªÙˆØ±Ø§Øª ÙˆÛŒÚ˜Ù‡",
        "tips_section": "Ù†Ú©Ø§Øª Ø³Ø±ÛŒØ¹",
        "back_to_help": "Ø¨Ø§Ø²Ú¯Ø´Øª Ø¨Ù‡ Ù…Ù†ÙˆÛŒ Ø±Ø§Ù‡Ù†Ù…Ø§",
        "weapons_guide": "Ø±Ø§Ù‡Ù†Ù…Ø§ÛŒ ØªØ³Ù„ÛŒØ­Ø§Øª",
        "back_to_combat": "Ø¨Ø§Ø²Ú¯Ø´Øª Ø¨Ù‡ Ù†Ø¨Ø±Ø¯",
        "main_help": "Ø±Ø§Ù‡Ù†Ù…Ø§ÛŒ Ø§ØµÙ„ÛŒ",
        "combat_system_guide": "Ø±Ø§Ù‡Ù†Ù…Ø§ÛŒ Ø³ÛŒØ³ØªÙ… Ù†Ø¨Ø±Ø¯",
        "how_to_attack": "Ù†Ø­ÙˆÙ‡ Ø­Ù…Ù„Ù‡ Ú©Ø±Ø¯Ù†",
        "damage_calculation": "Ø³ÛŒØ³ØªÙ… Ø¢Ø³ÛŒØ¨",
        "defense_system": "Ø³ÛŒØ³ØªÙ… Ø¯ÙØ§Ø¹ÛŒ",
        "rewards_system": "Ø³ÛŒØ³ØªÙ… Ù¾Ø§Ø¯Ø§Ø´",
        "cooldowns": "Ù…Ø­Ø¯ÙˆØ¯ÛŒØªâ€ŒÙ‡Ø§ Ùˆ Ø²Ù…Ø§Ù† Ø§Ù†ØªØ¸Ø§Ø±",
        "weapons_detail": "ØªØ³Ù„ÛŒØ­Ø§Øª",
        "stats_detail": "Ø¢Ù…Ø§Ø±Ù‡Ø§",
        "shop_system_guide": "Ø±Ø§Ù‡Ù†Ù…Ø§ÛŒ Ø³ÛŒØ³ØªÙ… ÙØ±ÙˆØ´Ú¯Ø§Ù‡ Ùˆ Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§",
        "currency_types": "Ø§Ù†ÙˆØ§Ø¹ Ø§Ø±Ø²",
        "item_categories": "Ø¯Ø³ØªÙ‡â€ŒØ¨Ù†Ø¯ÛŒ Ø¢ÛŒØªÙ…â€ŒÙ‡Ø§",
        "shopping_guide": "Ø±Ø§Ù‡Ù†Ù…Ø§ÛŒ Ø®Ø±ÛŒØ¯",
        "inventory_management": "Ù…Ø¯ÛŒØ±ÛŒØª Ø§Ù†Ø¨Ø§Ø±",
        "shopping_tips": "Ù†Ú©Ø§Øª Ø®Ø±ÛŒØ¯",
        "open_shop": "Ø¨Ø§Ø² Ú©Ø±Ø¯Ù† ÙØ±ÙˆØ´Ú¯Ø§Ù‡",
        "view_inventory": "Ù…Ø´Ø§Ù‡Ø¯Ù‡ Ø§Ù†Ø¨Ø§Ø±",
        "statistics_guide": "Ø±Ø§Ù‡Ù†Ù…Ø§ÛŒ Ø¢Ù…Ø§Ø± Ùˆ Ù¾ÛŒØ´Ø±ÙØª",
        "player_stats": "Ø¢Ù…Ø§Ø± Ø¨Ø§Ø²ÛŒÚ©Ù†",
        "progression_system": "Ø³ÛŒØ³ØªÙ… Ù¾ÛŒØ´Ø±ÙØª",
        "available_stats": "Ø¯Ø³ØªÙˆØ±Ø§Øª Ù…ÙˆØ¬ÙˆØ¯",
        "improvement_tips": "Ù†Ú©Ø§Øª Ø¨Ù‡Ø¨ÙˆØ¯",
        "view_profile": "Ù…Ø´Ø§Ù‡Ø¯Ù‡ Ù¾Ø±ÙˆÙØ§ÛŒÙ„",
        "view_leaderboard": "Ø¬Ø¯ÙˆÙ„ Ø§Ù…ØªÛŒØ§Ø²Ø§Øª",
        "faq_title": "Ø³ÙˆØ§Ù„Ø§Øª Ù…ØªØ¯Ø§ÙˆÙ„",
        "contact_support": "Ø±Ø§Ù‡Ù†Ù…Ø§ÛŒÛŒ Ø¨ÛŒØ´ØªØ±",
    }
    
    logger.info("Translations loaded successfully for both English and Persian")

# Initialize translations on module load
load_translations()

def get(key: str, lang: str = "en", default: str = None) -> str:
    """
    Get a translation for a specific key and language
    
    Args:
        key: The translation key
        lang: Language code (en/fa)
        default: Default value if key not found
    
    Returns:
        Translated string or default/fallback value
    """
    try:
        if lang not in T:
            lang = "en"  # Fallback to English
        
        if key in T[lang]:
            return T[lang][key]
        elif key in T["en"]:  # Fallback to English
            return T["en"][key]
        elif default:
            return default
        else:
            return f"[Missing: {key}]"
    except Exception as e:
        logger.error(f"Error getting translation for key '{key}': {e}")
        return default or f"[Error: {key}]"

def format_text(key: str, lang: str = "en", *args, **kwargs) -> str:
    """
    Get a translation and format it with provided arguments
    
    Args:
        key: The translation key
        lang: Language code (en/fa)
        *args: Positional arguments for formatting
        **kwargs: Keyword arguments for formatting
    
    Returns:
        Formatted translated string
    """
    try:
        text = get(key, lang)
        if args:
            return text.format(*args)
        elif kwargs:
            return text.format(**kwargs)
        else:
            return text
    except (KeyError, IndexError, ValueError) as e:
        logger.error(f"Error formatting translation for key '{key}': {e}")
        return get(key, lang)  # Return unformatted text

def get_supported_languages() -> list:
    """Get list of supported language codes"""
    return list(T.keys())

def is_language_supported(lang: str) -> bool:
    """Check if a language is supported"""
    return lang in T

def detect_language_from_text(text: str) -> str:
    """
    Detect language from text content
    
    Args:
        text: Text to analyze
    
    Returns:
        Detected language code
    """
    try:
        import re
        if not text:
            return "en"
        
        # Count Persian characters
        persian_chars = len(re.findall(r'[\u0600-\u06FF]', text))
        total_chars = len(text.replace(' ', ''))
        
        # If more than 30% Persian characters, assume Persian
        if total_chars > 0 and (persian_chars / total_chars) > 0.3:
            return "fa"
        else:
            return "en"
    except Exception as e:
        logger.error(f"Error detecting language: {e}")
        return "en"

def get_language_name(lang_code: str, in_language: str = "en") -> str:
    """
    Get the display name of a language
    
    Args:
        lang_code: Language code to get name for
        in_language: Language to display the name in
    
    Returns:
        Language display name
    """
    language_names = {
        "en": {
            "en": "English",
            "fa": "Persian"
        },
        "fa": {
            "en": "English (Ø§Ù†Ú¯Ù„ÛŒØ³ÛŒ)",
            "fa": "ÙØ§Ø±Ø³ÛŒ"
        }
    }
    
    return language_names.get(lang_code, {}).get(in_language, lang_code)

def format_number_localized(number: int, lang: str = "en") -> str:
    """
    Format number according to language locale
    
    Args:
        number: Number to format
        lang: Language code
    
    Returns:
        Formatted number string
    """
    try:
        if lang == "fa":
            # Persian digit conversion
            persian_digits = "Û°Û±Û²Û³Û´ÛµÛ¶Û·Û¸Û¹"
            english_digits = "0123456789"
            
            formatted = f"{number:,}"
            
            # Convert to Persian digits
            for eng, per in zip(english_digits, persian_digits):
                formatted = formatted.replace(eng, per)
            
            return formatted
        else:
            return f"{number:,}"
    except Exception as e:
        logger.error(f"Error formatting number {number}: {e}")
        return str(number)

def get_emoji_for_item(item_type: str) -> str:
    """
    Get emoji for item type
    
    Args:
        item_type: Type of item
    
    Returns:
        Appropriate emoji
    """
    emoji_map = {
        "weapon": "ðŸ”«",
        "shield": "ðŸ›¡ï¸",
        "missile": "ðŸš€",
        "bomb": "ðŸ’£",
        "nuclear": "â˜¢ï¸",
        "defense": "ðŸ›¡ï¸",
        "attack": "âš”ï¸",
        "medal": "ðŸ…",
        "star": "â­",
        "energy": "âš¡",
        "repair": "ðŸ”§",
        "boost": "ðŸ’ª"
    }
    
    return emoji_map.get(item_type, "ðŸ“¦")

def get_direction_for_language(lang: str) -> str:
    """
    Get text direction for language
    
    Args:
        lang: Language code
    
    Returns:
        Text direction (ltr/rtl)
    """
    if lang == "fa":
        return "rtl"
    else:
        return "ltr"

def create_localized_keyboard_text(buttons: list, lang: str = "en") -> list:
    """
    Create localized keyboard button texts
    
    Args:
        buttons: List of button keys
        lang: Language code
    
    Returns:
        List of localized button texts
    """
    localized_buttons = []
    for button_key in buttons:
        localized_text = get(button_key, lang, button_key)
        localized_buttons.append(localized_text)
    return localized_buttons

def get_time_format(lang: str = "en") -> str:
    """
    Get time format pattern for language
    
    Args:
        lang: Language code
    
    Returns:
        Time format pattern
    """
    if lang == "fa":
        return "%Y/%m/%d %H:%M"  # Persian date format
    else:
        return "%B %d, %Y %H:%M"  # English date format

def get_currency_text(currency_type: str, lang: str = "en") -> str:
    """
    Get localized currency text
    
    Args:
        currency_type: Type of currency (medals, stars, etc.)
        lang: Language code
    
    Returns:
        Localized currency text
    """
    currency_keys = {
        "medals": "medals",
        "stars": "tg_stars", 
        "medal": "medals",
        "star": "tg_stars"
    }
    
    key = currency_keys.get(currency_type, currency_type)
    return get(key, lang, currency_type)

def validate_translation_completeness() -> dict:
    """
    Validate that all translation keys exist in all languages
    
    Returns:
        Dictionary with validation results
    """
    results = {
        "complete": True,
        "missing_keys": {},
        "extra_keys": {}
    }
    
    try:
        # Get all keys from English (reference language)
        en_keys = set(T["en"].keys())
        
        for lang_code, translations in T.items():
            if lang_code == "en":
                continue
                
            lang_keys = set(translations.keys())
            
            # Find missing keys
            missing = en_keys - lang_keys
            if missing:
                results["missing_keys"][lang_code] = list(missing)
                results["complete"] = False
            
            # Find extra keys
            extra = lang_keys - en_keys
            if extra:
                results["extra_keys"][lang_code] = list(extra)
        
        logger.info(f"Translation validation complete. Status: {'âœ… Complete' if results['complete'] else 'âš ï¸ Incomplete'}")
        
        return results
    except Exception as e:
        logger.error(f"Error validating translations: {e}")
        return {"complete": False, "error": str(e)}

def get_fallback_text(key: str) -> str:
    """
    Get fallback text for missing translations
    
    Args:
        key: Translation key
    
    Returns:
        Fallback text
    """
    # Convert snake_case to readable text
    readable = key.replace('_', ' ').title()
    return f"[{readable}]"

# Convenience function for shorter syntax
def t(key: str, lang: str = "en", *args, **kwargs) -> str:
    """
    Shorthand function for getting translated text
    
    Args:
        key: Translation key
        lang: Language code
        *args: Positional formatting arguments
        **kwargs: Keyword formatting arguments
    
    Returns:
        Translated and formatted text
    """
    return format_text(key, lang, *args, **kwargs)

# Module initialization
logger.info("Translation module initialized with comprehensive bilingual support")
logger.info(f"Supported languages: {', '.join(get_supported_languages())}")

# Validate translations on startup
validation_results = validate_translation_completeness()
if not validation_results["complete"]:
    logger.warning("Some translation keys are missing. Check validation results.")
    for lang, missing_keys in validation_results.get("missing_keys", {}).items():
        logger.warning(f"Missing keys in {lang}: {missing_keys[:5]}{'...' if len(missing_keys) > 5 else ''}")

# Export main translation getter as T for compatibility
class TranslationHelper:
    """Helper class for easier translation access"""
    
    @staticmethod
    def get(key: str, lang: str = "en") -> str:
        return get(key, lang)
    
    @staticmethod
    def format(key: str, lang: str = "en", *args, **kwargs) -> str:
        return format_text(key, lang, *args, **kwargs)
    
    def __getitem__(self, lang: str) -> dict:
        return T.get(lang, T["en"])

# Create global instance for easier access
T_HELPER = TranslationHelper()

