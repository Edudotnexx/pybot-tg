import random
import sqlite3
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Database setup
conn = sqlite3.connect('config_bot.db', check_same_thread=False)
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS configs (
    id INTEGER PRIMARY KEY,
    code TEXT NOT NULL,
    usage_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    is_admin BOOLEAN DEFAULT 0,
    blocked BOOLEAN DEFAULT 0
)
''')

conn.commit()

# Welcome message
WELCOME_MESSAGE = "👋 خوش آمدید به ربات مدیریت کانفیگ!\n\n" \
                  "این ربات به شما امکان می‌دهد تا کانفیگ‌ها را مدیریت کنید. " \
                  "دستور‌های زیر را امتحان کنید:\n" \
                  "/add_config <کد کانفیگ> - افزودن کانفیگ جدید\n" \
                  "/remove_config <کد کانفیگ> - حذف کانفیگ\n" \
                  "/list_configs - لیست کانفیگ‌ها\n" \
                  "/get_config - دریافت کانفیگ تصادفی\n" \
                  "/status <کد کانفیگ> - بررسی وضعیت کانفیگ\n" \
                  "/login - ورود به عنوان ادمین\n" \
                  "/block_user <آیدی کاربر> - بلاک کردن کاربر\n" \
                  "/unblock_user <آیدی کاربر> - آنبلاک کردن کاربر\n"

# Command Handlers
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(WELCOME_MESSAGE)

def add_config(update: Update, context: CallbackContext) -> None:
    if context.user_data.get('is_admin'):
        code = context.args[0] if context.args else None
        if code:
            cursor.execute("INSERT INTO configs (code, created_at) VALUES (?, datetime('now'))", (code,))
            conn.commit()
            update.message.reply_text(f"✅ کانفیگ '{code}' با موفقیت افزوده شد.")
        else:
            update.message.reply_text("❌ لطفا کد کانفیگ را وارد کنید.")
    else:
        update.message.reply_text("❌ شما اجازه دسترسی ندارید.")

def remove_config(update: Update, context: CallbackContext) -> None:
    if context.user_data.get('is_admin'):
        code = context.args[0] if context.args else None
        if code:
            cursor.execute("DELETE FROM configs WHERE code = ?", (code,))
            conn.commit()
            update.message.reply_text(f"✅ کانفیگ '{code}' با موفقیت حذف شد.")
        else:
            update.message.reply_text("❌ لطفا کد کانفیگ را وارد کنید.")
    else:
        update.message.reply_text("❌ شما اجازه دسترسی ندارید.")

def list_configs(update: Update, context: CallbackContext) -> None:
    cursor.execute("SELECT code FROM configs")
    configs = cursor.fetchall()
    if configs:
        response = "📜 لیست کانفیگ‌ها:\n" + "\n".join([config[0] for config in configs])
        update.message.reply_text(response)
    else:
        update.message.reply_text("❌ هیچ کانفیگی وجود ندارد.")

def get_config(update: Update, context: CallbackContext) -> None:
    cursor.execute("SELECT code FROM configs")
    configs = cursor.fetchall()
    if configs:
        selected_config = random.choice(configs)[0]
        user_id = update.message.from_user.id
        cursor.execute("UPDATE configs SET usage_count = usage_count + 1 WHERE code = ?", (selected_config,))
        conn.commit()
        update.message.reply_text(f"🔑 کانفیگ شما: {selected_config}\n🆔 آیدی شما: {user_id}")
    else:
        update.message.reply_text("❌ هیچ کانفیگی وجود ندارد.")

def status(update: Update, context: CallbackContext) -> None:
    code = context.args[0] if context.args else None
    if code:
        cursor.execute("SELECT usage_count, created_at FROM configs WHERE code = ?", (code,))
        result = cursor.fetchone()
        if result:
            usage_count, created_at = result
            update.message.reply_text(f"📊 وضعیت کانفیگ '{code}':\n🔢 تعداد استفاده: {usage_count}\n🗓️ تاریخ ایجاد: {created_at}")
        else:
            update.message.reply_text("❌ کانفیگ وجود ندارد.")
    else:
        update.message.reply_text("❌ لطفا کد کانفیگ را وارد کنید.")

def login(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if user and user[2]:
        context.user_data['is_admin'] = True
        update.message.reply_text("✅ شما به عنوان ادمین وارد شدید.")
    else:
        update.message.reply_text("❌ شما ادمین نیستید.")

def block_user(update: Update, context: CallbackContext) -> None:
    if context.user_data.get('is_admin'):
        user_id = context.args[0] if context.args else None
        if user_id:
            cursor.execute("UPDATE users SET blocked = 1 WHERE id = ?", (user_id,))
            conn.commit()
            update.message.reply_text(f"✅ کاربر با آیدی {user_id} بلاک شد.")
        else:
            update.message.reply_text("❌ لطفا آیدی کاربر را وارد کنید.")
    else:
        update.message.reply_text("❌ شما اجازه دسترسی ندارید.")

def unblock_user(update: Update, context: CallbackContext) -> None:
    if context.user_data.get('is_admin'):
        user_id = context.args[0] if context.args else None
        if user_id:
            cursor.execute("UPDATE users SET blocked = 0 WHERE id = ?", (user_id,))
            conn.commit()
            update.message.reply_text(f"✅ کاربر با آیدی {user_id} آنبلاک شد.")
        else:
            update.message.reply_text("❌ لطفا آیدی کاربر را وارد کنید.")
    else:
        update.message.reply_text("❌ شما اجازه دسترسی ندارید.")

def main() -> None:
    updater = Updater("595966727:AAElzWidMnjFEQ4j6Ovvj31JusLalzsRBnA")
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("add_config", add_config))
    dispatcher.add_handler(CommandHandler("remove_config", remove_config))
    dispatcher.add_handler(CommandHandler("list_configs", list_configs))
    dispatcher.add_handler(CommandHandler("get_config", get_config))
    dispatcher.add_handler(CommandHandler("status", status))
    dispatcher.add_handler(CommandHandler("login", login))
    dispatcher.add_handler(CommandHandler("block_user", block_user))
    dispatcher.add_handler(CommandHandler("unblock_user", unblock_user))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
