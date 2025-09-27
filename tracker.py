import time as t
import os
import datetime
import csv

# Text colour codes
RED = '\033[91m'
GREEN = '\033[92m'
RESET = '\033[0m'
WHITE = '\033[97m'

LOGS_DIR = os.path.join(os.path.dirname(__file__), "Logs")

def log_filename():
    return os.path.join(LOGS_DIR, datetime.datetime.today().strftime('%Y-%m') + '.csv')

def load_logs():
    logs = []
    fname = log_filename()
    if os.path.exists(fname):
        with open(fname, "r", newline='') as f:
            reader = csv.DictReader(f)
            logs = [row for row in reader]
    return logs

def save_logs(logs):
    fname = log_filename()
    with open(fname, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["date", "minutes"])
        writer.writeheader()
        writer.writerows(logs)

def update_logs(n):
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    logs = load_logs()
    dates = [entry["date"] for entry in logs]
    if today in dates:
        for entry in logs:
            if entry["date"] == today:
                entry["minutes"] = str(int(entry["minutes"]) + n)
                break
    else:
        logs.append({"date": today, "minutes": str(n)})
    save_logs(logs)

def timer():
    print(f"{WHITE}Enter the number of minutes you're studying: {RESET}")
    try:
        n = int(input())
        os.system('cls')
        print(f"{GREEN}───♡───────── \nStarting study session of {WHITE}{n} minutes..{RESET}")
        for i in range(n, 0, -1):
            print(f"\r{RED}{i} minutes remaining.{RESET}", end="", flush=True)
            t.sleep(60)
        print(f"{GREEN}\n✦ Study session completed! ･ .{RESET}\n")
        update_logs(n)
    except KeyboardInterrupt:
        print(f"\n{RED}Study session interrupted!{RESET}")
    except Exception:
        print(f"{RED}Invalid input or unexpected error!{RESET}")


def statistics():
    logs = load_logs()
    if not logs:
        print(f"{RED}No study data available.{RESET}")
        return False

    today = datetime.datetime.today().strftime('%Y-%m-%d')
    idx = next((i for i, entry in enumerate(logs) if entry['date'] == today), None)
    ts = int(logs[idx]['minutes']) if idx is not None else 0
    ys = int(logs[idx - 1]['minutes']) if idx not in (None, 0) else 0
    print(f"{WHITE}Time studied today:{GREEN} {ts // 60} hours and {ts % 60} minutes today.{RESET}")

    if ts < ys:
        placeholder = RED
    else:
        placeholder = GREEN

    pct = round((ts / ys), 3) * 100 if ys else 100
    print(f"{placeholder}{pct:.1f}% compared to yesterday!{RESET}")

    today_dt = datetime.datetime.today()
    week_start = today_dt - datetime.timedelta(days=today_dt.weekday())
    prev_week_start = week_start - datetime.timedelta(days=7)
    prev_week_end = week_start - datetime.timedelta(days=1)

    week_total = sum(
        int(entry['minutes']) for entry in logs
        if week_start.strftime('%Y-%m-%d') <= entry['date'] <= today_dt.strftime('%Y-%m-%d')
    )

    prev_week_total = sum(
        int(entry['minutes']) for entry in logs
        if prev_week_start.strftime('%Y-%m-%d') <= entry['date'] <= prev_week_end.strftime('%Y-%m-%d')
    )

    week_avg = week_total / 7

    if week_total < prev_week_total:
        placeholder = RED
    else:
        placeholder = GREEN

    print(f"\n{WHITE}Total time studied this week: {GREEN}{week_total // 60} hours and {week_total % 60} minutes.{RESET}")
    print(f"{WHITE}Weekly average: {placeholder}{week_avg // 60:.0f} hours {week_avg % 60:.0f} minutes studied.{RESET}")



    pct_week = round((week_total / prev_week_total), 3) * 100 if prev_week_total else 100
    print(f"{placeholder}{pct_week:.1f}% compared to last week!{RESET}")

    print("\nPress Enter to return.")
    input()
    return True

def log_edit():
    print(f"{WHITE}Enter the number of minutes to be edited:{RESET}")
    try:
        a = int(input())
        update_logs(a)
        print(f"{GREEN}Your study session has been edited.{RESET}")
        t.sleep(1)
    except Exception:
        print(f"{RED}Invalid input.{RESET}")

def stopwatch():
    os.system('cls')
    print(f"{GREEN}────✦──────── \nStarting study session..{RESET}")
    st = t.time()
    try:
        while True:
            elapsed = t.time() - st
            print(f"{WHITE}\r\033[2K{elapsed // 60:.0f} minutes and {int(elapsed % 60)} seconds studied ✦{RESET}", end="", flush=True)
            t.sleep(1)
    except KeyboardInterrupt:
        elapsed = t.time() - st
        update_logs(int(elapsed / 60))
        print(f"{GREEN}\n･ . Studied for {int(elapsed / 60)} minutes. ✦{RESET}\n")
        t.sleep(2)

while True:
    os.system('cls')
    print(f"{GREEN}- - ———:꒰ Welcome back ꒱:{RESET}")
    print(f'\n  ⇀ {WHITE}Timer \n  ⇀ Stopwatch \n  ⇀ Statistics \n  ⇀ Log \n  ⇀ Quit {RESET}\n')
    i = input()
    command = i.strip().lower()
    if "timer".startswith(command):
        while True:
            timer()
            print("Would you like to start another session? (yes/no)")
            b = input()
            if 'no'.startswith(b.strip().lower()):
                os.system('cls')
                break
    elif "stopwatch".startswith(command):
        stopwatch()
    elif "statistics".startswith(command):
        statistics()
    elif "log".startswith(command):
        log_edit()
    elif "quit".startswith(command):
        print(f"{RED}Quitting{RESET}")
        t.sleep(1)
        break
    else:
        print(f"{RED}Not recognised, please try again{RESET}")
        t.sleep(1)