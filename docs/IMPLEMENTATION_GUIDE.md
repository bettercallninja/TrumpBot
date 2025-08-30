# IMPLEMENTATION GUIDE FOR ENHANCED ATTACK SYSTEM

## Introduction
This guide provides instructions for enhancing the TrumpBot with natural language attack commands, 
weapon selection, and improved inventory display. These enhancements will make the game more 
interactive and engaging for users.

## Features Added
1. Natural language attack commands (attack by replying to someone with attack phrases)
2. Weapon selection menu before attacks
3. Enhanced attack results with weapon-specific messages
4. Improved visual feedback for attacks (emoji, detailed results)
5. Rematch and stats buttons after attacks
6. Enhanced inventory display with categories and visual elements
7. Detailed player stats display

## Implementation Instructions

### Step 1: Copy Functions from attack_enhancements.py
Copy the following functions to the main.py file:

- `find_user_by_id(chat_id, user_id)` - Add after `find_defender(m)`
- `get_weapon_emoji(weapon_type)` - Add to utility functions section
- `get_weapon_display_name(weapon_type, lang)` - Add to utility functions section
- `select_weapon(chat_id, user_id, requested_weapon)` - Add to weapons section
- `detect_weapon_type(text, lang)` - Add to weapons section
- `show_weapon_selection(m, lang)` - Add to attack command section
- `after_attack_buttons(attacker_id, defender_id, lang)` - Add to attack command section
- `process_attack(m, weapon_type)` - Replace current attack logic

### Step 2: Replace Command Handlers
Replace these existing handlers:

1. Replace the existing `attack_cmd(m)` function with the new one that shows weapon selection
2. Add the `handle_natural_language_attacks(m)` function after the message handlers section
3. Replace the existing `inventory_cmd(m)` function with the enhanced one from inventory_enhancements.py

### Step 3: Add Callback Handlers
Add these new callback handlers:

1. `attack_weapon_cb(c)` - For weapon selection
2. `rematch_cb(c)` - For rematch button after attacks
3. `stats_cb(c)` - For showing player stats

### Step 4: Update Database Schema
Make sure your database has the necessary tables and fields:

1. Ensure the `user_data` table exists with (chat_id, user_id, key, value) columns
2. Make sure the `attacks` table has a `weapon` column to store the weapon used

### Step 5: Test Implementation
Test all new features:

1. Natural language attacks: Reply to a user with "fire missiles" or similar phrases
2. Weapon selection: Use /attack without replying to anyone
3. Enhanced inventory: Use /inv command to see the new display
4. Stats button: Press the stats button after an attack
5. Rematch button: Try the rematch button after an attack cooldown

## Key Code Changes

### Natural Language Attack Handler
```python
@bot.message_handler(func=lambda m: m.chat.type != 'private' and m.text and not m.text.startswith('/') and m.reply_to_message)
def handle_natural_language_attacks(m):
    # Check if the message contains attack keywords
    attack_keywords_en = ["attack", "fire", "launch", "missile", "strike", "bomb", "hit", "shoot"]
    attack_keywords_fa = ["حمله", "شلیک", "موشک", "بزن", "آتش", "بمباران", "ضربه"]
    
    # Check if message contains any attack keywords
    message_lower = m.text.lower()
    contains_attack_keyword = any(keyword in message_lower for keyword in attack_keywords_en + attack_keywords_fa)
    
    if not contains_attack_keyword:
        # If not an attack command, pass to regular message handler
        handle_regular_messages(m)
        return
    
    # Process the attack with detected weapon
    weapon_type = detect_weapon_type(m.text, lang)
    process_attack(m, weapon_type)
```

### Attack Command Changes
```python
@bot.message_handler(commands=['attack'])
def attack_cmd(m):
    # ...existing checks...
    
    # Show weapon selection if no defender specified
    if not m.reply_to_message and not get_args(m):
        show_weapon_selection(m, lang)
        return
    
    # ...existing defender checks...
    
    # Process the attack
    process_attack(m, "std")
```

## Additional Notes
- The code is designed to be modular, so you can implement it in stages
- All code is compatible with the existing database schema and functions
- Persian language support is included in all new features
- The weapon selection system preserves your inventory management system

## Future Enhancements
After implementing these changes, consider these future enhancements:
1. More weapon types with special effects
2. Alliance system for group attacks
3. Defensive equipment beyond shields
4. Achievement system for successful attacks/defenses
5. Special attack modes (stealth, precision, etc.)
