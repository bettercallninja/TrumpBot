﻿#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Enhanced Items Configuration and Management System
Provides comprehensive item definitions, multilingual support, and advanced functionality
"""

import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json

# Set up logging
logger = logging.getLogger(__name__)

class ItemType(Enum):
    """Enhanced item type enumeration"""
    WEAPON = "weapon"
    SHIELD = "shield" 
    INTERCEPT = "intercept"
    BOOST = "boost"
    STATUS = "status"
    ARSENAL = "arsenal"
    CONSUMABLE = "consumable"
    UTILITY = "utility"
    SPECIAL = "special"
    SEASONAL = "seasonal"

class PaymentType(Enum):
    """Payment type enumeration"""
    MEDALS = "medals"
    TG_STARS = "tg_stars"
    FREE = "free"
    ACHIEVEMENT = "achievement"

class ItemCategory(Enum):
    """Enhanced item category enumeration"""
    WEAPONS = "weapons"
    DEFENSE = "defense"
    UTILITIES = "utilities"
    BOOSTS = "boosts"
    PREMIUM = "premium"
    ARSENAL = "arsenal"
    SEASONAL = "seasonal"
    SPECIAL = "special"

class ItemRarity(Enum):
    """Item rarity levels"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"

class ItemTier(Enum):
    """Item power tiers"""
    BASIC = 1
    ADVANCED = 2
    MILITARY = 3
    SPECIAL = 4
    ULTIMATE = 5

@dataclass
class ItemConfig:
    """Enhanced item configuration data class"""
    type: ItemType
    payment: PaymentType
    category: ItemCategory
    rarity: ItemRarity
    tier: ItemTier
    stars: int
    title: str
    description: str
    emoji: str
    
    # Pricing
    medals_price: Optional[int] = None
    stars_price: Optional[int] = None
    
    # Combat stats
    damage: Optional[int] = None
    damage_bonus: Optional[float] = None
    critical_chance: Optional[float] = None
    
    # Defense stats
    duration_seconds: Optional[int] = None
    effectiveness: Optional[float] = None
    absorption: Optional[int] = None
    
    # Utility stats
    bonus: Optional[int] = None
    medals_reward: Optional[int] = None
    hp_restore: Optional[int] = None
    capacity: Optional[int] = None
    
    # Status effects
    days: Optional[int] = None
    cooldown_reduction: Optional[float] = None
    experience_multiplier: Optional[float] = None
    
    # Availability
    limited_time: bool = False
    achievement_required: Optional[str] = None
    level_required: int = 1
    
    # Usage
    consumable: bool = True
    max_stack: int = 99
    usage_limit: Optional[int] = None

@dataclass
class ItemEffectConfig:
    """Configuration for item effects and bonuses"""
    effect_type: str
    effect_value: Union[int, float]
    duration_seconds: Optional[int] = None
    stack_limit: int = 1
    description: Dict[str, str] = field(default_factory=dict)

# Comprehensive items database with enhanced features
ITEMS: Dict[str, Dict[str, Any]] = {
    # ===== BASIC WEAPONS (Medal-based) =====
    "missile": {
        "type": ItemType.WEAPON.value,
        "payment": PaymentType.MEDALS.value,
        "category": ItemCategory.WEAPONS.value,
        "rarity": ItemRarity.COMMON.value,
        "tier": ItemTier.BASIC.value,
        "damage": 10,
        "stars": 1,
        "medals_price": 25,
        "title": "Basic Missile",
        "description": "Standard military missile (+10 damage)",
        "emoji": "ðŸš€",
        "level_required": 1,
        "max_stack": 50
    },
    "f22": {
        "type": ItemType.WEAPON.value,
        "payment": PaymentType.MEDALS.value,
        "category": ItemCategory.WEAPONS.value,
        "rarity": ItemRarity.UNCOMMON.value,
        "tier": ItemTier.ADVANCED.value,
        "damage": 18,
        "damage_bonus": 0.1,
        "stars": 2,
        "medals_price": 75,
        "title": "F22 Raptor Strike",
        "description": "Advanced fighter jet attack (+18 damage, 10% damage bonus)",
        "emoji": "âœˆï¸",
        "level_required": 3,
        "max_stack": 25
    },
    "moab": {
        "type": ItemType.WEAPON.value,
        "payment": PaymentType.MEDALS.value,
        "category": ItemCategory.WEAPONS.value,
        "rarity": ItemRarity.RARE.value,
        "tier": ItemTier.MILITARY.value,
        "damage": 35,
        "critical_chance": 0.15,
        "stars": 3,
        "medals_price": 200,
        "title": "MOAB Heavy Bomb",
        "description": "Massive Ordnance Air Blast (+35 damage, 15% critical chance)",
        "emoji": "ðŸ’£",
        "level_required": 5,
        "max_stack": 15
    },
    "nuclear": {
        "type": ItemType.WEAPON.value,
        "payment": PaymentType.MEDALS.value,
        "category": ItemCategory.WEAPONS.value,
        "rarity": ItemRarity.EPIC.value,
        "tier": ItemTier.SPECIAL.value,
        "damage": 60,
        "damage_bonus": 0.25,
        "critical_chance": 0.2,
        "stars": 4,
        "medals_price": 500,
        "title": "Nuclear Warhead",
        "description": "Ultimate destruction weapon (+60 damage, 25% bonus, 20% critical)",
        "emoji": "â˜¢ï¸",
        "level_required": 10,
        "max_stack": 8
    },
    "antimatter": {
        "type": ItemType.WEAPON.value,
        "payment": PaymentType.MEDALS.value,
        "category": ItemCategory.WEAPONS.value,
        "rarity": ItemRarity.LEGENDARY.value,
        "tier": ItemTier.ULTIMATE.value,
        "damage": 100,
        "damage_bonus": 0.5,
        "critical_chance": 0.3,
        "stars": 5,
        "medals_price": 1000,
        "title": "Antimatter Cannon",
        "description": "Theoretical ultimate weapon (+100 damage, 50% bonus, 30% critical)",
        "emoji": "âš›ï¸",
        "level_required": 20,
        "max_stack": 3
    },
    
    # ===== DEFENSE SYSTEMS (Medal-based) =====
    "shield": {
        "type": ItemType.SHIELD.value,
        "payment": PaymentType.MEDALS.value,
        "category": ItemCategory.DEFENSE.value,
        "rarity": ItemRarity.COMMON.value,
        "tier": ItemTier.BASIC.value,
        "duration_seconds": 10800,  # 3 hours
        "effectiveness": 0.5,
        "absorption": 100,
        "stars": 2,
        "medals_price": 100,
        "title": "Basic Shield",
        "description": "Standard defense barrier (3 hours, 50% reduction, 100 absorption)",
        "emoji": "ðŸ›¡ï¸",
        "level_required": 2,
        "consumable": True
    },
    "aegis_shield": {
        "type": ItemType.SHIELD.value,
        "payment": PaymentType.MEDALS.value,
        "category": ItemCategory.DEFENSE.value,
        "rarity": ItemRarity.UNCOMMON.value,
        "tier": ItemTier.ADVANCED.value,
        "duration_seconds": 14400,  # 4 hours
        "effectiveness": 0.65,
        "absorption": 200,
        "stars": 3,
        "medals_price": 200,
        "title": "Aegis Defense Shield",
        "description": "Advanced protection system (4 hours, 65% reduction, 200 absorption)",
        "emoji": "ðŸ›¡ï¸âš¡",
        "level_required": 5,
        "consumable": True
    },
    "intercept": {
        "type": ItemType.INTERCEPT.value,
        "payment": PaymentType.MEDALS.value,
        "category": ItemCategory.DEFENSE.value,
        "rarity": ItemRarity.RARE.value,
        "tier": ItemTier.MILITARY.value,
        "duration_seconds": 21600,  # 6 hours
        "effectiveness": 0.7,
        "bonus": 25,
        "stars": 3,
        "medals_price": 150,
        "title": "Patriot Defense System",
        "description": "Missile interception system (6 hours, 70% effectiveness, +25 counter-damage)",
        "emoji": "ðŸš€ðŸ›¡ï¸",
        "level_required": 7,
        "consumable": True
    },
    "fortress_shield": {
        "type": ItemType.SHIELD.value,
        "payment": PaymentType.MEDALS.value,
        "category": ItemCategory.DEFENSE.value,
        "rarity": ItemRarity.EPIC.value,
        "tier": ItemTier.SPECIAL.value,
        "duration_seconds": 28800,  # 8 hours
        "effectiveness": 0.8,
        "absorption": 500,
        "stars": 4,
        "medals_price": 400,
        "title": "Fortress Shield",
        "description": "Heavy fortification system (8 hours, 80% reduction, 500 absorption)",
        "emoji": "ðŸ°",
        "level_required": 12,
        "consumable": True
    },
    
    # ===== ARSENAL EXPANSIONS (Medal-based) =====
    "carrier": {
        "type": ItemType.ARSENAL.value,
        "payment": PaymentType.MEDALS.value,
        "category": ItemCategory.ARSENAL.value,
        "rarity": ItemRarity.RARE.value,
        "tier": ItemTier.MILITARY.value,
        "capacity": 10,
        "stars": 4,
        "medals_price": 300,
        "title": "Aircraft Carrier",
        "description": "Naval arsenal expansion (+10 weapon capacity)",
        "emoji": "ðŸš¢",
        "level_required": 8,
        "consumable": False,
        "max_stack": 1
    },
    "military_base": {
        "type": ItemType.ARSENAL.value,
        "payment": PaymentType.MEDALS.value,
        "category": ItemCategory.ARSENAL.value,
        "rarity": ItemRarity.EPIC.value,
        "tier": ItemTier.SPECIAL.value,
        "capacity": 25,
        "stars": 5,
        "medals_price": 800,
        "title": "Military Base",
        "description": "Advanced weapons storage facility (+25 capacity)",
        "emoji": "ðŸ­",
        "level_required": 15,
        "consumable": False,
        "max_stack": 1
    },
    
    # ===== UTILITY ITEMS (Medal-based) =====
    "first_aid": {
        "type": ItemType.UTILITY.value,
        "payment": PaymentType.MEDALS.value,
        "category": ItemCategory.UTILITIES.value,
        "rarity": ItemRarity.COMMON.value,
        "tier": ItemTier.BASIC.value,
        "hp_restore": 25,
        "stars": 1,
        "medals_price": 30,
        "title": "First Aid Kit",
        "description": "Basic medical supplies (+25 HP restoration)",
        "emoji": "ðŸ¥",
        "level_required": 1,
        "max_stack": 20
    },
    "field_medic": {
        "type": ItemType.UTILITY.value,
        "payment": PaymentType.MEDALS.value,
        "category": ItemCategory.UTILITIES.value,
        "rarity": ItemRarity.UNCOMMON.value,
        "tier": ItemTier.ADVANCED.value,
        "hp_restore": 50,
        "stars": 2,
        "medals_price": 75,
        "title": "Field Medic Kit",
        "description": "Advanced medical equipment (+50 HP restoration)",
        "emoji": "â›‘ï¸",
        "level_required": 4,
        "max_stack": 15
    },
    
    # ===== PREMIUM WEAPONS (TG Stars) =====
    "stealth_bomber": {
        "type": ItemType.WEAPON.value,
        "payment": PaymentType.TG_STARS.value,
        "category": ItemCategory.PREMIUM.value,
        "rarity": ItemRarity.EPIC.value,
        "tier": ItemTier.SPECIAL.value,
        "damage": 85,
        "damage_bonus": 0.3,
        "critical_chance": 0.25,
        "stars": 4,
        "stars_price": 15,
        "title": "Stealth Bomber",
        "description": "Advanced stealth attack system (+85 damage, 30% bonus, 25% critical)",
        "emoji": "ðŸ›©ï¸",
        "level_required": 12,
        "max_stack": 10
    },
    "orbital_strike": {
        "type": ItemType.WEAPON.value,
        "payment": PaymentType.TG_STARS.value,
        "category": ItemCategory.PREMIUM.value,
        "rarity": ItemRarity.LEGENDARY.value,
        "tier": ItemTier.ULTIMATE.value,
        "damage": 120,
        "damage_bonus": 0.4,
        "critical_chance": 0.35,
        "stars": 5,
        "stars_price": 25,
        "title": "Orbital Strike Platform",
        "description": "Space-based weapons system (+120 damage, 40% bonus, 35% critical)",
        "emoji": "ðŸ›°ï¸",
        "level_required": 18,
        "max_stack": 5
    },
    "quantum_cannon": {
        "type": ItemType.WEAPON.value,
        "payment": PaymentType.TG_STARS.value,
        "category": ItemCategory.PREMIUM.value,
        "rarity": ItemRarity.MYTHIC.value,
        "tier": ItemTier.ULTIMATE.value,
        "damage": 200,
        "damage_bonus": 0.75,
        "critical_chance": 0.5,
        "stars": 5,
        "stars_price": 50,
        "title": "Quantum Destruction Cannon",
        "description": "Theoretical physics weapon (+200 damage, 75% bonus, 50% critical)",
        "emoji": "âš¡âš›ï¸",
        "level_required": 25,
        "max_stack": 2
    },
    
    # ===== PREMIUM DEFENSE (TG Stars) =====
    "super_aegis": {
        "type": ItemType.SHIELD.value,
        "payment": PaymentType.TG_STARS.value,
        "category": ItemCategory.PREMIUM.value,
        "rarity": ItemRarity.EPIC.value,
        "tier": ItemTier.SPECIAL.value,
        "duration_seconds": 43200,  # 12 hours
        "effectiveness": 0.85,
        "absorption": 750,
        "stars": 4,
        "stars_price": 12,
        "title": "Super Aegis Shield",
        "description": "Premium defense system (12 hours, 85% reduction, 750 absorption)",
        "emoji": "ðŸ›¡ï¸âœ¨",
        "level_required": 10,
        "consumable": True
    },
    "quantum_barrier": {
        "type": ItemType.SHIELD.value,
        "payment": PaymentType.TG_STARS.value,
        "category": ItemCategory.PREMIUM.value,
        "rarity": ItemRarity.LEGENDARY.value,
        "tier": ItemTier.ULTIMATE.value,
        "duration_seconds": 86400,  # 24 hours
        "effectiveness": 0.95,
        "absorption": 1500,
        "stars": 5,
        "stars_price": 30,
        "title": "Quantum Energy Barrier",
        "description": "Ultimate protection field (24 hours, 95% reduction, 1500 absorption)",
        "emoji": "âš¡ðŸ›¡ï¸",
        "level_required": 20,
        "consumable": True
    },
    
    # ===== PREMIUM BOOSTS AND UTILITIES (TG Stars) =====
    "medal_boost_small": {
        "type": ItemType.BOOST.value,
        "payment": PaymentType.TG_STARS.value,
        "category": ItemCategory.BOOSTS.value,
        "rarity": ItemRarity.COMMON.value,
        "tier": ItemTier.BASIC.value,
        "medals_reward": 250,
        "stars": 2,
        "stars_price": 3,
        "title": "Small Medal Boost",
        "description": "Instant medal bonus (+250 medals)",
        "emoji": "ðŸ…",
        "level_required": 1,
        "max_stack": 10
    },
    "medal_boost": {
        "type": ItemType.BOOST.value,
        "payment": PaymentType.TG_STARS.value,
        "category": ItemCategory.BOOSTS.value,
        "rarity": ItemRarity.UNCOMMON.value,
        "tier": ItemTier.ADVANCED.value,
        "medals_reward": 500,
        "stars": 3,
        "stars_price": 5,
        "title": "Medal Boost",
        "description": "Instant medal bonus (+500 medals)",
        "emoji": "ðŸ…ðŸ’°",
        "level_required": 1,
        "max_stack": 10
    },
    "mega_medal_boost": {
        "type": ItemType.BOOST.value,
        "payment": PaymentType.TG_STARS.value,
        "category": ItemCategory.BOOSTS.value,
        "rarity": ItemRarity.RARE.value,
        "tier": ItemTier.MILITARY.value,
        "medals_reward": 1000,
        "stars": 4,
        "stars_price": 8,
        "title": "Mega Medal Boost",
        "description": "Large instant medal bonus (+1000 medals)",
        "emoji": "ðŸ†ðŸ’°",
        "level_required": 5,
        "max_stack": 5
    },
    "energy_drink": {
        "type": ItemType.BOOST.value,
        "payment": PaymentType.TG_STARS.value,
        "category": ItemCategory.BOOSTS.value,
        "rarity": ItemRarity.UNCOMMON.value,
        "tier": ItemTier.ADVANCED.value,
        "cooldown_reduction": 0.5,
        "duration_seconds": 3600,  # 1 hour
        "stars": 2,
        "stars_price": 4,
        "title": "Energy Drink",
        "description": "Reduces attack cooldown by 50% for 1 hour",
        "emoji": "âš¡",
        "level_required": 3,
        "max_stack": 15
    },
    "adrenaline_shot": {
        "type": ItemType.BOOST.value,
        "payment": PaymentType.TG_STARS.value,
        "category": ItemCategory.BOOSTS.value,
        "rarity": ItemRarity.RARE.value,
        "tier": ItemTier.MILITARY.value,
        "cooldown_reduction": 0.75,
        "duration_seconds": 7200,  # 2 hours
        "stars": 3,
        "stars_price": 7,
        "title": "Adrenaline Shot",
        "description": "Reduces attack cooldown by 75% for 2 hours",
        "emoji": "ðŸ’‰",
        "level_required": 8,
        "max_stack": 8
    },
    "repair_kit": {
        "type": ItemType.UTILITY.value,
        "payment": PaymentType.TG_STARS.value,
        "category": ItemCategory.UTILITIES.value,
        "rarity": ItemRarity.UNCOMMON.value,
        "tier": ItemTier.ADVANCED.value,
        "hp_restore": 100,
        "stars": 3,
        "stars_price": 8,
        "title": "Advanced Repair Kit",
        "description": "Instantly restores full HP (100 HP)",
        "emoji": "ðŸ”§",
        "level_required": 5,
        "max_stack": 10
    },
    "nano_repair": {
        "type": ItemType.UTILITY.value,
        "payment": PaymentType.TG_STARS.value,
        "category": ItemCategory.UTILITIES.value,
        "rarity": ItemRarity.EPIC.value,
        "tier": ItemTier.SPECIAL.value,
        "hp_restore": 150,
        "stars": 4,
        "stars_price": 15,
        "title": "Nano Repair System",
        "description": "Advanced nanotechnology healing (+150 HP, overheal possible)",
        "emoji": "ðŸ”¬",
        "level_required": 12,
        "max_stack": 5
    },
    "experience_boost": {
        "type": ItemType.BOOST.value,
        "payment": PaymentType.TG_STARS.value,
        "category": ItemCategory.BOOSTS.value,
        "rarity": ItemRarity.RARE.value,
        "tier": ItemTier.MILITARY.value,
        "experience_multiplier": 2.0,
        "duration_seconds": 14400,  # 4 hours
        "stars": 3,
        "stars_price": 10,
        "title": "Experience Accelerator",
        "description": "Doubles experience gain for 4 hours",
        "emoji": "ðŸ“ˆ",
        "level_required": 6,
        "max_stack": 3
    },
    
    # ===== VIP AND STATUS ITEMS (TG Stars) =====
    "vip_status": {
        "type": ItemType.STATUS.value,
        "payment": PaymentType.TG_STARS.value,
        "category": ItemCategory.PREMIUM.value,
        "rarity": ItemRarity.LEGENDARY.value,
        "tier": ItemTier.ULTIMATE.value,
        "days": 30,
        "experience_multiplier": 1.5,
        "damage_bonus": 0.2,
        "stars": 5,
        "stars_price": 50,
        "title": "VIP Status",
        "description": "Premium membership (30 days: +50% XP, +20% damage, exclusive features)",
        "emoji": "ðŸ‘‘",
        "level_required": 1,
        "consumable": False,
        "max_stack": 1
    },
    "elite_membership": {
        "type": ItemType.STATUS.value,
        "payment": PaymentType.TG_STARS.value,
        "category": ItemCategory.PREMIUM.value,
        "rarity": ItemRarity.MYTHIC.value,
        "tier": ItemTier.ULTIMATE.value,
        "days": 90,
        "experience_multiplier": 2.0,
        "damage_bonus": 0.35,
        "cooldown_reduction": 0.25,
        "stars": 5,
        "stars_price": 120,
        "title": "Elite Membership",
        "description": "Ultimate membership (90 days: +100% XP, +35% damage, 25% faster cooldowns)",
        "emoji": "ðŸ’ŽðŸ‘‘",
        "level_required": 10,
        "consumable": False,
        "max_stack": 1
    },
    
    # ===== SEASONAL AND SPECIAL ITEMS =====
    "holiday_missile": {
        "type": ItemType.WEAPON.value,
        "payment": PaymentType.FREE.value,
        "category": ItemCategory.SEASONAL.value,
        "rarity": ItemRarity.RARE.value,
        "tier": ItemTier.SPECIAL.value,
        "damage": 40,
        "critical_chance": 0.3,
        "stars": 3,
        "title": "Holiday Firework Missile",
        "description": "Festive explosive with extra sparkle (+40 damage, 30% critical)",
        "emoji": "ðŸŽ†",
        "level_required": 1,
        "limited_time": True,
        "max_stack": 5
    },
    "anniversary_nuke": {
        "type": ItemType.WEAPON.value,
        "payment": PaymentType.ACHIEVEMENT.value,
        "category": ItemCategory.SPECIAL.value,
        "rarity": ItemRarity.LEGENDARY.value,
        "tier": ItemTier.ULTIMATE.value,
        "damage": 150,
        "damage_bonus": 0.5,
        "critical_chance": 0.4,
        "stars": 5,
        "title": "Anniversary Nuclear Device",
        "description": "Commemorative ultimate weapon (+150 damage, 50% bonus, 40% critical)",
        "emoji": "ðŸŽŠâ˜¢ï¸",
        "level_required": 15,
        "achievement_required": "veteran_player",
        "limited_time": True,
        "max_stack": 1
    }
}

# Comprehensive multilingual item names
ITEM_NAMES: Dict[str, Dict[str, str]] = {
    "en": {
        # Basic Weapons
        "missile": "Basic Missile",
        "f22": "F22 Raptor",
        "moab": "MOAB Bomb",
        "nuclear": "Nuclear Warhead",
        "antimatter": "Antimatter Cannon",
        
        # Defense Systems
        "shield": "Basic Shield",
        "aegis_shield": "Aegis Shield",
        "intercept": "Patriot System",
        "fortress_shield": "Fortress Shield",
        
        # Arsenal
        "carrier": "Aircraft Carrier",
        "military_base": "Military Base",
        
        # Utilities
        "first_aid": "First Aid Kit",
        "field_medic": "Field Medic Kit",
        
        # Premium Weapons
        "stealth_bomber": "Stealth Bomber",
        "orbital_strike": "Orbital Strike",
        "quantum_cannon": "Quantum Cannon",
        
        # Premium Defense
        "super_aegis": "Super Aegis Shield",
        "quantum_barrier": "Quantum Barrier",
        
        # Boosts
        "medal_boost_small": "Small Medal Boost",
        "medal_boost": "Medal Boost",
        "mega_medal_boost": "Mega Medal Boost",
        "energy_drink": "Energy Drink",
        "adrenaline_shot": "Adrenaline Shot",
        "repair_kit": "Repair Kit",
        "nano_repair": "Nano Repair",
        "experience_boost": "Experience Boost",
        
        # Status
        "vip_status": "VIP Status",
        "elite_membership": "Elite Membership",
        
        # Seasonal
        "holiday_missile": "Holiday Missile",
        "anniversary_nuke": "Anniversary Nuke",
    },
    "fa": {
        # Ø³Ù„Ø§Ø­â€ŒÙ‡Ø§ÛŒ Ù¾Ø§ÛŒÙ‡
        "missile": "Ù…ÙˆØ´Ú© Ù¾Ø§ÛŒÙ‡",
        "f22": "Ø¬Ù†Ú¯Ù†Ø¯Ù‡ Ø§Ù-Û²Û²",
        "moab": "Ø¨Ù…Ø¨ Ù…ÙˆØ¢Ø¨",
        "nuclear": "Ú©Ù„Ø§Ù‡Ú© Ù‡Ø³ØªÙ‡â€ŒØ§ÛŒ",
        "antimatter": "ØªÙˆÙ¾ Ù¾Ø§Ø¯Ù…Ø§Ø¯Ù‡",
        
        # Ø³ÛŒØ³ØªÙ…â€ŒÙ‡Ø§ÛŒ Ø¯ÙØ§Ø¹ÛŒ
        "shield": "Ø³Ù¾Ø± Ù¾Ø§ÛŒÙ‡",
        "aegis_shield": "Ø³Ù¾Ø± Ø§ÛŒØ¬ÛŒØ³",
        "intercept": "Ø³ÛŒØ³ØªÙ… Ù¾Ø§ØªØ±ÛŒÙˆØª",
        "fortress_shield": "Ø³Ù¾Ø± Ù‚Ù„Ø¹Ù‡",
        
        # Ø²Ø±Ø§Ø¯Ø®Ø§Ù†Ù‡
        "carrier": "Ù†Ø§Ùˆ Ù‡ÙˆØ§Ù¾ÛŒÙ…Ø§Ø¨Ø±",
        "military_base": "Ù¾Ø§ÛŒÚ¯Ø§Ù‡ Ù†Ø¸Ø§Ù…ÛŒ",
        
        # Ø§Ø¨Ø²Ø§Ø±Ù‡Ø§ÛŒ Ú©Ø§Ø±Ø¨Ø±Ø¯ÛŒ
        "first_aid": "Ú©ÛŒØª Ú©Ù…Ú©â€ŒÙ‡Ø§ÛŒ Ø§ÙˆÙ„ÛŒÙ‡",
        "field_medic": "Ú©ÛŒØª Ù¾Ø²Ø´Ú© Ù…ÛŒØ¯Ø§Ù†",
        
        # Ø³Ù„Ø§Ø­â€ŒÙ‡Ø§ÛŒ Ù¾Ø±ÛŒÙ…ÛŒÙˆÙ…
        "stealth_bomber": "Ø¨Ù…Ø¨â€ŒØ§ÙÚ©Ù† Ø±Ø§Ø¯Ø§Ø±Ú¯Ø±ÛŒØ²",
        "orbital_strike": "Ø­Ù…Ù„Ù‡ Ù…Ø¯Ø§Ø±ÛŒ",
        "quantum_cannon": "ØªÙˆÙ¾ Ú©ÙˆØ§Ù†ØªÙˆÙ…ÛŒ",
        
        # Ø¯ÙØ§Ø¹ Ù¾Ø±ÛŒÙ…ÛŒÙˆÙ…
        "super_aegis": "Ø³Ù¾Ø± Ø§ÛŒØ¬ÛŒØ³ Ù¾ÛŒØ´Ø±ÙØªÙ‡",
        "quantum_barrier": "Ø³Ø¯ Ú©ÙˆØ§Ù†ØªÙˆÙ…ÛŒ",
        
        # ØªÙ‚ÙˆÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡â€ŒÙ‡Ø§
        "medal_boost_small": "ØªÙ‚ÙˆÛŒØª Ú©ÙˆÚ†Ú© Ù…Ø¯Ø§Ù„",
        "medal_boost": "ØªÙ‚ÙˆÛŒØª Ù…Ø¯Ø§Ù„",
        "mega_medal_boost": "ØªÙ‚ÙˆÛŒØª Ø¹Ø¸ÛŒÙ… Ù…Ø¯Ø§Ù„",
        "energy_drink": "Ù†ÙˆØ´ÛŒØ¯Ù†ÛŒ Ø§Ù†Ø±Ú˜ÛŒ",
        "adrenaline_shot": "ØªØ²Ø±ÛŒÙ‚ Ø¢Ø¯Ø±Ù†Ø§Ù„ÛŒÙ†",
        "repair_kit": "Ú©ÛŒØª ØªØ¹Ù…ÛŒØ±",
        "nano_repair": "ØªØ¹Ù…ÛŒØ± Ù†Ø§Ù†Ùˆ",
        "experience_boost": "ØªÙ‚ÙˆÛŒØª ØªØ¬Ø±Ø¨Ù‡",
        
        # ÙˆØ¶Ø¹ÛŒØª
        "vip_status": "ÙˆØ¶Ø¹ÛŒØª VIP",
        "elite_membership": "Ø¹Ø¶ÙˆÛŒØª Ù†Ø®Ø¨Ú¯Ø§Ù†",
        
        # ÙØµÙ„ÛŒ
        "holiday_missile": "Ù…ÙˆØ´Ú© ØªØ¹Ø·ÛŒÙ„Ø§Øª",
        "anniversary_nuke": "Ø¨Ù…Ø¨ Ø³Ø§Ù„Ú¯Ø±Ø¯",
    }
}

# Comprehensive multilingual item descriptions
ITEM_DESCRIPTIONS: Dict[str, Dict[str, str]] = {
    "en": {
        # Basic Weapons
        "missile": "Standard military missile for basic attacks",
        "f22": "Advanced fighter jet with superior firepower",
        "moab": "Massive ordnance for devastating area damage",
        "nuclear": "Ultimate destruction weapon with radiation effects",
        "antimatter": "Theoretical ultimate weapon using antimatter physics",
        
        # Defense Systems
        "shield": "Basic energy barrier providing moderate protection",
        "aegis_shield": "Advanced defense system with enhanced durability",
        "intercept": "Missile defense system with counter-attack capability",
        "fortress_shield": "Heavy fortification providing maximum protection",
        
        # Arsenal
        "carrier": "Naval vessel expanding weapon storage capacity",
        "military_base": "Advanced facility for massive arsenal expansion",
        
        # Utilities
        "first_aid": "Basic medical supplies for minor health restoration",
        "field_medic": "Advanced medical equipment for significant healing",
        
        # Premium Weapons
        "stealth_bomber": "Undetectable aircraft with precision strike capability",
        "orbital_strike": "Space-based weapons platform for devastating attacks",
        "quantum_cannon": "Advanced physics weapon using quantum mechanics",
        
        # Premium Defense
        "super_aegis": "Premium defense system with superior protection",
        "quantum_barrier": "Ultimate protection field using quantum technology",
        
        # Boosts
        "medal_boost_small": "Small instant medal reward for quick progress",
        "medal_boost": "Significant medal bonus for steady advancement",
        "mega_medal_boost": "Large medal reward for major progress boost",
        "energy_drink": "Stimulant reducing combat fatigue and cooldowns",
        "adrenaline_shot": "Powerful stimulant for maximum performance boost",
        "repair_kit": "Advanced tools for complete health restoration",
        "nano_repair": "Cutting-edge nanotechnology for superior healing",
        "experience_boost": "Learning accelerator for enhanced skill development",
        
        # Status
        "vip_status": "Premium membership with exclusive benefits and bonuses",
        "elite_membership": "Ultimate membership tier with maximum privileges",
        
        # Seasonal
        "holiday_missile": "Festive explosive with celebratory effects",
        "anniversary_nuke": "Commemorative weapon for special occasions",
    },
    "fa": {
        # Ø³Ù„Ø§Ø­â€ŒÙ‡Ø§ÛŒ Ù¾Ø§ÛŒÙ‡
        "missile": "Ù…ÙˆØ´Ú© Ø§Ø³ØªØ§Ù†Ø¯Ø§Ø±Ø¯ Ù†Ø¸Ø§Ù…ÛŒ Ø¨Ø±Ø§ÛŒ Ø­Ù…Ù„Ø§Øª Ù¾Ø§ÛŒÙ‡",
        "f22": "Ø¬Ù†Ú¯Ù†Ø¯Ù‡ Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ø¨Ø§ Ù‚Ø¯Ø±Øª Ø¢ØªØ´ Ø¨Ø±ØªØ±",
        "moab": "Ù…Ù‡Ù…Ø§Øª Ø¹Ø¸ÛŒÙ… Ø¨Ø±Ø§ÛŒ Ø®Ø³Ø§Ø±Øª ÙˆÛŒØ±Ø§Ù†Ú¯Ø± Ù…Ù†Ø·Ù‚Ù‡â€ŒØ§ÛŒ",
        "nuclear": "Ø³Ù„Ø§Ø­ Ù†Ø§Ø¨ÙˆØ¯ÛŒ Ù†Ù‡Ø§ÛŒÛŒ Ø¨Ø§ Ø§Ø«Ø±Ø§Øª ØªØ´Ø¹Ø´Ø¹ÛŒ",
        "antimatter": "Ø³Ù„Ø§Ø­ Ù†Ù‡Ø§ÛŒÛŒ ØªØ¦ÙˆØ±ÛŒÚ© Ø¨Ø§ Ø§Ø³ØªÙØ§Ø¯Ù‡ Ø§Ø² ÙÛŒØ²ÛŒÚ© Ù¾Ø§Ø¯Ù…Ø§Ø¯Ù‡",
        
        # Ø³ÛŒØ³ØªÙ…â€ŒÙ‡Ø§ÛŒ Ø¯ÙØ§Ø¹ÛŒ
        "shield": "Ø³Ø¯ Ø§Ù†Ø±Ú˜ÛŒ Ù¾Ø§ÛŒÙ‡ Ø¨Ø§ Ø­ÙØ§Ø¸Øª Ù…ØªÙˆØ³Ø·",
        "aegis_shield": "Ø³ÛŒØ³ØªÙ… Ø¯ÙØ§Ø¹ÛŒ Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ø¨Ø§ Ø§Ø³ØªØ­Ú©Ø§Ù… Ø§ÙØ²Ø§ÛŒØ´ ÛŒØ§ÙØªÙ‡",
        "intercept": "Ø³ÛŒØ³ØªÙ… Ø¯ÙØ§Ø¹ Ù…ÙˆØ´Ú©ÛŒ Ø¨Ø§ Ù‚Ø§Ø¨Ù„ÛŒØª Ø¶Ø¯Ø­Ù…Ù„Ù‡",
        "fortress_shield": "Ø§Ø³ØªØ­Ú©Ø§Ù…Ø§Øª Ø³Ù†Ú¯ÛŒÙ† Ø¨Ø§ Ø­Ø¯Ø§Ú©Ø«Ø± Ø­ÙØ§Ø¸Øª",
        
        # Ø²Ø±Ø§Ø¯Ø®Ø§Ù†Ù‡
        "carrier": "Ú©Ø´ØªÛŒ Ø¬Ù†Ú¯ÛŒ Ú©Ù‡ Ø¸Ø±ÙÛŒØª Ø°Ø®ÛŒØ±Ù‡ Ø³Ù„Ø§Ø­ Ø±Ø§ Ø§ÙØ²Ø§ÛŒØ´ Ù…ÛŒâ€ŒØ¯Ù‡Ø¯",
        "military_base": "ØªØ§Ø³ÛŒØ³Ø§Øª Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ø¨Ø±Ø§ÛŒ Ú¯Ø³ØªØ±Ø´ Ø¹Ø¸ÛŒÙ… Ø²Ø±Ø§Ø¯Ø®Ø§Ù†Ù‡",
        
        # Ø§Ø¨Ø²Ø§Ø±Ù‡Ø§ÛŒ Ú©Ø§Ø±Ø¨Ø±Ø¯ÛŒ
        "first_aid": "ØªØ¬Ù‡ÛŒØ²Ø§Øª Ù¾Ø²Ø´Ú©ÛŒ Ù¾Ø§ÛŒÙ‡ Ø¨Ø±Ø§ÛŒ Ø¨Ø§Ø²Ø³Ø§Ø²ÛŒ Ø¬Ø²Ø¦ÛŒ Ø³Ù„Ø§Ù…Øª",
        "field_medic": "ØªØ¬Ù‡ÛŒØ²Ø§Øª Ù¾Ø²Ø´Ú©ÛŒ Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ø¨Ø±Ø§ÛŒ Ø¯Ø±Ù…Ø§Ù† Ù‚Ø§Ø¨Ù„ ØªÙˆØ¬Ù‡",
        
        # Ø³Ù„Ø§Ø­â€ŒÙ‡Ø§ÛŒ Ù¾Ø±ÛŒÙ…ÛŒÙˆÙ…
        "stealth_bomber": "Ù‡ÙˆØ§Ù¾ÛŒÙ…Ø§ÛŒ ØºÛŒØ±Ù‚Ø§Ø¨Ù„ ØªØ´Ø®ÛŒØµ Ø¨Ø§ Ù‚Ø§Ø¨Ù„ÛŒØª Ø­Ù…Ù„Ù‡ Ø¯Ù‚ÛŒÙ‚",
        "orbital_strike": "Ù¾Ù„ØªÙØ±Ù… ØªØ³Ù„ÛŒØ­Ø§ØªÛŒ ÙØ¶Ø§ÛŒÛŒ Ø¨Ø±Ø§ÛŒ Ø­Ù…Ù„Ø§Øª ÙˆÛŒØ±Ø§Ù†Ú¯Ø±",
        "quantum_cannon": "Ø³Ù„Ø§Ø­ ÙÛŒØ²ÛŒÚ© Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ø¨Ø§ Ø§Ø³ØªÙØ§Ø¯Ù‡ Ø§Ø² Ù…Ú©Ø§Ù†ÛŒÚ© Ú©ÙˆØ§Ù†ØªÙˆÙ…",
        
        # Ø¯ÙØ§Ø¹ Ù¾Ø±ÛŒÙ…ÛŒÙˆÙ…
        "super_aegis": "Ø³ÛŒØ³ØªÙ… Ø¯ÙØ§Ø¹ÛŒ Ù¾Ø±ÛŒÙ…ÛŒÙˆÙ… Ø¨Ø§ Ø­ÙØ§Ø¸Øª Ø¨Ø±ØªØ±",
        "quantum_barrier": "Ù…ÛŒØ¯Ø§Ù† Ø­ÙØ§Ø¸ØªÛŒ Ù†Ù‡Ø§ÛŒÛŒ Ø¨Ø§ Ø§Ø³ØªÙØ§Ø¯Ù‡ Ø§Ø² ÙÙ†Ø§ÙˆØ±ÛŒ Ú©ÙˆØ§Ù†ØªÙˆÙ…",
        
        # ØªÙ‚ÙˆÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡â€ŒÙ‡Ø§
        "medal_boost_small": "Ù¾Ø§Ø¯Ø§Ø´ ÙÙˆØ±ÛŒ Ú©ÙˆÚ†Ú© Ù…Ø¯Ø§Ù„ Ø¨Ø±Ø§ÛŒ Ù¾ÛŒØ´Ø±ÙØª Ø³Ø±ÛŒØ¹",
        "medal_boost": "Ù¾Ø§Ø¯Ø§Ø´ Ù‚Ø§Ø¨Ù„ ØªÙˆØ¬Ù‡ Ù…Ø¯Ø§Ù„ Ø¨Ø±Ø§ÛŒ Ù¾ÛŒØ´Ø±ÙØª Ù¾Ø§ÛŒØ¯Ø§Ø±",
        "mega_medal_boost": "Ù¾Ø§Ø¯Ø§Ø´ Ø¨Ø²Ø±Ú¯ Ù…Ø¯Ø§Ù„ Ø¨Ø±Ø§ÛŒ ØªÙ‚ÙˆÛŒØª Ø¹Ù…Ø¯Ù‡ Ù¾ÛŒØ´Ø±ÙØª",
        "energy_drink": "Ù…Ø­Ø±Ú© Ú©Ø§Ù‡Ø´ Ø®Ø³ØªÚ¯ÛŒ Ø¬Ù†Ú¯ÛŒ Ùˆ Ø²Ù…Ø§Ù† Ø§Ù†ØªØ¸Ø§Ø±",
        "adrenaline_shot": "Ù…Ø­Ø±Ú© Ù‚Ø¯Ø±ØªÙ…Ù†Ø¯ Ø¨Ø±Ø§ÛŒ Ø­Ø¯Ø§Ú©Ø«Ø± ØªÙ‚ÙˆÛŒØª Ø¹Ù…Ù„Ú©Ø±Ø¯",
        "repair_kit": "Ø§Ø¨Ø²Ø§Ø±Ù‡Ø§ÛŒ Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ø¨Ø±Ø§ÛŒ Ø¨Ø§Ø²Ø³Ø§Ø²ÛŒ Ú©Ø§Ù…Ù„ Ø³Ù„Ø§Ù…Øª",
        "nano_repair": "ÙÙ†Ø§ÙˆØ±ÛŒ Ù†Ø§Ù†Ùˆ Ù¾ÛŒØ´Ø±ÙØªÙ‡ Ø¨Ø±Ø§ÛŒ Ø¯Ø±Ù…Ø§Ù† Ø¨Ø±ØªØ±",
        "experience_boost": "Ø´ØªØ§Ø¨â€ŒØ¯Ù‡Ù†Ø¯Ù‡ ÛŒØ§Ø¯Ú¯ÛŒØ±ÛŒ Ø¨Ø±Ø§ÛŒ ØªÙˆØ³Ø¹Ù‡ Ù…Ù‡Ø§Ø±Øª Ø¨Ù‡Ø¨ÙˆØ¯ ÛŒØ§ÙØªÙ‡",
        
        # ÙˆØ¶Ø¹ÛŒØª
        "vip_status": "Ø¹Ø¶ÙˆÛŒØª Ù¾Ø±ÛŒÙ…ÛŒÙˆÙ… Ø¨Ø§ Ù…Ø²Ø§ÛŒØ§ Ùˆ Ù¾Ø§Ø¯Ø§Ø´â€ŒÙ‡Ø§ÛŒ Ø§Ù†Ø­ØµØ§Ø±ÛŒ",
        "elite_membership": "Ø¨Ø§Ù„Ø§ØªØ±ÛŒÙ† Ø³Ø·Ø­ Ø¹Ø¶ÙˆÛŒØª Ø¨Ø§ Ø­Ø¯Ø§Ú©Ø«Ø± Ø§Ù…ØªÛŒØ§Ø²Ø§Øª",
        
        # ÙØµÙ„ÛŒ
        "holiday_missile": "Ù…ÙˆØ§Ø¯ Ù…Ù†ÙØ¬Ø±Ù‡ Ø¬Ø´Ù†ÙˆØ§Ø±Ù‡â€ŒØ§ÛŒ Ø¨Ø§ Ø§Ø«Ø±Ø§Øª Ø¬Ø´Ù†",
        "anniversary_nuke": "Ø³Ù„Ø§Ø­ ÛŒØ§Ø¯Ø¨ÙˆØ¯ Ø¨Ø±Ø§ÛŒ Ù…Ù†Ø§Ø³Ø¨Øªâ€ŒÙ‡Ø§ÛŒ ÙˆÛŒÚ˜Ù‡",
    }
}

# Item category names in multiple languages
ITEM_CATEGORY_NAMES: Dict[str, Dict[str, str]] = {
    "en": {
        "weapons": "âš”ï¸ Weapons",
        "defense": "ðŸ›¡ï¸ Defense",
        "utilities": "ðŸ”§ Utilities",
        "boosts": "âš¡ Boosts",
        "premium": "ðŸ’Ž Premium",
        "arsenal": "ðŸ­ Arsenal",
        "seasonal": "ðŸŽŠ Seasonal",
        "special": "âœ¨ Special"
    },
    "fa": {
        "weapons": "âš”ï¸ Ø³Ù„Ø§Ø­â€ŒÙ‡Ø§",
        "defense": "ðŸ›¡ï¸ Ø¯ÙØ§Ø¹",
        "utilities": "ðŸ”§ Ø§Ø¨Ø²Ø§Ø±Ù‡Ø§ÛŒ Ú©Ø§Ø±Ø¨Ø±Ø¯ÛŒ",
        "boosts": "âš¡ ØªÙ‚ÙˆÛŒØªâ€ŒÚ©Ù†Ù†Ø¯Ù‡â€ŒÙ‡Ø§",
        "premium": "ðŸ’Ž Ù¾Ø±ÛŒÙ…ÛŒÙˆÙ…",
        "arsenal": "ðŸ­ Ø²Ø±Ø§Ø¯Ø®Ø§Ù†Ù‡",
        "seasonal": "ðŸŽŠ ÙØµÙ„ÛŒ",
        "special": "âœ¨ ÙˆÛŒÚ˜Ù‡"
    }
}

# Item rarity names and colors
ITEM_RARITY_INFO: Dict[str, Dict[str, str]] = {
    "common": {
        "name_en": "Common",
        "name_fa": "Ù…Ø¹Ù…ÙˆÙ„ÛŒ",
        "color": "âšª",
        "emoji": "ðŸ“¦"
    },
    "uncommon": {
        "name_en": "Uncommon", 
        "name_fa": "ØºÛŒØ±Ù…Ø¹Ù…ÙˆÙ„",
        "color": "ðŸŸ¢",
        "emoji": "ðŸ“—"
    },
    "rare": {
        "name_en": "Rare",
        "name_fa": "Ú©Ù…ÛŒØ§Ø¨",
        "color": "ðŸ”µ",
        "emoji": "ðŸ“˜"
    },
    "epic": {
        "name_en": "Epic",
        "name_fa": "Ø­Ù…Ø§Ø³ÛŒ",
        "color": "ðŸŸ£",
        "emoji": "ðŸ“œ"
    },
    "legendary": {
        "name_en": "Legendary",
        "name_fa": "Ø§ÙØ³Ø§Ù†Ù‡â€ŒØ§ÛŒ",
        "color": "ðŸŸ ",
        "emoji": "â­"
    },
    "mythic": {
        "name_en": "Mythic",
        "name_fa": "Ø§Ø³Ø§Ø·ÛŒØ±ÛŒ",
        "color": "ðŸ”´",
        "emoji": "ðŸ’«"
    }
}

# Enhanced item management functions
class ItemManager:
    """Advanced item management system"""
    
    @staticmethod
    def get_item_price(item_id: str) -> Tuple[int, str]:
        """Calculate item price and return with currency type"""
        item = ITEMS.get(item_id, {})
        
        if item.get("payment") == PaymentType.TG_STARS.value:
            return item.get("stars_price", 0), "tg_stars"
        elif item.get("payment") == PaymentType.MEDALS.value:
            return item.get("medals_price", 0), "medals"
        elif item.get("payment") == PaymentType.FREE.value:
            return 0, "free"
        elif item.get("payment") == PaymentType.ACHIEVEMENT.value:
            return 0, "achievement"
        
        return 0, "unknown"
    
    @staticmethod
    def calculate_damage_with_bonuses(item_id: str, base_damage: int, player_level: int = 1) -> int:
        """Calculate total damage including bonuses and critical hits"""
        item = ITEMS.get(item_id, {})
        if not item or item.get("type") != ItemType.WEAPON.value:
            return base_damage
        
        # Base weapon damage
        weapon_damage = item.get("damage", 0)
        
        # Damage bonus multiplier
        damage_bonus = item.get("damage_bonus", 0)
        
        # Level scaling
        level_bonus = (player_level - 1) * 0.05  # 5% per level above 1
        
        # Calculate total damage
        total_damage = base_damage + weapon_damage
        total_damage = int(total_damage * (1 + damage_bonus + level_bonus))
        
        return total_damage
    
    @staticmethod
    def calculate_defense_reduction(item_id: str, incoming_damage: int) -> Tuple[int, int]:
        """Calculate damage reduction and absorption"""
        item = ITEMS.get(item_id, {})
        if not item or item.get("type") not in [ItemType.SHIELD.value, ItemType.INTERCEPT.value]:
            return incoming_damage, 0
        
        effectiveness = item.get("effectiveness", 0)
        absorption = item.get("absorption", 0)
        
        # Apply absorption first
        damage_after_absorption = max(0, incoming_damage - absorption)
        absorbed_damage = incoming_damage - damage_after_absorption
        
        # Apply percentage reduction
        final_damage = int(damage_after_absorption * (1 - effectiveness))
        total_reduction = incoming_damage - final_damage
        
        return final_damage, total_reduction
    
    @staticmethod
    def get_items_by_filter(
        category: Optional[str] = None,
        payment_type: Optional[str] = None,
        rarity: Optional[str] = None,
        min_level: int = 1,
        available_only: bool = False
    ) -> Dict[str, Dict[str, Any]]:
        """Get items based on multiple filters"""
        filtered_items = {}
        
        for item_id, item_data in ITEMS.items():
            # Category filter
            if category and item_data.get("category") != category:
                continue
            
            # Payment type filter
            if payment_type and item_data.get("payment") != payment_type:
                continue
            
            # Rarity filter
            if rarity and item_data.get("rarity") != rarity:
                continue
            
            # Level requirement filter
            if item_data.get("level_required", 1) > min_level:
                continue
            
            # Availability filter
            if available_only:
                if item_data.get("limited_time", False):
                    continue
                if item_data.get("achievement_required"):
                    continue
            
            filtered_items[item_id] = item_data
        
        return filtered_items
    
    @staticmethod
    def get_item_effectiveness_rating(item_id: str) -> Dict[str, Any]:
        """Get comprehensive item effectiveness rating"""
        item = ITEMS.get(item_id, {})
        if not item:
            return {}
        
        rating = {
            "item_id": item_id,
            "overall_rating": 0,
            "damage_rating": 0,
            "defense_rating": 0,
            "utility_rating": 0,
            "cost_efficiency": 0
        }
        
        # Calculate damage rating
        if item.get("damage"):
            base_score = min(item["damage"] / 10, 10)  # Max 10 for 100+ damage
            bonus_score = (item.get("damage_bonus", 0) * 10)
            critical_score = (item.get("critical_chance", 0) * 10)
            rating["damage_rating"] = min(base_score + bonus_score + critical_score, 10)
        
        # Calculate defense rating
        if item.get("effectiveness"):
            effectiveness_score = item["effectiveness"] * 10
            duration_score = min((item.get("duration_seconds", 0) / 3600), 5)  # Max 5 for 5+ hours
            absorption_score = min((item.get("absorption", 0) / 100), 5)  # Max 5 for 500+ absorption
            rating["defense_rating"] = min(effectiveness_score + duration_score + absorption_score, 10)
        
        # Calculate utility rating
        utility_factors = []
        if item.get("hp_restore"):
            utility_factors.append(min(item["hp_restore"] / 10, 3))
        if item.get("medals_reward"):
            utility_factors.append(min(item["medals_reward"] / 100, 3))
        if item.get("cooldown_reduction"):
            utility_factors.append(item["cooldown_reduction"] * 5)
        if item.get("experience_multiplier"):
            utility_factors.append((item["experience_multiplier"] - 1) * 5)
        
        if utility_factors:
            rating["utility_rating"] = min(sum(utility_factors), 10)
        
        # Calculate cost efficiency
        price, currency = ItemManager.get_item_price(item_id)
        if price > 0:
            value_score = rating["damage_rating"] + rating["defense_rating"] + rating["utility_rating"]
            if currency == "medals":
                efficiency = value_score / (price / 100)  # Normalize medal prices
            else:  # TG Stars
                efficiency = value_score / price
            rating["cost_efficiency"] = min(efficiency, 10)
        
        # Calculate overall rating
        ratings = [rating["damage_rating"], rating["defense_rating"], rating["utility_rating"]]
        non_zero_ratings = [r for r in ratings if r > 0]
        if non_zero_ratings:
            rating["overall_rating"] = sum(non_zero_ratings) / len(non_zero_ratings)
        
        return rating

# Enhanced utility functions for item management
def get_item_price(item_id: str) -> int:
    """Calculate item price based on type and payment method (legacy function)"""
    price, _ = ItemManager.get_item_price(item_id)
    return price

def get_items_by_category(category: str) -> Dict[str, Dict[str, Any]]:
    """Get all items in a specific category"""
    return ItemManager.get_items_by_filter(category=category)

def get_items_by_payment_type(payment_type: PaymentType) -> Dict[str, Dict[str, Any]]:
    """Get all items for a specific payment type"""
    return ItemManager.get_items_by_filter(payment_type=payment_type.value)

def get_items_by_type(item_type: ItemType) -> Dict[str, Dict[str, Any]]:
    """Get all items of a specific type"""
    return {
        item_id: details 
        for item_id, details in ITEMS.items() 
        if details.get("type") == item_type.value
    }

def get_items_by_rarity(rarity: ItemRarity) -> Dict[str, Dict[str, Any]]:
    """Get all items of a specific rarity"""
    return ItemManager.get_items_by_filter(rarity=rarity.value)

def get_items_by_tier(tier: ItemTier) -> Dict[str, Dict[str, Any]]:
    """Get all items of a specific tier"""
    return {
        item_id: details 
        for item_id, details in ITEMS.items() 
        if details.get("tier") == tier.value
    }

def get_weapon_items() -> Dict[str, Dict[str, Any]]:
    """Get all weapon items"""
    return get_items_by_type(ItemType.WEAPON)

def get_defense_items() -> Dict[str, Dict[str, Any]]:
    """Get all defense items (shields and intercepts)"""
    defense_items = {}
    defense_items.update(get_items_by_type(ItemType.SHIELD))
    defense_items.update(get_items_by_type(ItemType.INTERCEPT))
    return defense_items

def get_utility_items() -> Dict[str, Dict[str, Any]]:
    """Get all utility items"""
    return get_items_by_type(ItemType.UTILITY)

def get_boost_items() -> Dict[str, Dict[str, Any]]:
    """Get all boost items"""
    return get_items_by_type(ItemType.BOOST)

def get_premium_items() -> Dict[str, Dict[str, Any]]:
    """Get all premium (TG Stars) items"""
    return get_items_by_payment_type(PaymentType.TG_STARS)

def get_medal_items() -> Dict[str, Dict[str, Any]]:
    """Get all medal-based items"""
    return get_items_by_payment_type(PaymentType.MEDALS)

def get_free_items() -> Dict[str, Dict[str, Any]]:
    """Get all free items"""
    return get_items_by_payment_type(PaymentType.FREE)

def get_seasonal_items() -> Dict[str, Dict[str, Any]]:
    """Get all seasonal/limited time items"""
    return {
        item_id: details 
        for item_id, details in ITEMS.items() 
        if details.get("limited_time", False)
    }

def get_available_items_for_level(level: int) -> Dict[str, Dict[str, Any]]:
    """Get items available for a specific level"""
    return ItemManager.get_items_by_filter(min_level=level, available_only=True)

def get_item_display_name(item_id: str, lang: str = "en") -> str:
    """Get localized display name for an item"""
    return ITEM_NAMES.get(lang, {}).get(item_id, item_id.replace("_", " ").title())

def get_item_description(item_id: str, lang: str = "en") -> str:
    """Get localized description for an item"""
    return ITEM_DESCRIPTIONS.get(lang, {}).get(item_id, "No description available")

def get_item_emoji(item_id: str) -> str:
    """Get emoji for an item"""
    item = ITEMS.get(item_id, {})
    return item.get("emoji", "ðŸ“¦")

def get_item_rarity_info(item_id: str, lang: str = "en") -> Dict[str, str]:
    """Get rarity information for an item"""
    item = ITEMS.get(item_id, {})
    rarity = item.get("rarity", "common")
    rarity_info = ITEM_RARITY_INFO.get(rarity, ITEM_RARITY_INFO["common"])
    
    return {
        "rarity": rarity,
        "name": rarity_info.get(f"name_{lang}", rarity_info["name_en"]),
        "color": rarity_info["color"],
        "emoji": rarity_info["emoji"]
    }

def get_category_display_name(category: str, lang: str = "en") -> str:
    """Get localized category display name"""
    return ITEM_CATEGORY_NAMES.get(lang, {}).get(category, category.title())

def is_weapon(item_id: str) -> bool:
    """Check if item is a weapon"""
    item = ITEMS.get(item_id, {})
    return item.get("type") == ItemType.WEAPON.value

def is_defense_item(item_id: str) -> bool:
    """Check if item is a defense item"""
    item = ITEMS.get(item_id, {})
    return item.get("type") in [ItemType.SHIELD.value, ItemType.INTERCEPT.value]

def is_utility_item(item_id: str) -> bool:
    """Check if item is a utility item"""
    item = ITEMS.get(item_id, {})
    return item.get("type") == ItemType.UTILITY.value

def is_boost_item(item_id: str) -> bool:
    """Check if item is a boost item"""
    item = ITEMS.get(item_id, {})
    return item.get("type") == ItemType.BOOST.value

def is_premium_item(item_id: str) -> bool:
    """Check if item requires TG Stars"""
    item = ITEMS.get(item_id, {})
    return item.get("payment") == PaymentType.TG_STARS.value

def is_consumable_item(item_id: str) -> bool:
    """Check if item is consumable"""
    item = ITEMS.get(item_id, {})
    return item.get("consumable", True)

def is_limited_time_item(item_id: str) -> bool:
    """Check if item is limited time"""
    item = ITEMS.get(item_id, {})
    return item.get("limited_time", False)

def requires_achievement(item_id: str) -> Optional[str]:
    """Check if item requires achievement and return achievement ID"""
    item = ITEMS.get(item_id, {})
    return item.get("achievement_required")

def get_item_level_requirement(item_id: str) -> int:
    """Get minimum level required for item"""
    item = ITEMS.get(item_id, {})
    return item.get("level_required", 1)

def get_item_max_stack(item_id: str) -> int:
    """Get maximum stack size for item"""
    item = ITEMS.get(item_id, {})
    return item.get("max_stack", 99)

def get_item_stats(item_id: str, lang: str = "en") -> Dict[str, Any]:
    """Get comprehensive stats for an item with localization"""
    item = ITEMS.get(item_id, {})
    if not item:
        return {}
    
    price, currency = ItemManager.get_item_price(item_id)
    rarity_info = get_item_rarity_info(item_id, lang)
    
    stats = {
        "id": item_id,
        "name": get_item_display_name(item_id, lang),
        "description": get_item_description(item_id, lang),
        "type": item.get("type"),
        "category": item.get("category"),
        "payment": item.get("payment"),
        "price": price,
        "currency": currency,
        "stars": item.get("stars", 1),
        "emoji": get_item_emoji(item_id),
        "rarity": rarity_info,
        "tier": item.get("tier"),
        "level_required": get_item_level_requirement(item_id),
        "max_stack": get_item_max_stack(item_id),
        "consumable": is_consumable_item(item_id),
        "limited_time": is_limited_time_item(item_id),
        "achievement_required": requires_achievement(item_id)
    }
    
    # Add type-specific stats
    if "damage" in item:
        stats["damage"] = item["damage"]
    if "damage_bonus" in item:
        stats["damage_bonus"] = item["damage_bonus"]
    if "critical_chance" in item:
        stats["critical_chance"] = item["critical_chance"]
    if "duration_seconds" in item:
        stats["duration_hours"] = item["duration_seconds"] // 3600
        stats["duration_seconds"] = item["duration_seconds"]
    if "effectiveness" in item:
        stats["effectiveness"] = item["effectiveness"]
    if "absorption" in item:
        stats["absorption"] = item["absorption"]
    if "bonus" in item:
        stats["bonus"] = item["bonus"]
    if "medals_reward" in item:
        stats["medals_reward"] = item["medals_reward"]
    if "hp_restore" in item:
        stats["hp_restore"] = item["hp_restore"]
    if "capacity" in item:
        stats["capacity"] = item["capacity"]
    if "days" in item:
        stats["days"] = item["days"]
    if "cooldown_reduction" in item:
        stats["cooldown_reduction"] = item["cooldown_reduction"]
    if "experience_multiplier" in item:
        stats["experience_multiplier"] = item["experience_multiplier"]
    
    return stats

def get_item_detailed_info(item_id: str, lang: str = "en") -> Dict[str, Any]:
    """Get detailed item information including effectiveness ratings"""
    basic_stats = get_item_stats(item_id, lang)
    effectiveness = ItemManager.get_item_effectiveness_rating(item_id)
    
    return {
        **basic_stats,
        "effectiveness_rating": effectiveness
    }

def format_item_display(item_id: str, lang: str = "en", include_price: bool = True, include_stats: bool = True) -> str:
    """Format item for display with full localization"""
    stats = get_item_stats(item_id, lang)
    if not stats:
        return f"Unknown item: {item_id}"
    
    # Build display string
    rarity_info = stats["rarity"]
    display_parts = [
        f"{rarity_info['color']} {stats['emoji']} **{stats['name']}**",
        f"_{stats['description']}_"
    ]
    
    if include_stats:
        # Add type-specific information
        if stats.get("damage"):
            bonus_text = f" (+{int(stats.get('damage_bonus', 0) * 100)}% bonus)" if stats.get("damage_bonus") else ""
            critical_text = f" ({int(stats.get('critical_chance', 0) * 100)}% critical)" if stats.get("critical_chance") else ""
            display_parts.append(f"âš”ï¸ Damage: {stats['damage']}{bonus_text}{critical_text}")
        
        if stats.get("effectiveness"):
            duration_text = f" ({stats.get('duration_hours', 0)}h)" if stats.get("duration_hours") else ""
            absorption_text = f" ({stats.get('absorption', 0)} absorption)" if stats.get("absorption") else ""
            display_parts.append(f"ðŸ›¡ï¸ Defense: {int(stats['effectiveness'] * 100)}%{duration_text}{absorption_text}")
        
        if stats.get("hp_restore"):
            display_parts.append(f"â¤ï¸ Healing: +{stats['hp_restore']} HP")
        
        if stats.get("medals_reward"):
            display_parts.append(f"ðŸ… Medal Bonus: +{stats['medals_reward']}")
        
        if stats.get("cooldown_reduction"):
            display_parts.append(f"âš¡ Cooldown: -{int(stats['cooldown_reduction'] * 100)}%")
        
        if stats.get("experience_multiplier"):
            display_parts.append(f"ðŸ“ˆ Experience: x{stats['experience_multiplier']}")
    
    if include_price and stats["price"] > 0:
        currency_emoji = "â­" if stats["currency"] == "tg_stars" else "ðŸ…"
        display_parts.append(f"ðŸ’° Price: {stats['price']} {currency_emoji}")
    
    # Add requirements and limitations
    if stats["level_required"] > 1:
        level_text = "Level" if lang == "en" else "Ø³Ø·Ø­"
        display_parts.append(f"ðŸ”’ {level_text}: {stats['level_required']}+")
    
    if stats["limited_time"]:
        limited_text = "Limited Time!" if lang == "en" else "Ø²Ù…Ø§Ù† Ù…Ø­Ø¯ÙˆØ¯!"
        display_parts.append(f"â° {limited_text}")
    
    return "\n".join(display_parts)

def validate_item_id(item_id: str) -> bool:
    """Validate if item ID exists"""
    return item_id in ITEMS

def get_all_item_ids() -> List[str]:
    """Get list of all item IDs"""
    return list(ITEMS.keys())

def get_items_summary(lang: str = "en") -> Dict[str, Any]:
    """Get comprehensive summary of items by various categories"""
    summary = {
        "total": len(ITEMS),
        "by_type": {},
        "by_category": {},
        "by_payment": {},
        "by_rarity": {},
        "by_tier": {},
        "special_counts": {
            "weapons": len(get_weapon_items()),
            "defense": len(get_defense_items()),
            "premium": len(get_premium_items()),
            "medal_based": len(get_medal_items()),
            "free_items": len(get_free_items()),
            "seasonal": len(get_seasonal_items()),
            "limited_time": len([i for i in ITEMS.values() if i.get("limited_time")]),
            "achievement_locked": len([i for i in ITEMS.values() if i.get("achievement_required")])
        }
    }
    
    # Count by type
    for item_type in ItemType:
        summary["by_type"][item_type.value] = len(get_items_by_type(item_type))
    
    # Count by category
    for category in ItemCategory:
        summary["by_category"][category.value] = len(get_items_by_category(category.value))
    
    # Count by payment type
    for payment in PaymentType:
        summary["by_payment"][payment.value] = len(get_items_by_payment_type(payment))
    
    # Count by rarity
    for rarity in ItemRarity:
        summary["by_rarity"][rarity.value] = len(get_items_by_rarity(rarity))
    
    # Count by tier
    for tier in ItemTier:
        summary["by_tier"][tier.value] = len(get_items_by_tier(tier))
    
    return summary

def search_items(query: str, lang: str = "en") -> List[str]:
    """Search items by name or description"""
    query_lower = query.lower()
    matching_items = []
    
    for item_id in ITEMS.keys():
        name = get_item_display_name(item_id, lang).lower()
        description = get_item_description(item_id, lang).lower()
        
        if query_lower in name or query_lower in description or query_lower in item_id:
            matching_items.append(item_id)
    
    return matching_items

def get_recommended_items_for_level(level: int, limit: int = 5) -> List[str]:
    """Get recommended items for a specific player level"""
    available_items = get_available_items_for_level(level)
    
    # Score items based on level appropriateness and effectiveness
    scored_items = []
    for item_id, item_data in available_items.items():
        effectiveness = ItemManager.get_item_effectiveness_rating(item_id)
        level_score = max(0, 10 - abs(level - item_data.get("level_required", 1)))
        total_score = effectiveness.get("overall_rating", 0) + level_score
        scored_items.append((item_id, total_score))
    
    # Sort by score and return top items
    scored_items.sort(key=lambda x: x[1], reverse=True)
    return [item_id for item_id, _ in scored_items[:limit]]

# Legacy compatibility functions
def get_item_config(item_id: str) -> Optional[ItemConfig]:
    """Get ItemConfig object for an item (legacy compatibility)"""
    item_data = ITEMS.get(item_id)
    if not item_data:
        return None
    
    return ItemConfig(
        type=ItemType(item_data["type"]),
        payment=PaymentType(item_data["payment"]),
        category=ItemCategory(item_data["category"]),
        rarity=ItemRarity(item_data.get("rarity", "common")),
        tier=ItemTier(item_data.get("tier", 1)),
        stars=item_data["stars"],
        title=item_data.get("title", ""),
        description=item_data.get("description", ""),
        emoji=item_data.get("emoji", "ðŸ“¦"),
        medals_price=item_data.get("medals_price"),
        stars_price=item_data.get("stars_price"),
        damage=item_data.get("damage"),
        damage_bonus=item_data.get("damage_bonus"),
        critical_chance=item_data.get("critical_chance"),
        duration_seconds=item_data.get("duration_seconds"),
        effectiveness=item_data.get("effectiveness"),
        absorption=item_data.get("absorption"),
        bonus=item_data.get("bonus"),
        medals_reward=item_data.get("medals_reward"),
        hp_restore=item_data.get("hp_restore"),
        capacity=item_data.get("capacity"),
        days=item_data.get("days"),
        cooldown_reduction=item_data.get("cooldown_reduction"),
        experience_multiplier=item_data.get("experience_multiplier"),
        limited_time=item_data.get("limited_time", False),
        achievement_required=item_data.get("achievement_required"),
        level_required=item_data.get("level_required", 1),
        consumable=item_data.get("consumable", True),
        max_stack=item_data.get("max_stack", 99),
        usage_limit=item_data.get("usage_limit")
    )

# Export enhanced item manager for external use
__all__ = [
    "ItemType", "PaymentType", "ItemCategory", "ItemRarity", "ItemTier",
    "ItemConfig", "ItemEffectConfig", "ItemManager",
    "ITEMS", "ITEM_NAMES", "ITEM_DESCRIPTIONS", "ITEM_CATEGORY_NAMES", "ITEM_RARITY_INFO",
    "get_item_price", "get_items_by_category", "get_items_by_payment_type", "get_items_by_type",
    "get_items_by_rarity", "get_items_by_tier", "get_weapon_items", "get_defense_items",
    "get_utility_items", "get_boost_items", "get_premium_items", "get_medal_items",
    "get_free_items", "get_seasonal_items", "get_available_items_for_level",
    "get_item_display_name", "get_item_description", "get_item_emoji", "get_item_rarity_info",
    "get_category_display_name", "is_weapon", "is_defense_item", "is_utility_item",
    "is_boost_item", "is_premium_item", "is_consumable_item", "is_limited_time_item",
    "requires_achievement", "get_item_level_requirement", "get_item_max_stack",
    "get_item_stats", "get_item_detailed_info", "format_item_display",
    "validate_item_id", "get_all_item_ids", "get_items_summary", "search_items",
    "get_recommended_items_for_level", "get_item_config"
]

