import os
from datetime import datetime
import discord

LINKS_FILE = "discord_links.csv"
LAST_DATE = datetime(2019, 5, 22)

client = discord.Client()
headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'}
with open("discord_api_token.txt", encoding="utf-8") as f:
    discord_api_token = f.read().strip()

if not os.path.exists(LINKS_FILE):
    with open(LINKS_FILE, "w") as f:
        f.write("UTC Time,User,Attachment Link\n")

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    for channel in client.get_all_channels():
        if str(channel) == "rashoumon-raid":
            async for message in channel.history(limit=None):
                with open(LINKS_FILE, "a", encoding="utf-8") as out:
                    if message.attachments:
                        user = str(message.author.display_name)
                        print(user)
                        time = message.created_at
                        if time < LAST_DATE:
                            for attachment in message.attachments:
                                out.write(f"{time},{user},{attachment.url}\n")

client.run(discord_api_token)
