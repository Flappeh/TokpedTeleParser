from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler, CallbackContext, ConversationHandler, Defaults
from modules.environment import BOT_USERNAME,TOKEN
from typing import List
import datetime
from modules.utils import get_logger
from modules.tokped import start_item_search
import pytz

logger = get_logger(__name__)
# Commands

PRODUCT_NAME, MIN_PRICE, MAX_PRICE, CONFIRM = range(4)

def check_time(update: Update) -> bool:
    if update.message.date.timestamp() < datetime.datetime.now().timestamp() - 600:
        return True
    return False

def validate_price(data: str):
    try:
        val = int(data)
        return True, val
    except:
        return False, None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if check_time(update):
        return
    await update.message.reply_text("""
*Tokped Notifier Bot*

Command yang dapat dilakukan:

/help \\-\\> Show command ini

/add\\_item \\-\\> Tambah item ke list yang dimonitor

/list\\_job \\-\\> List semua item yang sedang di cari

/stop *<job\\-name\\>*  \\-\\> Stop pencarian item berdasarkan nama job yang berjalan
""",
    parse_mode=ParseMode.MARKDOWN_V2)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Help text")
    else:
        if check_time(update):
            return
        await update.message.reply_text("""
*Tokped Notifier Bot*

Command yang dapat dilakukan:

/help \\-\\> Show command ini

/add\\_item \\-\\> Tambah item ke list yang dimonitor

/list\\_job \\-\\> List semua item yang sedang di cari

/stop *<job\\-name\\>*  \\-\\> Stop pencarian item berdasarkan nama job yang berjalan
""",
    parse_mode=ParseMode.MARKDOWN_V2)

async def item_start_command(update: Update, context:CallbackContext):
    if check_time(update):
        return
    await update.message.reply_text("Masukkan nama item yang mau dicari")
    return PRODUCT_NAME

async def item_get_name(update: Update, context: CallbackContext) -> int:
    data = update.message.text
    context.user_data['product_name'] = data
    await update.message.reply_text(f"Minimum price untuk item {data}")
    return MIN_PRICE

async def item_get_min_price(update: Update, context: CallbackContext) -> int:
    result,value = validate_price(update.message.text)
    if result == False:
        await update.message.reply_text("Masukkan angka dalam range 0-9")
        return MIN_PRICE
    context.user_data['min_price'] = value
    await update.message.reply_text("Masukkan harga maksimum")
    return MAX_PRICE
    

async def item_get_max_price(update: Update, context: CallbackContext) -> int:
    result,value = validate_price(update.message.text)
    if result == False:
        await update.message.reply_text("Masukkan angka dalam range 0-9")
        return MAX_PRICE
    elif value < context.user_data['min_price']:
        await update.message.reply_text("Harga maximum tidak dapat lebih kecil dari harga minimum!")
        return MAX_PRICE
    context.user_data['max_price'] = value
    await update.message.reply_text(f"""
Summary:

Nama : {context.user_data['product_name']}
Min price : {context.user_data['min_price']:,}
Max Price : {context.user_data['max_price']:,}

apakah data sudah benar? (y/n)
""")
    return CONFIRM

async def item_confirm_choices(update: Update, context: CallbackContext):
    data = update.message.text
    if data.lower() != 'y' and data.lower() != 'n':
        await update.message.reply_text("Reply dengan membalas y/n")
        return CONFIRM
    await update.message.reply_text("Mulai proses produk")
    start_item_search(context.user_data)
    return ConversationHandler.END

# Responses


async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Pendaftaran item di cancel")
    return ConversationHandler.END

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
    builder = Application.builder()
    builder.token(TOKEN)
    builder.defaults(Defaults(tzinfo=pytz.timezone('Asia/Jakarta')))
    app = builder.build()
    logger.info("INITIALIZING Tokped Parser Bot")
    
    # Conv handler
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add_item', item_start_command)],
        states={
            PRODUCT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, item_get_name)],
            MIN_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, item_get_min_price)],
            MAX_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, item_get_max_price)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, item_confirm_choices)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    
    # Command
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(conv_handler)
    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    # Errors
    app.add_error_handler(handle_error)
    
    logger.info("BOT RUNNING")
    app.run_polling(poll_interval=3)
    