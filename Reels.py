import os
import json
import asyncio
import logging
from datetime import datetime
from instagrapi import Client
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
Logger = logging.getLogger(__name__)

Instagram_Username = "satya.dynasty"
Instagram_Password = "Bhawani8094"
Telegram_Token = "8677114145:AAFeHE3zjzDj19ET1bpTejBS9EXdR5WPaGM"
Target_Group_Id = -1003830400479
User_Database_Path = "Users_Registry.json"
Session_File_Path = "Instagram_Session.json"

Ig_Bot = Client()

def Handle_Instagram_Login():
    try:
        if os.path.exists(Session_File_Path):
            Logger.info("Loading Existing Instagram Session...")
            Ig_Bot.load_settings(Session_File_Path)
        
        Ig_Bot.login(Instagram_Username, Instagram_Password)
        Ig_Bot.dump_settings(Session_File_Path)
        Logger.info("Instagram Authentication Successful!")
    except Exception as Error:
        Logger.error(f"Critical Authentication Failure: {Error}")

def Fetch_Local_Database():
    if os.path.exists(User_Database_Path):
        with open(User_Database_Path, "r") as Data_File:
            return json.load(Data_File)
    return {}

def Commit_To_Database(Data):
    with open(User_Database_Path, "w") as Data_File:
        json.dump(Data, Data_File, indent=4)

Registry = Fetch_Local_Database()

async def Start_Command(Update: Update, Context: ContextTypes.DEFAULT_TYPE):
    User_Identity = str(Update.effective_user.id)
    if User_Identity not in Registry:
        await Update.message.reply_text("System Online. Access Restricted. Please Submit Your Full Name For Identity Verification.")
    else:
        await Update.message.reply_text(f"Welcome Back, {Registry[User_Identity]['Name']}. All Systems Operational.")

async def Registration_Handler(Update: Update, Context: ContextTypes.DEFAULT_TYPE):
    User_Identity = str(Update.effective_user.id)
    User_Input = Update.message.text
    
    if User_Identity not in Registry:
        Registry[User_Identity] = {"Name": User_Input, "Timestamp": str(datetime.now())}
        Commit_To_Database(Registry)
        await Update.message.reply_text(f"Identity Confirmed: {User_Input}. You Are Now Authorized To Forward Content.")

async def Instagram_Monitor_Engine(App_Instance: Application):
    Last_Processed_Id = None
    Logger.info("Starting Instagram Intelligence Engine...")
    
    while True:
        try:
            Inbox_Threads = Ig_Bot.direct_threads()
            if not Inbox_Threads:
                await asyncio.sleep(40)
                continue
              
            Latest_Thread = Inbox_Threads[0]
            Recent_Message = Latest_Thread.messages[0]
            
            if Recent_Message.id != Last_Processed_Id:
                if Recent_Message.clip or Recent_Message.media:
                    Logger.info("New High-Value Target Detected In DMs!")
                    
                    Media_Pk = Recent_Message.clip.pk if Recent_Message.clip else Recent_Message.media.pk
                    Download_Path = Ig_Bot.video_download(Media_Pk, folder="Downloads")
                    
                    Sender_Info = Ig_Bot.user_info(Recent_Message.user_id).full_name
                    
                    with open(Download_Path, "rb") as Media_File:
                        await App_Instance.bot.send_video(
                            chat_id=Target_Group_Id,
                            video=Media_File,
                            caption=f"Source: Instagram DM\nAgent: {Sender_Info}\nTime: {datetime.now().strftime('%H:%M:%S')}"
                        )
                    
                    os.remove(Download_Path)
                    Logger.info("Media Successfully Exfiltrated To Telegram.")
                    
                Last_Processed_Id = Recent_Message.id
            
            await asyncio.sleep(45)
            
        except Exception as Incident:
            Logger.warning(f"Engine Alert: {Incident}")
            await asyncio.sleep(60)

async def Main_System_Boot():
    Handle_Instagram_Login()
    
    App = Application.builder().token(Telegram_Token).build()
    
    App.add_handler(CommandHandler("start", Start_Command))
    App.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, Registration_Handler))
    
    Logger.info("Synchronizing Telegram And Instagram Services...")
    
    async with App:
        await App.initialize()
        await App.start()
        await asyncio.gather(
            App.updater.start_polling(),
            Instagram_Monitor_Engine(App)
        )

if __name__ == "__main__":
    try:
        asyncio.run(Main_System_Boot())
    except KeyboardInterrupt:
        Logger.info("System Shutdown Initiated By User.")
