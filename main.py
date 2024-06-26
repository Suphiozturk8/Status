import os, time, shutil, psutil, datetime

from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, filters
from pyrogram.types import Message, InputMediaPhoto


NAME = "ServerStats"
API_ID = 6
API_HASH = "eb06d4abfb49dc3eeb1aeb98ae0f581e"
BOT_TOKEN = ""

app = Client(
    name=NAME,
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

BotStartTime = time.time()


def get_readable_time(seconds: int) -> str:
    result = ""
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)

    if days != 0:
        result += f"{days}d "
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)

    if hours != 0:
        result += f"{hours}h "
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)

    if minutes != 0:
        result += f"{minutes}m "

    seconds = int(seconds)
    result += f"{seconds}s "
    return result


def get_readable_bytes(size: str) -> str:
    dict_power_n = {0: "", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}

    if not size:
        return ""
    power = 2**10
    raised_to_pow = 0

    while size > power:
        size /= power
        raised_to_pow += 1

    return f"{str(round(size, 2))} {dict_power_n[raised_to_pow]}B"


@app.on_message(
    filters.command(
        ["s", "stats", "serverstats"]
    )
)
async def stats(_, message: Message):
    await message.reply(
        "Please wait...",
        quote=True
    )
    image = Image.open('./statsbg.jpg').convert('RGB')
    IronFont = ImageFont.truetype("./IronFont.otf", 42)
    draw = ImageDraw.Draw(image)

    def draw_progressbar(coordinate, progress):
        progress = 110+(progress*10.8)
        draw.ellipse((105, coordinate-25, 127 , coordinate), fill='#FFFFFF')
        draw.rectangle((120, coordinate-25, progress, coordinate), fill='#FFFFFF')
        draw.ellipse((progress-7, coordinate-25, progress+15, coordinate), fill='#FFFFFF')
        
    total, used, free = shutil.disk_usage(".")
    process = psutil.Process(os.getpid())

    botuptime = get_readable_time(time.time() - BotStartTime)
    osuptime  =  get_readable_time(time.time() - psutil.boot_time())
    botusage = f"{round(process.memory_info()[0]/1024 ** 2)} MiB"

    upload= get_readable_bytes(psutil.net_io_counters().bytes_sent)
    download= get_readable_bytes(psutil.net_io_counters().bytes_recv)

    cpu_percentage = psutil.cpu_percent()
    cpu_count = psutil.cpu_count()

    ram_percentage = psutil.virtual_memory().percent
    ram_total = get_readable_bytes(psutil.virtual_memory().total)
    ram_used = get_readable_bytes(psutil.virtual_memory().used)	

    disk_percenatge = psutil.disk_usage("/").percent
    disk_total = get_readable_bytes(total)
    disk_used = get_readable_bytes(used)
    disk_free = get_readable_bytes(free)

    caption = f"""
**OS Uptime:** {osuptime}
**Bot Usage:** {botusage}

**Total Space:** {disk_total}
**Free Space:** {disk_free}

**Download:** {download}
**Upload:** {upload}
    """

    start = datetime.datetime.now()
    msg = await message.reply_photo(
        photo="https://te.legra.ph/file/30a82c22854971d0232c7.jpg",
        caption=caption,
        quote=True
    )
    end = datetime.datetime.now()

    draw_progressbar(243, int(cpu_percentage))
    draw.text((225,153), f"( {cpu_count} core, {cpu_percentage}% )", (255, 255, 255), font=IronFont)	

    draw_progressbar(395, int(disk_percenatge))
    draw.text((335,302), f"( {disk_used} / {disk_total}, {disk_percenatge}% )", (255, 255, 255), font=IronFont)

    draw_progressbar(533, int(ram_percentage))
    draw.text((225,445), f"( {ram_used} / {ram_total}, {ram_percentage}% )", (255, 255, 255), font=IronFont)

    draw.text((335,600), f"{botuptime}", (255, 255, 255), font=IronFont)
    draw.text((857,607), f"{(end-start).microseconds/1000} ms", (255, 255, 255), font=IronFont)

    image.save("stats.png")
    await msg.edit_media(
        media=InputMediaPhoto(
            "stats.png",
            caption=caption
        )
    )
    os.remove("stats.png")


print(f"{NAME} Bot is runing...")
app.run()
