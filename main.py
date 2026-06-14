#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py — MINER PANEL v4
"""

import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, request, jsonify, render_template_string

import config as cfg_module
from miner_api import (
    poll_all,
    read_pools, read_estats, read_error_code, read_miner_info,
    do_reboot, do_restart_btminer,
    do_enable_fast_boot, do_disable_fast_boot, do_adjust_upfreq_speed,
    do_update_pools,
    do_power_off, do_power_on,
    do_led, do_update_pwd,
    read_cmd,
)
from ntp_module import update_ntp_settings
from logs_module import get_miner_logs
from visit_tracker import update_login_data, get_week_report
from template import get_html
from settings_template import get_settings_html

app = Flask(__name__)

# ─────────────────────────────────────────────────────────
# CONFIG — loaded at startup, reloaded after save
# ─────────────────────────────────────────────────────────

_cfg = cfg_module.load()

def C(key, default=None):
    return _cfg.get(key, default)

def _reload():
    global _cfg
    _cfg = cfg_module.load()

def _names():    return C("MINER_NAMES", [])
def _api_ports():return C("API_PORTS", [])
def _web_ports():return C("WEB_PORTS", {})
def _ip():       return C("MINER_IP", "")
def _password(): return C("MINER_PASSWORD", "admin")
def _username(): return C("MINER_USERNAME", "admin")
def _prefix():   return C("WORKER_PREFIX", "kop1ma")
def _pin():      return C("ACTION_PIN", "")

def _pin_ok() -> bool:
    """
    ACTION_PIN is read from config.txt first, then from the environment
    variable (Railway) if not found in the file.
    - If a value is set (from either source): protected endpoints require
      that same value sent via the X-Action-Pin header or the action_pin
      field in the JSON body.
    - If no value is set anywhere: the request is rejected with an error
      telling the admin to set the ACTION_PIN environment variable.
    """
    pin = _pin()
    if not pin:
        return False
    sent = request.headers.get("X-Action-Pin", "")
    if not sent:
        data = request.get_json(silent=True) or {}
        sent = str(data.get("action_pin", ""))
    return sent == pin

def _pin_error():
    if not _pin():
        return jsonify({
            "ok": False,
            "error": "ACTION_PIN is not configured. Please set the ACTION_PIN environment variable (or add ACTION_PIN to config.txt).",
            "pin_required": True,
            "pin_not_configured": True,
        }), 403
    return jsonify({"ok": False, "error": "Invalid or missing PIN", "pin_required": True}), 403


# Endpoints that require ACTION_PIN (when configured) for protected actions
PROTECTED_PATHS = {
    "/api/reboot",
    "/api/restart_btminer",
    "/api/fast_boot",
    "/api/upfreq_speed",
    "/api/update_pools",
    "/api/set_ntp",
    "/api/power_off",
    "/api/power_on",
    "/api/led",
    "/api/change_password",
    "/api/reboot_one",
    "/api/terminal",
    "/api/settings/save",
    "/api/settings/restart",
}

@app.before_request
def _guard():
    if request.method == "POST" and request.path in PROTECTED_PATHS:
        if not _pin_ok():
            return _pin_error()

def build_miners() -> list[dict]:
    return [
        {"name": n, "ip": _ip(), "port": p}
        for n, p in zip(_names(), _api_ports())
    ]

def get_api_port(name: str) -> int:
    names = _names()
    ports = _api_ports()
    idx = names.index(name) if name in names else -1
    return ports[idx] if idx >= 0 else 0

def auto_worker(name: str, custom: str = "") -> str:
    base = _prefix() if not custom.strip() or custom.strip().lower() == "auto" else custom.strip()
    if "." in base:
        return base
    return f"{base}.{name}"


# ─────────────────────────────────────────────────────────
# ROUTES — pages
# ─────────────────────────────────────────────────────────

@app.route("/")
def index():
    update_login_data()
    html = get_html(
        miner_names=_names(),
        api_ports=_api_ports(),
        web_ports=_web_ports(),
        miner_ip=_ip(),
        worker_prefix=_prefix(),
    )
    return render_template_string(html)


@app.route("/settings")
def settings():
    # MINER_IP فقط در صورتی نشون داده می‌شه که از config.txt اومده باشه،
    # نه وقتی از متغیر محیطی Railway گرفته شده
    display_cfg = dict(_cfg)
    display_cfg["MINER_IP"] = C("_file_cfg", {}).get("MINER_IP", "")
    html = get_settings_html(cfg=display_cfg)
    return render_template_string(html)


# ─────────────────────────────────────────────────────────
# ROUTES — Settings API
# ─────────────────────────────────────────────────────────

@app.route("/api/settings/get")
def api_settings_get():
    file_cfg = C("_file_cfg", {})
    return jsonify({
        # اگر MINER_IP از متغیر محیطی (Railway) بیاد و در config.txt نباشه،
        # به کاربر نشون داده نمی‌شه (خالی برمی‌گرده)
        "MINER_IP":       file_cfg.get("MINER_IP", ""),
        "PORT":           C("PORT"),
        "MINER_PASSWORD": C("MINER_PASSWORD"),
        "MINER_USERNAME": C("MINER_USERNAME"),
        "WORKER_PREFIX":  C("WORKER_PREFIX"),
        "miners":         C("ALL_MINERS", []),
    })


@app.route("/api/settings/save", methods=["POST"])
def api_settings_save():
    data = request.get_json(silent=True) or {}
    simple = {
        "MINER_IP":       data.get("MINER_IP", ""),
        "PORT":           str(data.get("PORT", "1090")),
        "MINER_PASSWORD": data.get("MINER_PASSWORD", "admin"),
        "MINER_USERNAME": data.get("MINER_USERNAME", "admin"),
        "WORKER_PREFIX":  data.get("WORKER_PREFIX", "kop1ma"),
        # ACTION_PIN is not part of the settings form — preserve its current
        # value so saving settings doesn't wipe it from config.txt
        "ACTION_PIN":     C("_file_cfg", {}).get("ACTION_PIN", ""),
    }
    miners = data.get("miners", [])
    # validate miners
    clean = []
    for m in miners:
        try:
            clean.append({
                "name":    str(m["name"]).strip(),
                "api":     int(m["api"]),
                "web":     int(m["web"]),
                "enabled": bool(m.get("enabled", True)),
            })
        except Exception:
            return jsonify({"ok": False, "msg": f"Invalid miner entry: {m}"}), 400

    cfg_module.write_config(simple, clean)
    _reload()
    return jsonify({"ok": True, "msg": "Saved"})


@app.route("/api/settings/restart", methods=["POST"])
def api_settings_restart():
    import threading
    def _do():
        import time; time.sleep(0.8)
        cfg_module.restart()
    threading.Thread(target=_do, daemon=True).start()
    return jsonify({"ok": True, "msg": "Restarting..."})


# ─────────────────────────────────────────────────────────
# ROUTES — READ API
# ─────────────────────────────────────────────────────────

@app.route("/api/dashboard")
def api_dashboard():
    miners = build_miners()
    data = poll_all(miners, _password())

    def _fetch_errors(name, port):
        codes = []
        try:
            resp = read_error_code(_ip(), port, _password())
            if not resp or not isinstance(resp, dict):
                return name, codes
            msg = resp.get("Msg")
            if not isinstance(msg, dict):
                return name, codes
            ec = msg.get("error_code")
            if isinstance(ec, list):
                for item in ec:
                    if isinstance(item, dict):
                        codes.extend(str(k) for k in item.keys())
            elif isinstance(ec, dict):
                codes = [str(k) for k in ec.keys()]
        except Exception:
            pass
        return name, codes

    error_map = {}
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(_fetch_errors, n, get_api_port(n)): n for n in _names()}
        for fut in as_completed(futs):
            try:
                name, codes = fut.result()
                error_map[name] = codes
            except Exception:
                error_map[futs[fut]] = []

    for m in data:
        m["error_codes"] = error_map.get(m["name"], [])

    total = round(sum(m["hashrate"] or 0 for m in data), 2)
    total_ampere = round(sum(m.get("ampere") or 0 for m in data), 1)
    return jsonify({
        "miners":         data,
        "total_hashrate": total,
        "total_ampere":   total_ampere,
        "miner_ip":       _ip(),
        "web_ports":      _web_ports(),
    })


@app.route("/api/pools/<miner_name>")
def api_get_pools(miner_name):
    if miner_name not in _names():
        return jsonify({"error": "ماینر پیدا نشد"}), 404
    resp = read_pools(_ip(), get_api_port(miner_name), _password())
    return jsonify(resp or {"error": "پاسخی دریافت نشد"})


@app.route("/api/estats/<miner_name>")
def api_get_estats(miner_name):
    if miner_name not in _names():
        return jsonify({"error": "ماینر پیدا نشد"}), 404
    resp = read_estats(_ip(), get_api_port(miner_name), _password())
    return jsonify(resp or {"error": "پاسخی دریافت نشد"})


@app.route("/api/errors/<miner_name>")
def api_get_errors(miner_name):
    if miner_name not in _names():
        return jsonify({"error": "ماینر پیدا نشد"}), 404
    resp = read_error_code(_ip(), get_api_port(miner_name), _password())
    return jsonify(resp or {"error": "پاسخی دریافت نشد"})


@app.route("/api/info/<miner_name>")
def api_get_info(miner_name):
    if miner_name not in _names():
        return jsonify({"error": "ماینر پیدا نشد"}), 404
    resp = read_miner_info(_ip(), get_api_port(miner_name), _password())
    return jsonify(resp or {"error": "پاسخی دریافت نشد"})


@app.route("/api/login_report")
def api_login_report():
    return jsonify(get_week_report())


@app.route("/api/worker_prefix")
def api_worker_prefix():
    return jsonify({"prefix": _prefix()})


# ─────────────────────────────────────────────────────────
# ROUTES — WRITE API
# ─────────────────────────────────────────────────────────

def _require_json(*fields):
    data = request.get_json(silent=True) or {}
    missing = [f for f in fields if not data.get(f)]
    return data, missing

def _resolve_targets(data):
    targets = data.get("miners", [])
    if targets == "all":
        targets = _names()
    return [t for t in targets if t in _names()]

def _format_results(results: list) -> dict:
    ok_count = sum(1 for r in results if r.get("ok"))
    return {
        "results": results,
        "summary": {"total": len(results), "success": ok_count, "failed": len(results) - ok_count},
    }


@app.route("/api/reboot", methods=["POST"])
def api_reboot():
    data, _ = _require_json()
    targets = _resolve_targets(data)
    if not targets:
        return jsonify({"error": "هیچ ماینری انتخاب نشده"}), 400
    results = []
    for name in targets:
        ok, msg = do_reboot(_ip(), get_api_port(name), _password())
        results.append({"miner": name, "ok": ok, "msg": msg})
    return jsonify(_format_results(results))


@app.route("/api/restart_btminer", methods=["POST"])
def api_restart_btminer():
    data, _ = _require_json()
    targets = _resolve_targets(data)
    if not targets:
        return jsonify({"error": "هیچ ماینری انتخاب نشده"}), 400
    results = []
    for name in targets:
        ok, msg = do_restart_btminer(_ip(), get_api_port(name), _password())
        results.append({"miner": name, "ok": ok, "msg": msg})
    return jsonify(_format_results(results))


@app.route("/api/fast_boot", methods=["POST"])
def api_fast_boot():
    data, _ = _require_json()
    targets = _resolve_targets(data)
    action = data.get("action", "enable")
    if not targets:
        return jsonify({"error": "هیچ ماینری انتخاب نشده"}), 400
    results = []
    for name in targets:
        port = get_api_port(name)
        if action == "enable":
            ok, msg = do_enable_fast_boot(_ip(), port, _password())
        else:
            ok, msg = do_disable_fast_boot(_ip(), port, _password())
        results.append({"miner": name, "ok": ok, "msg": msg})
    return jsonify(_format_results(results))


@app.route("/api/upfreq_speed", methods=["POST"])
def api_upfreq_speed():
    data, _ = _require_json()
    targets = _resolve_targets(data)
    speed = int(data.get("speed", 0))
    if not targets:
        return jsonify({"error": "هیچ ماینری انتخاب نشده"}), 400
    results = []
    for name in targets:
        ok, msg = do_adjust_upfreq_speed(_ip(), get_api_port(name), _password(), speed)
        results.append({"miner": name, "ok": ok, "msg": msg})
    return jsonify(_format_results(results))


@app.route("/api/update_pools", methods=["POST"])
def api_update_pools():
    data, missing = _require_json("miners", "pool1")
    if missing:
        return jsonify({"error": f"فیلدهای لازم: {missing}"}), 400
    targets = _resolve_targets(data)
    if not targets:
        return jsonify({"error": "هیچ ماینری انتخاب نشده"}), 400
    results = []
    for name in targets:
        w1 = auto_worker(name, data.get("worker1", ""))
        w2 = auto_worker(name, data.get("worker2", "")) if data.get("pool2") else ""
        w3 = auto_worker(name, data.get("worker3", "")) if data.get("pool3") else ""
        ok, msg = do_update_pools(
            _ip(), get_api_port(name), _password(),
            pool1=data.get("pool1",""), worker1=w1, passwd1=data.get("passwd1","123"),
            pool2=data.get("pool2",""), worker2=w2, passwd2=data.get("passwd2","123"),
            pool3=data.get("pool3",""), worker3=w3, passwd3=data.get("passwd3","123"),
        )
        results.append({"miner": name, "ok": ok, "msg": msg,
                        "workers": {"pool1": w1, "pool2": w2, "pool3": w3}})
    return jsonify(_format_results(results))


@app.route("/api/set_ntp", methods=["POST"])
def api_set_ntp():
    data, missing = _require_json("miners", "ntp_server")
    if missing:
        return jsonify({"error": f"فیلدهای لازم: {missing}"}), 400
    targets = _resolve_targets(data)
    if not targets:
        return jsonify({"error": "هیچ ماینری انتخاب نشده"}), 400
    results = []
    for name in targets:
        res = update_ntp_settings(
            miner_name=name, timezone=data.get("timezone","Asia/Tehran"),
            ntp_servers=[data.get("ntp_server","ir.pool.ntp.org")],
            ntp_enabled=data.get("ntp_enabled", True),
            username=_username(), password=_password(),
            miner_ip=_ip(), web_port_map=_web_ports(),
        )
        results.append({"miner": name, "ok": res.get("success", False), "msg": res.get("message","")})
    return jsonify(_format_results(results))


@app.route("/get_miner_logs", methods=["POST"])
def get_miner_logs_route():
    data = request.get_json(silent=True) or {}
    miner_name = data.get("miner")
    hours = int(data.get("hours", 2))
    if not miner_name or miner_name not in _names():
        return jsonify({"status": "error", "message": "ماینر نامعتبر", "logs": ""})
    result = get_miner_logs(
        miner_name=miner_name, hours=hours,
        miner_ip=_ip(), web_port_map=_web_ports(),
        miner_username=_username(), miner_password=_password(),
    )
    return jsonify(result)


@app.route("/api/power_off", methods=["POST"])
def api_power_off():
    data, _ = _require_json()
    targets = _resolve_targets(data)
    if not targets:
        return jsonify({"error": "هیچ ماینری انتخاب نشده"}), 400
    results = []
    for name in targets:
        ok, msg = do_power_off(_ip(), get_api_port(name), _password())
        results.append({"miner": name, "ok": ok, "msg": msg})
    return jsonify(_format_results(results))


@app.route("/api/power_on", methods=["POST"])
def api_power_on():
    data, _ = _require_json()
    targets = _resolve_targets(data)
    if not targets:
        return jsonify({"error": "هیچ ماینری انتخاب نشده"}), 400
    results = []
    for name in targets:
        ok, msg = do_power_on(_ip(), get_api_port(name), _password())
        results.append({"miner": name, "ok": ok, "msg": msg})
    return jsonify(_format_results(results))


@app.route("/api/led", methods=["POST"])
def api_led():
    data, _ = _require_json()
    targets = _resolve_targets(data)
    if not targets:
        return jsonify({"error": "هیچ ماینری انتخاب نشده"}), 400
    color = data.get("color", "red")
    results = []
    for name in targets:
        ok, msg = do_led(_ip(), get_api_port(name), _password(), color)
        results.append({"miner": name, "ok": ok, "msg": msg})
    return jsonify(_format_results(results))


@app.route("/api/change_password", methods=["POST"])
def api_change_password():
    data, missing = _require_json("miner", "new_password")
    if missing:
        return jsonify({"error": f"فیلدهای لازم: {missing}"}), 400
    name = data["miner"]
    if name not in _names():
        return jsonify({"error": "ماینر پیدا نشد"}), 404
    ok, msg = do_update_pwd(_ip(), get_api_port(name), _password(), data["new_password"])
    return jsonify({"ok": ok, "msg": msg})


@app.route("/api/reboot_one", methods=["POST"])
def api_reboot_one():
    data, _ = _require_json()
    name = data.get("miner")
    cmd  = data.get("cmd", "reboot")
    if not name or name not in _names():
        return jsonify({"ok": False, "msg": "ماینر نامعتبر"}), 400
    port = get_api_port(name)
    dispatch = {
        "reboot":           lambda: do_reboot(_ip(), port, _password()),
        "restart_btminer":  lambda: do_restart_btminer(_ip(), port, _password()),
        "power_off":        lambda: do_power_off(_ip(), port, _password()),
        "power_on":         lambda: do_power_on(_ip(), port, _password()),
        "led":              lambda: do_led(_ip(), port, _password()),
    }
    if cmd not in dispatch:
        return jsonify({"ok": False, "msg": f"دستور ناشناخته: {cmd}"}), 400
    ok, msg = dispatch[cmd]()
    return jsonify({"ok": ok, "msg": msg, "miner": name})


@app.route("/api/terminal", methods=["POST"])
def api_terminal():
    data, missing = _require_json("miner", "cmd")
    if missing:
        return jsonify({"error": f"فیلدهای لازم: {missing}"}), 400
    name = data["miner"]
    if name not in _names():
        return jsonify({"error": "ماینر پیدا نشد"}), 404
    resp = read_cmd(_ip(), get_api_port(name), _password(), data["cmd"])
    if resp is None:
        return jsonify({"error": f"پاسخی از ماینر {name} دریافت نشد"})
    return jsonify({"output": json.dumps(resp, indent=2, ensure_ascii=False)})


# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = C("PORT", 1090)
    app.run(host="0.0.0.0", port=port, debug=False)
