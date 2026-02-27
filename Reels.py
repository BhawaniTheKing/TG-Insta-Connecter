import os, json, asyncio, base64
from datetime import datetime
from instagrapi import Client
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Configuration ---
Instagram_Username = "satya.dynasty"
Telegram_Token = "8677114145:AAFeHE3zjzDj19ET1bpTejBS9EXdR5WPaGM"
Target_Group_Id = -1003830400479
User_Database_Path = "Users_Registry.json"

Ig_Bot = Client()

def Handle_Instagram_Login():
    # Direct Dictionary: Isme ab koi json.loads() nahi hai, toh yahan se error nahi aa sakta
    FIXED_SETTINGS = {
        "uuids": {"phone_id": "auto", "uuid": "auto", "client_ad_id": "auto", "advertising_id": "auto"},
        "cookies": {
            "sessionid": "44932978833%3AKxf3Jn1yzJMjut%3A27%3AAYjUOdJAScrRC8xijh8W0KaWYOyT5qpiDNLeeoxzew"
        },
        "last_login": 0,
        "device_settings": {
            "app_version": "269.0.0.18.75", "android_version": 26, "android_release": "8.0.0", "device": "OnePlus 6T"
        },
        "user_agent": "Instagram 269.0.0.18.75 Android (26/8.0.0; 480dpi; 1080x2260; OnePlus; ONEPLUS A6013; fuji; qcom; en_US; 443419082)"
    }
    try:
        Ig_Bot.set_settings(FIXED_SETTINGS)
        Ig_Bot.get_timeline_feed() 
        print("✅ System Alert: Instagram Online.")
    except Exception as e:
        print(f"❌ System Error: Instagram Session Issue -> {e}")

# --- FIX: Safe Database Logic ---
def Fetch_Registry():
    if not os.path.exists(User_Database_Path):
        return {}
    try:
        with open(User_Database_Path, "r") as f:
            content = f.read().strip()
            if not content: # Agar file khali hai
                return {}
            return json.loads(content)
    except Exception as e:
        print(f"⚠️ Registry Corrupt, Resetting: {e}")
        return {}

def Save_Registry(Data):
    with open(User_Database_Path, "w") as f:
        json.dump(Data, f, indent=4)

# Load registry safely
Registry = Fetch_Registry()

# --- Telegram Handlers ---
async def Start_Command(Update: Update, Context: ContextTypes.DEFAULT_TYPE):
    if Update.effective_chat.type != "private": return
    uid = str(Update.effective_user.id)
    if uid not in Registry:
        await Update.message.reply_text("🔱 Satya Dynasty Security\n\nPlease send your Full Name to verify.")
    else:
        await Update.message.reply_text(f"Welcome back, {Registry[uid]['Name']}.")

async def Verification_Handler(Update: Update, Context: ContextTypes.DEFAULT_TYPE):
    if Update.effective_chat.type != "private": return
    uid = str(Update.effective_user.id)
    text = Update.message.text.strip()
    
    if uid not in Registry:
        if len(text) < 3 or text.lower() in ["hi", "hello", "bc", "hey", "hii"]:
            await Update.message.reply_text("❌ Invalid Name. Please provide your real Full Name.")
            return
        Registry[uid] = {"Name": text, "Time": str(datetime.now())}
        Save_Registry(Registry)
        await Update.message.reply_text(f"✅ Identity Verified: {text}")

# --- Monitoring Engine ---
async def Instagram_Monitor_Engine(App: Application):
    Last_Id = None
    print("🚀 Scanning Instagram DMs...")
    while True:
        try:
            Inbox = Ig_Bot.direct_threads()
            if not Inbox:
                await asyncio.sleep(40); continue
              
            Msg = Inbox[0].messages[0]
            if Msg.id != Last_Id and (Msg.clip or Msg.media):
                Pk = Msg.clip.pk if Msg.clip else Msg.media.pk
                Path = Ig_Bot.video_download(Pk, folder="Downloads")
                
                try: 
                    info = Ig_Bot.user_info(Msg.user_id)
                    sender = info.full_name or info.username
                except: sender = "Unknown"
                
                with open(Path, "rb") as V:
                    await App.bot.send_video(
                        chat_id=Target_Group_Id,
                        video=V,
                        caption=f"🔱 Source: Instagram DM\n👤 Agent: {sender}"
                    )
                if os.path.exists(Path): os.remove(Path)
                Last_Id = Msg.id
            await asyncio.sleep(40)
        except Exception: await asyncio.sleep(60)

async def Main_System_Boot():
    Handle_Instagram_Login()
    App = Application.builder().token(Telegram_Token).build()
    App.add_handler(CommandHandler("start", Start_Command))
    App.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & ~filters.COMMAND, Verification_Handler))
    
    async with App:
        await App.initialize()
        await App.start()
        await App.updater.start_polling(drop_pending_updates=True)
        print("🤖 Telegram Bot Synchronized.")
        await Instagram_Monitor_Engine(App)

if __name__ == "__main__":
    asyncio.run(Main_System_Boot())
