import time as t
import os
import datetime
import sqlite3

RED = '\033[91m'
GREEN = '\033[92m'
RESET = '\033[0m'
WHITE = '\033[97m'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def connectDB():
    conn = sqlite3.connect(os.path.join(BASE_DIR, "tracker.db"))
    conn.row_factory = sqlite3.Row
    return conn

def get_total_time(cur, start_date, end_date):
    cur.execute("""
        SELECT COALESCE(SUM(time), 0) AS total
        FROM tracking
        WHERE date BETWEEN ? AND ?
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
    return cur.fetchone()["total"]

def display_time(label, minutes):
    print(f"{WHITE}{label}: {GREEN}{int(minutes // 60)} hours and {int(minutes % 60)} minutes.{RESET}")

def update_logs(n):
    today = datetime.date.today().strftime('%Y-%m-%d')
    with connectDB() as conn:
        cur = conn.cursor()
        cur.execute("SELECT time FROM tracking WHERE date = ?", (today,))
        row = cur.fetchone()
        if row:
            cur.execute("UPDATE tracking SET time = time + ? WHERE date = ?", (n, today))
        else:
            cur.execute("INSERT INTO tracking (date, time) VALUES (?, ?)", (today, n))
        conn.commit()

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

def stopwatch():
    os.system('cls')
    print(f"{WHITE}────✦──────── \nStarting study session..{RESET}")
    st = t.time()
    try:
        while True:
            elapsed = t.time() - st
            print(f"\r{GREEN}{elapsed//60} minutes and {int(elapsed%60)} seconds {WHITE}studied.{RESET}", end="", flush=True)
            t.sleep(1)
    except KeyboardInterrupt:
        elapsed = t.time() - st
        minutes = int(elapsed / 60)
        update_logs(minutes)
        print(f"{GREEN}\n･ . Studied for {minutes} minutes. ✦{RESET}\n")
        t.sleep(2)

def log_edit():
    print(f"{WHITE}Enter the number of minutes to be edited:{RESET}")
    try:
        a = int(input())
        update_logs(a)
        print(f"{GREEN}Your study session has been edited.{RESET}")
        t.sleep(1)
    except Exception:
        print(f"{RED}Invalid input.{RESET}")

def statistics():
    os.system('cls')
    today = datetime.date.today()
    today_str = today.strftime('%Y-%m-%d')
    week_start = today - datetime.timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    with connectDB() as conn:
        cur = conn.cursor()
        cur.execute("SELECT time FROM tracking WHERE date = ?", (today_str,))
        today_minutes = cur.fetchone()
        today_minutes = today_minutes["time"] if today_minutes else 0
        week_total = get_total_time(cur, week_start, today)
        month_total = get_total_time(cur, month_start, today)

        print(f"\n{WHITE}Study Summary:{RESET}")
        display_time("Today's total", today_minutes)
        display_time("This week's total", week_total)
        display_time("This month's total", month_total)
        print(f"\n{WHITE}Would you like to see more detailed stats?{RESET}")
        print(f"{GREEN}1.{RESET} Weekly stats")
        print(f"{GREEN}2.{RESET} Monthly stats")
        choice = input(f"{WHITE}Enter your choice: {RESET}").lower().strip()

        if choice == "week":
            print(f"\n{WHITE}Weekly Stats:{RESET}")
            days_passed = (today - week_start).days + 1
            avg_week = week_total / days_passed if days_passed else 0
            display_time("This week's total", week_total)
            display_time("This week's average", avg_week)

            for i in range(1, 5):
                end_prev = week_start - datetime.timedelta(days=1 + (7 * (i - 1)))
                start_prev = end_prev - datetime.timedelta(days=6)
                prev_total = get_total_time(cur, start_prev, end_prev)
                avg_prev = prev_total / 7 if prev_total else 0
                print(f"\n{WHITE}Week of {start_prev.strftime('%b %d')} - {end_prev.strftime('%b %d')}{RESET}")
                display_time("\tTotal", prev_total)
                display_time("\tAverage", avg_prev)

        elif choice == "month":
            print(f"\n{WHITE}Monthly Stats:{RESET}")
            days_passed = today.day
            avg_month = month_total / days_passed if days_passed else 0
            display_time("\tThis month's total", month_total)
            display_time("\tThis month's average", avg_month)

            for i in range(1, 4):
                prev_month_end = month_start - datetime.timedelta(days=1)
                prev_month_start = prev_month_end.replace(day=1)
                prev_total = get_total_time(cur, prev_month_start, prev_month_end)
                days_in_prev_month = prev_month_end.day
                avg_prev = prev_total / days_in_prev_month if prev_total else 0
                print(f"\n{WHITE}{prev_month_start.strftime('%B %Y')}{RESET}")
                display_time("Total", prev_total)
                display_time("Average", avg_prev)
                month_start = prev_month_start
        else:
            print("Please enter a valid input")
            t.sleep(1)
            statistics()
            return
    print("\nPress Enter to return.")
    input()
    return True

def main():
    while True:
        os.system('cls')
        print(f"{GREEN}- - ———:꒰ Welcome back ꒱:{RESET}")
        print(f'\n  ⇀ {WHITE}Timer \n  ⇀ Stopwatch \n  ⇀ Statistics \n  ⇀ Log \n  ⇀ Quit {RESET}\n')
        command = input().strip().lower()
        if "timer".startswith(command):
            while True:
                timer()
                print("Would you like to start another session? (yes/no)")
                if input().strip().lower().startswith("no"):
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

if __name__ == "__main__":
    main()