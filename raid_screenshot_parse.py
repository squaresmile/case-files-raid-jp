import os
import re
import json
from datetime import datetime
from datetime import timedelta
import numpy as np
import pandas as pd
import pytesseract
import cv2


def get_qp_from_text(text):
    qp = 0
    power = 1
    # re matches left to right so reverse the list to process lower orders of magnitude first.
    for match in re.findall('[0-9]+', text)[::-1]:
        qp += int(match) * power
        power *= 1000

    return qp

dict_df = {"File": [], "Time": [], "Kills":[]}
with open("timezone.json", "r", encoding='utf-8') as f:
    timezone_offset = json.load(f)
user_list = os.listdir("screenshots")

for user in user_list:
    file_list = os.listdir(f"screenshots/{user}")
    file_list = [f for f in file_list if f.lower().endswith(".jpg")]
    user_tz = timezone_offset[user]
    for file in file_list:
        time = file[11:26]
        orig_time = datetime.strptime(time, "%Y%m%d-%H%M%S")
        time = orig_time + timedelta(hours=user_tz)

        path = f"screenshots/{user}/{file}"
        with open(path, "rb") as f:
            rawbytes = bytearray(f.read())
        nparray = np.asarray(rawbytes, dtype=np.uint8)
        image = cv2.imdecode(nparray, cv2.IMREAD_UNCHANGED)

        h, w = image.shape[:-1]
        if h == 1440 and w == 2960:
            cropped = image[97:160, 1350:1611]
        elif h == 1080 and w == 2280:
            cropped = image[72:117, 1062:1279]
        elif h == 1080 and w == 1920:
            cropped = image[72:117, 838:1066]

        gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        _, thres = cv2.threshold(gray, 65, 255, cv2.THRESH_BINARY_INV)
        ocr = pytesseract.image_to_string(thres, config='-l eng --oem 1 --psm 7 -c tessedit_char_whitelist=,0123456789')
        ocr = get_qp_from_text(ocr)

        if ocr != 0:
            dict_df["Time"].append(time)
            dict_df["Kills"].append(ocr)
            dict_df["File"].append(file)
        if ocr == 0:
            print(f"{file}, {time}")

df = pd.DataFrame.from_dict(dict_df)
df = df.sort_values("Time")
df.to_csv("parsed_data.csv", index=False)
