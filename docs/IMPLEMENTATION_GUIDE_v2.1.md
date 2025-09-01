# IMPLEMENTATION GUIDE FOR v2.1 ENHANCEMENTS

## Introduction
This guide provides instructions for implementing the TrumpBot v2.1 enhancements, including fixes for weapon selection, shield activation, stats buttons, and feature cross-linking. These improvements address key usability issues and create a more cohesive experience.

## Features Added/Fixed
1. Fixed weapon selection when using `/attack` without reply
2. Added `/shield` command for quick shield activation
3. Fixed stats buttons functionality (weapon stats and trends)
4. Added cross-linking between inventory and status screens
5. Enhanced help system with clearer instructions
6. Updated BotFather commands

## Implementation Instructions

### 1. Attack System Fixes

#### Fix Weapon Selection Logic
In `src/commands/attack.py`, update the `attack_command()` function:

```python
# Show weapon selection menu when no reply is provided
if not message.reply_to_message:
    # Display current weapon and weapon selection options
    current_weapon = await get_user_weapon(message.chat.id, message.from_user.id)
    
    # Build inline keyboard with weapon options
    markup = types.InlineKeyboardMarkup(row_width=2)
    # Add buttons for each weapon
    # Add clear instruction text
    
    await bot.reply_to(
        message,
        get("select_weapon", lang) + "\n" + 
        get("current_weapon", lang).format(weapon=get_weapon_name(current_weapon, lang)),
        reply_markup=markup
    )
    return
```

#### Improve Callback Handler
Update `handle_attack_callback()` to:
1. Save selected weapon to user data
2. Provide feedback about weapon selection
3. Include instructions for using the weapon

### 2. Shield Command Implementation

#### Add Shield Command
Create a new function in `src/commands/status.py`:

```python
@bot.message_handler(commands=['shield'])
async def shield_command(message):
    """Direct command to activate shield"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    lang = await get_user_language(user_id)
    
    # Check if user has shield
    has_shield = await user_has_item(chat_id, user_id, "shield")
    
    if not has_shield:
        await bot.reply_to(message, get("no_shield_owned", lang))
        return
        
    # Check if defense already active
    active_defense = await get_active_defense(chat_id, user_id)
    if active_defense:
        await bot.reply_to(message, get("defense_already_active", lang))
        return
        
    # Activate shield
    shield_item = "shield"  # Default shield item
    hours = 6  # Default duration
    
    success = await activate_defense(chat_id, user_id, shield_item, hours)
    if success:
        await bot.reply_to(
            message, 
            get("shield_activated_success", lang).format(
                item_name=get_item_name(shield_item, lang),
                hours=hours
            )
        )
    else:
        await bot.reply_to(message, get("item_use_failed", lang))
```

### 3. Stats System Fixes

#### Fix Stats Buttons
In `src/commands/stats.py`, update the keyboard creation:

```python
# Create buttons for different stats views
markup = types.InlineKeyboardMarkup(row_width=2)
markup.add(
    types.InlineKeyboardButton(
        get("weapons_button", lang), 
        callback_data=f"stats_weapons:{user_id}"
    ),
    types.InlineKeyboardButton(
        get("trends_button", lang), 
        callback_data=f"stats_trends:{user_id}"
    )
)
```

#### Implement Missing Callback Handlers
Add these handlers in `src/handlers/callbacks.py`:

```python
@bot.callback_query_handler(func=lambda c: c.data.startswith('stats_weapons:'))
async def handle_weapons_stats_callback(callback_query):
    """Handle weapons stats button"""
    user_id = int(callback_query.data.split(':')[1])
    chat_id = callback_query.message.chat.id
    lang = await get_user_language(callback_query.from_user.id)
    
    # Fetch weapon stats data
    weapons_data = await get_user_weapons_stats(chat_id, user_id)
    
    # Format and display weapons stats
    response = format_weapons_stats(weapons_data, lang)
    
    # Update the message with the weapons stats
    await bot.edit_message_text(
        response,
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        parse_mode='HTML',
        reply_markup=get_back_to_stats_button(user_id, lang)
    )

@bot.callback_query_handler(func=lambda c: c.data.startswith('stats_trends:'))
async def handle_trends_stats_callback(callback_query):
    """Handle trends stats button"""
    user_id = int(callback_query.data.split(':')[1])
    chat_id = callback_query.message.chat.id
    lang = await get_user_language(callback_query.from_user.id)
    
    # Fetch trends data
    trends_data = await get_user_stats_trends(chat_id, user_id)
    
    # Format and display trends
    response = format_trends_stats(trends_data, lang)
    
    # Update the message with the trends stats
    await bot.edit_message_text(
        response,
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        parse_mode='HTML',
        reply_markup=get_back_to_stats_button(user_id, lang)
    )
```

### 4. Feature Cross-Linking

#### Add Status Button to Inventory
In `src/commands/inventory.py`, add this to the keyboard:

```python
# Add status button
markup.add(
    types.InlineKeyboardButton(
        get("status_button", lang),
        callback_data=f"check_status:{user_id}"
    )
)
```

#### Add Inventory Button to Status
In `src/commands/status.py`, add this to the keyboard:

```python
# Add inventory button
markup.add(
    types.InlineKeyboardButton(
        get("inventory_button", lang),
        callback_data=f"view_inventory:{user_id}"
    )
)
```

#### Implement Cross-Link Callbacks
Add these handlers in `src/handlers/callbacks.py`:

```python
@bot.callback_query_handler(func=lambda c: c.data.startswith('check_status:'))
async def handle_check_status_callback(callback_query):
    """Redirect to status screen from inventory"""
    user_id = int(callback_query.data.split(':')[1])
    # Call status function with the same parameters as status command
    await status_command(callback_query.message, target_user_id=user_id)
    await bot.answer_callback_query(callback_query.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith('view_inventory:'))
async def handle_view_inventory_callback(callback_query):
    """Redirect to inventory screen from status"""
    user_id = int(callback_query.data.split(':')[1])
    # Call inventory function with the same parameters as inventory command
    await inventory_command(callback_query.message, target_user_id=user_id)
    await bot.answer_callback_query(callback_query.id)
```

### 5. Translations Update

Add all new translation keys to `src/utils/translations.py` for both English and Persian languages:

```python
# Attack System
"select_weapon": "Select your weapon:",
"current_weapon": "Current weapon: {weapon}",
"weapon_changed": "✅ Your weapon has been changed to {weapon}!",

# Shield Command
"shield_command_help": "Activate a shield to block incoming attacks",
"shield_command_description": "Activate your shield",
"no_shield_owned": "❌ You don't own any shields! Purchase from /shop.",
"shield_activated_success": "✅ {item_name} activated for {hours} hours!",

# Stats System
"weapons_button": "🔫 Weapons",
"trends_button": "📈 Trends",
"weapon_stats_title": "🔫 Weapon Statistics",

# Cross-Linking
"inventory_button": "📦 Inventory",
"status_button": "📊 Status",
"view_inventory": "📦 View Inventory",
"check_status": "📊 Check Status",
```

### 6. BotFather Commands Update

Update `BotFather_Commands.txt` with the new commands, especially:
- `shield - Activate a shield to block incoming attacks`
- Updated description for `attack - Attack another player or select your weapon`

## Testing Checklist

✅ Using `/attack` without reply shows weapon selection menu
✅ Weapon selection persists between attacks
✅ `/shield` command activates shield directly
✅ Stats buttons (weapons and trends) work correctly
✅ Status button in inventory opens status screen
✅ Inventory button in status opens inventory
✅ All new translations display correctly in both languages

## Troubleshooting

1. **Weapon selection not saving**: Check database writes for user preferences
2. **Shield activation failing**: Verify item ownership and defense status checks
3. **Button handlers not working**: Ensure callback patterns match exactly
4. **Cross-linking not working**: Check user_id is correctly passed in callback data

---

This implementation guide provides a comprehensive roadmap for implementing all the enhancements in TrumpBot v2.1. Follow each section carefully to ensure all features work as expected.
