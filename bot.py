from logging import INFO
from pyrogram import Client, filters
from pytube import YouTube, exceptions
import os
import requests
import logging
import sys
from autologging import logged, traced
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
import youtube_dl
from youtube_search import YoutubeSearch
import requests

import os
from config import Config
import os
import requests
import aiohttp
import math
from pyrogram import filters, Client
from youtube_search import YoutubeSearch
from urllib.parse import urlparse
import aiofiles
import os
from random import randint
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.types import Chat, Message, User
import asyncio
from typing import Callable, Coroutine, Dict, List, Tuple, Union
import sys
import time

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=INFO)
logger = logging.getLogger(__name__)

api_id = int(os.environ["API_ID"])
api_hash = os.environ["API_HASH"]
bot_token = os.environ["BOT_TOKEN"]

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
with app:
    botname = app.get_me().username


@traced
@logged
@app.on_message(filters.command(["start", f"start@{botname}"], prefixes="/") & ~filters.edited)
def start(client, message):
    text = f"Hello {str(message.from_user.first_name)}, I am a YouTube downloader bot made by @infinitEplus." + \
        "Please see /help if you want to know how to use me."
    app.send_message(chat_id=message.chat.id, text=text)


@traced
@logged
@app.on_message(filters.command(["help", f"help@{botname}"], prefixes="/") & ~filters.edited)
def help(client, message):
    text = 'Download YT videos and audios by:\n' + \
        '/video link\n' + \
        '/audio link'
    app.send_message(chat_id=message.chat.id, text=text)


@traced
@logged
@app.on_message(filters.command(["video", f"video@{botname}"], prefixes="/") & ~filters.edited)
def video_dl(client, message):
    chat_id = message.chat.id
    link = message.text.split(maxsplit=1)[1]
    try:
        yt = YouTube(link)
        video = yt.streams.get_highest_resolution().download('res')
        caption = yt.title
        with open('a.jpg', 'wb') as t:
            t.write(requests.get(yt.thumbnail_url).content)
        thumb = open('a.jpg', 'rb')
        app.send_chat_action(chat_id, "upload_video")
        client.send_video(chat_id=chat_id, video=video, caption=caption,
                          thumb=thumb, duration=yt.length)
        if os.path.exists(video):
            os.remove(video)
        if os.path.exists('a.jpg'):
            os.remove('a.jpg')

    except exceptions.RegexMatchError:
        message.reply_text("Invalid URL.")
    except exceptions.LiveStreamError:
        message.reply_text("Live Stream links not supported.")
    except exceptions.VideoUnavailable:
        message.reply_text("Video is unavailable.")
    except exceptions.HTMLParseError:
        message.reply_text("Given URL couldn't be parsed.")


@traced
@logged
@app.on_message(filters.command(["audio", f"audio@{botname}"], prefixes="/") & ~filters.edited)
def audio_dl(client, message):
    chat_id = message.chat.id
    link = message.text.split('audio', maxsplit=1)[1]
    try:
        yt = YouTube(link)
        audio = yt.streams.get_audio_only().download('res')
        title = yt.title
        app.send_chat_action(chat_id, "upload_audio")
        with open('a.jpg', 'wb') as t:
            t.write(requests.get(yt.thumbnail_url).content)
        thumb = open('a.jpg', 'rb')
        client.send_audio(chat_id=chat_id, audio=audio, title=title,
                          thumb=thumb, performer=yt.author, duration=yt.length)
        if os.path.exists(audio):
            os.remove(audio)
        if os.path.exists('a.jpg'):
            os.remove('a.jpg')

    except exceptions.RegexMatchError:
        message.reply_text("Invalid URL.")
    except exceptions.LiveStreamError:
        message.reply_text("Live Stream links not supported.")
    except exceptions.VideoUnavailable:
        message.reply_text("Video is unavailable.")
    except exceptions.HTMLParseError:
        message.reply_text("Given URL couldn't be parsed.")

@app.on_message(filters.command(['mp3']))
def mp3(client, message):
    query = ''
    for i in message.command[1:]:
        query += ' ' + str(i)
    print(query)
    m = message.reply('🔎 Mahnı axtarılır...')
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    try:
        results = []
        count = 0
        while len(results) == 0 and count < 6:
            if count>0:
                time.sleep(1)
            results = YoutubeSearch(query, max_results=1).to_dict()
            count += 1
        # results = YoutubeSearch(query, max_results=1).to_dict()
        try:
            link = f"https://youtube.com{results[0]['url_suffix']}"
            # print(results)
            title = results[0]["title"]
            thumbnail = results[0]["thumbnails"][0]
            duration = results[0]["duration"]

            ## UNCOMMENT THIS IF YOU WANT A LIMIT ON DURATION. CHANGE 1800 TO YOUR OWN PREFFERED DURATION AND EDIT THE MESSAGE (30 minutes cap) LIMIT IN SECONDS
            # if time_to_seconds(duration) >= 1800:  # duration limit
            #     m.edit("Exceeded 30mins cap")
            #     return

            views = results[0]["views"]
            thumb_name = f'thumb{message.message_id}.jpg'
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, 'wb').write(thumb.content)

        except Exception as e:
            print(e)
            m.edit('Heç nə tapmadım.\n\nOrfoqrafiyanı bir az dəyişməyə çalışın.')
            return
    except Exception as e:
        m.edit(
            "✖️ Heç nə tapmadım.\n\nOrfoqrafiyanı bir az dəyişməyə çalışın."
        )
        print(str(e))
        return
    m.edit("⏬ Yükləyirəm.")
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
        rep = f'🎧 **Başlıq**: [{title[:35]}]({link})\n⏳ **Müddəti**: `{duration}`\n👁‍🗨 **Baxış**: `{views}`'
        secmul, dur, dur_arr = 1, 0, duration.split(':')
        for i in range(len(dur_arr)-1, -1, -1):
            dur += (int(dur_arr[i]) * secmul)
            secmul *= 60
        message.reply_audio(audio_file, caption=rep, parse_mode='md',quote=False, title=title, duration=dur, thumb=thumb_name)
        m.delete()
    except Exception as e:
        m.edit('❌ XETA')
        print(e)
    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as e:
        print(e) 

app.run()
