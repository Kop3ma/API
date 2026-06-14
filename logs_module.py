#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
logs_module.py — Syslog via web login (luci)
"""

from __future__ import annotations
import re
import requests
import urllib3
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ── color scheme ─────────────────────────────────────────
_C = {
    'TIMESTAMP': '#6B7280',
    'NUMBERS':   '#EF4444',
    'KEYWORDS':  '#3B82F6',
    'CT_CV':     '#10B981',
    'BRACKETS':  '#F59E0B',
    'ERROR':     '#DC2626',
    'WARNING':   '#F59E0B',
    'SUCCESS':   '#10B981',
}

# ── login / fetch ─────────────────────────────────────────

def get_syslog_via_https(
    ip: str, port: int,
    username: str, password: str,
    timeout_login: int = 10,
    timeout_log: int = 30,
) -> str:
    """Login to miner and fetch syslog page. Returns raw HTML or ERROR string."""
    session = requests.Session()
    login_url = f"https://{ip}:{port}/cgi-bin/luci"

    try:
        session.get(login_url, verify=False, timeout=timeout_login)
        r2 = session.post(
            login_url,
            data={"luci_username": username, "luci_password": password},
            verify=False, timeout=timeout_login, allow_redirects=True,
        )
        if "Authorization Required" in r2.text:
            return "ERROR: Login failed"

        syslog_url = f"https://{ip}:{port}/cgi-bin/luci/admin/status/syslog"
        r3 = session.get(syslog_url, verify=False, timeout=timeout_log)
        if r3.status_code == 200:
            return r3.text

        # fallback
        r4 = session.get(f"https://{ip}:{port}/cgi-bin/log.cgi", verify=False, timeout=timeout_log)
        if r4.status_code == 200:
            return r4.text
        return f"ERROR: Status {r3.status_code}"

    except requests.exceptions.Timeout:
        return "ERROR: Timeout"
    except Exception as e:
        # fallback HTTP
        try:
            login_url_http = f"http://{ip}:{port}/cgi-bin/luci"
            session.get(login_url_http, timeout=timeout_login)
            session.post(login_url_http, data={"luci_username": username, "luci_password": password}, timeout=timeout_login, allow_redirects=True)
            res = session.get(f"http://{ip}:{port}/cgi-bin/luci/admin/status/syslog", timeout=timeout_log)
            return res.text
        except Exception as e2:
            return f"ERROR_FETCHING_SYSLOG: {e2}"


# ── parse ─────────────────────────────────────────────────

def parse_real_syslog(html_content: str, hours: int = 2) -> list[str]:
    """Extract and return last ~200 log lines from syslog HTML."""
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        syslog_content = None
        for tag_name in ["pre", "textarea", "code", "div"]:
            tag = soup.find(tag_name)
            if tag and len(tag.get_text().strip()) > 50:
                syslog_content = tag.get_text()
                break
        if not syslog_content:
            syslog_content = soup.get_text()

        if not syslog_content or len(syslog_content.strip()) < 10:
            return []

        lines = [ln.strip() for ln in syslog_content.split("\n") if ln.strip() and len(ln.strip()) > 5]

        try:
            now = datetime.now()
            cutoff = now - timedelta(hours=hours)
            recent = []
            for ln in lines:
                m = re.search(r"(\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?)", ln)
                if m:
                    try:
                        t = datetime.strptime(f"{now.year}-{m.group(1)}", "%Y-%m-%d %H:%M:%S.%f")
                    except Exception:
                        try:
                            t = datetime.strptime(f"{now.year}-{m.group(1)}", "%Y-%m-%d %H:%M:%S")
                        except Exception:
                            t = None
                    if t and t >= cutoff:
                        recent.append(ln)
            chosen = recent[-200:] if len(recent) >= 10 else lines[-200:]
        except Exception:
            chosen = lines[-200:]

        for i, ln in enumerate(chosen):
            if re.search(r"\bE\b", ln):
                chosen[i] = f"*{ln}"
        return chosen
    except Exception:
        return []


# ── format ────────────────────────────────────────────────

def _colorize(line: str) -> str:
    if not line:
        return line
    safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    leading = ""
    if safe.startswith("*"):
        leading = f"<span style='color:{_C['ERROR']};font-weight:bold;'>*</span> "
        safe = safe[1:]

    colored = re.sub(
        r"(\d+\.\d+|\d+)",
        lambda m: f"<span style='color:{_C['NUMBERS']};font-weight:bold;'>{m.group(1)}</span>",
        f"[{safe}]",
    )
    colored = re.sub(
        r"\b(ct:|cv:|ct|cv)\b",
        lambda m: f"<span style='color:{_C['CT_CV']};font-weight:bold;'>{m.group(1)}</span>",
        colored, flags=re.IGNORECASE,
    )
    for kw in ["btminer","bt","env","fan","ac","pin","vout","chain","temp","temperature",
               "frequency","voltage","power","hashrate","kernel","miner","pool","asic",
               "speed","rpm","watts","volts","mhz","ghz","th/s","gh/s","mh/s"]:
        colored = re.sub(
            r"\b" + re.escape(kw) + r"\b",
            lambda m: f"<span style='color:{_C['KEYWORDS']};font-weight:bold;'>{m.group(0)}</span>",
            colored, flags=re.IGNORECASE,
        )
    for pat, col in [
        (r"(error|failed|failure|crash|panic|fault|unable|cannot|timeout)", _C["ERROR"]),
        (r"(warn|warning|alert|notice|attention|caution)", _C["WARNING"]),
        (r"(success|completed|ready|online|started|connected|ok|running|active)", _C["SUCCESS"]),
    ]:
        colored = re.sub(pat, lambda m, c=col: f"<span style='color:{c};font-weight:bold;'>{m.group(0)}</span>", colored, flags=re.IGNORECASE)
    for pat in [r"(\w{3} \d{1,2} \d{2}:\d{2}:\d{2})", r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", r"(\d{2}-\d{2} \d{2}:\d{2}:\d{2})", r"(\d{2}:\d{2}:\d{2})"]:
        colored = re.sub(pat, lambda m: f"<span style='color:{_C['TIMESTAMP']};'>{m.group(1)}</span>", colored)
    colored = colored.replace("[", f"<span style='color:{_C['BRACKETS']};font-weight:bold;'>[</span>")
    colored = colored.replace("]", f"<span style='color:{_C['BRACKETS']};font-weight:bold;'>]</span>")
    return leading + colored


def format_logs_display(logs: list, miner_name: str, hours: int) -> str:
    if not logs:
        return f"<div style='text-align:center;color:{_C['TIMESTAMP']};padding:20px;'>📭 No logs for miner {miner_name}</div>"
    header = (
        f"<div style='color:{_C['KEYWORDS']};font-weight:bold;margin-bottom:12px;'>"
        f"📋 Logs — Miner <span style='color:{_C['BRACKETS']};'>{miner_name}</span> "
        f"({hours}h) — {len(logs)} entries</div>"
        f"<div style='border-bottom:1px solid #1e293b;margin-bottom:12px;'></div>"
    )
    lines = []
    for idx, ln in enumerate(logs, 1):
        num = f"<span style='color:{_C['TIMESTAMP']};font-weight:bold;user-select:none'>{idx:3d}. </span>"
        lines.append(f"<div style='line-height:1.6;padding:1px 0'>{num}{_colorize(ln)}</div>")
    return header + "".join(lines)


# ── public facade ─────────────────────────────────────────

def get_miner_logs(
    miner_name: str,
    hours: int = 2,
    miner_ip: str = None,
    web_port_map: dict = None,
    miner_username: str = "admin",
    miner_password: str = "admin",
) -> dict:
    """
    Main function called by main.py route /get_miner_logs.
    Returns dict: status / message / logs / progress / count
    """
    if not miner_ip:
        return {"status": "error", "message": "❌ Miner IP not configured", "logs": "", "progress": 100}
    if not web_port_map or miner_name not in web_port_map:
        return {"status": "error", "message": f"❌ Miner {miner_name} not in port map", "logs": "", "progress": 100}

    timeout_log = 45 if miner_name in ["131", "132", "133"] else 30
    port = web_port_map[miner_name]

    raw = get_syslog_via_https(miner_ip, port, miner_username, miner_password, timeout_log=timeout_log)

    if raw and not raw.startswith("ERROR"):
        logs = parse_real_syslog(raw, hours)
        if logs:
            return {
                "status": "success",
                "message": f"✅ {len(logs)} entries loaded from {miner_name}",
                "logs": format_logs_display(logs, miner_name, hours),
                "progress": 100,
                "count": len(logs),
            }
        return {
            "status": "success",
            "message": f"📭 No logs found for {miner_name} in last {hours}h",
            "logs": "📭 No logs found",
            "progress": 100,
            "count": 0,
        }

    return {
        "status": "error",
        "message": f"❌ Failed to fetch logs: {raw}",
        "logs": f"Connection Error: {raw}",
        "progress": 100,
    }
