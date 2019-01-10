import gspread
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
import os
import sys
import json
import datetime
sys.path.append("../components")

from logging_service import LoggingService

if "PROJECT_LOB_CONFIG" not in os.environ:
    print("PROJECT_LOB_CONFIG must be an environment variable set to "
          "the path of a JSON config file.")
    sys.exit()

config_path = os.environ["PROJECT_LOB_CONFIG"]
with open(config_path) as f:
    config = json.load(f)["hot_lob"]

service = LoggingService(os.environ[config["sheet_key"]], os.environ[config["cred_file"]], None, None, [])

today = datetime.datetime.today()
dtf = "{}_{}_{}".format(today.month, today.day, today.year)
dt = "{}/{}/{}".format(today.month, today.day, today.year)
# grab the last two full days worth of entries to protect from over/under fetching
data = service.all_entries()[-864: ]

tank_data = {}
for d in data:
    if d["Date"] != dt:
        continue
    if d["Tank"] not in tank_data:
        tank_data[d["Tank"]] = {"ts": [], "vals": []}
    t = tank_data[d["Tank"]]
    t["ts"].append(d["Time"])
    t["vals"].append(d["Temp_C"])

if len(tank_data.keys()):
    for tank in tank_data:
        plt.plot(tank_data[1]["ts"], tank_data[tank]["vals"])

    plt.savefig("{}.figure.png".format(dtf))

    # # write the filtered data to a json file
    with open(str(datetime.datetime.now().timestamp()).split('.')[0], "w+") as f:
        json.dump(tank_data, f)
