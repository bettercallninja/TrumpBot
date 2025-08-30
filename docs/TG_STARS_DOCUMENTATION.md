# TG Stars Integration Documentation

This document outlines the integration of Telegram Stars (TG Stars) into the TrumpBot game system.

## Overview

TG Stars are a premium currency that allows players to purchase exclusive items in the game. These premium items provide enhanced capabilities that aren't available through the regular medal-based economy.

## Features Implemented

### 1. TG Stars Balance

- Players can check their TG Stars balance using the `/stars` command
- The balance is also displayed in the player's status using `/status`

### 2. Premium Shop

- The shop now has a dedicated section for premium items purchasable with TG Stars
- Premium items are marked with a 💎 icon

### 3. Premium Inventory

- The inventory display now has a separate section for premium items
- Premium items are clearly distinguished from regular items

### 4. Payment Processing

- Secure payment flow for TG Stars transactions
- Transaction history tracking in the database
- Error handling for failed payments

## Database Structure

The integration utilizes two main database tables:

### 1. Players Table (Existing)

A new column `tg_stars` has been added to the players table to track the balance:

```sql
ALTER TABLE players ADD COLUMN tg_stars INT DEFAULT 0;
```

### 2. TG Stars Purchases Table (New)

```sql
CREATE TABLE IF NOT EXISTS tg_stars_purchases(
  id SERIAL PRIMARY KEY,
  chat_id BIGINT,
  user_id BIGINT,
  payment_id TEXT,
  item_id TEXT,
  stars_amount INT,
  purchase_time BIGINT,
  status TEXT
);
```

## Commands & Callbacks

### New Commands

- `/stars` - Check TG Stars balance and view available premium items

### Modified Commands

- `/status` - Now displays TG Stars balance along with other stats
- `/inventory` - Now separates and highlights premium items
- `/shop` - Now has a separate section for premium items

### New Callbacks

- `go:stars` - Navigate to the stars information screen
- `buy_tg:item_id` - Initiate purchase of a premium item with TG Stars
- `tg_stars_purchase:item_id:payment_id` - Confirm TG Stars purchase

## Premium Items

The following premium items have been added to the game:

1. **Super Aegis Shield (12h)**
   - Longer-lasting shield compared to the regular version
   - Cost: TG Stars

2. **Mega Nuclear Warhead**
   - Extra powerful weapon (+100 damage)
   - Cost: TG Stars

3. **Stealth Bomber**
   - High damage weapon (+75 damage)
   - Cost: TG Stars

4. **Medal Boost**
   - Instantly adds 500 medals to the player's balance
   - Cost: TG Stars

5. **VIP Status (30 days)**
   - Provides special benefits for 30 days
   - Cost: TG Stars

## User Flow

1. User checks their TG Stars balance with `/stars`
2. User browses premium items in the shop
3. User selects a premium item to purchase
4. Bot confirms the purchase and price
5. User completes payment through Telegram
6. Bot delivers the item to the user's inventory
7. User can see their premium items in a special section of their inventory

## Technical Implementation

- TG Stars balance is stored in the `players` table
- Purchases are tracked in the `tg_stars_purchases` table
- Premium items are differentiated from regular items with the `payment` field set to "tg_stars"
- Visual indicators (💎 icons) are used throughout the UI to highlight premium items

## Future Enhancements

1. **Subscription-Based Premium Items**:
   - Items that provide benefits over time
   - Auto-renewal options

2. **Bundle Deals**:
   - Packages of multiple premium items at a discount

3. **Gifting System**:
   - Allow players to gift premium items to others

4. **Seasonal Premium Items**:
   - Limited-time premium items for special events or holidays
