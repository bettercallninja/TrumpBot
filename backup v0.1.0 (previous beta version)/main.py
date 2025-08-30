# trump_wargame_bot_pg_v2.py
# Telegram PvP War Game — Donald Trump theme 🇺🇸
# Features:
# - PvP inside groups (reply/mention to attack)
# - Bilingual FA/EN with per-user language
# - UX: inline menus, counter buttons, short commands
# - Humor: ""We're making <b>{group}</b> great again—believe me." 😉",
#    "inv": "🎒 <b>Weapons Arsenal</b>\n{lines}",
#    "empty_inv": "— empty —",
# - Defense: Shield (block) & Intercept (reduce hit chance)
# - Stars Shop (XTR): Aegis Shield, Patriot Boost, MOAB Heavy Bomb
# - Medals economy, Daily bonus
# - Inventory + auto-use MOAB
# - Leaderboard /top, Inventory /inv
# - PostgreSQL storage

import os, time, random
from datetime import datetime
from psycopg_pool import ConnectionPool
import telebot
from telebot import types
from apscheduler.schedulers.background import BackgroundScheduler

BOT_TOKEN = os.getenv("BOT_TOKEN", "PUT_YOUR_TOKEN_HERE")
DATABASE_URL = os.getenv("DATABASE_URL", "postgres_url")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
pool = ConnectionPool(min_size=1, max_size=15, conninfo=DATABASE_URL)


def db(sql, params=None, fetch=None):
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            if fetch == "one":
                r = cur.fetchone()
            elif fetch == "all":
                r = cur.fetchall()
            else:
                r = None
        conn.commit()
        return r
    finally:
        pool.putconn(conn)


# --- schema ---
db("""
CREATE TABLE IF NOT EXISTS groups(
  chat_id BIGINT PRIMARY KEY,
  title TEXT,
  username TEXT,
  lang TEXT DEFAULT 'en'
);
CREATE TABLE IF NOT EXISTS players(
  chat_id BIGINT,
  user_id BIGINT,
  first_name TEXT,
  username TEXT,
  lang TEXT DEFAULT 'en',
  medals INT DEFAULT 150,
  score INT DEFAULT 0,
  level INT DEFAULT 1,
  shield_until BIGINT DEFAULT 0,
  intercept_until BIGINT DEFAULT 0,
  intercept_bonus INT DEFAULT 0,
  last_active BIGINT DEFAULT 0,
  tg_stars INT DEFAULT 0,
  PRIMARY KEY(chat_id, user_id)
);
CREATE INDEX IF NOT EXISTS players_by_score ON players(chat_id, score DESC);
CREATE TABLE IF NOT EXISTS cooldowns(
  chat_id BIGINT, user_id BIGINT, action TEXT, until_ts BIGINT,
  PRIMARY KEY(chat_id, user_id, action)
);
CREATE TABLE IF NOT EXISTS purchases(
  id BIGSERIAL PRIMARY KEY,
  chat_id BIGINT, user_id BIGINT,
  item TEXT, stars INT, ts BIGINT, payload TEXT,
  payment_type TEXT DEFAULT 'medals'
);
CREATE TABLE IF NOT EXISTS attacks(
  id BIGSERIAL PRIMARY KEY,
  chat_id BIGINT, attacker_id BIGINT, defender_id BIGINT,
  weapon TEXT, ts BIGINT, hit BOOL, dmg INT
);
CREATE TABLE IF NOT EXISTS inventories(
  chat_id BIGINT, user_id BIGINT, item TEXT, qty INT DEFAULT 0,
  PRIMARY KEY(chat_id, user_id, item)
);
CREATE TABLE IF NOT EXISTS quizzes(
  id BIGSERIAL PRIMARY KEY,
  chat_id BIGINT, 
  question TEXT,
  correct_answer TEXT,
  options TEXT[],
  created_at BIGINT,
  solved_by BIGINT,
  solved_at BIGINT
);
""")


def now(): return int(time.time())

# Helper function to get command arguments
def get_args(message):
    """Extract arguments from a command message"""
    if not message.text:
        return ""
    command_end = message.text.find(' ')
    if command_end == -1:
        return ""
    return message.text[command_end+1:].strip()

# User level system
# User level system
def calculate_level(score):
    # Simple level calculation based on score
    # Level 1: 0-99, Level 2: 100-299, Level 3: 300-599, etc.
    if score < 100:
        return 1
    elif score < 300:
        return 2
    elif score < 600:
        return 3
    elif score < 1000:
        return 4
    else:
        return 5 + (score - 1000) // 500  # Level increases every 500 points after level 5

def update_player_level(chat_id, user_id):
    # Get current score
    r = db("SELECT score FROM players WHERE chat_id=%s AND user_id=%s", (chat_id, user_id), fetch="one")
    if not r:
        return 1
    
    score = r[0]
    level = calculate_level(score)
    
    # Update player level in database
    db("UPDATE players SET level=%s WHERE chat_id=%s AND user_id=%s", (level, chat_id, user_id))
    return level

def get_player_level_info(chat_id, user_id):
    # Get current score and level
    r = db("SELECT score, level FROM players WHERE chat_id=%s AND user_id=%s", (chat_id, user_id), fetch="one")
    if not r:
        return {"level": 1, "score": 0, "next_level_score": 100, "progress": 0}
    
    score, current_level = r
    
    # Calculate scores needed for next level
    if current_level < 5:
        next_levels = [0, 100, 300, 600, 1000]
        next_level_score = next_levels[current_level]
        if current_level > 0:
            progress = (score - next_levels[current_level-1]) / (next_level_score - next_levels[current_level-1]) * 100
        else:
            progress = score / next_level_score * 100
    else:
        next_level_score = 1000 + (current_level - 4) * 500
        progress = (score - (next_level_score - 500)) / 500 * 100
    
    return {
        "level": current_level,
        "score": score,
        "next_level_score": next_level_score,
        "progress": min(100, max(0, progress))  # Ensure progress is between 0-100%
    }

# --- Activity Scoring System ---
def update_activity_score(chat_id, user_id, action_type):
    # Different actions have different point values
    points = {
        "message": 1,       # Regular message
        "attack": 5,        # Attack action
        "defend": 3,        # Defend action
        "shield": 2,        # Shield action
        "quiz_correct": 10, # Correct quiz answer
        "daily_bonus": 2    # Claimed daily bonus
    }
    
    # Update the player's activity score
    score_value = points.get(action_type, 1)
    db("UPDATE players SET score = score + %s, last_active = %s WHERE chat_id = %s AND user_id = %s", 
       (score_value, now(), chat_id, user_id))
    
    # Update player level based on new score
    update_player_level(chat_id, user_id)
    
    # Return the new score
    r = db("SELECT score FROM players WHERE chat_id = %s AND user_id = %s", 
           (chat_id, user_id), fetch="one")
    return r[0] if r else score_value


# --- i18n ---
T = {
  "en": {
    "brand": "🇺🇸 <b>Donald Trump WarBot</b>",
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
    "lang_set_fa": "زبان به فارسی تنظیم شد.",
    "status_self": "<b>{name}</b>\n🏅 Medals: <b>{medals}</b> | 🏆 Score: <b>{score}</b>\n🛡️ Shield: {shield} | 🛰️ Intercept: {intercept}",
    "status_hint": "Tip: reply to someone and send /attack to strike.",
    "shield_on": "🛡️ <b>Aegis Shield</b> up for <b>{hours}h</b>. No hits can land.",
    "shield_left": "🛡️ Shield active for {mins} minutes.",
    "def_on": "🛰️ <b>Patriot</b> online for <b>{hours}h</b> (+{bonus}% intercept).",
    "def_left": "🛰️ Interceptors active for {mins} minutes.",
    "no_target_bot": "❌ You can’t attack the bot itself.",
    "no_target_self": "😅 You can’t attack yourself.",
    "need_reply": "Reply to a user's message or mention them to attack.",
    "attack_ok": "🚀 <b>{attacker}</b> attacked <b>{defender}</b>\n🎯 Hit chance: {pct}% | 🛰️ Intercept +{bonus}%\n{result}",
    "attack_blocked": "🛡️ Defender's shield blocked the attack.",
    "attack_hit": "💥 DIRECT HIT! <b>{defender}</b> loses {dmg} medals, <b>{attacker}</b> +{score} score.",
    "attack_miss": "🤏 Missed by inches!",
    "cooldown": "⏱️ On cooldown. Try again in {m} seconds.",
    "not_enough_medals": "Not enough medals. Claim /bonus.",
    "shop": "🛍️ <b>Military Equipment Shop</b> — pick an item:",
    "buy_done": "✅ Purchase completed: <b>{item}</b>.",
    "bonus_ok": "🎁 Daily bonus: +<b>{medals}</b> medals.",
    "bonus_wait": "⏳ Already claimed. Try again in <b>{hrs}h</b>.",
    "humor": "“We’re making <b>{group}</b> great again—believe me.” 😉",
    "inv": "🎒 <b>Inventory</b>\n{lines}",
    "empty_inv": "— empty —",
    "top": "🏆 <b>Leaderboard</b>\n{lines}"
  },
  "fa": {
    "brand": "🇺🇸 <b>دونالد ترامپ وار‌بات</b>",
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
    "lang_set_fa": "زبان به فارسی تنظیم شد.",
    "status_self": "<b>{name}</b>\n🏅 مدال‌ها: <b>{medals}</b> | 🏆 امتیاز: <b>{score}</b>\n🛡️ سپر محافظ: {shield} | 🛰️ سیستم پدافند: {intercept}",
    "status_hint": "نکته: روی پیام فرد مورد نظر ریپلای کرده و /attack را ارسال کنید.",
    "shield_on": "🛡️ <b>سپر محافظ ایجیس</b> برای <b>{hours} ساعت</b> فعال شد. هیچ حمله‌ای به شما آسیب نمی‌رساند.",
    "shield_left": "🛡️ سپر محافظ فعال است: {mins} دقیقه باقی‌مانده.",
    "def_on": "🛰️ <b>سامانه پاتریوت</b> به مدت <b>{hours} ساعت</b> فعال شد (+{bonus}% قابلیت رهگیری).",
    "def_left": "🛰️ سامانه پدافند فعال است: {mins} دقیقه باقی‌مانده.",
    "no_target_bot": "❌ شما نمی‌توانید به خود بات حمله کنید.",
    "no_target_self": "😅 شما نمی‌توانید به خودتان حمله کنید.",
    "need_reply": "برای حمله باید روی پیام فرد مورد نظر ریپلای کنید یا نام کاربری او را منشن کنید.",
    "attack_ok": "🚀 <b>{attacker}</b> به <b>{defender}</b> حمله کرد\n🎯 احتمال اصابت: {pct}% | 🛰️ رهگیری: +{bonus}%\n{result}",
    "attack_blocked": "🛡️ سپر محافظ مدافع، حمله را کاملاً دفع کرد.",
    "attack_hit": "💥 اصابت مستقیم! <b>{defender}</b> {dmg} مدال از دست داد، <b>{attacker}</b> +{score} امتیاز.",
    "attack_miss": "🤏 حمله به هدف اصابت نکرد!",
    "cooldown": "⏱️ در حال استراحت سلاح‌ها. {m} ثانیه دیگر دوباره تلاش کنید.",
    "not_enough_medals": "مدال‌های شما کافی نیست. برای دریافت مدال روزانه /bonus را ارسال کنید.",
    "shop": "🛍️ <b>فروشگاه تجهیزات نظامی</b> — یک آیتم انتخاب کنید:",
    "buy_done": "✅ خرید با موفقیت انجام شد: <b>{item}</b>.",
    "bonus_ok": "🎁 پاداش روزانه: +<b>{medals}</b> مدال دریافت کردید.",
    "bonus_wait": "⏳ شما امروز پاداش خود را دریافت کرده‌اید. حدود <b>{hrs} ساعت</b> دیگر دوباره تلاش کنید.",
    "humor": "«ما گروه <b>{group}</b> را دوباره بزرگ خواهیم کرد—این قول من است!» 😉",
    "inv": "🎒 <b>انبار تسلیحات شما</b>\n{lines}",
    "empty_inv": "— خالی —",
    "top": "🏆 <b>برترین‌های گروه</b>\n{lines}"
  }
}

ITEMS = {
  # Star-rated items (1-5 stars) for medals
  "aegis":  {"title":"Aegis Shield (3h)", "stars":3, "type":"shield", "hours":3, "payment":"medals"},
  "patriot":  {"title":"Patriot Boost (12h)", "stars":2, "type":"intercept", "bonus":20, "hours":12, "payment":"medals"},
  "moab":  {"title":"MOAB Heavy Bomb (next attack +25 dmg)", "stars":4, "type":"weapon", "dmg":25, "payment":"medals"},
  "f22":  {"title":"F22 Raptor Heavy Attack (next attack +5 dmg)", "stars":1, "type":"weapon", "dmg":5, "payment":"medals"},
  "nuclear":  {"title":"Nuclear Warhead (next attack +50 dmg)", "stars":5, "type":"weapon", "dmg":50, "payment":"medals"},
  "carrier":  {"title":"Aircraft Carrier (permanent inventory)", "stars":5, "type":"arsenal", "capacity":5, "payment":"medals"},
  
  # Premium items requiring Telegram Stars
  "super_aegis": {"title":"Super Aegis Shield (12h)", "stars":2, "type":"shield", "hours":12, "payment":"tg_stars"},
  "mega_nuke": {"title":"Mega Nuclear Warhead (next attack +100 dmg)", "stars":3, "type":"weapon", "dmg":100, "payment":"tg_stars"},
  "stealth_bomber": {"title":"Stealth Bomber (next attack +75 dmg)", "stars":2, "type":"weapon", "dmg":75, "payment":"tg_stars"},
  "medal_boost": {"title":"Medal Boost (+500 medals)", "stars":1, "type":"boost", "medals":500, "payment":"tg_stars"},
  "vip_status": {"title":"VIP Status (30 days)", "stars":5, "type":"status", "days":30, "payment":"tg_stars"},
}


def ensure_group(chat_id, title, username):
    db("INSERT INTO groups(chat_id,title,username) VALUES(%s,%s,%s) ON CONFLICT (chat_id) DO UPDATE SET title=EXCLUDED.title, username=EXCLUDED.username",
       (chat_id, title, username))


def ensure_player(chat_id, user):
    uname = user.username or ""
    fname = user.first_name or "Unknown"
    db("""
        INSERT INTO players(chat_id,user_id,first_name,username,last_active)
        VALUES(%s,%s,%s,%s,%s)
        ON CONFLICT(chat_id,user_id) DO UPDATE 
          SET first_name = EXCLUDED.first_name,
              username   = EXCLUDED.username,
              last_active= EXCLUDED.last_active
    """, (chat_id, user.id, fname, uname, now()))


def get_lang(chat_id, uid):
    r = db("SELECT lang FROM players WHERE chat_id=%s AND user_id=%s", (chat_id, uid), fetch="one")
    if r and r[0]: return r[0]
    r = db("SELECT lang FROM groups WHERE chat_id=%s", (chat_id,), fetch="one")
    return r[0] if r and r[0] else "en"


def set_user_lang(chat_id, uid, lang):
    db("UPDATE players SET lang=%s WHERE chat_id=%s AND user_id=%s", (lang, chat_id, uid))


def medals(uid, chat_id):
    r = db("SELECT medals FROM players WHERE chat_id=%s AND user_id=%s", (chat_id, uid), fetch="one")
    return r[0] if r else 0


def add_medals(uid, chat_id, n):
    db("UPDATE players SET medals=GREATEST(0, medals + %s) WHERE chat_id=%s AND user_id=%s", (n, chat_id, uid))


def cd_left(chat_id, uid, action):
    r = db("SELECT until_ts FROM cooldowns WHERE chat_id=%s AND user_id=%s AND action=%s", (chat_id, uid, action), fetch="one")
    return max(0, (r[0]-now()) if r else 0)


def set_cd(chat_id, uid, action, seconds):
    db("INSERT INTO cooldowns(chat_id,user_id,action,until_ts) VALUES(%s,%s,%s,%s) ON CONFLICT(chat_id,user_id,action) DO UPDATE SET until_ts=EXCLUDED.until_ts",
       (chat_id, uid, action, now()+seconds))


def shield_rem(chat_id, uid):
    r = db("SELECT shield_until FROM players WHERE chat_id=%s AND user_id=%s", (chat_id, uid), fetch="one")
    return max(0, (r[0]-now()) if r else 0)


def set_shield(chat_id, uid, hours):
    db("UPDATE players SET shield_until=%s WHERE chat_id=%s AND user_id=%s", (now()+hours*3600, chat_id, uid))


def intercept_state(chat_id, uid):
    r = db("SELECT intercept_until, intercept_bonus FROM players WHERE chat_id=%s AND user_id=%s", (chat_id, uid), fetch="one")
    if not r: return (0,0)
    return (max(0, r[0]-now()), r[1])


def set_intercept(chat_id, uid, hours, bonus):
    db("UPDATE players SET intercept_until=%s, intercept_bonus=%s WHERE chat_id=%s AND user_id=%s",
       (now()+hours*3600, bonus, chat_id, uid))


# inventory helpers
def inv_get(chat_id, uid, item):
    r = db("SELECT qty FROM inventories WHERE chat_id=%s AND user_id=%s AND item=%s", (chat_id, uid, item), fetch="one")
    return r[0] if r else 0


def inv_add(chat_id, uid, item, delta):
    # فقط اضافه می‌کنیم؛ کم‌کردن با inv_consume انجام میشه
    if delta <= 0:
        # می‌تونی Exception بندازی یا فقط مقدار فعلی رو برگردونی
        r = db("SELECT qty FROM inventories WHERE chat_id=%s AND user_id=%s AND item=%s",
               (chat_id, uid, item.lower()), fetch="one")
        return r[0] if r else 0

    r = db("""
        INSERT INTO inventories(chat_id,user_id,item,qty)
        VALUES (%s,%s,%s,%s)
        ON CONFLICT(chat_id,user_id,item)
        DO UPDATE SET qty = inventories.qty + EXCLUDED.qty
        RETURNING qty
    """, (chat_id, uid, item.lower(), delta), fetch="one")
    return r[0]


def inv_consume(chat_id, uid, item, n=1):
    if n <= 0:
        return True  # یا خطا، بسته به سیاستت
    r = db("""
        UPDATE inventories
           SET qty = qty - %s
         WHERE chat_id=%s AND user_id=%s AND item=%s
           AND qty >= %s
     RETURNING qty
    """, (n, chat_id, uid, item.lower(), n), fetch="one")
    return bool(r)  # True اگر کم شد، False اگر کافی نبود


# --- keyboards ---
def lang_kb(current_lang=None):
    kb = types.InlineKeyboardMarkup()
    
    # Format buttons with checkmark for current language
    en_text = "✅ English" if current_lang == "en" else "English"
    fa_text = "✅ فارسی" if current_lang == "fa" else "فارسی"
    
    kb.row(types.InlineKeyboardButton(en_text, callback_data="lang:en"),
           types.InlineKeyboardButton(fa_text, callback_data="lang:fa"))
    return kb


def main_menu(lang="en"):
    kb = types.InlineKeyboardMarkup()
    if lang == "fa":
        kb.row(types.InlineKeyboardButton("🚀 حمله", callback_data="hint:attack"),
               types.InlineKeyboardButton("🛡️ سپر", callback_data="do:shield"))
        kb.row(types.InlineKeyboardButton("🛰️ دفاع", callback_data="do:defend"),
               types.InlineKeyboardButton("🛍️ فروشگاه ⭐️", callback_data="go:shop"))
        kb.row(types.InlineKeyboardButton("🌐 زبان", callback_data="go:lang"),
               types.InlineKeyboardButton("🏅 امتیازات", callback_data="go:scores"))
    else:
        kb.row(types.InlineKeyboardButton("🚀 Attack", callback_data="hint:attack"),
               types.InlineKeyboardButton("🛡️ Shield", callback_data="do:shield"))
        kb.row(types.InlineKeyboardButton("🛰️ Defend", callback_data="do:defend"),
               types.InlineKeyboardButton("🛍️ Shop ⭐️", callback_data="go:shop"))
        kb.row(types.InlineKeyboardButton("🌐 Language", callback_data="go:lang"),
               types.InlineKeyboardButton("🏅 Scores", callback_data="go:scores"))
    return kb


def after_attack_buttons(attacker_id, defender_id, lang="en"):
    kb = types.InlineKeyboardMarkup()
    if lang == "fa":
        kb.row(types.InlineKeyboardButton("🔁 ضد حمله", callback_data=f"counter:{attacker_id}"),
               types.InlineKeyboardButton("🛡 سپر", callback_data="do:shield"))
        kb.row(types.InlineKeyboardButton("🛰 دفاع", callback_data="do:defend"),
               types.InlineKeyboardButton("🛍 فروشگاه ⭐️", callback_data="go:shop"))
    else:
        kb.row(types.InlineKeyboardButton("🔁 Counter", callback_data=f"counter:{attacker_id}"),
               types.InlineKeyboardButton("🛡 Shield", callback_data="do:shield"))
        kb.row(types.InlineKeyboardButton("🛰 Defend", callback_data="do:defend"),
               types.InlineKeyboardButton("🛍 Shop ⭐️", callback_data="go:shop"))
    return kb


# --- commands ---
@bot.message_handler(commands=['start'])
def start(m):
    ensure_group(m.chat.id, m.chat.title or "PM", m.chat.username)
    ensure_player(m.chat.id, m.from_user)
    lang = get_lang(m.chat.id, m.from_user.id)
    bot.reply_to(m, f"{T[lang]['brand']}\n{T[lang]['welcome']}\n\n{T[lang]['humor'].format(group=m.chat.title or 'this chat')}", reply_markup=main_menu(lang))


@bot.message_handler(commands=['help'])
def help_cmd(m):
    ensure_player(m.chat.id, m.from_user)
    lang = get_lang(m.chat.id, m.from_user.id)
    bot.reply_to(m, T[lang]["help"])


@bot.message_handler(commands=['lang'])
def lang_cmd(m):
    ensure_player(m.chat.id, m.from_user)
    lang = get_lang(m.chat.id, m.from_user.id)
    bot.reply_to(m, T[lang]["lang_choose"], reply_markup=lang_kb(lang))


@bot.callback_query_handler(func=lambda c: c.data.startswith("lang:"))
def lang_cb(c):
    target = c.data.split(":")[1]
    set_user_lang(c.message.chat.id, c.from_user.id, target)
    bot.answer_callback_query(c.id, T[target]['lang_set_fa'] if target=='fa' else T[target]['lang_set_en'])


@bot.message_handler(commands=['status'])
def status_cmd(m):
    ensure_player(m.chat.id, m.from_user)
    lang = get_lang(m.chat.id, m.from_user.id)
    sh = shield_rem(m.chat.id, m.from_user.id)
    intr, bonus = intercept_state(m.chat.id, m.from_user.id)
    med = medals(m.from_user.id, m.chat.id)
    r = db("SELECT score, tg_stars FROM players WHERE chat_id=%s AND user_id=%s", (m.chat.id, m.from_user.id), fetch="one")
    score = r[0] if r else 0
    tg_stars = r[1] if r and len(r) > 1 else 0
    sh_t = f"{sh//60}m" if sh>0 else ("OFF" if lang=='en' else "خاموش")
    in_t = f"{intr//60}m (+{bonus}%)" if intr>0 else ("OFF" if lang=='en' else "خاموش")
    
    # Add TG Stars info to the status message
    stars_text = f"💎 TG Stars: <b>{tg_stars}</b>\n" if lang=='en' else f"💎 ستاره‌های تلگرام: <b>{tg_stars}</b>\n"
    
    status_message = T[lang]["status_self"].format(
        name=m.from_user.first_name, 
        medals=med, 
        score=score, 
        shield=sh_t, 
        intercept=in_t
    )
    
    # Insert stars info after the name line (before medals and score)
    status_lines = status_message.split('\n')
    status_with_stars = status_lines[0] + '\n' + stars_text + status_lines[1]
    if len(status_lines) > 2:
        for i in range(2, len(status_lines)):
            status_with_stars += '\n' + status_lines[i]
    
    bot.reply_to(m, status_with_stars + "\n\n" + T[lang]["status_hint"])


@bot.message_handler(commands=['stars'])
def stars_cmd(m):
    """Command to check TG Stars balance and show premium items in the shop"""
    ensure_player(m.chat.id, m.from_user)
    lang = get_lang(m.chat.id, m.from_user.id)
    
    # Get user's TG Stars balance
    r = db("SELECT tg_stars FROM players WHERE chat_id=%s AND user_id=%s", (m.chat.id, m.from_user.id), fetch="one")
    tg_stars = r[0] if r else 0
    
    # Create response message
    stars_msg = ""
    if lang == 'en':
        stars_msg = f"<b>💎 TG Stars Balance</b>\n\nYou have <b>{tg_stars}</b> TG Stars in your account.\n\n"
        stars_msg += "TG Stars can be used to purchase premium items in the shop.\n"
        stars_msg += "Use /shop to browse available items."
    else:
        stars_msg = f"<b>💎 موجودی ستاره‌های تلگرام</b>\n\nشما <b>{tg_stars}</b> ستاره تلگرام در حساب خود دارید.\n\n"
        stars_msg += "ستاره‌های تلگرام برای خرید آیتم‌های ویژه در فروشگاه استفاده می‌شوند.\n"
        stars_msg += "از دستور /shop برای مشاهده آیتم‌های موجود استفاده کنید."
    
    # Get premium items from the shop
    premium_items = [{'id': k, 'name_en': v['title'], 'name_fa': v['title'], 'stars_price': v['stars']} 
                     for k, v in ITEMS.items() 
                     if v.get('payment') == 'tg_stars']
    
    # Add premium items to the message if there are any
    if premium_items:
        if lang == 'en':
            stars_msg += "\n<b>Available Premium Items:</b>\n"
        else:
            stars_msg += "\n<b>آیتم‌های ویژه موجود:</b>\n"
            
        for item in premium_items:
            item_name = item['name_en'] if lang == 'en' else item['name_fa']
            stars_price = item.get('stars_price', 0)
            stars_msg += f"• {item_name} - 💎 {stars_price}\n"
    
    bot.reply_to(m, stars_msg, parse_mode="HTML")


@bot.message_handler(commands=['bonus'])
def bonus_cmd(m):
    ensure_player(m.chat.id, m.from_user)
    lang = get_lang(m.chat.id, m.from_user.id)
    left = cd_left(m.chat.id, m.from_user.id, 'daily')
    if left>0:
        bot.reply_to(m, T[lang]["bonus_wait"].format(hrs=left//3600 + 1)); return
    add_medals(m.from_user.id, m.chat.id, 60)
    set_cd(m.chat.id, m.from_user.id, 'daily', 23*3600)
    
    # Update activity score
    update_activity_score(m.chat.id, m.from_user.id, "daily_bonus")
    
    bot.reply_to(m, T[lang]["bonus_ok"].format(medals=60))


@bot.message_handler(commands=['shield'])
def shield_cmd(m):
    ensure_player(m.chat.id, m.from_user)
    lang = get_lang(m.chat.id, m.from_user.id)
    remain = shield_rem(m.chat.id, m.from_user.id)
    if remain>0:
        bot.reply_to(m, T[lang]["shield_left"].format(mins=remain//60)); return
    if medals(m.from_user.id, m.chat.id) < 40:
        bot.reply_to(m, T[lang]["not_enough_medals"]); return
    add_medals(m.from_user.id, m.chat.id, -40)
    set_shield(m.chat.id, m.from_user.id, 3)
    
    # Update activity score
    update_activity_score(m.chat.id, m.from_user.id, "shield")
    
    bot.reply_to(m, T[lang]["shield_on"].format(hours=3))


@bot.message_handler(commands=['defend'])
def defend_cmd(m):
    ensure_player(m.chat.id, m.from_user)
    lang = get_lang(m.chat.id, m.from_user.id)
    intr, bonus = intercept_state(m.chat.id, m.from_user.id)
    if intr>0:
        bot.reply_to(m, T[lang]["def_left"].format(mins=intr//60)); return
    set_intercept(m.chat.id, m.from_user.id, 12, 20)
    
    # Update activity score
    update_activity_score(m.chat.id, m.from_user.id, "defend")
    
    bot.reply_to(m, T[lang]["def_on"].format(hours=12, bonus=20))


def find_defender(m):
    if m.reply_to_message:
        u = m.reply_to_message.from_user
        if u: return u
    parts = m.text.split()
    if len(parts)>=2 and parts[1].startswith("@"):
        uname = parts[1][1:]
        r = db("SELECT user_id FROM players WHERE chat_id=%s AND username=%s", (m.chat.id, uname), fetch="one")
        if r:
            class U: pass
            u = U(); u.id = r[0]; u.first_name = "@"+uname; u.username = uname
            return u
    return None


@bot.message_handler(commands=['attack'])
def attack_cmd(m):
    ensure_player(m.chat.id, m.from_user)
    lang = get_lang(m.chat.id, m.from_user.id)
    left = cd_left(m.chat.id, m.from_user.id, 'attack')
    
    if left>0:
        bot.reply_to(m, T[lang]["cooldown"].format(m=left)); return
    
    # Show weapon selection if no defender specified
    if not m.reply_to_message and not get_args(m):
        show_weapon_selection(m, lang)
        return
    
    defender = find_defender(m)
    if not defender:
        bot.reply_to(m, T[lang]["need_reply"]); return
    if defender.id == bot.get_me().id:
        bot.reply_to(m, T[lang]["no_target_bot"]); return
    if defender.id == m.from_user.id:
        bot.reply_to(m, T[lang]["no_target_self"]); return
    ensure_player(m.chat.id, defender)
    
    # Use the process_attack function to handle the attack
    process_attack(m, "std")

def show_weapon_selection(m, lang):
    """Show a keyboard with available weapons for selection"""
    chat_id = m.chat.id
    user_id = m.from_user.id
    
    # Check what weapons the user has
    has_moab = inv_get(chat_id, user_id, "moab") > 0
    has_f22 = inv_get(chat_id, user_id, "f22") > 0
    has_nuclear = inv_get(chat_id, user_id, "nuclear") > 0
    
    # Create inline keyboard with weapon options
    keyboard = types.InlineKeyboardMarkup()
    
    # Standard missile is always available
    if lang == "fa":
        std_text = "🚀 موشک استاندارد (نامحدود)"
        moab_text = "💣 بمب سنگین مواب"
        f22_text = "✈️ جنگنده اف-۲۲ رپتور"
        nuclear_text = "☢️ کلاهک هسته‌ای"
        title = "🔫 انتخاب سلاح برای حمله"
        instruction = "برای حمله، پیام کاربر هدف را reply کنید و دکمه سلاح را انتخاب کنید"
    else:
        std_text = "🚀 Standard Missile (unlimited)"
        moab_text = "💣 MOAB Heavy Bomb"
        f22_text = "✈️ F22 Raptor"
        nuclear_text = "☢️ Nuclear Warhead"
        title = "🔫 Select Weapon for Attack"
        instruction = "Reply to target user's message and select a weapon to attack"
    
    # Add weapons to keyboard
    keyboard.add(types.InlineKeyboardButton(std_text, callback_data=f"attack_weapon:std"))
    
    # Add special weapons if available
    buttons = []
    if has_moab:
        count = inv_get(chat_id, user_id, "moab")
        buttons.append(types.InlineKeyboardButton(f"{moab_text} ({count})", callback_data=f"attack_weapon:moab"))
    if has_f22:
        count = inv_get(chat_id, user_id, "f22")
        buttons.append(types.InlineKeyboardButton(f"{f22_text} ({count})", callback_data=f"attack_weapon:f22"))
    
    # Add buttons in rows of 2
    if len(buttons) > 0:
        keyboard.row(*buttons[:2])
    
    # Add nuclear as its own row if available
    if has_nuclear:
        count = inv_get(chat_id, user_id, "nuclear")
        keyboard.add(types.InlineKeyboardButton(f"{nuclear_text} ({count})", callback_data=f"attack_weapon:nuclear"))
    
    # Send message with weapon selection
    msg = f"<b>{title}</b>\n\n{instruction}"
    bot.send_message(chat_id, msg, reply_markup=keyboard)

def process_attack(m, weapon_type="std"):
    """Process an attack with the specified weapon type"""
    ensure_player(m.chat.id, m.from_user)
    lang = get_lang(m.chat.id, m.from_user.id)
    left = cd_left(m.chat.id, m.from_user.id, 'attack')
    
    if left > 0:
        bot.reply_to(m, T[lang]["cooldown"].format(m=left))
        return
        
    # Get the defender
    defender = find_defender(m)
    
    if not defender:
        bot.reply_to(m, T[lang]["need_reply"])
        return
        
    if defender.id == bot.get_me().id:
        bot.reply_to(m, T[lang]["no_target_bot"])
        return
        
    if defender.id == m.from_user.id:
        bot.reply_to(m, T[lang]["no_target_self"])
        return
        
    ensure_player(m.chat.id, defender)

    # Block by shield
    if shield_rem(m.chat.id, defender.id) > 0:
        pct = 60
        bonus = intercept_state(m.chat.id, defender.id)[1]
        resline = T[lang]["attack_blocked"]
        hit = False
        dmg = 0
        weapon_used = "std"  # Default weapon when blocked
    else:
        intr, bonus = intercept_state(m.chat.id, defender.id)
        base = 60
        pct = max(5, min(95, base - bonus))
        
        # Determine which weapon to use based on user selection or availability
        weapon_used, weapon_bonus = select_weapon(m.chat.id, m.from_user.id, weapon_type)
        
        # Add level bonus (higher level = more damage)
        attacker_level = db("SELECT level FROM players WHERE chat_id=%s AND user_id=%s", 
                            (m.chat.id, m.from_user.id), fetch="one")
        level_bonus = (attacker_level[0] - 1) * 2 if attacker_level else 0
        
        hit = random.randint(1, 100) <= pct
        
        if hit:
            # Base damage plus weapon bonuses
            base_dmg = 15
            
            # Calculate total damage
            dmg = base_dmg + weapon_bonus + level_bonus
            
            # Get defender's current medals
            defender_medals = medals(defender.id, m.chat.id)
            
            # Calculate looting percentage based on attacker's level
            loot_percent = min(30, 10 + (attacker_level[0] * 3)) if attacker_level else 10
            
            # Calculate medals looted (percentage of damage or defender's medals)
            looted_medals = min(defender_medals, int(dmg * (loot_percent / 100)))
            
            # Apply medal changes
            add_medals(defender.id, m.chat.id, -dmg)
            add_medals(m.from_user.id, m.chat.id, looted_medals)
            
            # Update attacker's score
            score_gain = 10 + (level_bonus // 2)
            db("UPDATE players SET score=score+%s WHERE chat_id=%s AND user_id=%s", 
               (score_gain, m.chat.id, m.from_user.id))
            
            # Update activity scores
            update_activity_score(m.chat.id, m.from_user.id, "attack")
            
            # Weapon name for display
            weapon_display = get_weapon_display_name(weapon_used, lang)
            
            # Create a more dynamic hit message with weapon details
            if lang == "fa":
                resline = f"💥 اصابت مستقیم با {weapon_display}! <b>{defender.first_name}</b> {dmg} مدال از دست داد، <b>{m.from_user.first_name}</b> +{score_gain} امتیاز گرفت و {looted_medals} مدال غارت کرد!"
            else:
                resline = f"💥 DIRECT HIT with {weapon_display}! <b>{defender.first_name}</b> loses {dmg} medals, <b>{m.from_user.first_name}</b> gains +{score_gain} score and looted {looted_medals} medals!"
        else:
            dmg = 0
            looted_medals = 0
            
            # Create a more interesting miss message
            miss_messages_en = [
                "🤏 Missed by inches!",
                "💨 The missile flew right past the target!",
                "🌪️ Wind conditions affected the trajectory!",
                "⚠️ Missile guidance system failed!",
                "🔋 Energy systems malfunctioned mid-flight!"
            ]
            
            miss_messages_fa = [
                "🤏 موشک از کنار هدف گذشت!",
                "💨 موشک درست از بغل هدف عبور کرد!",
                "🌪️ شرایط باد مسیر موشک را تغییر داد!",
                "⚠️ سیستم هدایت موشک خراب شد!",
                "🔋 سیستم انرژی موشک در میانه پرواز از کار افتاد!"
            ]
            
            # Choose a random miss message based on language
            if lang == "fa":
                resline = random.choice(miss_messages_fa)
            else:
                resline = random.choice(miss_messages_en)
    
    # Record the attack in database
    db("INSERT INTO attacks(chat_id,attacker_id,defender_id,weapon,ts,hit,dmg) VALUES(%s,%s,%s,%s,%s,%s,%s)",
       (m.chat.id, m.from_user.id, defender.id, weapon_used, now(), hit, dmg))
    set_cd(m.chat.id, m.from_user.id, 'attack', 10)
    
    # Create a more visually appealing attack message
    weapon_emoji = get_weapon_emoji(weapon_used)
    
    if lang == "fa":
        attack_header = f"{weapon_emoji} <b>{m.from_user.first_name}</b> به <b>{defender.first_name}</b> حمله کرد"
        attack_details = f"🎯 احتمال اصابت: {pct}% | 🛰️ رهگیری: +{bonus}%"
    else:
        attack_header = f"{weapon_emoji} <b>{m.from_user.first_name}</b> attacked <b>{defender.first_name}</b>"
        attack_details = f"🎯 Hit chance: {pct}% | 🛰️ Intercept: +{bonus}%"
    
    attack_msg = f"{attack_header}\n{attack_details}\n{resline}"
    
    bot.reply_to(m, attack_msg, reply_markup=after_attack_buttons(m.from_user.id, defender.id, lang))

def select_weapon(chat_id, user_id, requested_weapon="std"):
    """Select and consume a weapon based on user request and availability"""
    # Check if the requested special weapon is available
    if requested_weapon != "std" and inv_get(chat_id, user_id, requested_weapon) > 0:
        # User has requested a specific weapon they own
        inv_consume(chat_id, user_id, requested_weapon, 1)
        return requested_weapon, ITEMS[requested_weapon]["dmg"]
    
    # If requested weapon not available or just using standard, check for any special weapons
    for weapon in ["nuclear", "moab", "f22"]:  # Check in order of power
        if inv_get(chat_id, user_id, weapon) > 0:
            inv_consume(chat_id, user_id, weapon, 1)
            return weapon, ITEMS[weapon]["dmg"]
    
    # No special weapons available, use standard missile
    return "std", 0

def get_weapon_emoji(weapon_type):
    """Get the appropriate emoji for the weapon type"""
    weapon_emojis = {
        "std": "🚀",      # Standard missile
        "moab": "💣",     # MOAB Heavy Bomb
        "f22": "✈️",      # F22 Raptor
        "nuclear": "☢️",  # Nuclear warhead
    }
    return weapon_emojis.get(weapon_type, "🚀")  # Default to missile if unknown

def get_weapon_display_name(weapon_type, lang):
    """Get a display name for the weapon type based on language"""
    if lang == "en":
        weapon_names = {
            "std": "Standard Missile",
            "moab": "MOAB Heavy Bomb",
            "f22": "F22 Raptor",
            "nuclear": "Nuclear Warhead",
        }
    else:  # Persian
        weapon_names = {
            "std": "موشک استاندارد",
            "moab": "بمب سنگین مواب",
            "f22": "جنگنده اف-۲۲ رپتور",
            "nuclear": "کلاهک هسته‌ای",
        }
    return weapon_names.get(weapon_type, weapon_names["std"])

def after_attack_buttons(attacker_id, defender_id, lang):
    """Create buttons for after attack actions"""
    keyboard = types.InlineKeyboardMarkup()
    
    if lang == "fa":
        rematch_text = "🔄 حمله مجدد"
        stats_text = "📊 آمار"
    else:
        rematch_text = "🔄 Attack Again"
        stats_text = "📊 Stats"
        
    # Add rematch button (will only work after cooldown)
    keyboard.add(
        types.InlineKeyboardButton(rematch_text, callback_data=f"rematch:{defender_id}"),
        types.InlineKeyboardButton(stats_text, callback_data=f"stats:{defender_id}")
    )
    
    return keyboard


@bot.message_handler(commands=['shop'])
def shop_cmd(m):
    ensure_player(m.chat.id, m.from_user)
    lang = get_lang(m.chat.id, m.from_user.id)
    
    # Check if this is a private chat - shop should only work in groups
    if m.chat.type == 'private':
        if lang == "fa":
            bot.reply_to(m, "⚠️ فروشگاه فقط در گروه‌ها قابل استفاده است. لطفاً این دستور را در یک گروه ارسال کنید.")
        else:
            bot.reply_to(m, "⚠️ The shop is only available in groups. Please use this command in a group.")
        return
    
    # Create two sections for the shop: medals and TG stars
    kb = types.InlineKeyboardMarkup()
    
    # Add header for medal items
    if lang == "fa":
        kb.add(types.InlineKeyboardButton("🏅 آیتم‌های قابل خرید با مدال", callback_data="shop_info:medals"))
    else:
        kb.add(types.InlineKeyboardButton("🏅 Items purchasable with Medals", callback_data="shop_info:medals"))
    
    # Add medal items
    medal_items = [k for k, v in ITEMS.items() if v.get('payment') == 'medals']
    for k in medal_items:
        v = ITEMS[k]
        stars_display = "⭐" * v['stars']
        price_display = f"🏅 {v['stars'] * 100}"
        if lang == "fa":
            kb.add(types.InlineKeyboardButton(f"{stars_display} {v['title']} - {price_display}", callback_data=f"buy:{k}"))
        else:
            kb.add(types.InlineKeyboardButton(f"{stars_display} {v['title']} - {price_display}", callback_data=f"buy:{k}"))
    
    # Add a spacer
    if lang == "fa":
        kb.add(types.InlineKeyboardButton("━━━━━━━━━━━━━━━━", callback_data="shop_info:spacer"))
    else:
        kb.add(types.InlineKeyboardButton("━━━━━━━━━━━━━━━━", callback_data="shop_info:spacer"))
    
    # Add header for TG stars items
    if lang == "fa":
        kb.add(types.InlineKeyboardButton("✨ آیتم‌های ویژه با ستاره تلگرام", callback_data="shop_info:tg_stars"))
    else:
        kb.add(types.InlineKeyboardButton("✨ Premium items with Telegram Stars", callback_data="shop_info:tg_stars"))
    
    # Add TG stars items
    tg_items = [k for k, v in ITEMS.items() if v.get('payment') == 'tg_stars']
    for k in tg_items:
        v = ITEMS[k]
        stars_display = "⭐" * v['stars']
        price_display = f"✨ {v['stars']}"
        if lang == "fa":
            kb.add(types.InlineKeyboardButton(f"{stars_display} {v['title']} - {price_display}", callback_data=f"buy_tg:{k}"))
        else:
            kb.add(types.InlineKeyboardButton(f"{stars_display} {v['title']} - {price_display}", callback_data=f"buy_tg:{k}"))
    
    # Add a close button
    if lang == "fa":
        kb.add(types.InlineKeyboardButton("❌ بستن", callback_data="shop_close"))
    else:
        kb.add(types.InlineKeyboardButton("❌ Close", callback_data="shop_close"))
    
    # Send the shop message
    if lang == "fa":
        shop_message = (
            "🛍️ <b>فروشگاه تجهیزات نظامی</b>\n\n"
            "برای خرید آیتم مورد نظر روی آن کلیک کنید.\n"
            "🏅 قیمت آیتم‌ها با مدال: هر ستاره = 100 مدال\n"
            "✨ قیمت آیتم‌های ویژه با ستاره تلگرام"
        )
    else:
        shop_message = (
            "🛍️ <b>Military Equipment Shop</b>\n\n"
            "Click on an item to purchase it.\n"
            "🏅 Medal items: Each star = 100 medals\n"
            "✨ Premium items: Require Telegram Stars"
        )
    
    bot.reply_to(m, shop_message, reply_markup=kb)


@bot.callback_query_handler(func=lambda c: c.data.startswith("buy:"))
def buy_cb(c):
    key = c.data.split(":")[1]
    item = ITEMS[key]
    lang = get_lang(c.message.chat.id, c.from_user.id)
    
    # Check if user has enough medals
    required_medals = item["stars"] * 100  # Each star equals 100 medals
    user_medals = medals(c.from_user.id, c.message.chat.id)
    
    if user_medals < required_medals:
        if lang == "fa":
            bot.answer_callback_query(c.id, f"مدال‌های کافی نداری! نیاز: {required_medals} | موجودی: {user_medals}", show_alert=True)
        else:
            bot.answer_callback_query(c.id, f"Not enough medals! Required: {required_medals} | You have: {user_medals}", show_alert=True)
        return
    
    # Process the purchase
    add_medals(c.from_user.id, c.message.chat.id, -required_medals)
    
    # Update player with purchased item
    if key == "aegis":
        set_shield(c.message.chat.id, c.from_user.id, ITEMS[key]["hours"])
    elif key == "patriot":
        set_intercept(c.message.chat.id, c.from_user.id, ITEMS[key]["hours"], ITEMS[key]["bonus"])
    elif key == "moab" or key == "f22" or key == "nuclear":
        inv_add(c.message.chat.id, c.from_user.id, key, 1)
    elif key == "carrier":
        inv_add(c.message.chat.id, c.from_user.id, key, 1)
        
    # Record the purchase
    db("INSERT INTO purchases(chat_id,user_id,item,stars,ts,payload,payment_type) VALUES(%s,%s,%s,%s,%s,%s,%s)",
       (c.message.chat.id, c.from_user.id, key, item["stars"], now(), f"medals:{key}:{c.from_user.id}:{c.message.chat.id}:{now()}", "medals"))
    
    bot.answer_callback_query(c.id, T[lang]["buy_done"].format(item=ITEMS[key]["title"]))
    
    # Update the message to show purchase completed
    stars_display = "⭐" * item['stars']
    if lang == "fa":
        bot.send_message(c.message.chat.id, f"✅ خرید انجام شد: {stars_display} {item['title']}")
    else:
        bot.send_message(c.message.chat.id, f"✅ Purchase completed: {stars_display} {item['title']}")


@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_tg:"))
def buy_tg_cb(c):
    key = c.data.split(":")[1]
    item = ITEMS[key]
    lang = get_lang(c.message.chat.id, c.from_user.id)
    
    # Get current TG stars balance
    r = db("SELECT tg_stars FROM players WHERE chat_id=%s AND user_id=%s", (c.message.chat.id, c.from_user.id), fetch="one")
    user_tg_stars = r[0] if r else 0
    
    # Check if user has enough TG stars
    required_stars = item["stars"]
    
    if user_tg_stars < required_stars:
        # Create an invoice for the TG stars purchase
        if lang == "fa":
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton("💫 خرید ستاره تلگرام", callback_data=f"tg_stars_purchase:{key}"))
            bot.answer_callback_query(c.id, f"ستاره‌های تلگرام کافی نداری! نیاز: {required_stars} | موجودی: {user_tg_stars}")
            bot.send_message(c.message.chat.id, f"⚠️ برای خرید {item['title']} به {required_stars} ستاره تلگرام نیاز دارید. برای خرید ستاره تلگرام روی دکمه زیر کلیک کنید:", reply_markup=kb)
        else:
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton("💫 Buy Telegram Stars", callback_data=f"tg_stars_purchase:{key}"))
            bot.answer_callback_query(c.id, f"Not enough Telegram Stars! Required: {required_stars} | You have: {user_tg_stars}")
            bot.send_message(c.message.chat.id, f"⚠️ You need {required_stars} Telegram Stars to purchase {item['title']}. Click the button below to buy Telegram Stars:", reply_markup=kb)
        return
    
    # Process the purchase
    db("UPDATE players SET tg_stars = tg_stars - %s WHERE chat_id=%s AND user_id=%s", 
       (required_stars, c.message.chat.id, c.from_user.id))
    
    # Update player with purchased item
    if key == "super_aegis":
        set_shield(c.message.chat.id, c.from_user.id, ITEMS[key]["hours"])
    elif key == "mega_nuke" or key == "stealth_bomber":
        inv_add(c.message.chat.id, c.from_user.id, key, 1)
    elif key == "medal_boost":
        add_medals(c.from_user.id, c.message.chat.id, ITEMS[key]["medals"])
    elif key == "vip_status":
        # Set VIP status for 30 days
        vip_until = now() + (ITEMS[key]["days"] * 24 * 3600)
        #UNCOMPLETED
        
    # Record the purchase
    db("INSERT INTO purchases(chat_id,user_id,item,stars,ts,payload,payment_type) VALUES(%s,%s,%s,%s,%s,%s,%s)",
       (c.message.chat.id, c.from_user.id, key, item["stars"], now(), 
        f"tg_stars:{key}:{c.from_user.id}:{c.message.chat.id}:{now()}", "tg_stars"))
    
    if lang == "fa":
        bot.answer_callback_query(c.id, f"✅ خرید آیتم {item['title']} با {required_stars} ستاره تلگرام انجام شد!")
        bot.send_message(c.message.chat.id, f"✨ <b>خرید ویژه انجام شد</b>\n\n🛍️ آیتم: {item['title']}\n💰 قیمت: {required_stars} ستاره تلگرام")
    else:
        bot.answer_callback_query(c.id, f"✅ Successfully purchased {item['title']} for {required_stars} Telegram Stars!")
        bot.send_message(c.message.chat.id, f"✨ <b>Premium Purchase Complete</b>\n\n🛍️ Item: {item['title']}\n💰 Price: {required_stars} Telegram Stars")


@bot.callback_query_handler(func=lambda c: c.data.startswith("tg_stars_purchase:"))
def tg_stars_purchase_cb(c):
    item_key = c.data.split(":")[1] if ":" in c.data else None
    lang = get_lang(c.message.chat.id, c.from_user.id)
    
    # This would integrate with Telegram's payment system in a real implementation
    # For now, we'll simulate the purchase by directly adding stars
    
    if lang == "fa":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("⭐ 1 ستاره - 100 تومان", callback_data=f"add_stars:1:{item_key}"))
        kb.add(types.InlineKeyboardButton("⭐⭐ 2 ستاره - 180 تومان", callback_data=f"add_stars:2:{item_key}"))
        kb.add(types.InlineKeyboardButton("⭐⭐⭐ 5 ستاره - 400 تومان", callback_data=f"add_stars:5:{item_key}"))
        kb.add(types.InlineKeyboardButton("⭐⭐⭐⭐ 10 ستاره - 750 تومان", callback_data=f"add_stars:10:{item_key}"))
        bot.send_message(c.message.chat.id, "💫 <b>خرید ستاره تلگرام</b>\n\nلطفاً تعداد ستاره مورد نظر را انتخاب کنید:", reply_markup=kb)
    else:
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("⭐ 1 Star - $1", callback_data=f"add_stars:1:{item_key}"))
        kb.add(types.InlineKeyboardButton("⭐⭐ 2 Stars - $1.8", callback_data=f"add_stars:2:{item_key}"))
        kb.add(types.InlineKeyboardButton("⭐⭐⭐ 5 Stars - $4", callback_data=f"add_stars:5:{item_key}"))
        kb.add(types.InlineKeyboardButton("⭐⭐⭐⭐ 10 Stars - $7.5", callback_data=f"add_stars:10:{item_key}"))
        bot.send_message(c.message.chat.id, "💫 <b>Buy Telegram Stars</b>\n\nPlease select the number of stars:", reply_markup=kb)
    
    bot.answer_callback_query(c.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("add_stars:"))
def add_stars_cb(c):
    parts = c.data.split(":")
    num_stars = int(parts[1])
    item_key = parts[2] if len(parts) > 2 and parts[2] else None
    lang = get_lang(c.message.chat.id, c.from_user.id)
    
    # In a real implementation, this would process the payment through Telegram
    # For now, we'll simulate it
    
    # Add stars to the user's account
    db("UPDATE players SET tg_stars = tg_stars + %s WHERE chat_id=%s AND user_id=%s", 
       (num_stars, c.message.chat.id, c.from_user.id))
    
    if lang == "fa":
        msg = f"✅ <b>{num_stars} ستاره تلگرام</b> به حساب شما اضافه شد!"
        if item_key and item_key != "none":
            msg += f"\n\nاکنون می‌توانید آیتم <b>{ITEMS[item_key]['title']}</b> را خریداری کنید."
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton(f"🛍️ خرید {ITEMS[item_key]['title']}", callback_data=f"buy_tg:{item_key}"))
            bot.send_message(c.message.chat.id, msg, reply_markup=kb)
        else:
            bot.send_message(c.message.chat.id, msg)
    else:
        msg = f"✅ <b>{num_stars} Telegram Stars</b> have been added to your account!"
        if item_key and item_key != "none":
            msg += f"\n\nYou can now purchase the <b>{ITEMS[item_key]['title']}</b>."
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton(f"🛍️ Buy {ITEMS[item_key]['title']}", callback_data=f"buy_tg:{item_key}"))
            bot.send_message(c.message.chat.id, msg, reply_markup=kb)
        else:
            bot.send_message(c.message.chat.id, msg)
    
    bot.answer_callback_query(c.id, "✅ Stars added successfully!")


@bot.callback_query_handler(func=lambda c: c.data.startswith("shop_info:") or c.data == "shop_close")
def shop_info_cb(c):
    if c.data == "shop_close":
        try:
            bot.delete_message(c.message.chat.id, c.message.message_id)
        except:
            pass
        bot.answer_callback_query(c.id)
        return
        
    info_type = c.data.split(":")[1]
    lang = get_lang(c.message.chat.id, c.from_user.id)
    
    if info_type == "medals":
        if lang == "fa":
            bot.answer_callback_query(c.id, "🏅 آیتم‌های قابل خرید با مدال - هر ستاره = 100 مدال")
        else:
            bot.answer_callback_query(c.id, "🏅 Items purchasable with Medals - Each star = 100 medals")
    elif info_type == "tg_stars":
        if lang == "fa":
            bot.answer_callback_query(c.id, "✨ آیتم‌های ویژه با ستاره تلگرام - آیتم‌های قدرتمندتر با امکانات ویژه")
        else:
            bot.answer_callback_query(c.id, "✨ Premium items with Telegram Stars - More powerful items with special features")
    else:
        bot.answer_callback_query(c.id)


# --- Quiz System ---
def create_quiz(chat_id):
    # List of quiz questions (can be expanded)
    quizzes = [
        {
            "question": "Who was the 45th president of the United States?",
            "correct": "Donald Trump",
            "options": ["Barack Obama", "Donald Trump", "Joe Biden", "George Bush"]
        },
        {
            "question": "What is Trump's famous slogan?",
            "correct": "Make America Great Again",
            "options": ["Yes We Can", "Make America Great Again", "America First", "Build Back Better"]
        },
        {
            "question": "What year was Donald Trump elected president?",
            "correct": "2016",
            "options": ["2012", "2016", "2020", "2008"]
        },
        {
            "question": "What is the name of Trump's company?",
            "correct": "The Trump Organization",
            "options": ["Trump Inc.", "The Trump Organization", "Trump Enterprises", "Trump Holdings"]
        },
        {
            "question": "What social media platform did Trump create?",
            "correct": "Truth Social",
            "options": ["Parler", "Gettr", "Truth Social", "Rumble"]
        }
    ]
    
    # Persian quizzes
    fa_quizzes = [
        {
            "question": "چه کسی چهل و پنجمین رئیس جمهور آمریکا بود؟",
            "correct": "دونالد ترامپ",
            "options": ["باراک اوباما", "دونالد ترامپ", "جو بایدن", "جورج بوش"]
        },
        {
            "question": "شعار معروف ترامپ چیست؟",
            "correct": "آمریکا را دوباره عالی کنیم",
            "options": ["بله ما می‌توانیم", "آمریکا را دوباره عالی کنیم", "آمریکا اول", "بازسازی بهتر"]
        },
        {
            "question": "ترامپ در چه سالی به ریاست جمهوری انتخاب شد؟",
            "correct": "2016",
            "options": ["2012", "2016", "2020", "2008"]
        },
        {
            "question": "نام شرکت ترامپ چیست؟",
            "correct": "سازمان ترامپ",
            "options": ["ترامپ اینک", "سازمان ترامپ", "شرکت‌های ترامپ", "هلدینگ ترامپ"]
        },
        {
            "question": "ترامپ چه پلتفرم رسانه اجتماعی را ایجاد کرد؟",
            "correct": "تروث سوشال",
            "options": ["پارلر", "گتر", "تروث سوشال", "رامبل"]
        }
    ]
    
    # Get group language
    r = db("SELECT lang FROM groups WHERE chat_id=%s", (chat_id,), fetch="one")
    lang = r[0] if r and r[0] else "en"
    
    # Select a random quiz based on language
    if lang == "fa":
        quiz = random.choice(fa_quizzes)
    else:
        quiz = random.choice(quizzes)
    
    # Insert the quiz into the database
    db("""
        INSERT INTO quizzes(chat_id, question, correct_answer, options, created_at, solved_by, solved_at)
        VALUES(%s, %s, %s, %s, %s, NULL, NULL)
        RETURNING id
    """, (chat_id, quiz["question"], quiz["correct"], quiz["options"], now()), fetch="one")
    
    return quiz

@bot.message_handler(commands=['quiz'])
def quiz_cmd(m):
    ensure_player(m.chat.id, m.from_user)
    lang = get_lang(m.chat.id, m.from_user.id)
    
    # Check if there's an active unsolved quiz
    r = db("SELECT id, question, options FROM quizzes WHERE chat_id=%s AND solved_by IS NULL ORDER BY created_at DESC LIMIT 1",
           (m.chat.id,), fetch="one")
           
    if r:
        # There's an active quiz, show it again
        quiz_id, question, options = r
        
        # Create inline keyboard with options
        kb = types.InlineKeyboardMarkup()
        for option in options:
            kb.add(types.InlineKeyboardButton(option, callback_data=f"quiz:{quiz_id}:{option}"))
        
        # Send the quiz
        if lang == "fa":
            bot.reply_to(m, f"🧠 <b>کوییز!</b>\n\n{question}\n\nاولین کسی باشید که پاسخ صحیح می‌دهد!", reply_markup=kb)
        else:
            bot.reply_to(m, f"🧠 <b>Quiz Time!</b>\n\n{question}\n\nBe the first to answer correctly!", reply_markup=kb)
    else:
        # Create a new quiz
        quiz = create_quiz(m.chat.id)
        
        # Get the quiz ID
        r = db("SELECT id FROM quizzes WHERE chat_id=%s AND solved_by IS NULL ORDER BY created_at DESC LIMIT 1",
               (m.chat.id,), fetch="one")
        quiz_id = r[0] if r else 0
        
        # Create inline keyboard with options
        kb = types.InlineKeyboardMarkup()
        for option in quiz["options"]:
            kb.add(types.InlineKeyboardButton(option, callback_data=f"quiz:{quiz_id}:{option}"))
        
        # Send the quiz
        if lang == "fa":
            bot.reply_to(m, f"🧠 <b>کوییز جدید!</b>\n\n{quiz['question']}\n\nاولین کسی باشید که پاسخ صحیح می‌دهد!", reply_markup=kb)
        else:
            bot.reply_to(m, f"🧠 <b>New Quiz!</b>\n\n{quiz['question']}\n\nBe the first to answer correctly!", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("quiz:"))
def quiz_cb(c):
    _, quiz_id, answer = c.data.split(":", 2)
    quiz_id = int(quiz_id)
    lang = get_lang(c.message.chat.id, c.from_user.id)
    
    # Check if the quiz has been solved
    r = db("SELECT solved_by, correct_answer FROM quizzes WHERE id=%s", (quiz_id,), fetch="one")
    if not r:
        bot.answer_callback_query(c.id, "Quiz not found.")
        return
    
    solved_by, correct_answer = r
    
    if solved_by is not None:
        # Quiz already solved
        if lang == "fa":
            bot.answer_callback_query(c.id, "کوییز قبلاً حل شده است!")
        else:
            bot.answer_callback_query(c.id, "This quiz has already been solved!")
        return
    
    # Check if the answer is correct
    if answer == correct_answer:
        # Update the quiz as solved
        db("UPDATE quizzes SET solved_by=%s, solved_at=%s WHERE id=%s",
           (c.from_user.id, now(), quiz_id))
        
        # Award medals and activity score
        add_medals(c.from_user.id, c.message.chat.id, 25)
        update_activity_score(c.message.chat.id, c.from_user.id, "quiz_correct")
        
        # Notify user
        if lang == "fa":
            bot.answer_callback_query(c.id, "🎉 صحیح! شما 25 مدال و 10 امتیاز فعالیت دریافت کردید!")
            bot.edit_message_text(f"🧠 <b>کوییز</b>\n\n{c.message.text.split('\n\n')[1]}\n\n✅ <b>{c.from_user.first_name}</b> پاسخ درست داد: <b>{correct_answer}</b>\n\n🏅 جایزه: 25 مدال + 10 امتیاز", 
                                  chat_id=c.message.chat.id, message_id=c.message.message_id, parse_mode="HTML")
        else:
            bot.answer_callback_query(c.id, "🎉 Correct! You earned 25 medals and 10 activity points!")
            bot.edit_message_text(f"🧠 <b>Quiz</b>\n\n{c.message.text.split('\n\n')[1]}\n\n✅ <b>{c.from_user.first_name}</b> answered correctly: <b>{correct_answer}</b>\n\n🏅 Reward: 25 medals + 10 points", 
                                  chat_id=c.message.chat.id, message_id=c.message.message_id, parse_mode="HTML")
    else:
        # Wrong answer
        if lang == "fa":
            bot.answer_callback_query(c.id, "❌ نادرست! دوباره تلاش کنید.")
        else:
            bot.answer_callback_query(c.id, "❌ Wrong! Try again.")

@bot.message_handler(commands=['score', 'level'])
def score_cmd(m):
    ensure_player(m.chat.id, m.from_user)
    lang = get_lang(m.chat.id, m.from_user.id)
    
    # Get the user's level info
    level_info = get_player_level_info(m.chat.id, m.from_user.id)
    
    # Generate progress bar (10 characters)
    progress_bar_length = 10
    filled_length = int(level_info["progress"] / 100 * progress_bar_length)
    progress_bar = "■" * filled_length + "□" * (progress_bar_length - filled_length)
    
    # Generate rank title based on level
    if lang == "fa":
        ranks = ["سرباز", "ستوان", "سروان", "سرگرد", "سرهنگ", "ژنرال", "فرمانده کل", "رئیس جمهور"]
    else:
        ranks = ["Private", "Lieutenant", "Captain", "Major", "Colonel", "General", "Commander", "President"]
    
    rank_index = min(level_info["level"] - 1, len(ranks) - 1)
    rank_title = ranks[rank_index]
    
    # Format the message
    if lang == "fa":
        message = (
            f"🏅 <b>امتیازات {m.from_user.first_name}</b>\n\n"
            f"🎖 سطح: <b>{level_info['level']}</b> ({rank_title})\n"
            f"📊 امتیاز: <b>{level_info['score']}</b> / {level_info['next_level_score']}\n"
            f"📈 پیشرفت: {progress_bar} {level_info['progress']:.1f}%\n\n"
            f"💡 با فعالیت در گروه امتیاز و سطح خود را افزایش دهید!"
        )
    else:
        message = (
            f"🏅 <b>{m.from_user.first_name}'s Status</b>\n\n"
            f"🎖 Level: <b>{level_info['level']}</b> ({rank_title})\n"
            f"📊 Score: <b>{level_info['score']}</b> / {level_info['next_level_score']}\n"
            f"📈 Progress: {progress_bar} {level_info['progress']:.1f}%\n\n"
            f"💡 Increase your activity in the group to level up!"
        )
    
    bot.reply_to(m, message)


@bot.message_handler(commands=['inventory', 'inv'])
def inventory_cmd(m):
    ensure_player(m.chat.id, m.from_user)
    lang = get_lang(m.chat.id, m.from_user.id)
    
    # Get inventory items
    rows = db("SELECT item, qty FROM inventories WHERE chat_id=%s AND user_id=%s ORDER BY item", 
              (m.chat.id, m.from_user.id), fetch="all")
    
    # Get player level info for better display
    level_info = get_player_level_info(m.chat.id, m.from_user.id)
    
    # Create a visual inventory display
    if not rows:
        if lang == "fa":
            msg = f"🎒 <b>انبار {m.from_user.first_name}</b>\n\n"
            msg += "❌ انبار شما خالی است!\n"
            msg += f"\n💡 از فروشگاه با دستور /shop آیتم بخرید"
        else:
            msg = f"🎒 <b>{m.from_user.first_name}'s Inventory</b>\n\n"
            msg += "❌ Your inventory is empty!\n"
            msg += f"\n💡 Buy items from the shop with /shop command"
    else:
        # Group items by category
        weapons = []
        premium_weapons = []
        consumables = []
        premium_consumables = []
        other = []
        premium_other = []
        
        # Sort items into categories
        for item, qty in rows:
            # Check if this is a premium item
            is_premium = item in ["super_aegis", "mega_nuke", "stealth_bomber", "medal_boost", "vip_status"]
            
            if item in ["moab", "f22", "nuclear", "mega_nuke", "stealth_bomber"]:
                if is_premium:
                    premium_weapons.append((item, qty))
                else:
                    weapons.append((item, qty))
            elif item in ["shield", "intercept", "super_aegis"]:
                if is_premium:
                    premium_consumables.append((item, qty))
                else:
                    consumables.append((item, qty))
            else:
                if is_premium:
                    premium_other.append((item, qty))
                else:
                    other.append((item, qty))
                
        # Create the message
        if lang == "fa":
            msg = f"🎒 <b>انبار {m.from_user.first_name}</b> (سطح {level_info['level']})\n\n"
            
            # Add premium section header if player has premium items
            if premium_weapons or premium_consumables or premium_other:
                msg += "💎 <b>آیتم‌های ویژه:</b>\n\n"
                
                # Add premium weapons
                if premium_weapons:
                    msg += "🔫 <b>سلاح‌های ویژه:</b>\n"
                    for item, qty in premium_weapons:
                        item_name = get_weapon_display_name(item, lang)
                        item_emoji = get_weapon_emoji(item)
                        msg += f"• {item_emoji} {item_name}: <b>×{qty}</b>\n"
                    msg += "\n"
                
                # Add premium consumables
                if premium_consumables:
                    msg += "🛡️ <b>آیتم‌های مصرفی ویژه:</b>\n"
                    for item, qty in premium_consumables:
                        if item == "super_aegis":
                            msg += f"• 🛡️ سپر دفاعی فوق پیشرفته: <b>×{qty}</b>\n"
                    msg += "\n"
                
                # Add premium other items
                if premium_other:
                    msg += "📦 <b>سایر آیتم‌های ویژه:</b>\n"
                    for item, qty in premium_other:
                        if item == "medal_boost":
                            msg += f"• 🏅 افزایش مدال: <b>×{qty}</b>\n"
                        elif item == "vip_status":
                            msg += f"• 👑 وضعیت VIP: <b>×{qty}</b>\n"
                        else:
                            msg += f"• {item}: <b>×{qty}</b>\n"
                    msg += "\n"
                
                msg += "🔹 <b>آیتم‌های عادی:</b>\n\n"
            
            # Add weapons section
            if weapons:
                msg += "🔫 <b>سلاح‌ها:</b>\n"
                for item, qty in weapons:
                    item_name = get_weapon_display_name(item, lang)
                    item_emoji = get_weapon_emoji(item)
                    msg += f"• {item_emoji} {item_name}: <b>×{qty}</b>\n"
                msg += "\n"
                
            # Add consumables section
            if consumables:
                msg += "🛡️ <b>آیتم‌های مصرفی:</b>\n"
                for item, qty in consumables:
                    if item == "shield":
                        msg += f"• 🛡️ سپر دفاعی: <b>×{qty}</b>\n"
                    elif item == "intercept":
                        msg += f"• 🛰️ سیستم رهگیری: <b>×{qty}</b>\n"
                msg += "\n"
                
            # Add other items section
            if other:
                msg += "📦 <b>سایر آیتم‌ها:</b>\n"
                for item, qty in other:
                    msg += f"• {item}: <b>×{qty}</b>\n"
            
            # Add helpful tip
            msg += f"\n💡 برای استفاده از سلاح‌ها، دستور /attack را استفاده کنید"
        else:
            msg = f"🎒 <b>{m.from_user.first_name}'s Inventory</b> (Level {level_info['level']})\n\n"
            
            # Add premium section header if player has premium items
            if premium_weapons or premium_consumables or premium_other:
                msg += "💎 <b>Premium Items:</b>\n\n"
                
                # Add premium weapons
                if premium_weapons:
                    msg += "🔫 <b>Premium Weapons:</b>\n"
                    for item, qty in premium_weapons:
                        item_name = get_weapon_display_name(item, lang)
                        item_emoji = get_weapon_emoji(item)
                        msg += f"• {item_emoji} {item_name}: <b>×{qty}</b>\n"
                    msg += "\n"
                
                # Add premium consumables
                if premium_consumables:
                    msg += "🛡️ <b>Premium Consumables:</b>\n"
                    for item, qty in premium_consumables:
                        if item == "super_aegis":
                            msg += f"• 🛡️ Super Aegis Shield: <b>×{qty}</b>\n"
                    msg += "\n"
                
                # Add premium other items
                if premium_other:
                    msg += "📦 <b>Other Premium Items:</b>\n"
                    for item, qty in premium_other:
                        if item == "medal_boost":
                            msg += f"• 🏅 Medal Boost: <b>×{qty}</b>\n"
                        elif item == "vip_status":
                            msg += f"• 👑 VIP Status: <b>×{qty}</b>\n"
                        else:
                            msg += f"• {item}: <b>×{qty}</b>\n"
                    msg += "\n"
                
                msg += "🔹 <b>Regular Items:</b>\n\n"
            
            # Add weapons section
            if weapons:
                msg += "🔫 <b>Weapons:</b>\n"
                for item, qty in weapons:
                    item_name = get_weapon_display_name(item, lang)
                    item_emoji = get_weapon_emoji(item)
                    msg += f"• {item_emoji} {item_name}: <b>×{qty}</b>\n"
                msg += "\n"
                
            # Add consumables section
            if consumables:
                msg += "🛡️ <b>Consumables:</b>\n"
                for item, qty in consumables:
                    if item == "shield":
                        msg += f"• 🛡️ Defense Shield: <b>×{qty}</b>\n"
                    elif item == "intercept":
                        msg += f"• 🛰️ Intercept System: <b>×{qty}</b>\n"
                msg += "\n"
                
            # Add other items section
            if other:
                msg += "📦 <b>Other Items:</b>\n"
                for item, qty in other:
                    msg += f"• {item}: <b>×{qty}</b>\n"
            
            # Add helpful tip
            msg += f"\n💡 Use /attack command to use your weapons"
    
    # Create keyboard with attack, shop, and stars buttons
    keyboard = types.InlineKeyboardMarkup()
    if lang == "fa":
        attack_text = "🔫 حمله"
        shop_text = "🛒 فروشگاه"
        stars_text = "💎 ستاره‌ها"
    else:
        attack_text = "🔫 Attack"
        shop_text = "🛒 Shop"
        stars_text = "💎 Stars"
    keyboard.add(
        types.InlineKeyboardButton(attack_text, callback_data=f"do:attack"),
        types.InlineKeyboardButton(shop_text, callback_data=f"go:shop")
    )
    keyboard.add(
        types.InlineKeyboardButton(stars_text, callback_data=f"go:stars")
    )
    
    # Send the inventory message
    bot.reply_to(m, msg, reply_markup=keyboard, parse_mode="HTML")

# Helper functions (make sure they're defined elsewhere or include them here)
def get_weapon_emoji(weapon_type):
    """Get the appropriate emoji for the weapon type"""
    weapon_emojis = {
        "std": "🚀",      # Standard missile
        "moab": "💣",     # MOAB Heavy Bomb
        "f22": "✈️",      # F22 Raptor
        "nuclear": "☢️",  # Nuclear warhead
    }
    return weapon_emojis.get(weapon_type, "🚀")  # Default to missile if unknown

def get_weapon_display_name(weapon_type, lang):
    """Get a display name for the weapon type based on language"""
    if lang == "en":
        weapon_names = {
            "std": "Standard Missile",
            "moab": "MOAB Heavy Bomb",
            "f22": "F22 Raptor",
            "nuclear": "Nuclear Warhead",
        }
    else:  # Persian
        weapon_names = {
            "std": "موشک استاندارد",
            "moab": "بمب سنگین مواب",
            "f22": "جنگنده اف-۲۲ رپتور",
            "nuclear": "کلاهک هسته‌ای",
        }
    return weapon_names.get(weapon_type, weapon_names["std"])



@bot.message_handler(commands=['top'])
def top_cmd(m):
    ensure_group(m.chat.id, m.chat.title or "PM", m.chat.username)
    lang = get_lang(m.chat.id, m.from_user.id)
    rows = db("SELECT first_name, score FROM players WHERE chat_id=%s ORDER BY score DESC LIMIT 10", (m.chat.id,), fetch="all")
    out = []
    rank = 1
    for name, score in rows:
        medal = "🥇" if rank==1 else ("🥈" if rank==2 else ("🥉" if rank==3 else "•"))
        out.append(f"{medal} <b>{name}</b> — {score}")
        rank += 1
    bot.reply_to(m, T[lang]["top"].format(n=len(rows), lines="\n".join(out) if out else "—"))


# --- callback helpers ---
@bot.callback_query_handler(func=lambda c: c.data.startswith("go:"))
def goto_cb(c):
    _, where = c.data.split(":")
    lang = get_lang(c.message.chat.id, c.from_user.id)
    if where=="lang":
        bot.send_message(c.message.chat.id, T[lang]["lang_choose"], reply_markup=lang_kb(lang))
    elif where=="shop":
        shop_cmd(c.message)
    elif where=="stars":
        # Create a fake message object to pass to stars_cmd
        fake_msg = types.Message(
            message_id=c.message.message_id,
            from_user=c.from_user,
            date=now(),
            chat=c.message.chat,
            content_type='text',
            options={},
            json_string=''
        )
        fake_msg.text = '/stars'
        stars_cmd(fake_msg)
    bot.answer_callback_query(c.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("do:"))
def do_cb(c):
    _, act = c.data.split(":")
    if act=="shield":
        shield_cmd(c.message)
    elif act=="defend":
        defend_cmd(c.message)
    bot.answer_callback_query(c.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("attack_weapon:"))
def attack_weapon_cb(c):
    """Handle weapon selection for attacks"""
    _, weapon_type = c.data.split(":")
    lang = get_lang(c.message.chat.id, c.from_user.id)
    
    # Check if player has this weapon
    if weapon_type != "std" and inv_get(c.message.chat.id, c.from_user.id, weapon_type) <= 0:
        if lang == "fa":
            bot.answer_callback_query(c.id, "شما این سلاح را ندارید!", show_alert=True)
        else:
            bot.answer_callback_query(c.id, "You don't have this weapon!", show_alert=True)
        return
    
    # Prompt to reply to a user
    if lang == "fa":
        bot.edit_message_text(
            f"🎯 <b>سلاح انتخاب شد:</b> {get_weapon_display_name(weapon_type, lang)}\n\n"
            f"اکنون به پیام کاربری که می‌خواهید حمله کنید reply کرده و /attack را بزنید.",
            chat_id=c.message.chat.id, 
            message_id=c.message.message_id,
            parse_mode="HTML"
        )
        bot.answer_callback_query(c.id, f"سلاح {get_weapon_display_name(weapon_type, lang)} انتخاب شد!")
    else:
        bot.edit_message_text(
            f"🎯 <b>Weapon selected:</b> {get_weapon_display_name(weapon_type, lang)}\n\n"
            f"Now reply to the user you want to attack and use /attack command.",
            chat_id=c.message.chat.id, 
            message_id=c.message.message_id,
            parse_mode="HTML"
        )
        bot.answer_callback_query(c.id, f"{get_weapon_display_name(weapon_type, lang)} selected!")


@bot.callback_query_handler(func=lambda c: c.data.startswith("stats:"))
def stats_cb(c):
    """Handle stats button press"""
    _, user_id = c.data.split(":")
    lang = get_lang(c.message.chat.id, c.from_user.id)
    user_id = int(user_id)
    
    # Get user info
    user = find_user_by_id(c.message.chat.id, user_id)
    if not user:
        if lang == "fa":
            bot.answer_callback_query(c.id, "کاربر مورد نظر پیدا نشد!", show_alert=True)
        else:
            bot.answer_callback_query(c.id, "User not found!", show_alert=True)
        return
    
    # Get stats from database
    level_info = get_player_level_info(c.message.chat.id, user_id)
    
    # Get attack stats
    attack_stats = db(
        "SELECT COUNT(*) as total, SUM(CASE WHEN hit THEN 1 ELSE 0 END) as hits, "
        "SUM(CASE WHEN NOT hit THEN 1 ELSE 0 END) as misses, SUM(dmg) as total_dmg "
        "FROM attacks WHERE chat_id=%s AND attacker_id=%s",
        (c.message.chat.id, user_id), fetch="one")
    
    # Get defense stats
    defense_stats = db(
        "SELECT COUNT(*) as total, SUM(CASE WHEN hit THEN 1 ELSE 0 END) as hits, "
        "SUM(CASE WHEN NOT hit THEN 1 ELSE 0 END) as blocks, SUM(dmg) as total_dmg "
        "FROM attacks WHERE chat_id=%s AND defender_id=%s",
        (c.message.chat.id, user_id), fetch="one")
    
    # Calculate hit rate and other stats
    total_attacks = attack_stats[0] or 0
    hits = attack_stats[1] or 0
    misses = attack_stats[2] or 0
    total_dmg_dealt = attack_stats[3] or 0
    
    total_defenses = defense_stats[0] or 0
    hits_taken = defense_stats[1] or 0
    blocks = defense_stats[2] or 0
    total_dmg_taken = defense_stats[3] or 0
    
    hit_rate = (hits / total_attacks * 100) if total_attacks > 0 else 0
    block_rate = (blocks / total_defenses * 100) if total_defenses > 0 else 0
    
    # Format message
    if lang == "fa":
        stats_msg = (
            f"📊 <b>آمار {user.first_name}</b>\n\n"
            f"🎖 سطح: <b>{level_info['level']}</b>\n"
            f"📈 امتیاز: <b>{level_info['score']}</b>\n"
            f"🏅 مدال‌ها: <b>{medals(user_id, c.message.chat.id)}</b>\n\n"
            f"⚔️ <b>آمار حملات:</b>\n"
            f"• تعداد حملات: {total_attacks}\n"
            f"• اصابت‌ها: {hits} ({hit_rate:.1f}%)\n"
            f"• ناموفق‌ها: {misses}\n"
            f"• آسیب کل: {total_dmg_dealt}\n\n"
            f"🛡️ <b>آمار دفاع:</b>\n"
            f"• حملات دریافتی: {total_defenses}\n"
            f"• اصابت‌های دریافتی: {hits_taken}\n"
            f"• دفاع‌های موفق: {blocks} ({block_rate:.1f}%)\n"
            f"• آسیب دریافتی: {total_dmg_taken}"
        )
    else:
        stats_msg = (
            f"📊 <b>{user.first_name}'s Stats</b>\n\n"
            f"🎖 Level: <b>{level_info['level']}</b>\n"
            f"📈 Score: <b>{level_info['score']}</b>\n"
            f"🏅 Medals: <b>{medals(user_id, c.message.chat.id)}</b>\n\n"
            f"⚔️ <b>Attack Stats:</b>\n"
            f"• Total Attacks: {total_attacks}\n"
            f"• Hits: {hits} ({hit_rate:.1f}%)\n"
            f"• Misses: {misses}\n"
            f"• Total Damage: {total_dmg_dealt}\n\n"
            f"🛡️ <b>Defense Stats:</b>\n"
            f"• Attacks Received: {total_defenses}\n"
            f"• Hits Taken: {hits_taken}\n"
            f"• Blocks: {blocks} ({block_rate:.1f}%)\n"
            f"• Damage Taken: {total_dmg_taken}"
        )
    
    # Send as a new message to avoid confusion
    bot.send_message(c.message.chat.id, stats_msg)
    bot.answer_callback_query(c.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("hint:attack"))
def hint_attack(c):
    bot.answer_callback_query(c.id, "Reply to someone and type /attack")


@bot.callback_query_handler(func=lambda c: c.data.startswith("counter:"))
def counter_cb(c):
    attacker_id = int(c.data.split(":")[1])
    try:
        bot.send_message(c.message.chat.id, "Reply to your opponent and send /attack", reply_to_message_id=c.message.message_id)
    except Exception:
        pass
    bot.answer_callback_query(c.id)


# --- Private Chat Mode ---
@bot.message_handler(func=lambda m: m.chat.type == 'private' and not m.text.startswith('/'))
def private_chat_mode(m):
    ensure_player(m.chat.id, m.from_user)
    lang = get_lang(m.chat.id, m.from_user.id)
    
    # Presidential responses in private chat
    presidential_responses = {
        "en": [
            "As your Commander-in-Chief, I'm focusing on making our military the strongest it's ever been!",
            "We have the best missiles, the best defense systems. Nobody has better military than us!",
            "Let's take your military operations to the next level. Have you tried upgrading your arsenal?",
            "I know more about missiles than anybody. Use my warbot to show your strength!",
            "Join a group and show them how to win. Nobody wins better than my supporters!",
            "Use /shop to get the biggest, most beautiful weapons. They're tremendous!",
            "Your medals are very important. The most important. Protect them with a shield!",
            "I've always said, the best defense is a good offense. Attack first, attack hard!",
            "Check your /score and /inv - we're going to make your arsenal great again!",
            "Try the quiz command in groups - I ask the best questions, everybody says so!"
        ],
        "fa": [
            "به عنوان فرمانده کل قوا، تمرکز من بر ساختن قوی‌ترین ارتش تاریخ است!",
            "ما بهترین موشک‌ها و بهترین سیستم‌های دفاعی را داریم. هیچ‌کس بهتر از ما نیست!",
            "بیا عملیات نظامی‌ات را به سطح بالاتری ببریم. زرادخانه‌ات را ارتقا داده‌ای؟",
            "من درباره موشک‌ها بیشتر از همه می‌دانم. از ربات جنگی من برای نشان دادن قدرتت استفاده کن!",
            "به یک گروه بپیوند و به آنها نشان بده چطور پیروز شوند. هیچ‌کس بهتر از طرفداران من پیروز نمی‌شود!",
            "از /shop استفاده کن تا بزرگترین و زیباترین سلاح‌ها را بدست آوری. آنها فوق‌العاده هستند!",
            "مدال‌های شما بسیار مهم هستند. مهم‌ترین چیز. از آنها با سپر محافظت کنید!",
            "همیشه گفته‌ام، بهترین دفاع حمله خوب است. اول حمله کن، محکم حمله کن!",
            "امتیاز /score و زرادخانه‌ات /inv را بررسی کن - ما می‌خواهیم زرادخانه‌ات را دوباره عالی کنیم!",
            "دستور quiz را در گروه‌ها امتحان کن - من بهترین سؤالات را می‌پرسم، همه این را می‌گویند!"
        ]
    }
    
    # Select a random response
    response = random.choice(presidential_responses[lang])
    
    # Create a keyboard for private chat
    kb = types.InlineKeyboardMarkup()
    if lang == "fa":
        kb.row(types.InlineKeyboardButton("🛡️ سپر محافظ", callback_data="do:shield"),
               types.InlineKeyboardButton("🛰️ سیستم دفاعی", callback_data="do:defend"))
        kb.row(types.InlineKeyboardButton("🛍️ فروشگاه تسلیحات", callback_data="go:shop"),
               types.InlineKeyboardButton("🎒 زرادخانه من", callback_data="cmd:inv"))
        kb.row(types.InlineKeyboardButton("🏅 امتیاز من", callback_data="cmd:score"),
               types.InlineKeyboardButton("🎁 پاداش روزانه", callback_data="cmd:bonus"))
    else:
        kb.row(types.InlineKeyboardButton("🛡️ Shield", callback_data="do:shield"),
               types.InlineKeyboardButton("🛰️ Defense System", callback_data="do:defend"))
        kb.row(types.InlineKeyboardButton("🛍️ Weapons Shop", callback_data="go:shop"),
               types.InlineKeyboardButton("🎒 My Arsenal", callback_data="cmd:inv"))
        kb.row(types.InlineKeyboardButton("🏅 My Score", callback_data="cmd:score"),
               types.InlineKeyboardButton("🎁 Daily Bonus", callback_data="cmd:bonus"))
    
    bot.reply_to(m, response, reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("cmd:"))
def cmd_cb(c):
    _, cmd = c.data.split(":")
    # Create a fake message object to pass to the command handler
    class FakeMessage:
        def __init__(self, chat_id, from_user, text):
            self.chat = types.Chat(id=chat_id, type='private')
            self.from_user = from_user
            self.text = text
            self.message_id = 0
    
    fake_msg = FakeMessage(c.message.chat.id, c.from_user, f"/{cmd}")
    
    if cmd == "inv":
        inventory_cmd(fake_msg)
    elif cmd == "score":
        score_cmd(fake_msg)
    elif cmd == "bonus":
        bonus_cmd(fake_msg)
    
    bot.answer_callback_query(c.id)

# --- Message handling for natural language attack commands ---
@bot.message_handler(func=lambda m: m.chat.type != 'private' and m.text and not m.text.startswith('/') and m.reply_to_message)
def handle_natural_language_attacks(m):
    # Check if the message contains attack keywords
    attack_keywords_en = ["attack", "fire", "launch", "missile", "strike", "bomb", "hit", "shoot"]
    attack_keywords_fa = ["حمله", "شلیک", "موشک", "بزن", "آتش", "بمباران", "ضربه"]
    
    # Check if message contains any attack keywords
    message_lower = m.text.lower()
    contains_attack_keyword = any(keyword in message_lower for keyword in attack_keywords_en + attack_keywords_fa)
    
    if not contains_attack_keyword:
        # If not an attack command, update activity score and return
        ensure_player(m.chat.id, m.from_user)
        update_activity_score(m.chat.id, m.from_user.id, "message")
        return
    
    # This is an attack command, handle it as such
    ensure_player(m.chat.id, m.from_user)
    lang = get_lang(m.chat.id, m.from_user.id)
    
    # Get the weapon type if specified
    weapon_type = detect_weapon_type(m.text, lang)
    
    # Create a simulated attack command and process it
    process_attack(m, weapon_type)

def detect_weapon_type(text, lang):
    """Detect which weapon the user wants to use based on their message"""
    text_lower = text.lower()
    
    # English weapon keywords
    if lang == "en" or any(word in text_lower for word in ["missile", "rocket", "attack", "fire", "launch", "strike"]):
        if any(word in text_lower for word in ["moab", "heavy", "bomb"]):
            return "moab"
        elif any(word in text_lower for word in ["f22", "raptor", "jet", "plane", "aircraft"]):
            return "f22"
        elif any(word in text_lower for word in ["nuclear", "nuke", "atomic"]):
            return "nuclear"
    
    # Persian weapon keywords
    if lang == "fa" or any(word in text_lower for word in ["موشک", "حمله", "شلیک", "آتش"]):
        if any(word in text_lower for word in ["مواب", "بمب", "سنگین"]):
            return "moab"
        elif any(word in text_lower for word in ["رپتور", "اف۲۲", "هواپیما", "جنگنده"]):
            return "f22" 
        elif any(word in text_lower for word in ["اتمی", "هسته‌ای", "نوکلئار"]):
            return "nuclear"
    
    # Default to standard missile if no specific weapon detected
    return "std"

def process_attack(m, weapon_type="std"):
    """Process an attack with the specified weapon type"""
    ensure_player(m.chat.id, m.from_user)
    lang = get_lang(m.chat.id, m.from_user.id)
    left = cd_left(m.chat.id, m.from_user.id, 'attack')
    
    if left > 0:
        bot.reply_to(m, T[lang]["cooldown"].format(m=left))
        return
        
    # Use the reply_to_message user as the defender
    defender = m.reply_to_message.from_user
    
    if not defender:
        bot.reply_to(m, T[lang]["need_reply"])
        return
        
    if defender.id == bot.get_me().id:
        bot.reply_to(m, T[lang]["no_target_bot"])
        return
        
    if defender.id == m.from_user.id:
        bot.reply_to(m, T[lang]["no_target_self"])
        return
        
    ensure_player(m.chat.id, defender)

    # Block by shield
    if shield_rem(m.chat.id, defender.id) > 0:
        pct = 60
        bonus = intercept_state(m.chat.id, defender.id)[1]
        resline = T[lang]["attack_blocked"]
        hit = False
        dmg = 0
        weapon_used = "std"  # Default weapon when blocked
    else:
        intr, bonus = intercept_state(m.chat.id, defender.id)
        base = 60
        pct = max(5, min(95, base - bonus))
        
        # Determine which weapon to use based on user selection or availability
        weapon_used, weapon_bonus = select_weapon(m.chat.id, m.from_user.id, weapon_type)
        
        # Add level bonus (higher level = more damage)
        attacker_level = db("SELECT level FROM players WHERE chat_id=%s AND user_id=%s", 
                            (m.chat.id, m.from_user.id), fetch="one")
        level_bonus = (attacker_level[0] - 1) * 2 if attacker_level else 0
        
        hit = random.randint(1, 100) <= pct
        
        if hit:
            # Base damage plus weapon bonuses
            base_dmg = 15
            
            # Calculate total damage
            dmg = base_dmg + weapon_bonus + level_bonus
            
            # Get defender's current medals
            defender_medals = medals(defender.id, m.chat.id)
            
            # Calculate looting percentage based on attacker's level
            loot_percent = min(30, 10 + (attacker_level[0] * 3)) if attacker_level else 10
            
            # Calculate medals looted (percentage of damage or defender's medals)
            looted_medals = min(defender_medals, int(dmg * (loot_percent / 100)))
            
            # Apply medal changes
            add_medals(defender.id, m.chat.id, -dmg)
            add_medals(m.from_user.id, m.chat.id, looted_medals)
            
            # Update attacker's score
            score_gain = 10 + (level_bonus // 2)
            db("UPDATE players SET score=score+%s WHERE chat_id=%s AND user_id=%s", 
               (score_gain, m.chat.id, m.from_user.id))
            
            # Update activity scores
            update_activity_score(m.chat.id, m.from_user.id, "attack")
            
            # Weapon name for display
            weapon_display = get_weapon_display_name(weapon_used, lang)
            
            # Create a more dynamic hit message with weapon details
            if lang == "fa":
                resline = f"💥 اصابت مستقیم با {weapon_display}! <b>{defender.first_name}</b> {dmg} مدال از دست داد، <b>{m.from_user.first_name}</b> +{score_gain} امتیاز گرفت و {looted_medals} مدال غارت کرد!"
            else:
                resline = f"💥 DIRECT HIT with {weapon_display}! <b>{defender.first_name}</b> loses {dmg} medals, <b>{m.from_user.first_name}</b> gains +{score_gain} score and looted {looted_medals} medals!"
        else:
            dmg = 0
            looted_medals = 0
            
            # Create a more interesting miss message
            miss_messages_en = [
                "🤏 Missed by inches!",
                "💨 The missile flew right past the target!",
                "🌪️ Wind conditions affected the trajectory!",
                "⚠️ Missile guidance system failed!",
                "🔋 Energy systems malfunctioned mid-flight!"
            ]
            
            miss_messages_fa = [
                "🤏 موشک از کنار هدف گذشت!",
                "💨 موشک درست از بغل هدف عبور کرد!",
                "🌪️ شرایط باد مسیر موشک را تغییر داد!",
                "⚠️ سیستم هدایت موشک خراب شد!",
                "🔋 سیستم انرژی موشک در میانه پرواز از کار افتاد!"
            ]
            
            # Choose a random miss message based on language
            if lang == "fa":
                resline = random.choice(miss_messages_fa)
            else:
                resline = random.choice(miss_messages_en)
    
    # Record the attack in database
    db("INSERT INTO attacks(chat_id,attacker_id,defender_id,weapon,ts,hit,dmg) VALUES(%s,%s,%s,%s,%s,%s,%s)",
       (m.chat.id, m.from_user.id, defender.id, weapon_used, now(), hit, dmg))
    set_cd(m.chat.id, m.from_user.id, 'attack', 10)
    
    # Create a more visually appealing attack message
    if lang == "fa":
        weapon_emoji = get_weapon_emoji(weapon_used)
        attack_header = f"{weapon_emoji} <b>{m.from_user.first_name}</b> به <b>{defender.first_name}</b> حمله کرد"
        attack_details = f"🎯 احتمال اصابت: {pct}% | 🛰️ رهگیری: +{bonus}%"
        attack_msg = f"{attack_header}\n{attack_details}\n{resline}"
    else:
        weapon_emoji = get_weapon_emoji(weapon_used)
        attack_header = f"{weapon_emoji} <b>{m.from_user.first_name}</b> attacked <b>{defender.first_name}</b>"
        attack_details = f"🎯 Hit chance: {pct}% | 🛰️ Intercept: +{bonus}%"
        attack_msg = f"{attack_header}\n{attack_details}\n{resline}"
    
    bot.reply_to(m, attack_msg, reply_markup=after_attack_buttons(m.from_user.id, defender.id, lang))

def select_weapon(chat_id, user_id, requested_weapon="std"):
    """Select and consume a weapon based on user request and availability"""
    # Check if the requested special weapon is available
    if requested_weapon != "std" and inv_get(chat_id, user_id, requested_weapon) > 0:
        # User has requested a specific weapon they own
        inv_consume(chat_id, user_id, requested_weapon, 1)
        return requested_weapon, ITEMS[requested_weapon]["dmg"]
    
    # If requested weapon not available or just using standard, check for any special weapons
    for weapon in ["nuclear", "moab", "f22"]:  # Check in order of power
        if inv_get(chat_id, user_id, weapon) > 0:
            inv_consume(chat_id, user_id, weapon, 1)
            return weapon, ITEMS[weapon]["dmg"]
    
    # No special weapons available, use standard missile
    return "std", 0

def get_weapon_emoji(weapon_type):
    """Get the appropriate emoji for the weapon type"""
    weapon_emojis = {
        "std": "🚀",      # Standard missile
        "moab": "💣",     # MOAB Heavy Bomb
        "f22": "✈️",      # F22 Raptor
        "nuclear": "☢️",  # Nuclear warhead
    }
    return weapon_emojis.get(weapon_type, "🚀")  # Default to missile if unknown

def get_weapon_display_name(weapon_type, lang):
    """Get a display name for the weapon type based on language"""
    if lang == "en":
        weapon_names = {
            "std": "Standard Missile",
            "moab": "MOAB Heavy Bomb",
            "f22": "F22 Raptor",
            "nuclear": "Nuclear Warhead",
        }
    else:  # Persian
        weapon_names = {
            "std": "موشک استاندارد",
            "moab": "بمب سنگین مواب",
            "f22": "جنگنده اف-۲۲ رپتور",
            "nuclear": "کلاهک هسته‌ای",
        }
    return weapon_names.get(weapon_type, weapon_names["std"])


def find_user_by_id(chat_id, user_id):
    """Find a user by their ID in the database"""
    # Check if the user exists in the database
    r = db("SELECT first_name, username FROM players WHERE chat_id=%s AND user_id=%s", (chat_id, user_id), fetch="one")
    if not r:
        return None
    
    # Create a simple User object with the necessary fields
    class SimpleUser:
        def __init__(self, id, first_name, username=None):
            self.id = id
            self.first_name = first_name
            self.username = username
    
    first_name, username = r
    return SimpleUser(id=user_id, first_name=first_name, username=username)


# --- Message handling for activity scoring ---
sched = BackgroundScheduler(timezone="UTC")
sched.start()

print("WarBot (Postgres PvP) v2 running.")
bot.infinity_polling(skip_pending=True)
