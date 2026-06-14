#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
settings_template.py — Settings page UI
"""

def get_settings_html(cfg: dict) -> str:
    miners_json = __import__('json').dumps(cfg.get("ALL_MINERS", []))
    return f"""<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>⚙ Settings — Miner Panel</title>
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
  background:var(--bg);color:var(--text);
  font-family:var(--mono);font-size:13px;min-height:100vh;
  background-image:
    radial-gradient(ellipse 80% 30% at 50% -5%,rgba(79,157,255,.07) 0%,transparent 70%),
    repeating-linear-gradient(90deg,transparent,transparent 39px,rgba(255,255,255,.012) 39px,rgba(255,255,255,.012) 40px),
    repeating-linear-gradient(0deg,transparent,transparent 39px,rgba(255,255,255,.012) 39px,rgba(255,255,255,.012) 40px);
}}

/* ── HEADER ── */
.hdr{{display:flex;align-items:center;justify-content:space-between;
  padding:10px 18px;background:var(--bg2);
  border-bottom:1px solid var(--border);position:sticky;top:0;z-index:200}}
.hdr-left{{display:flex;align-items:center;gap:12px}}
.back-btn{{display:flex;align-items:center;gap:6px;
  background:var(--bg3);border:1px solid var(--border);color:var(--muted);
  padding:6px 12px;border-radius:8px;cursor:pointer;
  font-family:var(--mono);font-size:11px;font-weight:700;
  letter-spacing:.5px;text-decoration:none;transition:all .2s}}
.back-btn:hover{{color:var(--accent);border-color:var(--accent)}}
.page-title{{font-family:var(--head);font-size:14px;font-weight:800;
  color:var(--white);letter-spacing:.5px}}
.page-sub{{font-size:10px;color:var(--muted);margin-top:1px}}

/* ── LAYOUT ── */
.wrap{{max-width:780px;margin:0 auto;padding:20px 14px 60px}}

/* ── SECTION ── */
.sec-hdr{{display:flex;align-items:center;gap:10px;margin-bottom:14px}}
.sec-icon{{width:32px;height:32px;border-radius:9px;display:flex;align-items:center;
  justify-content:center;font-size:15px;flex-shrink:0}}
.sec-icon.blue{{background:rgba(79,157,255,.15);border:1px solid rgba(79,157,255,.25)}}
.sec-icon.green{{background:rgba(0,212,170,.15);border:1px solid rgba(0,212,170,.25)}}
.sec-icon.orange{{background:rgba(255,107,53,.15);border:1px solid rgba(255,107,53,.25)}}
.sec-label{{font-family:var(--head);font-size:12px;font-weight:800;color:var(--white)}}
.sec-desc{{font-size:10px;color:var(--muted);margin-top:1px}}

.card{{background:var(--bg2);border:1px solid var(--border);
  border-radius:14px;padding:18px;margin-bottom:20px}}

/* ── FORM ── */
.frow{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px}}
.frow.single{{grid-template-columns:1fr}}
.frow.triple{{grid-template-columns:1fr 1fr 1fr}}
@media(max-width:520px){{.frow{{grid-template-columns:1fr}}.frow.triple{{grid-template-columns:1fr 1fr}}}}
.fg{{display:flex;flex-direction:column;gap:5px}}
label{{font-size:9px;color:var(--muted);letter-spacing:1.5px;text-transform:uppercase;font-weight:700}}
input,select{{
  background:var(--bg3);border:1px solid var(--border);color:var(--text);
  border-radius:8px;padding:9px 12px;font-family:var(--mono);font-size:12px;
  outline:none;transition:all .2s;width:100%}}
input:focus,select:focus{{border-color:var(--accent3);box-shadow:0 0 0 2px rgba(79,157,255,.12)}}
input.pass{{letter-spacing:2px}}

/* ── MINERS TABLE ── */
.miners-wrap{{margin-bottom:14px}}
table{{width:100%;border-collapse:collapse;table-layout:fixed}}
thead tr{{border-bottom:2px solid var(--border2)}}
th{{font-size:9px;font-weight:700;color:var(--muted);letter-spacing:1.5px;
  text-transform:uppercase;padding:8px 6px;text-align:left}}
th.col-name{{width:20%}} th.col-api{{width:26%}} th.col-web{{width:26%}}
th.col-tog{{width:16%;text-align:center}} th.col-del{{width:12%;text-align:center}}
tbody tr{{border-bottom:1px solid var(--border);transition:background .15s;cursor:grab}}
tbody tr:active{{cursor:grabbing}}
tbody tr:hover{{background:rgba(255,255,255,.02)}}
tbody tr.disabled-row{{opacity:.45}}
tbody tr.drag-over{{background:rgba(0,212,170,.07);border-top:2px solid var(--accent)}}
tbody tr.dragging{{opacity:.3}}
td{{padding:5px 4px;vertical-align:middle}}
td input{{padding:6px 8px;font-size:12px;border-radius:6px;width:100%;text-align:center}}
td input.nm{{font-weight:700;color:var(--white)}}
.drag-handle{{color:var(--muted);font-size:13px;text-align:center;
  padding:2px;user-select:none;cursor:grab}}
.drag-handle:hover{{color:var(--accent)}}

/* toggle switch */
.tog-wrap{{display:flex;align-items:center;justify-content:center}}
.tog{{position:relative;width:36px;height:20px;cursor:pointer;flex-shrink:0}}
.tog input{{opacity:0;width:0;height:0}}
.tog-slider{{position:absolute;inset:0;background:var(--bg4);
  border:1px solid var(--border2);border-radius:20px;transition:all .25s}}
.tog-slider::before{{content:'';position:absolute;left:3px;top:50%;
  transform:translateY(-50%);width:12px;height:12px;
  background:var(--muted);border-radius:50%;transition:all .25s}}
.tog input:checked + .tog-slider{{background:rgba(0,212,170,.2);border-color:var(--accent)}}
.tog input:checked + .tog-slider::before{{background:var(--accent);transform:translate(16px,-50%)}}

/* delete btn */
.del-btn{{background:none;border:none;color:var(--muted);cursor:pointer;
  font-size:14px;padding:4px 6px;border-radius:6px;transition:all .15s;line-height:1}}
.del-btn:hover{{color:var(--danger);background:rgba(239,68,68,.1)}}

/* add row btn */
.add-btn{{display:flex;align-items:center;gap:7px;width:100%;
  background:rgba(0,212,170,.05);border:1px dashed rgba(0,212,170,.25);
  color:var(--accent);border-radius:9px;padding:9px 14px;
  font-family:var(--mono);font-size:11px;font-weight:700;
  cursor:pointer;transition:all .2s;letter-spacing:.5px}}
.add-btn:hover{{background:rgba(0,212,170,.1);border-color:var(--accent)}}

/* ── BUTTONS ── */
.btn{{padding:9px 18px;border-radius:9px;border:none;font-family:var(--mono);
  font-size:11px;font-weight:700;cursor:pointer;transition:all .2s;letter-spacing:.5px}}
.btn-save{{background:linear-gradient(135deg,var(--accent),#00a884);color:#07090f}}
.btn-save:hover{{transform:translateY(-1px);box-shadow:0 4px 20px rgba(0,212,170,.4)}}
.btn-restart{{background:linear-gradient(135deg,var(--accent3),#2563eb);color:#fff}}
.btn-restart:hover{{box-shadow:0 4px 20px rgba(79,157,255,.4)}}
.btn-danger{{background:linear-gradient(135deg,var(--danger),#c82020);color:#fff}}
.btn-danger:hover{{box-shadow:0 4px 20px rgba(239,68,68,.4)}}
.btn:disabled{{opacity:.35;cursor:not-allowed;transform:none!important}}
.btn-row{{display:flex;gap:10px;flex-wrap:wrap;align-items:center}}

/* ── STATUS BAR ── */
.status-bar{{display:none;align-items:center;gap:10px;
  background:var(--bg3);border:1px solid var(--border);
  border-radius:9px;padding:10px 14px;margin-bottom:16px;font-size:11px}}
.status-bar.vis{{display:flex}}
.status-bar.ok{{border-color:rgba(16,185,129,.4);background:rgba(16,185,129,.07)}}
.status-bar.err{{border-color:rgba(239,68,68,.4);background:rgba(239,68,68,.07)}}
.status-bar.loading{{border-color:rgba(79,157,255,.3);background:rgba(79,157,255,.07)}}
.spin{{width:14px;height:14px;border:2px solid var(--border2);
  border-top-color:var(--accent3);border-radius:50%;
  animation:spin .7s linear infinite;flex-shrink:0}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}

/* ── RESTART MODAL ── */
.modal-overlay{{display:none;position:fixed;inset:0;z-index:999;
  background:rgba(0,0,0,.75);backdrop-filter:blur(6px)}}
.modal-overlay.vis{{display:flex;align-items:center;justify-content:center}}
.modal{{background:var(--bg2);border:1px solid var(--border);
  border-radius:16px;padding:28px 24px;max-width:340px;width:90%;text-align:center}}
.modal-icon{{font-size:36px;margin-bottom:12px}}
.modal-title{{font-family:var(--head);font-size:15px;font-weight:800;
  color:var(--white);margin-bottom:8px}}
.modal-desc{{font-size:11px;color:var(--muted);line-height:1.7;margin-bottom:20px}}
.restart-anim{{display:none;flex-direction:column;align-items:center;gap:10px}}
.restart-anim.vis{{display:flex}}
.big-spin{{width:36px;height:36px;border:3px solid var(--border2);
  border-top-color:var(--accent3);border-radius:50%;
  animation:spin .6s linear infinite}}

/* ── TOAST ── */
.toast{{position:fixed;bottom:22px;left:50%;transform:translateX(-50%) translateY(20px);
  background:var(--bg3);border:1px solid var(--border);color:var(--text);
  padding:9px 18px;border-radius:30px;font-size:11px;font-weight:700;
  opacity:0;transition:all .3s;z-index:9999;pointer-events:none;white-space:nowrap}}
.toast.show{{opacity:1;transform:translateX(-50%) translateY(0)}}
.toast.ok{{border-color:var(--success);color:var(--success)}}
.toast.err{{border-color:var(--danger);color:var(--danger)}}
</style>
</head>
<body>

<!-- HEADER -->
<div class="hdr">
  <div class="hdr-left">
    <a class="back-btn" href="/">← DASHBOARD</a>
    <div>
      <div class="page-title">⚙ SETTINGS</div>
      <div class="page-sub">Miner configuration &amp; panel setup</div>
    </div>
  </div>
</div>

<div class="wrap">

  <!-- STATUS BAR -->
  <div class="status-bar" id="statusBar">
    <div class="spin" id="statusSpin"></div>
    <span id="statusMsg">Saving...</span>
  </div>

  <!-- ── SERVER SETTINGS ── -->
  <div class="sec-hdr">
    <div class="sec-icon blue">🌐</div>
    <div>
      <div class="sec-label">Server Settings</div>
      <div class="sec-desc">Connection & authentication</div>
    </div>
  </div>
  <div class="card">
    <div class="frow">
      <div class="fg">
        <label>Miner IP Address</label>
        <input id="cfg-ip" type="text" placeholder="e.g. 185.135.229.121" value="{cfg.get('MINER_IP','')}">
      </div>
      <div class="fg">
        <label>Flask Port</label>
        <input id="cfg-port" type="number" placeholder="1090" value="{cfg.get('PORT',1090)}">
      </div>
    </div>
    <div class="frow">
      <div class="fg">
        <label>Miner Username</label>
        <input id="cfg-user" type="text" placeholder="admin" value="{cfg.get('MINER_USERNAME','admin')}">
      </div>
      <div class="fg">
        <label>Miner Password</label>
        <input id="cfg-pass" type="text" class="pass" placeholder="••••••••" value="{cfg.get('MINER_PASSWORD','')}">
      </div>
    </div>
    <div class="frow single">
      <div class="fg">
        <label>Worker Prefix</label>
        <input id="cfg-prefix" type="text" placeholder="kop1ma" value="{cfg.get('WORKER_PREFIX','kop1ma')}">
      </div>
    </div>
  </div>

  <!-- ── MINERS ── -->
  <div class="sec-hdr">
    <div class="sec-icon green">⛏</div>
    <div>
      <div class="sec-label">Miners</div>
      <div class="sec-desc">Name · API port · Web port · Enable/disable</div>
    </div>
  </div>
  <div class="card">
    <div class="miners-wrap">
      <table id="minersTable">
        <thead>
          <tr>
            <th class="col-name">NAME</th>
            <th class="col-api">API PORT</th>
            <th class="col-web">WEB PORT</th>
            <th class="col-tog">ACTIVE</th>
            <th class="col-del"></th>
          </tr>
        </thead>
        <tbody id="minersBody"></tbody>
      </table>
    </div>
    <button class="add-btn" onclick="addMiner()">＋ Add Miner</button>
  </div>

  <!-- ── ACTIONS ── -->
  <div class="sec-hdr">
    <div class="sec-icon orange">🚀</div>
    <div>
      <div class="sec-label">Apply Changes</div>
      <div class="sec-desc">Save config and restart panel to apply</div>
    </div>
  </div>
  <div class="card">
    <div style="background:rgba(245,158,11,.08);border:1px solid rgba(245,158,11,.2);
      border-radius:8px;padding:10px 14px;margin-bottom:16px;font-size:11px;color:var(--warn)">
      ⚠️ &nbsp;Restart takes ~3 seconds. Active connections will be dropped briefly.
    </div>
    <div class="btn-row">
      <button class="btn btn-save" onclick="saveSettings()">💾 Save Config</button>
      <button class="btn btn-restart" id="restartBtn" onclick="saveAndRestart()" disabled>
        🔄 Save &amp; Restart
      </button>
    </div>
  </div>

</div>

<!-- RESTART MODAL -->
<div class="modal-overlay" id="restartModal">
  <div class="modal">
    <div id="modalConfirmView">
      <div class="modal-icon">🔄</div>
      <div class="modal-title">Restart Panel?</div>
      <div class="modal-desc">Config will be saved first.<br>Panel restarts in ~3 seconds.</div>
      <div class="btn-row" style="justify-content:center">
        <button class="btn btn-restart" onclick="confirmRestart()">Yes, Restart</button>
        <button class="btn" style="background:var(--bg3);border:1px solid var(--border);color:var(--muted)"
          onclick="closeModal()">Cancel</button>
      </div>
    </div>
    <div class="restart-anim" id="modalRestartView">
      <div class="big-spin"></div>
      <div class="modal-title" style="margin-bottom:4px">Restarting...</div>
      <div style="font-size:10px;color:var(--muted)">Reconnecting in 4s</div>
    </div>
  </div>
</div>

<!-- TOAST -->
<div class="toast" id="toast"></div>

<script>
// ── Initial miners data from server ──
let miners = {miners_json};

// ─── ACTION PIN ───
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
      toast('⚠️ ACTION_PIN is not configured on the server', 'err');
      return r;
    }}
    clearActionPin();
    pin = window.prompt('Invalid PIN. Please enter it again:') || '';
    sessionStorage.setItem('action_pin', pin);
    r = await doFetch(pin);
  }}
  return r;
}}

// ── Render table ──
function renderTable() {{
  const tbody = document.getElementById('minersBody');
  if (!miners.length) {{
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:var(--muted);padding:20px;font-size:11px">No miners — click Add Miner</td></tr>`;
    return;
  }}
  tbody.innerHTML = miners.map((m, i) => `
    <tr class="${{m.enabled ? '' : 'disabled-row'}}" id="row-${{i}}"
      draggable="true"
      ondragstart="dragStart(event,${{i}})"
      ondragover="dragOver(event,${{i}})"
      ondragleave="dragLeave(event)"
      ondrop="dragDrop(event,${{i}})"
      ondragend="dragEnd()">
      <td><input class="nm" type="text" value="${{m.name}}" oninput="miners[${{i}}].name=this.value" placeholder="131"></td>
      <td><input type="number" value="${{m.api}}" oninput="miners[${{i}}].api=+this.value" placeholder="1312"></td>
      <td><input type="number" value="${{m.web}}" oninput="miners[${{i}}].web=+this.value" placeholder="1311"></td>
      <td>
        <div class="tog-wrap">
          <label class="tog">
            <input type="checkbox" ${{m.enabled ? 'checked' : ''}} onchange="toggleMiner(${{i}},this.checked)">
            <span class="tog-slider"></span>
          </label>
        </div>
      </td>
      <td style="text-align:center">
        <button class="del-btn" onclick="deleteMiner(${{i}})" title="Remove">🗑</button>
      </td>
    </tr>
  `).join('');
}}

function toggleMiner(i, val) {{
  miners[i].enabled = val;
  renderTable();
}}

function addMiner() {{
  miners.push({{ name: '', api: 0, web: 0, enabled: true }});
  renderTable();
  const rows = document.querySelectorAll('#minersBody tr');
  const last = rows[rows.length - 1];
  if (last) last.querySelector('input.nm')?.focus();
}}

function deleteMiner(i) {{
  miners.splice(i, 1);
  renderTable();
}}

// ── Drag & Drop reorder ──
let dragIdx = null;
function dragStart(e, i) {{
  dragIdx = i;
  e.currentTarget.classList.add('dragging');
  e.dataTransfer.effectAllowed = 'move';
}}
function dragOver(e, i) {{
  e.preventDefault();
  e.dataTransfer.dropEffect = 'move';
  document.querySelectorAll('#minersBody tr').forEach(r => r.classList.remove('drag-over'));
  e.currentTarget.classList.add('drag-over');
}}
function dragLeave(e) {{
  e.currentTarget.classList.remove('drag-over');
}}
function dragDrop(e, i) {{
  e.preventDefault();
  if (dragIdx === null || dragIdx === i) return;
  const moved = miners.splice(dragIdx, 1)[0];
  miners.splice(i, 0, moved);
  dragIdx = null;
  renderTable();
}}
function dragEnd() {{
  dragIdx = null;
  document.querySelectorAll('#minersBody tr').forEach(r => {{
    r.classList.remove('dragging', 'drag-over');
  }});
}}

// ── Collect form data ──
function collectData() {{
  return {{
    MINER_IP:       document.getElementById('cfg-ip').value.trim(),
    PORT:           document.getElementById('cfg-port').value.trim() || '1090',
    MINER_USERNAME: document.getElementById('cfg-user').value.trim() || 'admin',
    MINER_PASSWORD: document.getElementById('cfg-pass').value.trim(),
    WORKER_PREFIX:  document.getElementById('cfg-prefix').value.trim() || 'kop1ma',
    miners: miners.filter(m => m.name).map(m => ({{
      name:    String(m.name).trim(),
      api:     parseInt(m.api) || 0,
      web:     parseInt(m.web) || 0,
      enabled: !!m.enabled,
    }})),
  }};
}}

// ── Status bar ──
function setStatus(msg, type) {{
  const bar = document.getElementById('statusBar');
  const spin = document.getElementById('statusSpin');
  const txt = document.getElementById('statusMsg');
  bar.className = 'status-bar vis ' + type;
  spin.style.display = type === 'loading' ? '' : 'none';
  txt.textContent = msg;
  if (type !== 'loading') setTimeout(() => bar.classList.remove('vis'), 3500);
}}

// ── Save ──
async function saveSettings() {{
  const data = collectData();
  setStatus('Saving config...', 'loading');
  try {{
    const r = await apiPost('/api/settings/save', data);
    const d = await r.json();
    if (d.ok) {{
      setStatus('✅ Config saved successfully', 'ok');
      document.getElementById('restartBtn').disabled = false;
      toast('Saved!', 'ok');
    }} else {{
      setStatus('❌ ' + (d.msg || 'Save failed'), 'err');
      toast('Error saving', 'err');
    }}
  }} catch(e) {{
    setStatus('❌ Network error: ' + e, 'err');
    toast('Connection error', 'err');
  }}
}}

// ── Save & Restart ──
function saveAndRestart() {{
  document.getElementById('restartModal').classList.add('vis');
}}
function closeModal() {{
  document.getElementById('restartModal').classList.remove('vis');
  document.getElementById('modalConfirmView').style.display = '';
  document.getElementById('modalRestartView').classList.remove('vis');
}}
async function confirmRestart() {{
  document.getElementById('modalConfirmView').style.display = 'none';
  document.getElementById('modalRestartView').classList.add('vis');
  const data = collectData();
  try {{
    await apiPost('/api/settings/save', data);
  }} catch(e) {{}}
  try {{
    await apiPost('/api/settings/restart', {{}});
  }} catch(e) {{}}
  setTimeout(() => {{ window.location.href = '/'; }}, 4500);
}}

// ── Toast ──
function toast(msg, type='inf') {{
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'toast ' + type + ' show';
  setTimeout(() => t.classList.remove('show'), 3000);
}}

// ── Init ──
renderTable();
</script>
</body>
</html>"""
