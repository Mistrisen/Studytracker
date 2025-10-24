import time
import os
import datetime
import sqlite3
import keyboard

RED = '\033[91m'
GREEN = '\033[92m'
RESET = '\033[0m'
WHITE = '\033[97m'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def menu(options:list[str])-> int:
    current_selection = 0
    for i, option in enumerate(options):
        print((f'{GREEN}- {RESET}' if i != current_selection else f"{GREEN}> {RESET}") + option)    
    time.sleep(1)

    while True:
        key = keyboard.read_key()
        time.sleep(0.15)
        os.system('cls')
        if key == 'up':
            current_selection -= 1
        if key == 'down':
            current_selection += 1
        if key == "enter":
            input()
            return current_selection

        if current_selection>=len(options):
            current_selection=len(options)-1
        if current_selection<0:
            current_selection=0
        
        for i, option in enumerate(options):
            print((f'{GREEN}- {RESET}' if i != current_selection else f"{GREEN}> {RESET}") + option)

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
        print(f"{GREEN}\t───♡───────── \n\tStarting study session of {WHITE}{n} minutes..{RESET}")
        for i in range(n, 0, -1):
            print(f"\r{RED}{i} minutes remaining.{RESET}", end="", flush=True)
            time.sleep(60)
        os.system('cls')
        print(f"{GREEN}\n\t Study session completed !!{RESET}\n")
        update_logs(n)
    except KeyboardInterrupt:
        print(f"\n\t{RED}Study session interrupted !!{RESET}")
    time.sleep(1)

def stopwatch():
    os.system('cls')
    print(f"{WHITE}\n\tStarting study session..\n{RESET}")
    st = time.time()
    try:
        while True:
            elapsed = time.time() - st
            print(f"\r{GREEN}{elapsed//60} minutes and {int(elapsed%60)} seconds {WHITE}studied.{RESET}", end="", flush=True)
            time.sleep(1)
    except KeyboardInterrupt:
        elapsed = time.time() - st
        minutes = int(elapsed / 60)
        update_logs(minutes)
        print(f"{GREEN}\n\n\t Studied for {minutes} minutes. ✦{RESET}\n")
        time.sleep(2)

def log_edit():
    print(f"{WHITE}\tEnter the number of minutes to be edited:{RESET}")
    try:
        a = int(input())
        update_logs(a)
        print(f"{GREEN}\tYour study session has been edited.{RESET}")
        time.sleep(1)
    except Exception:
        print(f"{RED}\tInvalid input.{RESET}")

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
        match menu(["Weekly","Monthly","Exit"]):
            case 0:
                days_passed = (today - week_start).days + 1
                avg_week = week_total / days_passed if days_passed else 0
                display_time("\tThis week's total", week_total)
                display_time("\tThis week's average", avg_week)
                for i in range(1, 5):
                    end_prev = week_start - datetime.timedelta(days=1 + (7 * (i - 1)))
                    start_prev = end_prev - datetime.timedelta(days=6)
                    prev_total = get_total_time(cur, start_prev, end_prev)
                    avg_prev = prev_total / 7 if prev_total else 0
                    print(f"\n{WHITE}Week of {start_prev.strftime('%b %d')} - {end_prev.strftime('%b %d')}{RESET}")
                    display_time("\tTotal", prev_total)
                    display_time("\tAverage", avg_prev)
                input()
            case 1:
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
                    display_time("\tTotal", prev_total)
                    display_time("\tAverage", avg_prev)
                    month_start = prev_month_start
                input()  

            case 2:
                return True

def main():
    while True:
        print(f"{GREEN}\t- - ——— [ Welcome back ]{RESET}")
        match menu(["Timer","Stopwatch","Statistics","Log","Quit"]):
            case 0:
                timer()
            case 1:
                stopwatch()
            case 2:
                statistics()
            case 3:
                log_edit()
            case 4: 
                break
        os.system('cls')

if __name__ == "__main__":
    main()