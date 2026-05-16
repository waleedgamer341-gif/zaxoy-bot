# bot.py — Zaxoy Bot | Part 1/3
# Replace YOUR_BOT_TOKEN with your actual token

# ─────────────────────────────────────────────────────────────
# Imports
# ─────────────────────────────────────────────────────────────

import logging
import random
import asyncio
import re

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReactionTypeEmoji
)


from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

# ─────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────

BOT_TOKEN = "8502998355:AAFXTOA0UJW3IBwje7wIsC-M4vTIhBXubm0"

OWNER_ID = 7735152814

OPENROUTER_API_KEY = "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"

logging.basicConfig(level=logging.INFO)

# ─────────────────────────────────────────────────────────────
# Permission Store
# Structure:
# { user_id: set(commands) }
#
# "all" = full admin permissions
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
        "🇵🇱 Zaxoy Bot is here for you!"
    ],

    [
        "🚀 Launching Zaxo systems...",
        "🌙 Night or day, Zaxo never sleeps",
        "🎯 Precision mode activated",
        "🛡️ Zaxo protection enabled",
        "🇵🇱 Let's go, Zaxoy Bot!"
    ],

    [
        "💎 Zaxo — rare, sharp, unstoppable",
        "🌊 Flowing with power",
        "🎶 Tuned to perfection",
        "🦅 Flying above the rest",
        "🇵🇱 Zaxoy Bot online!"
    ],

    [
        "⚔️ Zaxo stands strong",
        " Beauty meets intelligence",
        "🔮 Future is Zaxo",
        "✨ Sparkling with features",
        "🇵🇱 Zaxoy Bot activated!"
    ],

    [
        "🏔️ Tall as Zaxo mountains",
        " Colorful like Zaxo skies",
        "🎯 Always on target",
        "🤝 Here to help you",
        "🇵🇱 Zaxoy Bot, always ready!"
    ],

    [
        "🌍 Zaxo — known worldwide",
        "💡 Smart, fast, reliable",
        "🔑 Unlocking possibilities",
        "🌟 Shining brighter every day",
        "🇵🇱 Zaxoy Bot loaded!"
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
        await msg.reply_text(
            "↩️ Reply to a message with //info to get user info."
        )
        return

    u = target.from_user

    lang = u.language_code or "Unknown"
    uid = u.id

    username = f"@{u.username}" if u.username else "No username"
    full_name = u.full_name or "Unknown"

    kb = [
        [
            InlineKeyboardButton(
                f"📋 Copy ID: {uid}",
                callback_data=f"copy_uid_{uid}"
            )
        ]
    ]

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
        reply_to_message_id=target.message_id
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
        [
            InlineKeyboardButton(
                f"👤 User ID: {uid}",
                callback_data=f"copy_uid_{uid}"
            )
        ],

        [
            InlineKeyboardButton(
                f"💬 Message ID: {msg_id}",
                callback_data=f"copy_mid_{msg_id}"
            )
        ],

        [
            InlineKeyboardButton(
                f"👥 Chat ID: {chat_id}",
                callback_data=f"copy_cid_{chat_id}"
            )
        ],
    ]

    reply_markup = InlineKeyboardMarkup(kb)

    text = (
        f"🆔 **User ID:** `{uid}`\n"
        f"💬 **Message ID:** `{msg_id}`\n"
        f"👥 **Chat/Group ID:** `{chat_id}`\n"
    )

    await msg.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def copy_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer(
        f"Copied: {query.data.split('_')[-1]}",
        show_alert=True
    )


# ─────────────────────────────────────────────────────────────
# Zaxo City Protection
# ─────────────────────────────────────────────────────────────

ZAXO_INSULTS = [
    "Fk zaxo",
    "zaxo pop",
    "Zaxo small",
    "Zaxo is part of duhok",
    "zaxo is trash",
    "bad zaxo",
    "i dont like zaxo",
    "hate zaxo",
    "zaxo is shit",
    "against zaxo"
]

ZAXO_DEFENSE =  [ 
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
        "Part of duhok",
        "shit",
        "trash",
        "hate",
        "bad",
        "ugly",
        "stupid",
        "against",
        "fk",
        "part of duhok",
        "small city"
    ]

    has_zaxo = any(
        z in t
        for z in ["zaxo", "zakho", "زاخو"]
    )

    has_neg = any(
        n in t
        for n in negative
    )

    return has_zaxo and has_neg


async def zaxo_defense_handler(
    update: Update,
    ctx: ContextTypes.DEFAULT_TYPE
):

    msg = update.message

    if not msg or not msg.text:
        return

    if is_zaxo_insult(msg.text):
        await msg.reply_text(
            random.choice(ZAXO_DEFENSE)
        )


# ─────────────────────────────────────────────────────────────
# Waleed Zaxoy Name Protection
# ─────────────────────────────────────────────────────────────

def is_waleed_fake(text: str) -> bool:

    pattern = r'\bWaleed\s+\w+[ie]\b'

    matches = re.findall(
        pattern,
        text,
        re.IGNORECASE
    )

    for m in matches:

        parts = m.strip().split()

        if len(parts) >= 2:

            second = parts[1].lower()

            if second not in ["zaxoy", "zaxo"]:
                return True

    return False


async def waleed_protection(
    update: Update,
    ctx: ContextTypes.DEFAULT_TYPE
):

    msg = update.message

    if not msg or not msg.text:
        return

    if is_waleed_fake(msg.text):

        await msg.reply_text(
            "Waleed Zaxoy*",
            reply_to_message_id=msg.message_id
        )


# ─────────────────────────────────────────────────────────────
# //zaxo
# ─────────────────────────────────────────────────────────────

ZAXO_MESSAGES = [
    "🌟 Zaxo — where the Khabur river sings and the mountains whisper ancient tales. 🇵🇱",

    "💫 Zaxo: the city of bridges, not only over rivers, but between hearts. 🇵🇱",

    "🎶 Erdwan Zaxoy — a voice that carries the soul of an entire city in every note. Pure magic. 🇵🇱",

    "🔥 If passion had an address, it would be Zaxo, Kurdistan. 🇵🇱",

    "Zaxo raised warriors, poets, and dreamers — all in one breath. 🇵🇱",

    "🎵 Erdwan Zaxoy sings and suddenly the whole world remembers where home is. 🇵🇱",

    "🏔️ From the peaks of Zaxo to the ends of the earth — the name travels far. 🇵🇱",

    "✨ Zaxo: ancient like history, fresh like morning air. 🇵🇱",

    "💎 The people of Zaxo carry gold in their words and steel in their hearts. 🇵🇱",

    "🌊 Every wave in the Khabur knows the name Zaxo — it's been whispered for centuries. 🇵🇱",

    "🎼 Erdwan Zaxoy — his melodies don't just play, they heal. A legend born from Zaxo's spirit. 🇵🇱",

    "Zaxo doesn't just exist on the map — it lives in every soul that once touched its streets. 🇵🇱",

    "⚡ From Zaxo, with pride. No city shines brighter. 🇵🇱",

    "🦅 Zaxo soars like an eagle — high, proud, and forever free. 🇵🇱",

    "🌙 When the night falls on Zaxo, the stars shine a little brighter than anywhere else. 🇵🇱",
]


async def zaxo_msg(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        random.choice(ZAXO_MESSAGES)
    )
# bot.py — Part 2/3

# ─────────────────────────────────────────────────────────────
# /choose Game
# ─────────────────────────────────────────────────────────────

choose_sessions: dict[int, dict] = {}


async def choose_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

    msg = update.message

    user_id = msg.from_user.id
    chat_id = msg.chat_id

    choose_sessions[chat_id] = {
        "owner": user_id,
        "names": [],
        "step": "waiting"
    }

    await msg.reply_text(
        "📝 Add names line by line. Send them now!"
    )


async def choose_names_handler(
    update: Update,
    ctx: ContextTypes.DEFAULT_TYPE
):

    msg = update.message

    chat_id = msg.chat_id
    user_id = msg.from_user.id

    session = choose_sessions.get(chat_id)

    if not session or session.get("step") != "waiting":
        return

    if session["owner"] != user_id:
        return

    names = [
        n.strip()
        for n in msg.text.strip().splitlines()
        if n.strip()
    ]

    if len(names) < 2:
        await msg.reply_text(
            "⚠️ Please send at least 2 names, one per line."
        )
        return

    session["step"] = "choosing"

    loading_msg = await msg.reply_text(
        "🎯 choosing someone"
    )

    dots = [".", "..", "..."]

    for _ in range(6):

        for d in dots:

            await asyncio.sleep(0.4)

            try:
                await loading_msg.edit_text(
                    f"🎯 choosing someone{d}"
                )

            except Exception:
                pass

    winner = random.choice(names)

    await loading_msg.edit_text(
        f"🏆 **{winner}**",
        parse_mode="Markdown"
    )

    await asyncio.sleep(20)

    try:
        await loading_msg.edit_text(
            f"🏆 **{winner}** 🎉",
            parse_mode="Markdown"
        )

    except Exception:
        pass

    del choose_sessions[chat_id]


# ─────────────────────────────────────────────────────────────
# /xo Game
# ─────────────────────────────────────────────────────────────

xo_games: dict[int, dict] = {}


def make_xo_board(game: dict) -> str:

    board = game["board"]

    e1 = game["p1_emoji"]
    e2 = game["p2_emoji"]

    symbols = {
        1: e1,
        2: e2,
        0: "⬜"
    }

    rows = []

    for i in range(0, 9, 3):

        rows.append(
            " ".join(
                symbols[board[j]]
                for j in range(i, i + 3)
            )
        )

    return "\n".join(rows)


def check_winner(board):

    wins = [
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),
        (0, 4, 8),
        (2, 4, 6)
    ]

    for a, b, c in wins:

        if board[a] and board[a] == board[b] == board[c]:
            return board[a]

    if all(board):
        return "draw"

    return None


def make_xo_keyboard(game):

    board = game["board"]

    buttons = []

    for i in range(0, 9, 3):

        row = []

        for j in range(i, i + 3):

            e = (
                game["p1_emoji"]
                if board[j] == 1
                else (
                    game["p2_emoji"]
                    if board[j] == 2
                    else "⬜"
                )
            )

            row.append(
                InlineKeyboardButton(
                    e,
                    callback_data=f"xo_{game['chat_id']}_{j}"
                )
            )

        buttons.append(row)

    return InlineKeyboardMarkup(buttons)


async def xo_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

    msg = update.message

    chat_id = msg.chat_id

    parts = msg.text.strip().split()

    if len(parts) < 2:

        await msg.reply_text(
            "🎮 Send /xo with your emoji!\n"
            "Example: /xo 🔥"
        )

        return

    emoji = parts[1]

    game = {
        "chat_id": chat_id,

        "p1": msg.from_user.id,
        "p1_name": msg.from_user.full_name,
        "p1_emoji": emoji,

        "p2": None,
        "p2_name": None,
        "p2_emoji": None,

        "board": [0] * 9,

        "turn": 1,

        "msg_id": None,
    }

    xo_games[chat_id] = game

    text = (
        f"🎮 **{msg.from_user.full_name}** {emoji}\n"
        f"Send /xo with your emoji to join!\n"
        f"Example: /xo ❄️"
    )

    sent = await msg.reply_text(
        text,
        parse_mode="Markdown"
    )

    game["msg_id"] = sent.message_id


async def xo_join(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

    msg = update.message

    chat_id = msg.chat_id

    game = xo_games.get(chat_id)

    if not game:
        return await xo_cmd(update, ctx)

    if game["p2"]:

        await msg.reply_text(
            "⚠️ Game already has 2 players!"
        )

        return

    parts = msg.text.strip().split()

    if len(parts) < 2:

        await msg.reply_text(
            "Send /xo with your emoji to join! "
            "Example: /xo ❄️"
        )

        return

    if msg.from_user.id == game["p1"]:

        await msg.reply_text(
            "⚠️ You started this game, "
            "wait for another player!"
        )

        return

    game["p2"] = msg.from_user.id
    game["p2_name"] = msg.from_user.full_name
    game["p2_emoji"] = parts[1]

    text = (
        f"🎮 **{game['p1_name']}** {game['p1_emoji']} VS "
        f"**{game['p2_name']}** {game['p2_emoji']}\n"
        f"Turn: **{game['p1_name']}** {game['p1_emoji']}"
    )

    await msg.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=make_xo_keyboard(game)
    )


async def xo_move(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    data = query.data.split("_")

    chat_id = int(data[1])
    cell = int(data[2])

    game = xo_games.get(chat_id)

    if not game:
        return

    user_id = query.from_user.id
    turn = game["turn"]

    if turn == 1 and user_id != game["p1"]:

        await query.answer(
            "Not your turn!",
            show_alert=True
        )

        return

    if turn == 2 and user_id != game["p2"]:

        await query.answer(
            "Not your turn!",
            show_alert=True
        )

        return

    if game["board"][cell] != 0:

        await query.answer(
            "Cell taken!",
            show_alert=True
        )

        return

    game["board"][cell] = turn

    winner = check_winner(game["board"])

    if winner == "draw":

        board_str = make_xo_board(game)

        await query.edit_message_text(
            f"{board_str}\n\n🤝 It's a Draw!",
            parse_mode="Markdown"
        )

        del xo_games[chat_id]

    elif winner:

        name = (
            game["p1_name"]
            if winner == 1
            else game["p2_name"]
        )

        emoji = (
            game["p1_emoji"]
            if winner == 1
            else game["p2_emoji"]
        )

        board_str = make_xo_board(game)

        await query.edit_message_text(
            f"{board_str}\n\n🏆 **{name}** {emoji} wins!",
            parse_mode="Markdown"
        )

        del xo_games[chat_id]

    else:

        game["turn"] = 2 if turn == 1 else 1

        next_name = (
            game["p1_name"]
            if game["turn"] == 1
            else game["p2_name"]
        )

        next_emoji = (
            game["p1_emoji"]
            if game["turn"] == 1
            else game["p2_emoji"]
        )

        board_str = make_xo_board(game)

        text = (
            f"🎮 **{game['p1_name']}** {game['p1_emoji']} VS "
            f"**{game['p2_name']}** {game['p2_emoji']}\n"
            f"{board_str}\n"
            f"Turn: **{next_name}** {next_emoji}"
        )

        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=make_xo_keyboard(game)
        )


# ─────────────────────────────────────────────────────────────
# //r — Relay / Replace Message
# ─────────────────────────────────────────────────────────────

async def r_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

    msg = update.message

    user_id = msg.from_user.id

    if not has_perm(user_id, "//r"):
        return

    target = msg.reply_to_message

    if not target:

        await msg.reply_text(
            "↩️ Reply to a message with //r [your message]"
        )

        return

    text_parts = msg.text.split(None, 1)

    new_text = (
        text_parts[1]
        if len(text_parts) > 1
        else None
    )

    if not new_text:

        await msg.reply_text(
            "✏️ Add your message after //r"
        )

        return

    chat_id = msg.chat_id

    try:
        await ctx.bot.delete_message(
            chat_id,
            msg.message_id
        )

    except Exception:
        pass

    await ctx.bot.send_message(
        chat_id,
        new_text,
        reply_to_message_id=target.message_id
    )


# ─────────────────────────────────────────────────────────────
# //say — Forward & Tag
# Owner Only | Private Chat Only
# ─────────────────────────────────────────────────────────────

async def say_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

    msg = update.message

    if msg.from_user.id != OWNER_ID:
        return

    if msg.chat.type != "private":
        return

    target = msg.reply_to_message

    if not target:

        await msg.reply_text(
            "↩️ Forward a message here, "
            "reply to it with //say [your text]"
        )

        return

    text_parts = msg.text.split(None, 1)

    new_text = (
        text_parts[1]
        if len(text_parts) > 1
        else None
    )

    if not new_text:

        await msg.reply_text(
            "✏️ Add your message after //say"
        )

        return

    fwd_from = getattr(target, "forward_from", None)

    if fwd_from:

        mention = (
            f"[{fwd_from.full_name}]"
            f"(tg://user?id={fwd_from.id})"
        )

        await msg.reply_text(
            f"{mention} {new_text}",
            parse_mode="Markdown"
        )

    else:
        await msg.reply_text(new_text)


# ─────────────────────────────────────────────────────────────
# //ask — AI via OpenRouter
# ─────────────────────────────────────────────────────────────

import httpx


async def ask_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

    msg = update.message

    text_parts = msg.text.split(None, 1)

    question = (
        text_parts[1]
        if len(text_parts) > 1
        else None
    )

    if not question:

        await msg.reply_text(
            "🤖 Ask me anything!\n"
            "Usage: //ask [your question]"
        )

        return

    thinking = await msg.reply_text(
        "🤔 Thinking..."
    )

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





                    "messages": [
                        {
                            "role": "user",
                            "content": question
                        }
                    ],

                    "max_tokens": 1000,
                }
            )

        data = resp.json()
        if "choices" in data:
            answer = data["choices"][0]["message"]["content"]
        else:
            answer = str(data)



    except Exception as e:

        answer = f"⚠️ Error: {str(e)}"

    await thinking.edit_text(
        f"🤖 {answer}"
    )
# bot.py — Part 3/3

# ─── //add ────────────────────────────────────────────────────────────
VALID_CMDS = {"//info", "//id", "//r", "//ask", "//zaxo", "//say", "//st", "//re"}


async def add_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if msg.from_user.id != OWNER_ID:
        return
    target = msg.reply_to_message
    parts = msg.text.strip().split(None, 1)
    specific_cmd = parts[1].strip() if len(parts) > 1 else None

    # Resolve target user: from reply or from ID/username in arg
    if target:
        u = target.from_user
        target_id = u.id
        target_name = u.full_name
    elif specific_cmd and specific_cmd.lstrip("-").isdigit():
        target_id = int(specific_cmd)
        target_name = str(target_id)
        specific_cmd = None
    else:
        await msg.reply_text("↩️ Reply to a user's message with //add or //add [command]")
        return

    if not target_id:
        return

    if target_id not in admin_perms:
        admin_perms[target_id] = set()

    if specific_cmd is None or specific_cmd == "":
        admin_perms[target_id] = {"all"}
        await msg.reply_text(
            f"🎖️ {target_name} is admin of Zaxoy Bot now 🇵🇱",
            reply_to_message_id=target.message_id if target else None
        )
    elif specific_cmd in VALID_CMDS:
        admin_perms[target_id].add(specific_cmd)
        await msg.reply_text(
            f"✅ {target_name} can use {specific_cmd} now 🇵🇱",
            reply_to_message_id=target.message_id if target else None
        )
    else:
        await msg.reply_text(f"⚠️ Unknown command: {specific_cmd}")

# ─── //remove ────────────────────────────────────────────────────────
async def remove_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if msg.from_user.id != OWNER_ID:
        return
    target = msg.reply_to_message
    parts = msg.text.strip().split(None, 1)
    specific_cmd = parts[1].strip() if len(parts) > 1 else None

    if target:
        u = target.from_user
        target_id = u.id
        target_name = u.full_name
    elif specific_cmd and specific_cmd.lstrip("-").isdigit():
        target_id = int(specific_cmd)
        target_name = str(target_id)
        specific_cmd = None
    else:
        await msg.reply_text("↩️ Reply to a user's message with //remove or //remove [command]")
        return

    perms = admin_perms.get(target_id, set())

    if specific_cmd is None or specific_cmd == "":
        admin_perms.pop(target_id, None)
        await msg.reply_text(
            f"😔 Sadly {target_name} can't use me now 🇵🇱",
            reply_to_message_id=target.message_id if target else None
        )
    elif specific_cmd in perms or "all" in perms:
        if "all" in perms:
            perms = VALID_CMDS.copy()
            perms.discard(specific_cmd)
        else:
            perms.discard(specific_cmd)
        
        if perms:
            admin_perms[target_id] = perms
        else:
            admin_perms.pop(target_id, None)
            
        await msg.reply_text(
            f"🗑️ {target_name}: {specific_cmd} has been removed 🇵🇱",
            reply_to_message_id=target.message_id if target else None
        )
    else:
        await msg.reply_text(f"⚠️ {target_name} didn't have {specific_cmd}")
async def react_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not has_perm(msg.from_user.id, "//re"):
        await msg.reply_text("⛔ You don't have permission 🇵🇱")
        return
    target = msg.reply_to_message
    if not target:
        await msg.reply_text("↩️ Reply to a message with //re [emoji]")
        return
    parts = msg.text.strip().split(None, 1)
    emoji = parts[1].strip() if len(parts) > 1 else None
    if not emoji:
        await msg.reply_text("❌ Send: //re [emoji]")
        return
    try:
        await ctx.bot.delete_message(msg.chat_id, msg.message_id)
    except Exception:
        pass
    try:
        await ctx.bot.set_message_reaction(
            chat_id=msg.chat_id,
            message_id=target.message_id,
            reaction=[ReactionTypeEmoji(emoji=emoji)]


        )
    except Exception as e:
        await msg.reply_text(f"⚠️ {str(e)}")

async def sticker_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    
    if not has_perm(msg.from_user.id, "//st"):
        await msg.reply_text("⛔ You don't have permission 🇵🇱")
        return
        
    parts = msg.text.strip().split(None, 1)
    sticker_id = parts[1].strip() if len(parts) > 1 else None
    
    if not sticker_id:
        await msg.reply_text("❌ Send: //st [file_id]")
        return
        
    target = msg.reply_to_message
    reply_to = target.message_id if target else None
    
    try:
        await ctx.bot.delete_message(msg.chat_id, msg.message_id)
    except Exception:
        pass
        
    await ctx.bot.send_sticker(
        chat_id=msg.chat_id,
        sticker=sticker_id,
        reply_to_message_id=reply_to
    )
# ─── Message router ──────────────────────────────────────────────────
async def message_router(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text:
        return
    text = msg.text.strip()

    # Double-slash commands
    if text.startswith("//info"):
        await info_cmd(update, ctx)
    elif text.startswith("//id"):
        await id_cmd(update, ctx)
    elif text.startswith("//r ") or text == "//r":
        await r_cmd(update, ctx)
    elif text.startswith("//say"):
        await say_cmd(update, ctx)
    elif text.startswith("//ask"):
        await ask_cmd(update, ctx)
    elif text.startswith("//zaxo"):
        await zaxo_msg(update, ctx)
    elif text.startswith("//add"):
        await add_cmd(update, ctx)
    elif text.startswith("//remove"):
        await remove_cmd(update, ctx)
    elif text.startswith("//st"):
        await sticker_cmd(update, ctx)
    elif  text.startswith("//re"):
        await react_cmd(update, ctx)
    
  
    else:
        await zaxo_defense_handler(update, ctx)
        await waleed_protection(update, ctx)
        session = choose_sessions.get(msg.chat_id)
        if session and session.get("step") == "waiting":
            await choose_names_handler(update, ctx)

# ─── /xo handler — start or join ─────────────────────────────────────
async def xo_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in xo_games and xo_games[chat_id]["p2"] is None:
        await xo_join(update, ctx)
    else:
        await xo_cmd(update, ctx)
import re as re_module
from datetime import timedelta, datetime, timezone

def parse_duration(text: str) -> int:
    units = {
        's': 1, 'sec': 1, 'second': 1, 'seconds': 1,
        'm': 60, 'min': 60, 'minute': 60, 'minutes': 60,
        'h': 3600, 'hr': 3600, 'hour': 3600, 'hours': 3600,
        'd': 86400, 'day': 86400, 'days': 86400,
        'w': 604800, 'week': 604800, 'weeks': 604800,
        'mo': 2592000, 'month': 2592000, 'months': 2592000,
        'y': 31536000, 'year': 31536000, 'years': 31536000,
    }
    pattern = r'(\d+)\s*([a-zA-Z]+)'
    matches = re_module.findall(pattern, text.lower())
    total = 0
    for amount, unit in matches:
        if unit in units:
            total += int(amount) * units[unit]
    return total

def format_duration(seconds: int) -> str:
    parts = []
    if seconds >= 31536000:
        y = seconds // 31536000; seconds %= 31536000
        parts.append(f"{y} year{'s' if y > 1 else ''}")
    if seconds >= 2592000:
        mo = seconds // 2592000; seconds %= 2592000
        parts.append(f"{mo} month{'s' if mo > 1 else ''}")
    if seconds >= 604800:
        w = seconds // 604800; seconds %= 604800
        parts.append(f"{w} week{'s' if w > 1 else ''}")
    if seconds >= 86400:
        d = seconds // 86400; seconds %= 86400
        parts.append(f"{d} day{'s' if d > 1 else ''}")
    if seconds >= 3600:
        h = seconds // 3600; seconds %= 3600
        parts.append(f"{h} hour{'s' if h > 1 else ''}")
    if seconds >= 60:
        m = seconds // 60; seconds %= 60
        parts.append(f"{m} minute{'s' if m > 1 else ''}")
    if seconds > 0:
        parts.append(f"{seconds} second{'s' if seconds > 1 else ''}")
    return " and ".join(parts) if parts else "0 seconds"

MUTE_MESSAGES = [
    "🔇 {name} has been silenced in Zaxo's domain for {duration}. The city speaks — you don't. 🇵🇱",
    "⛓️ {name} is now muted for {duration}. Zaxo's law has been enforced. 🇵🇱",
    "🚫 {name} — {duration} of silence. Zaxo does not tolerate noise. 🇵🇱",
    "🌑 {name} has entered the shadow zone for {duration}. Not a word. 🇵🇱",
    "⚔️ {name} has been struck silent for {duration} by order of Zaxoy Bot. 🇵🇱",
]

async def mute_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not has_perm(msg.from_user.id, "//mute"):
        await msg.reply_text("⛔ You don't have permission 🇵🇱")
        return

    text_parts = msg.text.strip().split(None, 1)
    args = text_parts[1].strip() if len(text_parts) > 1 else ""

    target_user = None
    target_id = None
    duration_text = args

    # Check if replying to a message
    if msg.reply_to_message:
        target_user = msg.reply_to_message.from_user
        target_id = target_user.id
        duration_text = args

    # Check if @username or ID provided
    elif args:
        parts = args.split(None, 1)
        identifier = parts[0]
        duration_text = parts[1] if len(parts) > 1 else ""

        if identifier.startswith("@"):
            try:
                member = await ctx.bot.get_chat_member(msg.chat_id, identifier)
                target_user = member.user
                target_id = target_user.id
            except Exception:
                await msg.reply_text("⚠️ User not found")
                return
        elif identifier.lstrip("-").isdigit():
            target_id = int(identifier)
            try:
                member = await ctx.bot.get_chat_member(msg.chat_id, target_id)
                target_user = member.user
            except Exception:
                await msg.reply_text("⚠️ User not found")
                return

    # If no duration — show remaining mute time
    if target_id and not duration_text.strip():
        try:
            member = await ctx.bot.get_chat_member(msg.chat_id, target_id)
            until = getattr(member, "until_date", None)
            if until:
                now = datetime.now(timezone.utc)
                remaining = int((until - now).total_seconds())
                if remaining > 0:
                    await msg.reply_text(
                        f"🔇 {target_user.full_name} is muted for {format_duration(remaining)} more. 🇵🇱"
                    )
                else:
                    await msg.reply_text(f"✅ {target_user.full_name} is not muted. 🇵🇱")
            else:
                await msg.reply_text(f"✅ {target_user.full_name} is not muted. 🇵🇱")
        except Exception as e:
            await msg.reply_text(f"⚠️ {str(e)}")
        return

    if not target_id:
        await msg.reply_text("↩️ Reply to a message or provide @username / ID\nExample: //mute @user 1h")
        return

    seconds = parse_duration(duration_text)
    if seconds == 0:
        await msg.reply_text("❌ Invalid duration. Example: //mute 1h 30m")
        return

    until = datetime.now(timezone.utc) + timedelta(seconds=seconds)

    try:
        await ctx.bot.restrict_chat_member(
            chat_id=msg.chat_id,
            user_id=target_id,
            permissions={"can_send_messages": False},
            until_date=until
        )
        try:
            await ctx.bot.delete_message(msg.chat_id, msg.message_id)
        except Exception:
            pass
        duration_str = format_duration(seconds)
        mute_text = random.choice(MUTE_MESSAGES).format(
            name=target_user.full_name if target_user else str(target_id),
            duration=duration_str
        )
        reply_to = msg.reply_to_message.message_id if msg.reply_to_message else None
        await ctx.bot.send_message(
            msg.chat_id,
            mute_text,
            reply_to_message_id=reply_to
        )
    except Exception as e:
        await msg.reply_text(f"⚠️ {str(e)}")


async def unmute_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not has_perm(msg.from_user.id, "//mute"):
        await msg.reply_text("⛔ You don't have permission 🇵🇱")
        return

    target_user = None
    target_id = None

    if msg.reply_to_message:
        target_user = msg.reply_to_message.from_user
        target_id = target_user.id
    else:
        text_parts = msg.text.strip().split(None, 1)
        if len(text_parts) > 1:
            identifier = text_parts[1].strip()
            if identifier.startswith("@"):
                try:
                    member = await ctx.bot.get_chat_member(msg.chat_id, identifier)
                    target_user = member.user
                    target_id = target_user.id
                except Exception:
                    await msg.reply_text("⚠️ User not found")
                    return
            elif identifier.lstrip("-").isdigit():
                target_id = int(identifier)
                try:
                    member = await ctx.bot.get_chat_member(msg.chat_id, target_id)
                    target_user = member.user
                except Exception:
                    pass

    if not target_id:
        await msg.reply_text("↩️ Reply to a message or provide @username / ID")
        return

    try:
        from telegram import ChatPermissions
        await ctx.bot.restrict_chat_member(
            chat_id=msg.chat_id,
            user_id=target_id,
            permissions=ChatPermissions(can_send_messages=True)
        )
        try:
            await ctx.bot.delete_message(msg.chat_id, msg.message_id)
        except Exception:
            pass
        name = target_user.full_name if target_user else str(target_id)
        await ctx.bot.send_message(
            msg.chat_id,
            f"✅ {name} has been unmuted. Welcome back to Zaxo 🇵🇱"
        )
    except Exception as e:
        await msg.reply_text(f"⚠️ {str(e)}")

# ─── Main ────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Slash commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("on", on_cmd))
    app.add_handler(CommandHandler("off", off_cmd))
    app.add_handler(CommandHandler("choose", choose_cmd))
    app.add_handler(CommandHandler("xo", xo_handler))

    # Inline keyboard callbacks
    app.add_handler(CallbackQueryHandler(copy_callback, pattern=r"^copy_"))
    app.add_handler(CallbackQueryHandler(xo_move, pattern=r"^xo_"))

    # All text messages (handles // commands + protections + choose input)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_router))

    print("🤖 Zaxoy Bot is running... 🇵🇱")
    app.run_polling()

if __name__ == "__main__":
    main()
