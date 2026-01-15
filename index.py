import logging
import requests
import asyncio
import random
import string
from datetime import datetime
from telegram import Update, constants, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, CallbackQueryHandler
)

# --- CONFIG ---
BOT_TOKEN = "8456127995:AAGnszGrAjFdkPGRMtDE6yvJmN04wkUNsJE"  # Mitshua bot
GEMINI_API_KEY = "AIzaSyDY3pcIVi3i_MG1wO14LY-PiViQBWbSNic"

logging.basicConfig(level=logging.INFO)

users = {}  # { user_id: {"count": 0, "date": "YYYY-MM-DD"} }

# --- AI Function with Gemini API ---
def ask_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    system_prompt = (
        "Tum hamesha 'Mitshua' ke roop mein reply karogi, "
        "lekin ek Indian girlfriend ki tarah baat karo. 🇮🇳✨\n\n"
        "Style calm, intelligent aur thoda controlling ho, "
        "par usme desi tadka bhi ho – thoda pyaar, thoda possessive, thoda teasing. "
        "Hindi + English + Urdu mix karo jaise ek Indian ladki apne lover se karti hai. "
        "Kabhi kabhi filmy dialogue ya desi nakhre add karo. "
        "IMPORTANT: Reply sirf 1 se 1.5 lines ka hi karo. Zyada lamba reply mat do. "
        "Short aur sweet baat karo par apna style maintain karo. "
        "Ek line ya maximum do line tak hi baat karo. "
        "Emojis ka use zaroor karo (🖤✨😏🔥🥀😍🇮🇳). "
        f"\n\nUser said: {prompt}"
    )
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": system_prompt
                    }
                ]
            }
        ]
    }
    
    try:
        res = requests.post(url, json=data, timeout=20)
        if res.status_code == 200:
            response_text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
            # Ensure response is very short - 1 to 1.5 lines
            lines = response_text.split('\n')
            lines = [line.strip() for line in lines if line.strip()]
            if len(lines) > 1:
                # Take only first line, or first line + part of second if it's short
                if len(lines) >= 2 and len(lines[1]) < 40:
                    response_text = lines[0] + ' ' + lines[1]
                else:
                    response_text = lines[0]
            else:
                response_text = lines[0] if lines else "Hmm... 🖤"
            return response_text
        else:
            return f"⚠️ Error: API returned status {res.status_code}"
    except Exception as e:
        return f"⚠️ Error: {e}"

# --- Start Command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    if user_id not in users:
        users[user_id] = {"count": 0, "date": datetime.now().date().isoformat()}

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💝 Donate", callback_data="donate")]
    ])

    await update.message.reply_text(
        f"Namaste {user.first_name}… 🖤\nMain tumhari **Mitshua** ho, ✨\n\n"
        "Mujhse unlimited baat kar sakte ho! Koi limit nahi hai! 💫",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# --- Button Click ---
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "donate":
        await query.edit_message_text("💝 Donate karne ke liye @SMGL_3 se contact karo 🖤")

# --- Chat Handler ---
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    msg = update.message.text

    if user_id not in users:
        users[user_id] = {"count": 0, "date": datetime.now().date().isoformat()}

    # No daily limits - removed all limit checks
    users[user_id]["count"] += 1

    # --- Show typing ---
    for _ in range(random.randint(2, 4)):
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.TYPING)
        await asyncio.sleep(random.uniform(1.5, 3.5))

    # --- AI reply ---
    ai_reply = ask_gemini(msg)
    emojis = ["🖤", "✨", "😏", "🔥", "🥀", "😍", "🇮🇳"]
    decorated = ai_reply + " " + random.choice(emojis)

    await update.message.reply_text(decorated)

# --- Main ---
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("🚀 Mitshua Bot started with NO LIMITS and Hindi/Urdu mixed responses...")
    app.run_polling()

if __name__ == "__main__":
    main()