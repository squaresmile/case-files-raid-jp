import os
from datetime import timezone
import discord
import requests

client = discord.Client()
headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'}
with open("discord_api_token.txt") as f:
    discord_api_token = f.read().strip()
if not os.path.exists("screenshots"):
    os.mkdir("screenshots")

async def download_raid_screenshots(time, user, url):
    print(f"{time:%H:%M} {user}: {url}")
    file_name = url.split("/")[-1]
    r = requests.get(url, headers=headers, allow_redirects=True)
    if not os.path.exists(f"screenshots/{user}"):
        os.mkdir(f"screenshots/{user}")
    with open(f"screenshots/{user}/{file_name}", "wb") as ss_img:
        ss_img.write(r.content)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if str(message.channel.name) == "jp-event-raid":
        if message.attachments:
            user = str(message.author.display_name)
            time = message.created_at.replace(tzinfo=timezone.utc).astimezone(tz=None)
            for attachment in message.attachments:
                await download_raid_screenshots(time, user, attachment.url)

client.run(discord_api_token)
