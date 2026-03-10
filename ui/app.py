import os, sys, math, datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
import streamlit.components.v1 as components

PROJECT_ROOT = os.getcwd()
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.pipeline import load_models, run_pipeline
from src.report_generator import generate_pdf_report

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StructScan AI",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────
# CSS  ── Industrial Precision Dark  (Rajdhani + Barlow)
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Barlow:ital,wght@0,300;0,400;0,500;1,300&family=Barlow+Condensed:wght@400;600;700&display=swap');

/* ── RESET & TOKENS ────────────────────────────────────────── */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}

:root{
  --ink:       #05090f;
  --surface:   #0b1220;
  --panel:     #0f1a2e;
  --raised:    #142035;
  --rim:       rgba(96,168,255,0.13);
  --rim-lit:   rgba(96,168,255,0.35);
  --sky:       #60a8ff;
  --ice:       #a8d8ff;
  --fog:       #4e7090;
  --low:       #22d984;
  --mid:       #f5a623;
  --high:      #ff4560;
  --text:      #d8eaff;
  --sub:       #5a80a0;
  --font-head: 'Rajdhani',sans-serif;
  --font-body: 'Barlow',sans-serif;
  --font-cond: 'Barlow Condensed',sans-serif;
}

/* ── BODY ──────────────────────────────────────────────────── */
html,body,.stApp{
  background:var(--ink) !important;
  font-family:var(--font-body);
  color:var(--text);
}

/* Noise grain */
.stApp::before{
  content:'';position:fixed;inset:0;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
  pointer-events:none;z-index:0;opacity:.5;
}

/* Ambient glow */
.stApp::after{
  content:'';position:fixed;
  top:-300px;right:-200px;
  width:700px;height:700px;
  background:radial-gradient(circle,rgba(96,168,255,0.055) 0%,transparent 68%);
  pointer-events:none;z-index:0;
}

/* ── STREAMLIT CHROME ──────────────────────────────────────── */
#MainMenu,footer,header{visibility:hidden}
.block-container{padding:0 2rem 4rem !important;max-width:1280px}
[data-testid="stAppViewBlockContainer"]{padding-top:0 !important}

/* ── SECTION WRAPPER ───────────────────────────────────────── */
.sect{
  background:var(--panel);
  border:1px solid var(--rim);
  border-radius:14px;
  padding:28px 32px 32px;
  margin-bottom:20px;
  position:relative;
  overflow:hidden;
  transition:border-color .3s,box-shadow .3s;
}
.sect:hover{border-color:var(--rim-lit);box-shadow:0 0 40px rgba(96,168,255,.07)}
.sect::after{
  content:'';position:absolute;
  inset:0;border-radius:14px;
  background:linear-gradient(180deg,rgba(96,168,255,.04) 0%,transparent 60%);
  pointer-events:none;
}

/* ── SECTION HEADER ────────────────────────────────────────── */
.sh{
  display:flex;align-items:center;gap:12px;
  margin-bottom:24px;
  padding-bottom:16px;
  border-bottom:1px solid var(--rim);
}
.sh-icon{
  width:36px;height:36px;border-radius:9px;
  display:flex;align-items:center;justify-content:center;
  font-size:1.05rem;flex-shrink:0;
  background:rgba(96,168,255,.1);
  border:1px solid rgba(96,168,255,.2);
}
.sh-text{}
.sh-title{
  font-family:var(--font-head);
  font-size:1.05rem;font-weight:700;
  letter-spacing:.06em;text-transform:uppercase;
  color:var(--ice);line-height:1;
}
.sh-sub{
  font-family:var(--font-body);
  font-size:.78rem;font-weight:300;
  color:var(--sub);margin-top:3px;letter-spacing:.02em;
}

/* ── PAGE HEADER ───────────────────────────────────────────── */
.page-hdr{
  display:flex;align-items:center;justify-content:space-between;
  padding:36px 0 28px;border-bottom:1px solid var(--rim);
  margin-bottom:24px;
}
.page-hdr-left{}
.page-hdr-eyebrow{
  font-family:var(--font-cond);font-size:.7rem;
  font-weight:600;letter-spacing:.18em;text-transform:uppercase;
  color:var(--sky);margin-bottom:6px;
  display:flex;align-items:center;gap:8px;
}
.page-hdr-eyebrow::before{content:'';display:block;width:24px;height:1px;background:var(--sky)}
.page-hdr h1{
  font-family:var(--font-head) !important;
  font-size:2.6rem !important;font-weight:700 !important;
  color:var(--text) !important;letter-spacing:.02em !important;
  line-height:1 !important;margin:0 !important;
  text-shadow:none !important;
}
.page-hdr h1 span{color:var(--sky)}
.page-hdr-desc{
  font-family:var(--font-body);font-size:.88rem;font-weight:300;
  color:var(--sub);margin-top:8px;letter-spacing:.03em;
}
.page-hdr-right{text-align:right}
.sys-badge{
  font-family:var(--font-cond);font-size:.68rem;font-weight:600;
  letter-spacing:.14em;text-transform:uppercase;
  color:var(--sky);background:rgba(96,168,255,.07);
  border:1px solid rgba(96,168,255,.18);
  padding:5px 14px;border-radius:4px;display:inline-block;margin-bottom:8px;
}
.sys-status{
  font-family:var(--font-cond);font-size:.72rem;
  color:var(--low);letter-spacing:.1em;text-transform:uppercase;
  display:flex;align-items:center;gap:6px;justify-content:flex-end;
}
.dot{width:6px;height:6px;border-radius:50%;background:var(--low);
     box-shadow:0 0 8px var(--low);animation:pulse 2s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}

/* ── INPUTS ────────────────────────────────────────────────── */
.stTextInput input,.stSelectbox>div>div,.stTextArea textarea{
  background:var(--raised) !important;
  border:1px solid var(--rim) !important;
  border-radius:8px !important;
  color:var(--text) !important;
  font-family:var(--font-body) !important;
  font-size:.9rem !important;
  transition:border-color .25s,box-shadow .25s !important;
}
.stTextInput input:focus,.stTextArea textarea:focus{
  border-color:rgba(96,168,255,.45) !important;
  box-shadow:0 0 0 3px rgba(96,168,255,.07) !important;
  outline:none !important;
}
label{
  color:var(--fog) !important;font-size:.76rem !important;
  font-weight:500 !important;letter-spacing:.06em !important;
  text-transform:uppercase !important;font-family:var(--font-cond) !important;
}

/* ── BUTTONS ───────────────────────────────────────────────── */
.stButton>button{
  background:linear-gradient(135deg,#1a6fff 0%,#0050cc 100%) !important;
  color:#fff !important;border:none !important;border-radius:8px !important;
  font-family:var(--font-head) !important;font-weight:600 !important;
  font-size:.95rem !important;letter-spacing:.08em !important;
  text-transform:uppercase !important;
  padding:13px 28px !important;
  transition:all .22s cubic-bezier(.4,0,.2,1) !important;
  box-shadow:0 4px 24px rgba(26,111,255,.3) !important;
}
.stButton>button:hover{
  transform:translateY(-2px) !important;
  box-shadow:0 8px 32px rgba(26,111,255,.5) !important;
}
.stDownloadButton>button{
  background:linear-gradient(135deg,#0090d4 0%,#006fa3 100%) !important;
  box-shadow:0 4px 24px rgba(0,144,212,.3) !important;
}
.stDownloadButton>button:hover{box-shadow:0 8px 32px rgba(0,144,212,.5) !important}

/* ── FILE UPLOADER ─────────────────────────────────────────── */
[data-testid="stFileUploader"]{
  background:var(--raised) !important;
  border:2px dashed rgba(96,168,255,.2) !important;
  border-radius:10px !important;
  transition:all .3s !important;
}
[data-testid="stFileUploader"]:hover{
  border-color:rgba(96,168,255,.45) !important;
  background:rgba(96,168,255,.03) !important;
}

/* ── METRICS ───────────────────────────────────────────────── */
[data-testid="metric-container"]{
  background:var(--raised) !important;
  border:1px solid var(--rim) !important;
  border-radius:10px !important;padding:22px 20px !important;
}
[data-testid="stMetricValue"]{
  font-family:var(--font-head) !important;
  font-size:2.1rem !important;font-weight:700 !important;
  color:var(--ice) !important;letter-spacing:.02em !important;
}
[data-testid="stMetricLabel"]{
  color:var(--fog) !important;font-size:.72rem !important;
  font-family:var(--font-cond) !important;
  text-transform:uppercase !important;letter-spacing:.08em !important;
}

/* ── TABS ──────────────────────────────────────────────────── */
[data-testid="stTabs"] [role="tablist"]{
  border-bottom:1px solid var(--rim) !important;gap:0 !important;
}
[data-testid="stTabs"] [role="tab"]{
  font-family:var(--font-cond) !important;font-weight:600 !important;
  font-size:.82rem !important;letter-spacing:.1em !important;
  text-transform:uppercase !important;color:var(--sub) !important;
  padding:10px 20px !important;border-radius:6px 6px 0 0 !important;
  transition:color .2s,background .2s !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"]{
  color:var(--sky) !important;
  background:rgba(96,168,255,.06) !important;
  border-bottom:2px solid var(--sky) !important;
}
[data-testid="stTabs"] [role="tab"]:hover{color:var(--text) !important}

/* ── RECOMMENDATION ROWS ───────────────────────────────────── */
.rec{
  display:grid;grid-template-columns:44px 1fr;
  gap:0 16px;align-items:start;
  padding:16px 20px;border-radius:10px;
  background:var(--raised);border:1px solid var(--rim);
  margin-bottom:10px;transition:border-color .2s,background .2s;
}
.rec:hover{border-color:var(--rim-lit);background:rgba(96,168,255,.04)}
.rec-num{
  width:36px;height:36px;border-radius:8px;
  background:rgba(96,168,255,.1);border:1px solid rgba(96,168,255,.2);
  display:flex;align-items:center;justify-content:center;
  font-family:var(--font-head);font-size:1.1rem;font-weight:700;
  color:var(--sky);flex-shrink:0;margin-top:1px;
}
.rec-body{}
.rec-label{
  font-family:var(--font-cond);font-size:.72rem;font-weight:700;
  letter-spacing:.12em;text-transform:uppercase;color:var(--sky);margin-bottom:4px;
}
.rec-desc{font-size:.88rem;line-height:1.7;color:var(--text);font-weight:300}

/* ── RISK STATUS BANNER ────────────────────────────────────── */
.risk-banner{
  padding:20px 24px;border-radius:10px;
  border-left:4px solid;margin-bottom:0;
  background:var(--raised);
}
.risk-banner.low {border-left-color:var(--low)}
.risk-banner.mid {border-left-color:var(--mid)}
.risk-banner.high{border-left-color:var(--high)}
.rb-eyebrow{
  font-family:var(--font-cond);font-size:.68rem;font-weight:700;
  letter-spacing:.14em;text-transform:uppercase;margin-bottom:5px;
}
.rb-title{
  font-family:var(--font-head);font-size:1.15rem;font-weight:700;
  margin-bottom:8px;color:var(--text);letter-spacing:.03em;
}
.rb-body{font-size:.86rem;line-height:1.75;color:var(--sub);font-weight:300}
.rb-pills{margin-top:14px;display:flex;flex-wrap:wrap;gap:8px}
.pill{
  display:inline-flex;align-items:center;gap:6px;
  font-family:var(--font-cond);font-size:.7rem;font-weight:600;
  letter-spacing:.08em;text-transform:uppercase;
  padding:5px 12px;border-radius:4px;
  background:rgba(96,168,255,.07);border:1px solid var(--rim);color:var(--fog);
}

/* ── SEPARATOR ─────────────────────────────────────────────── */
hr{border:none;border-top:1px solid var(--rim);margin:40px 0 16px}

/* ── ALERTS ────────────────────────────────────────────────── */
.stAlert{border-radius:8px !important}

/* ── SPINNER ───────────────────────────────────────────────── */
.stSpinner>div{border-color:var(--sky) transparent transparent transparent !important}

/* ── SCROLLBAR ─────────────────────────────────────────────── */
::-webkit-scrollbar{width:5px}
::-webkit-scrollbar-track{background:var(--ink)}
::-webkit-scrollbar-thumb{background:rgba(96,168,255,.25);border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:rgba(96,168,255,.45)}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# HELPERS  –  section header HTML
# ─────────────────────────────────────────────────────────────
def sh(icon: str, title: str, sub: str = "") -> str:
    sub_html = f'<div class="sh-sub">{sub}</div>' if sub else ""
    return f"""
    <div class="sh">
      <div class="sh-icon">{icon}</div>
      <div class="sh-text">
        <div class="sh-title">{title}</div>
        {sub_html}
      </div>
    </div>"""


# ─────────────────────────────────────────────────────────────
# PREMIUM SVG GAUGE
# ─────────────────────────────────────────────────────────────
def render_gauge(severity: float, risk: str) -> str:
    # Colors per zone
    zone_colors = {"Low": "#22d984", "Medium": "#f5a623", "High": "#ff4560"}
    needle_color = zone_colors.get(risk, "#60a8ff")
    risk_label   = {"Low": "LOW RISK", "Medium": "MODERATE RISK", "High": "HIGH RISK"}.get(risk, "—")

    W, H = 380, 230
    cx, cy = W // 2, H - 44
    R_outer, R_inner = 130, 95   # track radii
    R_needle = 108

    def pt(angle_deg, r):
        a = math.radians(angle_deg)
        return cx + r * math.cos(a), cy - r * math.sin(a)

    def arc(r, a1, a2, sw, color, dash="", linecap="butt", opacity=1.0):
        x1, y1 = pt(a1, r); x2, y2 = pt(a2, r)
        laf = 1 if abs(a2 - a1) > 180 else 0
        sf  = 1 if a2 < a1 else 0
        d   = f"M {x1:.3f} {y1:.3f} A {r} {r} 0 {laf} {sf} {x2:.3f} {y2:.3f}"
        dash_attr = f'stroke-dasharray="{dash}"' if dash else ""
        return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="{linecap}" {dash_attr} opacity="{opacity}"/>'

    # Needle end
    needle_deg = 180 - (severity / 100) * 180
    nex, ney   = pt(needle_deg, R_needle)
    # needle tail (small nub opposite)
    ntx, nty   = pt(needle_deg + 180, 14)

    # Tick marks
    ticks_svg = ""
    for i in range(11):
        deg   = 180 - i * 18          # 180° → 0°
        is_maj = (i % 5 == 0)
        r1 = R_outer + 6
        r2 = R_outer + (16 if is_maj else 10)
        ax1, ay1 = pt(deg, r1); ax2, ay2 = pt(deg, r2)
        w  = 2 if is_maj else 1
        op = ".5" if is_maj else ".25"
        ticks_svg += f'<line x1="{ax1:.2f}" y1="{ay1:.2f}" x2="{ax2:.2f}" y2="{ay2:.2f}" stroke="#a8d8ff" stroke-width="{w}" opacity="{op}"/>'
        # Major tick value labels
        if is_maj:
            val = i * 10
            lx, ly = pt(deg, R_outer + 28)
            ticks_svg += f'<text x="{lx:.1f}" y="{ly+4:.1f}" text-anchor="middle" fill="rgba(168,216,255,0.35)" font-size="9.5" font-family="Barlow Condensed,sans-serif" font-weight="600">{val}</text>'

    # Zone separator dividers
    dividers = ""
    for deg in [60, 120]:
        ax1, ay1 = pt(deg, R_inner - 4); ax2, ay2 = pt(deg, R_outer + 4)
        dividers += f'<line x1="{ax1:.2f}" y1="{ay1:.2f}" x2="{ax2:.2f}" y2="{ay2:.2f}" stroke="#05090f" stroke-width="3.5"/>'

    # Active progress arc
    progress_a2 = max(180 - (severity / 100) * 180, 0.1)
    R_mid = (R_outer + R_inner) // 2

    return f"""
<div style="display:flex;flex-direction:column;align-items:center;padding:8px 0 4px">
<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
<defs>
  <filter id="glow_n">
    <feGaussianBlur stdDeviation="5" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="glow_s">
    <feGaussianBlur stdDeviation="3" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="shadow">
    <feDropShadow dx="0" dy="3" stdDeviation="6" flood-color="rgba(0,0,0,.6)"/>
  </filter>
  <radialGradient id="hub" cx="50%" cy="50%">
    <stop offset="0%" stop-color="#d8eaff" stop-opacity=".9"/>
    <stop offset="60%" stop-color="{needle_color}"/>
    <stop offset="100%" stop-color="{needle_color}" stop-opacity=".6"/>
  </radialGradient>
  <linearGradient id="low_g" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" stop-color="#22d984"/>
    <stop offset="100%" stop-color="#18b870"/>
  </linearGradient>
  <linearGradient id="mid_g" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" stop-color="#f5c842"/>
    <stop offset="100%" stop-color="#f5a623"/>
  </linearGradient>
  <linearGradient id="hi_g" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" stop-color="#ff7340"/>
    <stop offset="100%" stop-color="#ff4560"/>
  </linearGradient>
</defs>

<!-- ── BACKGROUND TRACK ── -->
{arc(R_mid, 180, 0, R_outer-R_inner, "rgba(255,255,255,.04)", linecap="butt")}

<!-- ── ZONE ARCS ── -->
<path d="M {pt(180,R_outer)[0]:.3f} {pt(180,R_outer)[1]:.3f}
         A {R_outer} {R_outer} 0 0 0 {pt(120,R_outer)[0]:.3f} {pt(120,R_outer)[1]:.3f}
         L {pt(120,R_inner)[0]:.3f} {pt(120,R_inner)[1]:.3f}
         A {R_inner} {R_inner} 0 0 1 {pt(180,R_inner)[0]:.3f} {pt(180,R_inner)[1]:.3f} Z"
      fill="url(#low_g)" opacity=".85"/>
<path d="M {pt(120,R_outer)[0]:.3f} {pt(120,R_outer)[1]:.3f}
         A {R_outer} {R_outer} 0 0 0 {pt(60,R_outer)[0]:.3f} {pt(60,R_outer)[1]:.3f}
         L {pt(60,R_inner)[0]:.3f} {pt(60,R_inner)[1]:.3f}
         A {R_inner} {R_inner} 0 0 1 {pt(120,R_inner)[0]:.3f} {pt(120,R_inner)[1]:.3f} Z"
      fill="url(#mid_g)" opacity=".85"/>
<path d="M {pt(60,R_outer)[0]:.3f} {pt(60,R_outer)[1]:.3f}
         A {R_outer} {R_outer} 0 0 0 {pt(0,R_outer)[0]:.3f} {pt(0,R_outer)[1]:.3f}
         L {pt(0,R_inner)[0]:.3f} {pt(0,R_inner)[1]:.3f}
         A {R_inner} {R_inner} 0 0 1 {pt(60,R_inner)[0]:.3f} {pt(60,R_inner)[1]:.3f} Z"
      fill="url(#hi_g)" opacity=".85"/>

<!-- ── ZONE DIVIDERS ── -->
{dividers}

<!-- ── TICK MARKS ── -->
{ticks_svg}

<!-- ── ZONE LABELS ── -->
<text x="{pt(150,R_inner+10)[0]:.1f}" y="{pt(150,R_inner+10)[1]+4:.1f}"
      text-anchor="middle" fill="#22d984" font-size="10.5"
      font-family="Barlow Condensed,sans-serif" font-weight="700" letter-spacing=".1em">LOW</text>
<text x="{cx}" y="{cy - R_inner - 14}"
      text-anchor="middle" fill="#f5a623" font-size="10.5"
      font-family="Barlow Condensed,sans-serif" font-weight="700" letter-spacing=".1em">MED</text>
<text x="{pt(30,R_inner+10)[0]:.1f}" y="{pt(30,R_inner+10)[1]+4:.1f}"
      text-anchor="middle" fill="#ff4560" font-size="10.5"
      font-family="Barlow Condensed,sans-serif" font-weight="700" letter-spacing=".1em">HIGH</text>

<!-- ── PROGRESS GLOW ARC ── -->
{arc(R_mid, 180, progress_a2, 6, needle_color, linecap="round", opacity=0.55)}
{arc(R_mid, 180, progress_a2, 2.5, needle_color, linecap="round", opacity=0.9)}

<!-- ── NEEDLE SHADOW ── -->
<line x1="{ntx:.2f}" y1="{nty:.2f}" x2="{nex:.2f}" y2="{ney:.2f}"
      stroke="rgba(0,0,0,.45)" stroke-width="6" stroke-linecap="round"/>

<!-- ── NEEDLE ── -->
<line x1="{ntx:.2f}" y1="{nty:.2f}" x2="{nex:.2f}" y2="{ney:.2f}"
      stroke="{needle_color}" stroke-width="3.5" stroke-linecap="round"
      filter="url(#glow_n)"/>

<!-- ── HUB ── -->
<circle cx="{cx}" cy="{cy}" r="13" fill="#0b1220" filter="url(#shadow)"/>
<circle cx="{cx}" cy="{cy}" r="10" fill="url(#hub)"/>
<circle cx="{cx}" cy="{cy}" r="4"  fill="white" opacity=".95"/>

<!-- ── SCORE DISPLAY ── -->
<text x="{cx}" y="{cy-26}" text-anchor="middle"
      fill="{needle_color}" font-size="32" font-family="Rajdhani,sans-serif"
      font-weight="700" letter-spacing=".02em" filter="url(#glow_s)">{severity:.1f}</text>
<text x="{cx}" y="{cy-9}" text-anchor="middle"
      fill="rgba(168,216,255,.35)" font-size="10"
      font-family="Barlow Condensed,sans-serif" font-weight="600" letter-spacing=".12em">/ 100</text>

<!-- ── RISK BADGE ── -->
<rect x="{cx-52}" y="{cy+8}" width="104" height="24" rx="5"
      fill="{needle_color}" fill-opacity=".12"
      stroke="{needle_color}" stroke-width="1" stroke-opacity=".35"/>
<text x="{cx}" y="{cy+24}" text-anchor="middle"
      fill="{needle_color}" font-size="11" font-family="Barlow Condensed,sans-serif"
      font-weight="700" letter-spacing=".14em">{risk_label}</text>
</svg>
</div>
"""


# ─────────────────────────────────────────────────────────────
# RECOMMENDATION DATA
# ─────────────────────────────────────────────────────────────
RECS = {
    "Low": {
        "color": "#22d984", "cls": "low",
        "headline": "Low Risk — Routine Monitoring Advised",
        "summary": "Hairline or surface-level cracks detected, typically under 0.2 mm width. These are generally cosmetic and non-structural, caused by thermal cycling, drying shrinkage, or minor settlement. No immediate danger present, though baseline documentation and periodic monitoring remain best practice.",
        "timeline": "Action within 90 days", "specialist": "General maintenance crew",
        "actions": [
            ("01", "Clean & Baseline Document", "Remove dust and debris from cracks. Photograph with a ruler in frame and measure width using a feeler gauge or crack comparator card. Record date, orientation (horizontal / vertical / diagonal), length, and GPS location as a reference baseline."),
            ("02", "Apply Flexible Sealant", "Use a polyurethane, silicone, or elastomeric crack filler to block moisture ingress and freeze-thaw damage. Prime the surface, slightly overfill, and strike flush once cured."),
            ("03", "Install Tell-Tale Gauges", "Affix adhesive tell-tale gauges at crack endpoints. Re-check after every seasonal change to detect any width progression due to thermal expansion or moisture movement."),
            ("04", "6-Month Follow-Up Inspection", "Schedule a formal visual re-inspection at 6 and 12 months. Compare against baseline photographs. Escalate to Medium-risk protocol if any crack exceeds 0.3 mm or new cracking appears."),
            ("05", "Update Maintenance Register", "Log all findings with grid/GPS reference, inspector credentials, date, and actions taken. Critical for warranty, insurance, and future inspection continuity."),
        ]
    },
    "Medium": {
        "color": "#f5a623", "cls": "mid",
        "headline": "Moderate Risk — Prompt Professional Repair Required",
        "summary": "Significant cracks detected, typically 0.2–1.0 mm width, indicating structural stress, load redistribution, or early foundation movement. While not immediately catastrophic, these can propagate and cause rebar corrosion, water ingress, and long-term degradation if left unaddressed.",
        "timeline": "Repair within 30–45 days", "specialist": "Licensed structural engineer",
        "actions": [
            ("01", "Structural Engineer Site Assessment", "Engage a licensed structural engineer within 2–4 weeks. Request load-path analysis to determine whether cracks are active (widening) or dormant, and to identify root cause (overload, differential settlement, shrinkage, or thermal stress)."),
            ("02", "Epoxy / Polyurethane Crack Injection", "For cracks ≥ 0.3 mm, perform low-pressure injection with low-viscosity epoxy (e.g. Sikadur-52) or polyurethane foam. This restores tensile strength, seals against moisture and chlorides, and prevents further propagation. Allow full cure before re-loading."),
            ("03", "Inspect All Connections & Joints", "Check nearby bolted connections, welds, expansion joints, and bearing plates for fatigue, corrosion, loosening, or misalignment. Retorque or replace fasteners per engineer specifications."),
            ("04", "Restrict Imposed Loads", "Temporarily reduce or divert heavy equipment, machinery, stacked materials, and concentrated live loads from the affected zone until repairs are completed and verified by the engineer."),
            ("05", "Install Digital Crack Monitors", "Fit mechanical tell-tales or digital crack-displacement transducers. Record weekly. Alert the structural engineer immediately if movement exceeds 0.1 mm/week."),
            ("06", "Apply Waterproof Membrane", "After crack repair, apply a 2-coat crystalline waterproofing system (e.g. Xypex or Kryton) or flexible polymer-modified coating to prevent future water infiltration and rebar corrosion onset."),
        ]
    },
    "High": {
        "color": "#ff4560", "cls": "high",
        "headline": "Critical Risk — Immediate Emergency Action Required",
        "summary": "Severe crack patterns detected — typically > 1.0 mm width, diagonal shear cracks, flexural cracks at mid-span, or extensive crack networks. This signals significant structural distress: possible overloading, foundation failure, or advanced rebar corrosion. Risk of partial or complete structural failure is elevated.",
        "timeline": "IMMEDIATE — within 24–72 hours", "specialist": "Emergency structural engineer + authority notification",
        "actions": [
            ("01", "EVACUATE & Restrict Access Now", "Immediately restrict all personnel, vehicles, and public access to the affected structural zone. Post hazard signage, establish an exclusion perimeter, and do not allow re-entry until a structural engineer issues written clearance."),
            ("02", "Emergency Engineering Consultation", "Contact a licensed structural engineer for an emergency site visit within 24 hours. Bring all as-built drawings, original design calculations, soil investigation reports, historical inspection records, and details of any loading changes."),
            ("03", "Non-Destructive Testing (NDT)", "Commission urgent NDT: Ultrasonic Pulse Velocity (UPV) for concrete integrity, Ground-Penetrating Radar (GPR) for rebar location and voids, Rebound Hammer for surface strength, and half-cell potential mapping to detect active rebar corrosion."),
            ("04", "Install Temporary Shoring", "Engineer-designed temporary steel props, scaffold shores, or flying shores must be installed immediately to stabilise the structure, limit further deflection, and redistribute loads to sound elements while permanent repairs are designed."),
            ("05", "Full Structural Remediation", "Depending on findings: expose and treat corroded rebar (descaling + corrosion inhibitor + patch mortar); apply CFRP wrapping for shear/flexural strengthening; install external post-tensioning; perform section enlargement; or full member replacement if beyond repair."),
            ("06", "Root Cause Analysis & Code Review", "Investigate the cause thoroughly — overload, design deficiency, poor construction quality, aggressive environment, or foundation movement. Redesign affected elements to current code (IS 456, ACI 318-19, Eurocode 2, or applicable standard)."),
            ("07", "Regulatory Notification", "Notify the local municipal authority and building department as legally required. Engage a third-party peer reviewer if mandated. Maintain a full paper trail of all assessments, remediation actions, and sign-offs for legal and insurance purposes."),
        ]
    }
}


# ─────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────
for k, v in [("page","landing"), ("result",None)]:
    if k not in st.session_state: st.session_state[k] = v


# ─────────────────────────────────────────────────────────────
# LANDING PAGE
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "landing":
    components.html("""
<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Barlow:wght@300;400&family=Barlow+Condensed:wght@400;600;700&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
body{
  background:#05090f;font-family:'Barlow',sans-serif;
  min-height:100vh;display:flex;align-items:center;justify-content:center;
  overflow:hidden;
}
/* subtle grid */
body::before{
  content:'';position:fixed;inset:0;
  background-image:linear-gradient(rgba(96,168,255,.03) 1px,transparent 1px),
    linear-gradient(90deg,rgba(96,168,255,.03) 1px,transparent 1px);
  background-size:48px 48px;
}
/* glow orbs */
.orb{position:fixed;border-radius:50%;filter:blur(100px);pointer-events:none}
.o1{width:600px;height:600px;top:-220px;left:-180px;
    background:radial-gradient(circle,rgba(26,111,255,.2),transparent);animation:drift 14s ease-in-out infinite alternate}
.o2{width:500px;height:500px;bottom:-180px;right:-160px;
    background:radial-gradient(circle,rgba(0,144,212,.15),transparent);animation:drift 18s ease-in-out infinite alternate-reverse}
@keyframes drift{from{transform:translate(0,0)}to{transform:translate(60px,40px)}}

.card{
  position:relative;z-index:1;
  max-width:940px;width:92%;
  background:linear-gradient(160deg,rgba(15,26,46,.97) 0%,rgba(11,18,32,.99) 100%);
  border:1px solid rgba(96,168,255,.15);border-radius:18px;
  padding:60px 56px;
  box-shadow:0 40px 100px rgba(0,0,0,.7),0 0 0 1px rgba(96,168,255,.05);
  animation:rise .9s cubic-bezier(.22,1,.36,1) forwards;opacity:0;
}
@keyframes rise{from{opacity:0;transform:translateY(50px)}to{opacity:1;transform:translateY(0)}}
.card::before{
  content:'';position:absolute;top:0;left:10%;right:10%;height:1px;
  background:linear-gradient(90deg,transparent,rgba(96,168,255,.6),transparent);
}
/* scan line */
.scan{position:absolute;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(96,168,255,.7),transparent);
  animation:scan 6s ease-in-out infinite;opacity:0}
@keyframes scan{0%,100%{top:0;opacity:0}8%{opacity:.8}92%{opacity:.8}100%{top:100%;opacity:0}}

.eyebrow{
  font-family:'Barlow Condensed',sans-serif;font-size:.7rem;font-weight:700;
  letter-spacing:.2em;text-transform:uppercase;color:#60a8ff;
  display:flex;align-items:center;gap:10px;margin-bottom:18px;
}
.eyebrow::before{content:'';width:28px;height:1px;background:#60a8ff}
h1{
  font-family:'Rajdhani',sans-serif;font-size:3.8rem;font-weight:700;
  color:#d8eaff;letter-spacing:.04em;line-height:1;margin-bottom:6px;
}
h1 span{color:#60a8ff}
.tagline{
  font-size:1rem;font-weight:300;color:#4e7090;letter-spacing:.04em;
  margin-bottom:50px;border-left:2px solid rgba(96,168,255,.25);
  padding-left:16px;margin-left:2px;line-height:1.6;
}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:52px}
@media(max-width:700px){.grid{grid-template-columns:repeat(2,1fr)}}
.feat{
  padding:22px 18px;
  background:rgba(96,168,255,.04);
  border:1px solid rgba(96,168,255,.1);
  border-radius:10px;
  transition:all .25s;
}
.feat:hover{
  background:rgba(96,168,255,.09);border-color:rgba(96,168,255,.3);
  transform:translateY(-4px);box-shadow:0 10px 30px rgba(0,0,0,.4);
}
.feat-n{
  font-family:'Barlow Condensed',sans-serif;font-size:.62rem;font-weight:700;
  letter-spacing:.15em;text-transform:uppercase;color:#3a6080;margin-bottom:10px;
}
.feat-icon{font-size:1.6rem;margin-bottom:10px;display:block}
.feat-t{
  font-family:'Rajdhani',sans-serif;font-size:.95rem;font-weight:700;
  color:#d8eaff;letter-spacing:.04em;margin-bottom:5px;
}
.feat-d{font-size:.78rem;color:#4e7090;line-height:1.55;font-weight:300}
.bottom{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px}
.version{
  font-family:'Barlow Condensed',sans-serif;font-size:.68rem;font-weight:600;
  letter-spacing:.12em;text-transform:uppercase;color:#3a6080;
  border:1px solid rgba(96,168,255,.15);padding:6px 14px;border-radius:4px;
}
</style>
</head><body>
<div class="orb o1"></div>
<div class="orb o2"></div>
<div class="card">
  <div class="scan"></div>
  <div class="eyebrow">Structural Intelligence Platform</div>
  <h1>Struct<span>Scan</span> AI</h1>
  <p class="tagline">
    AI-powered structural crack detection, severity quantification &amp; risk assessment<br>
    built for field engineers and safety inspection teams.
  </p>
  <div class="grid">
    <div class="feat">
      <div class="feat-n">Module 01</div>
      <span class="feat-icon">⚡</span>
      <div class="feat-t">YOLO Detection</div>
      <div class="feat-d">Real-time crack detection on high-resolution structural imagery</div>
    </div>
    <div class="feat">
      <div class="feat-n">Module 02</div>
      <span class="feat-icon">📊</span>
      <div class="feat-t">Risk Gauge</div>
      <div class="feat-d">Precision 0–100 severity scoring with animated precision gauge</div>
    </div>
    <div class="feat">
      <div class="feat-n">Module 03</div>
      <span class="feat-icon">🔥</span>
      <div class="feat-t">Dual Viz</div>
      <div class="feat-d">Toggle between bounding box detection and density heatmap modes</div>
    </div>
    <div class="feat">
      <div class="feat-n">Module 04</div>
      <span class="feat-icon">📄</span>
      <div class="feat-t">PDF Export</div>
      <div class="feat-d">Full inspection reports + comparison snapshot PDFs</div>
    </div>
  </div>
  <div class="bottom">
    <div class="version">v2.0 · YOLO Deep Learning · Field Edition</div>
  </div>
</div>
</body></html>
""", height=640)

    c1, c2, c3 = st.columns([2,1,2])
    with c2:
        if st.button("Launch Dashboard →", use_container_width=True):
            st.session_state.page = "inspection"
            st.rerun()
    st.stop()


# ─────────────────────────────────────────────────────────────
# INSPECTION PAGE  ── PAGE HEADER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-hdr">
  <div class="page-hdr-left">
    <div class="page-hdr-eyebrow">Structural Health Monitoring Platform</div>
    <h1>Struct<span>Scan</span> <span style="font-weight:400;color:var(--fog)">AI</span></h1>
    <div class="page-hdr-desc">Advanced Crack Detection &amp; Risk Intelligence Dashboard · YOLO Deep Learning Engine</div>
  </div>
  <div class="page-hdr-right">
    <div class="sys-badge">System Online</div>
    <div class="sys-status"><span class="dot"></span> All modules operational</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# § 1  INSPECTION DETAILS
# ─────────────────────────────────────────────────────────────
st.markdown('<div class="sect">', unsafe_allow_html=True)
st.markdown(sh("📋", "Inspection Details", "Fill in project metadata — included in all exported reports"), unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1: engineer_name     = st.text_input("Engineer Name",    "Adrija Roy")
with c2: project_id        = st.text_input("Project ID",       "CIV-021")
with c3: location          = st.text_input("Site Location",    "Site A, Block 3")
with c4: construction_type = st.selectbox("Construction Type", [
    "Residential Building","Commercial Building","Bridge / Flyover",
    "Industrial Structure","Heritage Structure","Infrastructure / Road","Other"])

c5, c6 = st.columns([1, 2])
with c5: inspection_date = st.date_input("Inspection Date", datetime.date.today())
with c6: notes           = st.text_input("Site Notes (optional)", "")

st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# § 2  IMAGE UPLOAD
# ─────────────────────────────────────────────────────────────
st.markdown('<div class="sect">', unsafe_allow_html=True)
st.markdown(sh("📤", "Upload Structural Image", "High-resolution JPG or PNG — clear, well-lit, non-blurred photos yield the best results"), unsafe_allow_html=True)
uploaded_image = st.file_uploader("", type=["jpg","jpeg","png"], label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# MODEL LOAD
# ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_model():
    return load_models()

model = get_model()


# ─────────────────────────────────────────────────────────────
# RUN ANALYSIS
# ─────────────────────────────────────────────────────────────
if uploaded_image:
    temp_dir = os.path.join(PROJECT_ROOT, "results")
    os.makedirs(temp_dir, exist_ok=True)
    tmp_path = os.path.join(temp_dir, "temp_uploaded.jpg")
    with open(tmp_path, "wb") as f:
        f.write(uploaded_image.read())

    st.markdown('<div class="sect">', unsafe_allow_html=True)
    st.markdown(sh("🖼️", "Uploaded Image Preview", "Source image submitted for analysis"), unsafe_allow_html=True)
    st.image(tmp_path, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    cc1, cc2, cc3 = st.columns([1, 2, 1])
    with cc2:
        if st.button("Run AI Structural Analysis →", use_container_width=True, type="primary"):
            with st.spinner("Deep-learning model analysing structural integrity…"):
                st.session_state.result = run_pipeline(
                    model=model,
                    image_path=tmp_path,
                    output_path=os.path.join(temp_dir, "annotated_output.jpg")
                )
                st.session_state.tmp_path = tmp_path
            st.success("✅ Analysis complete — results below.")
            st.rerun()


# ─────────────────────────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────────────────────────
if st.session_state.result:
    r   = st.session_state.result
    rl  = r["risk_level"]
    rec = RECS[rl]

    # ── § GAUGE + METRICS ───────────────────────────────────
    col_g, col_m = st.columns([1, 1.65], gap="large")

    with col_g:
        st.markdown('<div class="sect" style="min-height:320px">', unsafe_allow_html=True)
        st.markdown(sh("📈", "Severity Gauge", "0 = no damage · 100 = catastrophic failure"), unsafe_allow_html=True)
        components.html(render_gauge(r["severity_score"], rl), height=245)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_m:
        st.markdown('<div class="sect" style="min-height:320px">', unsafe_allow_html=True)
        st.markdown(sh("📊", "Analysis Metrics", "Quantified results from the AI inference pass"), unsafe_allow_html=True)

        m1, m2, m3 = st.columns(3)
        m1.metric("Crack Coverage",  f"{r['crack_percentage']:.2f}%")
        m2.metric("Severity Score",  f"{r['severity_score']:.1f}")
        emoji = {"Low":"↓ Low","Medium":"→ Medium","High":"↑ High"}
        m3.metric("Risk Level",      emoji.get(rl, rl))

        st.markdown(f"""
        <div class="risk-banner {rec['cls']}" style="margin-top:18px">
          <div class="rb-eyebrow" style="color:{rec['color']}">{rl.upper()} RISK ASSESSMENT</div>
          <div class="rb-title">{rec['headline']}</div>
          <div class="rb-body">{rec['summary'][:250]}…</div>
          <div class="rb-pills">
            <span class="pill">⏱ {rec['timeline']}</span>
            <span class="pill">👷 {rec['specialist']}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── § VISUALIZATION ─────────────────────────────────────
    st.markdown('<div class="sect">', unsafe_allow_html=True)
    st.markdown(sh("🧠", "Crack Detection Visualization", "Switch between detection modes using the tabs below"), unsafe_allow_html=True)

    t_box, t_heat = st.tabs(["  Bounding Box Detection  ", "  Density Heatmap  "])
    with t_box:
        st.image(r["annotated_image"], use_container_width=True,
                 caption="AI-detected cracks with confidence bounding boxes")
    with t_heat:
        if r.get("heatmap_path") and os.path.exists(r["heatmap_path"]):
            st.image(r["heatmap_path"], use_container_width=True,
                     caption="Crack density heatmap — brighter zones indicate higher crack concentration")
        else:
            st.info("Heatmap unavailable for this image. Ensure heatmap generation is enabled in the pipeline config.")

    st.markdown('</div>', unsafe_allow_html=True)

    # ── § RECOMMENDATIONS ───────────────────────────────────
    st.markdown('<div class="sect">', unsafe_allow_html=True)
    st.markdown(sh("🔧", "Repair & Action Recommendations",
                   f"Prioritised action plan for {rl.lower()}-risk structural cracking"), unsafe_allow_html=True)

    st.markdown(f'<p style="font-size:.88rem;line-height:1.8;color:var(--sub);margin-bottom:22px">{rec["summary"]}</p>', unsafe_allow_html=True)

    for icon_num, title, desc in rec["actions"]:
        st.markdown(f"""
        <div class="rec">
          <div class="rec-num">{icon_num}</div>
          <div class="rec-body">
            <div class="rec-label">{title}</div>
            <div class="rec-desc">{desc}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── § EXPORTS ────────────────────────────────────────────
    st.markdown('<div class="sect">', unsafe_allow_html=True)
    st.markdown(sh("📥", "Export & Download", "Generate inspection-grade PDFs for records and briefings"), unsafe_allow_html=True)

    tab_pdf, tab_snap = st.tabs(["  Full Inspection Report PDF  ", "  Comparison Snapshot PDF  "])

    # --- Full PDF ---
    with tab_pdf:
        st.markdown('<p style="color:var(--sub);font-size:.86rem;margin-bottom:18px">Generates a comprehensive, print-ready PDF with gauge, metrics, visualizations, and all detailed recommendations.</p>', unsafe_allow_html=True)
        if st.button("Generate Full Inspection Report →", use_container_width=True, type="primary"):
            with st.spinner("Compiling professional inspection report…"):
                rdir = os.path.join(PROJECT_ROOT, "reports"); os.makedirs(rdir, exist_ok=True)
                rpath = os.path.join(rdir, "StructScan_Report.pdf")
                generate_pdf_report(
                    output_path=rpath,
                    engineer_name=engineer_name, project_id=project_id,
                    crack_percentage=float(r["crack_percentage"]),
                    severity_score=float(r["severity_score"]), risk_level=str(rl),
                    annotated_image_path=r["annotated_image_path"],
                    heatmap_path=r.get("heatmap_path"),
                    location=location, construction_type=construction_type,
                    inspection_date=str(inspection_date), site_notes=notes,
                    recommendations=rec["actions"],
                    timeline=rec["timeline"], specialist=rec["specialist"],
                )
            with open(rpath, "rb") as f:
                st.download_button("Download PDF Report ↓", f,
                    file_name=f"StructScan_{project_id}_{inspection_date}.pdf",
                    mime="application/pdf", use_container_width=True)
            st.success("Report ready for download.")

    # --- Snapshot PDF ---
    with tab_snap:
        st.markdown('<p style="color:var(--sub);font-size:.86rem;margin-bottom:16px">Side-by-side visual comparison PDF (bounding box vs heatmap) — ideal for quick briefings and site handover.</p>', unsafe_allow_html=True)

        sc1, sc2 = st.columns(2)
        with sc1: include_bbox = st.checkbox("Include Bounding Box View", value=True)
        with sc2: include_heat = st.checkbox("Include Heatmap View",      value=True)

        if st.button("Generate Comparison Snapshot →", use_container_width=True):
            try:
                import cv2, numpy as np, tempfile
                from reportlab.lib.pagesizes import A4, landscape
                from reportlab.lib import colors as rc
                from reportlab.platypus import SimpleDocTemplate, Image as RLI, Table, TableStyle, Paragraph, Spacer
                from reportlab.lib.styles import ParagraphStyle
                from reportlab.lib.units import mm
                from reportlab.lib.enums import TA_CENTER

                sdir = os.path.join(PROJECT_ROOT, "reports"); os.makedirs(sdir, exist_ok=True)
                spath = os.path.join(sdir, "StructScan_Snapshot.pdf")

                ann_p = r.get("annotated_image_path") or r.get("annotated_image")
                heat_p = r.get("heatmap_path")

                TS = ParagraphStyle('T', fontName='Helvetica-Bold', fontSize=16,
                                    textColor=rc.HexColor('#60a8ff'), alignment=TA_CENTER, spaceAfter=4)
                SS = ParagraphStyle('S', fontName='Helvetica', fontSize=8.5,
                                    textColor=rc.HexColor('#4e7090'), alignment=TA_CENTER, spaceAfter=10)
                LS = ParagraphStyle('L', fontName='Helvetica-Bold', fontSize=9.5,
                                    textColor=rc.HexColor('#d8eaff'), alignment=TA_CENTER, spaceAfter=3)
                MS = ParagraphStyle('M', fontName='Helvetica-Bold', fontSize=11,
                                    textColor=rc.HexColor(rec["color"]), alignment=TA_CENTER)

                doc = SimpleDocTemplate(spath, pagesize=landscape(A4),
                                        leftMargin=14*mm, rightMargin=14*mm,
                                        topMargin=12*mm, bottomMargin=12*mm)
                story = [
                    Paragraph("StructScan AI  ·  Comparison Snapshot Report", TS),
                    Paragraph(f"Project: {project_id}  ·  Engineer: {engineer_name}  ·  Date: {inspection_date}  ·  Site: {location}", SS),
                ]

                items = []
                if include_bbox and ann_p  and os.path.exists(str(ann_p)):  items.append(("Bounding Box Detection", str(ann_p)))
                if include_heat and heat_p and os.path.exists(heat_p):       items.append(("Density Heatmap",        heat_p))

                if items:
                    pw = landscape(A4)[0] - 28*mm
                    iw = pw / max(len(items), 1) - 8*mm
                    ih = iw * 0.66
                    with tempfile.TemporaryDirectory() as td:
                        cols = []
                        for lbl, ip in items:
                            tp = os.path.join(td, os.path.basename(ip))
                            cv2.imwrite(tp, cv2.imread(ip))
                            cols.append([Paragraph(lbl, LS), RLI(tp, width=iw, height=ih)])
                        tbl = Table([[c[0] for c in cols],[c[1] for c in cols]],
                                    colWidths=[iw+8*mm]*len(cols))
                        tbl.setStyle(TableStyle([
                            ('BACKGROUND',(0,0),(-1,-1),rc.HexColor('#0f1a2e')),
                            ('GRID',(0,0),(-1,-1),.5,rc.HexColor('#1a3050')),
                            ('ALIGN',(0,0),(-1,-1),'CENTER'),
                            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                            ('TOPPADDING',(0,0),(-1,-1),8),
                            ('BOTTOMPADDING',(0,0),(-1,-1),8),
                        ]))
                        story.append(tbl)

                story.append(Spacer(1, 7*mm))
                pw4 = (landscape(A4)[0] - 28*mm) / 4
                mtbl = Table([[
                    Paragraph(f"Crack Coverage\n{r['crack_percentage']:.2f}%",    MS),
                    Paragraph(f"Severity Score\n{r['severity_score']:.1f} / 100", MS),
                    Paragraph(f"Risk Level\n{rl}",                                 MS),
                    Paragraph(f"Construction Type\n{construction_type}",           MS),
                ]], colWidths=[pw4]*4)
                mtbl.setStyle(TableStyle([
                    ('BACKGROUND',(0,0),(-1,-1),rc.HexColor('#0b1220')),
                    ('GRID',(0,0),(-1,-1),.5,rc.HexColor('#1a3050')),
                    ('ALIGN',(0,0),(-1,-1),'CENTER'),
                    ('TOPPADDING',(0,0),(-1,-1),10),
                    ('BOTTOMPADDING',(0,0),(-1,-1),10),
                ]))
                story.append(mtbl)
                doc.build(story)

                with open(spath,"rb") as f:
                    st.download_button("Download Snapshot PDF ↓", f,
                        file_name=f"StructScan_Snapshot_{project_id}_{inspection_date}.pdf",
                        mime="application/pdf", use_container_width=True)
                st.success("Snapshot PDF ready.")
            except Exception as e:
                st.error(f"Snapshot generation failed: {e}")

    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<hr>
<div style="display:flex;justify-content:space-between;align-items:center;padding-bottom:32px;flex-wrap:wrap;gap:12px">
  <div style="font-family:'Barlow Condensed',sans-serif;font-size:.7rem;
              letter-spacing:.1em;text-transform:uppercase;color:#2a4560">
    © 2025 StructScan AI · Structural Health Monitoring Platform
  </div>
  <div style="font-family:'Barlow Condensed',sans-serif;font-size:.7rem;
              letter-spacing:.08em;text-transform:uppercase;color:#2a4560">
    Powered by YOLO Deep Learning · Built for field structural engineers
  </div>
</div>
""", unsafe_allow_html=True)
