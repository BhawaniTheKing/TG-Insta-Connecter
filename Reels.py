import os
import json
import asyncio
import base64
from datetime import datetime
from instagrapi import Client
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

Instagram_Username = "satya.dynasty"
Instagram_Password = "Kaka9090"
Telegram_Token = "8677114145:AAFeHE3zjzDj19ET1bpTejBS9EXdR5WPaGM"
Target_Group_Id = -1003830400479
User_Database_Path = "Users_Registry.json"

Ig_Bot = Client()

def Handle_Instagram_Login():
    # Pehle Session String Try Karo
    Session_String = os.getenv("INSTA_SESSION_STRING")
    try:
        if Session_String and len(Session_String) > 10:
            Decoded_Data = base64.b64decode(Session_String).decode('utf-8')
            Settings = json.loads(Decoded_Data)
            Ig_Bot.set_settings(Settings)
            print("System Alert: Session String Applied.")
        
        # Agar string fail hui toh normal login
        Ig_Bot.login(Instagram_Username, Instagram_Password)
        print("System Alert: Instagram Access Granted.")
    except Exception as Error:
        print(f"System Error: Login Failed -> {Error}")

# Database Functions (Same as before)
def Fetch_Local_Database():
    if os.path.exists(User_Database_Path):
        with open(User_Database_Path, "r") as Data_File: return json.load(Data_File)
    return {}

def Commit_To_Database(Data):
    with open(User_Database_Path, "w") as Data_File: json.dump(Data, Data_File, indent=4)

Registry = Fetch_Local_Database()

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
        await Update.message.reply_text("Verification Complete.")

async def Instagram_Monitor_Engine(App: Application):
    Last_Id = None
    print("System Alert: Monitor Active.")
    while True:
        try:
            # Check for new messages
            Inbox = Ig_Bot.direct_threads()
            if Inbox:
                Thread = Inbox[0]
                Msg = Thread.messages[0]
                
                if Msg.id != Last_Id and (Msg.clip or Msg.media):
                    print("New Reel Found!")
                    Media_Pk = Msg.clip.pk if Msg.clip else Msg.media.pk
                    Path = Ig_Bot.video_download(Media_Pk, folder="Downloads")
                    
                    # Send to Group
                    with open(Path, "rb") as Video:
                        await App.bot.send_video(chat_id=Target_Group_Id, video=Video, caption=f"Shared By: {Ig_Bot.user_info(Msg.user_id).full_name}")
                    
                    os.remove(Path)
                    Last_Id = Msg.id
            await asyncio.sleep(60) # Keep a safe gap
        except Exception:
            await asyncio.sleep(60)

async def Main_System_Boot():
    Handle_Instagram_Login()
    # drop_pending_updates=True isse conflict error khatam ho jayega
    App = Application.builder().token(Telegram_Token).build()
    App.add_handler(CommandHandler("start", Start_Command))
    App.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, Registration_Handler))
    
    async with App:
        await App.initialize()
        await App.start()
        # Conflict fix: Pehle purane updates clear karo
        await App.updater.start_polling(drop_pending_updates=True)
        await Instagram_Monitor_Engine(App)

if __name__ == "__main__":
    asyncio.run(Main_System_Boot())
