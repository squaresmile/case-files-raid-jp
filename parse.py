import json
import os
from datetime import datetime, timedelta
from tqdm import tqdm
import requests
import numpy as np
import cv2
import screenshot_parse

INPUT = "discord_links.csv"
OUTPUT = "parsed_hp.csv"
HEADERS = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'}

def url_to_image(url):
    response = requests.get(url, headers=HEADERS, allow_redirects=True)
    image = np.asarray(bytearray(response.content), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    if image is None:
        raise Exception(f"OpenCV can't read {url}")
    return image


if __name__ == "__main__":
    with open("timezone.json", "r", encoding='utf-8') as f:
        timezone_offset = json.load(f)
    with open(INPUT, "r") as f:
        lines = f.readlines()
    if not os.path.exists(OUTPUT):
        with open(OUTPUT, "w", encoding='utf-8') as f:
            f.write("Japan Standard Time,Kills,Discord Message UTC Time,User,Link\n")
    with open(OUTPUT, "a", encoding='utf-8') as f:
        for line in tqdm(lines[1:]):
            message_utc_time, user, link = line.split(",")
            message_utc_time = datetime.strptime(message_utc_time, "%Y-%m-%d %H:%M:%S.%f")
            link = link.strip()
            file_name = link.split("/")[-1]
            if file_name == "unknown.png":
                japan_time = message_utc_time + timedelta(hours=9)
            elif file_name.startswith("Screenshot_2019-"):
                japan_time = datetime.strptime(file_name[11:30], "%Y-%m-%d-%H-%M-%S") + timedelta(hours=timezone_offset[user])
            elif file_name.startswith("Screenshot_2019"):
                japan_time = datetime.strptime(file_name[11:26], "%Y%m%d-%H%M%S") + timedelta(hours=timezone_offset[user])
            img = url_to_image(link)
            kill = screenshot_parse.parse_hp(img)
            f.write(f"{japan_time},{kill},{line}")
