import os
import re
import json
from datetime import datetime
from datetime import timedelta
import numpy as np
import pandas as pd
import pandas.plotting._converter as pandacnv
import matplotlib.pyplot as plt
import pytesseract
import cv2

HP = 60000000

def get_qp_from_text(text):
    qp = 0
    power = 1
    # re matches left to right so reverse the list to process lower orders of magnitude first.
    for match in re.findall('[0-9]+', text)[::-1]:
        qp += int(match) * power
        power *= 1000

    return qp

if os.path.exists("manual_data.csv"):
    manual_data = pd.read_csv("manual_data.csv", parse_dates=["Time"])

dict_df = {"File": [], "Time": [], "Kills":[]}
with open("timezone.json", "r", encoding='utf-8') as f:
    timezone_offset = json.load(f)
user_list = os.listdir("screenshots")

for user in user_list:
    file_list = os.listdir(f"screenshots/{user}")
    file_list = [f for f in file_list if f.lower().endswith(".jpg") or f.lower().endswith(".png")]
    user_tz = timezone_offset[user]
    for file in file_list:
        if user == "Aurion":
            orig_time = file[11:30]
            orig_time = datetime.strptime(orig_time, "%Y-%m-%d-%H-%M-%S")
        else:
            orig_time = file[11:26]
            orig_time = datetime.strptime(orig_time, "%Y%m%d-%H%M%S")
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
            if manual_data is not None and file not in list(manual_data["File"]):
                print(f"{file},{time}")

df = pd.DataFrame.from_dict(dict_df)
df = df.sort_values("Time")
df.to_csv("parsed_data.csv", index=False)

if manual_data is not None:
    raid_data = pd.concat([manual_data, df])
else:
    raid_data = df
raid_data = raid_data.drop_duplicates("Time").sort_values("Time")

# Increasing kill count only
raid_data = raid_data[raid_data["Kills"] > raid_data["Kills"].shift(1).fillna(0)]

x = raid_data["Time"][1:]
y = raid_data["Kills"].diff()[1:] / raid_data['Time'].diff().dt.total_seconds()[1:]
x = x[1:-1]
y = y.rolling(3, center=True).mean()[1:-1]

pandacnv.register()
plt.style.use('seaborn')
fig, ax = plt.subplots(figsize=(14, 7.5))
ax.plot(x, y)
# plt.plot_date(x, y)
# fig.autofmt_xdate()
update_time = x.iloc[-1]
plt.title(f"JP case files raid KPS - updated {update_time:%Y-%m-%d %H:%M} JST")
plt.xlabel("Japan Standard Time")
plt.ylabel("Kills per Second")
plt.savefig("chart.png", dpi=200, bbox_inches='tight')

avg_rate = raid_data["Kills"].iloc[-1] / (raid_data["Time"].iloc[-1] - raid_data["Time"].iloc[0]).total_seconds()
time_to_kill = (HP - raid_data["Kills"].iloc[-1])/avg_rate
time_to_kill = pd.to_timedelta(time_to_kill, unit='s')

print(f"Time to death: {time_to_kill}")
