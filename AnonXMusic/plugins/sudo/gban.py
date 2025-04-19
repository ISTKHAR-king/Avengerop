import asyncio

from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from AnonXMusic import app
from AnonXMusic.misc import SUDOERS
from AnonXMusic.utils import get_readable_time
from AnonXMusic.utils.database import (
    add_banned_user,
    get_banned_count,
    get_banned_users,
    get_served_chats,
    is_banned_user,
    remove_banned_user,
)
from AnonXMusic.utils.decorators.language import language
from AnonXMusic.utils.extraction import extract_user
from config import BANNED_USERS
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

@app.on_message(filters.command(["gban", "globalban"]) & SUDOERS)
@language
async def global_ban(client, message: Message, _):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(_["general_1"])

    user = await extract_user(message)
    if user.id == message.from_user.id:
        return await message.reply_text(_["gban_1"])
    elif user.id == app.id:
        return await message.reply_text(_["gban_2"])
    elif user.id in SUDOERS:
        return await message.reply_text(_["gban_3"])

    is_gbanned = await is_banned_user(user.id)
    if is_gbanned:
        return await message.reply_text(_["gban_4"].format(user.mention))

    if user.id not in BANNED_USERS:
        BANNED_USERS.add(user.id)

    served_chats = []
    chats = await get_served_chats()
    for chat in chats:
        served_chats.append(int(chat["chat_id"]))

    time_expected = get_readable_time(len(served_chats))
    mystic = await message.reply_text(
        f"🚫 Global Ban initiated!\n\n"
        f"⚠️ User: {user.mention} has been banned globally!\n\n"
        f"🗂 Affected Chats: {len(served_chats)}\n"
        f"⏳ Expected Time: {time_expected}\n\n"
        f"🔐 Banned by: {message.from_user.mention}\n"
        f"🔄 Progress: ⏳ 0% Banning...",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Cancel Ban", callback_data=f"cancel_ban_{user.id}")]
        ])
    )

    number_of_chats = 0
    for chat_id in served_chats:
        try:
            await app.ban_chat_member(chat_id, user.id)
            number_of_chats += 1
            # Calculate the percentage
            percentage = (number_of_chats / len(served_chats)) * 100
            await mystic.edit_text(
                f"🚫 Global Ban in Progress!\n\n"
                f"⚠️ User: {user.mention} has been banned globally!\n\n"
                f"🗂 Affected Chats: {len(served_chats)}\n"
                f"⏳ Expected Time: {time_expected}\n\n"
                f"🔐 Banned by: {message.from_user.mention}\n"
                f"🔄 Progress: ⏳ {int(percentage)}% Banning...",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Cancel Ban", callback_data=f"cancel_ban_{user.id}")]
                ])
            )
        except FloodWait as fw:
            await asyncio.sleep(int(fw.value))
        except:
            continue

    await add_banned_user(user.id)

    await message.reply_text(
        f"🔒 User: {user.mention} has been banned successfully in {number_of_chats} chats!\n"
        f"⏳ Banned by: {message.from_user.mention}\n"
        f"💬 Chat Title: {message.chat.title}\n"
        f"🔐 User ID: {user.id}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("View Banned Users", callback_data="view_banned_users")]
        ])
    )
    await mystic.delete()

@app.on_message(filters.command(["ungban"]) & SUDOERS)
@language
async def global_un(client, message: Message, _):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(_["general_1"])

    user = await extract_user(message)
    is_gbanned = await is_banned_user(user.id)
    if not is_gbanned:
        return await message.reply_text(_["gban_7"].format(user.mention))

    if user.id in BANNED_USERS:
        BANNED_USERS.remove(user.id)

    served_chats = []
    chats = await get_served_chats()
    for chat in chats:
        served_chats.append(int(chat["chat_id"]))

    time_expected = get_readable_time(len(served_chats))
    mystic = await message.reply_text(
        f"🔓 Global Unban initiated!\n\n"
        f"✅ User: {user.mention} is being unbanned globally!\n\n"
        f"🔄 Progress: ⏳ 0% Unbanning...\n\n"
        f"🗂 Reinstating in: {len(served_chats)} chats\n"
        f"⏳ Expected Time: {time_expected}\n\n"
        f"🎉 Unbanned by: {message.from_user.mention}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Cancel Unban", callback_data=f"cancel_unban_{user.id}")]
        ])
    )

    number_of_chats = 0
    for chat_id in served_chats:
        try:
            await app.unban_chat_member(chat_id, user.id)
            number_of_chats += 1
            # Calculate the percentage
            percentage = (number_of_chats / len(served_chats)) * 100
            await mystic.edit_text(
                f"🔓 Global Unban in Progress!\n\n"
                f"✅ User: {user.mention} has been unbanned globally!\n\n"
                f"🔄 Progress: ⏳ {int(percentage)}% Unbanning...\n\n"
                f"🗂 Reinstating in: {len(served_chats)} chats\n"
                f"⏳ Expected Time: {time_expected}\n\n"
                f"🎉 Unbanned by: {message.from_user.mention}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Cancel Unban", callback_data=f"cancel_unban_{user.id}")]
                ])
            )
        except FloodWait as fw:
            await asyncio.sleep(int(fw.value))
        except:
            continue

    await remove_banned_user(user.id)

    await message.reply_text(
        f"✅ **User**: {user.mention} has been unbanned from **{number_of_chats}** chats!\n"
        f"🎉 **Unbanned by**: {message.from_user.mention}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("View Banned Users", callback_data="view_banned_users")]
        ])
    )
    await mystic.delete()


@app.on_message(filters.command(["gbannedusers", "gbanlist"]) & SUDOERS)
@language
async def gbanned_list(client, message: Message, _):
    counts = await get_banned_count()
    if counts == 0:
        return await message.reply_text(
            "📜 Global Banned Users List:\n\n"
            "🚫 No users are currently banned."
        )

    mystic = await message.reply_text("📜 Fetching Global Banned Users...")
    msg = "📜 Global Banned Users List:\n\n"
    count = 0
    users = await get_banned_users()
    for user_id in users:
        count += 1
        try:
            user = await app.get_users(user_id)
            user = user.first_name if not user.mention else user.mention
            msg += f"{count}➤ {user}\n"
        except Exception:
            msg += f"{count}➤ {user_id}\n"
            continue

    if count == 0:
        return await mystic.edit_text(
            "📜 Global Banned Users List:\n\n🚫 No banned users found!"
        )
    else:
        return await mystic.edit_text(msg, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Refresh List", callback_data="refresh_gban_list")]
        ]))
