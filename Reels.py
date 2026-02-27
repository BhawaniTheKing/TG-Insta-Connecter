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

# --- TERI HARDCODED STRING ---
# Maine ise yahan direct paste kar diya hai
RAW_SESSION = "eyJ1dWlkcyI6IHsicGhvbmVfaWQiOiAiYXV0byIsICJ1dWlkIjogImF1dG8iLCAiY2xpZW50X2FkX2lkIjogImF1dG8iLCAiYWR2ZXJ0aXNpbmdfaWQiOiAiYXV0byJ9LCAiY29va2llcyI6IHsic2Vzc2lvbmlkIjogIjQ0OTMyOTc4ODMzJTNBS3hmM0puMXl6Sk1qdXQlM0EyNyUzQUFZalVPZEpBU2NyUkM4eGlqaDhXMEthV1lPeVQ1cXBpRE5MZWVveHpldyJ9LCAibGFzdF9sb2dpbiI6IDAsICJkZXZpY2Vfc2V0dGluZ3MiOiB7ImFwcF92ZXJzaW9uIjogIjI2OS4wLjAuMTguNzUiLCAiYW5kcm9pZF92ZXJzaW9uIjogMjYsICJhbmRyb2lkX3JlbGVhc2UiOiAiOC4wLjAiLCAiZGV2aWNlIjogIk9uZVBsdXMgNlQifSwgInVzZXJfYWdlbnQiOiAiSW5zdGFncmFtIDI2OS4wLjAuMTguNzUgQW5kcm9pZCAoMjYvOC4wLjA7IDQ4MGRwaTsgMTA4MHgyMjYwOyBPbmVQbHVzOyBPTkVQTFVTIEE2MDEzOyBmdWppOyBxY29tOyBlbl9VUzsgNDQzNDE5MDgyKSJ9"

Ig_Bot = Client()

def Handle_Instagram_Login():
    try:
        # String Cleaning (Extra protection)
        clean_str = RAW_SESSION.strip().replace('"', '').replace("'", "")
        
        # Auto-Padding Fix (Jo tune bola tha == wala chakkar)
        missing_padding = len(clean_str) % 4
        if missing_padding:
            clean_str += '=' * (4 - missing_padding)
            
        # Decode and Apply
        decoded = base64.b64decode(clean_str).decode('utf-8')
        settings = json.loads(decoded)
        Ig_Bot.set_settings(settings)
        
        # Check if actually working
        Ig_Bot.get_timeline_feed() 
        print("✅ System Alert: Instagram Online (Hardcoded Session).")
    except Exception as e:
        print(f"❌ System Error: Hardcoded Login Failed -> {e}")

# --- Database Logic ---
def Fetch_Registry():
    if os.path.exists(User_Database_Path):
        try:
            with open(User_Database_Path, "r") as f: return json.load(f)
        except: return {}
    return {}

def Save_Registry(Data):
    with open(User_Database_Path, "w") as f: json.dump(Data, f, indent=4)

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
        # Strict Filtering: Fake names block
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
                await asyncio.sleep(30); continue
              
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
                        caption=f"🔱 Source: Instagram DM\n👤 Agent: {sender}\n⏰ {datetime.now().strftime('%H:%M:%S')}"
                    )
                os.remove(Path)
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
        # Clean conflict at start
        await App.updater.start_polling(drop_pending_updates=True)
        print("🤖 Telegram Bot Synchronized.")
        await Instagram_Monitor_Engine(App)

if __name__ == "__main__":
    asyncio.run(Main_System_Boot())
