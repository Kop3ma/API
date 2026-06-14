#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ntp_module.py — NTP via web login (luci)
"""

from __future__ import annotations
import requests
from bs4 import BeautifulSoup

DEFAULT_NTP_SERVERS = ["ir.pool.ntp.org"]

# ── helpers ──────────────────────────────────────────────

def _session_noverify() -> requests.Session:
    s = requests.Session()
    s.verify = False
    requests.packages.urllib3.disable_warnings()
    return s


def _login(base: str, username: str, password: str) -> tuple[requests.Session | None, str | None]:
    """Login to miner web panel. Returns (session, error)."""
    login_url = f"{base}/cgi-bin/luci"
    session = _session_noverify()
    try:
        session.get(login_url, timeout=10)
    except Exception as e:
        return None, f"GET login page failed: {e}"

    for payload in [
        {"luci_username": username, "luci_password": password},
        {"username": username, "password": password},
    ]:
        try:
            resp = session.post(login_url, data=payload, timeout=10, allow_redirects=False)
            if resp.status_code in (200, 302, 303):
                return session, None
        except Exception:
            continue

    return None, "Login failed"


# ── core ─────────────────────────────────────────────────

def update_ntp_settings(
    miner_name: str,
    timezone: str,
    ntp_servers: list | None,
    ntp_enabled: bool,
    username: str,
    password: str,
    miner_ip: str = None,
    web_port_map: dict = None,
) -> dict:
    """
    Update NTP via luci web login.
    Called by main.py route /api/set_ntp for each miner.
    """
    # resolve IP + port
    if not miner_ip:
        # fallback: try import from main
        try:
            from main import MINER_IP, WEB_PORT_MAP
            miner_ip = MINER_IP
            web_port_map = WEB_PORT_MAP
        except Exception as e:
            return {"success": False, "message": f"❌ MINER_IP not set: {e}"}

    if not web_port_map or miner_name not in web_port_map:
        return {"success": False, "message": f"❌ Port not found for miner {miner_name}"}

    port = web_port_map[miner_name]
    base = f"https://{miner_ip}:{port}"

    # login
    session, err = _login(base, username, password)
    if not session:
        return {"success": False, "message": f"❌ Login error: {err}"}

    system_url = f"{base}/cgi-bin/luci/admin/system/system"

    # get system page for token
    try:
        resp = session.get(system_url, timeout=10)
        if resp.status_code != 200:
            return {"success": False, "message": f"❌ Page load error: {resp.status_code}"}
    except Exception as e:
        return {"success": False, "message": f"❌ Page load error: {e}"}

    soup = BeautifulSoup(resp.text, "html.parser")
    token_input = soup.find("input", {"name": "token"})
    token = token_input["value"] if token_input and token_input.has_attr("value") else ""
    if not token:
        return {"success": False, "message": "❌ Security token not found"}

    servers = ntp_servers or DEFAULT_NTP_SERVERS
    ntp_value = "1" if ntp_enabled else "0"

    form_data = {
        "token": token,
        "cbi.submit": "1",
        "cbi.apply": "Save & Apply",
        "cbid.system.ntp.enabled": ntp_value,
        "cbi.cbe.system.ntp.enabled": ntp_value,
    }

    # timezone keys (try all variants)
    for tz_key in [
        "cbid.system.cfg02e48a.zonename",
        "cbid.system.system.zonename",
        "cbid.system.timezone",
    ]:
        form_data[tz_key] = timezone

    # ntp server
    if servers:
        form_data["cbid.system.ntp.server"] = servers[0]
        form_data["cbid.system.ntp.server.1"] = servers[0]

    try:
        post_resp = session.post(system_url, data=form_data, timeout=15)
        if post_resp.status_code in (200, 302):
            return {
                "success": True,
                "message": f"✅ NTP updated — miner {miner_name}",
                "ntp_enabled": ntp_enabled,
                "servers": servers,
                "timezone": timezone,
                "miner": miner_name,
            }
        return {"success": False, "message": f"❌ Server error: {post_resp.status_code}"}
    except Exception as e:
        return {"success": False, "message": f"❌ Send error: {e}"}


def bulk_update_ntp(
    miner_names: list,
    timezone: str,
    ntp_servers: list | None,
    ntp_enabled: bool,
    username: str,
    password: str,
    miner_ip: str = None,
    web_port_map: dict = None,
) -> list:
    results = []
    for name in miner_names:
        r = update_ntp_settings(name, timezone, ntp_servers, ntp_enabled, username, password, miner_ip, web_port_map)
        results.append({"miner": name, "success": r.get("success", False), "message": r.get("message", "")})
    return results
