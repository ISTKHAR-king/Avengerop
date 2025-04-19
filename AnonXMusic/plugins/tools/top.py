from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from AnonXMusic.core.mongo import mongodb
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
            text += f"**{i}. {chat.title.ljust(30)}** — {str(count).rjust(3)} songs\n"
        except:
            text += f"**{i}. [Group ID: {group_id}]** — {str(count).rjust(3)} songs\n"

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
            text += f"**{i}. {chat.title.ljust(30)}** — {str(count).rjust(3)} songs\n"
        except:
            text += f"**{i}. [Group ID: {group_id}]** — {str(count).rjust(3)} songs\n"

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
            text += f"**{i}. {chat.title.ljust(30)}** — {str(count).rjust(3)} songs\n"
        except:
            text += f"**{i}. [Group ID: {group_id}]** — {str(count).rjust(3)} songs\n"

    await callback_query.message.edit_text(text)

# Helper: Show top users overall (with mentions)
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
            text += f"**{i}.** [{user.first_name}](tg://user?id={user.id}) — {count} songs\n"
        except:
            text += f"**{i}. [User ID: {user_id}]** — {count} songs\n"

    await callback_query.message.edit_text(text, disable_web_page_preview=True)

# Update song count when a song is played via /play or /vplay
@app.on_message(filters.text & filters.command())
async def song_played(client, message: Message):
    if message.text.startswith(("/play", "/vplay")):  # Check if command is /play or /vplay
        if not message.from_user:
            return  # skip if no user info (like anonymous admin or channel)

        group_id = message.chat.id
        user_id = message.from_user.id
        await update_song_count(group_id, user_id)


# Helper: Get user's song count and rank
async def get_user_profile(user_id):
    user_counter = {}

    # Fetch all song stats
    records = song_stats_db.find({})
    async for record in records:
        for u_id, count in record.get("users", {}).items():
            if u_id == str(user_id):
                user_counter[u_id] = user_counter.get(u_id, 0) + count

    # Sort users by song count
    leaderboard = sorted(user_counter.items(), key=itemgetter(1), reverse=True)

    # Get the user's rank
    user_rank = next((i + 1 for i, (u_id, count) in enumerate(leaderboard) if u_id == str(user_id)), None)

    user_song_count = user_counter.get(str(user_id), 0)
    
    return user_song_count, user_rank

# Default image URL (could be a placeholder image link)
DEFAULT_IMAGE = "https://example.com/default_profile_image.jpg"

# Command: /profile
@app.on_message(filters.command("profile") & filters.group)  # Only eligible in groups
async def user_profile(client, message: Message):
    user_id = message.from_user.id
    user_song_count, user_rank = await get_user_profile(user_id)

    # Fetch the user's profile photo
    profile_photos = await client.get_user_profile_photos(user_id)
    profile_photo = profile_photos[0].file_id if profile_photos.total_count > 0 else DEFAULT_IMAGE

    if user_song_count == 0:
        text = "Your Profile\n\nYou haven't played any songs yet."
    else:
        text = "𝗠𝘂𝘀𝗶𝗰𝗮𝗹 𝗜𝗻𝗳𝗼 📢\n\n"
        text += f"📝 Name: {message.from_user.first_name}\n"
        text += f"✨ Username: @{message.from_user.username if message.from_user.username else 'N/A'}\n"
        text += f"🆔 User ID: {user_id}\n"
        text += f"🎶 Songs Played: {user_song_count}\n"
        text += f"♨️ Rank: #{user_rank}"

    # Create a close button
    close_button = InlineKeyboardMarkup([
        [InlineKeyboardButton("⏹ Close", callback_data="close_profile")]
    ])
    
    # Send the message with the user's profile photo and the close button
    if profile_photo != DEFAULT_IMAGE:
        await message.reply_photo(profile_photo, caption=text, reply_markup=close_button)
    else:
        await message.reply_photo(DEFAULT_IMAGE, caption=text, reply_markup=close_button)
    
    # Handle callback for closing the message
    @app.on_callback_query(filters.regex("close_profile"))
    async def close_profile(client, callback_query):
        await callback_query.message.delete()
