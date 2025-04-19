import time
import asyncio

from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import FloodWait, RPCError

from AnonXMusic import app
from AnonXMusic.misc import SUDOERS
from AnonXMusic.utils.database import (
    get_active_chats,
    get_authuser_names,
    get_client,
    get_served_chats,
    get_served_users,
)
from AnonXMusic.utils.decorators.language import language
from AnonXMusic.utils.formatters import alpha_to_int
from config import adminlist

REQUEST_LIMIT = 50
BATCH_SIZE = 500
BATCH_DELAY = 2
MAX_RETRIES = 3

@app.on_message(filters.command("broadcast") & SUDOERS)
@language
async def broadcast_command(client, message, _):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a message you want to broadcast.")

    command_text = message.text.lower()
    target_chats, target_users = [], []
    mode = "forward" if "-forward" in command_text else "copy"

    # Decide targets based on tag
    if "-all" in command_text:
        target_chats = [int(chat["chat_id"]) for chat in await get_served_chats()]
        target_users = [int(user["user_id"]) for user in await get_served_users()]
    elif "-users" in command_text:
        target_users = [int(user["user_id"]) for user in await get_served_users()]
    elif "-chats" in command_text:
        target_chats = [int(chat["chat_id"]) for chat in await get_served_chats()]
    else:
        return await message.reply_text("Please use a valid tag: `-all`, `-users`, `-chats`.")

    if not target_chats and not target_users:
        return await message.reply_text("No targets found for broadcast.")

    start_time = time.time()
    await message.reply_text(f"Broadcast started in `{mode}` mode...")

    sent_count, failed_count = 0, 0
    targets = target_chats + target_users

    async def send_with_retries(chat_id):
        nonlocal sent_count, failed_count
        for attempt in range(MAX_RETRIES):
            try:
                if mode == "forward":
                    await app.forward_messages(chat_id, message.chat.id, message.reply_to_message.id)
                else:
                    await message.reply_to_message.copy(chat_id)
                sent_count += 1
                return
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except RPCError:
                await asyncio.sleep(0.5)
        failed_count += 1

    async def broadcast_targets(target_list):
        for i in range(0, len(target_list), BATCH_SIZE):
            batch = target_list[i:i + BATCH_SIZE]
            tasks = []
            for chat_id in batch:
                if len(tasks) >= REQUEST_LIMIT:
                    await asyncio.gather(*tasks)
                    tasks.clear()
                tasks.append(send_with_retries(chat_id))
            if tasks:
                await asyncio.gather(*tasks)
            await asyncio.sleep(BATCH_DELAY)

    await broadcast_targets(targets)

    total_time = round(time.time() - start_time, 2)
    total_targets = len(targets)

    summary = (
        f"**Broadcast Report**\n\n"
        f"**Mode:** `{mode}`\n"
        f"**Total Targets:** `{total_targets}`\n"
        f"**Successful:** `{sent_count}`\n"
        f"**Failed:** `{failed_count}`\n"
        f"**Time Taken:** `{total_time} seconds`"
    )

    await message.reply_text(summary)


async def auto_clean():
    while not await asyncio.sleep(10):
        try:
            served_chats = await get_active_chats()
            for chat_id in served_chats:
                if chat_id not in adminlist:
                    adminlist[chat_id] = []
                    async for user in app.get_chat_members(
                        chat_id, filter=ChatMembersFilter.ADMINISTRATORS
                    ):
                        if user.privileges.can_manage_video_chats:
                            adminlist[chat_id].append(user.user.id)
                    authusers = await get_authuser_names(chat_id)
                    for user in authusers:
                        user_id = await alpha_to_int(user)
                        adminlist[chat_id].append(user_id)
        except:
            continue


asyncio.create_task(auto_clean())
