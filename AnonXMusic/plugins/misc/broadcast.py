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
    mode = "forward" if "-forward" in command_text else "copy"

    if "-all" in command_text:
        target_chats = [int(chat_id) for chat_id in await get_served_chats()]
        target_users = [int(user_id) for user_id in await get_served_users()]
    elif "-users" in command_text:
        target_chats = []
        target_users = [int(user_id) for user_id in await get_served_users()]
    elif "-chats" in command_text:
        target_chats = [int(chat_id) for chat_id in await get_served_chats()]
        target_users = []
    else:
        return await message.reply_text("Please use a valid tag: `-all`, `-users`, `-chats`.")

    if not target_chats and not target_users:
        return await message.reply_text("No targets found for broadcast.")

    start_time = time.time()
    total_targets = len(target_chats) + len(target_users)
    sent_count, failed_count = 0, 0
    all_targets = target_chats + target_users
    total_batches = (len(all_targets) + BATCH_SIZE - 1) // BATCH_SIZE
    batch_times = []

    status_message = await message.reply_text(
        f"**Broadcast started in `{mode}` mode.**\n"
        f"**Total Targets:** `{total_targets}`\n"
        f"**Progress:** `0%`\n"
        f"**Successful:** `0`\n"
        f"**Failed:** `0`\n"
        f"`██████████`"
    )

    def make_progress_bar(percent):
        filled_slots = int(percent // 10)
        empty_slots = 10 - filled_slots
        return "█" * filled_slots + "░" * empty_slots

    def format_eta(seconds):
        if seconds < 60:
            return f"{int(seconds)} sec"
        mins, secs = divmod(int(seconds), 60)
        return f"{mins}m {secs}s"

    async def send_with_retries(chat_id):
        nonlocal sent_count, failed_count
        for attempt in range(MAX_RETRIES):
            try:
                if mode == "forward":
                    await app.forward_messages(chat_id, message.chat.id, message.reply_to_message.id, remove_caption=True)
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
        nonlocal sent_count, failed_count
        for batch_num in range(0, len(target_list), BATCH_SIZE):
            batch_start_time = time.time()
            batch = target_list[batch_num:batch_num + BATCH_SIZE]
            tasks = []
            for chat_id in batch:
                if len(tasks) >= REQUEST_LIMIT:
                    await asyncio.gather(*tasks)
                    tasks.clear()
                tasks.append(send_with_retries(chat_id))
            if tasks:
                await asyncio.gather(*tasks)

            batch_time = time.time() - batch_start_time
            batch_times.append(batch_time)
            average_batch_time = sum(batch_times) / len(batch_times)
            batches_done = (batch_num // BATCH_SIZE) + 1
            batches_left = total_batches - batches_done
            eta = format_eta(average_batch_time * batches_left)

            progress = round(((sent_count + failed_count) / total_targets) * 100, 2)
            progress_bar = make_progress_bar(progress)
            await status_message.edit_text(
                f"**Broadcast In Progress...**\n\n"
                f"**Mode:** `{mode}`\n"
                f"**Total Targets:** `{total_targets}`\n"
                f"**Successful:** `{sent_count}`\n"
                f"**Failed:** `{failed_count}`\n"
                f"**Progress:** `{progress}%`\n"
                f"`{progress_bar}`\n"
                f"**ETA:** `{eta}`"
            )
            await asyncio.sleep(BATCH_DELAY)

    await broadcast_targets(all_targets)

    total_time = round(time.time() - start_time, 2)
    await status_message.edit_text(
        f"**Broadcast Complete ✅**\n\n"
        f"**Mode:** `{mode}`\n"
        f"**Total Targets:** `{total_targets}`\n"
        f"**Successful:** `{sent_count}`\n"
        f"**Failed:** `{failed_count}`\n"
        f"**Total Time:** `{total_time} seconds`"
    )


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
