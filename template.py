#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
template.py — MINER PANEL v4
تب‌ها: Dashboard | Pools | Reboot | FastBoot | NTP | Terminal | Logs
"""

def get_html(miner_names, api_ports, web_ports, miner_ip, worker_prefix="kop1ma"):
    names_js    = str(miner_names)
    ports_js    = str(api_ports)
    web_map_js  = str(web_ports).replace("'", '"')
    group_a     = [n for n in miner_names if n in ["131","132","133"]]
    group_b     = [n for n in miner_names if n in ["65","66","70"]]

    return f"""<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>⛏ MINER PANEL</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700;800&family=Syne:wght@700;800&display=swap" rel="stylesheet">
<style>
:root{{
  --bg:#07090f; --bg2:#0d1117; --bg3:#141b26; --bg4:#1a2332;
  --border:#1e2a3a; --border2:#243040;
  --accent:#00d4aa; --accent2:#ff6b35; --accent3:#4f9dff;
  --warn:#f59e0b; --danger:#ef4444; --success:#10b981;
  --text:#c8d6e8; --muted:#4a6080; --white:#e8f0f8;
  --mono:'JetBrains Mono',monospace; --head:'Syne',sans-serif;
  --r:10px;
}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html{{scrollbar-color:var(--border) var(--bg)}}
body{{
  background:var(--bg); color:var(--text);
  font-family:var(--mono); font-size:13px; min-height:100vh;
  background-image:
    radial-gradient(ellipse 90% 35% at 50% -5%,rgba(0,212,170,.06) 0%,transparent 70%),
    repeating-linear-gradient(90deg,transparent,transparent 39px,rgba(255,255,255,.012) 39px,rgba(255,255,255,.012) 40px),
    repeating-linear-gradient(0deg, transparent,transparent 39px,rgba(255,255,255,.012) 39px,rgba(255,255,255,.012) 40px);
}}

/* ─── HEADER ─── */
.hdr{{display:flex;align-items:center;justify-content:space-between;
  padding:8px 14px; background:var(--bg2);
  border-bottom:1px solid var(--border); position:sticky;top:0;z-index:200;gap:8px}}
.dot{{width:7px;height:7px;border-radius:50%;background:var(--accent);
  animation:pulse 2s infinite;flex-shrink:0}}
@keyframes pulse{{0%,100%{{opacity:1;transform:scale(1)}}50%{{opacity:.3;transform:scale(1.6)}}}}
.hdr-left{{display:flex;align-items:center;gap:8px;flex:1}}
.total-badge{{
  background:linear-gradient(135deg,rgba(0,212,170,.15),rgba(0,212,170,.05));
  border:1px solid rgba(0,212,170,.3); padding:4px 12px; border-radius:20px;
  font-size:13px;font-weight:800;color:var(--accent);white-space:nowrap}}
.hdr-btn{{background:var(--bg3);border:1px solid var(--border);color:var(--muted);
  padding:5px 10px;border-radius:7px;cursor:pointer;font-family:var(--mono);
  font-size:11px;letter-spacing:.5px;transition:all .2s;white-space:nowrap}}
.hdr-btn:hover{{color:var(--accent);border-color:var(--accent)}}

/* ─── TABS ─── */
.tabs{{display:flex;gap:1px;padding:0 10px;background:var(--bg2);
  border-bottom:1px solid var(--border);overflow-x:auto;-webkit-overflow-scrolling:touch}}
.tab{{padding:9px 13px;border:none;background:none;font-family:var(--mono);
  font-size:10px;font-weight:700;color:var(--muted);cursor:pointer;
  border-bottom:2px solid transparent;white-space:nowrap;letter-spacing:.8px;
  transition:all .2s}}
.tab:hover{{color:var(--text)}}
.tab.active{{color:var(--accent);border-bottom-color:var(--accent)}}

/* ─── PANELS ─── */
.panel{{display:none;padding:12px;animation:fadeIn .2s}}
.panel.active{{display:block}}
@keyframes fadeIn{{from{{opacity:0;transform:translateY(4px)}}to{{opacity:1;transform:none}}}}

/* ─── SECTION TITLE ─── */
.sec{{font-family:var(--head);font-size:10px;font-weight:800;color:var(--muted);
  letter-spacing:2px;text-transform:uppercase;margin-bottom:12px;
  display:flex;align-items:center;gap:8px}}
.sec::after{{content:'';flex:1;height:1px;background:var(--border)}}

/* ─── DASHBOARD GRID ─── */
.dash-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:7px}}
@media(max-width:520px){{.dash-grid{{grid-template-columns:1fr 1fr}}}}

/* ─── MINER CARD ─── */
.mc{{background:var(--bg2);border:1px solid var(--border);border-radius:var(--r);
  padding:12px;transition:border-color .25s;position:relative;overflow:hidden}}
.mc::before{{content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,var(--accent),transparent);opacity:0;transition:opacity .25s}}
.mc:hover{{border-color:rgba(0,212,170,.3)}} .mc:hover::before{{opacity:1}}
.mc.offline{{border-color:rgba(239,68,68,.25)}}
.mc.offline::before{{background:linear-gradient(90deg,var(--danger),transparent);opacity:1}}

/* card header row */
.ch{{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}}
.cn{{font-family:var(--head);font-size:14px;font-weight:800;color:var(--white)}}
.cn a{{color:inherit;text-decoration:none}} .cn a:hover{{color:var(--accent)}}
.sb{{padding:2px 8px;border-radius:20px;font-size:9px;font-weight:700;letter-spacing:1px}}
.sb.on{{background:rgba(16,185,129,.14);color:var(--success);border:1px solid rgba(16,185,129,.3)}}
.sb.off{{background:rgba(239,68,68,.14);color:var(--danger);border:1px solid rgba(239,68,68,.3)}}

/* ردیف ۱: Hash | Uptime | Power */
.row1{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:4px;margin-bottom:4px}}
/* ردیف ۲: Port | Temp | Temp | Temp */
.row2{{display:grid;grid-template-columns:auto 1fr 1fr 1fr;gap:4px;align-items:center}}
.met{{background:var(--bg3);border-radius:6px;padding:4px 8px}}
.ml{{font-size:7px;color:var(--muted);letter-spacing:1px;text-transform:uppercase;margin-bottom:1px;display:block}}
.mv{{font-size:14px;font-weight:800;color:var(--white);line-height:1.1}}
.mv small{{font-size:7px;font-weight:400;color:var(--muted)}}
.mv.hok{{color:var(--success)}} .mv.hlow{{color:var(--danger)}} .mv.hnone{{color:var(--muted);font-size:11px}}
.mv.unew{{color:var(--accent3)}} .mv.uold{{color:var(--success)}}
.tc{{text-align:center;padding:4px 2px;border-radius:6px;font-size:13px;font-weight:800}}
.tc.ok{{background:rgba(16,185,129,.14);color:var(--success);border:1px solid rgba(16,185,129,.2)}}
.tc.hi{{background:rgba(239,68,68,.16);color:var(--danger);border:1px solid rgba(239,68,68,.25)}}
.tc.warm{{background:rgba(245,158,11,.14);color:var(--warn);border:1px solid rgba(245,158,11,.2)}}
.port-tag{{font-size:9px;font-weight:700;color:var(--muted);
  background:var(--bg3);padding:4px 7px;border-radius:6px;border:1px solid var(--border);
  white-space:nowrap;text-align:center}}

/* ─── FORM ELEMENTS ─── */
.fcard{{background:var(--bg2);border:1px solid var(--border);border-radius:var(--r);padding:16px;margin-bottom:12px}}
.frow{{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:12px;align-items:flex-end}}
.fg{{display:flex;flex-direction:column;gap:5px;flex:1;min-width:160px}}
.fg.full{{flex:0 0 100%}}
label{{font-size:9px;color:var(--muted);letter-spacing:1.5px;text-transform:uppercase}}
input,select,textarea{{
  background:var(--bg3);border:1px solid var(--border);color:var(--text);
  border-radius:7px;padding:8px 11px;font-family:var(--mono);font-size:12px;
  outline:none;transition:border-color .2s;width:100%}}
input:focus,select:focus,textarea:focus{{
  border-color:var(--accent);box-shadow:0 0 0 2px rgba(0,212,170,.1)}}
select option{{background:var(--bg3)}}
textarea{{resize:vertical;min-height:70px}}

/* auto-worker hint */
.worker-hint{{font-size:10px;color:var(--accent3);margin-top:3px;font-style:italic}}

/* ─── MINER CHIPS ─── */
.msel{{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px}}
.chip{{padding:5px 11px;border-radius:7px;border:1px solid var(--border);
  background:var(--bg3);cursor:pointer;font-family:var(--mono);font-size:12px;
  font-weight:700;color:var(--muted);transition:all .15s;user-select:none}}
.chip:hover{{border-color:var(--accent2);color:var(--text)}}
.chip.sel{{background:rgba(0,212,170,.13);border-color:var(--accent);color:var(--accent)}}

.grp-btns{{display:flex;gap:5px;flex-wrap:wrap;margin-bottom:8px}}
.grp-btn{{padding:4px 10px;border-radius:6px;border:1px solid var(--border);
  background:var(--bg3);color:var(--muted);cursor:pointer;font-family:var(--mono);
  font-size:10px;transition:all .15s}}
.grp-btn:hover{{color:var(--text);border-color:var(--muted)}}

/* ─── POOL BOXES ─── */
.pool-box{{border:1px solid var(--border);border-radius:8px;padding:14px;
  margin-bottom:10px;background:var(--bg3);position:relative}}
.pool-lbl{{position:absolute;top:-9px;left:10px;background:var(--bg2);
  padding:0 6px;font-size:9px;font-weight:700;color:var(--accent);letter-spacing:1.5px}}

/* ─── BUTTONS ─── */
.btn{{padding:8px 16px;border-radius:8px;border:none;font-family:var(--mono);
  font-size:11px;font-weight:700;cursor:pointer;transition:all .2s;letter-spacing:.5px}}
.btn-p{{background:linear-gradient(135deg,var(--accent),#00a884);color:#07090f}}
.btn-p:hover{{transform:translateY(-1px);box-shadow:0 4px 18px rgba(0,212,170,.35)}}
.btn-d{{background:linear-gradient(135deg,var(--danger),#c82020);color:#fff}}
.btn-d:hover{{box-shadow:0 4px 18px rgba(239,68,68,.35)}}
.btn-w{{background:linear-gradient(135deg,var(--warn),#d97706);color:#07090f}}
.btn-w:hover{{box-shadow:0 4px 18px rgba(245,158,11,.35)}}
.btn-b{{background:linear-gradient(135deg,var(--accent3),#2563eb);color:#fff}}
.btn-b:hover{{box-shadow:0 4px 18px rgba(79,157,255,.35)}}
.btn-g{{background:var(--bg3);border:1px solid var(--border);color:var(--muted)}}
.btn-g:hover{{border-color:var(--accent);color:var(--accent)}}
.btn-o{{background:linear-gradient(135deg,#ff6b35,#e85d04);color:#fff}}
.btn-o:hover{{box-shadow:0 4px 18px rgba(255,107,53,.35)}}
.btn:disabled{{opacity:.35;cursor:not-allowed;transform:none!important}}
.btn-row{{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}}

/* ─── PROGRESS ─── */
.prog-wrap{{margin:10px 0}}
.prog-meta{{display:flex;justify-content:space-between;font-size:10px;color:var(--muted);margin-bottom:4px}}
.prog-bar{{height:4px;background:var(--bg3);border-radius:4px;overflow:hidden}}
.prog-fill{{height:100%;border-radius:4px;transition:width .4s;
  background:linear-gradient(90deg,var(--accent),var(--accent3))}}

/* ─── RESULT LOG ─── */
.rlog{{background:var(--bg);border:1px solid var(--border);border-radius:7px;
  padding:12px;font-size:11px;line-height:1.9;max-height:200px;overflow-y:auto;
  display:none;margin-top:10px}}
.rlog.vis{{display:block}}
.lok{{color:var(--success)}} .lerr{{color:var(--danger)}}
.linf{{color:var(--accent3)}} .lwarn{{color:var(--warn)}}

/* ─── TERMINAL ─── */
.term{{background:#000;border:1px solid var(--border);border-radius:9px;
  font-family:var(--mono);font-size:11px;min-height:280px;max-height:460px;
  overflow-y:auto;padding:14px;line-height:1.75;white-space:pre-wrap;color:#00ff88}}
.term .tk{{color:#4f9dff}} .term .tv{{color:#ff9f43}}
.term .ts{{color:#a8ff78}} .term .tn{{color:#ff6b9d}}
.term .tb{{color:#dfe6e9}} .term .te{{color:#ef4444}}
.term-toolbar{{display:flex;gap:7px;margin-bottom:8px;flex-wrap:wrap}}

/* ─── FASTBOOT CARD ─── */
.fb-grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px}}
@media(max-width:480px){{.fb-grid{{grid-template-columns:1fr}}}}
.fb-card{{background:var(--bg3);border:1px solid var(--border);border-radius:9px;padding:14px}}
.fb-title{{font-size:10px;font-weight:700;color:var(--muted);letter-spacing:1.5px;
  text-transform:uppercase;margin-bottom:6px}}
.fb-desc{{font-size:11px;color:var(--text);line-height:1.5;margin-bottom:10px}}

/* speed slider */
.slider-wrap{{margin:8px 0 14px}}
.slider-row{{display:flex;align-items:center;gap:10px}}
input[type=range]{{
  -webkit-appearance:none;width:100%;height:4px;border-radius:4px;
  background:var(--border);outline:none;border:none;padding:0}}
input[type=range]::-webkit-slider-thumb{{
  -webkit-appearance:none;width:16px;height:16px;border-radius:50%;
  background:var(--accent);cursor:pointer}}
.speed-val{{font-size:14px;font-weight:800;color:var(--accent);min-width:20px;text-align:center}}

/* ─── TOAST ─── */
.toast{{position:fixed;bottom:18px;right:14px;padding:10px 16px;
  border-radius:9px;font-size:12px;font-weight:700;z-index:9999;
  transform:translateY(70px);opacity:0;transition:all .3s;pointer-events:none;
  max-width:calc(100vw - 28px)}}
.toast.show{{transform:translateY(0);opacity:1}}
.toast.ok{{background:rgba(16,185,129,.95);color:#fff}}
.toast.err{{background:rgba(239,68,68,.95);color:#fff}}
.toast.inf{{background:rgba(79,157,255,.95);color:#fff}}

/* ─── SCROLLBAR ─── */
::-webkit-scrollbar{{width:4px;height:4px}}
::-webkit-scrollbar-track{{background:var(--bg)}}
::-webkit-scrollbar-thumb{{background:var(--border);border-radius:3px}}

/* ─── MOBILE ─── */
@media(max-width:600px){{
  .hdr,.panel,.tabs{{padding-left:10px;padding-right:10px}}
  .dash-grid{{grid-template-columns:1fr}}
  .mv{{font-size:15px}}
  .tab{{padding:8px 10px;font-size:9px}}
  .mets{{grid-template-columns:1fr 1fr}}
  .btn{{padding:7px 12px;font-size:10px}}
}}
</style>
</head>
<body>

<!-- HEADER -->
<div class="hdr">
  <div class="hdr-left">
    <div class="dot"></div>
    <div class="total-badge" id="totalBadge">... TH/s</div>
    <div class="total-badge" id="totalAmpere" style="display:none;background:linear-gradient(135deg,rgba(245,158,11,.15),rgba(245,158,11,.05));border-color:rgba(245,158,11,.3);color:var(--warn)">⚡ —A</div>
  </div>
  <div style="display:flex;gap:6px;align-items:center">
    <button class="hdr-btn" onclick="showDev()" title="Developer Info">👨‍💻</button>
    <button class="hdr-btn" onclick="showVisits()" title="Visit Report">👤</button>
    <a class="hdr-btn" href="/settings" title="Settings" style="font-size:16px;padding:5px 9px">⚙</a>
  </div>
</div>

<!-- Developer Modal -->
<div id="devModal" style="display:none;position:fixed;inset:0;z-index:999;background:rgba(0,0,0,.7);backdrop-filter:blur(4px)" onclick="if(event.target===this)this.style.display='none'">
  <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);background:var(--bg2);border:1px solid var(--border);border-radius:14px;padding:20px;min-width:280px;max-width:340px;width:90%">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
      <div style="font-family:var(--head);font-size:13px;font-weight:800;color:var(--accent)">👨‍💻 DEVELOPER</div>
      <button onclick="document.getElementById('devModal').style.display='none'" style="background:none;border:none;color:var(--muted);cursor:pointer;font-size:16px">✕</button>
    </div>
    <div style="font-size:11px;color:var(--text);line-height:2">
      <div>⛏️ <b>Powerbay:</b> kop3ma</div>
      <div>📸 <b>Instagram:</b> Kop3m_a</div>
      <div>▶️ <b>YouTube:</b> Kop3ma</div>
      <div>✈️ <b>Telegram:</b> @kop3ma</div>
    </div>
    <a href="https://t.me/kop3ma" target="_blank" rel="noopener" style="display:block;text-align:center;margin-top:14px;padding:8px;border-radius:8px;background:var(--bg3);border:1px solid var(--border);color:var(--accent);font-size:11px;font-weight:800;text-decoration:none">برای اطلاعات بیشتر</a>
  </div>
</div>

<!-- Visit Modal -->
<div id="visitModal" style="display:none;position:fixed;inset:0;z-index:999;background:rgba(0,0,0,.7);backdrop-filter:blur(4px)" onclick="if(event.target===this)this.style.display='none'">
  <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);background:var(--bg2);border:1px solid var(--border);border-radius:14px;padding:20px;min-width:280px;max-width:360px;width:90%">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
      <div style="font-family:var(--head);font-size:13px;font-weight:800;color:var(--accent)">👤 VISIT REPORT</div>
      <button onclick="document.getElementById('visitModal').style.display='none'" style="background:none;border:none;color:var(--muted);cursor:pointer;font-size:16px">✕</button>
    </div>
    <div id="visitContent" style="font-size:11px;color:var(--text)">loading...</div>
  </div>
</div>

<!-- TABS -->
<div class="tabs">
  <button class="tab active" onclick="sw('dashboard',this)">⊞ DASHBOARD</button>
  <button class="tab" onclick="sw('pools',this)">🏊 POOLS</button>
  <button class="tab" onclick="sw('reboot',this)">🔄 REBOOT</button>
  <button class="tab" onclick="sw('fastboot',this)">⚡ FASTBOOT</button>
  <button class="tab" onclick="sw('ntp',this)">⏰ NTP</button>
  <button class="tab" onclick="sw('terminal',this)">💻 TERMINAL</button>
  <button class="tab" onclick="sw('logs',this)">📋 LOGS</button>
</div>

<!-- ══════════════════════════════════════════
     TAB: DASHBOARD
═══════════════════════════════════════════ -->
<div class="panel active" id="p-dashboard">
  <div class="dash-grid" id="dashGrid">
    <div style="color:var(--muted);padding:20px">⏳ Loading miners...</div>
  </div>
</div>

<!-- ══════════════════════════════════════════
     TAB: POOLS
═══════════════════════════════════════════ -->
<div class="panel" id="p-pools">
  <div class="fcard">
    <div style="margin-bottom:12px">
      <div class="sec" style="margin-bottom:7px">Select Miners</div>
      <div class="grp-btns">
        <button class="grp-btn" onclick="selGroup('pools','all')">ALL</button>
        <button class="grp-btn" onclick="selGroup('pools','A')">Group A (131-133)</button>
        <button class="grp-btn" onclick="selGroup('pools','B')">Group B (65-70)</button>
        <button class="grp-btn" onclick="selGroup('pools','none')">Clear</button>
      </div>
      <div class="msel" id="msel-pools">{_chips('pools', miner_names)}</div>
    </div>

    <!-- Pool 1 -->
    <div class="pool-box">
      <div class="pool-lbl">POOL 1 — PRIMARY</div>
      <div class="frow">
        <div class="fg full"><label>URL</label>
          <input id="p1url" type="text" placeholder="stratum+tcp://sha256.pool.com:443" value="stratum+tcp://sha256.poolbinance.com:443"></div>
      </div>
      <div class="frow">
        <div class="fg">
          <label>Worker</label>
          <input id="p1usr" type="text" placeholder="auto — {worker_prefix}[minerName]">
          <div class="worker-hint">⚙ auto: {worker_prefix}131, {worker_prefix}132, ...</div>
        </div>
        <div class="fg"><label>Password</label><input id="p1pw" type="text" value="123"></div>
      </div>
    </div>

    <!-- Pool 2 -->
    <div class="pool-box">
      <div class="pool-lbl">POOL 2 — SECONDARY</div>
      <div class="frow">
        <div class="fg full"><label>URL</label>
          <input id="p2url" type="text" placeholder="stratum+tcp://..." value="stratum+tcp://bs.poolbinance.com:3333"></div>
      </div>
      <div class="frow">
        <div class="fg"><label>Worker</label><input id="p2usr" type="text" placeholder="auto — {worker_prefix}[minerName]"></div>
        <div class="fg"><label>Password</label><input id="p2pw" type="text" value="123"></div>
      </div>
    </div>

    <!-- Pool 3 -->
    <div class="pool-box">
      <div class="pool-lbl">POOL 3 — TERTIARY</div>
      <div class="frow">
        <div class="fg full"><label>URL</label>
          <input id="p3url" type="text" placeholder="stratum+tcp://..." value="stratum+tcp://btc.poolbinance.com:1800"></div>
      </div>
      <div class="frow">
        <div class="fg"><label>Worker</label><input id="p3usr" type="text" placeholder="auto — {worker_prefix}[minerName]"></div>
        <div class="fg"><label>Password</label><input id="p3pw" type="text" value="123"></div>
      </div>
    </div>

    <div class="btn-row">
      <button class="btn btn-p" onclick="runPools()">🚀 Apply Pools</button>
      <button class="btn btn-b" onclick="readPools()">📖 Read Current</button>
    </div>

    <div class="prog-wrap" id="prog-pools" style="display:none">
      <div class="prog-meta"><span id="prog-pools-lbl">Working...</span><span id="prog-pools-pct">0%</span></div>
      <div class="prog-bar"><div class="prog-fill" id="prog-pools-fill" style="width:0%"></div></div>
    </div>
    <div class="rlog" id="rlog-pools"></div>
  </div>
</div>

<!-- ══════════════════════════════════════════
     TAB: REBOOT
═══════════════════════════════════════════ -->
<div class="panel" id="p-reboot">
  <div class="fcard">
    <div style="background:rgba(245,158,11,.1);border:1px solid rgba(245,158,11,.3);
         border-radius:7px;padding:10px 14px;margin-bottom:14px;color:var(--warn);font-size:11px">
      ⚠️ &nbsp;Rebooting stops mining temporarily.
    </div>
    <div class="sec" style="margin-bottom:7px">Select Miners</div>
    <div class="grp-btns">
      <button class="grp-btn" onclick="selGroup('reboot','all')">ALL</button>
      <button class="grp-btn" onclick="selGroup('reboot','A')">Group A</button>
      <button class="grp-btn" onclick="selGroup('reboot','B')">Group B</button>
      <button class="grp-btn" onclick="selGroup('reboot','none')">Clear</button>
    </div>
    <div class="msel" id="msel-reboot">{_chips('reboot', miner_names)}</div>

    <div class="btn-row">
      <button class="btn btn-d" onclick="runAction('reboot','reboot')">🔄 Full Reboot</button>
      <button class="btn btn-w" onclick="runAction('restart_btminer','reboot')">⚡ Restart BTMiner</button>
      <button class="btn btn-g" onclick="runAction('power_off','reboot')">🔌 Power OFF</button>
      <button class="btn btn-p" onclick="runAction('power_on','reboot')">▶️ Power ON</button>
      <button class="btn btn-b" onclick="runAction('led','reboot')">💡 Flash LED</button>
    </div>

    <div class="prog-wrap" id="prog-reboot" style="display:none">
      <div class="prog-meta"><span id="prog-reboot-lbl">Working...</span><span id="prog-reboot-pct">0%</span></div>
      <div class="prog-bar"><div class="prog-fill" id="prog-reboot-fill" style="width:0%"></div></div>
    </div>
    <div class="rlog" id="rlog-reboot"></div>
  </div>
</div>

<!-- ══════════════════════════════════════════
     TAB: FASTBOOT
═══════════════════════════════════════════ -->
<div class="panel" id="p-fastboot">
  <div class="fcard">
    <div class="sec" style="margin-bottom:7px">Select Miners</div>
    <div class="grp-btns">
      <button class="grp-btn" onclick="selGroup('fastboot','all')">ALL</button>
      <button class="grp-btn" onclick="selGroup('fastboot','A')">Group A</button>
      <button class="grp-btn" onclick="selGroup('fastboot','B')">Group B</button>
      <button class="grp-btn" onclick="selGroup('fastboot','none')">Clear</button>
    </div>
    <div class="msel" id="msel-fastboot">{_chips('fastboot', miner_names)}</div>

<div class="fb-grid">
  <div class="fb-card">
    <div class="fb-title">⚡ Fast Boot</div>
    <div class="fb-desc">Quickly ramps up power on miner startup. Takes effect until next btminer restart.</div>
    <div class="btn-row">
      <button class="btn btn-p" onclick="runFastBoot('enable')">✅ Enable</button>
      <button class="btn btn-g" onclick="runFastBoot('disable')">❌ Disable</button>
    </div>
  </div>
  <div class="fb-card">
    <div class="fb-title">📈 Upfreq Speed</div>
    <div class="fb-desc">Speed to reach stable hashrate. 0=normal, 9=fastest. Cannot be combined with Fast Boot.</div>
        <div class="slider-wrap">
          <div class="slider-row">
            <input type="range" min="0" max="9" value="0" id="upfreqSlider"
              oninput="document.getElementById('upfreqVal').textContent=this.value">
            <span class="speed-val" id="upfreqVal">0</span>
          </div>
        </div>
        <button class="btn btn-o" onclick="runUpfreq()">🚀 Set Speed</button>
      </div>
    </div>

    <div class="prog-wrap" id="prog-fastboot" style="display:none">
      <div class="prog-meta"><span id="prog-fastboot-lbl">Working...</span><span id="prog-fastboot-pct">0%</span></div>
      <div class="prog-bar"><div class="prog-fill" id="prog-fastboot-fill" style="width:0%"></div></div>
    </div>
    <div class="rlog" id="rlog-fastboot"></div>
  </div>
</div>

<!-- ══════════════════════════════════════════
     TAB: NTP
═══════════════════════════════════════════ -->
<div class="panel" id="p-ntp">
  <div class="fcard">
    <div class="sec" style="margin-bottom:7px">Select Miners</div>
    <div class="grp-btns">
      <button class="grp-btn" onclick="selGroup('ntp','all')">ALL</button>
      <button class="grp-btn" onclick="selGroup('ntp','A')">Group A</button>
      <button class="grp-btn" onclick="selGroup('ntp','B')">Group B</button>
      <button class="grp-btn" onclick="selGroup('ntp','none')">Clear</button>
    </div>
    <div class="msel" id="msel-ntp">{_chips('ntp', miner_names)}</div>

    <div class="frow">
      <div class="fg">
        <label>NTP Server</label>
        <input id="ntpServer" type="text" value="ir.pool.ntp.org" placeholder="pool.ntp.org">
      </div>
      <div class="fg">
        <label>Timezone</label>
        <select id="ntpTZ">
          <option value="Asia/Tehran">Asia/Tehran — Iran (+03:30)</option>
          <option value="UTC">UTC — Universal</option>
          <option value="Europe/Istanbul">Europe/Istanbul (+03:00)</option>
          <option value="Asia/Dubai">Asia/Dubai (+04:00)</option>
          <option value="Europe/London">Europe/London (GMT)</option>
          <option value="America/New_York">America/New_York (EST)</option>
        </select>
      </div>
    </div>

    <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px">
      <button class="grp-btn" onclick="document.getElementById('ntpServer').value='ir.pool.ntp.org'">🇮🇷 Iranian</button>
      <button class="grp-btn" onclick="document.getElementById('ntpServer').value='pool.ntp.org'">🌐 Global</button>
      <button class="grp-btn" onclick="document.getElementById('ntpServer').value='time.google.com'">Google</button>
      <button class="grp-btn" onclick="document.getElementById('ntpServer').value='time.cloudflare.com'">Cloudflare</button>
    </div>

    <button class="btn btn-p" onclick="runNTP()">🚀 Apply NTP</button>

    <div class="prog-wrap" id="prog-ntp" style="display:none">
      <div class="prog-meta"><span id="prog-ntp-lbl">Working...</span><span id="prog-ntp-pct">0%</span></div>
      <div class="prog-bar"><div class="prog-fill" id="prog-ntp-fill" style="width:0%"></div></div>
    </div>
    <div class="rlog" id="rlog-ntp"></div>
  </div>
</div>

<!-- ══════════════════════════════════════════
     TAB: TERMINAL
═══════════════════════════════════════════ -->
<div class="panel" id="p-terminal">
  <div class="fcard">
    <div class="frow">
      <div class="fg">
        <label>Miner</label>
        <select id="termMiner">
          {"".join(f'<option value="{n}">{n}</option>' for n in miner_names)}
        </select>
      </div>
      <div class="fg">
        <label>Command</label>
        <select id="termCmd">
          <option value="summary">summary</option>
          <option value="devs">devs</option>
          <option value="pools">pools</option>
          <option value="estats">estats</option>
          <option value="get_psu">get_psu</option>
          <option value="get_error_code">get_error_code</option>
          <option value="get_miner_info">get_miner_info</option>
          <option value="get_logs">get_logs</option>
        </select>
      </div>
    </div>
    <div class="term-toolbar">
      <button class="btn btn-p" onclick="runTerminal()">▶ Run</button>
      <button class="btn btn-g" onclick="document.getElementById('termOut').innerHTML='<span style=\\'color:var(--muted)\\'>// cleared</span>'">🗑 Clear</button>
      <button class="btn btn-g" onclick="copyTerm()">📋 Copy</button>
    </div>
    <div class="term" id="termOut"><span style="color:var(--muted)">// Select miner and command, then click Run</span></div>
  </div>
</div>

<!-- ══════════════════════════════════════════
     TAB: LOGS
═══════════════════════════════════════════ -->
<div class="panel" id="p-logs">
  <div class="fcard">
    <div class="frow">
      <div class="fg">
        <label>Miner</label>
        <select id="logMiner">
          {"".join(f'<option value="{n}">{n}</option>' for n in miner_names)}
        </select>
      </div>
    </div>
    <div class="term-toolbar">
      <button class="btn btn-p" onclick="runLogs()">📋 Load Logs</button>
      <button class="btn btn-b" onclick="runErrors()">⚠️ Error Codes</button>
      <button class="btn btn-g" onclick="document.getElementById('logsOut').innerHTML='<span style=\\'color:var(--muted)\\'>// cleared</span>'">🗑 Clear</button>
      <button class="btn btn-g" onclick="copyLogs()">📋 Copy</button>
    </div>
    <div class="term" id="logsOut" style="min-height:360px;white-space:normal">
      <span style="color:var(--muted)">// Select a miner and click Load Logs</span>
    </div>
  </div>
</div>

<!-- TOAST -->
<div class="toast" id="toast"></div>

<script>
const MINERS  = {names_js};
const PORTS   = {ports_js};
const WEB_MAP = {web_map_js};
const GROUP_A = {str(group_a)};
const GROUP_B = {str(group_b)};
const MINER_IP = "{miner_ip}";
const WORKER_PREFIX = "{worker_prefix}";

// ─── ACTION PIN ───
// Protected endpoints may require a PIN if ACTION_PIN is configured on the server
function getActionPin(){{
  let pin = sessionStorage.getItem('action_pin');
  if(pin === null){{
    pin = window.prompt('Enter security PIN:') || '';
    sessionStorage.setItem('action_pin', pin);
  }}
  return pin;
}}
function clearActionPin(){{
  sessionStorage.removeItem('action_pin');
}}

// ─── PROTECTED POST — for reboot/pools/power/terminal/etc ───
async function apiPost(url, body){{
  const doFetch = (pin) => fetch(url, {{
    method: 'POST',
    headers: {{
      'Content-Type': 'application/json',
      'X-Action-Pin': pin || ''
    }},
    body: JSON.stringify(body || {{}})
  }});

  let pin = sessionStorage.getItem('action_pin') || '';
  let r = await doFetch(pin);

  if (r.status === 403) {{
    let d = {{}};
    try {{ d = await r.clone().json(); }} catch(e) {{}}
    if (d.pin_not_configured) {{
      // ACTION_PIN is not configured on the server at all — nothing the user can do
      toast('⚠️ ACTION_PIN is not configured on the server', 'err');
      return r;
    }}
    // PIN was wrong or missing — ask again
    clearActionPin();
    pin = window.prompt('Invalid PIN. Please enter it again:') || '';
    sessionStorage.setItem('action_pin', pin);
    r = await doFetch(pin);
  }}
  return r;
}}

// ─── TAB SWITCH ───
function sw(id, el){{
  document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.getElementById('p-'+id).classList.add('active');
  el.classList.add('active');
  if(id==='dashboard') loadDashboard();
}}

// ─── TOAST ───
function toast(msg, type='inf'){{
  const t=document.getElementById('toast');
  t.textContent=msg; t.className='toast '+type+' show';
  setTimeout(()=>t.classList.remove('show'),3400);
}}

// ─── MINER CHIPS ───
function selGroup(ns,g){{
  const chips=document.querySelectorAll('#msel-'+ns+' .chip');
  chips.forEach(c=>{{
    const m=c.dataset.miner;
    if(g==='all') c.classList.add('sel');
    else if(g==='none') c.classList.remove('sel');
    else if(g==='A' && GROUP_A.includes(m)) c.classList.add('sel');
    else if(g==='B' && GROUP_B.includes(m)) c.classList.add('sel');
  }});
}}
function getSelected(ns){{
  return [...document.querySelectorAll('#msel-'+ns+' .chip.sel')].map(c=>c.dataset.miner);
}}
document.querySelectorAll('.chip').forEach(c=>
  c.addEventListener('click',()=>c.classList.toggle('sel'))
);

// ─── PROGRESS ───
function showProg(ns,show){{
  document.getElementById('prog-'+ns).style.display=show?'block':'none';
}}
function setProg(ns,pct,lbl){{
  document.getElementById('prog-'+ns+'-fill').style.width=pct+'%';
  document.getElementById('prog-'+ns+'-pct').textContent=pct+'%';
  if(lbl) document.getElementById('prog-'+ns+'-lbl').textContent=lbl;
}}
function showRlog(ns,html){{
  const el=document.getElementById('rlog-'+ns);
  el.innerHTML=html; el.classList.add('vis');
}}
function logLine(txt,cls='linf'){{ return `<div class="${{cls}}">${{txt}}</div>`; }}

// ─── DASHBOARD ───
async function loadDashboard(){{
  try{{
    const r=await fetch('/api/dashboard');
    const d=await r.json();
    document.getElementById('totalBadge').textContent=`⛏ ${{d.total_hashrate}} TH/s`;
    if(d.total_ampere){{
      document.getElementById('totalAmpere').textContent=`⚡ ${{d.total_ampere}}A`;
      document.getElementById('totalAmpere').style.display='';
    }}
    renderCards(d.miners, d.web_ports||WEB_MAP, d.miner_ip||MINER_IP);
  }}catch(e){{
    document.getElementById('dashGrid').innerHTML=`<div style="color:var(--danger)">❌ ${{e}}</div>`;
  }}
}}

function renderCards(miners, wmap, ip){{
  const grid=document.getElementById('dashGrid');
  if(!miners||!miners.length){{ grid.innerHTML='<div style="color:var(--muted)">No miners configured</div>'; return; }}
  grid.innerHTML=miners.map(m=>{{
    const wport=(wmap[m.name]||WEB_MAP[m.name]||m.port);
    const link=`https://${{ip}}:${{wport}}`;
    const alive=m.alive;
    const hClass=!m.hashrate?'hnone':m.hashrate<60?'hlow':'hok';
    const uClass=!m.uptime?'hnone':m.uptime.includes('d')?'uold':'unew';

    // temps — color by heat
    const tempsHtml=(m.board_temps||[]).map(t=>{{
      const cls=t>=70?'hi':t>=60?'warm':'ok';
      return `<span class="tc ${{cls}}">${{t}}°</span>`;
    }}).join('');

    // fast_boot badge — فقط اگه روشن باشه نشون بده
    const fbOn = m.fast_boot === 'enable' || m.fast_boot === 'enabled' || m.fast_boot === true || m.fast_boot === 'true';

    // error codes — قرمز کنار ON/FB
    const errCodes = m.error_codes || [];
    const errBadges = errCodes.length
      ? errCodes.map(c => `<span style="background:rgba(239,68,68,.18);border:1px solid rgba(239,68,68,.5);color:#ef4444;font-size:8px;font-weight:800;padding:1px 5px;border-radius:4px;letter-spacing:.3px">${{c}}</span>`).join('')
      : '';

    // ردیف ۲: port + دماها (تا ۳ بورد)
    const temps = m.board_temps || [];
    const t0 = temps[0]!=null ? `<div class="tc ${{temps[0]>=70?'hi':temps[0]>=60?'warm':'ok'}}">${{temps[0]}}°</div>` : '<div class="tc" style="opacity:.2">—</div>';
    const t1 = temps[1]!=null ? `<div class="tc ${{temps[1]>=70?'hi':temps[1]>=60?'warm':'ok'}}">${{temps[1]}}°</div>` : '<div class="tc" style="opacity:.2">—</div>';
    const t2 = temps[2]!=null ? `<div class="tc ${{temps[2]>=70?'hi':temps[2]>=60?'warm':'ok'}}">${{temps[2]}}°</div>` : '<div class="tc" style="opacity:.2">—</div>';
    return `<div class="mc ${{alive?'':'offline'}}" style="padding:8px 10px">
      <div class="ch" style="margin-bottom:6px">
        <div class="cn" style="font-size:12px">
          <a href="${{link}}" target="_blank">MINER ${{m.name}}</a>
        </div>
        <div style="display:flex;align-items:center;gap:4px">
          ${{fbOn ? '<span style="background:rgba(0,212,170,.2);border:1px solid rgba(0,212,170,.5);color:var(--accent);font-size:8px;font-weight:800;padding:1px 5px;border-radius:4px;letter-spacing:.5px">⚡FB</span>' : ''}}
          ${{errBadges}}
          <div class="sb ${{alive?'on':'off'}}" style="font-size:8px">${{alive?'ON':'OFF'}}</div>
        </div>
      </div>
      <div class="row1">
        <div class="met"><span class="ml">HASH</span><div class="mv ${{hClass}}">${{m.hashrate||'—'}}<small>TH</small></div></div>
        <div class="met"><span class="ml">UPTIME</span><div class="mv ${{uClass}}" style="font-size:12px">${{m.uptime||'—'}}</div></div>
        <div class="met"><span class="ml">POWER</span><div class="mv">${{m.power||'—'}}<small>W</small>${{m.ampere ? ` <span style="color:var(--accent3);font-size:10px;font-weight:700">${{m.ampere}}A</span>` : ''}}</div></div>
      </div>
      <div class="row2">
        <div class="port-tag">:${{m.port}}</div>
        ${{t0}}${{t1}}${{t2}}
      </div>
    </div>`;
  }}).join('');
}}

// ─── POOLS ───
async function runPools(){{
  const miners=getSelected('pools');
  if(!miners.length){{ toast('Select at least one miner','err'); return; }}
  const w1=document.getElementById('p1usr').value.trim()||'auto';
  const w2=document.getElementById('p2usr').value.trim()||'auto';
  const w3=document.getElementById('p3usr').value.trim()||'auto';
  const body={{
    miners,
    pool1:document.getElementById('p1url').value, worker1:w1, passwd1:document.getElementById('p1pw').value,
    pool2:document.getElementById('p2url').value, worker2:w2, passwd2:document.getElementById('p2pw').value,
    pool3:document.getElementById('p3url').value, worker3:w3, passwd3:document.getElementById('p3pw').value,
  }};
  if(!body.pool1){{ toast('Pool 1 URL is required','err'); return; }}
  await batchPost('/api/update_pools', body, 'pools', 'Updating pools', true);
}}

async function readPools(){{
  const miners=getSelected('pools');
  if(!miners.length){{ toast('Select one miner','err'); return; }}
  const name=miners[0];
  try{{
    const r=await fetch('/api/pools/'+name);
    const d=await r.json();
    let html='';
    if(d.POOLS){{
      d.POOLS.forEach((p,i)=>{{
        const status=p.Status||'?';
        const cls=status==='Alive'?'lok':'lerr';
        html+=logLine(`Pool ${{i+1}}: ${{p.URL||'?'}}  Worker: ${{p.User||'?'}}  [${{status}}]`,cls);
      }});
    }}else{{ html=logLine(JSON.stringify(d),'linf'); }}
    showRlog('pools',html);
  }}catch(e){{ showRlog('pools',logLine('❌ '+e,'lerr')); }}
}}

// ─── REBOOT — Sequential per-miner با real-time progress ───
async function runAction(url_cmd, ns){{
  const miners = getSelected(ns);
  if (!miners.length) {{ toast('Select at least one miner', 'err'); return; }}
  const total = miners.length;
  let okCount = 0;
  showProg(ns, true);
  const rlog = document.getElementById('rlog-' + ns);
  rlog.innerHTML = ''; rlog.classList.add('vis');

  for (let i = 0; i < total; i++) {{
    const name = miners[i];
    // progress: ماینر جاری در حال کار — 100% فقط بعد از اتمام همه
    setProg(ns, Math.round(((i) / total) * 95) + 2, `[${{i+1}}/${{total}}] Miner ${{name}}...`);

    const div = document.createElement('div');
    div.className = 'linf';
    div.textContent = `⏳ Miner ${{name}}: ارسال دستور ${{url_cmd}}...`;
    rlog.appendChild(div);
    rlog.scrollTop = rlog.scrollHeight;

    // کوتاه صبر کن تا رندر بشه
    await new Promise(res => setTimeout(res, 50));

    try {{
      const r = await apiPost('/api/reboot_one', {{miner: name, cmd: url_cmd}});
      const d = await r.json();
      if (d.ok) {{
        okCount++;
        div.className = 'lok';
        div.textContent = `✅ Miner ${{name}}: ${{d.msg}}`;
      }} else {{
        div.className = 'lerr';
        div.textContent = `❌ Miner ${{name}}: ${{d.msg}}`;
      }}
    }} catch(e) {{
      // قطع کانکشن = ماینر داره ریبوت میشه = موفق
      okCount++;
      div.className = 'lok';
      div.textContent = `✅ Miner ${{name}}: ریبوت شد (کانکشن قطع شد)`;
    }}

    // toast بعد از هر ماینر — شامل آخری
    const lastOk = div.className === 'lok';
    toast(lastOk ? `✅ Miner ${{name}} — OK` : `❌ Miner ${{name}} — failed`, lastOk ? 'ok' : 'err');

    rlog.scrollTop = rlog.scrollHeight;

    // delay بین ماینرها (حتی بعد از آخری نه، ولی قبل از summary کمی صبر)
    if (i < total - 1) await new Promise(res => setTimeout(res, 800));
  }}

  // کمی صبر تا toast آخری دیده بشه، بعد summary نشون بده
  await new Promise(res => setTimeout(res, 400));

  setProg(ns, 100, `تموم شد — ${{okCount}}/${{total}} موفق`);
  const summary = document.createElement('div');
  summary.className = okCount === total ? 'lok' : 'lwarn';
  summary.style = 'margin-top:8px;border-top:1px solid var(--border);padding-top:6px;font-weight:700';
  summary.textContent = `${{okCount === total ? '✅' : '⚠️'}} ${{okCount}}/${{total}} miners succeeded`;
  rlog.appendChild(summary);
  rlog.scrollTop = rlog.scrollHeight;

  // toast نهایی
  toast(
    okCount === total ? `✅ همه ${{total}} ماینر موفق` : `⚠️ ${{okCount}}/${{total}} موفق`,
    okCount === total ? 'ok' : 'err'
  );

  setTimeout(() => showProg(ns, false), 3000);
}}

// ─── FASTBOOT ───
async function runFastBoot(action){{
  const miners=getSelected('fastboot');
  if(!miners.length){{ toast('Select at least one miner','err'); return; }}
  await batchPost('/api/fast_boot', {{miners, action}}, 'fastboot',
    action==='enable'?'Enabling fast boot':'Disabling fast boot');
}}

async function runUpfreq(){{
  const miners=getSelected('fastboot');
  if(!miners.length){{ toast('Select at least one miner','err'); return; }}
  const speed=parseInt(document.getElementById('upfreqSlider').value);
  await batchPost('/api/upfreq_speed', {{miners, speed}}, 'fastboot',
    `Setting upfreq speed ${{speed}}`);
}}

// ─── NTP — Sequential per-miner با real-time progress ───
// ─── NTP — Sequential per-miner (login method) ───
async function runNTP(){{
  const miners = getSelected('ntp');
  if (!miners.length) {{ toast('Select at least one miner', 'err'); return; }}
  const ntp = document.getElementById('ntpServer').value.trim();
  const tz  = document.getElementById('ntpTZ').value;
  if (!ntp) {{ toast('Enter NTP server address', 'err'); return; }}

  const total = miners.length;
  let okCount = 0;
  showProg('ntp', true);
  const rlog = document.getElementById('rlog-ntp');
  rlog.innerHTML = ''; rlog.classList.add('vis');

  for (let i = 0; i < total; i++) {{
    const name = miners[i];
    setProg('ntp', Math.round((i / total) * 95) + 2, `[${{i+1}}/${{total}}] Login → miner ${{name}}...`);

    const div = document.createElement('div');
    div.className = 'linf';
    div.textContent = `⏳ Miner ${{name}}: connecting via web login...`;
    rlog.appendChild(div);
    rlog.scrollTop = rlog.scrollHeight;
    await new Promise(res => setTimeout(res, 50));

    try {{
      const r = await apiPost('/api/set_ntp', {{
        miners: [name],
        ntp_server: ntp,
        timezone: tz,
        ntp_enabled: true
      }});
      const d = await r.json();
      const res = d.results && d.results[0];
      const ok  = res ? res.ok : false;
      const msg = res ? res.msg : JSON.stringify(d);
      div.className = ok ? 'lok' : 'lerr';
      div.textContent = `${{ok ? '✅' : '❌'}} Miner ${{name}}: ${{msg}}`;
      if (ok) okCount++;
      toast(ok ? `✅ ${{name}} — NTP OK` : `❌ ${{name}} — failed`, ok ? 'ok' : 'err');
    }} catch(e) {{
      div.className = 'lerr';
      div.textContent = `❌ Miner ${{name}}: ${{e}}`;
      toast(`❌ ${{name}} — error`, 'err');
    }}
    rlog.scrollTop = rlog.scrollHeight;
    if (i < total - 1) await new Promise(res => setTimeout(res, 600));
  }}

  await new Promise(res => setTimeout(res, 300));
  setProg('ntp', 100, `Done — ${{okCount}}/${{total}} OK`);
  const summary = document.createElement('div');
  summary.className = okCount === total ? 'lok' : 'lwarn';
  summary.style = 'margin-top:6px;border-top:1px solid var(--border);padding-top:6px;font-weight:700';
  summary.textContent = `${{okCount === total ? '✅' : '⚠️'}} NTP: ${{okCount}}/${{total}} OK`;
  rlog.appendChild(summary);
  rlog.scrollTop = rlog.scrollHeight;
  toast(
    okCount === total ? `✅ همه ${{total}} ماینر NTP شدن` : `⚠️ ${{okCount}}/${{total}} موفق`,
    okCount === total ? 'ok' : 'err'
  );
  setTimeout(() => showProg('ntp', false), 3000);
}}

// ─── TERMINAL ───
async function runTerminal(){{
  const miner=document.getElementById('termMiner').value;
  const cmd=document.getElementById('termCmd').value;
  const out=document.getElementById('termOut');
  out.innerHTML=`<span style="color:var(--muted)">⏳ ${{cmd}} → miner ${{miner}}...</span>`;
  try{{
    const r=await apiPost('/api/terminal',{{miner,cmd}});
    const d=await r.json();
    if(d.error){{ out.innerHTML=`<span class="te">❌ ${{d.error}}</span>`; return; }}
    out.innerHTML=syntaxHL(d.output||JSON.stringify(d,null,2));
  }}catch(e){{ out.innerHTML=`<span class="te">❌ ${{e}}</span>`; }}
}}
function copyTerm(){{
  navigator.clipboard.writeText(document.getElementById('termOut').innerText)
    .then(()=>toast('Copied!','ok')).catch(()=>toast('Copy failed','err'));
}}

// ─── LOGS — login method ───
async function runLogs(){{
  const miner=document.getElementById('logMiner').value;
  const out=document.getElementById('logsOut');
  out.innerHTML=`<span style="color:var(--muted)">⏳ Logging in to miner ${{miner}} via web panel...</span>`;
  try{{
    const r=await fetch('/get_miner_logs',{{
      method:'POST',
      headers:{{'Content-Type':'application/json'}},
      body:JSON.stringify({{miner,hours:2}})
    }});
    const d=await r.json();
    if(d.status==='error'){{ out.innerHTML=`<span class="te">❌ ${{d.message}}</span>`; return; }}
    out.innerHTML=d.logs||`<span style="color:var(--muted)">📭 No logs</span>`;
  }}catch(e){{ out.innerHTML=`<span class="te">❌ ${{e}}</span>`; }}
}}
async function runErrors(){{
  const miner=document.getElementById('logMiner').value;
  const out=document.getElementById('logsOut');
  out.innerHTML=`<span style="color:var(--muted)">⏳ Error codes for ${{miner}}...</span>`;
  try{{
    const r=await fetch('/api/errors/'+miner);
    const d=await r.json();
    if(d.error){{ out.innerHTML=`<span class="te">❌ ${{d.error}}</span>`; return; }}
    // نمایش human-readable
    let html='';
    if(d.Msg&&d.Msg.error_code){{
      const codes=d.Msg.error_code;
      if(Object.keys(codes).length===0){{
        html='<span style="color:var(--success)">✅ No error codes</span>';
      }}else{{
        Object.entries(codes).forEach(([code,time])=>{{
          html+=`<div class="te">❌ Error ${{code}} — ${{time}}</div>`;
        }});
      }}
    }}else{{
      html=syntaxHL(JSON.stringify(d,null,2));
    }}
    out.innerHTML=html;
  }}catch(e){{ out.innerHTML=`<span class="te">❌ ${{e}}</span>`; }}
}}
function copyLogs(){{
  navigator.clipboard.writeText(document.getElementById('logsOut').innerText)
    .then(()=>toast('Copied!','ok')).catch(()=>toast('Copy failed','err'));
}}

// ─── BATCH POST — با تفکیک خطا و موفقیت ───
async function batchPost(url, body, ns, label, showWorker=false){{
  showProg(ns,true); setProg(ns,5,label+'...');
  let html='';
  try{{
    setProg(ns,30,'Sending...');
    const r=await apiPost(url, body);
    const d=await r.json();
    setProg(ns,100,'Done');

    if(d.results){{
      // نمایش نتایج
      d.results.forEach(res=>{{
        const cls=res.ok?'lok':'lerr';
        const icon=res.ok?'✅':'❌';
        let line=`${{icon}} Miner ${{res.miner}}: ${{res.msg}}`;
        if(showWorker && res.worker_used) line+=` [worker: ${{res.worker_used}}]`;
        html+=logLine(line, cls);
      }});

      // خلاصه
      const s=d.summary||{{}};
      if(s.failed>0){{
        html+=`<div class="lwarn" style="margin-top:6px;border-top:1px solid var(--border);padding-top:6px">`;
        html+=`⚠️ ${{s.failed}} miner(s) failed — ${{s.success}}/${{s.total}} succeeded</div>`;
        toast(`${{s.failed}} error(s) — check log`,'err');
      }}else{{
        toast(`${{label}} — all ${{s.total}} OK`,'ok');
      }}
    }}else if(d.error){{
      html=logLine('❌ '+d.error,'lerr');
      toast('Error: '+d.error,'err');
    }}
  }}catch(e){{
    html=logLine('❌ Network error: '+e,'lerr');
    toast('Connection error','err');
    setProg(ns,100,'Error');
  }}
  showRlog(ns,html);
  setTimeout(()=>showProg(ns,false),2500);
}}

// ─── JSON SYNTAX HIGHLIGHTER ───
function syntaxHL(json){{
  if(!json) return '';
  return json
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/(\"(\\\\u[a-zA-Z0-9]{{4}}|\\\\[^u]|[^\\\\"])*\")(\x20*:)/g,
      '<span class="tk">$1</span>$3')
    .replace(/:\x20*(\"(\\\\u[a-zA-Z0-9]{{4}}|\\\\[^u]|[^\\\\"])*\")/g,
      ': <span class="ts">$1</span>')
    .replace(/:\x20*(-?[0-9]+([.][0-9]+)?([eE][+-]?[0-9]+)?)/g,
      ': <span class="tn">$1</span>')
    .replace(/:\x20*(true|false|null)/g,
      ': <span class="tv">$1</span>')
    .replace(/([{{}}[\x5d])/g,
      '<span class="tb">$1</span>');
}}

// ─── DEVELOPER INFO ───
function showDev(){{
  document.getElementById('devModal').style.display='block';
}}

// ─── VISIT TRACKER ───
async function showVisits(){{
  document.getElementById('visitModal').style.display='block';
  const content=document.getElementById('visitContent');
  content.innerHTML='<span style="color:var(--muted)">loading...</span>';
  try{{
    const r=await fetch('/api/login_report');
    const d=await r.json();
    const total=d.days.reduce((s,day)=>s+day.count,0);
    let html=`<div style="color:var(--muted);font-size:10px;margin-bottom:10px">هفته از ${{d.saturday}} — جمع: <span style="color:var(--accent);font-weight:800">${{total}}</span> بازدید</div>`;
    d.days.forEach(day=>{{
      if(!day.count) return;
      html+=`<div style="margin-bottom:8px">
        <div style="color:var(--accent3);font-weight:700;margin-bottom:3px">${{day.day_name}} <span style="color:var(--muted);font-size:10px">${{day.date}}</span> — <span style="color:var(--accent)">${{day.count}}</span></div>
        <div style="display:flex;flex-wrap:wrap;gap:4px">
          ${{day.logins.map(t=>`<span style="background:var(--bg3);border:1px solid var(--border);border-radius:5px;padding:2px 6px;font-size:10px;color:var(--text)">${{t}}</span>`).join('')}}
        </div>
      </div>`;
    }});
    if(!total) html='<div style="color:var(--muted);text-align:center;padding:10px">هنوز بازدیدی ثبت نشده</div>';
    content.innerHTML=html;
  }}catch(e){{
    content.innerHTML=`<span style="color:var(--danger)">❌ ${{e}}</span>`;
  }}
}}

// ─── INIT ───
loadDashboard();
setInterval(loadDashboard, 30000);
</script>
</body>
</html>"""


def _chips(ns, names):
    return "".join(
        f'<div class="chip" data-miner="{n}">{n}</div>'
        for n in names
    )
