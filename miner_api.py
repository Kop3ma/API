#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
miner_api.py — fixed + enhanced
"""

from __future__ import annotations
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from whatsminer import WhatsminerAccessToken, WhatsminerAPI
    _LIB_OK = True
except ImportError:
    _LIB_OK = False

_token_cache: dict[str, "WhatsminerAccessToken"] = {}

def _get_token(ip: str, port: int, password: str) -> Optional["WhatsminerAccessToken"]:
    if not _LIB_OK:
        return None
    key = f"{ip}:{port}"
    if key not in _token_cache:
        try:
            _token_cache[key] = WhatsminerAccessToken(
                ip_address=ip, admin_password=password, port=port,
            )
        except Exception:
            return None
    return _token_cache.get(key)

def _invalidate_token(ip: str, port: int):
    _token_cache.pop(f"{ip}:{port}", None)


# ── READ ──────────────────────────────────────────────────

def read_cmd(ip: str, port: int, password: str, cmd: str) -> Optional[dict]:
    token = _get_token(ip, port, password)
    if not token:
        return None
    try:
        return WhatsminerAPI.get_read_only_info(access_token=token, cmd=cmd)
    except Exception:
        _invalidate_token(ip, port)
        return None

def read_summary(ip, port, password): return read_cmd(ip, port, password, "summary")
def read_devs(ip, port, password): return read_cmd(ip, port, password, "devs")
def read_pools(ip, port, password): return read_cmd(ip, port, password, "pools")
def read_estats(ip, port, password): return read_cmd(ip, port, password, "estats")
def read_psu(ip, port, password): return read_cmd(ip, port, password, "get_psu")
def read_error_code(ip, port, password): return read_cmd(ip, port, password, "get_error_code")
def read_miner_info(ip, port, password): return read_cmd(ip, port, password, "get_miner_info")
def read_logs(ip, port, password): return read_cmd(ip, port, password, "get_logs")


# ── WRITE ─────────────────────────────────────────────────

def _parse_response(resp) -> tuple[bool, str]:
    if resp is None:
        return False, "پاسخی از ماینر دریافت نشد (تایم‌اوت)"

    if isinstance(resp, str):
        s = resp.strip().lower()
        if "can't access write" in s or "access write cmd" in s or "write cmd" in s:
            return False, "can't access write cmd"
        if s in ("ok", "s", "success", "true"):
            return True, "موفق"
        return False, f"پاسخ متنی غیرمنتظره از ماینر: {resp}"

    if not isinstance(resp, dict):
        return False, f"فرمت پاسخ نامشخص: {type(resp).__name__}"

    # {"STATUS":[{"STATUS":"S","Msg":"..."}]}
    status_list = resp.get("STATUS") or []
    if isinstance(status_list, list) and status_list:
        s = status_list[0]
        if isinstance(s, dict):
            ok = s.get("STATUS") == "S"
            msg = s.get("Msg", "")
            if isinstance(msg, dict):
                msg = str(msg)
            # چک کن داخل Msg هم خطای write نباشه
            if isinstance(msg, str) and ("can't access write" in msg.lower() or "write cmd" in msg.lower()):
                return False, "can't access write cmd"
            return ok, msg or ("موفق" if ok else "خطا")

    # {"STATUS":"S","Msg":"..."}  فرمت مستقیم
    if "STATUS" in resp and isinstance(resp["STATUS"], str):
        ok = resp["STATUS"] == "S"
        msg = resp.get("Msg", "")
        if isinstance(msg, dict):
            msg = str(msg)
        if isinstance(msg, str) and ("can't access write" in msg.lower() or "write cmd" in msg.lower()):
            return False, "can't access write cmd"
        return ok, msg or ("موفق" if ok else "خطا")

    # {"Code":131,"Msg":"..."}
    code = resp.get("Code")
    if code is not None:
        ok = code == 131
        msg = resp.get("Msg", "")
        if isinstance(msg, dict):
            msg = str(msg)
        code_msgs = {14: "دستور نامعتبر", 23: "JSON نامعتبر", 45: "دسترسی رد شد",
                     132: "خطای دستور", 135: "خطای token", 136: "token بیش از حد مجاز"}
        if not ok and code in code_msgs:
            msg = code_msgs[code]
        return ok, msg or ("موفق" if ok else f"کد خطا: {code}")

    if "Msg" in resp:
        msg = resp["Msg"]
        if isinstance(msg, dict):
            msg = str(msg)
        return True, str(msg)

    return True, str(resp)


def _exec(ip: str, port: int, password: str,
          cmd: str, params: dict = None) -> tuple[bool, str]:
    token = _get_token(ip, port, password)
    if not token:
        if not _LIB_OK:
            return False, "کتابخونه whatsminer نصب نیست — pip install whatsminer"
        return False, f"اتصال به {ip}:{port} ناموفق — ماینر آنلاین نیست یا رمز اشتباه"
    try:
        resp = WhatsminerAPI.exec_command(
            access_token=token,
            cmd=cmd,
            additional_params=params or {},
        )
        return _parse_response(resp)
    except Exception as e:
        _invalidate_token(ip, port)
        err = str(e)
        if "timeout" in err.lower():
            return False, f"تایم‌اوت — ماینر در {cmd} جواب نداد"
        if "connection" in err.lower() or "refused" in err.lower():
            return False, f"اتصال رد شد — پورت بسته است"
        if "permission" in err.lower() or "denied" in err.lower() or "45" in err:
            return False, f"دسترسی رد شد — رمز اشتباه است"
        return False, f"خطا در اجرای {cmd}: {err}"


# ── هسته مشترک reboot/restart ─────────────────────────────

def _do_reboot_like(ip: str, port: int, password: str,
                    cmd: str, success_msg: str) -> tuple[bool, str]:
    """
    - اگه پاسخ برگشت → parse می‌کنه (خطای write token رو می‌فهمه)
    - اگه کانکشن قطع شد → موفق (ماینر داره ریست میشه)
    - اگه خطای write/permission بود → ناموفق
    """
    token = _get_token(ip, port, password)
    if not token:
        if not _LIB_OK:
            return False, "کتابخونه whatsminer نصب نیست"
        return False, f"اتصال به {ip}:{port} ناموفق"
    try:
        resp = WhatsminerAPI.exec_command(
            access_token=token,
            cmd=cmd,
            additional_params={},
        )
        _invalidate_token(ip, port)
        ok, msg = _parse_response(resp)
        if not ok:
            return False, msg
        return True, success_msg
    except Exception as e:
        _invalidate_token(ip, port)
        err = str(e).lower()
        err_orig = str(e)
        # اول خطای write token چک بشه
        if any(k in err for k in ("write", "can't access", "access write")):
            return False, "can't access write cmd"
        if any(k in err for k in ("permission", "denied")):
            return False, "دسترسی رد شد — write token مجاز نیست"
        # قطع کانکشن = ماینر داره ریست میشه = موفق
        if any(k in err for k in ("timeout", "reset", "closed", "broken", "eof",
                                   "connection", "refused", "forcibly")):
            return True, success_msg
        return False, f"خطا: {err_orig}"


def do_reboot(ip: str, port: int, password: str) -> tuple[bool, str]:
    return _do_reboot_like(ip, port, password, "reboot", "دستور ریبوت ارسال شد")

def do_restart_btminer(ip: str, port: int, password: str) -> tuple[bool, str]:
    return _do_reboot_like(ip, port, password, "restart_btminer", "سرویس btminer ری‌استارت شد")

def do_enable_fast_boot(ip: str, port: int, password: str) -> tuple[bool, str]:
    return _exec(ip, port, password, "enable_btminer_fast_boot")

def do_disable_fast_boot(ip: str, port: int, password: str) -> tuple[bool, str]:
    return _exec(ip, port, password, "disable_btminer_fast_boot")

def do_adjust_upfreq_speed(ip: str, port: int, password: str, speed: int) -> tuple[bool, str]:
    speed = max(0, min(9, int(speed)))
    return _exec(ip, port, password, "adjust_upfreq_speed", {"upfreq_speed": str(speed)})

def do_update_pools(
    ip, port, password,
    pool1, worker1, passwd1,
    pool2="", worker2="", passwd2="",
    pool3="", worker3="", passwd3="",
) -> tuple[bool, str]:
    params = {
        "pool1": pool1, "worker1": worker1, "passwd1": passwd1,
        "pool2": pool2, "worker2": worker2, "passwd2": passwd2,
        "pool3": pool3, "worker3": worker3, "passwd3": passwd3,
    }
    return _exec(ip, port, password, "update_pools", params)

def do_set_ntp(ip: str, port: int, password: str, ntp_server: str) -> tuple[bool, str]:
    _SKIP = ("invalid", "unknown", "not support", "no cmd", "bad cmd")
    for cmd, params in [
        ("set_ntp",     {"ntp": ntp_server}),
        ("set_ntp",     {"ntpserver": ntp_server}),
        ("net_config",  {"ntp": ntp_server}),
        ("set_network", {"ntp": ntp_server}),
    ]:
        ok, msg = _exec(ip, port, password, cmd, params)
        if ok:
            return True, f"OK [{cmd}]"
        if any(k in msg.lower() for k in _SKIP):
            continue
        return False, msg
    return False, "NTP توسط این firmware پشتیبانی نمیشه"

def do_set_timezone(ip: str, port: int, password: str, timezone: str) -> tuple[bool, str]:
    _TZ = {
        "Asia/Tehran":     "IRST-3:30IRDT,80/0,264/0",
        "UTC":             "UTC0",
        "Europe/Istanbul": "TRT-3",
        "Asia/Dubai":      "GST-4",
        "Europe/London":   "GMT0BST,M3.5.0,M10.5.0",
        "America/New_York":"EST5EDT,M3.2.0,M11.1.0",
    }
    posix = _TZ.get(timezone, "IRST-3:30IRDT,80/0,264/0")
    _SKIP = ("invalid", "unknown", "not support", "no cmd", "bad cmd")
    for cmd, params in [
        ("set_timezone", {"timezone": posix}),
        ("set_timezone", {"timezone": timezone}),
        ("set_zone",     {"timezone": posix, "zonename": timezone}),
        ("set_zone",     {"zonename": timezone}),
        ("net_config",   {"timezone": posix}),
    ]:
        ok, msg = _exec(ip, port, password, cmd, params)
        if ok:
            return True, f"OK [{cmd}]"
        if any(k in msg.lower() for k in _SKIP):
            continue
        return False, msg
    return False, "Timezone توسط این firmware پشتیبانی نمیشه"

def do_set_fan(ip, port, password, fan_num, speed):
    return _exec(ip, port, password, "set_fan", {"fan": fan_num, "speed": speed})

def do_set_power_mode(ip, port, password, mode):
    cmd_map = {"normal": "set_normal_power", "low": "set_low_power", "high": "set_high_power"}
    return _exec(ip, port, password, cmd_map.get(mode, "set_normal_power"))

def do_power_off(ip, port, password):
    return _exec(ip, port, password, "power_off", {"respbefore": "true"})

def do_power_on(ip, port, password):
    return _exec(ip, port, password, "power_on")

def do_update_pwd(ip, port, old_pass, new_pass):
    return _exec(ip, port, old_pass, "update_pwd", {"old": old_pass, "new": new_pass})

def do_led(ip, port, password, color="red"):
    return _exec(ip, port, password, "set_led", {"color": color, "period": 500})


# ── Dashboard polling ──────────────────────────────────────

def _fmt_uptime(sec: int) -> str:
    d, r = divmod(sec, 86400)
    h, r = divmod(r, 3600)
    m, _ = divmod(r, 60)
    parts = []
    if d: parts.append(f"{d}d")
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}m")
    return " ".join(parts) or "< 1m"

def poll_miner(name: str, ip: str, port: int, password: str) -> dict:
    base = {"name": name, "port": port, "alive": False,
            "hashrate": None, "uptime": None, "power": None, "ampere": None,
            "board_temps": [], "fan_speeds": [], "fast_boot": None}

    token = _get_token(ip, port, password)
    if not token:
        return base

    try:
        summary_r = WhatsminerAPI.get_read_only_info(access_token=token, cmd="summary")
        devs_r    = WhatsminerAPI.get_read_only_info(access_token=token, cmd="devs")
    except Exception:
        _invalidate_token(ip, port)
        return base

    if not summary_r and not devs_r:
        return base

    base["alive"] = True

    s = None
    if isinstance(summary_r, dict):
        if summary_r.get("SUMMARY") and isinstance(summary_r["SUMMARY"], list):
            s = summary_r["SUMMARY"][0]
        elif isinstance(summary_r.get("Msg"), dict):
            s = summary_r["Msg"]

    if isinstance(s, dict):
        mhs = s.get("MHS av")
        if mhs is not None:
            base["hashrate"] = round(mhs / 1_000_000, 2) if mhs > 1_000_000 else round(mhs, 2)
        up = s.get("Uptime") or s.get("Elapsed")
        if up:
            base["uptime"] = _fmt_uptime(int(up))
        pw = s.get("Power")
        if pw:
            base["power"] = int(pw)
            base["ampere"] = round(int(pw) / 220, 1)
        fans = [s[f"Fan{i} Speed"] for i in range(1, 5) if s.get(f"Fan{i} Speed")]
        base["fan_speeds"] = fans
        fb = s.get("Btminer Fast Boot")
        if fb is not None:
            base["fast_boot"] = str(fb).lower()

    if isinstance(devs_r, dict) and devs_r.get("DEVS"):
        base["board_temps"] = [
            round(b["Temperature"], 1)
            for b in devs_r["DEVS"]
            if isinstance(b, dict) and b.get("Temperature") is not None
        ]

    # fallback: اگه power نداشتیم از get_psu بگیر
    if not base["power"]:
        try:
            psu_r = WhatsminerAPI.get_read_only_info(access_token=token, cmd="get_psu")
            if isinstance(psu_r, dict):
                msg = psu_r.get("Msg") or {}
                if isinstance(msg, dict):
                    pin = msg.get("pin")
                    iin = msg.get("iin")
                    if pin:
                        base["power"] = int(pin)
                        base["ampere"] = round(int(pin) / 220, 1)
                    if iin:
                        # iin دقیق‌تره — override می‌کنه
                        base["ampere"] = round(int(iin) / 1000, 1)
        except Exception:
            pass

    # اگه ampere هنوز نداریم ولی power داریم، از voltage تخمین نمی‌زنیم
    # فقط اگه get_psu داد حساب می‌کنیم

    return base


def poll_all(miners: list[dict], password: str, max_workers: int = 6) -> list[dict]:
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {ex.submit(poll_miner, m["name"], m["ip"], m["port"], password): m
                for m in miners}
        for fut in as_completed(futs):
            try:
                results.append(fut.result())
            except Exception:
                m = futs[fut]
                results.append({"name": m["name"], "port": m["port"], "alive": False,
                                 "hashrate": None, "uptime": None, "power": None,
                                 "board_temps": [], "fan_speeds": [], "fast_boot": None})
    return sorted(results, key=lambda x: x["name"])
