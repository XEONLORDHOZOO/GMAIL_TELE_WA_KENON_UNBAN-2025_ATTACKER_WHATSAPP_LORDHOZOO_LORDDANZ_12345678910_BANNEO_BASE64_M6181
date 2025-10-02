#AUTHOR LORDHOZOO
# RECORD LAMMER KONTOLL 
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import os
import google.auth
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime
import requests

# --- Fungsi Email Anda (Tetap Sama) ---
def send_email(to_address, subject, body, from_address="hozoowarnet@gmail.com"):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    from_email = from_address

    # Load credentials
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/gmail.send'])
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', ['https://www.googleapis.com/auth/gmail.send'])
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    from_password = creds.token  # Use the access token for authentication

    message = MIMEMultipart()
    message['From'] = from_email
    message['To'] = to_address
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(from_email, from_password)
        server.sendmail(from_email, to_address, message.as_string())
        return "Email berhasil dikirim!"
    except Exception as e:
        return f"Gagal mengirim email: {e}"
    finally:
        server.quit()

# --- Handler untuk Perintah Bot ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Cek Cuaca", callback_data='weather')],
        [InlineKeyboardButton("Tampilkan Gambar", callback_data='photo')],
        [InlineKeyboardButton("Cek Waktu", callback_data='time')],
        [InlineKeyboardButton("Cek Tanggal", callback_data='date')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Halo! Silahkan pilih opsi di bawah:',
                                    reply_markup=reply_markup)

async def send_email_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Misalnya: /send_email 628123456789
    if not context.args:
        await update.message.reply_text('Format: /send_email <nomor_telepon>')
        return

    phone_number = context.args[0]
    to_address = "support@whatsapp.com"
    subject = "Hai WhatsApp Android"
    body = f"Tolong di pilih akun saya dengan nomor {phone_number}"

    result = send_email(to_address, subject, body)
    await update.message.reply_text(result)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'weather':
        weather_info = get_weather()
        await query.edit_message_text(text=f"Cuaca hari ini: {weather_info}")
    elif query.data == 'photo':
        await query.edit_message_media(media=InputMediaPhoto(media='hozoo.jpg'))
    elif query.data == 'time':
        current_time = datetime.now().strftime("%H:%M:%S")
        await query.edit_message_text(text=f"Waktu saat ini: {current_time}")
    elif query.data == 'date':
        current_date = datetime.now().strftime("%Y-%m-%d")
        await query.edit_message_text(text=f"Tanggal saat ini: {current_date}")

def get_weather():
    # Replace 'your_city' with the desired city
    city = 'your_city'
    api_key = 'your_openweathermap_api_key'
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    response = requests.get(url)
    data = response.json()
    return f"{data['weather'][0]['description']}, Suhu: {data['main']['temp']}°C"

# --- Main Function ---
def main():
    # Ganti 'TOKEN_BOT_ANDA' dengan token yang dari BotFather
    application = Application.builder().token("TOKEN_BOT_ANDA").build()

    # Tambahkan handler untuk command
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("send_email", send_email_command))
    application.add_handler(CallbackQueryHandler(button))

    print("Bot sedang berjalan...")
    application.run_polling()

if __name__ == '__main__':
    main()
