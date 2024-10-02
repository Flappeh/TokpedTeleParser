from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
from modules.environment import BOT_USERNAME,TOKEN
from typing import List
import datetime
from modules.utils import get_logger

logger = get_logger(__name__)
# Commands

def check_time(update: Update) -> bool:
    if update.message.date.timestamp() < datetime.datetime.now().timestamp() - 600:
        return True
    return False

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if check_time(update):
        return
    await update.message.reply_text("""
*Tokped Notifier Bot*

Command yang dapat dilakukan:

/help \\-\\> Show command ini

/add\\_item \\-\\> Tambah item ke list yang dimonitor

/list\\_job \\-\\> List semua item yang sedang di

/change \\-\\> *Ganti user* Pi Account
""",
    parse_mode=ParseMode.MARKDOWN_V2)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Help text")
    else:
        if check_time(update):
            return
        await update.message.reply_text("""
*Pi Wallet Bot*

Command yang dapat dilakukan:

/help \\-\\> Show command ini

/phrase *<24\\-phrase\\>* \\-\\> Perintah bot untuk search wallet berdasarkan 24 word phrase

/wallet *<public\\-key\\>* \\-\\> Perintah bot untuk search wallet berdasarkan public key

/change \\-\\> *Ganti user* Pi Account
""",
    parse_mode=ParseMode.MARKDOWN_V2)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    await query.answer()
        
    try:
        await query.delete_message()
        match query.data:
            case "check_wallet":
                await from_wallet_command(update=update, context=context)
            case "check_phrase":
                await from_passphrase_command(update=update, context=context)
            case "help":
                await help_command(update=update, context=context)
            case _:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Unknown Command")
    except Exception as e:
        logger.error(f"Error running command after button with identifier {query.data} is clicked!, detail: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Error occurred")

async def from_wallet_helper(update: Update, context: ContextTypes.DEFAULT_TYPE, wallet_key: List[str]):
    if len(wallet_key) != 1:
            await update.message.reply_text("Mohon masukkan hanya satu wallet per transaksi")
            return
    key = wallet_key[0]
    try:
        data = get_balance_from_public_key(key)
        if not data:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="None")
            return
        await context.bot.send_message(chat_id=update.effective_chat.id, text=data)
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=str(e))
     
async def from_wallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = ""
    if update.callback_query:
        
        query = update.callback_query
        await query.answer()
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Masukkan public key wallet yang ingin di cari")
        
        print("Callback query received:", query.data)
        data = query.data.split()
    else:
        if check_time(update):
            return
        data = context.args    
    await from_wallet_helper(update,context,data)
        
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")    

async def proses_phrase(proses_message, context: ContextTypes.DEFAULT_TYPE, phrase: str) -> str:
    try:
        data = start_bot_phrase_process(phrase)
        if "Invalid" in data:
            return "Phrase yang dikirim invalid!"
        if "timeout" in data:
            return "Timeout limit telah tercapai, mohon request ulang!"
        elif "Error butuh ganti ke user lain" in data:
            await context.bot.edit_message_text(text=f"Limit user tercapai, proses ganti user",chat_id=proses_message.chat_id,message_id=proses_message.id)
            data = start_phrase_process_after_error(phrase)
            return f"""
*Pi Wallet Bot*

*Phrase*: 
{phrase}

*Jumlah wallet*: 
{data}
        """
        else:
            return f"""
*Pi Wallet Bot*

*Phrase*: 
{phrase}

*Jumlah wallet*: 
{data}
        """
    except Exception as e:
        logger.error(f"Error retrieving passphrase details, {e}")
        return "Error occured, please contact administrator"


async def from_passphrase_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if check_time(update):
        return
    phrase: List[str] = context.args
    if len(phrase) != 24:
        await update.message.reply_text("Passphrase harus 24 kata!")
        return
    phrase = ' '.join(phrase)
    proses_message = await update.message.reply_text("Sedang memproses request...",reply_to_message_id=update.message.id)
    data = await proses_phrase(proses_message,context,phrase)
    data = data.replace('.', '\\.').replace('!','\\!')
    await context.bot.edit_message_text(
        text=data,
        chat_id=proses_message.chat_id,
        message_id=proses_message.id,
        parse_mode=ParseMode.MARKDOWN_V2
    )
    

# async def print_page_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     if check_time(update):
#         return
#     proses_message = await update.message.reply_text("Sedang memproses request...",reply_to_message_id=update.message.id) 
#     try:
#         bot = AndroidBot()
#         data = bot.print_current_page()
#         print(data)
#         await context.bot.edit_message_text(text=f"Done",chat_id=proses_message.chat_id,message_id=proses_message.id)
#     except Exception as e:
#         await update.message.reply_text("Error occured, please contact administrator")
#         logger.error(f"Error retrieving passphrase details, {e}")

async def change_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if check_time(update):
        return
    proses_message = await update.message.reply_text("Sedang memproses request...",reply_to_message_id=update.message.id) 
    try:
        data = await start_change_user_process()
        if data == "timeout":            
            return "Timeout limit telah tercapai, mohon request ulang!"
        await context.bot.edit_message_text(text=f"Done Processing",chat_id=proses_message.chat_id,message_id=proses_message.id)
    except Exception as e:
        await update.message.reply_text("Error occured, please contact administrator")
        logger.error(f"Error retrieving passphrase details, {e}")

# Responses

def handle_response(text: str) -> str:
    # This is the logic for processing the request
    string_content: str = text.lower()
    
    if 'hello' in string_content:
        return "Hello"
    if 'test' in string_content:
        return "Test triggered"
    return "Nothing known"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if check_time(update):
        return
    message_type: str = update.message.chat.type # Group or Private Chat
    text: str = update.message.text
    
    print(f"User: ({update.message.chat.id}) in {message_type} sent: {text}")
    
    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else: 
        response: str = handle_response(text)
    
    print('Bot ', response )
    await update.message.reply_text(response)
    

async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error : {context.error}")
    

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    logger.info("INITIALIZING Telegram Pi Wallet Bot")
    # Command
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('wallet', from_wallet_command))
    app.add_handler(CommandHandler('phrase', from_passphrase_command))
    app.add_handler(CommandHandler('change', change_user_command))
    # app.add_handler(CommandHandler('print', print_page_command))
    app.add_handler(CallbackQueryHandler(button))
    
    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    # Errors
    app.add_error_handler(handle_error)
    
    logger.info("BOT RUNNING")
    app.run_polling(poll_interval=3)
    