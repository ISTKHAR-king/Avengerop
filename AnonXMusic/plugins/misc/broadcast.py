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

# Configurable limits
REQUEST_LIMIT = 50
BATCH_SIZE = 1000
BATCH_DELAY = 2
MAX_RETRIES = 3
PING_EVERY_BATCHES = 10
STATUS_UPDATE_EVERY = 1
SLICE_SIZE = 20000

last_broadcast_result = {}

@app.on_message(filters.command("broadcast") & SUDOERS)
@language
async def broadcast_command(client, message, _):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a message you want to broadcast.")

    command_text = message.text.lower()
    mode = "forward" if "-forward" in command_text else "copy"

    users = await get_served_users()
    target_chats = await get_served_chats()

    # Properly determine targets based on provided flags
    if "-users" in command_text:
        targets = users
    elif "-nochats" in command_text:
        targets = target_chats
    else:
        targets = target_chats + users

    if not targets:
        return await message.reply_text("No targets found for broadcast.")

    start_time = time.time()
    sent_count, failed_count = 0, 0
    total_targets = len(targets)

    status_msg = await message.reply_text(f"Broadcast started in `{mode}` mode...\n\nProgress: `0%`")

    async def send_with_retries(chat_id):
        nonlocal sent_count, failed_count
        for attempt in range(MAX_RETRIES):
            try:
                if mode == "forward":
                    await app.forward_messages(
                        chat_id=chat_id,
                        from_chat_id=message.chat.id,
                        message_ids=message.reply_to_message.id
                    )
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
        batch_count = 0
        total_batches = (len(target_list) + BATCH_SIZE - 1) // BATCH_SIZE

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

            batch_count += 1

            if batch_count % PING_EVERY_BATCHES == 0:
                try:
                    await app.get_me()
                except Exception as e:
                    print(f"Session health ping failed: {e}")
                    await asyncio.sleep(2)

            if batch_count % STATUS_UPDATE_EVERY == 0 or batch_count == total_batches:
                percent = round((sent_count + failed_count) / total_targets * 100, 2)
                elapsed = time.time() - start_time
                eta = (elapsed / (sent_count + failed_count)) * (total_targets - (sent_count + failed_count)) if sent_count + failed_count > 0 else 0
                eta_formatted = f"{int(eta // 60)}m {int(eta % 60)}s"

                progress_bar = f"[{'█' * int(percent // 5)}{'░' * (20 - int(percent // 5))}]"
                await status_msg.edit_text(
                    f"𝗕𝗿𝗼𝗮𝗱𝗰𝗮𝘀𝘁 𝗣𝗿𝗼𝗴𝗿𝗲𝘀𝘀 📢\n"
                    f"{progress_bar} {percent}%\n"
                    f"Sent:  {sent_count}  🟢\n"
                    f"Failed: {failed_count}  🔴\n"
                    f"ETA:  {eta_formatted} ⏳"
                )

            await asyncio.sleep(BATCH_DELAY)

        await asyncio.sleep(1)

    for j in range(0, total_targets, SLICE_SIZE):
        await broadcast_targets(targets[j:j + SLICE_SIZE])

    total_time = round(time.time() - start_time, 2)

    final_summary = (
        f"✅𝗕𝗿𝗼𝗮𝗱𝗰𝗮𝘀𝘁 𝗥𝗲𝗽𝗼𝗿𝘁 📢\n\n"
        f"Mode: {mode}\n"
        f"Total Targets: {total_targets}\n"
        f"Successful: {sent_count} 🟢\n"
        f"Failed: {failed_count} 🔴\n"
        f"Time Taken: {total_time} seconds ⏰"
    )

    await status_msg.edit_text(final_summary)

    last_broadcast_result.update({
        "mode": mode,
        "total": total_targets,
        "sent": sent_count,
        "failed": failed_count,
        "time": total_time
    })

@app.on_message(filters.command("broadcaststats") & SUDOERS)
async def broadcast_stats(_, message):
    if not last_broadcast_result:
        return await message.reply_text("No broadcast run yet.")

    res = last_broadcast_result
    await message.reply_text(
        f"📝 Last Broadcast Report:\n\n"
        f"♨️ Mode: {res['mode']}\n"
        f"✨ Total Targets: {res['total']}\n"
        f"✅ Successful: {res['sent']} \n"
        f"⛔ Failed: {res['failed']} \n"
        f"🔮 Time Taken: {res['time']} seconds ⏰"
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
