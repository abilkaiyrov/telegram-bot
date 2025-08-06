from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import gspread
import re
from google.oauth2.service_account import Credentials

SPREADSHEET_ID = '1RdI7R0XJp7efHG3FRnXczplw6SdqlafUh5Y3ZnPtFs4'
creds = Credentials.from_service_account_file('credentials.json', scopes=['https://www.googleapis.com/auth/spreadsheets'])
client = gspread.authorize(creds)

def ensure_task3_worksheet():
    sheet = client.open_by_key(SPREADSHEET_ID)
    try:
        worksheet = sheet.worksheet("Задача 3")
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title="Задача 3", rows="100", cols="2")
        worksheet.append_row(["Email", "Отправитель"])
    return worksheet

worksheet = ensure_task3_worksheet()

def is_valid_email(text):
    return re.match(r"[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+", text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text.strip()
    if is_valid_email(text):
        worksheet.append_row([text, user.username or user.first_name])
        await update.message.reply_text(f"Email '{text}' сохранён.")
    else:
        await update.message.reply_text("Это не похоже на email.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет. Просто отправь email, и я сохраню его в таблицу.\n"
        "/list — последние 5 email-ов\n"
        "/clear — очистить все email-ы"
    )

async def list_emails(update: Update, context: ContextTypes.DEFAULT_TYPE):
    values = worksheet.get_all_values()[1:]
    if not values:
        await update.message.reply_text("Email-ов пока нет.")
        return
    last = values[-5:]
    message = "\n".join([f"{row[0]} — {row[1]}" for row in last])
    await update.message.reply_text(f"Последние email-ы:\n{message}")

async def clear_emails(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        values = worksheet.get_all_values()
        if len(values) > 1:
            worksheet.batch_clear(['A2:B1000'])
        await update.message.reply_text("Все email-ы удалены из таблицы.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при очистке: {str(e)}")

app = ApplicationBuilder().token("8324672074:AAFbiA2EgAG1QXIwCGrzD08xF7F2imNVRZA").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("list", list_emails))
app.add_handler(CommandHandler("clear", clear_emails))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Бот запущен...")
app.run_polling()
