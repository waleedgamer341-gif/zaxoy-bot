# bot.py — Zaxoy Bot | Part 1/3
# Replace YOUR_BOT_TOKEN / YOUR_OPENROUTER_KEY with your actual values

# ─────────────────────────────────────────────────────────────
# Imports
# ─────────────────────────────────────────────────────────────

import logging
import random
import asyncio
import re
import httpx

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReactionTypeEmoji,
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

from datetime import datetime, timezone

# ─────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────

BOT_TOKEN = "PUT_YOUR_TOKEN_HERE"
OWNER_ID = 7735152814
OPENROUTER_API_KEY = "PUT_YOUR_OPENROUTER_KEY_HERE"

logging.basicConfig(level=logging.INFO)

# ─────────────────────────────────────────────────────────────
# Permission Store
# ─────────────────────────────────────────────────────────────

admin_perms: dict[int, set] = {}


def has_perm(user_id: int, cmd: str) -> bool:
    if user_id == OWNER_ID:
        return True

    perms = admin_perms.get(user_id, set())
    return "all" in perms or cmd in perms


# ─────────────────────────────────────────────────────────────
# /start
# ─────────────────────────────────────────────────────────────

START_MESSAGES = [
    [
        "🌟 Zaxo is awake and ready!",
        "💫 Commands loading...",
        "🔥 Full power mode ON",
        "⚡ All systems go!",
        "🇵🇱 Zaxoy Bot is here for you!",
    ],
    [
        "🚀 Launching Zaxo systems...",
        "🌙 Night or day, Zaxo never sleeps",
        "🎯 Precision mode activated",
        "🛡️ Zaxo protection enabled",
        "🇵🇱 Let's go, Zaxoy Bot!",
    ],
    [
        "💎 Zaxo — rare, sharp, unstoppable",
        "🌊 Flowing with power",
        "🎶 Tuned to perfection",
        "🦅 Flying above the rest",
        "🇵🇱 Zaxoy Bot online!",
    ],
    [
        "⚔️ Zaxo stands strong",
        "Beauty meets intelligence",
        "🔮 Future is Zaxo",
        "✨ Sparkling with features",
        "🇵🇱 Zaxoy Bot activated!",
    ],
    [
        "🏔️ Tall as Zaxo mountains",
        "Colorful like Zaxo skies",
        "🎯 Always on target",
        "🤝 Here to help you",
        "🇵🇱 Zaxoy Bot, always ready!",
    ],
    [
        "🌍 Zaxo — known worldwide",
        "💡 Smart, fast, reliable",
        "🔑 Unlocking possibilities",
        "🌟 Shining brighter every day",
        "🇵🇱 Zaxoy Bot loaded!",
    ],
]


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msgs = random.choice(START_MESSAGES)
    text = "\n".join(msgs)
    await update.message.reply_text(text)


# ─────────────────────────────────────────────────────────────
# /on & /off
# ─────────────────────────────────────────────────────────────

ON_MSGS = [
    "✅ Zaxoy Bot is ON and fully operational 🇵🇱",
    "🟢 Discount Zaxoy Bot activated — ready to serve 🇵🇱",
    "⚡ Contact Zaxoy Bot — I'm online and listening 🇵🇱",
    "🔛 Zaxoy Bot switched ON — let the magic begin 🇵🇱",
    "💚 Zaxoy Bot is live and kicking 🇵🇱",
]

OFF_MSGS = [
    "🔴 Zaxoy Bot going offline — see you soon 🇵🇱",
    "⛔ Discount Zaxoy Bot is OFF for now 🇵🇱",
    "💤 Contact Zaxoy Bot — resting mode activated 🇵🇱",
    "🔕 Zaxoy Bot switched OFF — take care 🇵🇱",
    "❌ Zaxoy Bot signing out 🇵🇱",
]


async def on_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(ON_MSGS))


async def off_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(OFF_MSGS))


# ─────────────────────────────────────────────────────────────
# //info
# ─────────────────────────────────────────────────────────────

async def info_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    target = msg.reply_to_message

    if not target:
        await msg.reply_text("↩️ Reply to a message with //info to get user info.")
        return

    u = target.from_user
    lang = u.language_code or "Unknown"
    uid = u.id
    username = f"@{u.username}" if u.username else "No username"
    full_name = u.full_name or "Unknown"

    kb = [[InlineKeyboardButton(f"📋 Copy ID: {uid}", callback_data=f"copy_uid_{uid}")]]
    reply_markup = InlineKeyboardMarkup(kb)

    text = (
        f"👤 **Name:** {full_name}\n"
        f"🆔 **User ID:** `{uid}`\n"
        f"📎 **Username:** {username}\n"
        f"🌐 **Language:** {lang}\n"
        f"💬 **Message ID:** `{target.message_id}`\n"
        f"📅 **Account type:** {'Bot' if u.is_bot else 'Human'}\n"
        f"⭐ **Premium:** {'Yes' if getattr(u, 'is_premium', False) else 'No'}\n"
    )

    await msg.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=reply_markup,
        reply_to_message_id=target.message_id,
    )


# ─────────────────────────────────────────────────────────────
# //id
# ─────────────────────────────────────────────────────────────

async def id_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    target = msg.reply_to_message
    u = target.from_user if target else msg.from_user

    uid = u.id
    msg_id = target.message_id if target else msg.message_id
    chat_id = msg.chat_id

    kb = [
        [InlineKeyboardButton(f"👤 User ID: {uid}", callback_data=f"copy_uid_{uid}")],
        [InlineKeyboardButton(f"💬 Message ID: {msg_id}", callback_data=f"copy_mid_{msg_id}")],
        [InlineKeyboardButton(f"👥 Chat ID: {chat_id}", callback_data=f"copy_cid_{chat_id}")],
    ]

    text = (
        f"🆔 **User ID:** `{uid}`\n"
        f"💬 **Message ID:** `{msg_id}`\n"
        f"👥 **Chat/Group ID:** `{chat_id}`\n"
    )

    await msg.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb),
    )


async def copy_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(f"Copied: {query.data.split('_')[-1]}", show_alert=True)

# ─────────────────────────────────────────────────────────────
# Zaxo Protection + choose + xo
# ─────────────────────────────────────────────────────────────

ZAXO_DEFENSE = [
    "🛡️ Zaxo is the crown jewel of Kurdistan — built on history, love, and pride. Think before you speak. 🇵🇱",
    "🌊 The rivers of Zaxo carry more dignity than your words ever could. 🇵🇱",
    "⚔️ Zaxo stood for centuries — your opinion won't scratch it. 🇵🇱",
    "🏔️ Zaxo is carved from mountains. Insults? Just wind. 🇵🇱",
    "💎 Every stone in Zaxo is worth more than a thousand hateful words. 🇵🇱",
    "Zaxo doesn't need defense — it speaks for itself through its people, culture, and beauty. 🇵🇱",
]


def is_zaxo_insult(text: str) -> bool:
    t = text.lower()
    negative = [
        "part of duhok", "shit", "trash", "hate", "bad", "ugly",
        "stupid", "against", "fk", "small city"
    ]
    has_zaxo = any(z in t for z in ["zaxo", "zakho", "زاخو"])
    has_neg = any(n in t for n in negative)
    return has_zaxo and has_neg


async def zaxo_defense_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if msg and msg.text and is_zaxo_insult(msg.text):
        await msg.reply_text(random.choice(ZAXO_DEFENSE))


def is_waleed_fake(text: str) -> bool:
    pattern = r'\bWaleed\s+\w+[ie]\b'
    matches = re.findall(pattern, text, re.IGNORECASE)

    for m in matches:
        parts = m.strip().split()
        if len(parts) >= 2 and parts[1].lower() not in ["zaxoy", "zaxo"]:
            return True

    return False


async def waleed_protection(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if msg and msg.text and is_waleed_fake(msg.text):
        await msg.reply_text("Waleed Zaxoy*", reply_to_message_id=msg.message_id)


ZAXO_MESSAGES = [
    "🌟 Zaxo — where the Khabur river sings and the mountains whisper ancient tales. 🇵🇱",
    "💫 Zaxo: the city of bridges, not only over rivers, but between hearts. 🇵🇱",
    "🎶 Erdwan Zaxoy — a voice that carries the soul of an entire city in every note. Pure magic. 🇵🇱",
    "🔥 If passion had an address, it would be Zaxo, Kurdistan. 🇵🇱",
    "Zaxo raised warriors, poets, and dreamers — all in one breath. 🇵🇱",
]


async def zaxo_msg(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(ZAXO_MESSAGES))


# choose
choose_sessions: dict[int, dict] = {}


async def choose_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    choose_sessions[msg.chat_id] = {
        "owner": msg.from_user.id,
        "names": [],
        "step": "waiting",
    }
    await msg.reply_text("📝 Add names line by line. Send them now!")


async def choose_names_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    session = choose_sessions.get(msg.chat_id)

    if not session or session["owner"] != msg.from_user.id or session["step"] != "waiting":
        return

    names = [n.strip() for n in msg.text.splitlines() if n.strip()]

    if len(names) < 2:
        await msg.reply_text("⚠️ Please send at least 2 names, one per line.")
        return

    session["step"] = "choosing"
    loading = await msg.reply_text("🎯 choosing someone")

    for _ in range(6):
        for d in [".", "..", "..."]:
            await asyncio.sleep(0.4)
            try:
                await loading.edit_text(f"🎯 choosing someone{d}")
            except:
                pass

    winner = random.choice(names)
    await loading.edit_text(f"🏆 **{winner}**", parse_mode="Markdown")
    await asyncio.sleep(20)

    try:
        await loading.edit_text(f"🏆 **{winner}** 🎉", parse_mode="Markdown")
    except:
        pass

    choose_sessions.pop(msg.chat_id, None)


# xo
xo_games: dict[int, dict] = {}


def check_winner(board):
    wins = [
        (0,1,2),(3,4,5),(6,7,8),
        (0,3,6),(1,4,7),(2,5,8),
        (0,4,8),(2,4,6)
    ]

    for a,b,c in wins:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]

    if all(board):
        return "draw"

    return None


def make_xo_keyboard(game):
    buttons = []

    for i in range(0, 9, 3):
        row = []

        for j in range(i, i + 3):
            val = game["board"][j]

            e = (
                game["p1_emoji"] if val == 1
                else game["p2_emoji"] if val == 2
                else "⬜"
            )

            row.append(
                InlineKeyboardButton(
                    e,
                    callback_data=f"xo_{game['chat_id']}_{j}"
                )
            )

        buttons.append(row)

    return InlineKeyboardMarkup(buttons)

VALID_CMDS = {
    "//info", "//id", "//r", "//ask", "//zaxo",
    "//say", "//st", "//re", "//mute"
}


async def ask_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    text_parts = msg.text.split(None, 1)
    question = text_parts[1] if len(text_parts) > 1 else None

    if not question:
        await msg.reply_text("🤖 Ask me anything!\nUsage: //ask [your question]")
        return

    thinking = await msg.reply_text("🤔 Thinking...")

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://t.me/",
                    "X-Title": "ZaxoyBot",
                },
                json={
                    "model": "google/gemma-2-9b-it:free",
                    "messages": [{"role": "user", "content": question}],
                    "max_tokens": 1000,
                },
            )

        data = resp.json()
        answer = data["choices"][0]["message"]["content"] if "choices" in data else str(data)

    except Exception as e:
        answer = f"⚠️ Error: {str(e)}"

    await thinking.edit_text(f"🤖 {answer}")


# ─────────────────────────────────────────────────────────────
# mute / unmute
# ─────────────────────────────────────────────────────────────

def parse_duration(text: str) -> int:
    units = {
        "s": 1, "sec": 1,
        "m": 60, "min": 60,
        "h": 3600, "hr": 3600,
        "d": 86400,
        "w": 604800,
        "mo": 2592000,
        "y": 31536000,
    }

    pattern = r"(\d+)\s*([a-zA-Z]+)"
    matches = re.findall(pattern, text.lower())

    total = 0

    for amount, unit in matches:
        if unit in units:
            total += int(amount) * units[unit]

    return total


def format_duration(seconds: int) -> str:
    if seconds >= 86400:
        return f"{seconds // 86400} day(s)"
    if seconds >= 3600:
        return f"{seconds // 3600} hour(s)"
    if seconds >= 60:
        return f"{seconds // 60} minute(s)"
    return f"{seconds} second(s)"


MUTE_MESSAGES = [
    "🔇 {name} has been silenced in Zaxo's domain for {duration}. 🇵🇱",
    "⛓️ {name} is now muted for {duration}. 🇵🇱",
    "🚫 {name} — {duration} of silence. 🇵🇱",
]


async def mute_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    if not has_perm(msg.from_user.id, "//mute"):
        await msg.reply_text("⛔ You don't have permission 🇵🇱")
        return

    target = msg.reply_to_message

    if not target:
        await msg.reply_text(
            "↩️ Reply to a message or provide @username / ID\nExample: //mute @user 1h"
        )
        return

    text_parts = msg.text.strip().split(None, 1)
    args = text_parts[1] if len(text_parts) > 1 else ""

    duration_seconds = parse_duration(args)

    if duration_seconds <= 0:
        await msg.reply_text("❌ Example: //mute 1h or //mute 2d")
        return

    until = datetime.now(timezone.utc).timestamp() + duration_seconds

    try:
        await ctx.bot.restrict_chat_member(
            chat_id=msg.chat_id,
            user_id=target.from_user.id,
            permissions={},
            until_date=int(until),
        )

        await msg.reply_text(
            random.choice(MUTE_MESSAGES).format(
                name=target.from_user.full_name,
                duration=format_duration(duration_seconds),
            )
        )

    except Exception as e:
        await msg.reply_text(f"⚠️ {str(e)}")


async def unmute_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    if not has_perm(msg.from_user.id, "//mute"):
        await msg.reply_text("⛔ You don't have permission 🇵🇱")
        return

    target = msg.reply_to_message

    if not target:
        await msg.reply_text("↩️ Reply to a message with //unmute")
        return

    try:
        from telegram import ChatPermissions

        await ctx.bot.restrict_chat_member(
            chat_id=msg.chat_id,
            user_id=target.from_user.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_invite_users=True,
            ),
        )

        await msg.reply_text(
            f"🔊 {target.from_user.full_name} can speak again 🇵🇱"
        )

    except Exception as e:
        await msg.reply_text(f"⚠️ {str(e)}")


# ─────────────────────────────────────────────────────────────
# router + main
# ─────────────────────────────────────────────────────────────

async def message_router(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    if not msg or not msg.text:
        return

    text = msg.text.strip()

    if text.startswith("//info"):
        await info_cmd(update, ctx)

    elif text.startswith("//id"):
        await id_cmd(update, ctx)

    elif text.startswith("//ask"):
        await ask_cmd(update, ctx)

    elif text.startswith("//zaxo"):
        await zaxo_msg(update, ctx)

    elif text.startswith("//mute"):
        await mute_cmd(update, ctx)

    elif text.startswith("//unmute"):
        await unmute_cmd(update, ctx)

    else:
        await zaxo_defense_handler(update, ctx)
        await waleed_protection(update, ctx)

        session = choose_sessions.get(msg.chat_id)
        if session and session.get("step") == "waiting":
            await choose_names_handler(update, ctx)


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("on", on_cmd))
    app.add_handler(CommandHandler("off", off_cmd))
    app.add_handler(CommandHandler("choose", choose_cmd))

    app.add_handler(CallbackQueryHandler(copy_callback, pattern="^copy_"))
    app.add_handler(CallbackQueryHandler(xo_move, pattern="^xo_"))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_router
        )
    )

    app.run_polling()


if __name__ == "__main__":
    main()
