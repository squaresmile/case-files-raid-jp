import pandas as pd
import pandas.plotting._converter as pandacnv
import matplotlib.pyplot as plt

HP = 60000000

parsed = pd.read_csv("parsed_data.csv", parse_dates=["Time"])
manual = pd.read_csv("manual_data.csv", parse_dates=["Time"])
manual["Time"] = manual["Time"]
raid_data = pd.concat([manual, parsed])
raid_data = raid_data.drop_duplicates("Time").sort_values("Time")

x = raid_data["Time"][1:]
y = raid_data["Kills"].diff()[1:] / raid_data['Time'].diff().dt.total_seconds()[1:]
# print(raid_data.iloc[1:][y<0])
print(sum(y<0))
x = x[y>0]
y = y[y>0]
x = x[1:-1]
y = y.rolling(3, center=True).mean()[1:-1]

pandacnv.register()
plt.style.use('seaborn')
fig, ax = plt.subplots(figsize=(14, 7.5))
ax.plot(x, y)
# plt.plot_date(x, y)
# fig.autofmt_xdate()
plt.title("JP case files raid KPS")
plt.xlabel("Japan Standard Time")
plt.ylabel("KPS")
plt.savefig("chart.png", dpi=200, bbox_inches='tight')


avg_rate = y[-10:].mean()
time_to_kill = (HP - raid_data["Kills"].iloc[-1])/avg_rate
time_to_kill = pd.to_timedelta(time_to_kill, unit='s')

print(f"Time to death: {time_to_kill}")
