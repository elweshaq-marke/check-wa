import asyncio
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "7598031263:AAEnkrP-mQszjK9pStiLslCtOnKxAoS91UY"
ADMIN_ID = 7011309417
API_URL = "http://localhost:5000"
WHATSAPP_URL = "http://localhost:3000"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Unauthorized access. This bot is for admin only.")
        return
    
    keyboard = [
        [InlineKeyboardButton("📊 Statistics", callback_data="stats")],
        [InlineKeyboardButton("✅ Check Number", callback_data="check")],
        [InlineKeyboardButton("📤 Upload Session", callback_data="upload")],
        [InlineKeyboardButton("🔐 Create Session", callback_data="create")],
        [InlineKeyboardButton("📡 Server Status", callback_data="status")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🤖 *WhatsApp Checker Bot*\n\n"
        "Welcome Admin! Choose an option:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await query.edit_message_text("⛔ Unauthorized access.")
        return
    
    if query.data == "stats":
        await show_stats(query)
    elif query.data == "check":
        await query.edit_message_text("📱 Send me the phone number with country code to check.\n\nExample: +1234567890")
        context.user_data['waiting_for'] = 'phone_number'
    elif query.data == "upload":
        await query.edit_message_text("📤 Send me the session file (creds.json)")
        context.user_data['waiting_for'] = 'session_file'
    elif query.data == "create":
        await query.edit_message_text("🔐 Send me the phone number with country code to create a session.\n\nExample: +1234567890")
        context.user_data['waiting_for'] = 'pairing_code'
    elif query.data == "status":
        await show_status(query)

async def show_stats(query):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}/stats") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    message = (
                        f"📊 *Server Statistics*\n\n"
                        f"✅ Total Checks: {data['total_checks']}\n"
                        f"📱 Registered: {data['registered']}\n"
                        f"❌ Not Registered: {data['not_registered']}\n"
                        f"⚠️ Errors: {data['errors']}\n"
                        f"⏱️ Uptime: {data['uptime_formatted']}\n"
                    )
                    
                    keyboard = [[InlineKeyboardButton("🔄 Refresh", callback_data="stats")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
                else:
                    await query.edit_message_text("❌ Failed to get statistics")
    except Exception as e:
        await query.edit_message_text(f"❌ Error: {str(e)}")

async def show_status(query):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}/whatsapp-status") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    status_icon = "🟢" if data.get('connected') else "🔴"
                    status_text = "Connected" if data.get('connected') else "Disconnected"
                    
                    message = (
                        f"📡 *WhatsApp Server Status*\n\n"
                        f"{status_icon} Status: {status_text}\n"
                        f"📱 Has QR: {'Yes' if data.get('hasQR') else 'No'}\n"
                        f"🔐 Has Pairing Code: {'Yes' if data.get('hasPairingCode') else 'No'}\n"
                    )
                    
                    keyboard = [[InlineKeyboardButton("🔄 Refresh", callback_data="status")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
                else:
                    await query.edit_message_text("❌ WhatsApp server unavailable")
    except Exception as e:
        await query.edit_message_text(f"❌ Error: {str(e)}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Unauthorized access.")
        return
    
    waiting_for = context.user_data.get('waiting_for')
    
    if waiting_for == 'phone_number':
        phone = update.message.text.strip()
        await check_number(update, phone)
        context.user_data['waiting_for'] = None
    
    elif waiting_for == 'pairing_code':
        phone = update.message.text.strip()
        await create_session(update, phone)
        context.user_data['waiting_for'] = None

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Unauthorized access.")
        return
    
    waiting_for = context.user_data.get('waiting_for')
    
    if waiting_for == 'session_file':
        await upload_session(update, context)
        context.user_data['waiting_for'] = None

async def check_number(update: Update, phone: str):
    try:
        await update.message.reply_text(f"🔍 Checking {phone}...")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_URL}/check",
                json={"phoneNumber": phone}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    status = data.get('status', 'unknown')
                    
                    if 'registered' in status.lower():
                        await update.message.reply_text(f"✅ {phone} is *registered* on WhatsApp", parse_mode='Markdown')
                    else:
                        await update.message.reply_text(f"❌ {phone} is *not registered* on WhatsApp", parse_mode='Markdown')
                else:
                    error = await response.text()
                    await update.message.reply_text(f"❌ Error: {error}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def create_session(update: Update, phone: str):
    try:
        await update.message.reply_text(f"🔐 Creating session for {phone}...")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_URL}/create-session",
                json={"phoneNumber": phone}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    code = data.get('pairingCode', 'N/A')
                    
                    await update.message.reply_text(
                        f"✅ *Pairing Code Generated*\n\n"
                        f"📱 Phone: {phone}\n"
                        f"🔐 Code: `{code}`\n\n"
                        f"Enter this code in WhatsApp on your phone.",
                        parse_mode='Markdown'
                    )
                else:
                    error = await response.text()
                    await update.message.reply_text(f"❌ Error: {error}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def upload_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        document = update.message.document
        file = await document.get_file()
        
        file_data = await file.download_as_bytearray()
        
        await update.message.reply_text("📤 Uploading session...")
        
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('session_file', file_data, filename=document.file_name)
            
            async with session.post(f"{API_URL}/upload-session", data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    await update.message.reply_text("✅ Session uploaded successfully!")
                else:
                    error = await response.text()
                    await update.message.reply_text(f"❌ Upload failed: {error}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception while handling an update: {context.error}")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_error_handler(error_handler)
    
    print("🤖 Telegram Bot started...")
    print(f"Admin ID: {ADMIN_ID}")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
