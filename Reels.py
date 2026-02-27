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
    Session_String = os.getenv("INSTA_SESSION_STRING")
    if not Session_String:
        print("System Error: INSTA_SESSION_STRING Missing!")
        return
    try:
        # Decode and Load Settings
        Decoded_Data = base64.b64decode(Session_String).decode('utf-8')
        Settings = json.loads(Decoded_Data)
        Ig_Bot.set_settings(Settings)
        
        # Force login via session only
        Ig_Bot.get_timeline_feed() # Token test karne ke liye
        print("System Alert: Instagram Online via Session.")
    except Exception as Error:
        print(f"System Error: Session Expired or Invalid -> {Error}")

# --- Database Logic (Cleaned) ---
def Fetch_Registry():
    if os.path.exists(User_Database_Path):
        with open(User_Database_Path, "r") as f: return json.load(f)
    return {}

def Save_Registry(Data):
    with open(User_Database_Path, "w") as f: json.dump(Data, f, indent=4)

# Purana kachra delete karne ke liye registry reset (sirf ek baar manual kar sakte ho)
Registry = Fetch_Registry()

# --- Telegram Handlers ---
async def Start_Command(Update: Update, Context: ContextTypes.DEFAULT_TYPE):
    # Sirf Private DM mein kaam karega
    if Update.effective_chat.type != "private": return
    
    User_Id = str(Update.effective_user.id)
    if User_Id not in Registry:
        await Update.message.reply_text("🔱 Satya Dynasty Security System\n\nPlease send your Full Name to verify identity.")
    else:
        await Update.message.reply_text(f"Welcome back, {Registry[User_Id]['Name']}. System is monitoring DMs.")

async def Verification_Handler(Update: Update, Context: ContextTypes.DEFAULT_TYPE):
    # Sirf Private DM mein aur non-verified users ke liye
    if Update.effective_chat.type != "private": return
    
    User_Id = str(Update.effective_user.id)
    User_Text = Update.message.text
    
    if User_Id not in Registry:
        # Simple validation: Naam kam se kam 3 word ka ho aur "Hi/Hello" na ho
        if len(User_Text.strip()) < 3 or User_Text.lower() in ["hi", "hello", "bc", "hey"]:
            await Update.message.reply_text("Invalid Name. Please enter your real Full Name.")
            return

        Registry[User_Id] = {"Name": User_Text, "Time": str(datetime.now())}
        Save_Registry(Registry)
        await Update.message.reply_text(f"✅ Identity Verified: {User_Text}.\nYou can now share reels in Instagram DM.")

# --- Monitoring Engine ---
async def Instagram_Monitor_Engine(App: Application):
    Last_Id = None
    print("Intelligence Engine: Scanning DMs...")
    while True:
        try:
            Inbox = Ig_Bot.direct_threads()
            if not Inbox:
                await asyncio.sleep(45); continue
              
            Msg = Inbox[0].messages[0]
            if Msg.id != Last_Id and (Msg.clip or Msg.media):
                Media_Pk = Msg.clip.pk if Msg.clip else Msg.media.pk
                Path = Ig_Bot.video_download(Media_Pk, folder="Downloads")
                
                # Sender Info fetch
                try: 
                    info = Ig_Bot.user_info(Msg.user_id)
                    sender = info.full_name or info.username
                except: sender = "Unknown"
                
                with open(Path, "rb") as Video:
                    await App.bot.send_video(
                        chat_id=Target_Group_Id,
                        video=Video,
                        caption=f"🔱 Source: Instagram DM\n👤 Agent: {sender}\n⏰ {datetime.now().strftime('%H:%M:%S')}"
                    )
                os.remove(Path)
                Last_Id = Msg.id
            await asyncio.sleep(45)
        except Exception: await asyncio.sleep(60)

async def Main_System_Boot():
    Handle_Instagram_Login()
    App = Application.builder().token(Telegram_Token).build()
    
    # Handlers
    App.add_handler(CommandHandler("start", Start_Command))
    # Ye sirf Private DM ke text ko pakdega
    App.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & ~filters.COMMAND, Verification_Handler))
    
    async with App:
        await App.initialize()
        await App.start()
        await App.updater.start_polling(drop_pending_updates=True)
        await Instagram_Monitor_Engine(App)

if __name__ == "__main__":
    asyncio.run(Main_System_Boot())
