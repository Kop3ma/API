#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
visit_tracker.py — Login / Visit tracker (ماژول مستقل)
"""

from datetime import datetime, timedelta
import pytz
import jdatetime

login_data = {
    "current_week": {},
    "current_saturday": None,
    "last_login_time": None,
}

def get_current_saturday() -> str:
    tz = pytz.timezone("Asia/Tehran")
    now = datetime.now(tz)
    j_now = jdatetime.datetime.fromgregorian(datetime=now)
    sat = j_now - timedelta(days=j_now.weekday())
    return sat.strftime("%Y/%m/%d")

def should_record_login() -> bool:
    tz = pytz.timezone("Asia/Tehran")
    if login_data["last_login_time"] is None:
        return True
    diff = datetime.now(tz) - login_data["last_login_time"]
    return diff.total_seconds() >= 300

def update_login_data():
    if not should_record_login():
        return
    tz = pytz.timezone("Asia/Tehran")
    now = datetime.now(tz)
    j = jdatetime.datetime.fromgregorian(datetime=now)
    date_str = j.strftime("%Y/%m/%d")
    time_str = j.strftime("%H:%M:%S")
    sat = get_current_saturday()
    if login_data["current_saturday"] != sat:
        login_data["current_week"] = {}
        login_data["current_saturday"] = sat
    login_data["current_week"].setdefault(date_str, [])
    if time_str not in login_data["current_week"][date_str]:
        login_data["current_week"][date_str].append(time_str)
        login_data["current_week"][date_str].sort()
    login_data["last_login_time"] = now

def get_week_report() -> dict:
    days_fa = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه"]
    sat_str = login_data["current_saturday"] or get_current_saturday()
    sat_dt = jdatetime.datetime.strptime(sat_str, "%Y/%m/%d")
    days = []
    for i in range(7):
        d = sat_dt + timedelta(days=i)
        ds = d.strftime("%Y/%m/%d")
        logins = login_data["current_week"].get(ds, [])
        days.append({
            "date": ds,
            "day_name": days_fa[i],
            "logins": logins,
            "count": len(logins),
        })
    return {"saturday": sat_str, "days": days}
