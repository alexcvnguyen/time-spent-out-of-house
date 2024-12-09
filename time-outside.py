import csv
from datetime import datetime
import pytz

MELBOURNE_TZ = pytz.timezone("Australia/Melbourne") #docs : https://pypi.org/project/pytz/

def parse_datetime(date_str):
    utc_time = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    return pytz.utc.localize(utc_time).astimezone(MELBOURNE_TZ)

def calculate_time_out(data):
    total_time_out = 0
    not_home_start = None

    for entry in data:
        state = entry["state"]
        last_changed = parse_datetime(entry["last_changed"])

        if state == "not_home":
            not_home_start = last_changed
        elif state == "home" and not_home_start:
            total_time_out += (last_changed - not_home_start).total_seconds()
            not_home_start = None
    return total_time_out

def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return int(hours), int(minutes), int(seconds)

def read_csv(filename):
    data = []
    first_date = None
    last_date = None

    with open(filename, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            last_changed = parse_datetime(row["last_changed"])
            if not first_date or last_changed < first_date:
                first_date = last_changed
            if not last_date or last_changed > last_date:
                last_date = last_changed
            data.append({
                "entity_id": row["entity_id"],
                "state": row["state"],
                "last_changed": row["last_changed"]
            })
    return data, first_date, last_date

filename = "history.csv" #RENAME THIS IF NECESSARY
data, first_date, last_date = read_csv(filename)
total_seconds_out = calculate_time_out(data)
hours, minutes, seconds = format_time(total_seconds_out)

print(f"In the last 7 days, I've spent: {hours} hours, {minutes} minutes, {seconds} seconds out of my house")
