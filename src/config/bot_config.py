#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Enhanced Bot Configuration Management System
Provides comprehensive bot configuration, game mechanics, and multilingual settings
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, field
from enum import Enum
# Note: AsyncTeleBot import moved to create_bot() function to avoid import delays
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

class GameMode(Enum):
    """Game mode enumeration"""
    CASUAL = "casual"
    COMPETITIVE = "competitive"
    TOURNAMENT = "tournament"
    PRACTICE = "practice"

class DifficultyLevel(Enum):
    """Difficulty level enumeration"""
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    EXPERT = "expert"

class LanguageCode(Enum):
    """Supported language codes"""
    ENGLISH = "en"
    PERSIAN = "fa"

@dataclass
class GameMechanics:
    """Game mechanics configuration"""
    # Attack settings
    max_attacks_per_day: int = 50
    attack_cooldown: int = 5  # seconds
    damage_base: int = 25
    level_damage_multiplier: float = 1.1
    
    # Defense settings
    shield_duration: int = 10800  # 3 hours
    intercept_duration: int = 43200  # 12 hours
    super_aegis_duration: int = 86400  # 24 hours
    
    # Economy settings
    shield_cost: int = 100
    intercept_cost: int = 50
    super_aegis_cost: int = 200
    daily_bonus: int = 20
    level_up_bonus: int = 50
    
    # Advanced mechanics
    critical_hit_chance: float = 0.1  # 10%
    critical_hit_multiplier: float = 1.5
    comeback_bonus: bool = True
    revenge_bonus_multiplier: float = 1.25

@dataclass
class FeatureFlags:
    """Feature toggles and experimental features"""
    unlimited_missiles: bool = True
    free_stars_enabled: bool = True
    premium_features: bool = True
    analytics_enabled: bool = True
    debug_mode: bool = False
    
    # Advanced features
    achievements_system: bool = True
    seasonal_events: bool = True
    guild_system: bool = False
    tournament_mode: bool = False
    ai_opponents: bool = False

@dataclass
class SecuritySettings:
    """Security and anti-abuse settings"""
    rate_limit_enabled: bool = True
    max_requests_per_minute: int = 30
    anti_spam_enabled: bool = True
    admin_only_commands: List[str] = field(default_factory=lambda: ["/admin", "/reset", "/broadcast"])
    
    # Anti-cheat
    damage_validation: bool = True
    inventory_validation: bool = True
    score_validation: bool = True

@dataclass
class NotificationSettings:
    """Notification and messaging settings"""
    welcome_message_enabled: bool = True
    achievement_notifications: bool = True
    daily_bonus_reminders: bool = True
    attack_notifications: bool = True
    defense_notifications: bool = True
    
    # Advanced notifications
    maintenance_notifications: bool = True
    event_notifications: bool = True
    update_notifications: bool = True

@dataclass
class PerformanceSettings:
    """Performance and optimization settings"""
    database_pool_size: int = 10
    cache_enabled: bool = True
    cache_ttl: int = 300  # 5 minutes
    async_enabled: bool = True
    
    # Advanced performance
    query_optimization: bool = True
    batch_processing: bool = True
    lazy_loading: bool = True

class EnhancedBotConfig:
    """Enhanced bot configuration management system"""
    
    def __init__(self):
        # Core bot settings
        self.TOKEN: Optional[str] = os.getenv("BOT_TOKEN")
        self.BOT_USERNAME: str = os.getenv("BOT_USERNAME", "@TrumpBot")
        self.BOT_NAME: str = os.getenv("BOT_NAME", "TrumpBot")
        self.BOT_VERSION: str = "2.0.0"
        self.BOT_DESCRIPTION: Dict[str, str] = {
            "en": "Advanced Telegram combat game bot with comprehensive features",
            "fa": "ربات پیشرفته بازی نبرد تلگرام با امکانات جامع"
        }
        
        # Game configuration
        self.game_mechanics = GameMechanics()
        self.feature_flags = FeatureFlags()
        self.security_settings = SecuritySettings()
        self.notification_settings = NotificationSettings()
        self.performance_settings = PerformanceSettings()
        
        # Load custom configurations
        self._load_environment_overrides()
        self._load_configuration_file()
        
        # Damage multipliers with enhanced weapon system
        self.DAMAGE_MULTIPLIERS = {
            "missile": 1.0,      # Base weapon
            "f22": 1.5,          # Fighter jet
            "moab": 2.0,         # Massive bomb
            "nuclear": 3.0,      # Nuclear weapon
            "carrier": 2.2,      # Aircraft carrier
            "stealth_bomber": 2.5,  # Stealth bomber
            "mega_nuke": 4.0,    # Ultimate weapon
            "plasma_cannon": 3.5, # Sci-fi weapon
            "antimatter": 5.0,   # Theoretical maximum
        }
        
        # Defense effectiveness with enhanced defense system
        self.DEFENSE_EFFECTIVENESS = {
            "shield": 0.75,      # 75% damage reduction
            "intercept": 0.60,   # 60% damage reduction  
            "super_aegis": 0.90, # 90% damage reduction
            "force_field": 0.85, # 85% damage reduction
            "quantum_shield": 0.95, # 95% damage reduction
        }
        
        # Multilingual configuration
        self.SUPPORTED_LANGUAGES = [LanguageCode.ENGLISH, LanguageCode.PERSIAN]
        self.DEFAULT_LANGUAGE = LanguageCode.ENGLISH
        self.RTL_LANGUAGES = [LanguageCode.PERSIAN]
        
        # Game modes and difficulty
        self.GAME_MODES = {
            GameMode.CASUAL: {
                "damage_multiplier": 1.0,
                "cooldown_multiplier": 1.0,
                "reward_multiplier": 1.0
            },
            GameMode.COMPETITIVE: {
                "damage_multiplier": 1.2,
                "cooldown_multiplier": 0.8,
                "reward_multiplier": 1.5
            },
            GameMode.TOURNAMENT: {
                "damage_multiplier": 1.5,
                "cooldown_multiplier": 0.5,
                "reward_multiplier": 2.0
            },
            GameMode.PRACTICE: {
                "damage_multiplier": 0.5,
                "cooldown_multiplier": 0.1,
                "reward_multiplier": 0.1
            }
        }
        
        # Experience and leveling system
        self.LEVEL_SYSTEM = {
            "base_experience": 100,
            "experience_multiplier": 1.5,
            "max_level": 100,
            "prestige_levels": 10,
            "experience_sources": {
                "attack": 10,
                "defend": 5,
                "win": 25,
                "daily_bonus": 50,
                "achievement": 100
            }
        }
        
        # Economy system
        self.ECONOMY_SYSTEM = {
            "starting_medals": 100,
            "starting_tg_stars": 5,
            "inflation_rate": 0.02,
            "tax_rate": 0.1,
            "market_volatility": 0.05,
            "investment_returns": {
                "low_risk": 0.03,
                "medium_risk": 0.07,
                "high_risk": 0.15
            }
        }
        
    def _load_environment_overrides(self):
        """Load configuration overrides from environment variables"""
        try:
            # Game mechanics overrides
            if os.getenv("MAX_ATTACKS_PER_DAY"):
                self.game_mechanics.max_attacks_per_day = int(os.getenv("MAX_ATTACKS_PER_DAY"))
            if os.getenv("ATTACK_COOLDOWN"):
                self.game_mechanics.attack_cooldown = int(os.getenv("ATTACK_COOLDOWN"))
            if os.getenv("DAILY_BONUS"):
                self.game_mechanics.daily_bonus = int(os.getenv("DAILY_BONUS"))
                
            # Feature flags overrides
            if os.getenv("UNLIMITED_MISSILES"):
                self.feature_flags.unlimited_missiles = os.getenv("UNLIMITED_MISSILES").lower() == "true"
            if os.getenv("FREE_STARS_ENABLED"):
                self.feature_flags.free_stars_enabled = os.getenv("FREE_STARS_ENABLED").lower() == "true"
            if os.getenv("DEBUG_MODE"):
                self.feature_flags.debug_mode = os.getenv("DEBUG_MODE").lower() == "true"
                
            # Security settings overrides
            if os.getenv("RATE_LIMIT_ENABLED"):
                self.security_settings.rate_limit_enabled = os.getenv("RATE_LIMIT_ENABLED").lower() == "true"
            if os.getenv("MAX_REQUESTS_PER_MINUTE"):
                self.security_settings.max_requests_per_minute = int(os.getenv("MAX_REQUESTS_PER_MINUTE"))
                
        except Exception as e:
            logger.error(f"Error loading environment overrides: {e}")
    
    def _load_configuration_file(self):
        """Load configuration from JSON file if available"""
        try:
            config_file = os.getenv("CONFIG_FILE", "config/bot_config.json")
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self._apply_configuration(config_data)
                    logger.info(f"Configuration loaded from {config_file}")
        except Exception as e:
            logger.error(f"Error loading configuration file: {e}")
    
    def _apply_configuration(self, config_data: Dict[str, Any]):
        """Apply configuration data to settings"""
        try:
            if "game_mechanics" in config_data:
                for key, value in config_data["game_mechanics"].items():
                    if hasattr(self.game_mechanics, key):
                        setattr(self.game_mechanics, key, value)
                        
            if "feature_flags" in config_data:
                for key, value in config_data["feature_flags"].items():
                    if hasattr(self.feature_flags, key):
                        setattr(self.feature_flags, key, value)
                        
            # Apply other configuration sections as needed
        except Exception as e:
            logger.error(f"Error applying configuration: {e}")
    
    def get_game_mode_settings(self, mode: GameMode) -> Dict[str, float]:
        """Get settings for specific game mode"""
        return self.GAME_MODES.get(mode, self.GAME_MODES[GameMode.CASUAL])
    
    def get_weapon_damage(self, weapon_id: str, base_damage: int = None) -> int:
        """Calculate weapon damage based on multipliers"""
        if base_damage is None:
            base_damage = self.game_mechanics.damage_base
        multiplier = self.DAMAGE_MULTIPLIERS.get(weapon_id, 1.0)
        return int(base_damage * multiplier)
    
    def get_defense_effectiveness(self, defense_id: str) -> float:
        """Get defense effectiveness percentage"""
        return self.DEFENSE_EFFECTIVENESS.get(defense_id, 0.0)
    
    def calculate_level_requirement(self, level: int) -> int:
        """Calculate experience required for specific level"""
        base = self.LEVEL_SYSTEM["base_experience"]
        multiplier = self.LEVEL_SYSTEM["experience_multiplier"]
        return int(base * (multiplier ** (level - 1)))
    
    def get_experience_reward(self, action: str) -> int:
        """Get experience reward for specific action"""
        return self.LEVEL_SYSTEM["experience_sources"].get(action, 0)
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled"""
        return getattr(self.feature_flags, feature_name, False)
    
    def get_localized_description(self, language: str = "en") -> str:
        """Get bot description in specified language"""
        return self.BOT_DESCRIPTION.get(language, self.BOT_DESCRIPTION["en"])
    
    def get_security_setting(self, setting_name: str) -> Any:
        """Get security setting value"""
        return getattr(self.security_settings, setting_name, None)
    
    def validate_configuration(self) -> bool:
        """Validate configuration settings"""
        try:
            # Validate required settings
            if not self.TOKEN:
                logger.error("BOT_TOKEN is required")
                return False
                
            # Validate numeric ranges
            if self.game_mechanics.max_attacks_per_day <= 0:
                logger.error("MAX_ATTACKS_PER_DAY must be positive")
                return False
                
            if self.game_mechanics.attack_cooldown < 0:
                logger.error("ATTACK_COOLDOWN cannot be negative")
                return False
                
            # Validate multipliers
            for weapon, multiplier in self.DAMAGE_MULTIPLIERS.items():
                if multiplier <= 0:
                    logger.error(f"Invalid damage multiplier for {weapon}: {multiplier}")
                    return False
                    
            # Validate defense effectiveness
            for defense, effectiveness in self.DEFENSE_EFFECTIVENESS.items():
                if not (0 <= effectiveness <= 1):
                    logger.error(f"Invalid defense effectiveness for {defense}: {effectiveness}")
                    return False
                    
            logger.info("Configuration validation successful")
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
    
    def export_configuration(self, file_path: str = None) -> Dict[str, Any]:
        """Export current configuration to dictionary or file"""
        try:
            config_export = {
                "bot_info": {
                    "name": self.BOT_NAME,
                    "username": self.BOT_USERNAME,
                    "version": self.BOT_VERSION,
                    "description": self.BOT_DESCRIPTION
                },
                "game_mechanics": {
                    "max_attacks_per_day": self.game_mechanics.max_attacks_per_day,
                    "attack_cooldown": self.game_mechanics.attack_cooldown,
                    "damage_base": self.game_mechanics.damage_base,
                    "daily_bonus": self.game_mechanics.daily_bonus,
                    "shield_cost": self.game_mechanics.shield_cost,
                    "intercept_cost": self.game_mechanics.intercept_cost
                },
                "feature_flags": {
                    "unlimited_missiles": self.feature_flags.unlimited_missiles,
                    "free_stars_enabled": self.feature_flags.free_stars_enabled,
                    "premium_features": self.feature_flags.premium_features,
                    "analytics_enabled": self.feature_flags.analytics_enabled,
                    "debug_mode": self.feature_flags.debug_mode
                },
                "damage_multipliers": self.DAMAGE_MULTIPLIERS,
                "defense_effectiveness": self.DEFENSE_EFFECTIVENESS,
                "supported_languages": [lang.value for lang in self.SUPPORTED_LANGUAGES]
            }
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config_export, f, indent=2, ensure_ascii=False)
                logger.info(f"Configuration exported to {file_path}")
                
            return config_export
            
        except Exception as e:
            logger.error(f"Error exporting configuration: {e}")
            return {}
    
    def get_configuration_summary(self, language: str = "en") -> Dict[str, str]:
        """Get human-readable configuration summary"""
        if language == "fa":
            return {
                "نام ربات": self.BOT_NAME,
                "نسخه": self.BOT_VERSION,
                "حداکثر حملات روزانه": str(self.game_mechanics.max_attacks_per_day),
                "زمان انتظار حمله": f"{self.game_mechanics.attack_cooldown} ثانیه",
                "پاداش روزانه": f"{self.game_mechanics.daily_bonus} مدال",
                "موشک‌های نامحدود": "فعال" if self.feature_flags.unlimited_missiles else "غیرفعال",
                "ستاره‌های رایگان": "فعال" if self.feature_flags.free_stars_enabled else "غیرفعال",
                "حالت دیباگ": "فعال" if self.feature_flags.debug_mode else "غیرفعال",
                "امکانات پریمیوم": "فعال" if self.feature_flags.premium_features else "غیرفعال",
                "زبان‌های پشتیبانی شده": "انگلیسی، فارسی"
            }
        else:
            return {
                "Bot Name": self.BOT_NAME,
                "Version": self.BOT_VERSION,
                "Max Daily Attacks": str(self.game_mechanics.max_attacks_per_day),
                "Attack Cooldown": f"{self.game_mechanics.attack_cooldown} seconds",
                "Daily Bonus": f"{self.game_mechanics.daily_bonus} medals",
                "Unlimited Missiles": "Enabled" if self.feature_flags.unlimited_missiles else "Disabled",
                "Free Stars": "Enabled" if self.feature_flags.free_stars_enabled else "Disabled",
                "Debug Mode": "Enabled" if self.feature_flags.debug_mode else "Disabled",
                "Premium Features": "Enabled" if self.feature_flags.premium_features else "Disabled",
                "Supported Languages": "English, Persian"
            }

# Initialize enhanced configuration
config = EnhancedBotConfig()

# Note: Validation will be performed when needed to avoid import delays

def create_bot():
    """Create and return enhanced bot instance with full configuration"""
    try:
        # Import AsyncTeleBot here to avoid import delays
        from telebot.async_telebot import AsyncTeleBot
        
        if config.TOKEN:
            bot_instance = AsyncTeleBot(config.TOKEN, parse_mode="HTML")
            
            # Configure bot settings
            if config.feature_flags.debug_mode:
                logging.getLogger('telebot').setLevel(logging.DEBUG)
            
            logger.info(f"Bot initialized: {config.BOT_NAME} v{config.BOT_VERSION}")
            return bot_instance
        else:
            logger.error("BOT_TOKEN not found, bot not initialized")
            return None
            
    except Exception as e:
        logger.error(f"Error creating bot instance: {e}")
        return None

def get_bot_info(language: str = "en") -> Dict[str, str]:
    """Get comprehensive bot information"""
    return {
        "name": config.BOT_NAME,
        "username": config.BOT_USERNAME,
        "version": config.BOT_VERSION,
        "description": config.get_localized_description(language),
        "features": {
            "unlimited_missiles": config.feature_flags.unlimited_missiles,
            "free_stars": config.feature_flags.free_stars_enabled,
            "premium_features": config.feature_flags.premium_features,
            "multilingual": True,
            "analytics": config.feature_flags.analytics_enabled
        }
    }

def get_game_settings(language: str = "en") -> Dict[str, Any]:
    """Get current game settings with localization"""
    settings = {
        "mechanics": {
            "max_attacks_per_day": config.game_mechanics.max_attacks_per_day,
            "attack_cooldown": config.game_mechanics.attack_cooldown,
            "damage_base": config.game_mechanics.damage_base,
            "daily_bonus": config.game_mechanics.daily_bonus
        },
        "weapons": config.DAMAGE_MULTIPLIERS,
        "defenses": config.DEFENSE_EFFECTIVENESS,
        "languages": [lang.value for lang in config.SUPPORTED_LANGUAGES]
    }
    
    return settings

# Global bot instance with enhanced configuration
bot = create_bot()

# Legacy exports for backward compatibility
TOKEN = config.TOKEN
BOT_USERNAME = config.BOT_USERNAME
UNLIMITED_MISSILES = config.feature_flags.unlimited_missiles
FREE_STARS_ENABLED = config.feature_flags.free_stars_enabled
MAX_ATTACKS_PER_DAY = config.game_mechanics.max_attacks_per_day
ATTACK_COOLDOWN = config.game_mechanics.attack_cooldown
SHIELD_DURATION = config.game_mechanics.shield_duration
INTERCEPT_DURATION = config.game_mechanics.intercept_duration
SHIELD_COST = config.game_mechanics.shield_cost
INTERCEPT_COST = config.game_mechanics.intercept_cost
DAILY_BONUS = config.game_mechanics.daily_bonus
DAMAGE_MULTIPLIERS = config.DAMAGE_MULTIPLIERS
DEFENSE_EFFECTIVENESS = config.DEFENSE_EFFECTIVENESS

# Enhanced exports
BotConfig = config  # Main configuration object
BOT_CONFIG = config  # Backward compatibility alias
GameMechanics = config.game_mechanics
FeatureFlags = config.feature_flags
SecuritySettings = config.security_settings
