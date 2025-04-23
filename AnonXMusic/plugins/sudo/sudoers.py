from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ChatAction

from AnonXMusic import app
from AnonXMusic.misc import SUDOERS
from AnonXMusic.utils.database import add_sudo, remove_sudo
from AnonXMusic.utils.decorators.language import language
from AnonXMusic.utils.extraction import extract_user
from config import BANNED_USERS, OWNER_ID

# Secondary owner/user allowed to manage SUDO
SECOND_OWNER_ID = 6848223695  # Replace with the actual second owner ID
ALLOWED_ADMINS = [OWNER_ID, SECOND_OWNER_ID]


# Custom filter for allowed sudo command users
sudo_admin_filter = filters.user(ALLOWED_ADMINS)


@app.on_message(filters.command("addsudo") & sudo_admin_filter)
@language
async def useradd(client, message: Message, _):
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text("❗ Usage: Reply to a user or use `/addsudo user_id`")

    user = await extract_user(message)
    if user.id in SUDOERS:
        return await message.reply_text(f"⚠️ {user.mention} is already a sudo user!")

    if await add_sudo(user.id):
        SUDOERS.add(user.id)
        return await message.reply_text(
            f"✅ Successfully promoted {user.mention} to SUDO user."
        )
    return await message.reply_text("❌ Failed to add user to SUDO list.")


@app.on_message(filters.command(["delsudo", "rmsudo"]) & sudo_admin_filter)
@language
async def userdel(client, message: Message, _):
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text("❗ Usage: Reply to a user or use `/delsudo user_id`")

    user = await extract_user(message)
    if user.id not in SUDOERS:
        return await message.reply_text(f"⚠️ {user.mention} is not a sudo user!")

    if await remove_sudo(user.id):
        SUDOERS.remove(user.id)
        return await message.reply_text(f"❌ {user.mention} has been removed from SUDO users.")
    return await message.reply_text("❌ Failed to remove user from SUDO list.")


@app.on_message(filters.command(["sudolist", "listsudo", "sudoers"]) & ~BANNED_USERS)
@language
async def sudoers_list(client, message: Message, _):
    text = "🧑‍💻<u><b>SUDO USERS LIST</b></u>\n\n"
    buttons = []

    try:
        owner = await app.get_users(OWNER_ID)
        text += f"1️⃣<b> <a herf=tg://user?id=7765692814>𝐒ᴍᴀᴜɢ 🇷🇺</a></b>\n"
    except:
        text += "1️⃣ Owner (User not found)\n"

    count = 2
    for user_id in SUDOERS:
        if user_id != OWNER_ID:
            try:
                user = await app.get_users(user_id)
                mention = user.first_name
                text += f"{count}️⃣ {mention}\n"
                buttons.append([
                    InlineKeyboardButton(
                        text=f"Remove {mention}",
                        callback_data=f"remove_sudo:{user.id}"
                    )
                ])
                count += 1
            except:
                continue

    if count == 2:
        return await message.reply_text("⚠️ No SUDO users found.")

    return await message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@app.on_callback_query(filters.regex("remove_sudo:(\\d+)"))
async def handle_remove_sudo(client, callback_query: CallbackQuery):
    user_id = int(callback_query.data.split(":")[1])
    if callback_query.from_user.id not in ALLOWED_ADMINS:
        return await callback_query.answer("⛔ You don't have permission to do this!", show_alert=True)

    if user_id not in SUDOERS:
        return await callback_query.answer("⚠️ User is not in the SUDO list!", show_alert=True)

    removed = await remove_sudo(user_id)
    if removed:
        SUDOERS.remove(user_id)
        await callback_query.answer("✅ User removed from SUDO.")
        await callback_query.message.edit_text("Updated sudo list. Use /sudolist again to refresh.")
    else:
        await callback_query.answer("❌ Failed to remove user.", show_alert=True)
