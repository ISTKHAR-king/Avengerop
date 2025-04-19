from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from AnonXMusic.Core.mongo import mongodb
from datetime import datetime, timedelta
from operator import itemgetter

# Mongo Collections
song_stats_db = mongodb.song_stats

# Helper: Update song count for a group
async def update_song_count(group_id, user_id):
    today_date = datetime.utcnow().strftime("%Y-%m-%d")

    # Update the song count in MongoDB for overall, daily, and user-specific counts
    await song_stats_db.update_one(
        {"group_id": group_id},
        {
            "$inc": {
                "overall_count": 1,  # Increment overall song count
                f"daily.{today_date}": 1,  # Increment daily song count
                f"users.{str(user_id)}": 1  # Increment song count for the user
            }
        },
        upsert=True  # Create a new record if it doesn't exist
    )

# Command: Show leaderboard menu
@app.on_message(filters.command("leaderboard"))
async def leaderboard_menu(client, message: Message):
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🎶 Overall Songs", callback_data="overall_songs"),
                InlineKeyboardButton("📅 Today’s Songs", callback_data="today_songs")
            ],
            [
                InlineKeyboardButton("📊 Weekly Songs", callback_data="weekly_songs"),
                InlineKeyboardButton("🏆 Top Users", callback_data="top_users")
            ]
        ]
    )
    await message.reply_text(
        "**📈 Music Leaderboard Menu 📈**\n\nChoose a category below to view rankings!",
        reply_markup=buttons
    )

# Callback Handler
@app.on_callback_query(filters.regex("^(overall_songs|today_songs|weekly_songs|top_users)$"))
async def leaderboard_callback(client, callback_query):
    data = callback_query.data
    if data == "overall_songs":
        await show_overall_leaderboard(client, callback_query)
    elif data == "today_songs":
        await show_today_leaderboard(client, callback_query)
    elif data == "weekly_songs":
        await show_weekly_leaderboard(client, callback_query)
    elif data == "top_users":
        await show_top_users(client, callback_query)

# Helper: Show overall songs leaderboard
async def show_overall_leaderboard(client, callback_query):
    records = song_stats_db.find({})
    leaderboard = []
    async for record in records:
        leaderboard.append((record["group_id"], record.get("overall_count", 0)))

    leaderboard = sorted(leaderboard, key=itemgetter(1), reverse=True)[:10]
    if not leaderboard:
        return await callback_query.message.edit_text("No data found!")

    text = "🏆 **Top 10 Groups (Overall Songs Played)** 🏆\n\n"
    for i, (group_id, count) in enumerate(leaderboard, 1):
        try:
            chat = await client.get_chat(group_id)
            text += f"**{i}. {chat.title}** — {count} songs\n"
        except:
            text += f"**{i}. [Group ID: {group_id}]** — {count} songs\n"

    await callback_query.message.edit_text(text)

# Helper: Show today's leaderboard
async def show_today_leaderboard(client, callback_query):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    records = song_stats_db.find({})
    leaderboard = []
    async for record in records:
        count = record.get("daily", {}).get(today, 0)
        leaderboard.append((record["group_id"], count))

    leaderboard = sorted(leaderboard, key=itemgetter(1), reverse=True)[:10]
    if not leaderboard or leaderboard[0][1] == 0:
        return await callback_query.message.edit_text("No songs played today!")

    text = "📅 **Top 10 Groups (Today’s Songs Played)** 📅\n\n"
    for i, (group_id, count) in enumerate(leaderboard, 1):
        try:
            chat = await client.get_chat(group_id)
            text += f"**{i}. {chat.title}** — {count} songs\n"
        except:
            text += f"**{i}. [Group ID: {group_id}]** — {count} songs\n"

    await callback_query.message.edit_text(text)

# Helper: Show weekly leaderboard
async def show_weekly_leaderboard(client, callback_query):
    today = datetime.utcnow()
    last_week = today - timedelta(days=7)
    dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

    records = song_stats_db.find({})
    leaderboard = []
    async for record in records:
        total = sum(record.get("daily", {}).get(d, 0) for d in dates)
        leaderboard.append((record["group_id"], total))

    leaderboard = sorted(leaderboard, key=itemgetter(1), reverse=True)[:10]
    if not leaderboard or leaderboard[0][1] == 0:
        return await callback_query.message.edit_text("No songs played this week!")

    text = "📊 **Top 10 Groups (This Week’s Songs Played)** 📊\n\n"
    for i, (group_id, count) in enumerate(leaderboard, 1):
        try:
            chat = await client.get_chat(group_id)
            text += f"**{i}. {chat.title}** — {count} songs\n"
        except:
            text += f"**{i}. [Group ID: {group_id}]** — {count} songs\n"

    await callback_query.message.edit_text(text)

# Helper: Show top users overall
async def show_top_users(client, callback_query):
    records = song_stats_db.find({})
    user_counter = {}

    async for record in records:
        for user_id, count in record.get("users", {}).items():
            user_counter[user_id] = user_counter.get(user_id, 0) + count

    leaderboard = sorted(user_counter.items(), key=itemgetter(1), reverse=True)[:10]
    if not leaderboard:
        return await callback_query.message.edit_text("No user data found!")

    text = "🏆 **Top 10 Users (Overall Songs Played)** 🏆\n\n"
    for i, (user_id, count) in enumerate(leaderboard, 1):
        try:
            user = await client.get_users(int(user_id))
            text += f"**{i}. {user.first_name}** — {count} songs\n"
        except:
            text += f"**{i}. [User ID: {user_id}]** — {count} songs\n"

    await callback_query.message.edit_text(text)

# Update song count when a song is played
@app.on_message(filters.command("play"))  # Replace with your actual play trigger
async def song_played(client, message: Message):
    group_id = message.chat.id
    user_id = message.from_user.id
    await update_song_count(group_id, user_id)
    await message.reply_text(f"🎶 **{message.from_user.first_name}** played a song in {message.chat.title}!")

