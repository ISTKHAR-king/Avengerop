from pyrogram import Client, filters
from pyrogram.types import (
    Message, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    CallbackQuery
)
from datetime import datetime, timedelta
from operator import itemgetter
from AnonXMusic import app
from AnonXMusic.utils.database import song_stats_db

# Default placeholder image
DEFAULT_IMAGE = "https://telegra.ph/file/5c8b65dd0c2c63d55a406-789e86998c5e1cc434.jpg"

# ───── Helpers ─────────────────────────────────────────

async def update_song_count(group_id: int, user_id: int):
    try:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        await song_stats_db.update_one(
            {"group_id": group_id},
            {
                "$inc": {
                    "overall_count": 1,
                    f"daily.{today}": 1,
                    f"users.{user_id}": 1
                }
            },
            upsert=True
        )
        print("Song count updated successfully!")
    except Exception as e:
        print(f"Error updating song count: {e}")

async def get_user_profile(user_id: int):
    user_counter = {}
    async for rec in song_stats_db.find({}):
        for u, c in rec.get("users", {}).items():
            user_counter[u] = user_counter.get(u, 0) + c

    sorted_users = sorted(user_counter.items(), key=itemgetter(1), reverse=True)
    count = user_counter.get(str(user_id), 0)
    rank = next((i+1 for i, (u, _) in enumerate(sorted_users) if u == str(user_id)), None)
    return count, rank

# ───── Handlers ────────────────────────────────────────

@app.on_message(filters.command("leaderboard") & filters.group)
async def leaderboard_menu(client: Client, message: Message):
    print("Leaderboard command received")
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎶 Overall Top Groups", callback_data="overall_songs"),
            InlineKeyboardButton("📅 Today Top Groups", callback_data="today_songs")
        ],
        [
            InlineKeyboardButton("📊 Weekly Top Groups", callback_data="weekly_songs"),
            InlineKeyboardButton("🏆 Overall Top Users", callback_data="top_users")
        ]
    ])
    await message.reply_text("📈 Music Leaderboard — choose one:", reply_markup=kb)

@app.on_message(filters.command("profile") & filters.group)
async def user_profile(client: Client, message: Message):
    uid = message.from_user.id
    count, rank = await get_user_profile(uid)
    
    # Ensure the correct method is called for getting user profile photos
    try:
        photos = await client.get_user_profile_photos(uid)
        photo = photos[0].file_id if photos.total_count else DEFAULT_IMAGE
    except AttributeError:
        # In case the method doesn't exist, set a default photo
        photo = DEFAULT_IMAGE

    if count == 0:
        text = "Your Profile\n\nYou haven't played any songs yet."
    else:
        uname = message.from_user.username or "N/A"
        text = (
            "Musical Info 📢\n\n"
            f"📝 Name: {message.from_user.first_name}\n"
            f"✨ Username: @{uname}\n"
            f"🆔 ID: {uid}\n"
            f"🎶 Songs Played: {count}\n"
            f"♨️ Rank: #{rank}"
        )

    kb = InlineKeyboardMarkup([[InlineKeyboardButton("⏹ Close", callback_data="close_profile")]])
    await message.reply_photo(photo, caption=text, reply_markup=kb)

@app.on_callback_query(filters.regex("^close_profile$"))
async def close_profile(client: Client, cq: CallbackQuery):
    await cq.message.delete()

@app.on_callback_query(filters.regex("^(overall_songs|today_songs|weekly_songs|top_users)$"))
async def leaderboard_callback(client: Client, cq: CallbackQuery):
    data = cq.data
    if data == "overall_songs":
        await show_overall_leaderboard(client, cq)
    elif data == "today_songs":
        await show_today_leaderboard(client, cq)
    elif data == "weekly_songs":
        await show_weekly_leaderboard(client, cq)
    elif data == "top_users":
        await show_top_users(client, cq)

# ───── Leaderboard Views ───────────────────────────────

async def show_overall_leaderboard(client: Client, cq: CallbackQuery):
    leaderboard = []
    async for record in song_stats_db.find({}):
        leaderboard.append((record["group_id"], record.get("overall_count", 0)))

    leaderboard = sorted(leaderboard, key=itemgetter(1), reverse=True)[:10]
    if not leaderboard:
        return await cq.message.edit_text("No data found!")

    text = "🏆 **Top 10 Groups (Overall Songs Played)** 🏆\n\n"
    for i, (group_id, count) in enumerate(leaderboard, 1):
        try:
            chat = await client.get_chat(group_id)
            text += f"**{i}. {chat.title}** — {count} songs\n"
        except:
            text += f"**{i}. [Group ID: {group_id}]** — {count} songs\n"

    await cq.message.edit_text(text)

async def show_today_leaderboard(client: Client, cq: CallbackQuery):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    leaderboard = []
    async for record in song_stats_db.find({}):
        count = record.get("daily", {}).get(today, 0)
        leaderboard.append((record["group_id"], count))

    leaderboard = sorted(leaderboard, key=itemgetter(1), reverse=True)[:10]
    if not leaderboard or leaderboard[0][1] == 0:
        return await cq.message.edit_text("No songs played today!")

    text = "📅 **Top 10 Groups (Today’s Songs Played)** 📅\n\n"
    for i, (group_id, count) in enumerate(leaderboard, 1):
        try:
            chat = await client.get_chat(group_id)
            text += f"**{i}. {chat.title}** — {count} songs\n"
        except:
            text += f"**{i}. [Group ID: {group_id}]** — {count} songs\n"

    await cq.message.edit_text(text)

async def show_weekly_leaderboard(client: Client, cq: CallbackQuery):
    today = datetime.utcnow()
    dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    leaderboard = []

    async for record in song_stats_db.find({}):
        total = sum(record.get("daily", {}).get(d, 0) for d in dates)
        leaderboard.append((record["group_id"], total))

    leaderboard = sorted(leaderboard, key=itemgetter(1), reverse=True)[:10]
    if not leaderboard or leaderboard[0][1] == 0:
        return await cq.message.edit_text("No songs played this week!")

    text = "📊 **Top 10 Groups (This Week’s Songs Played)** 📊\n\n"
    for i, (group_id, count) in enumerate(leaderboard, 1):
        try:
            chat = await client.get_chat(group_id)
            text += f"**{i}. {chat.title}** — {count} songs\n"
        except:
            text += f"**{i}. [Group ID: {group_id}]** — {count} songs\n"

    await cq.message.edit_text(text)

async def show_top_users(client: Client, cq: CallbackQuery):
    user_counter = {}
    async for record in song_stats_db.find({}):
        for user_id, count in record.get("users", {}).items():
            user_counter[user_id] = user_counter.get(user_id, 0) + count

    leaderboard = sorted(user_counter.items(), key=itemgetter(1), reverse=True)[:10]
    if not leaderboard:
        return await cq.message.edit_text("No user data found!")

    text = "🏆 **Top 10 Users (Overall Songs Played)** 🏆\n\n"
    for i, (user_id, count) in enumerate(leaderboard, 1):
        try:
            user = await client.get_users(int(user_id))
            text += f"**{i}.** [{user.first_name}](tg://user?id={user.id}) — {count} songs\n"
        except:
            text += f"**{i}. [User ID: {user_id}]** — {count} songs\n"

    await cq.message.edit_text(text, disable_web_page_preview=True)

