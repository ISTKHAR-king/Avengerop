import random
from pyrogram import Client, filters
from pyrogram.types import (
    Message, InlineKeyboardButton, InlineKeyboardMarkup, 
    InputMediaPhoto, InputMediaVideo
)
from AnonXMusic import app

JOINLOGS = -1002144355688  # Ensure this is a valid chat ID where bot has access

@app.on_message(filters.new_chat_members)
async def on_new_chat_members(client: Client, message: Message):
    bot_user = await client.get_me()
    
    for new_member in message.new_chat_members:
        if new_member.id == bot_user.id:  # Bot has been added
            added_by = message.from_user.mention if message.from_user else "Unknown User"
            chat_title = message.chat.title
            chat_id = message.chat.id
            chat_username = f"@{message.chat.username}" if message.chat.username else "Private Chat"
            
            log_text = (
                f"```\n"
                f"#NEWCHAT \n"
                f"ᴄʜᴀᴛ ᴛɪᴛʟᴇ : {chat_title}\n"
                f"ᴄʜᴀᴛ ɪᴅ : {chat_id}\n"
                f"ᴄʜᴀᴛ ᴜɴᴀᴍᴇ : {chat_username}\n"
                f"ᴀᴅᴅᴇᴅ ʙʏ : {added_by}"
                f"```"
            )
            
            try:
                await client.send_message(JOINLOGS, log_text)
            except Exception as e:
                print(f"Error sending log message: {e}")
            
            # Optional: Send welcome message to the group
            try:
                await client.send_message(
                    chat_id, 
                    f"Hello! Thanks for adding me to {chat_title}. Use /help to see available commands."
                )
            except Exception as e:
                print(f"Error sending welcome message: {e}")
