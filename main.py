# trump_wargame_bot_pg_v2.py
# Telegram PvP War Game — Donald Trump theme 🇺🇸
# Features:
# - PvP inside groups (reply/mention to attack)
# - Bilingual FA/EN with per-user language
# - UX: inline menus, counter buttons, short cards
# - Defense: Shield (block) & Intercept (reduce hit chance)
# - Stars Shop (XTR): Aegis Shield, Patriot Boost, MOAB Heavy Bomb
# - Medals economy, Daily bonus
# - Inventory + auto-use MOAB
# - Leaderboard /top, Inventory /inv
# - PostgreSQL storage

import os, time, random
from datetime import datetime
import psycopg
from psycopg_pool import ConnectionPool
import telebot
from telebot import types
from apscheduler.schedulers.background import BackgroundScheduler

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL", "YOUR_URL")
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
  shield_until BIGINT DEFAULT 0,
  intercept_until BIGINT DEFAULT 0,
  intercept_bonus INT DEFAULT 0,
  last_active BIGINT DEFAULT 0,
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
  item TEXT, stars INT, ts BIGINT, payload TEXT
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
""")


def now(): return int(time.time())


# --- i18n ---
T = {
  "en": {
    "brand": "🇺🇸 <b>Donald Trump WarBot</b>",
    "welcome": "PvP missile fights inside your group. Use /help to learn how to collect 🏅 medals.",
    "help": (
      "🎮 <b>How to play</b>\n"
      "• Reply to someone and send /attack — launch a missile\n"
      "• /defend — bring Patriot interceptors online\n"
      "• /shield — full Aegis shield for hours\n"
      "• /status — your stats & defenses\n"
      "• /shop — buy special gear with Stars ⭐️\n"
      "• /bonus — daily medals\n"
      "• /inv — your inventory\n"
      "• /top — group leaderboard\n"
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
    "cooldown": "⏱️ On cooldown. Try again in {m} minutes.",
    "not_enough_medals": "Not enough medals. Claim /bonus.",
    "shop": "🛍️ <b>Stars Shop</b> — pick an item:",
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
    "welcome": "نبرد موشکی بین اعضای گروه! برای یادگیری جمع‌کردن 🏅 مدال، /help را بزن.",
    "help": (
      "🎮 <b>قوانین بازی</b>\n"
      "• روی پیام طرف ریپلای کن و /attack بزن — حمله موشکی\n"
      "• /defend — پدافند پاتریوت (رهگیری ۱۲ ساعت)\n"
      "• /shield — سپر ایجیس (۳ ساعت)\n"
      "• /status — وضعیت و دفاع‌ها\n"
      "• /shop — خرید آیتم ویژه با Stars ⭐️\n"
      "• /bonus — پاداش روزانه\n"
      "• /inv — موجودی شما\n"
      "• /top — جدول برترین‌های گروه\n"
      "• /lang — تغییر زبان\n\n"
      "🚫 هدف گرفتن خود بات ممنوع است."
    ),
    "lang_choose": "زبان را انتخاب کن:",
    "lang_set_en": "Language set to English.",
    "lang_set_fa": "زبان به فارسی تنظیم شد.",
    "status_self": "<b>{name}</b>\n🏅 مدال: <b>{medals}</b> | 🏆 امتیاز: <b>{score}</b>\n🛡️ سپر: {shield} | 🛰️ پدافند: {intercept}",
    "status_hint": "نکته: روی پیام طرف ریپلای کن و /attack بزن.",
    "shield_on": "🛡️ <b>سپر ایجیس</b> برای <b>{hours} ساعت</b> فعال شد.",
    "shield_left": "🛡️ سپر فعال است: {mins} دقیقه باقی‌مانده.",
    "def_on": "🛰️ <b>پاتریوت</b> به مدت <b>{hours} ساعت</b> فعال شد (+{bonus}% رهگیری).",
    "def_left": "🛰️ پدافند فعال است: {mins} دقیقه باقی‌مانده.",
    "no_target_bot": "❌ نمی‌تونی خود بات را هدف بگیری.",
    "no_target_self": "😅 خودت را نمی‌شود هدف گرفت.",
    "need_reply": "برای حمله باید روی پیام طرف ریپلای کنی یا منشنش کنی.",
    "attack_ok": "🚀 <b>{attacker}</b> به <b>{defender}</b> حمله کرد\n🎯 شانس اصابت: {pct}% | 🛰️ رهگیری +{bonus}%\n{result}",
    "attack_blocked": "🛡️ سپر دفاعی طرف، حمله را کامل دفع کرد.",
    "attack_hit": "💥 اصابت مستقیم! <b>{defender}</b> {dmg} مدال از دست داد، <b>{attacker}</b> +{score} امتیاز.",
    "attack_miss": "🤏 اصابت نشد!",
    "cooldown": "⏱️ در کول‌داون هستی. {m} دقیقه دیگر تلاش کن.",
    "not_enough_medals": "مدال کافی نداری. /bonus را بزن.",
    "shop": "🛍️ <b>فروشگاه Stars</b> — یک آیتم انتخاب کن:",
    "buy_done": "✅ خرید انجام شد: <b>{item}</b>.",
    "bonus_ok": "🎁 پاداش روزانه: +<b>{medals}</b> مدال.",
    "bonus_wait": "⏳ امروز گرفتی. حدود <b>{hrs} ساعت</b> دیگر امتحان کن.",
    "humor": "«داریم گروه <b>{group}</b> را دوباره بزرگ می‌کنیم—قول می‌دم!» 😉",
    "inv": "🎒 <b>موجودی</b>\n{lines}",
    "empty_inv": "— خالی —",
    "top": "🏆 <b>برترین‌ها</b>\n{lines}"
  }
}

ITEMS = {
  # Stars items
  "aegis":  {"title":"Aegis Shield (3h)", "price":499, "type":"shield", "hours":3},
  "patriot":  {"title":"Patriot Boost (12h)", "price":299, "type":"intercept", "bonus":20, "hours":12},
  "moab":  {"title":"MOAB Heavy Bomb (next attack +25 dmg)", "price":699, "type":"weapon", "dmg":25},
  "f22":  {"title":"F22 Raptor Heavy Attack (next attack +5 dmg)", "price":1, "type":"weapon", "dmg":5},
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
def lang_kb():
    kb = types.InlineKeyboardMarkup()
    kb.row(types.InlineKeyboardButton("English", callback_data="lang:en"),
           types.InlineKeyboardButton("فارسی", callback_data="lang:fa"))
    return kb


def main_menu():
    kb = types.InlineKeyboardMarkup()
    kb.row(types.InlineKeyboardButton("🚀 Attack", callback_data="hint:attack"),
           types.InlineKeyboardButton("🛡️ Shield", callback_data="do:shield"))
    kb.row(types.InlineKeyboardButton("🛰️ Defend", callback_data="do:defend"),
           types.InlineKeyboardButton("🛍️ Shop ⭐️", callback_data="go:shop"))
    kb.row(types.InlineKeyboardButton("🌐 Language", callback_data="go:lang"))
    return kb


def after_attack_buttons(attacker_id, defender_id):
    kb = types.InlineKeyboardMarkup()
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
    bot.reply_to(m, f"{T[lang]['brand']}\n{T[lang]['welcome']}\n\n{T[lang]['humor'].format(group=m.chat.title or 'this chat')}", reply_markup=main_menu())


@bot.message_handler(commands=['help'])
def help_cmd(m):
    ensure_player(m.chat.id, m.from_user)
    lang = get_lang(m.chat.id, m.from_user.id)
    bot.reply_to(m, T[lang]["help"])


@bot.message_handler(commands=['lang'])
def lang_cmd(m):
    ensure_player(m.chat.id, m.from_user)
    lang = get_lang(m.chat.id, m.from_user.id)
    bot.reply_to(m, T[lang]["lang_choose"], reply_markup=lang_kb())


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
    r = db("SELECT score FROM players WHERE chat_id=%s AND user_id=%s", (m.chat.id, m.from_user.id), fetch="one")
    score = r[0] if r else 0
    sh_t = f"{sh//60}m" if sh>0 else ("OFF" if lang=='en' else "خاموش")
    in_t = f"{intr//60}m (+{bonus}%)" if intr>0 else ("OFF" if lang=='en' else "خاموش")
    bot.reply_to(m, T[lang]["status_self"].format(name=m.from_user.first_name, medals=med, score=score, shield=sh_t, intercept=in_t) + "\\n\\n" + T[lang]["status_hint"])


@bot.message_handler(commands=['bonus'])
def bonus_cmd(m):
    ensure_player(m.chat.id, m.from_user)
    lang = get_lang(m.chat.id, m.from_user.id)
    left = cd_left(m.chat.id, m.from_user.id, 'daily')
    if left>0:
        bot.reply_to(m, T[lang]["bonus_wait"].format(hrs=left//3600 + 1)); return
    add_medals(m.from_user.id, m.chat.id, 60)
    set_cd(m.chat.id, m.from_user.id, 'daily', 23*3600)
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
    bot.reply_to(m, T[lang]["shield_on"].format(hours=3))


@bot.message_handler(commands=['defend'])
def defend_cmd(m):
    ensure_player(m.chat.id, m.from_user)
    lang = get_lang(m.chat.id, m.from_user.id)
    intr, bonus = intercept_state(m.chat.id, m.from_user.id)
    if intr>0:
        bot.reply_to(m, T[lang]["def_left"].format(mins=intr//60)); return
    set_intercept(m.chat.id, m.from_user.id, 12, 20)
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
        bot.reply_to(m, T[lang]["cooldown"].format(m=left//60)); return
    defender = find_defender(m)
    if not defender:
        bot.reply_to(m, T[lang]["need_reply"]); return
    if defender.id == bot.get_me().id:
        bot.reply_to(m, T[lang]["no_target_bot"]); return
    if defender.id == m.from_user.id:
        bot.reply_to(m, T[lang]["no_target_self"]); return
    ensure_player(m.chat.id, defender)

    # Block by shield
    if shield_rem(m.chat.id, defender.id) > 0:
        pct = 60; bonus = intercept_state(m.chat.id, defender.id)[1]
        resline = T[lang]["attack_blocked"]
        hit = False; dmg = 0
    else:
        intr, bonus = intercept_state(m.chat.id, defender.id)
        base = 60
        pct = max(5, min(95, base - bonus))
        # MOAB auto-use if available
        moab_bonus = 0
        if inv_get(m.chat.id, m.from_user.id, "moab") > 0:
            inv_consume(m.chat.id, m.from_user.id, "moab", 1)
            moab_bonus = ITEMS["moab"]["dmg"]
        hit = random.randint(1,100) <= pct
        if hit:
            dmg = 15 + moab_bonus
            add_medals(defender.id, m.chat.id, -dmg)
            db("UPDATE players SET score=score+10 WHERE chat_id=%s AND user_id=%s", (m.chat.id, m.from_user.id))
            resline = T[lang]["attack_hit"].format(defender=defender.first_name, attacker=m.from_user.first_name, dmg=dmg, score=10)
        else:
            dmg = 0
            resline = T[lang]["attack_miss"]
    db("INSERT INTO attacks(chat_id,attacker_id,defender_id,weapon,ts,hit,dmg) VALUES(%s,%s,%s,%s,%s,%s,%s)",
       (m.chat.id, m.from_user.id, defender.id, 'std', now(), hit, dmg))
    set_cd(m.chat.id, m.from_user.id, 'attack', 600)
    bot.reply_to(m, T[lang]["attack_ok"].format(attacker=m.from_user.first_name, defender=defender.first_name, pct=pct, bonus=intercept_state(m.chat.id, defender.id)[1], result=resline), reply_markup=after_attack_buttons(m.from_user.id, defender.id))


@bot.message_handler(commands=['shop'])
def shop_cmd(m):
    ensure_player(m.chat.id, m.from_user)
    lang = get_lang(m.chat.id, m.from_user.id)
    kb = types.InlineKeyboardMarkup()
    for k,v in ITEMS.items():
        kb.add(types.InlineKeyboardButton(f"⭐️ {v['title']} — {v['price']}", callback_data=f"buy:{k}"))
    bot.reply_to(m, T[lang]["shop"], reply_markup=kb)


@bot.callback_query_handler(func=lambda c: c.data.startswith("buy:"))
def buy_cb(c):
    key = c.data.split(":")[1]
    item = ITEMS[key]
    prices = [types.LabeledPrice(label=item["title"], amount=item["price"])]
    bot.send_invoice(
        chat_id=c.message.chat.id,
        title=item["title"],
        description=f"Buy {item['title']} with Telegram Stars.",
        invoice_payload=f"stars:{key}:{c.from_user.id}:{c.message.chat.id}:{now()}",
        provider_token="",   # Stars/XTR
        currency="XTR",
        prices=prices,
        start_parameter=f"buy_{key}"
    )


@bot.pre_checkout_query_handler(func=lambda q: True)
def on_pre_checkout(q):
    bot.answer_pre_checkout_query(q.id, ok=True)


@bot.message_handler(content_types=['successful_payment'])
def on_success(m):
    payload = m.successful_payment.invoice_payload
    if not payload.startswith("stars:"): return
    _, key, uid, chat_id, ts = payload.split(":")
    uid = int(uid); chat_id = int(chat_id)
    db("INSERT INTO purchases(chat_id,user_id,item,stars,ts,payload) VALUES(%s,%s,%s,%s,%s,%s)",
       (chat_id, uid, key, m.successful_payment.total_amount, now(), payload))
    if key == "aegis":
        set_shield(chat_id, uid, ITEMS[key]["hours"])
    elif key == "patriot":
        set_intercept(chat_id, uid, ITEMS[key]["hours"], ITEMS[key]["bonus"])
    elif key == "moab":
        inv_add(chat_id, uid, "moab", 1)
    lang = get_lang(chat_id, uid)
    bot.reply_to(m, T[lang]["buy_done"].format(item=ITEMS[key]["title"]))


@bot.message_handler(commands=['inv'])
def inv_cmd(m):
    ensure_player(m.chat.id, m.from_user)
    lang = get_lang(m.chat.id, m.from_user.id)
    rows = db("SELECT item, qty FROM inventories WHERE chat_id=%s AND user_id=%s ORDER BY item", (m.chat.id, m.from_user.id), fetch="all")
    if not rows:
        lines = T[lang]["empty_inv"]
    else:
        pretty = {"moab":"MOAB Heavy Bomb"}
        lines = "\\n".join([f"• {pretty.get(k,k)} × {q}" for k,q in rows])
    bot.reply_to(m, T[lang]["inv"].format(lines=lines))


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
    bot.reply_to(m, T[lang]["top"].format(n=len(rows), lines="\\n".join(out) if out else "—"))


# --- callback helpers ---
@bot.callback_query_handler(func=lambda c: c.data.startswith("go:"))
def goto_cb(c):
    _, where = c.data.split(":")
    lang = get_lang(c.message.chat.id, c.from_user.id)
    if where=="lang":
        bot.send_message(c.message.chat.id, T[lang]["lang_choose"], reply_markup=lang_kb())
    elif where=="shop":
        shop_cmd(c.message)
    bot.answer_callback_query(c.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("do:"))
def do_cb(c):
    _, act = c.data.split(":")
    if act=="shield":
        shield_cmd(c.message)
    elif act=="defend":
        defend_cmd(c.message)
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


# --- scheduler (placeholder for future events/cleanup) ---
sched = BackgroundScheduler(timezone="UTC")
sched.start()

print("WarBot (Postgres PvP) v2 running.")
bot.infinity_polling(skip_pending=True)
