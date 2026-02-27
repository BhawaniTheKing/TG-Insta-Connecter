import os, json, asyncio
from datetime import datetime
from instagrapi import Client
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Configuration ---
Instagram_Username = "satya.dynasty"
Instagram_Password = "Kaka0909"
Telegram_Token = "8677114145:AAFeHE3zjzDj19ET1bpTejBS9EXdR5WPaGM"
Target_Group_Id = -1003830400479
User_Database_Path = "Users_Registry.json"

Ig_Bot = Client()

def Handle_Instagram_Login():
    try:
        # Hum koi purani setting load hi nahi karenge
        # Seedha fresh login try karenge
        print("Attempting Fresh Login...")
        Ig_Bot.login(Instagram_Username, Instagram_Password)
        print("✅ System Alert: Instagram Access Granted via Password.")
    except Exception as e:
        print(f"❌ System Error: Login Failed -> {e}")

# --- Safe Database Logic ---
def Fetch_Registry():
    if not os.path.exists(User_Database_Path): return {}
    try:
        with open(User_Database_Path, "r") as f:
            data = f.read().strip()
            return json.loads(data) if data else {}
    except: return {}

def Save_Registry(Data):
    with open(User_Database_Path, "w") as f: json.dump(Data, f, indent=4)

Registry = Fetch_Registry()

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
                    await App.bot.send_video(chat_id=Target_Group_Id, video=V, caption=f"🔱 Agent: {sender}")
                if os.path.exists(Path): os.remove(Path)
                Last_Id = Msg.id
            await asyncio.sleep(40)
        except Exception: await asyncio.sleep(60)

async def Main_System_Boot():
    Handle_Instagram_Login()
    App = Application.builder().token(Telegram_Token).build()
    App.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("System Online.")))
    
    async with App:
        await App.initialize()
        await App.start()
        await App.updater.start_polling(drop_pending_updates=True)
        print("🤖 Telegram Bot Synchronized.")
        await Instagram_Monitor_Engine(App)

if __name__ == "__main__":
    asyncio.run(Main_System_Boot())
