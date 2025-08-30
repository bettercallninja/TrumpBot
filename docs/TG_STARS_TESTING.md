# TG Stars Testing Guide

This document provides step-by-step instructions for testing the TG Stars integration in TrumpBot.

## Prerequisites

- A Telegram group with TrumpBot added
- Admin permissions in the group
- A test Telegram account

## Test Cases

### 1. Checking TG Stars Balance

**Test Steps:**
1. Send `/stars` command in the group
2. Verify that your current TG Stars balance is displayed
3. Verify that available premium items are listed

**Expected Result:**
- A message showing your current TG Stars balance
- A list of premium items with their prices

### 2. Viewing Status with TG Stars

**Test Steps:**
1. Send `/status` command in the group
2. Verify that TG Stars balance is displayed along with other stats

**Expected Result:**
- Status message includes TG Stars balance with 💎 icon
- All other stats are displayed correctly

### 3. Viewing Premium Items in Shop

**Test Steps:**
1. Send `/shop` command in the group
2. Verify that there is a separate section for premium items
3. Verify that premium items are marked with 💎 icon

**Expected Result:**
- Shop menu shows separate sections for medal items and TG Stars items
- Premium items are clearly marked with 💎 icon
- Premium items show TG Stars price

### 4. Buying a Premium Item

**Test Steps:**
1. Send `/shop` command in the group
2. Select a premium item to purchase
3. Confirm the purchase
4. Complete the Telegram payment process
5. Verify that the item is added to your inventory
6. Verify that your TG Stars balance is updated

**Expected Result:**
- Purchase confirmation message is displayed
- After payment, item is added to inventory
- TG Stars balance is reduced by the item's price

### 5. Viewing Premium Items in Inventory

**Test Steps:**
1. Purchase a premium item (see Test Case 4)
2. Send `/inv` command in the group
3. Verify that premium items are displayed in a separate section

**Expected Result:**
- Inventory shows a "Premium Items" section at the top
- Premium items are clearly marked
- Regular items are shown in their respective categories

### 6. Using Premium Items

**Test Steps:**
1. Purchase a premium weapon (like Mega Nuclear Warhead)
2. Reply to another user's message and send `/attack`
3. Select the premium weapon from the attack menu
4. Verify that the attack is executed with the premium weapon

**Expected Result:**
- Attack menu shows the premium weapon
- Attack is executed successfully
- Damage dealt matches the premium weapon's power

### 7. Using Premium Shields

**Test Steps:**
1. Purchase a Super Aegis Shield
2. Activate it using the inventory
3. Verify that the shield is active in your status
4. Have another user attack you
5. Verify that the shield protects you

**Expected Result:**
- Shield is activated successfully
- Status shows shield is active with the correct duration
- Attack from another user is blocked

### 8. Using Medal Boost

**Test Steps:**
1. Note your current medal count
2. Purchase a Medal Boost
3. Verify that your medal count increases by 500

**Expected Result:**
- Medal count increases by exactly 500
- Confirmation message is displayed

### 9. Error Handling: Insufficient TG Stars

**Test Steps:**
1. Ensure your TG Stars balance is less than the price of an item
2. Try to purchase that item
3. Verify that an appropriate error message is displayed

**Expected Result:**
- Error message stating you don't have enough TG Stars
- Option to add more TG Stars

### 10. Adding TG Stars (Admin Only)

**Test Steps:**
1. Use the admin command to add TG Stars to a user
2. Verify that the user's TG Stars balance is updated

**Expected Result:**
- TG Stars are added to the user's balance
- Confirmation message is displayed

## Edge Cases to Test

1. **Concurrent Purchases:**
   - Try to purchase multiple items simultaneously
   - Verify that all transactions are processed correctly

2. **Connection Issues:**
   - Simulate connection issues during purchase
   - Verify that the system handles it gracefully

3. **Expired Payments:**
   - Start a payment but don't complete it
   - Verify that expired payments are handled correctly

4. **Group vs Private Chat:**
   - Test the `/stars` command in both group and private chats
   - Verify appropriate behavior in each context

## Report Issues

If you encounter any issues during testing, please document:
1. The exact steps to reproduce the issue
2. Expected vs actual behavior
3. Any error messages displayed
4. Screenshots if applicable

Report issues to the development team for resolution.
