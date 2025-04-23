import os
import re
import random
import aiohttp
import aiofiles
import traceback

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from youtubesearchpython.__future__ import VideosSearch


def changeImageSize(maxWidth, maxHeight, image):
    ratio = min(maxWidth / image.size[0], maxHeight / image.size[1])
    newSize = (int(image.size[0] * ratio), int(image.size[1] * ratio))
    return image.resize(newSize, Image.ANTIALIAS)


def truncate(text):
    list = text.split(" ")
    text1, text2 = "", ""
    for i in list:
        if len(text1) + len(i) < 30:
            text1 += " " + i
        elif len(text2) + len(i) < 30:
            text2 += " " + i
    return [text1.strip(), text2.strip()]


def add_rounded_corners(im, radius):
    circle = Image.new('L', (radius * 2, radius * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radius * 2, radius * 2), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))
    alpha.paste(circle.crop((0, radius, radius, radius * 2)), (0, h - radius))
    alpha.paste(circle.crop((radius, 0, radius * 2, radius)), (w - radius, 0))
    alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)), (w - radius, h - radius))
    im.putalpha(alpha)
    return im


async def get_thumb(videoid: str):
    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            try:
                title = result["title"]
                title = re.sub("\W+", " ", title)
                title = title.title()
            except:
                title = "Unsupported Title"
            try:
                duration = result["duration"]
            except:
                duration = "Unknown Mins"
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            try:
                views = result["viewCount"]["short"]
            except:
                views = "Unknown Views"
            try:
                channel = result["channel"]["name"]
            except:
                channel = "Unknown Channel"

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        icons = Image.open("AnonXMusic/assets/icons.png")
        youtube = Image.open(f"cache/thumb{videoid}.png")
        image1 = changeImageSize(1280, 720, youtube)
        image2 = image1.convert("RGBA")

        # Create a soft gradient background
        gradient = Image.new("RGBA", image2.size, (0, 0, 0, 255))
        enhancer = ImageEnhance.Brightness(image2.filter(ImageFilter.GaussianBlur(15)))
        blurred = enhancer.enhance(0.5)
        background = Image.alpha_composite(gradient, blurred)

        Xcenter = image2.width / 2
        Ycenter = image2.height / 2
        x1 = Xcenter - 200
        y1 = Ycenter - 200
        x2 = Xcenter + 200
        y2 = Ycenter + 200
        rand = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        logo = youtube.crop((x1, y1, x2, y2))
        logo.thumbnail((340, 340), Image.ANTIALIAS)

        # Add soft shadow
        shadow = Image.new("RGBA", logo.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.ellipse((0, 0, logo.size[0], logo.size[1]), fill=(0, 0, 0, 100))
        background.paste(shadow, (110, 160), shadow)

        # Add logo with border
        logo = ImageOps.expand(logo, border=15, fill=rand)
        background.paste(logo, (100, 150))

        draw = ImageDraw.Draw(background)
        arial = ImageFont.truetype("AnonXMusic/assets/font2.ttf", 30)
        font = ImageFont.truetype("AnonXMusic/assets/font.ttf", 30)
        tfont = ImageFont.truetype("AnonXMusic/assets/font3.ttf", 45)

        stitle = truncate(title)
        draw.text((565, 180), stitle[0], (255, 255, 255), font=tfont)
        draw.text((565, 230), stitle[1], (255, 255, 255), font=tfont)
        draw.text((565, 320), f"{channel} | {views[:23]}", (255, 255, 255), font=arial)

        draw.line([(565, 385), (1130, 385)], fill="white", width=8)
        draw.line([(565, 385), (999, 385)], fill=rand, width=8)
        draw.ellipse([(999, 375), (1020, 395)], outline=rand, fill=rand, width=15)
        draw.text((565, 400), "00:00", (255, 255, 255), font=arial)
        draw.text((1080, 400), f"{duration[:23]}", (255, 255, 255), font=arial)

        picons = icons.resize((580, 62))
        background.paste(picons, (565, 450), picons)

        # Watermark: Team DeadlineTech (glowing)
        watermark_font = ImageFont.truetype("AnonXMusic/assets/font2.ttf", 24)
        watermark_text = "Team DeadlineTech"
        text_size = draw.textsize(watermark_text, font=watermark_font)
        margin = 25
        x = background.width - text_size[0] - margin
        y = background.height - text_size[1] - margin

        glow_pos = [(x + dx, y + dy) for dx in (-1, 1) for dy in (-1, 1)]
        for pos in glow_pos:
            draw.text(pos, watermark_text, font=watermark_font, fill=(0, 0, 0, 180))
        draw.text((x, y), watermark_text, font=watermark_font, fill=(255, 255, 255, 240))

        # Rounded corners for final thumbnail
        background = add_rounded_corners(background, 30)

        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass

        tpath = f"cache/{videoid}.png"
        background.save(tpath)
        return tpath

    except:
        traceback.print_exc()
        return None
