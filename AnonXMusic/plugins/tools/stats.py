import platform
from sys import version as pyver

import psutil
from pyrogram import __version__ as pyrover
from pyrogram import filters
from pyrogram.errors import MessageIdInvalid
from pyrogram.types import InputMediaPhoto, Message
from pytgcalls.__version__ import __version__ as pytgver

import config
from AnonXMusic import app
from AnonXMusic.core.userbot import assistants
from AnonXMusic.misc import SUDOERS, mongodb
from AnonXMusic.plugins import ALL_MODULES
from AnonXMusic.utils.database import get_served_chats, get_served_users, get_sudoers
from AnonXMusic.utils.decorators.language import language, languageCB
from AnonXMusic.utils.inline.stats import back_stats_buttons, stats_buttons
from config import BANNED_USERS

# Group Stats Command
@app.on_message(filters.command(["stats", "gstats"]) & filters.group & ~BANNED_USERS)
@language
async def stats_global(client, message: Message, _):
    upl = stats_buttons(_, message.from_user.id in SUDOERS)
    await message.reply_photo(
        photo=config.STATS_IMG_URL,
        caption=f"**📊 Global Stats Panel for {app.mention}**",
        reply_markup=upl,
    )

# Back to Stats Callback
@app.on_callback_query(filters.regex("stats_back") & ~BANNED_USERS)
@languageCB
async def home_stats(client, CallbackQuery, _):
    upl = stats_buttons(_, CallbackQuery.from_user.id in SUDOERS)
    await CallbackQuery.edit_message_text(
        text=f"**📊 Global Stats Panel for {app.mention}**",
        reply_markup=upl,
    )

# Top Overall Stats Callback
@app.on_callback_query(filters.regex("TopOverall") & ~BANNED_USERS)
@languageCB
async def overall_stats(client, CallbackQuery, _):
    await CallbackQuery.answer()
    upl = back_stats_buttons(_)
    served_chats = len(await get_served_chats())
    served_users = len(await get_served_users())
    text = (
        f"**📈 Bot Usage Summary**\n\n"
        f"**🤖 Bot Name:** {app.mention}\n"
        f"**🎛 Assistants:** `{len(assistants)}`\n"
        f"**🚫 Banned Users:** `{len(BANNED_USERS)}`\n"
        f"**💬 Served Chats:** `{served_chats}`\n"
        f"**👥 Served Users:** `{served_users}`\n"
        f"**📦 Modules Loaded:** `{len(ALL_MODULES)}`\n"
        f"**🛡️ Sudo Users:** `{len(SUDOERS)}`\n"
        f"**👋 Auto Leave Assistants:** `{config.AUTO_LEAVING_ASSISTANT}`\n"
        f"**⏱️ Max Song Duration:** `{config.DURATION_LIMIT_MIN} Minutes`\n"
    )
    med = InputMediaPhoto(media=config.STATS_IMG_URL, caption=text)
    try:
        await CallbackQuery.edit_message_media(media=med, reply_markup=upl)
    except MessageIdInvalid:
        await CallbackQuery.message.reply_photo(
            photo=config.STATS_IMG_URL, caption=text, reply_markup=upl
        )

# Bot System Stats for Sudo Users
@app.on_callback_query(filters.regex("bot_stats_sudo"))
@languageCB
async def bot_stats(client, CallbackQuery, _):
    if CallbackQuery.from_user.id not in SUDOERS:
        return await CallbackQuery.answer(_["gstats_4"], show_alert=True)

    upl = back_stats_buttons(_)
    await CallbackQuery.answer()

    p_core = psutil.cpu_count(logical=False)
    t_core = psutil.cpu_count(logical=True)
    ram = str(round(psutil.virtual_memory().total / (1024.0**3))) + " GB"
    try:
        cpu_freq = psutil.cpu_freq().current
        cpu_freq = f"{round(cpu_freq / 1000, 2)} GHz" if cpu_freq >= 1000 else f"{round(cpu_freq, 2)} MHz"
    except:
        cpu_freq = "Unavailable"

    hdd = psutil.disk_usage("/")
    total = hdd.total / (1024.0**3)
    used = hdd.used / (1024.0**3)
    free = hdd.free / (1024.0**3)

    call = await mongodb.command("dbstats")
    datasize = call["dataSize"] / 1024
    storage = call["storageSize"] / 1024
    served_chats = len(await get_served_chats())
    served_users = len(await get_served_users())
    sudo_count = len(await get_sudoers())

    text = (
        f"**📊 {app.mention} System Stats**\n\n"
        f"**🔧 System:**\n"
        f"• OS : `{platform.system()}`\n"
        f"• RAM : `{ram}`\n"
        f"• CPU Cores : `{p_core}` Physical | `{t_core}` Logical\n"
        f"• Frequency : `{cpu_freq}`\n\n"
        f"**💾 Disk & Database:**\n"
        f"• Disk : `{total:.2f} GB` Total | `{used:.2f} GB` Used | `{free:.2f} GB` Free\n"
        f"• DB Size : `{datasize:.2f} MB`\n"
        f"• Storage Used : `{storage:.2f} MB`\n"
        f"• Collections : `{call['collections']}` | Objects : `{call['objects']}`\n\n"
        f"**👥 Usage:**\n"
        f"• Served Chats : `{served_chats}`\n"
        f"• Served Users : `{served_users}`\n\n"
        f"**🔒 Moderation:**\n"
        f"• Banned Users : `{len(BANNED_USERS)}`\n"
        f"• Sudoers : `{sudo_count}`\n"
        f"• Modules : `{len(ALL_MODULES)}`\n\n"
        f"**⚙️ Software:**\n"
        f"• Python : `{pyver.split()[0]}`\n"
        f"• Pyrogram : `{pyrover}`\n"
        f"• PyTgCalls : `{pytgver}`"
    )

    med = InputMediaPhoto(media=config.STATS_IMG_URL, caption=text)
    try:
        await CallbackQuery.edit_message_media(media=med, reply_markup=upl)
    except MessageIdInvalid:
        await CallbackQuery.message.reply_photo(
            photo=config.STATS_IMG_URL, caption=text, reply_markup=upl
        )
