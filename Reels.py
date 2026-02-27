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
    # Railway Variables se Session String uthayega
    Session_String = os.getenv("INSTA_SESSION_STRING")
    
    if not Session_String:
        print("System Error: INSTA_SESSION_STRING Variable Missing In Railway!")
        return

    try:
        # Decode and Load Settings
        Decoded_Data = base64.b64decode(Session_String).decode('utf-8')
        Settings = json.loads(Decoded_Data)
        Ig_Bot.set_settings(Settings)
        
        # Login using only session (No Password Required)
        Ig_Bot.login(Instagram_Username, "") 
        print("System Alert: Instagram Online via Session String (No Password).")
        
    except Exception as Error:
        print(f"System Error: Session Failed -> {Error}")
        print("Tip: Browser se nayi Session ID nikalo aur Base64 string update karo.")

# --- Database Functions ---
def Fetch_Local_Database():
    if os.path.exists(User_Database_Path):
        with open(User_Database_Path, "r") as Data_File: return json.load(Data_File)
    return {}

def Commit_To_Database(Data):
    with open(User_Database_Path, "w") as Data_File: json.dump(Data, Data_File, indent=4)

Registry = Fetch_Local_Database()

# --- Telegram Handlers ---
async def Start_Command(Update: Update, Context: ContextTypes.DEFAULT_TYPE):
    User_Id = str(Update.effective_user.id)
    if User_Id not in Registry:
        await Update.message.reply_text("System Online. Access Restricted. Send Your Full Name.")
    else:
        await Update.message.reply_text(f"Access Granted. Hello {Registry[User_Id]['Name']}.")

async def Registration_Handler(Update: Update, Context: ContextTypes.DEFAULT_TYPE):
    User_Id = str(Update.effective_user.id)
    if User_Id not in Registry:
        Registry[User_Id] = {"Name": Update.message.text, "Time": str(datetime.now())}
        Commit_To_Database(Registry)
        await Update.message.reply_text("Verification Complete. You can now use the bot.")

# --- Monitoring Engine ---
async def Instagram_Monitor_Engine(App: Application):
    Last_Id = None
    print("System Alert: Intelligence Engine Is Active.")
    
    while True:
        try:
            Inbox = Ig_Bot.direct_threads()
            if not Inbox:
                await asyncio.sleep(45)
                continue
              
            Msg = Inbox[0].messages[0]
            
            if Msg.id != Last_Id:
                if Msg.clip or Msg.media:
                    print(f"New Reel Detected from {Msg.user_id}!")
                    
                    Media_Pk = Msg.clip.pk if Msg.clip else Msg.media.pk
                    Path = Ig_Bot.video_download(Media_Pk, folder="Downloads")
                    
                    # Fetch User Info Safely
                    try:
                        User_Info = Ig_Bot.user_info(Msg.user_id)
                        Sender = User_Info.full_name or User_Info.username
                    except:
                        Sender = "Unknown Agent"
                    
                    with open(Path, "rb") as Video:
                        await App.bot.send_video(
                            chat_id=Target_Group_Id,
                            video=Video,
                            caption=f"Source: Instagram DM\nAgent: {Sender}\nTime: {datetime.now().strftime('%H:%M:%S')}"
                        )
                    
                    os.remove(Path)
                    print("System Alert: Reel Sent Successfully.")
                    
                Last_Id = Msg.id
            
            await asyncio.sleep(45)
            
        except Exception as E:
            # Silent error to avoid log spamming
            await asyncio.sleep(60)

# --- Boot Sequence ---
async def Main_System_Boot():
    Handle_Instagram_Login()
    
    App = Application.builder().token(Telegram_Token).build()
    App.add_handler(CommandHandler("start", Start_Command))
    App.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, Registration_Handler))
    
    async with App:
        await App.initialize()
        await App.start()
        # Conflict fix: Purane updates clear karega
        await App.updater.start_polling(drop_pending_updates=True)
        print("System Alert: Telegram Services Synchronized.")
        await Instagram_Monitor_Engine(App)

if __name__ == "__main__":
    asyncio.run(Main_System_Boot())
