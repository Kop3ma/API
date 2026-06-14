#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
config.py — Central config loader
Priority: ENV VAR > config.txt > default
"""

import os
import sys
from pathlib import Path

CONFIG_PATH = Path(os.path.dirname(__file__)) / "config" / "config.txt"


# ─────────────────────────────────────────────
# READ / WRITE config.txt
# ─────────────────────────────────────────────

def _read_raw() -> list[str]:
    if CONFIG_PATH.exists():
        return CONFIG_PATH.read_text(encoding="utf-8").splitlines()
    return []


def _parse_file() -> tuple[dict, list[dict]]:
    """Returns (simple_cfg dict, miners list)"""
    cfg = {}
    miners = []
    for line in _read_raw():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip()
        if key == "MINER":
            parts = [p.strip() for p in val.split(",")]
            if len(parts) >= 3:
                miners.append({
                    "name":    parts[0],
                    "api":     int(parts[1]),
                    "web":     int(parts[2]),
                    "enabled": (parts[3].lower() == "true") if len(parts) > 3 else True,
                })
        else:
            cfg[key] = val
    return cfg, miners


def write_config(simple: dict, miners: list[dict]):
    """Write config.txt — keys set via ENV VAR (Railway) are never written to file."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append("# === Server ===")
    for key in ("MINER_IP", "PORT", "MINER_PASSWORD", "MINER_USERNAME", "WORKER_PREFIX", "ACTION_PIN"):
        if os.environ.get(key):
            continue  # Railway env var — skip, don't override
        if key in simple and simple[key]:
            lines.append(f"{key}={simple[key]}")
    lines.append("")
    lines.append("# === Miners: name,api_port,web_port,enabled ===")
    for m in miners:
        enabled = "true" if m.get("enabled", True) else "false"
        lines.append(f"MINER={m['name']},{m['api']},{m['web']},{enabled}")
    CONFIG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ─────────────────────────────────────────────
# LOAD (called once at startup)
# ─────────────────────────────────────────────

def load() -> dict:
    """
    Returns unified config dict with keys:
      MINER_IP, PORT, MINER_PASSWORD, MINER_USERNAME, WORKER_PREFIX
      MINER_NAMES, API_PORTS, WEB_PORTS, MINERS (full list incl disabled)
    """
    file_cfg, all_miners = _parse_file()

    def _get(key, default=""):
        # ENV VAR first (Railway), then config.txt, then default
        return os.environ.get(key) or file_cfg.get(key) or default

    # default miners if config empty
    if not all_miners:
        all_miners = [
            {"name": "131", "api": 1312, "web": 1311, "enabled": True},
            {"name": "132", "api": 1323, "web": 1322, "enabled": True},
            {"name": "133", "api": 1356, "web": 1355, "enabled": True},
            {"name": "65",  "api": 1364, "web": 1367, "enabled": True},
            {"name": "66",  "api": 1369, "web": 1368, "enabled": True},
            {"name": "70",  "api": 1371, "web": 1370, "enabled": True},
        ]

    enabled = [m for m in all_miners if m.get("enabled", True)]

    return {
        # server
        "MINER_IP":       _get("MINER_IP"),
        "PORT":           int(_get("PORT", "1090")),
        "MINER_PASSWORD": _get("MINER_PASSWORD", "admin"),
        "MINER_USERNAME": _get("MINER_USERNAME", "admin"),
        "WORKER_PREFIX":  _get("WORKER_PREFIX", "kop1ma"),
        # امنیت — اول از config.txt، اگه نبود از متغیر محیطی Railway
        # هیچ‌وقت در API/UI نمایش داده نمی‌شه (مثل MINER_IP که از env میاد)
        "ACTION_PIN":     _get("ACTION_PIN"),
        # miners
        "ALL_MINERS":   all_miners,           # کل لیست (شامل disabled)
        "MINERS":       enabled,              # فقط enabled
        "MINER_NAMES":  [m["name"] for m in enabled],
        "API_PORTS":    [m["api"]  for m in enabled],
        "WEB_PORTS":    {m["name"]: m["web"] for m in enabled},
        # raw file cfg (for save)
        "_file_cfg":    file_cfg,
    }


# ─────────────────────────────────────────────
# RESTART
# ─────────────────────────────────────────────

def restart():
    """Replace current process — works on Termux and Railway"""
    os.execv(sys.executable, [sys.executable] + sys.argv)
