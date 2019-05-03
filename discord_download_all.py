import os
import discord
import requests

client = discord.Client()
headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'}
with open("discord_api_token.txt") as f:
    discord_api_token = f.read().strip()

def download_raid_screenshots(user, url):
    file_name = url.split("/")[-1]
    r = requests.get(url, headers=headers, allow_redirects=True)
    if not os.path.exists(f"screenshots/{user}"):
        os.mkdir(f"screenshots/{user}")
    with open(f"screenshots/{user}/{file_name}", "wb") as ss_img:
        ss_img.write(r.content)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    for channel in client.get_all_channels():
        if str(channel) == "jp-event-raid":
            async for message in channel.history():
                if message.attachments:
                    user = str(message.author.display_name)
                    for attachment in message.attachments:
                        print(f"{user} {attachment.url}")
                        download_raid_screenshots(user, attachment.url)

client.run(discord_api_token)
