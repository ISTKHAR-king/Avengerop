import re
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

# Get this value from my.telegram.org/apps
API_ID = int(getenv("24620300"))
API_HASH = getenv("9a098f01aa56c836f2e34aee4b7ef963")

# Get your token from @BotFather on Telegram.
BOT_TOKEN = getenv("5709725711:AAECCIW4_ItA0vI1M0f_z1w6DT_2ZSVGqXI")

# Get your mongo url from cloud.mongodb.com
MONGO_DB_URI = getenv("MONGO_DB_URI", "mongodb+srv://SpotifyNew:Pv7X6VKj0LBLYPpb@spotify.4dojmsr.mongodb.net/?retryWrites=true&w=majority&appName=Spotify")

DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 9000))

# Set this to true if you want post ads automatically
ADS_MODE = getenv("ADS_MODE", None)

# Chat id of a group for logging bot's activities
LOGGER_ID = int(getenv("LOGGER_ID", -1001802598180))

# Get this value from @FallenxBot on Telegram by /id
OWNER_ID = int(getenv("OWNER_ID", 7765692814))

## Fill these variables if you're deploying on heroku.
# Your heroku app name
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
# Get it from http://dashboard.heroku.com/account
HEROKU_API_KEY = getenv("HEROKU_API_KEY")

UPSTREAM_REPO = getenv(
    "UPSTREAM_REPO",
    "https://github.com/Raghav-afk25/botz-hub",
)
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")
GIT_TOKEN = getenv(
    "GIT_TOKEN", None
)  # Fill this variable if your upstream repository is private

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/DeadlineTechTeam")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/DeadlineTechsupport")

# Set this to True if you want the assistant to automatically leave chats after an interval
AUTO_LEAVING_ASSISTANT = bool(getenv("AUTO_LEAVING_ASSISTANT", True))


# Get this credentials from https://developer.spotify.com/dashboard
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "95f4f5c6df5744698035a0948e801ad9")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "4b03167b38c943c3857333b3f5ea95ea")


# Maximum limit for fetching playlist's track from youtube, spotify, apple links.
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 25))


# Telegram audio and video file size limit (in bytes)
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", 104857600))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", 1073741824))
# Checkout https://www.gbmb.org/mb-to-bytes for converting mb to bytes


# Get your pyrogram v2 session from @StringFatherBot on Telegram
STRING1 = getenv("STRING_SESSION", "BQF3rQwAdd8hIJtMVANLqDNdcItgKWlucGMDW0Jri_G5_Mf6tsKDYgECsUUT2hlnpsYhMHXomdmjdNOORvSRojyR6idppVUqEYtE6xiI3EbdMnKP5X-XJ7jorJ--a2OUofPJ8XINDudV-fLSruWg2LfeYgqXjqpyrBc6I0or4EM4um9eGAcvnIh2jWF-QN0Pue8nw4mUF99JpUfYc9NHF_DigHPTZDILaL2dmdOVrp16SanxuRAC30eKVUhn6BjQi7IyfNliaUG3umQf2t0VVZ3Pj5PS1-4nKm-smpKTqicdCdNL-YZKKDpdnzQgh8hjlyxISfoAE1bwbpJ8RQqf1THcAUTZfQAAAAHS5ocSAA")
STRING2 = getenv("STRING_SESSION2", "BQF3rQwAstrAmKxhPon-Ptlv26XM0nWCpQfYvBzJrTZzvpNcn769oGaoXb3PVcGu-NxnSPKGsULu7ddnfBtnSqtjJbhxr2uBnqy24wDBPPtvZo2oKYcZHhjZlh7rS9Cjb73qONZzjCHiLnqcf7wdSngqJ-bwXJWe2MB_uOWQwvIhDj8B9r89FxtGEY-QJ4BRsdkboiJ6rxrkAUjYi52YXtdxZUZZb-mJiPV9h7LHuO4WD2f50CCANUNG1ySYMQq3EeKGGrLgbjivB7HjHLCwXez4xHG4N1U5V0KZQihvjvgw6imkal_0b94kEWlVg8I3Pm2D2O4EqhlR7yk4YzV5Vx8LXsYz1gAAAAGgRV9bAA")
STRING3 = getenv("STRING_SESSION3", "BQF3rQwAenFhXOpkGKX7-aMTlyqbUjjajCWmm8IjOs0l_nHZdvDUdOjEWA3xhAwcyEWOgme7KUHG9YaMR-qSS72d8gkWi6OMLcr5LZ8x7_5K5H1W_SuZJmZp32X1-_Z7WcODrf3pL7_d3er0RjByxeeeuM7awouw5-Zo7XlNofjYxbQsrQYc0sfcC32T8Xsobu0t1gjMnKRQmKbuwmXvIEAaMS6Pp0k6k91u6l1fg-qRyU5Vs8sENFQD1glaLhB8vnKUQ7rQYVpLgBQ3OY9alSBdtwzVZWuBAAmnAQ-hX9j_vJhnCy8612V_tfVHQZ5gAY9EG7iNYDE4uHy8D56iHeywXbB8MQAAAAGhW2XzAA")
STRING4 = getenv("STRING_SESSION4", "BQF3rQwAPM9Qwb7eOrx4zj15Os7_kVqDuMm44Rg0f0MjiO2Ar7G6al4ed4-dcfeqH3Qe1GfH9nv0YD1UsHJMBOUXzDE9pwpBH1aitQG-Z6ULanu4jeE9lY12nEjoV3lvRuOZm0k4ZEZnDvQisatQoWTJ3mgtzofudlmowbK92Ln9b5te8DCevZS48ZeU1cuNqVAowbjdG0npRQSwhXz0lcG9EAGPDtxbLDjVHC9cRiZM6YLMJQ1RZvVhl7swtfKtQ-8H0-rP7gxxMrdlVK75N1B_BuPt_nQ_dwuUWtJpW8bCV4FZk84zpBqdDtz79CVNf34BTuQFn4C7k81TcEzHnB3cSP3YiQAAAAHmlfNEAA")
STRING5 = getenv("STRING_SESSION5", "BQF3rQwAgl9einaQdf_bfiukdbthJM_SGbPV9yPHf28kpPL3-Kw_WFo3T3SrkNWwU2rBq06J7zDZuDDMLsfREAt6OkJcOAsr9xQGoxlaVO7G6sdYahwKMsjwKecSXQSvWEI5EddJozbxzyj8iJDayOezu90kpl3vvSh7p2eKA6_kLQ9T6BkJgVk31YuiSelYUzPC-Gi7lPxq1m4Ay0GlXf1hQUonwbxNArEDtP4TC7dV6fSXG1WH2U7wG5zixrcT9QRFzjmnw3eOzFPFrM_99vwSJcsF6EHY6GsuoLBoyY28cbtUEaCJwKQVzQ7tpm_WadZidBlnELXNNhIvLoFbBAgd-mPU2AAAAAGqeMbeAA")


BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}


START_IMG_URL = getenv(
    "START_IMG_URL", "https://telegra.ph/file/4bff7df05636d1cca7532.jpg"
)
PING_IMG_URL = getenv(
    "PING_IMG_URL", "https://telegra.ph/file/4bff7df05636d1cca7532.jpg"
)
PLAYLIST_IMG_URL = "https://te.legra.ph/file/4ec5ae4381dffb039b4ef.jpg"
STATS_IMG_URL = "https://graph.org/file/15606f735b1e4e3c98e5e.jpg"
TELEGRAM_AUDIO_URL = "https://te.legra.ph/file/6298d377ad3eb46711644.jpg"
TELEGRAM_VIDEO_URL = "https://te.legra.ph/file/6298d377ad3eb46711644.jpg"
STREAM_IMG_URL = "https://te.legra.ph/file/bd995b032b6bd263e2cc9.jpg"
SOUNCLOUD_IMG_URL = "https://te.legra.ph/file/bb0ff85f2dd44070ea519.jpg"
YOUTUBE_IMG_URL = "https://te.legra.ph/file/6298d377ad3eb46711644.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://te.legra.ph/file/37d163a2f75e0d3b403d6.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://te.legra.ph/file/b35fd1dfca73b950b1b05.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://te.legra.ph/file/95b3ca7993bbfaf993dcb.jpg"


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))


DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))


if SUPPORT_CHANNEL:
    if not re.match("(?:http|https)://", SUPPORT_CHANNEL):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHANNEL url is wrong. Please ensure that it starts with https://"
        )

if SUPPORT_CHAT:
    if not re.match("(?:http|https)://", SUPPORT_CHAT):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHAT url is wrong. Please ensure that it starts with https://"
        )
