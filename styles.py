
import streamlit as st

# ZeroBaseTrack-inspired + H2M palette
NAVY = "#071E36"
NAVY_2 = "#0C2B4A"
BLUE = "#0B5EA8"
CYAN = "#00B8F0"
CYAN_LIGHT = "#DDF6FF"
WHITE = "#FFFFFF"
BG = "#F5F8FC"
TEXT = "#10233F"
MUTED = "#66758A"
BORDER = "#DFE7F0"
RED = "#E53935"
ORANGE = "#FF7A00"
GREEN = "#12A866"
LIGHT_RED = "#FFF0EF"
LIGHT_ORANGE = "#FFF5E8"
LIGHT_GREEN = "#EAF8F1"

def inject_css():
    st.markdown(f"""
    <style>
    .stApp {{ background:{BG}; color:{TEXT}; }}
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg,{NAVY} 0%, {NAVY_2} 100%);
        border-right: 1px solid rgba(255,255,255,.08);
    }}
    [data-testid="stSidebar"] * {{ color: #F6FAFF; }}
    [data-testid="stSidebar"] .stRadio label {{
        padding: .55rem .65rem; border-radius: 8px; margin-bottom:.25rem;
    }}
    [data-testid="stSidebar"] .stRadio label:hover {{
        background: rgba(0,184,240,.12);
    }}
    .block-container {{
        padding-top: 1.1rem; padding-bottom: 2rem; max-width: 1700px;
    }}
    h1,h2,h3 {{ color:{TEXT}; }}
    .eyebrow {{
        color:{BLUE}; font-size:.72rem; font-weight:800; letter-spacing:.05em;
        text-transform:uppercase; margin-bottom:.15rem;
    }}
    .page-title {{ font-size:2rem; font-weight:850; line-height:1.05; color:{TEXT}; }}
    .page-subtitle {{ color:{MUTED}; margin-top:.2rem; margin-bottom:1rem; }}
    .card {{
        background:{WHITE}; border:1px solid {BORDER}; border-radius:12px;
        padding:14px 16px; box-shadow:0 1px 2px rgba(15,35,60,.03);
    }}
    .kpi-label {{ font-size:.77rem; color:{MUTED}; font-weight:700; }}
    .kpi-value {{ font-size:1.55rem; color:{TEXT}; font-weight:850; margin:.2rem 0; }}
    .delta {{ font-size:.82rem; font-weight:800; }}
    .section {{
        background:{WHITE}; border:1px solid {BORDER}; border-radius:12px;
        padding:15px 16px; box-shadow:0 1px 2px rgba(15,35,60,.03);
        margin-bottom:.7rem;
    }}
    .section-title {{font-weight:850; color:{TEXT}; font-size:1.05rem; margin-bottom:.65rem;}}
    .status-pill {{
        display:inline-block; padding:3px 8px; border-radius:999px;
        font-size:.72rem; font-weight:800;
    }}
    .agent-box {{
        background:linear-gradient(135deg,#E9F5FF 0%,#F4FAFF 100%);
        border:1px solid #CDE7FB; border-radius:12px; padding:16px;
    }}
    .small-muted {{font-size:.78rem; color:{MUTED};}}
    .metric-grid {{display:grid; grid-template-columns:repeat(3,1fr); gap:.55rem;}}
    .metric-mini {{
        background:{WHITE}; border:1px solid {BORDER}; border-radius:9px; padding:10px 12px;
    }}
    .metric-mini .v {{font-size:1.05rem;font-weight:850;}}
    .metric-mini .l {{font-size:.7rem;color:{MUTED};font-weight:700;}}
    div[data-testid="stDataFrame"] {{ border-radius:10px; overflow:hidden; }}
    </style>
    """, unsafe_allow_html=True)

def status_color(delta):
    # User rule interpreted as:
    # red < -10%; orange from -10% to -1%; green >= 0.
    if delta < -0.10:
        return RED
    if delta < 0:
        return ORANGE
    return GREEN

def status_name(delta):
    if delta < -0.10:
        return "Crítico"
    if delta < 0:
        return "Atenção"
    return "Em linha"

def card_html(label, value, delta, delta_txt):
    c = status_color(delta)
    arrow = "↑" if delta >= 0 else "↓"
    return f"""
    <div class="card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      <div class="delta" style="color:{c}">{arrow} {delta_txt}</div>
    </div>
    """

def page_header(title, subtitle):
    st.markdown('<div class="eyebrow">EXECUÇÃO HOJE. COMPETITIVIDADE AMANHÃ.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)
