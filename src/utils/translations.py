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
        "welcome": "🎮 PvP missile fights inside your group. Use /help to learn how to collect 🏅 medals.",
        "help": (
          "🎮 <b>How to play</b>\n"
          "• Reply to someone and send /attack — launch a missile\n"
          "• /defend — bring Patriot interceptors online\n"
          "• /shield — full Aegis shield for hours\n"
          "• /status — your stats & defenses\n"
          "• /shop — buy equipment with Medals\n"
          "• /stars — view TG Stars balance and premium items 💎\n"
          "• /bonus — daily medals\n"
          "• /inv — your weapons arsenal\n"
          "• /top — group leaderboard\n"
          "• /score — view your activity level\n"
          "• /quiz — participate in quizzes to earn rewards\n"
          "• /lang — switch language\n\n"
          "🚫 You cannot target the bot itself."
        ),
        "lang_choose": "Choose language:",
        "lang_set_en": "Language set to English.",
        "lang_set_fa": "زبان به فارسی تغییر کرد.",
        "status_self": "<b>{name}</b>\n🏅 Medals: <b>{medals}</b> | 🏆 Score: <b>{score}</b>\n🛡️ Shield: {shield} | 🛰️ Intercept: {intercept}",
        "status_hint": "Reply to someone with /attack to strike!",
        "bonus_received": "🎁 You received your daily bonus: <b>{amount}</b> medals!",
        "bonus_already": "⏳ You already claimed your daily bonus. Try again tomorrow!",
        "shield_activated": "🛡️ Aegis shield activated for <b>{hours}</b> hours!",
        "shield_no_medals": "❌ Not enough medals! You need <b>{cost}</b> medals to activate shield.",
        "shield_already": "⚠️ You already have an active shield ({time_left}m remaining).",
        "intercept_activated": "🛰️ Patriot defense system activated for <b>{hours}</b> hours!",
        "intercept_no_medals": "❌ Not enough medals! You need <b>{cost}</b> medals to activate defense system.",
        "intercept_already": "⚠️ You already have an active defense system ({time_left}m remaining).",
        "attack_yourself": "🤦‍♂️ You can't attack yourself!",
        "attack_bot": "🤖 You can't attack the bot!",
        "attack_quota": "⚠️ You've reached your attack limit for today. Try again tomorrow!",
        "attack_shielded": "🛡️ Your attack was blocked by {name}'s Aegis Shield!",
        "attack_intercepted": "🛰️ Your attack was intercepted by {name}'s Patriot Defense System! They gained <b>{bonus}%</b> of your attack power!",
        "attack_success": "💥 You hit {name} for <b>{damage}</b> damage!",
        "shop": "🛍️ <b>Military Equipment Shop</b> — pick an item:",
        "shop_item": "{stars} {name} — {price} medals",
        "shop_premium_item": "💎 {name} — {price} TG Stars",
        "shop_no_medals": "❌ Not enough medals! You need <b>{price}</b> medals to buy this item.",
        "shop_no_stars": "❌ Not enough TG Stars! You need <b>{price}</b> TG Stars to buy this item.",
        "shop_purchased": "✅ You purchased {name} for <b>{price}</b> medals!",
        "shop_premium_purchased": "✅ You purchased {name} for <b>{price}</b> TG Stars!",
        "stars_balance": "<b>💎 TG Stars Balance</b>\n\nYou have <b>{stars}</b> TG Stars in your account.\n\nTG Stars can be used to purchase premium items in the shop.\nUse /shop to browse available items.",
        
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
        "purchase_successful": "✅ Successfully purchased {item_name} for {price} {currency}!",
        "purchase_failed": "❌ Purchase failed. Please try again.",
        "purchase_error": "❌ Error processing purchase.",
        "item_not_found": "❌ Item not found.",
        "insufficient_medals": "❌ Not enough medals!",
        "premium_info": "💎 Premium items available with TG Stars",
        
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

        "private_chat_error": "⚠️ This command only works in groups. Please use it in a group chat.",
        
        # Inventory translations
        "inventory_title": "🎒 <b>{first_name}'s Arsenal</b> (Level {level})",
        "inventory_empty": "Your arsenal is empty! Visit the /shop to get some equipment.",
        "inventory_stats": "📊 <b>Arsenal Statistics:</b>\n• Total Items: {total_items}\n• Categories: {categories}\n• Total Value: {total_value} medals",
        "inventory_categories": {
            "weapons": "🗡️ Weapons",
            "defense": "🛡️ Defense Items",
            "other": "📦 Other Items"
        },
        "use_item_menu": "🔧 <b>Use Item</b>\n\nSelect an item to use:",
        "item_used_success": "✅ You used {item_name} successfully!",
        "item_used_defense": "🛡️ {item_name} activated! Protection active for 24 hours.",
        "item_used_boost": "⚡ {item_name} used! {effect}",
        "item_not_found": "❌ Item not found in your inventory.",
        "item_already_active": "⚠️ You already have this effect active.",
        "close_button": "❌ Close",
        "back_to_inventory": "🔙 Back to Inventory",
        "use_item_button": "🔧 Use Item",
        "category_weapons": "🗡️ Weapons",
        "category_defense": "🛡️ Defense",
        "category_other": "📦 Other",
        "hp_restored": "❤️ HP restored to full!",
        "no_items_category": "No items in this category.",
        
        # Enhanced Status System Translations
        "status_dashboard": "📊 Player Status Dashboard",
        "comprehensive_status": "🎯 Comprehensive Status",
        "player_overview": "👤 Player Overview",
        "combat_status": "⚔️ Combat Status",
        "defense_status": "🛡️ Defense Status",
        "inventory_status": "📦 Inventory Status",
        "achievements_status": "🏆 Achievements",
        "detailed_analytics": "📈 Detailed Analytics",
        "status_message": "👤 <b>{first_name}'s Status</b>\n\n💰 <b>Resources:</b>\n🏅 Medals: <b>{medals:,}</b>\n⭐ TG Stars: <b>{tg_stars}</b>\n\n❤️ <b>Health:</b> <b>{hp}/100</b>\n🔥 <b>Level:</b> <b>{level}</b>\n\n🛡️ <b>Defense:</b> {defense_status}",
        "defense_status_none": "❌ No active defense",
        "defense_status_active": "✅ {item_name} ({time_left} min remaining)",
        "activate_button": "🛡️ Activate {item_name}",
        "defense_already_active": "⚠️ You already have an active defense!",
        "defense_activated": "✅ {item_name} activated for {hours} hours!",
        "item_not_owned": "❌ You don't have {item_name}",
        "view_detailed_status": "📊 View Detailed Status",
        "quick_status": "⚡ Quick Status",
        "status_analytics": "📈 Status Analytics",
        "refresh_status": "🔄 Refresh Status",
        "status_history": "📜 Status History",
        "performance_overview": "🎯 Performance Overview",
        "current_streak": "🔥 Current Streak",
        "best_streak": "🏆 Best Streak",
        "total_playtime": "⏱️ Total Playtime",
        "rank_in_chat": "🏆 Rank in Chat",
        "activity_level": "📊 Activity Level",
        "last_active": "⏰ Last Active",
        "status_comparison": "📊 Compare with Others",
        "status_trends": "📈 Status Trends",
        "weekly_progress": "📅 Weekly Progress",
        "monthly_progress": "📅 Monthly Progress",
        "status_summary": "📋 Status Summary",
        "status_breakdown": "🔍 Status Breakdown",
        
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
            "f22": "✈️",
            "moab": "💣",
            "nuclear": "☢️",
            "shield": "🛡️",
            "intercept": "🚀",
            "carrier": "🚢",
            "stealth_bomber": "🛩️",
            "mega_nuke": "💥",
            "super_aegis": "🛡️✨",
            "medal_boost": "🏅",
            "vip_status": "👑",
            "energy_drink": "⚡",
            "repair_kit": "🔧"
        },
        
        # TG Stars System Translations
        "stars_welcome": "💎 TG Stars Dashboard",
        "stars_balance_overview": "Your TG Stars Balance",
        "current_stars_balance": "Current Balance: ⭐ {stars} TG Stars",
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
        "purchase_successful_stars": "✅ Successfully purchased {item_name} with TG Stars!",
        
        # Stars Shop Integration
        "view_premium_shop": "🛒 View Premium Shop",
        "premium_catalog": "Premium Catalog",
        "exclusive_weapons": "Exclusive Weapons",
        "special_abilities": "Special Abilities",
        "item_requires_stars": "Requires ⭐ {price} TG Stars",
        "insufficient_stars": "❌ Not enough TG Stars! You need {required} more.",
        "confirm_purchase": "Confirm Purchase",
        "purchase_confirmation": "Are you sure you want to purchase {item_name} for ⭐ {price} TG Stars?",
        "confirm_yes": "✅ Yes, Purchase",
        "confirm_no": "❌ Cancel",
        
        # Stars Features
        "stars_features_list": "🌟 TG Stars Features:",
        "feature_exclusive_weapons": "• Access to exclusive premium weapons",
        "feature_special_abilities": "• Unlock special combat abilities", 
        "feature_premium_support": "• Priority customer support",
        "feature_advanced_stats": "• Advanced statistics and analytics",
        "feature_custom_themes": "• Custom themes and personalization",
        "feature_early_access": "• Early access to new features",
        
        # Error Messages
        "stars_error_generic": "❌ An error occurred with TG Stars system.",
        "stars_error_insufficient": "❌ Insufficient TG Stars balance.",
        "stars_error_item_unavailable": "❌ This item is currently unavailable.",
        "stars_error_payment": "❌ Payment processing failed.",
        "stars_error_network": "❌ Network error. Please try again.",
        
        # Help and Support
        "stars_help": "🆘 TG Stars Help",
        "stars_support": "📞 Contact Support",
        "stars_faq": "❓ Frequently Asked Questions",
        "stars_terms": "📜 Terms of Service",
        "refresh_balance": "🔄 Refresh Balance",
        "close_stars_menu": "❌ Close",
        
        # Quick Actions
        "buy_stars": "💰 Buy TG Stars",
        "view_history": "📊 View History",
        "browse_premium": "🛒 Browse Premium Items",
        "stars_settings": "⚙️ Settings",
        
        # Statistics System Translations
        "stats_dashboard": "📊 Statistics Dashboard",
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
        "view_personal": "👤 Personal Stats",
        "view_combat": "⚔️ Combat Stats",
        "view_weapons": "🔫 Weapon Stats",
        "view_achievements": "🏆 Achievements",
        "view_leaderboard": "📊 Leaderboard",
        "view_trends": "📈 Trends",
        "refresh_stats": "🔄 Refresh",
        "export_stats": "📤 Export",
        "stats_help": "🆘 Help",
        "close_stats": "❌ Close",
        
        # Enhanced Configuration System Translations
        "bot_configuration": "🔧 Bot Configuration",
        "configuration_dashboard": "📊 Configuration Dashboard",
        "game_mechanics": "🎮 Game Mechanics",
        "feature_flags": "🚩 Feature Flags",
        "security_settings": "🔐 Security Settings",
        "notification_settings": "🔔 Notification Settings",
        "performance_settings": "⚡ Performance Settings",
        "multilingual_settings": "🌐 Multilingual Settings",
        "bot_information": "🤖 Bot Information",
        "bot_version": "Version",
        "bot_description": "Description",
        "supported_languages": "Supported Languages",
        "current_language": "Current Language",
        "change_language": "🌐 Change Language",
        "language_changed": "✅ Language changed successfully!",
        "configuration_updated": "✅ Configuration updated successfully!",
        "configuration_error": "❌ Configuration update failed",
        "invalid_setting": "❌ Invalid setting value",
        "setting_saved": "✅ Setting saved: {setting_name}",
        "setting_reset": "🔄 Setting reset to default: {setting_name}",
        "export_configuration": "📤 Export Configuration",
        "import_configuration": "📥 Import Configuration",
        "configuration_exported": "✅ Configuration exported successfully",
        "configuration_imported": "✅ Configuration imported successfully",
        "reset_to_defaults": "🔄 Reset to Defaults",
        "confirm_reset": "⚠️ This will reset all settings to default values. Continue?",
        "reset_confirmed": "✅ Configuration reset to defaults",
        "game_mode_settings": "🎮 Game Mode Settings",
        "difficulty_settings": "📊 Difficulty Settings",
        "economy_settings": "💰 Economy Settings",
        "combat_settings": "⚔️ Combat Settings",
        "weapon_multipliers": "🔫 Weapon Damage Multipliers",
        "defense_effectiveness": "🛡️ Defense Effectiveness",
        "level_system": "📈 Level System",
        "experience_settings": "⭐ Experience Settings",
        "feature_enabled": "✅ Enabled",
        "feature_disabled": "❌ Disabled",
        "toggle_feature": "🔄 Toggle Feature",
        "advanced_settings": "⚙️ Advanced Settings",
        "developer_mode": "👨‍💻 Developer Mode",
        "debug_information": "🐛 Debug Information",
        "system_status": "📊 System Status",
        "performance_metrics": "📈 Performance Metrics",
        "configuration_validation": "✅ Configuration Validation",
        "validation_passed": "✅ All settings are valid",
        "validation_failed": "❌ Configuration validation failed",
        "backup_configuration": "💾 Backup Configuration",
        "restore_configuration": "🔄 Restore Configuration",
        "configuration_help": "❓ Configuration Help",
        "setting_description": "📝 Setting Description",
        "recommended_value": "💡 Recommended Value",
        "current_value": "📊 Current Value",
        "default_value": "🔧 Default Value",
        "apply_changes": "✅ Apply Changes",
        "cancel_changes": "❌ Cancel Changes",
        "unsaved_changes": "⚠️ You have unsaved changes",
        "save_before_exit": "💾 Save changes before exiting?",
        
        # Stats Messages
        "stats_loading": "Loading statistics...",
        "stats_error": "❌ Error loading statistics.",
        "stats_no_data": "No data available yet. Start playing to see your stats!",
        "stats_updated": "✅ Statistics updated!",
        "rank_improved": "🎉 Your rank has improved!",
        "new_achievement": "🏆 New achievement unlocked!",
        "milestone_reached": "🎯 Milestone reached!",
        
        # Legacy Stats (maintaining compatibility)
        "stats_title": "Group Statistics",
        "stats_top_players": "Top Players",
        "stats_no_players": "No players found",
        "stats_general": "General Statistics",
        "stats_total_attacks": "Total Attacks",
        "stats_most_used_weapon": "Most Used Weapon",
        "medals_emoji": "🏅",
    }
    
    # Persian (Farsi) translations
    T["fa"] = {
        "welcome": "🎮 نبرد موشکی بین اعضای گروه! برای یادگیری نحوه‌ی جمع‌آوری 🏅 مدال، دستور /help را ارسال کنید.",
        "help": (
          "🎮 <b>راهنمای بازی</b>\n"
          "• روی پیام فرد مورد نظر ریپلای کرده و /attack را بزنید — برای حمله موشکی\n"
          "• /defend — فعال‌سازی سامانه دفاع پاتریوت (رهگیری ۱۲ ساعت)\n"
          "• /shield — سپر محافظ ایجیس (۳ ساعت)\n"
          "• /status — مشاهده وضعیت و سیستم‌های دفاعی\n"
          "• /shop — خرید تجهیزات با مدال\n"
          "• /stars — مشاهده موجودی ستاره‌های تلگرام و آیتم‌های ویژه 💎\n"
          "• /bonus — دریافت پاداش روزانه\n"
          "• /inv — مشاهده موجودی انبار تسلیحات\n"
          "• /top — مشاهده جدول برترین‌های گروه\n"
          "• /score — مشاهده امتیاز و سطح فعالیت شما\n"
          "• /quiz — شرکت در کوییز و دریافت جایزه\n"
          "• /lang — تغییر زبان\n\n"
          "🚫 هدف قرار دادن خود بات ممنوع است."
        ),
        "lang_choose": "لطفاً زبان مورد نظر خود را انتخاب کنید:",
        "lang_set_en": "Language set to English.",
        "lang_set_fa": "زبان به فارسی تغییر کرد.",
        "status_self": "<b>{name}</b>\n🏅 مدال‌ها: <b>{medals}</b> | 🏆 امتیاز: <b>{score}</b>\n🛡️ سپر محافظ: {shield} | 🛰️ سیستم پدافند: {intercept}",
        "status_hint": "برای حمله، روی پیام فرد مورد نظر ریپلای کرده و دستور /attack را بزنید!",
        "bonus_received": "🎁 شما پاداش روزانه خود را دریافت کردید: <b>{amount}</b> مدال!",
        "bonus_already": "⏳ شما امروز پاداش روزانه خود را دریافت کرده‌اید. فردا دوباره تلاش کنید!",
        "shield_activated": "🛡️ سپر دفاعی ایجیس برای <b>{hours}</b> ساعت فعال شد!",
        "shield_no_medals": "❌ مدال کافی ندارید! برای فعال‌سازی سپر به <b>{cost}</b> مدال نیاز دارید.",
        "shield_already": "⚠️ شما در حال حاضر یک سپر فعال دارید ({time_left} دقیقه باقی‌مانده).",
        "intercept_activated": "🛰️ سیستم دفاعی پاتریوت برای <b>{hours}</b> ساعت فعال شد!",
        "intercept_no_medals": "❌ مدال کافی ندارید! برای فعال‌سازی سیستم دفاعی به <b>{cost}</b> مدال نیاز دارید.",
        "intercept_already": "⚠️ شما در حال حاضر یک سیستم دفاعی فعال دارید ({time_left} دقیقه باقی‌مانده).",
        "attack_yourself": "🤦‍♂️ شما نمی‌توانید به خودتان حمله کنید!",
        "attack_bot": "🤖 شما نمی‌توانید به بات حمله کنید!",
        "attack_quota": "⚠️ شما به سقف حملات روزانه خود رسیده‌اید. فردا دوباره تلاش کنید!",
        "attack_shielded": "🛡️ حمله شما توسط سپر ایجیس {name} دفع شد!",
        "attack_intercepted": "🛰️ حمله شما توسط سیستم دفاعی پاتریوت {name} رهگیری شد! آنها <b>{bonus}%</b> از قدرت حمله شما را دریافت کردند!",
        "attack_success": "💥 شما {name} را با <b>{damage}</b> آسیب مورد اصابت قرار دادید!",
        "shop": "🛍️ <b>فروشگاه تجهیزات نظامی</b> — یک آیتم انتخاب کنید:",
        "shop_item": "{stars} {name} — {price} مدال",
        "shop_premium_item": "💎 {name} — {price} ستاره تلگرام",
        "shop_no_medals": "❌ مدال کافی ندارید! برای خرید این آیتم به <b>{price}</b> مدال نیاز دارید.",
        "shop_no_stars": "❌ ستاره تلگرام کافی ندارید! برای خرید این آیتم به <b>{price}</b> ستاره تلگرام نیاز دارید.",
        "shop_purchased": "✅ شما {name} را با <b>{price}</b> مدال خریداری کردید!",
        "shop_premium_purchased": "✅ شما {name} را با <b>{price}</b> ستاره تلگرام خریداری کردید!",
        "stars_balance": "<b>💎 موجودی ستاره‌های تلگرام</b>\n\nشما <b>{stars}</b> ستاره تلگرام در حساب خود دارید.\n\nستاره‌های تلگرام برای خرید آیتم‌های ویژه در فروشگاه استفاده می‌شوند.\nاز دستور /shop برای مشاهده آیتم‌های موجود استفاده کنید.",
        
        # Enhanced shop translations (Persian)
        "shop_welcome": "فروشگاه تجهیزات نظامی",
        "your_balance": "موجودی شما",
        "medals": "مدال‌ها",
        "tg_stars": "ستاره‌های تلگرام",
        "shop_categories_intro": "یک دسته‌بندی را برای مشاهده آیتم‌ها انتخاب کنید:",
        "premium_items": "آیتم‌های ویژه",
        "medal_items": "آیتم‌های مدالی",
        "all_items": "همه آیتم‌ها",
        "back_to_shop": "بازگشت به فروشگاه",
        "no_items_in_category": "هیچ آیتمی در این دسته موجود نیست.",
        "description": "توضیحات",
        "damage": "آسیب",
        "duration": "مدت زمان",
        "hours": "ساعت",
        "effectiveness": "تاثیرگذاری",
        "capacity": "ظرفیت",
        "medal_bonus": "جایزه مدال",
        "price": "قیمت",
        "you_can_afford": "شما می‌توانید این آیتم را خریداری کنید!",
        "need_more_currency": "شما به {amount} {currency} بیشتر نیاز دارید",
        "buy_item": "خرید آیتم",
        "back_to_category": "بازگشت به دسته‌بندی",
        "purchase_successful": "✅ {item_name} با موفقیت به قیمت {price} {currency} خریداری شد!",
        "purchase_failed": "❌ خرید ناموفق بود. لطفاً دوباره تلاش کنید.",
        "purchase_error": "❌ خطا در پردازش خرید.",
        "item_not_found": "❌ آیتم یافت نشد.",
        "insufficient_medals": "❌ مدال کافی ندارید!",
        "premium_info": "💎 آیتم‌های ویژه با ستاره‌های تلگرام",
        
        "help_intro": "برای دریافت راهنمایی، یک دسته را انتخاب کنید:",
        "help_basic_btn": "دستورات اصلی",
        "help_attack_btn": "حمله کردن",
        "help_defense_btn": "دفاع کردن",
        "help_items_btn": "آیتم‌ها و فروشگاه",
        "help_stars_btn": "ستاره‌های تلگرام",
        "back_btn": "بازگشت",

        "help_basic": (
            "<b>دستورات اصلی</b>\n"
            "/status - وضعیت و دفاع‌های شما\n"
            "/inv - انبار تسلیحات شما\n"
            "/top - جدول برترین‌های گروه\n"
            "/bonus - دریافت پاداش روزانه"
        ),
        "help_attack": (
            "<b>حمله کردن</b>\n"
            "برای حمله به کاربر دیگر، به پیام او ریپلای کرده و از دستور /attack استفاده کنید.\n"
            "مثال: به پیام یک کاربر ریپلای کرده و `/attack` را ارسال کنید."
        ),
        "help_defense": (
            "<b>دفاع کردن</b>\n"
            "/shield - فعال کردن سپر برای جلوگیری از حملات.\n"
            "/defend - فعال کردن سیستم رهگیری برای کاهش شانس اصابت."
        ),
        "help_items": (
            "<b>آیتم‌ها و فروشگاه</b>\n"
            "/shop - خرید آیتم‌هایی مانند سپر و بمب‌های ویژه با استفاده از مدال.\n"
            "آیتم‌ها در /inv شما ذخیره می‌شوند."
        ),
        "help_stars": (
            "<b>ستاره‌های تلگرام</b>\n"
            "/stars - مشاهده موجودی ستاره‌های تلگرام و خرید آیتم‌های ویژه.\n"
            "در حال حاضر، اضافه کردن ستاره رایگان است!"
        ),
        
        # Comprehensive help system translations (Persian)
        "help_welcome": "مرکز راهنمای ترامپ‌بات",
        "recommendations_for_you": "پیشنهادات برای شما",
        "commands_help": "دستورات",
        "combat_help": "نبرد",
        "items_help": "فروشگاه و آیتم‌ها",
        "stats_help": "آمارها",
        "faq_help": "سوالات متداول",
        "main_menu": "منوی اصلی",
        "back_to_help": "بازگشت به منوی راهنما",
        "comprehensive_commands": "راهنمای کامل دستورات",
        "combat_commands": "دستورات نبرد",
        "info_commands": "دستورات اطلاعاتی",
        "shop_commands": "دستورات فروشگاه",
        "utility_commands": "دستورات کاربردی",
        "premium_commands": "دستورات ویژه",
        "tips_section": "نکات سریع",
        "weapons_guide": "راهنمای تسلیحات",
        "back_to_combat": "بازگشت به نبرد",
        "main_help": "راهنمای اصلی",
        "combat_system_guide": "راهنمای سیستم نبرد",
        "how_to_attack": "نحوه حمله کردن",
        "damage_calculation": "سیستم آسیب",
        "defense_system": "سیستم دفاعی",
        "rewards_system": "سیستم پاداش",
        "cooldowns": "محدودیت‌ها و زمان انتظار",
        "weapons_detail": "تسلیحات",
        "stats_detail": "آمارها",
        "shop_system_guide": "راهنمای فروشگاه و آیتم‌ها",
        "currency_types": "انواع ارز",
        "item_categories": "دسته‌بندی آیتم‌ها",
        "shopping_guide": "راهنمای خرید",
        "inventory_management": "مدیریت انبار",
        "shopping_tips": "نکات خرید",
        "open_shop": "باز کردن فروشگاه",
        "view_inventory": "مشاهده انبار",
        "statistics_guide": "راهنمای آمار و پیشرفت",
        "player_stats": "آمار بازیکن",
        "combat_stats": "آمار نبرد",
        "progression_system": "سیستم پیشرفت",
        "available_stats": "دستورات موجود",
        "improvement_tips": "نکات بهبود",
        "view_profile": "مشاهده پروفایل",
        "view_leaderboard": "جدول امتیازات",
        "faq_title": "سوالات متداول",
        "contact_support": "راهنمایی بیشتر",
        "back_button": "بازگشت",
        
        "private_chat_error": "⚠️ این دستور فقط در گروه‌ها کار می‌کند. لطفاً آن را در یک گروه استفاده کنید.",
        
        # Inventory translations
        "inventory_title": "🎒 <b>انبار تسلیحات {first_name}</b> (سطح {level})",
        "inventory_empty": "انبار تسلیحات شما خالی است! از /shop بازدید کنید تا تجهیزات تهیه کنید.",
        "inventory_stats": "📊 <b>آمار انبار تسلیحات:</b>\n• کل آیتم‌ها: {total_items}\n• دسته‌بندی‌ها: {categories}\n• ارزش کل: {total_value} مدال",
        "inventory_categories": {
            "weapons": "🗡️ تسلیحات",
            "defense": "🛡️ آیتم‌های دفاعی",
            "other": "📦 سایر آیتم‌ها"
        },
        "use_item_menu": "🔧 <b>استفاده از آیتم</b>\n\nیک آیتم برای استفاده انتخاب کنید:",
        "item_used_success": "✅ شما با موفقیت از {item_name} استفاده کردید!",
        "item_used_defense": "🛡️ {item_name} فعال شد! محافظت برای ۲۴ ساعت فعال است.",
        "item_used_boost": "⚡ {item_name} استفاده شد! {effect}",
        "item_not_found": "❌ آیتم در انبار شما یافت نشد.",
        "item_already_active": "⚠️ شما قبلاً این اثر را فعال دارید.",
        "close_button": "❌ بستن",
        "back_to_inventory": "🔙 بازگشت به انبار",
        "use_item_button": "🔧 استفاده از آیتم",
        "category_weapons": "🗡️ تسلیحات",
        "category_defense": "🛡️ دفاعی",
        "category_other": "📦 سایر",
        "hp_restored": "❤️ نقاط زندگی به حالت کامل بازگردانده شد!",
        "no_items_category": "هیچ آیتمی در این دسته وجود ندارد.",
        
        # Enhanced Status System Translations (Persian)
        "status_dashboard": "📊 داشبورد وضعیت بازیکن",
        "comprehensive_status": "🎯 وضعیت جامع",
        "player_overview": "👤 نمای کلی بازیکن",
        "combat_status": "⚔️ وضعیت نبرد",
        "defense_status": "🛡️ وضعیت دفاع",
        "inventory_status": "📦 وضعیت انبار",
        "achievements_status": "🏆 دستاوردها",
        "detailed_analytics": "📈 تحلیل‌های تفصیلی",
        "status_message": "👤 <b>وضعیت {first_name}</b>\n\n💰 <b>منابع:</b>\n🏅 مدال‌ها: <b>{medals:,}</b>\n⭐ ستاره‌های تلگرام: <b>{tg_stars}</b>\n\n❤️ <b>سلامت:</b> <b>{hp}/100</b>\n🔥 <b>سطح:</b> <b>{level}</b>\n\n🛡️ <b>دفاع:</b> {defense_status}",
        "defense_status_none": "❌ هیچ دفاع فعالی وجود ندارد",
        "defense_status_active": "✅ {item_name} ({time_left} دقیقه باقی‌مانده)",
        "activate_button": "🛡️ فعال‌سازی {item_name}",
        "defense_already_active": "⚠️ شما قبلاً یک دفاع فعال دارید!",
        "defense_activated": "✅ {item_name} برای {hours} ساعت فعال شد!",
        "item_not_owned": "❌ شما {item_name} ندارید",
        "view_detailed_status": "📊 مشاهده وضعیت تفصیلی",
        "quick_status": "⚡ وضعیت سریع",
        "status_analytics": "📈 تحلیل‌های وضعیت",
        "refresh_status": "🔄 به‌روزرسانی وضعیت",
        "status_history": "📜 تاریخچه وضعیت",
        "performance_overview": "🎯 نمای کلی عملکرد",
        "current_streak": "🔥 سری فعلی",
        "best_streak": "🏆 بهترین سری",
        "total_playtime": "⏱️ کل زمان بازی",
        "rank_in_chat": "🏆 رتبه در چت",
        "activity_level": "📊 سطح فعالیت",
        "last_active": "⏰ آخرین فعالیت",
        "status_comparison": "📊 مقایسه با سایرین",
        "status_trends": "📈 روندهای وضعیت",
        "weekly_progress": "📅 پیشرفت هفتگی",
        "monthly_progress": "📅 پیشرفت ماهانه",
        "status_summary": "📋 خلاصه وضعیت",
        "status_breakdown": "🔍 تجزیه وضعیت",
        
        # Item names (Persian)
        "items": {
            "f22": "حمله سنگین F22 رپتور",
            "moab": "بمب سنگین MOAB",
            "nuclear": "کلاهک هسته‌ای",
            "shield": "سپر ایجیس",
            "intercept": "سیستم پاتریوت",
            "carrier": "ناو هواپیمابر",
            "stealth_bomber": "بمب‌افکن نامرئی",
            "mega_nuke": "کلاهک هسته‌ای فوق‌العاده",
            "super_aegis": "سپر فوق‌العاده ایجیس",
            "medal_boost": "تقویت مدال",
            "vip_status": "وضعیت VIP",
            "energy_drink": "نوشیدنی انرژی‌زا",
            "repair_kit": "کیت تعمیر"
        },
        
        # Item emojis (same for all languages)
        "item_emojis": {
            "f22": "✈️",
            "moab": "💣",
            "nuclear": "☢️",
            "shield": "🛡️",
            "intercept": "🚀",
            "carrier": "🚢",
            "stealth_bomber": "🛩️",
            "mega_nuke": "💥",
            "super_aegis": "🛡️✨",
            "medal_boost": "🏅",
            "vip_status": "👑",
            "energy_drink": "⚡",
            "repair_kit": "🔧"
        },
        
        # TG Stars System Translations (Persian)
        "stars_welcome": "💎 داشبورد ستاره‌های تلگرام",
        "stars_balance_overview": "موجودی ستاره‌های تلگرام شما",
        "current_stars_balance": "موجودی فعلی: ⭐ {stars} ستاره تلگرام",
        "stars_description": "ستاره‌های تلگرام ارز ویژه هستند که برای خرید آیتم‌ها و ویژگی‌های انحصاری استفاده می‌شوند.",
        "how_to_get_stars": "نحوه دریافت ستاره‌های تلگرام",
        "stars_purchase_info": "می‌توانید ستاره‌های تلگرام را مستقیماً از طریق سیستم پرداخت تلگرام خریداری کنید.",
        "premium_features": "ویژگی‌های ویژه",
        "exclusive_items": "آیتم‌های انحصاری",
        "purchase_history": "تاریخچه خریدها",
        "transaction_history": "تاریخچه تراکنش‌ها",
        "no_transactions": "هیچ تراکنشی پیدا نشد.",
        "transaction_date": "تاریخ",
        "transaction_amount": "مقدار",
        "transaction_item": "آیتم",
        "transaction_status": "وضعیت",
        "transaction_completed": "تکمیل شده",
        "transaction_pending": "در انتظار",
        "transaction_failed": "ناموفق",
        
        # Invoice and Payment (Persian)
        "invoice_title": "خرید آیتم ویژه",
        "invoice_description": "خرید {item_name} با ستاره‌های تلگرام",
        "invoice_creation_failed": "ایجاد فاکتور پرداخت ناموفق بود",
        "payment_processing": "در حال پردازش پرداخت شما...",
        "payment_successful": "پرداخت با موفقیت انجام شد!",
        "payment_failed": "پرداخت ناموفق بود. لطفاً دوباره تلاش کنید.",
        "payment_cancelled": "پرداخت لغو شد.",
        "item_not_for_sale": "این آیتم برای فروش در دسترس نیست.",
        "purchase_successful_stars": "✅ خرید {item_name} با ستاره‌های تلگرام موفقیت‌آمیز بود!",
        
        # Stars Shop Integration (Persian)
        "view_premium_shop": "🛒 مشاهده فروشگاه ویژه",
        "premium_catalog": "کاتالوگ ویژه",
        "exclusive_weapons": "تسلیحات انحصاری",
        "special_abilities": "توانایی‌های ویژه",
        "item_requires_stars": "نیاز به ⭐ {price} ستاره تلگرام",
        "insufficient_stars": "❌ ستاره‌های تلگرام کافی نیست! {required} ستاره بیشتر نیاز دارید.",
        "confirm_purchase": "تأیید خرید",
        "purchase_confirmation": "آیا مطمئن هستید که می‌خواهید {item_name} را به قیمت ⭐ {price} ستاره تلگرام خریداری کنید؟",
        "confirm_yes": "✅ بله، خرید کن",
        "confirm_no": "❌ لغو",
        
        # Stars Features (Persian)
        "stars_features_list": "🌟 ویژگی‌های ستاره‌های تلگرام:",
        "feature_exclusive_weapons": "• دسترسی به تسلیحات ویژه انحصاری",
        "feature_special_abilities": "• باز کردن توانایی‌های ویژه نبرد",
        "feature_premium_support": "• پشتیبانی اولویت‌دار مشتریان",
        "feature_advanced_stats": "• آمار و تحلیل‌های پیشرفته",
        "feature_custom_themes": "• تم‌ها و شخصی‌سازی سفارشی",
        "feature_early_access": "• دسترسی زودهنگام به ویژگی‌های جدید",
        
        # Error Messages (Persian)
        "stars_error_generic": "❌ خطایی در سیستم ستاره‌های تلگرام رخ داد.",
        "stars_error_insufficient": "❌ موجودی ستاره‌های تلگرام ناکافی است.",
        "stars_error_item_unavailable": "❌ این آیتم در حال حاضر در دسترس نیست.",
        "stars_error_payment": "❌ پردازش پرداخت ناموفق بود.",
        "stars_error_network": "❌ خطای شبکه. لطفاً دوباره تلاش کنید.",
        
        # Help and Support (Persian)
        "stars_help": "🆘 راهنمای ستاره‌های تلگرام",
        "stars_support": "📞 تماس با پشتیبانی",
        "stars_faq": "❓ سوالات متداول",
        "stars_terms": "📜 شرایط استفاده",
        "refresh_balance": "🔄 بروزرسانی موجودی",
        "close_stars_menu": "❌ بستن",
        
        # Quick Actions (Persian)
        "buy_stars": "💰 خرید ستاره‌های تلگرام",
        "view_history": "📊 مشاهده تاریخچه",
        "browse_premium": "🛒 مرور آیتم‌های ویژه",
        "stars_settings": "⚙️ تنظیمات",
        
        # Statistics System Translations (Persian)
        "stats_dashboard": "📊 داشبورد آمار",
        "stats_overview": "نمای کلی آمار",
        "personal_stats": "آمار شخصی",
        "group_stats": "آمار گروه",
        "combat_analytics": "تحلیل‌های نبرد",
        "leaderboard_ranking": "جدول امتیازات و رده‌بندی",
        
        # Personal Stats (Persian)
        "your_rank": "رتبه شما",
        "current_level": "سطح فعلی",
        "total_score": "امتیاز کل",
        "current_hp": "HP فعلی",
        "max_hp": "حداکثر HP",
        "attack_power": "قدرت حمله",
        "defense_rating": "امتیاز دفاع",
        "accuracy_rate": "نرخ دقت",
        "survival_rate": "نرخ بقا",
        
        # Combat Statistics (Persian)
        "battles_fought": "نبردهای انجام شده",
        "battles_won": "نبردهای برده شده",
        "battles_lost": "نبردهای باخته شده",
        "win_rate": "نرخ پیروزی",
        "total_damage_dealt": "کل آسیب وارد شده",
        "total_damage_taken": "کل آسیب دریافتی",
        "average_damage": "میانگین آسیب",
        "critical_hits": "ضربات بحرانی",
        "successful_defenses": "دفاع‌های موفق",
        "times_defeated": "دفعات شکست",
        
        # Advanced Metrics (Persian)
        "kill_death_ratio": "نسبت کشتن/مرگ",
        "damage_efficiency": "کارایی آسیب",
        "active_time": "زمان فعالیت",
        "last_activity": "آخرین فعالیت",
        "streak_current": "رکورد فعلی",
        "streak_best": "بهترین رکورد",
        "medals_earned": "مدال‌های کسب شده",
        "medals_spent": "مدال‌های خرج شده",
        "net_medals": "مدال‌های خالص",
        
        # Group Statistics (Persian)
        "total_players": "کل بازیکنان",
        "active_players": "بازیکنان فعال",
        "total_battles": "کل نبردها",
        "most_active_player": "فعال‌ترین بازیکن",
        "strongest_player": "قوی‌ترین بازیکن",
        "most_battles": "بیشترین نبرد",
        "highest_damage": "بالاترین آسیب",
        "group_activity": "فعالیت گروه",
        
        # Weapon Statistics (Persian)
        "favorite_weapon": "تسلیح مورد علاقه",
        "most_effective_weapon": "مؤثرترین تسلیح",
        "weapon_usage": "استفاده از تسلیحات",
        "weapon_effectiveness": "کارایی تسلیحات",
        "weapons_owned": "تسلیحات موجود",
        "premium_items": "آیتم‌های ویژه",
        
        # Time-based Stats (Persian)
        "daily_activity": "فعالیت روزانه",
        "weekly_summary": "خلاصه هفتگی",
        "monthly_progress": "پیشرفت ماهانه",
        "session_duration": "مدت جلسه",
        "peak_activity_time": "زمان اوج فعالیت",
        
        # Achievements & Milestones (Persian)
        "achievements_unlocked": "دستاوردهای باز شده",
        "milestones_reached": "نقاط عطف رسیده",
        "badges_earned": "نشان‌های کسب شده",
        "special_titles": "عناوین ویژه",
        "progression_rate": "نرخ پیشرفت",
        
        # Comparison Stats (Persian)
        "vs_group_average": "در مقابل میانگین گروه",
        "percentile_ranking": "رده‌بندی صدکی",
        "performance_trend": "روند عملکرد",
        "improvement_rate": "نرخ بهبود",
        
        # Stats Navigation (Persian)
        "view_personal": "👤 آمار شخصی",
        "view_combat": "⚔️ آمار نبرد",
        "view_weapons": "🔫 آمار تسلیحات",
        "view_achievements": "🏆 دستاوردها",
        "view_leaderboard": "📊 جدول امتیازات",
        "view_trends": "📈 روندها",
        "refresh_stats": "🔄 بروزرسانی",
        "export_stats": "📤 خروجی",
        "stats_help": "🆘 راهنما",
        "close_stats": "❌ بستن",
        
        # Enhanced Configuration System Translations (Persian)
        "bot_configuration": "🔧 پیکربندی ربات",
        "configuration_dashboard": "📊 داشبورد پیکربندی",
        "game_mechanics": "🎮 مکانیک‌های بازی",
        "feature_flags": "🚩 پرچم‌های ویژگی",
        "security_settings": "🔐 تنظیمات امنیتی",
        "notification_settings": "🔔 تنظیمات اعلانات",
        "performance_settings": "⚡ تنظیمات عملکرد",
        "multilingual_settings": "🌐 تنظیمات چندزبانه",
        "bot_information": "🤖 اطلاعات ربات",
        "bot_version": "نسخه",
        "bot_description": "توضیحات",
        "supported_languages": "زبان‌های پشتیبانی شده",
        "current_language": "زبان فعلی",
        "change_language": "🌐 تغییر زبان",
        "language_changed": "✅ زبان با موفقیت تغییر کرد!",
        "configuration_updated": "✅ پیکربندی با موفقیت به‌روزرسانی شد!",
        "configuration_error": "❌ به‌روزرسانی پیکربندی ناموفق بود",
        "invalid_setting": "❌ مقدار تنظیمات نامعتبر",
        "setting_saved": "✅ تنظیمات ذخیره شد: {setting_name}",
        "setting_reset": "🔄 تنظیمات به حالت پیش‌فرض بازگردانده شد: {setting_name}",
        "export_configuration": "📤 صادرات پیکربندی",
        "import_configuration": "📥 وارد کردن پیکربندی",
        "configuration_exported": "✅ پیکربندی با موفقیت صادر شد",
        "configuration_imported": "✅ پیکربندی با موفقیت وارد شد",
        "reset_to_defaults": "🔄 بازگردانی به حالت پیش‌فرض",
        "confirm_reset": "⚠️ این عمل همه تنظیمات را به مقادیر پیش‌فرض بازمی‌گرداند. ادامه؟",
        "reset_confirmed": "✅ پیکربندی به حالت پیش‌فرض بازگردانده شد",
        "game_mode_settings": "🎮 تنظیمات حالت بازی",
        "difficulty_settings": "📊 تنظیمات سختی",
        "economy_settings": "💰 تنظیمات اقتصادی",
        "combat_settings": "⚔️ تنظیمات نبرد",
        "weapon_multipliers": "🔫 ضرایب آسیب تسلیحات",
        "defense_effectiveness": "🛡️ اثربخشی دفاع",
        "level_system": "📈 سیستم سطح",
        "experience_settings": "⭐ تنظیمات تجربه",
        "feature_enabled": "✅ فعال",
        "feature_disabled": "❌ غیرفعال",
        "toggle_feature": "🔄 تغییر وضعیت ویژگی",
        "advanced_settings": "⚙️ تنظیمات پیشرفته",
        "developer_mode": "👨‍💻 حالت توسعه‌دهنده",
        "debug_information": "🐛 اطلاعات دیباگ",
        "system_status": "📊 وضعیت سیستم",
        "performance_metrics": "📈 معیارهای عملکرد",
        "configuration_validation": "✅ اعتبارسنجی پیکربندی",
        "validation_passed": "✅ همه تنظیمات معتبر هستند",
        "validation_failed": "❌ اعتبارسنجی پیکربندی ناموفق بود",
        "backup_configuration": "💾 پشتیبان‌گیری از پیکربندی",
        "restore_configuration": "🔄 بازیابی پیکربندی",
        "configuration_help": "❓ راهنمای پیکربندی",
        "setting_description": "📝 توضیحات تنظیمات",
        "recommended_value": "💡 مقدار توصیه شده",
        "current_value": "📊 مقدار فعلی",
        "default_value": "🔧 مقدار پیش‌فرض",
        "apply_changes": "✅ اعمال تغییرات",
        "cancel_changes": "❌ لغو تغییرات",
        "unsaved_changes": "⚠️ شما تغییرات ذخیره نشده‌ای دارید",
        "save_before_exit": "💾 قبل از خروج تغییرات را ذخیره کنید؟",
        
        # Stats Messages (Persian)
        "stats_loading": "در حال بارگذاری آمار...",
        "stats_error": "❌ خطا در بارگذاری آمار.",
        "stats_no_data": "هنوز داده‌ای موجود نیست. شروع به بازی کنید تا آمارتان را ببینید!",
        "stats_updated": "✅ آمار بروزرسانی شد!",
        "rank_improved": "🎉 رتبه شما بهبود یافت!",
        "new_achievement": "🏆 دستاورد جدید باز شد!",
        "milestone_reached": "🎯 نقطه عطف حاصل شد!",
        
        # Legacy Stats (maintaining compatibility) (Persian)
        "stats_title": "آمار گروه",
        "stats_top_players": "برترین بازیکنان",
        "stats_no_players": "هیچ بازیکنی پیدا نشد",
        "stats_general": "آمار عمومی",
        "stats_total_attacks": "کل حملات",
        "stats_most_used_weapon": "پرکاربردترین تسلیح",
        "medals_emoji": "🏅",
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
            "fa": "English"
        },
        "fa": {
            "en": "Persian (فارسی)",
            "fa": "فارسی"
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
            persian_digits = "۰۱۲۳۴۵۶۷۸۹"
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
        "weapon": "🔫",
        "shield": "🛡️",
        "missile": "🚀",
        "bomb": "💣",
        "nuclear": "☢️",
        "defense": "🛡️",
        "attack": "⚔️",
        "medal": "🏅",
        "star": "⭐",
        "energy": "⚡",
        "repair": "🔧",
        "boost": "💪"
    }
    
    return emoji_map.get(item_type, "📦")

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
        
        logger.info(f"Translation validation complete. Status: {'✅ Complete' if results['complete'] else '⚠️ Incomplete'}")
        
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
