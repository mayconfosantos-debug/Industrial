
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from io import BytesIO
import unicodedata
import base64
from urllib.parse import quote

import industrial_data_layer as idl
import analytics_engine as ae

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

st.set_page_config(
    page_title="Industrial Performance | H2M",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# THEME
# ============================================================
NAVY = "#071C31"
NAVY_2 = "#0A2E4E"
BLUE = "#0B5FA5"
CYAN = "#00B7E8"
TEXT = "#10233F"
MUTED = "#6E7C90"
BG = "#F5F8FC"
WHITE = "#FFFFFF"
BORDER = "#DDE6EF"
RED = "#E53B36"
ORANGE = "#F47B20"
GREEN = "#12A66A"
SOFT_GREEN = "#EAF8F2"
SOFT_ORANGE = "#FFF5E9"
SOFT_RED = "#FFF0EF"

st.markdown(f"""
<style>
#MainMenu {{visibility:hidden;}}
footer {{visibility:hidden;}}
header[data-testid="stHeader"] {{height:40px;background:transparent;}}
[data-testid="stToolbar"] {{right:1rem;}}

.stApp {{
    background:{BG};
    color:{TEXT};
}}
.block-container {{
    max-width: 1640px;
    padding: .45rem 1.25rem 2rem 1.25rem;
}}

[data-testid="stSidebar"] {{
    background:linear-gradient(180deg,{NAVY} 0%,{NAVY_2} 100%);
    border-right:0;
    width:280px !important;
}}
[data-testid="stSidebar"] > div:first-child {{width:280px !important;}}
[data-testid="stSidebar"] .block-container {{padding:1rem .8rem 1rem .8rem;}}

[data-testid="stSidebar"] .stButton>button {{
    width:100%;
    min-height:38px;
    justify-content:flex-start !important;
    text-align:left !important;
    padding:.45rem .75rem;
    border:0;
    border-radius:8px;
    background:transparent;
    color:#D8E4EE;
    box-shadow:none;
    font-size:.78rem;
    font-weight:650;
}}
[data-testid="stSidebar"] .stButton>button p {{
    width:100%;
    margin:0;
    text-align:left !important;
}}
[data-testid="stSidebar"] .stButton>button:hover {{
    background:rgba(0,183,232,.10);
    color:white;
}}
[data-testid="stSidebar"] .stButton>button[kind="primary"] {{
    background:rgba(11,95,165,.42);
    color:white;
    border-left:3px solid {CYAN};
}}

.brand-title {{
    color:white;
    font-weight:850;
    font-size:.84rem;
    line-height:1.1;
}}
.brand-sub {{
    color:#A6BBCB;
    font-size:.62rem;
    margin-top:2px;
}}
.menu-group {{
    color:#77DDF8;
    font-size:.54rem;
    letter-spacing:.11em;
    font-weight:850;
    margin:14px 8px 6px;
}}
.sidebar-footer {{
    margin-top:16px;
    padding:10px 8px 0;
    color:#BFD0DD;
    font-size:.66rem;
    line-height:1.45;
}}
.sidebar-footer small {{
    color:#77E1FF;
    font-size:.53rem;
    letter-spacing:.08em;
}}

.eyebrow {{
    color:{BLUE};
    font-size:.59rem;
    font-weight:850;
    letter-spacing:.095em;
    text-transform:uppercase;
}}
.page-title {{
    font-size:1.76rem;
    line-height:1.03;
    font-weight:860;
    letter-spacing:-.035em;
    color:{TEXT};
    margin:.06rem 0 0 0;
}}
.page-subtitle {{
    font-size:.80rem;
    color:{MUTED};
    margin:.22rem 0 .9rem 0;
}}
.data-badge {{
    display:inline-block;
    border-radius:999px;
    padding:4px 9px;
    font-size:.59rem;
    font-weight:800;
    border:1px solid #D6E3ED;
    background:#FBFCFE;
    color:#476176;
}}

.kpi-card {{
    height:104px;
    background:{WHITE};
    border:1px solid {BORDER};
    border-radius:12px;
    padding:12px 14px;
    box-shadow:0 3px 12px rgba(10,35,60,.03);
    overflow:hidden;
}}
.kpi-label {{
    color:{MUTED};
    font-size:.64rem;
    font-weight:760;
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
}}
.kpi-value {{
    color:{TEXT};
    font-size:1.38rem;
    line-height:1.08;
    font-weight:860;
    letter-spacing:-.034em;
    margin:.34rem 0 .18rem;
    white-space:nowrap;
}}
.kpi-delta {{
    font-size:.66rem;
    font-weight:820;
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
}}
.dot {{
    display:inline-block;
    width:7px;
    height:7px;
    margin-right:5px;
    border-radius:50%;
}}

.panel-title {{
    font-size:.90rem;
    font-weight:850;
    color:{TEXT};
    margin-bottom:2px;
}}
.panel-sub {{
    font-size:.60rem;
    color:{MUTED};
    margin-bottom:8px;
}}

.kpi-table {{
    width:100%;
    table-layout:fixed;
    border-collapse:collapse;
    font-size:.66rem;
}}
.kpi-table th {{
    color:{MUTED};
    font-size:.54rem;
    letter-spacing:.04em;
    text-transform:uppercase;
    text-align:left;
    padding:6px 4px;
    border-bottom:1px solid {BORDER};
}}
.kpi-table td {{
    color:{TEXT};
    padding:7px 4px;
    border-bottom:1px solid #EFF3F7;
    vertical-align:middle;
    overflow:hidden;
    text-overflow:ellipsis;
}}
.kpi-table td:first-child {{font-weight:780;}}

.alert {{
    display:grid;
    grid-template-columns:22px 1fr;
    gap:8px;
    padding:7px 0;
    border-bottom:1px solid #EEF2F6;
}}
.alert-icon {{
    width:22px;
    height:22px;
    display:flex;
    align-items:center;
    justify-content:center;
    border-radius:50%;
    color:white;
    font-size:.63rem;
    font-weight:850;
}}
.alert-title {{
    color:{TEXT};
    font-size:.65rem;
    font-weight:820;
    line-height:1.2;
}}
.alert-sub {{
    color:{MUTED};
    font-size:.57rem;
    line-height:1.2;
    margin-top:2px;
}}

.agent-strip {{
    display:grid;
    grid-template-columns:1.35fr .85fr;
    gap:14px;
    background:linear-gradient(135deg,#EAF6FE 0%,#F9FCFF 100%);
    border:1px solid #CDE6F8;
    border-radius:12px;
    padding:13px 15px;
}}
.agent-title {{font-size:.79rem;font-weight:850;color:{TEXT};}}
.agent-copy {{font-size:.66rem;line-height:1.45;color:#34465C;margin-top:4px;}}

.priority {{
    display:inline-block;
    padding:3px 7px;
    border-radius:999px;
    font-size:.56rem;
    font-weight:850;
}}

.scenario-card {{
    background:#FBFCFE;
    border:1px solid {BORDER};
    border-radius:10px;
    padding:11px 12px;
    min-height:84px;
}}
.scenario-label {{
    color:{MUTED};
    font-size:.59rem;
    font-weight:760;
}}
.scenario-value {{
    color:{TEXT};
    font-size:1.18rem;
    font-weight:850;
    margin-top:5px;
}}
.scenario-delta {{
    font-size:.61rem;
    color:{GREEN};
    font-weight:820;
    margin-top:2px;
}}

.small {{font-size:.59rem;color:{MUTED};}}

.stSelectbox [data-baseweb="select"] > div {{
    min-height:36px;
    border-radius:8px;
    background:#FBFCFE;
}}
.stButton>button, .stDownloadButton>button, .stFormSubmitButton>button {{
    border-radius:8px;
    min-height:36px;
    font-weight:760;
}}
div[data-testid="stMetric"] {{
    background:white;
    border:1px solid {BORDER};
    border-radius:12px;
    padding:10px 12px;
}}
div[data-testid="stDataFrame"] {{
    border:1px solid {BORDER};
    border-radius:10px;
    overflow:hidden;
}}
.stTabs [data-baseweb="tab-list"] {{gap:4px;}}
.stTabs [data-baseweb="tab"] {{
    height:36px;
    border-radius:8px;
    padding:0 12px;
    font-size:.70rem;
    font-weight:750;
}}
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background:white;
    border:1px solid {BORDER} !important;
    border-radius:12px;
    padding:12px 14px;
    box-shadow:0 3px 12px rgba(10,35,60,.03);
}}

/* v0.6.1 - front-end refinement */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    min-width:0;
}}
div[data-testid="stVerticalBlockBorderWrapper"] > div {{
    min-width:0;
}}
div[data-testid="stDataFrame"] {{
    width:100%;
}}
[data-testid="stMetric"] label {{
    min-height:18px;
}}
[data-testid="stMetricValue"] {{
    white-space:nowrap;
}}
.email-note {{
    font-size:.62rem;
    color:#6E7C90;
    line-height:1.45;
}}
.report-note {{
    border-left:3px solid #00B7E8;
    padding:8px 10px;
    background:#F7FCFF;
    border-radius:6px;
    color:#34465C;
    font-size:.65rem;
}}


/* =========================================================
   v0.6.2 — FRONT-END PREMIUM
   ========================================================= */
.block-container {{
    max-width: 1540px;
    padding: .55rem 1.35rem 2.25rem 1.35rem;
}}
[data-testid="stSidebar"] {{
    width:258px !important;
}}
[data-testid="stSidebar"] > div:first-child {{
    width:258px !important;
}}
[data-testid="stSidebar"] .block-container {{
    padding: .9rem .72rem 1rem .72rem;
}}
[data-testid="stHorizontalBlock"] {{
    align-items: stretch;
}}
[data-testid="stHorizontalBlock"] > div {{
    min-width:0;
}}
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background:#FFFFFF;
    border:1px solid #DFE7EF !important;
    border-radius:14px;
    box-shadow:0 4px 16px rgba(10,35,60,.035);
    overflow:hidden;
}}
div[data-testid="stVerticalBlockBorderWrapper"] > div {{
    min-width:0;
}}
div[data-testid="stMetric"] {{
    height:104px;
    display:flex;
    flex-direction:column;
    justify-content:center;
    background:#FFFFFF;
    border:1px solid #DFE7EF;
    border-radius:12px;
    box-shadow:0 3px 12px rgba(10,35,60,.03);
}}
div[data-testid="stMetricValue"] {{
    font-size:1.34rem;
    line-height:1.05;
    color:#10233F;
}}
div[data-testid="stDataFrame"] {{
    border:1px solid #E3EAF1;
    border-radius:10px;
    overflow:hidden;
}}
[data-testid="stDataFrame"] [role="columnheader"] {{
    font-weight:700;
}}
.stTabs [data-baseweb="tab-list"] {{
    background:#F4F7FA;
    border:1px solid #E1E8EF;
    border-radius:10px;
    padding:3px;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius:7px;
}}
.stTabs [aria-selected="true"] {{
    background:white !important;
    box-shadow:0 1px 4px rgba(10,35,60,.08);
}}
[data-baseweb="select"] > div {{
    border-color:#DCE5ED !important;
}}
.stSlider [data-baseweb="slider"] {{
    padding-top: .2rem;
}}
.lever-shell {{
    background:linear-gradient(180deg,#FFFFFF 0%,#FAFCFE 100%);
    border:1px solid #DDE6EF;
    border-radius:14px;
    padding:14px 15px;
    min-height:96px;
}}
.lever-kicker {{
    font-size:.55rem;
    font-weight:850;
    letter-spacing:.08em;
    color:#0B5FA5;
    text-transform:uppercase;
}}
.lever-title {{
    font-size:.78rem;
    font-weight:850;
    color:#10233F;
    margin-top:3px;
}}
.lever-meta {{
    font-size:.58rem;
    color:#6E7C90;
    margin-top:4px;
    line-height:1.35;
}}
.sim-header {{
    display:flex;
    align-items:flex-start;
    justify-content:space-between;
    gap:12px;
    margin-bottom:5px;
}}
.sim-header-title {{
    font-size:1rem;
    font-weight:850;
    color:#10233F;
}}
.sim-header-sub {{
    font-size:.63rem;
    color:#6E7C90;
    margin-top:3px;
}}
.sim-scope-chip {{
    display:inline-block;
    background:#EAF6FE;
    color:#0B5FA5;
    border:1px solid #CDE6F8;
    padding:4px 8px;
    border-radius:999px;
    font-size:.55rem;
    font-weight:850;
}}
.sim-card {{
    background:#FFFFFF;
    border:1px solid #DFE7EF;
    border-radius:12px;
    padding:12px 13px;
    min-height:92px;
}}
.sim-card-label {{
    color:#6E7C90;
    font-size:.58rem;
    font-weight:760;
}}
.sim-card-value {{
    color:#10233F;
    font-size:1.20rem;
    font-weight:850;
    margin-top:5px;
    white-space:nowrap;
}}
.sim-card-delta {{
    font-size:.59rem;
    font-weight:800;
    margin-top:3px;
}}
.sim-mini {{
    font-size:.58rem;
    color:#6E7C90;
    line-height:1.4;
}}
.conf-high {{color:#12805C;font-weight:800;}}
.conf-mid {{color:#C76A15;font-weight:800;}}
.conf-low {{color:#7C8795;font-weight:800;}}
.frontend-note {{
    background:#F7FBFE;
    border-left:3px solid #00B7E8;
    border-radius:8px;
    padding:9px 11px;
    color:#40576B;
    font-size:.62rem;
    line-height:1.45;
}}


/* v0.6.2.2 — Sidebar menu fully left-aligned */
[data-testid="stSidebar"] .stButton {{
    width:100%;
}}
[data-testid="stSidebar"] .stButton > button {{
    width:100% !important;
    display:flex !important;
    justify-content:flex-start !important;
    align-items:center !important;
    text-align:left !important;
    padding-left:.85rem !important;
    padding-right:.65rem !important;
}}
[data-testid="stSidebar"] .stButton > button > div {{
    width:100% !important;
    display:flex !important;
    justify-content:flex-start !important;
    text-align:left !important;
}}
[data-testid="stSidebar"] .stButton > button p,
[data-testid="stSidebar"] .stButton > button span {{
    width:100% !important;
    text-align:left !important;
    justify-content:flex-start !important;
    margin:0 !important;
}}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
    text-align:left !important;
}}

</style>
""", unsafe_allow_html=True)

# ============================================================
# HELPERS
# ============================================================
def norm(x):
    x = str(x).strip().lower()
    x = ''.join(c for c in unicodedata.normalize("NFKD", x) if not unicodedata.combining(c))
    return ''.join(ch if ch.isalnum() else '_' for ch in x).strip('_')

def nseries(s):
    return pd.to_numeric(s, errors="coerce").fillna(0)

def safe_div(a,b):
    return float(a/b) if b not in (0,0.0) and pd.notna(b) else 0.0

def fmt_pct(x):
    return f"{x:.1%}".replace(".",",")

def fmt_money(x, decimals=1):
    if abs(x) >= 1_000_000:
        return f"R$ {x/1_000_000:.{decimals}f} mi".replace(".",",")
    if abs(x) >= 1_000:
        return f"R$ {x/1_000:.{decimals}f} mil".replace(".",",")
    return f"R$ {x:,.0f}".replace(",", ".")

def score_color(score):
    if score < -0.10:
        return RED
    if score < 0:
        return ORANGE
    return GREEN

SHEETS = {
    "producao":["producao","produção","production"],
    "qualidade":["qualidade","quality"],
    "manutencao":["manutencao","manutenção","maintenance"],
    "pessoas":["pessoas","people","mao_de_obra","mão de obra"],
    "custos":["custos","costs","financeiro"],
    "metas":["metas","targets","goals"],
    "padroes_produto":["padroes_produto","padrões_produto","padroes","product_standards","standards"],
    "parametros_diagnostico":["parametros_diagnostico","parametros_diagnóstico","diagnostico_parametros","diagnostic_parameters"],
    "responsaveis":["responsaveis","responsáveis","owners","responsibles"],
    "alavancas_simulador":["alavancas_simulador","alavancas_simulação","simulator_levers"],
    "premissas_simulador":["premissas_simulador","premissas_simulação","simulator_assumptions"]
}
ALIASES = {
    "producao":{
        "data":["data","date"],"fabrica":["fabrica","planta","site","factory"],
        "linha":["linha","line"],"produto":["produto","sku","product"],
        "planejado":["planejado","plano","meta_producao","planned"],
        "realizado":["realizado","producao_real","qtd_produzida","volume","actual"],
        "horas_disponiveis":["horas_disponiveis","horas_planejadas","available_hours"],
        "horas_paradas":["horas_paradas","paradas_horas","downtime_hours"],
        "velocidade_real":["velocidade_real","performance_real","actual_speed"],
        "velocidade_nominal":["velocidade_nominal","velocidade_padrao","nominal_speed"]
    },
    "qualidade":{
        "data":["data","date"],"linha":["linha","line"],"produto":["produto","sku","product"],
        "produzido":["produzido","producao","produced"],"aprovado":["aprovado","bons","good_units"],
        "refugo":["refugo","scrap"],"retrabalho":["retrabalho","rework"]
    },
    "manutencao":{
        "data":["data","date"],"linha":["linha","line"],"maquina":["maquina","equipamento","machine"],
        "tipo_parada":["tipo_parada","tipo","downtime_type"],"duracao_horas":["duracao_horas","horas","duracao","duration_hours"],
        "causa":["causa","motivo","cause"]
    },
    "pessoas":{
        "data":["data","date"],"linha":["linha","line"],"turno":["turno","shift"],
        "operadores":["operadores","headcount","pessoas"],"horas_normais":["horas_normais","regular_hours"],
        "horas_extras":["horas_extras","overtime","overtime_hours"]
    },
    "custos":{
        "data":["data","date"],"linha":["linha","line"],"produto":["produto","sku","product"],
        "custo_mp":["custo_mp","materia_prima","raw_material_cost"],
        "custo_mod":["custo_mod","mao_de_obra_direta","direct_labor_cost"],
        "custo_energia":["custo_energia","energia","energy_cost"],
        "custo_manutencao":["custo_manutencao","manutencao","maintenance_cost"],
        "custo_fixo":["custo_fixo","fixed_cost","custos_fixos"],
        "receita":["receita","faturamento","revenue"]
    },
    "metas":{
        "indicador":["indicador","kpi","metric"],"meta":["meta","target","goal"],
        "direcao":["direcao","direção","direction"],"unidade":["unidade","unit"],
        "obrigatoria":["obrigatoria","obrigatória","mandatory"],
        "referencia_financeira":["referencia_financeira","referência_financeira","financial_reference"]
    },
    "padroes_produto":{
        "produto":["produto","sku","product"],"familia":["familia","família","family"],
        "linha_padrao":["linha_padrao","linha_padrão","standard_line"],
        "tempo_ciclo_padrao_min_un":["tempo_ciclo_padrao_min_un","tempo_ciclo_padrão_min_un","standard_cycle_min_unit"],
        "operadores_padrao":["operadores_padrao","operadores_padrão","standard_operators"],
        "hh_padrao_un":["hh_padrao_un","hh_padrão_un","standard_labor_hours_unit"],
        "tempo_setup_padrao_min_lote":["tempo_setup_padrao_min_lote","tempo_setup_padrão_min_lote","standard_setup_min_batch"],
        "lote_padrao_un":["lote_padrao_un","lote_padrão_un","standard_batch"],
        "mp_padrao_kg_un":["mp_padrao_kg_un","mp_padrão_kg_un","standard_material_kg_unit"],
        "energia_padrao_kwh_un":["energia_padrao_kwh_un","energia_padrão_kwh_un","standard_energy_kwh_unit"],
        "custo_hh_mod":["custo_hh_mod","custo_hh_mod_r","labor_hour_cost"],
        "preco_liquido_padrao":["preco_liquido_padrao","preço_liquido_padrão","standard_net_price"],
        "custo_variavel_padrao":["custo_variavel_padrao","custo_variável_padrão","standard_variable_cost"],
        "margem_contrib_padrao":["margem_contrib_padrao","margem_contrib_padrão","standard_contribution_margin"]
    },
    "parametros_diagnostico":{
        "alavanca":["alavanca","lever"],
        "esforco_1a5":["esforco_1a5","esforço_1a5","effort"],
        "horizonte_dias":["horizonte_dias","horizon_days"],
        "responsavel_tipico":["responsavel_tipico","responsável_típico","typical_owner"],
        "tipo_impacto":["tipo_impacto","impact_type"],
        "peso_minimo_gestao":["peso_minimo_gestao","peso_mínimo_gestão","minimum_management_weight"]
    },
    "responsaveis":{
        "responsavel":["responsavel","responsável","name"],
        "cargo_funcao":["cargo_funcao","cargo_função","role"],
        "area":["area","área"],
        "email":["email","e_mail","e-mail"],
        "observacao":["observacao","observação","notes"]
    },
    "alavancas_simulador":{
        "grupo":["grupo","group"],
        "alavanca":["alavanca","lever"],
        "formato":["formato","format"],
        "atual_exemplo":["atual_exemplo","current_example"],
        "meta_exemplo":["meta_exemplo","target_example"],
        "unidade":["unidade","unit"],
        "impacto_principal":["impacto_principal","primary_impact"],
        "impacto_secundario":["impacto_secundario","secondary_impact"],
        "dependencia":["dependencia","dependência","dependency"],
        "confianca":["confianca","confiança","confidence"],
        "ativa":["ativa","active"],
        "observacao":["observacao","observação","notes"]
    },
    "premissas_simulador":{
        "chave":["chave","key"],
        "valor":["valor","value"],
        "unidade":["unidade","unit"],
        "uso_no_motor":["uso_no_motor","engine_use"],
        "observacao":["observacao","observação","notes"]
    }
}

def canonical_sheet(name):
    n = norm(name)
    for canon, aliases in SHEETS.items():
        if n in [norm(a) for a in aliases]:
            return canon
    return None

def rename_cols(df, sheet):
    amap={}
    for canon, aliases in ALIASES[sheet].items():
        for a in aliases + [canon]:
            amap[norm(a)] = canon
    return df.rename(columns={c:amap[norm(c)] for c in df.columns if norm(c) in amap})

def parse_excel(raw):
    xls = pd.ExcelFile(BytesIO(raw))
    data={}
    for sh in xls.sheet_names:
        canon=canonical_sheet(sh)
        if canon:
            df=pd.read_excel(BytesIO(raw),sheet_name=sh)
            data[canon]=rename_cols(df,canon)

    required={
        "producao":["data","linha","produto","planejado","realizado","horas_disponiveis","horas_paradas","velocidade_real","velocidade_nominal"],
        "qualidade":["data","linha","produto","produzido","aprovado","refugo"],
        "manutencao":["data","linha","maquina","duracao_horas","causa"],
        "pessoas":["data","linha","horas_normais","horas_extras"],
        "custos":["data","linha","custo_mp","custo_mod","custo_energia","custo_manutencao","receita"],
        "metas":["indicador","meta"],
        "padroes_produto":["produto"]
    }
    issues=[]
    for sh, cols in required.items():
        if sh not in data:
            issues.append(f"Aba ausente: {sh.title().replace('_',' ')}")
        else:
            miss=[c for c in cols if c not in data[sh].columns]
            if miss:
                issues.append(f"{sh.title().replace('_',' ')}: faltam {', '.join(miss)}")

    if "padroes_produto" in data:
        pp=data["padroes_produto"]
        has_hh="hh_padrao_un" in pp.columns
        has_cycle=("tempo_ciclo_padrao_min_un" in pp.columns and "operadores_padrao" in pp.columns)
        if not has_hh and not has_cycle:
            issues.append("Padroes Produto: informar HH_Padrao_un ou Tempo_Ciclo_Padrao_min_un + Operadores_Padrao")

    if issues:
        return None, issues

    for _,df in data.items():
        if "data" in df.columns:
            df["data"]=pd.to_datetime(df["data"],errors="coerce")
    return data, []

def target_from(data, names, default=np.nan):
    m=data.get("metas")
    if m is None or m.empty or "indicador" not in m or "meta" not in m:
        return default
    mm=m.copy()
    mm["_i"]=mm["indicador"].map(norm)
    hit=mm[mm["_i"].isin([norm(x) for x in names])]
    if hit.empty:
        return default
    v=pd.to_numeric(hit.iloc[0]["meta"],errors="coerce")
    return float(v) if pd.notna(v) else default

def _status_points(score, has_target=True, has_data=True):
    # KPI sem meta ou sem dado não é ignorado: penaliza governança.
    if not has_target or not has_data or score is None or pd.isna(score):
        return 25.0
    if score >= 0:
        return 100.0
    if score >= -0.01:
        return 90.0
    if score >= -0.10:
        # -1% => 90 ; -10% => 55
        return 90 - ((abs(score)-0.01)/0.09)*35
    # abaixo de -10% cai rapidamente
    return max(0.0, 55 - (abs(score)-0.10)*180)

def _effort_parameters(data):
    defaults={
        "Disponibilidade":(4,60,"Manutenção"),
        "Performance":(3,45,"Produção / Processos"),
        "Setup":(2,30,"Engenharia de Processos"),
        "Refugo":(3,45,"Qualidade / Processos"),
        "Eficiência MOD":(3,45,"Produção / Engenharia"),
        "Horas extras":(2,30,"Produção"),
        "Consumo MP":(3,45,"Processos / Suprimentos"),
        "Energia":(3,60,"Utilidades / Engenharia"),
        "Custo fixo":(4,90,"Diretor Industrial / CFO"),
        "OTIF":(3,45,"PCP / Logística"),
    }
    prm=data.get("parametros_diagnostico")
    if prm is None or prm.empty or "alavanca" not in prm.columns:
        return defaults
    out=defaults.copy()
    for _,r in prm.iterrows():
        key=str(r.get("alavanca","")).strip()
        if not key:
            continue
        effort=pd.to_numeric(r.get("esforco_1a5",np.nan),errors="coerce")
        horizon=pd.to_numeric(r.get("horizonte_dias",np.nan),errors="coerce")
        owner=str(r.get("responsavel_tipico","")).strip()
        old=out.get(key,(3,45,"Gestão"))
        out[key]=(int(effort) if pd.notna(effort) else old[0],
                  int(horizon) if pd.notna(horizon) else old[1],
                  owner if owner else old[2])
    return out

def calculate_real(data):
    p=data["producao"].copy()
    q=data["qualidade"].copy()
    m=data["manutencao"].copy()
    pe=data["pessoas"].copy()
    c=data["custos"].copy()
    dg=data.get("dre_gerencial",pd.DataFrame()).copy()
    std=data.get("padroes_produto",pd.DataFrame()).copy()

    for col in ["planejado","realizado","horas_disponiveis","horas_paradas","velocidade_real","velocidade_nominal"]:
        p[col]=nseries(p[col])
    for col in ["produzido","aprovado","refugo"]:
        q[col]=nseries(q[col])
    if "retrabalho" in q.columns:
        q["retrabalho"]=nseries(q["retrabalho"])
    m["duracao_horas"]=nseries(m["duracao_horas"])
    for col in ["horas_normais","horas_extras"]:
        pe[col]=nseries(pe[col])
    for col in ["custo_mp","custo_mod","custo_energia","custo_manutencao","receita"]:
        if col not in c.columns:
            c[col]=0
        c[col]=nseries(c[col])
    for col in ["custo_frete","ggf_outros","custo_fixo"]:
        c[col]=nseries(c[col]) if col in c.columns else 0

    if dg is not None and not dg.empty:
        for col in [
            "receita_bruta","impostos_deducoes","receita_liquida","insumos_mp","mod",
            "ggf_frete","ggf_energia","ggf_manutencao","ggf_contratos_servicos","ggf_outros",
            "custos_fixos_industriais","desp_administrativas","desp_comerciais",
            "desp_logisticas","outros_opex","volume_vendido","consumo_mp_kg",
            "preco_medio_mp_kg","consumo_energia_kwh","estoque_dias",
            "prazo_fornecedor_dias","prazo_cliente_dias"
        ]:
            dg[col]=nseries(dg[col]) if col in dg.columns else 0

    # ---------------- Basic operation ----------------
    planned=p["planejado"].sum()
    actual=p["realizado"].sum()
    attainment=safe_div(actual,planned)

    availability=max(0,min(1,1-safe_div(p["horas_paradas"].sum(),p["horas_disponiveis"].sum())))
    pr=(p["velocidade_real"]/p["velocidade_nominal"].replace(0,np.nan)).replace([np.inf,-np.inf],np.nan)
    performance=float(pr.mean()) if pr.notna().any() else 0
    performance=max(0,min(1.2,performance))
    quality=max(0,min(1,safe_div(q["aprovado"].sum(),q["produzido"].sum())))
    oee=availability*min(performance,1)*quality
    scrap=safe_div(q["refugo"].sum(),q["produzido"].sum())
    rework_rate=safe_div(q["retrabalho"].sum(),q["produzido"].sum()) if "retrabalho" in q.columns else np.nan

    # ---------------- Finance / DRE Gerencial ----------------
    if dg is not None and not dg.empty:
        revenue_gross=float(dg["receita_bruta"].sum())
        deductions=float(dg["impostos_deducoes"].sum())
        revenue=float(dg["receita_liquida"].sum())
        if revenue == 0 and revenue_gross != 0:
            revenue=revenue_gross-deductions
        if revenue_gross == 0:
            revenue_gross=revenue+deductions

        cost_mp=float(dg["insumos_mp"].sum())
        cost_mod=float(dg["mod"].sum())
        cost_freight=float(dg["ggf_frete"].sum())
        cost_energy=float(dg["ggf_energia"].sum())
        cost_maintenance=float(dg["ggf_manutencao"].sum())
        cost_contracts=float(dg["ggf_contratos_servicos"].sum())
        cost_ggf_other=float(dg["ggf_outros"].sum())
        fixed_industrial=float(dg["custos_fixos_industriais"].sum())
        exp_admin=float(dg["desp_administrativas"].sum())
        exp_commercial=float(dg["desp_comerciais"].sum())
        exp_logistics=float(dg["desp_logisticas"].sum())
        other_opex=float(dg["outros_opex"].sum())

        sold_volume=float(dg["volume_vendido"].sum()) if float(dg["volume_vendido"].sum())>0 else float(actual)
        material_consumption_kg=float(dg["consumo_mp_kg"].sum())
        mp_price_series=dg["preco_medio_mp_kg"].replace(0,np.nan)
        weighted_mp_price=float(mp_price_series.mean()) if mp_price_series.notna().any() else np.nan
        energy_consumption_kwh=float(dg["consumo_energia_kwh"].sum())
        inv_series=dg["estoque_dias"].replace(0,np.nan)
        dpo_series=dg["prazo_fornecedor_dias"].replace(0,np.nan)
        dso_series=dg["prazo_cliente_dias"].replace(0,np.nan)
        inventory_days=float(inv_series.mean()) if inv_series.notna().any() else np.nan
        dpo_days=float(dpo_series.mean()) if dpo_series.notna().any() else np.nan
        dso_days=float(dso_series.mean()) if dso_series.notna().any() else np.nan
    else:
        revenue=float(c["receita"].sum())
        revenue_gross=revenue
        deductions=0.0
        cost_mp=float(c["custo_mp"].sum())
        cost_mod=float(c["custo_mod"].sum())
        cost_freight=float(c["custo_frete"].sum()) if "custo_frete" in c.columns else 0.0
        cost_energy=float(c["custo_energia"].sum())
        cost_maintenance=float(c["custo_manutencao"].sum())
        cost_contracts=0.0
        cost_ggf_other=float(c["ggf_outros"].sum()) if "ggf_outros" in c.columns else 0.0
        fixed_industrial=float(c["custo_fixo"].sum())
        exp_admin=0.0
        exp_commercial=0.0
        exp_logistics=0.0
        other_opex=0.0
        sold_volume=float(actual)
        material_consumption_kg=np.nan
        weighted_mp_price=np.nan
        energy_consumption_kwh=np.nan
        inventory_days=np.nan
        dpo_days=np.nan
        dso_days=np.nan

    ggf_total=cost_freight+cost_energy+cost_maintenance+cost_contracts+cost_ggf_other
    industrial_cost=cost_mp+cost_mod+ggf_total
    industrial_margin_value=revenue-industrial_cost
    industrial_margin=safe_div(industrial_margin_value,revenue)
    expenses_total=exp_admin+exp_commercial+exp_logistics+other_opex
    result_industrial=industrial_margin_value-fixed_industrial
    ebitda=result_industrial-expenses_total
    total_cost=industrial_cost+fixed_industrial+expenses_total

    contrib=industrial_margin_value
    margin_contrib=industrial_margin
    var_cost=industrial_cost
    fixed_cost=fixed_industrial+expenses_total
    cost_unit=safe_div(total_cost,actual)

    dre=pd.DataFrame({
        "Linha":[
            "Receita Bruta","(-) Impostos e deduções","Receita Líquida",
            "(-) Insumos / Matéria-prima","(-) MOD",
            "(-) GGF — Frete","(-) GGF — Energia","(-) GGF — Manutenção",
            "(-) GGF — Contratos e Serviços","(-) GGF — Outros",
            "Margem Industrial","(-) Custos Fixos Industriais","Resultado Industrial",
            "(-) Despesas Administrativas","(-) Despesas Comerciais",
            "(-) Despesas Logísticas","(-) Outros OPEX","EBITDA"
        ],
        "Realizado":[
            revenue_gross,-deductions,revenue,
            -cost_mp,-cost_mod,-cost_freight,-cost_energy,-cost_maintenance,
            -cost_contracts,-cost_ggf_other,industrial_margin_value,-fixed_industrial,result_industrial,
            -exp_admin,-exp_commercial,-exp_logistics,-other_opex,ebitda
        ]
    })

    overtime=pe["horas_extras"].sum()
    actual_hh=pe["horas_normais"].sum()+overtime
    productivity_raw=safe_div(actual,actual_hh)
    avg_headcount=np.nan
    if "operadores" in pe.columns:
        pe["operadores"]=nseries(pe["operadores"])
        if "data" in pe.columns:
            daily_hc=pe.groupby("data")["operadores"].sum()
            avg_headcount=float(daily_hc.mean()) if len(daily_hc) else np.nan
        else:
            avg_headcount=float(pe["operadores"].mean()) if len(pe) else np.nan

    # ---------------- Mix linearization / labor efficiency ----------------
    labor_eff=np.nan
    std_hours_earned=np.nan
    standards_missing=[]
    labor_gap_cost=0.0
    if std is not None and not std.empty and "produto" in std.columns:
        if "hh_padrao_un" not in std.columns:
            std["hh_padrao_un"]=np.nan
        std["hh_padrao_un"]=pd.to_numeric(std["hh_padrao_un"],errors="coerce")
        if "tempo_ciclo_padrao_min_un" in std.columns and "operadores_padrao" in std.columns:
            cyc=pd.to_numeric(std["tempo_ciclo_padrao_min_un"],errors="coerce")
            ops=pd.to_numeric(std["operadores_padrao"],errors="coerce")
            calc_hh=cyc/60*ops
            std["hh_padrao_un"]=std["hh_padrao_un"].fillna(calc_hh)
        good=q.groupby("produto",as_index=False)["aprovado"].sum()
        merge=good.merge(std[["produto","hh_padrao_un"]],on="produto",how="left")
        standards_missing=merge.loc[merge["hh_padrao_un"].isna(),"produto"].astype(str).tolist()
        if not merge.empty and len(standards_missing)==0:
            std_hours_earned=float((merge["aprovado"]*merge["hh_padrao_un"]).sum())
            labor_eff=safe_div(std_hours_earned,actual_hh)
            labor_rate=safe_div(c["custo_mod"].sum(),actual_hh)
            labor_gap_cost=max(0,actual_hh-std_hours_earned)*labor_rate

    # ---------------- Targets ----------------
    t_prod=target_from(data,["Atingimento Produção","Produção"],1.0)
    t_oee=target_from(data,["OEE"],0.78)
    t_avail=target_from(data,["Disponibilidade"],0.82)
    t_perf=target_from(data,["Performance"],0.97)
    t_quality=target_from(data,["Qualidade"],0.985)
    t_labor=target_from(data,["Eficiência MOD","Eficiencia MOD"],0.95)
    t_scrap=target_from(data,["Refugo","Taxa Refugo"],0.025)
    t_otif=target_from(data,["OTIF"],np.nan)
    t_cost=target_from(data,["Custo/unidade","Custo por unidade"],np.nan)
    t_overtime=target_from(data,["Horas extras"],np.nan)
    t_margin=target_from(data,["Margem","Margem Industrial","Margem Contribuição"],0.31)
    t_ebitda=target_from(data,["EBITDA Industrial","EBITDA"],np.nan)

    # ---------------- Trends / line view ----------------
    trend=p.groupby("data",as_index=False)[["planejado","realizado"]].sum().dropna().sort_values("data")
    if len(trend)>35:
        trend=trend.tail(35)

    rows=[]
    for line in sorted(p["linha"].astype(str).unique()):
        pp=p[p["linha"].astype(str)==line]
        qq=q[q["linha"].astype(str)==line]
        mm=m[m["linha"].astype(str)==line]
        av=max(0,min(1,1-safe_div(pp["horas_paradas"].sum(),pp["horas_disponiveis"].sum())))
        rr=(pp["velocidade_real"]/pp["velocidade_nominal"].replace(0,np.nan)).replace([np.inf,-np.inf],np.nan)
        pf=float(rr.mean()) if rr.notna().any() else 0
        qu=max(0,min(1,safe_div(qq["aprovado"].sum(),qq["produzido"].sum())))
        oo=av*min(pf,1)*qu
        rows.append({
            "Linha":line,"OEE":oo,"Disponibilidade":av,"Performance":pf,"Qualidade":qu,
            "Refugo":safe_div(qq["refugo"].sum(),qq["produzido"].sum()),
            "Gap Produção":pp["realizado"].sum()-pp["planejado"].sum(),
            "Paradas h":mm["duracao_horas"].sum()
        })
    line_perf=pd.DataFrame(rows)

    mttr_min=float(m["duracao_horas"].mean()*60) if len(m) else np.nan
    setup_avg_min=np.nan
    if "tipo_parada" in m.columns:
        setup_mask=m["tipo_parada"].astype(str).map(norm).str.contains("setup|troca|changeover",regex=True)
        if setup_mask.any():
            setup_avg_min=float(m.loc[setup_mask,"duracao_horas"].mean()*60)
    if pd.isna(setup_avg_min) and "causa" in m.columns:
        setup_mask=m["causa"].astype(str).map(norm).str.contains("setup|troca|changeover",regex=True)
        if setup_mask.any():
            setup_avg_min=float(m.loc[setup_mask,"duracao_horas"].mean()*60)

    if "tipo_parada" in m.columns:
        planned_mask=m["tipo_parada"].astype(str).map(norm).str.contains("setup|planejada|preventiva|planned",regex=True)
        unplanned_downtime_h=float(m.loc[~planned_mask,"duracao_horas"].sum())
    else:
        unplanned_downtime_h=float(m["duracao_horas"].sum())

    causes=m.groupby("causa",as_index=False)["duracao_horas"].sum().rename(columns={"causa":"Causa","duracao_horas":"Horas"})
    if not causes.empty:
        margin_unit=safe_div(contrib,actual)
        units_h=safe_div(actual,max(1,actual_hh))
        causes["Impacto R$ mil"]=causes["Horas"]*units_h*margin_unit/1000
        causes=causes.sort_values("Horas",ascending=False).head(8)

    # ---------------- Unique financial impact buckets (avoid double count) ----------------
    margin_unit=safe_div(contrib,max(1,actual))
    loss_prod=max(0,planned-actual)*margin_unit
    loss_scrap=q["refugo"].sum()*safe_div(total_cost,max(1,actual))
    labor_hour_rate=safe_div(cost_mod,max(actual_hh,1))
    overtime_premium_factor=sim_assumption("adicional_hora_extra",0.50)
    overtime_excess=max(0,overtime-(t_overtime if pd.notna(t_overtime) else 0)) if pd.notna(t_overtime) else overtime
    overtime_premium=overtime_excess*labor_hour_rate*overtime_premium_factor
    cost_gap=max(0,cost_unit-t_cost)*actual if pd.notna(t_cost) else max(0,total_cost*0.015)
    energy_gap=max(0,cost_energy*0.05)
    impacts=pd.DataFrame({
        "Impacto":["Gap de volume","Refugo","Eficiência MOD","Horas extras","Custo / consumo"],
        "R$":[loss_prod,loss_scrap,labor_gap_cost,overtime_premium,cost_gap]
    }).sort_values("R$",ascending=False)

    # ---------------- KPIs: raw units/h no longer used as consolidated productivity ----------------
    labor_has_data=pd.notna(labor_eff)
    labor_score=(safe_div(labor_eff,t_labor)-1) if labor_has_data and pd.notna(t_labor) else np.nan
    labor_mes=fmt_pct(labor_eff) if labor_has_data else "Padrão ausente"
    labor_delta=(f"{(labor_eff-t_labor)*100:+.1f} pp".replace(".",",")
                 if labor_has_data and pd.notna(t_labor) else "cadastro incompleto")

    kpis=[
        ("Produção",f"{actual:,.0f} un".replace(",","."),f"{planned:,.0f}".replace(",","."),attainment-1,f"{attainment-1:+.1%}".replace(".",","),"↓" if attainment<1 else "↑"),
        ("OEE",fmt_pct(oee),fmt_pct(t_oee),safe_div(oee,t_oee)-1,f"{(oee-t_oee)*100:+.1f} pp".replace(".",","),"↓" if oee<t_oee else "↑"),
        ("Eficiência MOD",labor_mes,fmt_pct(t_labor) if pd.notna(t_labor) else "Meta ausente",labor_score,labor_delta,"!" if not labor_has_data else ("↓" if labor_eff<t_labor else "↑")),
        ("Refugo",fmt_pct(scrap),fmt_pct(t_scrap),1-safe_div(scrap,t_scrap),f"{(scrap-t_scrap)*100:+.1f} pp".replace(".",","),"↑" if scrap>t_scrap else "↓"),
        ("OTIF","—",fmt_pct(t_otif) if pd.notna(t_otif) else "Meta ausente",np.nan,"sem dado","!"),
        ("Custo/unidade",fmt_money(cost_unit,2),fmt_money(t_cost,2) if pd.notna(t_cost) else "Meta ausente",(1-safe_div(cost_unit,t_cost)) if pd.notna(t_cost) else np.nan,(f"{safe_div(cost_unit,t_cost)-1:+.1%}".replace(".",",") if pd.notna(t_cost) else "sem meta"),"↑" if pd.notna(t_cost) and cost_unit>t_cost else "→"),
        ("Horas extras",f"{overtime:,.0f} h".replace(",","."),f"{t_overtime:,.0f} h".replace(",",".") if pd.notna(t_overtime) else "Meta ausente",(1-safe_div(overtime,t_overtime)) if pd.notna(t_overtime) else np.nan,(f"{safe_div(overtime,t_overtime)-1:+.1%}".replace(".",",") if pd.notna(t_overtime) else "sem meta"),"↑" if pd.notna(t_overtime) and overtime>t_overtime else "→"),
        ("Margem Industrial",fmt_pct(margin_contrib),fmt_pct(t_margin),safe_div(margin_contrib,t_margin)-1,f"{(margin_contrib-t_margin)*100:+.1f} pp".replace(".",","),"↓" if margin_contrib<t_margin else "↑"),
    ]

    margin_score=safe_div(margin_contrib,t_margin)-1
    cards=[
        ("Receita Líquida",fmt_money(revenue),attainment-1,f"{attainment-1:+.1%} vs. plano".replace(".",",")),
        ("Margem Industrial",fmt_pct(margin_contrib),margin_score,f"{(margin_contrib-t_margin)*100:+.1f} pp vs. meta".replace(".",",")),
        ("EBITDA Industrial",fmt_money(ebitda),(safe_div(ebitda,t_ebitda)-1) if pd.notna(t_ebitda) else margin_score,(f"{safe_div(ebitda,t_ebitda)-1:+.1%} vs. meta".replace(".",",") if pd.notna(t_ebitda) else "meta financeira")),
        ("Produção",f"{actual:,.0f} un".replace(",","."),attainment-1,f"{attainment-1:+.1%} vs. meta".replace(".",",")),
        ("OEE",fmt_pct(oee),safe_div(oee,t_oee)-1,f"{(oee-t_oee)*100:+.1f} pp vs. meta".replace(".",",")),
        ("Custo / un.",fmt_money(cost_unit,2),(1-safe_div(cost_unit,t_cost)) if pd.notna(t_cost) else np.nan,(f"{safe_div(cost_unit,t_cost)-1:+.1%} vs. meta".replace(".",",") if pd.notna(t_cost) else "meta não definida")),
    ]

    # ---------------- Health: all KPIs count; finance increases relevance weight ----------------
    financial_relevance={
        "Produção":loss_prod,
        "OEE":loss_prod*0.70,  # relevance signal, not additive impact
        "Eficiência MOD":labor_gap_cost,
        "Refugo":loss_scrap,
        "OTIF":revenue*0.01,
        "Custo/unidade":cost_gap,
        "Horas extras":overtime_premium,
        "Margem Industrial":max(0,(t_margin-margin_contrib)*revenue)
    }
    max_rel=max([v for v in financial_relevance.values() if pd.notna(v)] + [1])
    health_rows=[]
    for ind,mes,meta,score,delta,tend in kpis:
        has_target=("Meta ausente" not in str(meta))
        has_data=(mes not in ["—","Padrão ausente"])
        pts=_status_points(score,has_target,has_data)
        rel=max(0,financial_relevance.get(ind,0))
        weight=1.0 + 2.0*(rel/max_rel)  # all KPIs count; financial relevance can triple weight
        health_rows.append([ind,pts,weight,rel,has_target,has_data])
    health_df=pd.DataFrame(health_rows,columns=["KPI","Score","Peso","Relevancia_R$","Tem_Meta","Tem_Dado"])
    health_score=float(np.average(health_df["Score"],weights=health_df["Peso"]))

    financial_names=["Produção","Refugo","Custo/unidade","Horas extras","Margem Industrial","Eficiência MOD"]
    hfin=health_df[health_df["KPI"].isin(financial_names)]
    financial_health=float(np.average(hfin["Score"],weights=hfin["Peso"])) if not hfin.empty else health_score
    operational_names=["Produção","OEE","Eficiência MOD","Refugo","OTIF"]
    hop=health_df[health_df["KPI"].isin(operational_names)]
    operational_health=float(np.average(hop["Score"],weights=hop["Peso"])) if not hop.empty else health_score

    # ---------------- Diagnostic engine ----------------
    effort=_effort_parameters(data)
    worst_line=line_perf.sort_values("OEE").iloc[0] if not line_perf.empty else None
    top_cause=causes.iloc[0] if not causes.empty else None

    lever_impacts={
        "Disponibilidade":loss_prod*0.45,
        "Performance":loss_prod*0.25,
        "Setup":loss_prod*0.12,
        "Refugo":loss_scrap,
        "Eficiência MOD":labor_gap_cost,
        "Horas extras":overtime_premium,
        "Consumo MP":cost_gap*0.70,
        "Energia":energy_gap,
        "Custo fixo":max(0,fixed_cost*0.03),
        "OTIF":revenue*0.005
    }
    action_library={
        "Disponibilidade":"Plano de confiabilidade nos equipamentos críticos; revisar preventiva, sobressalentes e reincidências.",
        "Performance":"Atacar microparadas e perdas de velocidade; revisar padrão operacional e parâmetros de processo.",
        "Setup":"Aplicar SMED, preparação externa e sequenciamento por família para reduzir troca.",
        "Refugo":"Pareto por produto/causa; revisar parâmetros, matéria-prima, inspeção e estabilidade do processo.",
        "Eficiência MOD":"Rebalancear células/turnos usando HH padrão por produto; atacar esperas, movimentação e desequilíbrio.",
        "Horas extras":"Revisar dimensionamento, escala, restrições de capacidade e relação hora extra × volume incremental.",
        "Consumo MP":"Comparar consumo real versus padrão por produto; investigar rendimento, perdas e variação de processo.",
        "Energia":"Medir kWh por unidade equivalente e atacar equipamentos/processos fora do padrão.",
        "Custo fixo":"Revisar estrutura, contratos e capacidade ociosa; separar custo estrutural de custo necessário ao crescimento.",
        "OTIF":"Atacar aderência ao plano, disponibilidade de material e gargalos de expedição/PCP."
    }
    diag_rows=[]
    max_impact=max(list(lever_impacts.values())+[1])
    for lever,impact in lever_impacts.items():
        ef,horizon,owner=effort.get(lever,(3,45,"Gestão"))
        result_score=impact/max_impact*100
        priority_score=result_score/max(1,ef)
        if priority_score>=22:
            priority="Prioridade 1"
        elif priority_score>=10:
            priority="Prioridade 2"
        else:
            priority="Prioridade 3"
        diag_rows.append([lever,impact,ef,horizon,owner,result_score,priority_score,priority,action_library[lever]])
    diagnostic=pd.DataFrame(diag_rows,columns=[
        "Alavanca","Impacto_R$","Esforco","Horizonte_dias","Responsavel","Resultado_0a100",
        "Indice_Prioridade","Prioridade","Acao"
    ]).sort_values(["Indice_Prioridade","Impacto_R$"],ascending=False)

    top2=diagnostic.head(2)["Alavanca"].tolist()
    conclusion=(
        f"A operação fechou em {attainment:.1%} do plano, com OEE de {oee:.1%} e margem industrial de {margin_contrib:.1%}. "
        f"A saúde consolidada está em {health_score:.0f}/100 e a saúde financeira em {financial_health:.0f}/100. "
    )
    if worst_line is not None:
        conclusion += f"A linha mais crítica é {worst_line['Linha']} (OEE {worst_line['OEE']:.1%}). "
    if top_cause is not None:
        conclusion += f"A principal causa de parada é {top_cause['Causa']} ({top_cause['Horas']:.0f} h). "
    if top2:
        conclusion += "As alavancas a priorizar são " + " e ".join(top2) + "."

    return {
        "cards":cards,"kpis":kpis,"trend":trend,"line_perf":line_perf,"causes":causes,
        "impacts":impacts,"dre":dre,"cost_structure":{"Variável":var_cost,"Fixo":fixed_cost},
        "cost_structure_detail":{
            "Insumos / MP":cost_mp,"MOD":cost_mod,"GGF — Frete":cost_freight,
            "GGF — Energia":cost_energy,"GGF — Manutenção":cost_maintenance,
            "GGF — Contratos":cost_contracts,"GGF — Outros":cost_ggf_other,
            "Custos Fixos Industriais":fixed_industrial,
            "Despesas":expenses_total
        },
        "oee":oee,"target_oee":t_oee,"scrap":scrap,"target_scrap":t_scrap,
        "attainment":attainment,"margin":margin_contrib,"target_margin":t_margin,
        "ebitda":ebitda,"revenue":revenue,"revenue_gross":revenue_gross,"deductions":deductions,
        "actual":actual,"planned":planned,"sold_volume":sold_volume,
        "availability":availability,"performance":performance,"quality":quality,
        "cost_unit":cost_unit,"overtime":overtime,"productivity":productivity_raw,
        "rework_rate":rework_rate,"mttr_min":mttr_min,"setup_avg_min":setup_avg_min,
        "unplanned_downtime_h":unplanned_downtime_h,
        "avg_headcount":avg_headcount,
        "cost_mp":cost_mp,"cost_mod":cost_mod,"cost_freight":cost_freight,
        "cost_energy":cost_energy,"cost_maintenance":cost_maintenance,
        "cost_contracts":cost_contracts,"cost_ggf_other":cost_ggf_other,
        "fixed_industrial":fixed_industrial,
        "exp_admin":exp_admin,"exp_commercial":exp_commercial,"exp_logistics":exp_logistics,
        "other_opex":other_opex,"expenses_total":expenses_total,
        "material_consumption_kg":material_consumption_kg,
        "mp_price_per_kg":weighted_mp_price if pd.notna(weighted_mp_price) and weighted_mp_price>0 else np.nan,
        "energy_consumption_kwh":energy_consumption_kwh,
        "energy_kwh_per_unit":safe_div(energy_consumption_kwh,sold_volume) if energy_consumption_kwh>0 else np.nan,
        "inventory_days":inventory_days,"dpo_days":dpo_days,"dso_days":dso_days,
        "labor_efficiency":labor_eff,"std_hours_earned":std_hours_earned,"actual_hh":actual_hh,
        "standards_missing":standards_missing,
        "health_score":health_score,"financial_health":financial_health,"operational_health":operational_health,
        "health_details":health_df,
        "diagnostic":diagnostic,"diagnostic_conclusion":conclusion
    }

def demo_dataset():
    trend=pd.DataFrame({
        "data":pd.date_range("2026-08-01",periods=31,freq="D"),
        "planejado":[1450+((i%7)*12) for i in range(31)],
        "realizado":[1320+((i%7)*17)+(40 if i>20 else 0) for i in range(31)]
    })
    line_perf=pd.DataFrame({
        "Linha":["Linha 1","Linha 2","Linha 3","Linha 4"],
        "OEE":[.81,.76,.64,.74],"Disponibilidade":[.86,.82,.69,.80],
        "Performance":[.96,.94,.95,.93],"Qualidade":[.98,.985,.975,.99],
        "Refugo":[.022,.026,.041,.019],"Gap Produção":[-1200,-2100,-7200,-1800],
        "Paradas h":[18,31,79,25]
    })
    causes=pd.DataFrame({
        "Causa":["Falha mecânica","Setup","Falha elétrica","Falta de material","Microparadas","Qualidade"],
        "Horas":[58,41,29,22,18,12],
        "Impacto R$ mil":[164,96,82,61,45,39]
    })
    cards=[
        ("Receita Líquida","R$ 12,4 mi",-0.068,"-6,8% vs. meta"),
        ("Margem Industrial","27,8%",-0.103,"-3,2 pp vs. meta"),
        ("EBITDA Industrial","R$ 1,9 mi",-0.208,"-20,8% vs. meta"),
        ("Produção","41.250 un",-0.083,"-8,3% vs. meta"),
        ("OEE","71,4%",-0.0846,"-6,6 pp vs. meta"),
        ("Custo / un.","R$ 18,42",-0.077,"+7,7% vs. meta"),
    ]
    kpis=[
        ("Produção","41.250 un","45.000",-0.083,"-8,3%","↓"),
        ("OEE","71,4%","78%",-0.0846,"-6,6 pp","↓"),
        ("Eficiência MOD","89,8%","95%",-0.055,"-5,2 pp","↓"),
        ("Refugo","3,8%","2,5%",-0.52,"+1,3 pp","↑"),
        ("OTIF","89%","95%",-0.063,"-6 pp","↓"),
        ("Custo/unidade","R$ 18,42","R$ 17,10",-0.077,"+7,7%","↑"),
        ("Horas extras","1.280 h","900 h",-0.422,"+42%","↑"),
        ("Margem Industrial","27,8%","31%",-0.103,"-3,2 pp","↓"),
    ]
    impacts=pd.DataFrame({
        "Impacto":["Gap de volume","Refugo","Eficiência MOD","Horas extras","Custo / consumo"],
        "R$":[220000,110000,84000,75000,48000]
    })
    dre=pd.DataFrame({
        "Linha":[
            "Receita Bruta","(-) Impostos e deduções","Receita Líquida",
            "(-) Insumos / Matéria-prima","(-) MOD",
            "(-) GGF — Frete","(-) GGF — Energia","(-) GGF — Manutenção",
            "(-) GGF — Contratos e Serviços","(-) GGF — Outros",
            "Margem Industrial","(-) Custos Fixos Industriais","Resultado Industrial",
            "(-) Despesas Administrativas","(-) Despesas Comerciais",
            "(-) Despesas Logísticas","(-) Outros OPEX","EBITDA"
        ],
        "Realizado":[
            13200000,-800000,12400000,
            -5191000,-1611000,-553000,-895000,-500000,-120000,-80000,
            3450000,-950000,2500000,-250000,-180000,-100000,-70000,1900000
        ]
    })
    health_details=pd.DataFrame([
        ["Produção",72,3.0,220000,True,True],
        ["OEE",67,2.4,154000,True,True],
        ["Eficiência MOD",72,1.8,84000,True,True],
        ["Refugo",20,2.0,110000,True,True],
        ["OTIF",70,1.2,50000,True,True],
        ["Custo/unidade",68,1.6,95000,True,True],
        ["Horas extras",0,1.5,75000,True,True],
        ["Margem Industrial",50,2.2,397000,True,True],
    ],columns=["KPI","Score","Peso","Relevancia_R$","Tem_Meta","Tem_Dado"])
    diagnostic=pd.DataFrame([
        ["Setup",96000,2,30,"Engenharia de Processos",31,15.5,"Prioridade 2","Aplicar SMED e preparação externa."],
        ["Refugo",214000,3,45,"Qualidade / Processos",69,23.0,"Prioridade 1","Pareto por produto/causa e revisão de parâmetros."],
        ["Disponibilidade",312000,4,60,"Manutenção",100,25.0,"Prioridade 1","Plano de confiabilidade na Linha 3 / MX-04."],
        ["Eficiência MOD",84000,3,45,"Produção / Engenharia",27,9.0,"Prioridade 3","Rebalancear células usando HH padrão por produto."],
        ["Horas extras",88000,2,30,"Produção",28,14.0,"Prioridade 2","Revisar escala, gargalos e capacidade."],
        ["Consumo MP",72000,3,45,"Processos / Suprimentos",23,7.7,"Prioridade 3","Comparar consumo real x padrão e atacar rendimento."],
    ],columns=["Alavanca","Impacto_R$","Esforco","Horizonte_dias","Responsavel","Resultado_0a100","Indice_Prioridade","Prioridade","Acao"]).sort_values("Indice_Prioridade",ascending=False)

    return {
        "cards":cards,"kpis":kpis,"trend":trend,"line_perf":line_perf,"causes":causes,"impacts":impacts,
        "dre":dre,"cost_structure":{"Variável":8950000,"Fixo":1550000},
        "cost_structure_detail":{
            "Insumos / MP":5191000.0,"MOD":1611000.0,"GGF — Frete":553000.0,
            "GGF — Energia":895000.0,"GGF — Manutenção":500000.0,
            "GGF — Contratos":120000.0,"GGF — Outros":80000.0,
            "Custos Fixos Industriais":950000.0,"Despesas":600000.0
        },
        "oee":.714,"target_oee":.78,"scrap":.038,"target_scrap":.025,
        "attainment":.917,"margin":.278,"target_margin":.31,
        "ebitda":1900000,"revenue":12400000,"revenue_gross":13200000,"deductions":800000,
        "actual":41250,"planned":45000,"sold_volume":41250,
        "availability":.748,"performance":.945,"quality":.981,
        "cost_unit":18.42,"overtime":1280,"productivity":18.2,
        "rework_rate":.042,"mttr_min":95.0,"setup_avg_min":48.0,"unplanned_downtime_h":112.0,
        "avg_headcount":118,
        "cost_mp":5191000.0,"cost_mod":1611000.0,"cost_freight":553000.0,
        "cost_energy":895000.0,"cost_maintenance":500000.0,
        "cost_contracts":120000.0,"cost_ggf_other":80000.0,
        "fixed_industrial":950000.0,
        "exp_admin":250000.0,"exp_commercial":180000.0,"exp_logistics":100000.0,
        "other_opex":70000.0,"expenses_total":600000.0,
        "material_consumption_kg":61800.0,"mp_price_per_kg":84.0,
        "energy_consumption_kwh":23512.5,"energy_kwh_per_unit":0.57,
        "inventory_days":45.0,"dpo_days":30.0,"dso_days":35.0,
        "labor_efficiency":.898,"std_hours_earned":12120,"actual_hh":13497,
        "standards_missing":[],
        "health_score":55,"financial_health":49,"operational_health":61,
        "health_details":health_details,
        "diagnostic":diagnostic,
        "diagnostic_conclusion":"A fábrica fechou em 91,7% do plano, com OEE de 71,4% e margem industrial de 27,8%. A saúde consolidada está em 55/100 e a saúde financeira em 49/100. A Linha 3 é a mais crítica (OEE 64%). A principal causa de parada é Falha mecânica (58 h). As alavancas a priorizar são Disponibilidade e Refugo."
    }


def _pdf_money(v):
    try:
        return fmt_money(float(v))
    except Exception:
        return str(v)

def build_diagnostic_pdf(D, diag, causes):
    """Create a compact executive PDF report from the diagnostic page."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=14*mm, leftMargin=14*mm,
        topMargin=14*mm, bottomMargin=14*mm,
        title="Industrial Performance - Relatorio de Diagnostico"
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="H2MTitle", parent=styles["Title"],
        fontName="Helvetica-Bold", fontSize=18, leading=21,
        textColor=colors.HexColor("#071C31"), spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        name="H2MSub", parent=styles["Normal"],
        fontName="Helvetica", fontSize=8.5, leading=11,
        textColor=colors.HexColor("#6E7C90"), spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name="H2MSection", parent=styles["Heading2"],
        fontName="Helvetica-Bold", fontSize=11, leading=13,
        textColor=colors.HexColor("#10233F"), spaceBefore=8, spaceAfter=5
    ))
    styles.add(ParagraphStyle(
        name="H2MBody", parent=styles["BodyText"],
        fontName="Helvetica", fontSize=8.5, leading=12,
        textColor=colors.HexColor("#34465C")
    ))
    styles.add(ParagraphStyle(
        name="H2MSmall", parent=styles["BodyText"],
        fontName="Helvetica", fontSize=7.4, leading=9.5,
        textColor=colors.HexColor("#566B7C")
    ))

    story = []
    story.append(Paragraph("INDUSTRIAL PERFORMANCE", styles["H2MSub"]))
    story.append(Paragraph("Relatorio Executivo de Diagnostico", styles["H2MTitle"]))
    story.append(Paragraph(
        "Performance operacional -> causa -> impacto financeiro -> alavanca -> acao.",
        styles["H2MSub"]
    ))

    # Executive score table
    score_data = [
        ["Saude Geral", "Saude Financeira", "Saude Operacional", "OEE", "Margem"],
        [f"{D['health_score']:.0f}/100", f"{D['financial_health']:.0f}/100",
         f"{D['operational_health']:.0f}/100", fmt_pct(D["oee"]), fmt_pct(D["margin"])]
    ]
    score_table = Table(score_data, colWidths=[35*mm]*5)
    score_table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#071C31")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),7.5),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("BACKGROUND",(0,1),(-1,1),colors.HexColor("#F4F7FB")),
        ("TEXTCOLOR",(0,1),(-1,1),colors.HexColor("#10233F")),
        ("FONTNAME",(0,1),(-1,1),"Helvetica-Bold"),
        ("BOX",(0,0),(-1,-1),0.4,colors.HexColor("#DDE6EF")),
        ("INNERGRID",(0,0),(-1,-1),0.3,colors.HexColor("#DDE6EF")),
        ("TOPPADDING",(0,0),(-1,-1),5),
        ("BOTTOMPADDING",(0,0),(-1,-1),5),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 5*mm))

    story.append(Paragraph("Conclusao executiva", styles["H2MSection"]))
    story.append(Paragraph(str(D.get("diagnostic_conclusion","")), styles["H2MBody"]))

    story.append(Paragraph("Principais KPIs", styles["H2MSection"]))
    kpi_data = [["Indicador","Realizado","Meta","Desvio"]]
    for ind,mes,meta,score,delta,tend in D["kpis"]:
        kpi_data.append([str(ind),str(mes),str(meta),str(delta)])
    t = Table(kpi_data, colWidths=[56*mm,39*mm,39*mm,38*mm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0B5FA5")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),7.2),
        ("TEXTCOLOR",(0,1),(-1,-1),colors.HexColor("#10233F")),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F8FAFC")]),
        ("GRID",(0,0),(-1,-1),0.25,colors.HexColor("#DDE6EF")),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),4),
        ("BOTTOMPADDING",(0,0),(-1,-1),4),
    ]))
    story.append(t)

    story.append(Paragraph("Alavancas priorizadas", styles["H2MSection"]))
    d = diag.head(6).copy()
    lever_data = [["Prioridade","Alavanca","Impacto","Esforco","Horizonte","Responsavel"]]
    for _,r in d.iterrows():
        lever_data.append([
            str(r["Prioridade"]), str(r["Alavanca"]), _pdf_money(r["Impacto_R$"]),
            f"{int(r['Esforco'])}/5", f"{int(r['Horizonte_dias'])} dias", str(r["Responsavel"])
        ])
    lt = Table(lever_data, colWidths=[24*mm,34*mm,28*mm,20*mm,24*mm,46*mm], repeatRows=1)
    lt.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#071C31")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),6.8),
        ("GRID",(0,0),(-1,-1),0.25,colors.HexColor("#DDE6EF")),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F8FAFC")]),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("TOPPADDING",(0,0),(-1,-1),4),
        ("BOTTOMPADDING",(0,0),(-1,-1),4),
    ]))
    story.append(lt)

    story.append(PageBreak())
    story.append(Paragraph("Causas e perdas", styles["H2MSection"]))
    cause_data=[["Causa","Horas","Impacto estimado"]]
    for _,r in causes.head(8).iterrows():
        cause_data.append([
            str(r["Causa"]), f"{float(r['Horas']):.0f} h",
            f"R$ {float(r.get('Impacto R$ mil',0)):.0f} mil"
        ])
    ct=Table(cause_data,colWidths=[95*mm,35*mm,48*mm],repeatRows=1)
    ct.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0B5FA5")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),7.2),
        ("GRID",(0,0),(-1,-1),0.25,colors.HexColor("#DDE6EF")),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F8FAFC")]),
        ("TOPPADDING",(0,0),(-1,-1),4),
        ("BOTTOMPADDING",(0,0),(-1,-1),4),
    ]))
    story.append(ct)

    story.append(Paragraph("Plano de acoes sugerido", styles["H2MSection"]))
    action_data=[["Alavanca","Acao proposta","Responsavel","Impacto"]]
    for _,r in d.iterrows():
        action_data.append([
            str(r["Alavanca"]),
            Paragraph(str(r["Acao"]), styles["H2MSmall"]),
            str(r["Responsavel"]),
            _pdf_money(r["Impacto_R$"])
        ])
    at=Table(action_data,colWidths=[32*mm,82*mm,38*mm,30*mm],repeatRows=1)
    at.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#071C31")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),6.8),
        ("GRID",(0,0),(-1,-1),0.25,colors.HexColor("#DDE6EF")),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F8FAFC")]),
        ("TOPPADDING",(0,0),(-1,-1),4),
        ("BOTTOMPADDING",(0,0),(-1,-1),4),
    ]))
    story.append(at)
    story.append(Spacer(1,4*mm))
    story.append(Paragraph(
        "Nota metodologica: o impacto financeiro utiliza buckets sem dupla contagem entre causa e efeito. "
        "KPIs sem meta ou sem dado sao penalizados como risco de gestao. A produtividade multiproduto deve ser linearizada por horas-padrao.",
        styles["H2MSmall"]
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def sim_assumption(key, default):
    data=st.session_state.get("real_data")
    if not data or "premissas_simulador" not in data:
        return default
    df=data["premissas_simulador"]
    if df is None or df.empty or "chave" not in df.columns or "valor" not in df.columns:
        return default
    hit=df[df["chave"].astype(str).map(norm)==norm(key)]
    if hit.empty:
        return default
    val=pd.to_numeric(hit.iloc[0]["valor"],errors="coerce")
    return float(val) if pd.notna(val) else default


def simulator_baselines(D):
    """Baselines reais usados pelo simulador. Sempre trabalha em Atual -> Meta."""
    base_volume=max(1.0,float(D.get("sold_volume",D.get("actual",1)) or 1))
    base_price=safe_div(float(D.get("revenue",0)),base_volume)

    material_kg=float(D.get("material_consumption_kg",np.nan))
    if pd.notna(material_kg) and material_kg>0:
        mp_specific=material_kg/base_volume
        mp_specific_unit="kg/un"
    else:
        mp_specific=sim_assumption("consumo_mp_indice_base",1.04)
        mp_specific_unit="índice"

    mp_price=float(D.get("mp_price_per_kg",np.nan))
    if pd.notna(mp_price) and mp_price>0:
        mp_price_unit="R$/kg"
    else:
        mp_price=1.0
        mp_price_unit="índice"

    energy_intensity=float(D.get("energy_kwh_per_unit",np.nan))
    if pd.notna(energy_intensity) and energy_intensity>0:
        energy_unit="kWh/un"
    else:
        energy_intensity=1.0
        energy_unit="índice"

    freight_unit=safe_div(float(D.get("cost_freight",0)),base_volume)
    setup=float(D.get("setup_avg_min",np.nan))
    if pd.isna(setup):
        setup=sim_assumption("setup_medio_base",48.0)
    mttr=float(D.get("mttr_min",np.nan))
    if pd.isna(mttr):
        mttr=sim_assumption("mttr_base",95.0)
    rework=float(D.get("rework_rate",np.nan))*100
    if pd.isna(rework):
        rework=sim_assumption("retrabalho_base",4.2)

    inv=float(D.get("inventory_days",np.nan))
    dpo=float(D.get("dpo_days",np.nan))
    dso=float(D.get("dso_days",np.nan))

    return {
        "oee":float(D.get("oee",0))*100,
        "availability":float(D.get("availability",0))*100,
        "performance":float(D.get("performance",0))*100,
        "capacity":sim_assumption("capacidade_utilizada_base",72.0),
        "scrap":float(D.get("scrap",0))*100,
        "rework":rework,
        "setup":setup,
        "unplanned_hours":float(D.get("unplanned_downtime_h",0) or 0),
        "mttr":mttr,
        "overtime_hours":float(D.get("overtime",0) or 0),
        "productivity":max(0.01,float(D.get("productivity",18.2) or 18.2)),
        "headcount":float(D.get("avg_headcount",118) if pd.notna(D.get("avg_headcount",np.nan)) else 118),
        "mp_specific":max(0.0001,float(mp_specific)),
        "mp_specific_unit":mp_specific_unit,
        "mp_price":max(0.0001,float(mp_price)),
        "mp_price_unit":mp_price_unit,
        "material_loss_pct":sim_assumption("perdas_material_base_pct",4.0),
        "energy_intensity":max(0.0001,float(energy_intensity)),
        "energy_unit":energy_unit,
        "freight_per_unit":max(0.0,float(freight_unit)),
        "otif":sim_assumption("otif_base",89.0),
        "price_per_unit":max(0.01,float(base_price)),
        "mix_pp":0.0,
        "volume_units":base_volume,
        "fixed_industrial":max(0.0,float(D.get("fixed_industrial",D.get("cost_structure",{}).get("Fixo",0)))),
        "contracts_services":max(0.0,float(D.get("cost_contracts",0))),
        "inventory_days":inv if pd.notna(inv) and inv>0 else sim_assumption("estoque_dias_base",45.0),
        "dpo_days":dpo if pd.notna(dpo) and dpo>0 else sim_assumption("prazo_fornecedor_base",30.0),
        "dso_days":dso if pd.notna(dso) and dso>0 else sim_assumption("prazo_cliente_base",35.0),
    }


def calculate_simulator_scenario(D, targets, prod_mode="OEE direto"):
    """
    Motor determinístico do simulador.
    A entrada é sempre valor atual -> valor meta.
    Preço e volume são encadeados: Receita = volume simulado x preço simulado.
    OTIF é receita protegida e não entra automaticamente na DRE.
    """
    B=simulator_baselines(D)

    base_revenue=float(D.get("revenue",0))
    base_ebitda=float(D.get("ebitda",0))
    base_volume=max(1.0,B["volume_units"])
    base_price=B["price_per_unit"]

    base_mp=float(D.get("cost_mp",0))
    base_mod=float(D.get("cost_mod",0))
    base_freight=float(D.get("cost_freight",0))
    base_energy=float(D.get("cost_energy",0))
    base_maintenance=float(D.get("cost_maintenance",0))
    base_contracts=float(D.get("cost_contracts",0))
    base_ggf_other=float(D.get("cost_ggf_other",0))
    base_fixed=float(D.get("fixed_industrial",0))
    exp_admin=float(D.get("exp_admin",0))
    exp_commercial=float(D.get("exp_commercial",0))
    exp_logistics=float(D.get("exp_logistics",0))
    other_opex=float(D.get("other_opex",0))
    expenses_total=exp_admin+exp_commercial+exp_logistics+other_opex

    # ---------- Capacidade / produção: habilita volume, não soma EBITDA em duplicidade ----------
    base_oee=max(0.0001,float(D.get("oee",0.0001)))
    base_avail=max(0.0001,float(D.get("availability",0.0001)))
    base_perf=max(0.0001,float(D.get("performance",0.0001)))
    base_quality=max(0.0001,float(D.get("quality",1.0)))

    setup_improvement=(B["setup"]-targets["setup"])/max(B["setup"],1e-9)
    unplanned_improvement=(B["unplanned_hours"]-targets["unplanned_hours"])/max(B["unplanned_hours"],1e-9) if B["unplanned_hours"]>0 else 0
    mttr_improvement=(B["mttr"]-targets["mttr"])/max(B["mttr"],1e-9)
    downtime_share=max(0.0,1-base_avail)
    process_recovery=downtime_share*(0.25*setup_improvement+0.45*unplanned_improvement+0.30*mttr_improvement)
    derived_availability=float(np.clip(base_avail+process_recovery,0.01,0.99))

    if prod_mode=="OEE direto":
        effective_oee=float(np.clip(targets["oee"]/100,0.01,0.99))
        effective_availability=base_avail
        effective_performance=base_perf
    else:
        manual_availability=float(np.clip(targets["availability"]/100,0.01,0.99))
        effective_availability=max(manual_availability,derived_availability)
        effective_performance=float(np.clip(targets["performance"]/100,0.01,1.05))
        effective_oee=float(np.clip(effective_availability*min(effective_performance,1.0)*base_quality,0.01,0.99))

    capacity_ratio=max(0.01,targets["capacity"]/max(B["capacity"],0.01))
    performance_capacity_ratio=max(0.01,effective_oee/base_oee)*capacity_ratio
    potential_units=max(0.0,base_volume*performance_capacity_ratio)

    requested_volume=max(0.0,float(targets["volume_units"]))
    realized_volume=min(requested_volume,potential_units) if requested_volume>base_volume else requested_volume
    realized_volume=max(0.0,realized_volume)
    volume_factor=safe_div(realized_volume,base_volume)

    # ---------- Receita: preço x volume, sem soma independente sobre a mesma base ----------
    target_price=max(0.0,float(targets["price_per_unit"]))
    volume_revenue_effect=base_price*(realized_volume-base_volume)
    price_revenue_effect=realized_volume*(target_price-base_price)
    simulated_revenue=base_revenue+volume_revenue_effect+price_revenue_effect

    # Mix altera contribuição / EBITDA, não a receita nominal.
    mix_ebitda=simulated_revenue*(float(targets["mix_pp"])/100)

    # ---------- MP / insumos: efeitos encadeados ----------
    mp_after_volume=base_mp*volume_factor
    base_scrap=float(B["scrap"])/100
    target_scrap=float(targets["scrap"])/100
    scrap_factor=(1-base_scrap)/max(1-target_scrap,0.001)
    mp_after_scrap=mp_after_volume*scrap_factor

    specific_ratio=float(targets["mp_specific"])/max(B["mp_specific"],1e-9)
    mp_after_specific=mp_after_scrap*specific_ratio

    price_mp_ratio=float(targets["mp_price"])/max(B["mp_price"],1e-9)
    mp_after_price=mp_after_specific*price_mp_ratio

    loss_factor=(1+float(targets["material_loss_pct"])/100)/max(1+B["material_loss_pct"]/100,1e-9)
    scenario_mp=max(0.0,mp_after_price*loss_factor)

    scrap_saving=mp_after_volume-mp_after_scrap
    mp_specific_saving=mp_after_scrap-mp_after_specific
    mp_price_saving=mp_after_specific-mp_after_price
    material_loss_saving=mp_after_price-scenario_mp

    # ---------- MOD + retrabalho + produtividade + hora extra ----------
    mod_after_volume=base_mod*volume_factor
    rework_factor=(1+float(targets["rework"])/100)/max(1+B["rework"]/100,1e-9)
    mod_after_rework=mod_after_volume*rework_factor
    productivity_factor=B["productivity"]/max(float(targets["productivity"]),0.01)
    mod_after_productivity=mod_after_rework*productivity_factor

    actual_hh=max(1.0,float(D.get("actual_hh",1)))
    labor_rate=safe_div(base_mod,actual_hh)
    overtime_premium_factor=sim_assumption("adicional_hora_extra",0.50)
    overtime_saving=(B["overtime_hours"]-float(targets["overtime_hours"]))*labor_rate*overtime_premium_factor
    scenario_mod=max(0.0,mod_after_productivity-overtime_saving)

    rework_mod_saving=mod_after_volume-mod_after_rework
    productivity_saving=mod_after_rework-mod_after_productivity

    # ---------- Energia: volume + retrabalho + intensidade ----------
    energy_after_volume=base_energy*volume_factor
    energy_after_rework=energy_after_volume*rework_factor
    energy_intensity_ratio=float(targets["energy_intensity"])/max(B["energy_intensity"],1e-9)
    scenario_energy=max(0.0,energy_after_rework*energy_intensity_ratio)
    rework_energy_saving=energy_after_volume-energy_after_rework
    energy_saving=energy_after_rework-scenario_energy
    rework_saving=rework_mod_saving+rework_energy_saving

    # ---------- Frete dentro de GGF ----------
    freight_after_volume=base_freight*volume_factor
    scenario_freight=max(0.0,float(targets["freight_per_unit"])*realized_volume)
    freight_saving=freight_after_volume-scenario_freight

    # ---------- GGF / Estrutura ----------
    scenario_contracts=max(0.0,float(targets["contracts_services"]))
    contracts_saving=base_contracts-scenario_contracts

    headcount_value=(B["headcount"]-float(targets["headcount"]))*sim_assumption("custo_medio_mensal_pessoa",8500.0)
    explicit_fixed_change=abs(float(targets["fixed_industrial"])-B["fixed_industrial"])>1.0
    if explicit_fixed_change:
        scenario_fixed=max(0.0,float(targets["fixed_industrial"]))
        fixed_saving=base_fixed-scenario_fixed
        headcount_ebitda=0.0
    else:
        scenario_fixed=max(0.0,base_fixed-headcount_value)
        fixed_saving=0.0
        headcount_ebitda=base_fixed-scenario_fixed

    # ---------- DRE simulada ----------
    scenario_industrial_cost=(
        scenario_mp+scenario_mod+scenario_freight+scenario_energy+
        base_maintenance+scenario_contracts+base_ggf_other
    )
    simulated_industrial_margin_value=simulated_revenue+mix_ebitda-scenario_industrial_cost
    simulated_margin=safe_div(simulated_industrial_margin_value,simulated_revenue)
    simulated_result_industrial=simulated_industrial_margin_value-scenario_fixed
    simulated_ebitda=simulated_result_industrial-expenses_total
    ebitda_gain=simulated_ebitda-base_ebitda
    revenue_gain=simulated_revenue-base_revenue

    # O efeito volume no EBITDA inclui a variação de custos necessária para produzir/vender o volume.
    volume_cost_effect=-(
        (mp_after_volume-base_mp)+(mod_after_volume-base_mod)+
        (energy_after_volume-base_energy)+(freight_after_volume-base_freight)
    )
    volume_ebitda=volume_revenue_effect+volume_cost_effect
    price_ebitda=price_revenue_effect

    # ---------- OTIF: valor protegido, não DRE automática ----------
    otif_delta=float(targets["otif"])-B["otif"]
    if otif_delta>=0:
        denominator=max(1.0,100-B["otif"])
    else:
        denominator=max(1.0,B["otif"])
    otif_protected_value=base_revenue*sim_assumption("receita_em_risco_otif",0.12)*(otif_delta/denominator)

    # ---------- Capital de giro fora do EBITDA ----------
    period_days=max(1.0,sim_assumption("dias_periodo",30.0))
    inventory_release=(float(D.get("cost_structure",{}).get("Variável",scenario_industrial_cost))/period_days)*(B["inventory_days"]-float(targets["inventory_days"]))
    supplier_release=(base_mp/period_days)*(float(targets["dpo_days"])-B["dpo_days"])
    customer_release=(simulated_revenue/period_days)*(B["dso_days"]-float(targets["dso_days"]))
    working_capital_release=inventory_release+supplier_release+customer_release

    # ---------- Capacidade habilitada ----------
    incremental_capacity_units=max(0.0,potential_units-base_volume)
    unit_industrial_margin=safe_div(base_revenue-float(D.get("cost_structure",{}).get("Variável",0)),base_volume)
    capacity_value=max(0.0,incremental_capacity_units*max(unit_industrial_margin,0))

    # ---------- Bridge reconciliado ----------
    bridge={
        "Volume vendido":volume_ebitda,
        "Preço médio":price_ebitda,
        "Mix":mix_ebitda,
        "Refugo":scrap_saving,
        "Retrabalho":rework_saving,
        "Produtividade":productivity_saving,
        "Horas extras":overtime_saving,
        "Consumo específico MP":mp_specific_saving,
        "Preço de MP":mp_price_saving,
        "Perdas de material":material_loss_saving,
        "kWh/unidade":energy_saving,
        "Frete/unidade":freight_saving,
        "Contratos/serviços":contracts_saving,
        "Custo fixo":fixed_saving,
        "Headcount":headcount_ebitda,
    }
    bridge={k:float(v) for k,v in bridge.items() if abs(float(v))>0.5}

    # ---------- Value map: 26 alavancas ----------
    enable_weights={}
    if prod_mode=="OEE direto":
        enable_weights["OEE"]=abs(float(targets["oee"])-B["oee"])/max(B["oee"],1)
    else:
        enable_weights["Disponibilidade"]=abs(float(targets["availability"])-B["availability"])/max(B["availability"],1)
        enable_weights["Performance"]=abs(float(targets["performance"])-B["performance"])/max(B["performance"],1)
    enable_weights["Capacidade utilizada"]=abs(float(targets["capacity"])-B["capacity"])/max(B["capacity"],1)
    enable_weights["Setup médio"]=abs(float(targets["setup"])-B["setup"])/max(B["setup"],1)
    enable_weights["Paradas não planejadas"]=abs(float(targets["unplanned_hours"])-B["unplanned_hours"])/max(B["unplanned_hours"],1) if B["unplanned_hours"] else 0
    enable_weights["MTTR"]=abs(float(targets["mttr"])-B["mttr"])/max(B["mttr"],1)
    total_weight=sum(enable_weights.values()) or 1.0

    breakdown=[]
    for lever,w in enable_weights.items():
        if w>1e-9:
            breakdown.append([lever,capacity_value*w/total_weight,"Valor habilitado","Alta" if lever!="Capacidade utilizada" else "Média"])

    additive_map=[
        ("Refugo",scrap_saving,"EBITDA","Alta"),
        ("Retrabalho",rework_saving,"EBITDA","Alta"),
        ("Horas extras",overtime_saving,"EBITDA","Alta"),
        ("Produtividade",productivity_saving,"EBITDA","Alta"),
        ("Headcount",headcount_ebitda if not explicit_fixed_change else headcount_value,"EBITDA" if not explicit_fixed_change else "Driver de estrutura","Alta"),
        ("Consumo específico MP",mp_specific_saving,"EBITDA","Alta"),
        ("Preço de MP",mp_price_saving,"EBITDA","Alta"),
        ("Perdas de material",material_loss_saving,"EBITDA","Alta"),
        ("kWh/unidade",energy_saving,"EBITDA","Média"),
        ("Frete/unidade",freight_saving,"EBITDA / GGF","Alta"),
        ("OTIF",otif_protected_value,"Receita protegida","Média"),
        ("Preço médio",price_ebitda,"EBITDA","Alta"),
        ("Mix de produtos",mix_ebitda,"EBITDA","Média"),
        ("Volume vendido",volume_ebitda,"EBITDA","Alta"),
        ("Custo fixo",fixed_saving,"EBITDA","Alta"),
        ("Contratos/serviços",contracts_saving,"EBITDA / GGF","Alta"),
        ("Estoque",(float(D.get("cost_structure",{}).get("Variável",0))/period_days)*(B["inventory_days"]-float(targets["inventory_days"])),"Caixa","Alta"),
        ("Prazo fornecedor",supplier_release,"Caixa","Alta"),
        ("Prazo cliente",customer_release,"Caixa","Alta"),
    ]
    breakdown.extend(additive_map)
    breakdown_df=pd.DataFrame(breakdown,columns=["Alavanca","Impacto_R$","Tipo","Confiança"])
    if not breakdown_df.empty:
        breakdown_df["AbsImpact"]=breakdown_df["Impacto_R$"].abs()
        breakdown_df=breakdown_df.sort_values("AbsImpact",ascending=False).drop(columns=["AbsImpact"])

    simulated_dre=pd.DataFrame({
        "Linha":[
            "Receita Líquida","(-) Insumos / Matéria-prima","(-) MOD",
            "(-) GGF — Frete","(-) GGF — Energia","(-) GGF — Manutenção",
            "(-) GGF — Contratos e Serviços","(-) GGF — Outros",
            "Margem Industrial","(-) Custos Fixos Industriais","Resultado Industrial",
            "(-) Despesas Administrativas","(-) Despesas Comerciais",
            "(-) Despesas Logísticas","(-) Outros OPEX","EBITDA"
        ],
        "Base":[
            base_revenue,-base_mp,-base_mod,-base_freight,-base_energy,-base_maintenance,
            -base_contracts,-base_ggf_other,
            base_revenue-(base_mp+base_mod+base_freight+base_energy+base_maintenance+base_contracts+base_ggf_other),
            -base_fixed,
            base_revenue-(base_mp+base_mod+base_freight+base_energy+base_maintenance+base_contracts+base_ggf_other)-base_fixed,
            -exp_admin,-exp_commercial,-exp_logistics,-other_opex,base_ebitda
        ],
        "Simulado":[
            simulated_revenue,-scenario_mp,-scenario_mod,-scenario_freight,-scenario_energy,-base_maintenance,
            -scenario_contracts,-base_ggf_other,simulated_industrial_margin_value,
            -scenario_fixed,simulated_result_industrial,
            -exp_admin,-exp_commercial,-exp_logistics,-other_opex,simulated_ebitda
        ]
    })

    return {
        "baseline":B,
        "realized_volume":realized_volume,
        "requested_volume":requested_volume,
        "potential_units":potential_units,
        "output_potential_growth":safe_div(potential_units,base_volume)-1,
        "effective_oee":effective_oee,
        "effective_availability":effective_availability,
        "effective_performance":effective_performance,
        "simulated_revenue":simulated_revenue,
        "revenue_gain":revenue_gain,
        "simulated_ebitda":simulated_ebitda,
        "ebitda_gain":ebitda_gain,
        "simulated_margin":simulated_margin,
        "working_capital_release":working_capital_release,
        "otif_protected_value":otif_protected_value,
        "capacity_value":capacity_value,
        "scenario_fixed":scenario_fixed,
        "scenario_freight":scenario_freight,
        "bridge":bridge,
        "breakdown":breakdown_df,
        "simulated_dre":simulated_dre,
        "explicit_fixed_change":explicit_fixed_change,
    }


def owner_email(owner_name):
    data=st.session_state.get("real_data")
    if not data or "responsaveis" not in data:
        return ""
    r=data["responsaveis"]
    if r is None or r.empty or "responsavel" not in r.columns or "email" not in r.columns:
        return ""
    target=norm(owner_name)
    hit=r[r["responsavel"].astype(str).map(norm)==target]
    if hit.empty:
        return ""
    return str(hit.iloc[0]["email"] or "").strip()

def action_mailto(row):
    email=str(row.get("E-mail","") or "").strip()
    subject=f"Plano de Acao - {row.get('Problema','Industrial Performance')}"
    body=(
        f"Ola {row.get('Responsável','')},\n\n"
        f"Segue a acao sob sua responsabilidade no Industrial Performance:\n\n"
        f"Problema / oportunidade: {row.get('Problema','')}\n"
        f"Acao: {row.get('Ação','')}\n"
        f"Prioridade: {row.get('Prioridade','')}\n"
        f"Prazo: {row.get('Prazo','')}\n"
        f"Impacto esperado: {row.get('Impacto','')}\n"
        f"Status: {row.get('Status','')}\n\n"
        "Por favor, confirme o recebimento e atualize o andamento da acao."
    )
    return f"mailto:{quote(email)}?subject={quote(subject)}&body={quote(body)}"

def kpi_card(label,value,score,delta):
    c=score_color(score)
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-delta" style="color:{c}">
            <span class="dot" style="background:{c}"></span>{delta}
        </div>
    </div>"""

def panel_title(title,sub=None):
    st.markdown(
        f'<div class="panel-title">{title}</div>' +
        (f'<div class="panel-sub">{sub}</div>' if sub else ''),
        unsafe_allow_html=True
    )

def table_kpis(data):
    rows=[]
    for ind,mes,meta,score,delta,tend in data["kpis"]:
        c=score_color(score)
        rows.append(
            f"<tr><td>{ind}</td><td>{mes}</td><td>{meta}</td>"
            f"<td style='color:{c};font-weight:850'>{delta}</td>"
            f"<td style='color:{c};font-weight:850'>{tend}</td></tr>"
        )
    return f"""
    <table class="kpi-table">
        <colgroup><col style="width:34%"><col style="width:19%"><col style="width:17%"><col style="width:20%"><col style="width:10%"></colgroup>
        <thead><tr><th>Indicador</th><th>Mês</th><th>Meta</th><th>Desvio</th><th>Tend.</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
    </table>
    """

def nav(page):
    st.session_state.page = page
    st.rerun()


def _analytics_prepare_state(data):
    opts=ae.filter_options(data)
    signature=(
        tuple(opts.get("grupo",[])),tuple(opts.get("planta",[])),
        tuple(opts.get("linha",[])),tuple(opts.get("produto",[])),
        str(opts.get("date_min")),str(opts.get("date_max"))
    )
    if st.session_state.get("af_dataset_signature") != signature:
        st.session_state.af_dataset_signature=signature
        st.session_state.af_group="Todos"
        st.session_state.af_plant="Todas"
        st.session_state.af_line="Todas"
        st.session_state.af_product="Todos"
        if opts.get("date_min") is not None and opts.get("date_max") is not None:
            st.session_state.af_period=(opts["date_min"].date(),opts["date_max"].date())
        else:
            st.session_state.af_period=()
    st.session_state.analytics_filter_options=opts
    return opts


def _analytics_filters_from_state():
    period=st.session_state.get("af_period",())
    start=end=None
    if isinstance(period,(tuple,list)) and len(period)>=2:
        start,end=period[0],period[1]
    elif period:
        start=end=period
    return {
        "grupo":None if st.session_state.get("af_group","Todos")=="Todos" else st.session_state.get("af_group"),
        "planta":None if st.session_state.get("af_plant","Todas")=="Todas" else st.session_state.get("af_plant"),
        "linha":None if st.session_state.get("af_line","Todas")=="Todas" else st.session_state.get("af_line"),
        "produto":None if st.session_state.get("af_product","Todos")=="Todos" else st.session_state.get("af_product"),
        "start":start,"end":end,
    }


def page_header(title, subtitle):
    opts=st.session_state.get("analytics_filter_options",{})
    has_real=bool(st.session_state.get("real_data"))
    if has_real:
        groups=["Todos"]+list(opts.get("grupo",[]))
        plants=["Todas"]+list(opts.get("planta",[]))
        lines=["Todas"]+list(opts.get("linha",[]))
        products=["Todos"]+list(opts.get("produto",[]))

        c1,c2,c3,c4,c5,c6=st.columns([.86,.92,.86,.92,1.28,.88],gap="small")
        with c1:
            st.selectbox("Grupo",groups,key="af_group",label_visibility="collapsed")
        with c2:
            st.selectbox("Planta",plants,key="af_plant",label_visibility="collapsed")
        with c3:
            st.selectbox("Linha",lines,key="af_line",label_visibility="collapsed")
        with c4:
            st.selectbox("Produto",products,key="af_product",label_visibility="collapsed")
        with c5:
            dmin=opts.get("date_min")
            dmax=opts.get("date_max")
            if dmin is not None and dmax is not None:
                st.date_input(
                    "Período",key="af_period",
                    min_value=dmin.date(),max_value=dmax.date(),
                    label_visibility="collapsed"
                )
            else:
                st.caption("Período não disponível")
        with c6:
            context=ae.filter_context_label(_analytics_filters_from_state())
            badge="Dados filtrados" if context!="Todos os dados" else "Dados importados"
            st.markdown(f'<div style="text-align:right;padding-top:.2rem"><span class="data-badge">{badge}</span></div>',unsafe_allow_html=True)
    else:
        c1,c2,c3,c4,c5=st.columns([1,1,1,1,1.35],gap="small")
        c1.selectbox("Grupo",["Grupo Industrial S.A."],disabled=True,label_visibility="collapsed",key=f"demo_g_{title}")
        c2.selectbox("Planta",["Planta São Paulo"],disabled=True,label_visibility="collapsed",key=f"demo_p_{title}")
        c3.selectbox("Linha",["Todas"],disabled=True,label_visibility="collapsed",key=f"demo_l_{title}")
        c4.selectbox("Produto",["Todos"],disabled=True,label_visibility="collapsed",key=f"demo_pr_{title}")
        c5.markdown('<div style="text-align:right;padding-top:.2rem"><span class="data-badge">Dados demo · filtros após importação</span></div>',unsafe_allow_html=True)

    st.markdown('<div class="eyebrow">EXECUÇÃO HOJE. COMPETITIVIDADE AMANHÃ.</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="page-title">{title}</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{subtitle}</div>',unsafe_allow_html=True)

    meta=st.session_state.get("analytics_filter_meta",{})
    if meta.get("empty"):
        st.error("A combinação de filtros não possui registros de Produção. Os indicadores permanecem no último recorte válido até você ajustar os filtros.")
    for warning in meta.get("warnings",[]):
        st.warning(warning)


def admin_header(title, subtitle):
    st.markdown('<div class="eyebrow">INDUSTRIAL DATA + ANALYTICS · v0.6.4</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def _idl_init_state():
    defaults = {
        "idl_step": 1,
        "idl_raw": None,
        "idl_filename": "",
        "idl_file_hash": "",
        "idl_profile": None,
        "idl_mapping": None,
        "idl_mapping_rev": 0,
        "idl_standard": None,
        "idl_lineage": None,
        "idl_quality_checks": None,
        "idl_quality_summary": None,
        "idl_company": "Grupo Industrial S.A.",
        "idl_source": "Excel mensal",
        "idl_last_record": None,
        "idl_mapping_import_hash": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _idl_reset(keep_company=True):
    company = st.session_state.get("idl_company", "Grupo Industrial S.A.")
    source = st.session_state.get("idl_source", "Excel mensal")
    for key in list(st.session_state.keys()):
        if key.startswith("idl_"):
            del st.session_state[key]
    _idl_init_state()
    if keep_company:
        st.session_state.idl_company = company
        st.session_state.idl_source = source


def _idl_set_step(step):
    st.session_state.idl_step = int(max(1, min(5, step)))
    st.rerun()


def _idl_stepper():
    labels = ["Carregar", "Identificar", "Mapear", "Validar", "Aplicar"]
    step = st.session_state.idl_step
    st.progress(step / 5)
    cols = st.columns(5, gap="small")
    for i, (col, label) in enumerate(zip(cols, labels), start=1):
        with col:
            prefix = "●" if i == step else ("✓" if i < step else "○")
            color = BLUE if i == step else (GREEN if i < step else MUTED)
            st.markdown(
                f'<div style="font-size:.68rem;font-weight:800;color:{color};text-align:center">{prefix} {i}. {label}</div>',
                unsafe_allow_html=True,
            )
    st.write("")


def _idl_confidence_text(value):
    pct = float(value or 0) * 100
    if pct >= 95:
        return f"{pct:.0f}% · automático"
    if pct >= 70:
        return f"{pct:.0f}% · confirmar"
    return f"{pct:.0f}% · revisar"


def _idl_load_uploaded_file(uploaded):
    raw = uploaded.getvalue()
    digest = idl.workbook_fingerprint(raw)
    if digest != st.session_state.idl_file_hash:
        with st.spinner("Lendo estrutura, abas e campos do arquivo..."):
            mapping = idl.build_initial_mapping(raw, uploaded.name)
            profile = idl.inspect_workbook(raw, uploaded.name)
        st.session_state.idl_raw = raw
        st.session_state.idl_filename = uploaded.name
        st.session_state.idl_file_hash = digest
        st.session_state.idl_mapping = mapping
        st.session_state.idl_profile = profile
        st.session_state.idl_mapping_rev += 1
        st.session_state.idl_standard = None
        st.session_state.idl_lineage = None
        st.session_state.idl_quality_checks = None
        st.session_state.idl_quality_summary = None


def _idl_apply_mapping_profile(profile_bytes):
    try:
        imported = idl.mapping_from_json(profile_bytes)
        if not st.session_state.idl_raw:
            st.warning("Carregue primeiro o Excel que receberá este mapeamento.")
            return
        imported = idl.refresh_column_mapping(st.session_state.idl_raw, imported)
        st.session_state.idl_mapping = imported
        st.session_state.idl_mapping_rev += 1
        st.success("Perfil de mapeamento carregado. Revise as sugestões antes de aplicar.")
    except Exception as exc:
        st.error(f"Não foi possível ler o perfil de mapeamento: {exc}")


def _idl_render_step_1():
    st.markdown("### 1 · Carregar fonte")
    st.caption("O arquivo original é preservado na camada RAW. Nesta versão piloto, o armazenamento local do Streamlit é temporário; o mapping também pode ser exportado em JSON.")

    c1, c2 = st.columns(2, gap="small")
    with c1:
        st.session_state.idl_company = st.text_input("Empresa", value=st.session_state.idl_company, key="idl_company_input")
    with c2:
        st.session_state.idl_source = st.text_input("Fonte / sistema", value=st.session_state.idl_source, key="idl_source_input", help="Ex.: SAP Produção, TOTVS Custos, Excel Fechamento Industrial")

    uploaded = st.file_uploader("Arquivo Excel", type=["xlsx", "xls"], accept_multiple_files=False, key="idl_excel_upload")
    if uploaded is not None:
        try:
            _idl_load_uploaded_file(uploaded)
        except Exception as exc:
            st.error(f"Não foi possível ler o arquivo: {exc}")
            return

    if st.session_state.idl_profile:
        p = st.session_state.idl_profile
        cols = st.columns(4, gap="small")
        cols[0].metric("Abas", p["sheet_count"])
        cols[1].metric("Registros lidos", f"{p['total_rows']:,}".replace(",", "."))
        cols[2].metric("Tamanho", f"{p['size_bytes']/1024:.0f} KB")
        cols[3].metric("Fingerprint", p["hash"][:10].upper())

        with st.expander("Ver estrutura detectada", expanded=False):
            rows = []
            for sh, info in p["sheets"].items():
                suggestion = st.session_state.idl_mapping.get("sheet_map", {}).get(sh, {}) if st.session_state.idl_mapping else {}
                rows.append({
                    "Aba": sh,
                    "Linhas": info["rows"],
                    "Colunas": info["cols"],
                    "Sugestão": idl.ENTITY_LABELS.get(suggestion.get("entity"), "Ignorar / informativa"),
                    "Confiança": _idl_confidence_text(suggestion.get("confidence", 0)),
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        saved = idl.load_saved_mapping(st.session_state.idl_company, st.session_state.idl_source)
        if saved:
            st.info("Encontramos um DE/PARA salvo para esta empresa e fonte neste ambiente piloto.")
            if st.button("Reutilizar mapping salvo", key="idl_use_saved_mapping"):
                st.session_state.idl_mapping = idl.refresh_column_mapping(st.session_state.idl_raw, saved)
                st.session_state.idl_mapping_rev += 1
                st.success("Mapping reutilizado. Confirme as abas e campos nas próximas etapas.")

        mapping_file = st.file_uploader("Opcional · importar perfil de mapeamento (.json)", type=["json"], key="idl_mapping_upload")
        if mapping_file is not None:
            mh = idl.workbook_fingerprint(mapping_file.getvalue())
            if mh != st.session_state.idl_mapping_import_hash:
                st.session_state.idl_mapping_import_hash = mh
                _idl_apply_mapping_profile(mapping_file.getvalue())

        cprev, cnext = st.columns([1, 1], gap="small")
        with cprev:
            if st.button("Limpar importação", key="idl_reset_import"):
                _idl_reset(keep_company=True)
                st.rerun()
        with cnext:
            if st.button("Continuar · identificar abas →", type="primary", use_container_width=True, key="idl_to_step2"):
                _idl_set_step(2)
    else:
        st.info("Carregue um arquivo Excel para iniciar. O sistema não exige que as abas ou colunas tenham os nomes do nosso modelo padrão.")


def _idl_render_step_2():
    if not st.session_state.idl_raw or not st.session_state.idl_profile or not st.session_state.idl_mapping:
        st.warning("Carregue um arquivo antes de identificar as abas.")
        if st.button("← Voltar para carregar"):
            _idl_set_step(1)
        return

    st.markdown("### 2 · Identificar as abas")
    st.caption("O sistema sugere o papel de cada aba. Confirme apenas onde houver dúvida. Abas informativas podem ser ignoradas.")
    mapping = st.session_state.idl_mapping
    options = idl.entity_options()
    rev = st.session_state.idl_mapping_rev

    for sh, info in st.session_state.idl_profile["sheets"].items():
        current = mapping.get("sheet_map", {}).get(sh, {})
        entity = current.get("entity")
        current_label = idl.ENTITY_LABELS.get(entity, idl.IGNORE_ENTITY)
        c1, c2, c3 = st.columns([1.25, 1.35, .65], gap="small")
        with c1:
            st.markdown(f"**{sh}**")
            st.caption(f"{info['rows']:,} linhas · {info['cols']} colunas".replace(",", "."))
        with c2:
            choice = st.selectbox(
                "Entidade",
                options,
                index=options.index(current_label) if current_label in options else 0,
                key=f"idl_sheet_{rev}_{idl.safe_slug(sh)}",
                label_visibility="collapsed",
            )
            chosen_entity = None if choice == idl.IGNORE_ENTITY else idl.LABEL_TO_ENTITY[choice]
            if chosen_entity != entity:
                mapping["sheet_map"].setdefault(sh, {})["entity"] = chosen_entity
                mapping["sheet_map"][sh]["confidence"] = 1.0
                mapping["sheet_map"][sh]["reason"] = "confirmado pelo usuário"
        with c3:
            st.caption("Confiança")
            st.markdown(f"**{_idl_confidence_text(current.get('confidence', 0))}**")

    st.session_state.idl_mapping = mapping
    preview_sheet = st.selectbox("Prévia da aba", list(st.session_state.idl_profile["sheets"].keys()), key=f"idl_preview_sheet_{rev}")
    st.dataframe(st.session_state.idl_profile["sheets"][preview_sheet]["preview"], use_container_width=True, hide_index=True)

    cback, cnext = st.columns([1, 1], gap="small")
    with cback:
        if st.button("← Voltar", key="idl_step2_back"):
            _idl_set_step(1)
    with cnext:
        if st.button("Continuar · fazer DE/PARA →", type="primary", use_container_width=True, key="idl_to_step3"):
            st.session_state.idl_mapping = idl.refresh_column_mapping(st.session_state.idl_raw, st.session_state.idl_mapping)
            st.session_state.idl_mapping_rev += 1
            _idl_set_step(3)


def _idl_mapping_table_for_sheet(sh, entity, df):
    mapping = st.session_state.idl_mapping
    rows = []
    for col in df.columns:
        col_s = str(col)
        meta = mapping.get("column_map", {}).get(sh, {}).get(col_s, {})
        field = meta.get("field")
        unit_meta = mapping.get("unit_map", {}).get(sh, {}).get(col_s, {})
        sample_values = df[col].dropna().astype(str).head(3).tolist()
        rows.append({
            "Coluna origem": col_s,
            "Exemplo": " · ".join(sample_values)[:80],
            "Tipo": st.session_state.idl_profile["sheets"][sh]["types"].get(col_s, "—"),
            "Campo padrão": idl.field_display(entity, field) if field else "Não mapear",
            "Confiança": round(float(meta.get("confidence", 0)) * 100),
            "Unidade origem": unit_meta.get("source", idl.AUTO_UNIT),
            "Unidade destino": unit_meta.get("target") or "—",
        })
    table = pd.DataFrame(rows)
    field_display_options = ["Não mapear"] + [idl.field_display(entity, f) for f in idl.FIELD_SPECS.get(entity, {})]
    edited = st.data_editor(
        table,
        use_container_width=True,
        hide_index=True,
        disabled=["Coluna origem", "Exemplo", "Tipo", "Confiança", "Unidade destino"],
        column_config={
            "Campo padrão": st.column_config.SelectboxColumn("Campo padrão", options=field_display_options, required=True),
            "Unidade origem": st.column_config.SelectboxColumn("Unidade origem", options=idl.UNIT_OPTIONS, required=True),
            "Confiança": st.column_config.NumberColumn("Confiança", format="%d%%"),
        },
        key=f"idl_colmap_{st.session_state.idl_mapping_rev}_{idl.safe_slug(sh)}",
    )

    mapped_fields = []
    for _, row in edited.iterrows():
        source_col = str(row["Coluna origem"])
        field = idl.field_label_to_name(entity, str(row["Campo padrão"]))
        field = None if field == "Não mapear" else field
        old_field = mapping.get("column_map", {}).get(sh, {}).get(source_col, {}).get("field")
        mapping.setdefault("column_map", {}).setdefault(sh, {}).setdefault(source_col, {})["field"] = field
        if field != old_field:
            mapping["column_map"][sh][source_col]["confidence"] = 1.0
            mapping["column_map"][sh][source_col]["reason"] = "confirmado pelo usuário"
        source_unit = str(row["Unidade origem"])
        mapping.setdefault("unit_map", {}).setdefault(sh, {}).setdefault(source_col, {})["source"] = source_unit
        mapping["unit_map"][sh][source_col]["target"] = idl.FIELD_SPECS.get(entity, {}).get(field, {}).get("unit") if field else None
        if field:
            mapped_fields.append(field)

    duplicates = sorted({f for f in mapped_fields if mapped_fields.count(f) > 1})
    if duplicates:
        st.error("Há campos padrão usados mais de uma vez nesta aba: " + ", ".join(duplicates) + ". Mantenha apenas uma coluna de origem por campo.")

    # Required-field coverage
    required = [f for f, spec in idl.FIELD_SPECS.get(entity, {}).items() if spec.get("priority") == "required"]
    missing = [f for f in required if f not in mapped_fields]
    if missing:
        st.warning("Obrigatórios ainda sem DE/PARA: " + ", ".join(idl.FIELD_SPECS[entity][f]["label"] for f in missing))
    else:
        st.success("Campos obrigatórios desta entidade estão mapeados.")

    # Optional value-level dimension mapping
    dim_sources = []
    for source_col, meta in mapping.get("column_map", {}).get(sh, {}).items():
        if meta.get("field") in idl.DIMENSION_FIELDS:
            dim_sources.append((source_col, meta.get("field")))
    if dim_sources:
        with st.expander("Padronizar valores / dimensões", expanded=False):
            st.caption("Ex.: L01, Linha-01 e Célula A podem convergir para Linha 1. Até 40 valores distintos por campo são mostrados nesta tela; os demais são preservados como vieram.")
            for source_col, field in dim_sources:
                if source_col not in df.columns:
                    continue
                values = df[source_col].dropna().astype(str).str.strip()
                values = values[values.ne("")].drop_duplicates().head(40).tolist()
                if not values:
                    continue
                current_map = mapping.setdefault("dimension_map", {}).setdefault(sh, {}).setdefault(field, {})
                dim_df = pd.DataFrame({
                    "Valor origem": values,
                    "Valor padrão": [current_map.get(v, v) for v in values],
                })
                st.markdown(f"**{idl.FIELD_SPECS.get(entity, {}).get(field, {}).get('label', field)}**")
                dim_edit = st.data_editor(
                    dim_df,
                    use_container_width=True,
                    hide_index=True,
                    disabled=["Valor origem"],
                    key=f"idl_dim_{st.session_state.idl_mapping_rev}_{idl.safe_slug(sh)}_{field}",
                )
                for _, r in dim_edit.iterrows():
                    current_map[str(r["Valor origem"])] = str(r["Valor padrão"]).strip() or str(r["Valor origem"])

    st.session_state.idl_mapping = mapping
    return len(duplicates) == 0


def _idl_render_step_3():
    if not st.session_state.idl_raw or not st.session_state.idl_mapping:
        st.warning("Carregue e identifique as abas antes do DE/PARA.")
        if st.button("← Voltar para carregar"):
            _idl_set_step(1)
        return

    st.markdown("### 3 · DE/PARA e normalização")
    st.caption("Mapeie colunas, confirme unidades e, quando necessário, padronize dimensões. O arquivo original não é alterado.")
    raw = st.session_state.idl_raw
    xls = pd.ExcelFile(BytesIO(raw))
    all_ok = True
    mapped_sheets = 0
    for sh in xls.sheet_names:
        entity = st.session_state.idl_mapping.get("sheet_map", {}).get(sh, {}).get("entity")
        if not entity:
            continue
        mapped_sheets += 1
        df = pd.read_excel(BytesIO(raw), sheet_name=sh)
        with st.expander(f"{sh}  →  {idl.ENTITY_LABELS.get(entity, entity)}", expanded=mapped_sheets <= 2):
            ok = _idl_mapping_table_for_sheet(sh, entity, df)
            all_ok = all_ok and ok

    if mapped_sheets == 0:
        st.error("Nenhuma aba foi classificada. Volte à etapa anterior e identifique ao menos as entidades de dados.")
        all_ok = False

    cback, cnext = st.columns([1, 1], gap="small")
    with cback:
        if st.button("← Voltar", key="idl_step3_back"):
            _idl_set_step(2)
    with cnext:
        if st.button("Continuar · validar dados →", type="primary", use_container_width=True, disabled=not all_ok, key="idl_to_step4"):
            with st.spinner("Transformando para o Industrial Performance Data Model..."):
                standard, lineage = idl.transform_to_standard(st.session_state.idl_raw, st.session_state.idl_mapping)
                quality = idl.evaluate_data_quality(standard, st.session_state.idl_mapping)
            st.session_state.idl_standard = standard
            st.session_state.idl_lineage = lineage
            st.session_state.idl_quality_checks = quality.checks
            st.session_state.idl_quality_summary = quality.summary
            _idl_set_step(4)


def _idl_render_quality_summary(quality):
    cols = st.columns(4, gap="small")
    cols[0].metric("Qualidade da base", f"{quality.score:.0f}/100")
    cols[1].metric("Status", quality.status)
    cols[2].metric("Alertas", quality.summary.get("warnings", 0))
    cols[3].metric("Bloqueio", "Sim" if quality.blocking else "Não")
    if quality.blocking:
        st.error("Existem falhas estruturais que impedem o Performance Engine de calcular o modelo com segurança.")
    elif quality.score < 80:
        st.warning("A base pode ser aplicada, mas há limitações relevantes. Revise os alertas antes de usar os números para decisão.")
    else:
        st.success("A base está apta para alimentar o Performance Engine.")


def _idl_render_step_4():
    if not st.session_state.idl_standard:
        st.warning("Faça o DE/PARA antes de validar a base.")
        if st.button("← Voltar para mapear"):
            _idl_set_step(3)
        return

    st.markdown("### 4 · Validar qualidade dos dados")
    quality = idl.evaluate_data_quality(st.session_state.idl_standard, st.session_state.idl_mapping)
    st.session_state.idl_quality_checks = quality.checks
    st.session_state.idl_quality_summary = quality.summary
    _idl_render_quality_summary(quality)

    if not quality.checks.empty:
        view = quality.checks.copy()
        st.dataframe(view[["Categoria", "Item", "Severidade", "Resultado", "Detalhe", "Penalidade"]], use_container_width=True, hide_index=True)

    entities = list(st.session_state.idl_standard.keys())
    if entities:
        with st.expander("Revisar dados padronizados", expanded=False):
            ent = st.selectbox("Entidade", entities, format_func=lambda x: idl.ENTITY_LABELS.get(x, x), key="idl_standard_preview")
            st.dataframe(st.session_state.idl_standard[ent].head(30), use_container_width=True, hide_index=True)

    cback, cnext = st.columns([1, 1], gap="small")
    with cback:
        if st.button("← Corrigir DE/PARA", key="idl_step4_back"):
            _idl_set_step(3)
    with cnext:
        if st.button("Continuar · revisar aplicação →", type="primary", use_container_width=True, disabled=quality.blocking, key="idl_to_step5"):
            _idl_set_step(5)


def _idl_render_step_5():
    if not st.session_state.idl_standard or not st.session_state.idl_mapping:
        st.warning("Ainda não há uma base validada para aplicar.")
        if st.button("← Voltar"):
            _idl_set_step(4)
        return

    st.markdown("### 5 · Aplicar ao Industrial Performance")
    quality = idl.evaluate_data_quality(st.session_state.idl_standard, st.session_state.idl_mapping)
    if quality.blocking:
        _idl_render_quality_summary(quality)
        return

    nrows = sum(len(df) for df in st.session_state.idl_standard.values())
    cols = st.columns(4, gap="small")
    cols[0].metric("Entidades", len(st.session_state.idl_standard))
    cols[1].metric("Registros standard", f"{nrows:,}".replace(",", "."))
    cols[2].metric("Data Quality", f"{quality.score:.0f}/100")
    cols[3].metric("Lineage", f"{len(st.session_state.idl_lineage or [])} campos")

    st.info("Ao aplicar, Cockpit, Diagnóstico e Simulador passam a consumir o modelo padronizado. A origem continua rastreável pelo lineage.")

    mapping_json = idl.mapping_to_json(st.session_state.idl_mapping, st.session_state.idl_company, st.session_state.idl_source)
    c1, c2 = st.columns(2, gap="small")
    with c1:
        st.download_button(
            "Baixar perfil DE/PARA (.json)",
            mapping_json,
            file_name=f"mapping_{idl.safe_slug(st.session_state.idl_company)}_{idl.safe_slug(st.session_state.idl_source)}.json",
            mime="application/json",
            use_container_width=True,
        )
    with c2:
        if st.button("Aplicar dados ao Performance Engine", type="primary", use_container_width=True, key="idl_apply_engine"):
            record = None
            persist_error = None
            try:
                record = idl.persist_ingestion(
                    raw=st.session_state.idl_raw,
                    filename=st.session_state.idl_filename,
                    company=st.session_state.idl_company,
                    source=st.session_state.idl_source,
                    mapping=st.session_state.idl_mapping,
                    standard=st.session_state.idl_standard,
                    lineage=st.session_state.idl_lineage or [],
                    quality=quality,
                )
            except Exception as exc:
                persist_error = str(exc)
            st.session_state.real_data = st.session_state.idl_standard
            st.session_state.idl_last_record = record or {
                "company": st.session_state.idl_company,
                "source": st.session_state.idl_source,
                "filename": st.session_state.idl_filename,
                "quality_score": quality.score,
                "quality_status": quality.status,
                "storage_mode": "session_only",
                "persist_error": persist_error,
            }
            if persist_error:
                st.warning("Os dados foram aplicados ao Engine, mas a cópia local da camada piloto não pôde ser gravada. O cockpit continuará funcionando nesta sessão.")
            st.session_state.page = "Cockpit Executivo"
            st.rerun()

    with st.expander("Ver lineage / rastreabilidade", expanded=False):
        lineage_df = pd.DataFrame(st.session_state.idl_lineage or [])
        if lineage_df.empty:
            st.info("Nenhum lineage disponível.")
        else:
            st.dataframe(lineage_df, use_container_width=True, hide_index=True)

    if st.button("← Voltar à validação", key="idl_step5_back"):
        _idl_set_step(4)


def render_data_layer_import():
    _idl_init_state()
    _idl_stepper()
    step = st.session_state.idl_step
    if step == 1:
        _idl_render_step_1()
    elif step == 2:
        _idl_render_step_2()
    elif step == 3:
        _idl_render_step_3()
    elif step == 4:
        _idl_render_step_4()
    else:
        _idl_render_step_5()


# ============================================================
# SESSION STATE
# ============================================================
if "page" not in st.session_state:
    st.session_state.page = "Cockpit Executivo"
if "real_data" not in st.session_state:
    st.session_state.real_data = None
if "actions" not in st.session_state:
    st.session_state.actions = pd.DataFrame([
        ["Alta","Disponibilidade Linha 3","Plano de confiabilidade MX-04","Ger. Manutenção","","10/09/2026","R$ 312 mil","Em andamento"],
        ["Alta","Refugo Produto A","Revisar parâmetros de processo","Ger. Qualidade","","12/09/2026","R$ 214 mil","Não iniciado"],
        ["Média","Horas extras","Redimensionar turnos","Ger. Produção","","15/09/2026","R$ 88 mil","Em andamento"],
    ], columns=["Prioridade","Problema","Ação","Responsável","E-mail","Prazo","Impacto","Status"])

_analytics_prepare_state(st.session_state.real_data)
ACTIVE_FILTERS=_analytics_filters_from_state()
FILTERED_DATA, FILTER_META=ae.apply_filters(st.session_state.real_data,ACTIVE_FILTERS)
if st.session_state.real_data:
    if FILTER_META.get("empty"):
        ACTIVE_DATA=st.session_state.real_data
        D=calculate_real(ACTIVE_DATA)
    else:
        ACTIVE_DATA=FILTERED_DATA
        D=calculate_real(ACTIVE_DATA)
else:
    ACTIVE_DATA=None
    D=demo_dataset()
st.session_state.analytics_filter_meta=FILTER_META

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    c1, c2 = st.columns([.34, .66], gap="small")
    logo = Path(__file__).parent / "logo_h2m_transparent.png"
    with c1:
        if logo.exists():
            logo_b64 = base64.b64encode(logo.read_bytes()).decode("ascii")
            st.markdown(
                f'<a href="https://h2mconsulting.com.br" target="_blank" rel="noopener noreferrer" '
                f'title="Abrir H2M Consulting">'
                f'<img src="data:image/png;base64,{logo_b64}" alt="H2M Consulting" '
                f'style="width:76px;max-width:100%;height:auto;display:block;margin-top:1px;">'
                f'</a>',
                unsafe_allow_html=True
            )
    with c2:
        st.markdown(
            '<div class="brand-title" style="padding-top:4px">Industrial Performance</div>'
            '<div class="brand-sub">by H2M Consulting</div>',
            unsafe_allow_html=True
        )

    groups = [
        ("VISÃO", ["Cockpit Executivo","Performance Operacional","Diagnóstico e Causas"]),
        ("RESULTADO", ["Finanças / DRE","Alavancas de Valor","Plano de Ação"]),
        ("INTELIGÊNCIA", ["Agente de Performance","Relatórios"]),
        ("ADMINISTRAÇÃO", ["Central de Dados","Mapeamentos","Qualidade dos Dados","Configurações"]),
    ]
    for group, items in groups:
        st.markdown(f'<div class="menu-group">{group}</div>', unsafe_allow_html=True)
        for p in items:
            if st.button(p, key=f"nav_{p}", type="primary" if st.session_state.page == p else "secondary", use_container_width=True):
                nav(p)

    st.markdown('<div class="sidebar-footer"><b>Da operação ao resultado.</b><br><small>DADOS &nbsp;&nbsp; PERFORMANCE &nbsp;&nbsp; VALOR</small></div>', unsafe_allow_html=True)

# ============================================================
# PAGES
# ============================================================
page = st.session_state.page

if page == "Cockpit Executivo":
    page_header("Cockpit Executivo","Performance operacional e impacto financeiro em uma única leitura.")

    cols = st.columns(6, gap="small")
    for col, item in zip(cols, D["cards"]):
        with col:
            st.markdown(kpi_card(*item), unsafe_allow_html=True)

    st.write("")
    left, mid, right = st.columns([1.00,1.25,.72], gap="small")

    with left:
        with st.container(border=True, height=425):
            panel_title("Principais Indicadores","Realizado, meta, desvio e tendência")
            st.markdown(table_kpis(D), unsafe_allow_html=True)

    with mid:
        with st.container(border=True, height=425):
            panel_title("Tendência de Produção","Realizado versus plano — leitura contínua")
            trend = D["trend"].copy()
            x = trend["data"] if "data" in trend.columns else np.arange(len(trend))
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=x,y=trend["planejado"],name="Plano",
                mode="lines",line=dict(color="#AFC0D0",width=2,dash="dot")
            ))
            fig.add_trace(go.Scatter(
                x=x,y=trend["realizado"],name="Realizado",
                mode="lines",line=dict(color=BLUE,width=3),
                fill="tozeroy",fillcolor="rgba(11,95,165,.07)"
            ))
            fig.update_layout(
                height=300,margin=dict(l=4,r=4,t=10,b=6),
                paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h",y=1.08,x=0,font=dict(size=10)),
                xaxis=dict(showgrid=False,zeroline=False,tickfont=dict(size=9,color=MUTED)),
                yaxis=dict(gridcolor="#EFF3F7",zeroline=False,tickfont=dict(size=9,color=MUTED)),
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    with right:
        with st.container(border=True, height=425):
            panel_title("Saúde de Performance","Score ponderado por relevância financeira")
            h=D["health_score"]
            hcolor=GREEN if h>=75 else ORANGE if h>=55 else RED
            fig = go.Figure(go.Pie(
                labels=["Score","Gap"],
                values=[h,max(0,100-h)],
                hole=.76,
                marker=dict(colors=[hcolor,"#E8EEF4"],line=dict(width=0)),
                textinfo="none",
                hoverinfo="skip"
            ))
            fig.update_layout(
                height=190,margin=dict(l=0,r=0,t=0,b=0),showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                annotations=[dict(text=f"<b>{h:.0f}/100</b><br><span style='font-size:9px'>saúde geral</span>",
                                  x=.5,y=.5,showarrow=False,font=dict(size=16,color=TEXT))]
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
            st.markdown(
                f"<div style='display:flex;justify-content:space-between;font-size:.60rem'>"
                f"<span>Operacional <b>{D['operational_health']:.0f}</b></span>"
                f"<span>Financeira <b>{D['financial_health']:.0f}</b></span></div>",
                unsafe_allow_html=True
            )
            with st.expander("Como o score é calculado"):
                st.caption("Todos os KPIs críticos entram no score. KPI sem meta ou sem dado é penalizado como risco de gestão. O peso aumenta conforme a relevância financeira estimada em receita, margem, EBITDA ou caixa. A relevância usada no score não é somada ao DRE; o impacto financeiro aditivo evita dupla contagem entre causa e efeito.")
            st.write("")
            var = D["cost_structure"]["Variável"]
            fixed = D["cost_structure"]["Fixo"]
            totalc = max(1, var + fixed)
            vp = var / totalc * 100
            fp = fixed / totalc * 100
            st.markdown(
                f"<div class='panel-sub' style='margin-top:5px'>Estrutura de custos</div>"
                f"<div style='height:8px;border-radius:6px;overflow:hidden;display:flex'>"
                f"<div style='width:{vp:.1f}%;background:{BLUE}'></div>"
                f"<div style='width:{fp:.1f}%;background:#BBD8EC'></div></div>"
                f"<div style='display:flex;justify-content:space-between;margin-top:6px;font-size:.60rem'>"
                f"<span>Custo industrial <b>{vp:.0f}%</b></span><span>Estrutura + despesas <b>{fp:.0f}%</b></span></div>",
                unsafe_allow_html=True
            )

    st.write("")
    c1, c2, c3 = st.columns([1.02,1.05,.88], gap="small")

    with c1:
        with st.container(border=True, height=315):
            panel_title("Impactos no Resultado","Principais perdas traduzidas em R$")
            imp = D["impacts"].sort_values("R$").tail(5)
            fig = go.Figure(go.Bar(
                x=imp["R$"], y=imp["Impacto"], orientation="h",
                marker=dict(color="#E85B55"),
                text=[fmt_money(v,0) for v in imp["R$"]],
                textposition="outside",
                hovertemplate="%{y}<br>%{text}<extra></extra>"
            ))
            fig.update_layout(
                height=240,margin=dict(l=4,r=72,t=6,b=4),
                paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False,showticklabels=False,zeroline=False),
                yaxis=dict(showgrid=False,tickfont=dict(size=9,color=TEXT)),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    with c2:
        with st.container(border=True, height=315):
            panel_title("Alavancas Prioritárias","Onde atacar primeiro para recuperar resultado")
            lev = [
                ("Disponibilidade","Linha 3",312000,"Alta"),
                ("Refugo","Produto A",214000,"Alta"),
                ("Setup","Linha 2",96000,"Média"),
                ("Horas extras","Operação",88000,"Média"),
                ("Consumo MP","Mix",72000,"Baixa"),
            ]
            for name,scope,impact,prio in lev:
                if prio == "Alta":
                    bc,bg = RED,SOFT_RED
                elif prio == "Média":
                    bc,bg = ORANGE,SOFT_ORANGE
                else:
                    bc,bg = GREEN,SOFT_GREEN
                st.markdown(
                    f"<div style='display:grid;grid-template-columns:1.35fr .8fr .82fr .58fr;gap:7px;"
                    f"align-items:center;padding:7px 0;border-bottom:1px solid #EEF2F6;font-size:.64rem'>"
                    f"<div><b>{name}</b><br><span style='color:{MUTED};font-size:.55rem'>{scope}</span></div>"
                    f"<div>{fmt_money(impact,0)}</div>"
                    f"<div style='color:{MUTED}'>potencial</div>"
                    f"<div><span class='priority' style='color:{bc};background:{bg}'>{prio}</span></div></div>",
                    unsafe_allow_html=True
                )
        if st.button("Abrir alavancas", use_container_width=True):
            nav("Alavancas de Valor")

    with c3:
        with st.container(border=True, height=315):
            panel_title("Alertas Executivos","Desvios que exigem atenção")
            alerts = [
                (RED,"OEE da Linha 3 abaixo da meta","Principal pressão sobre disponibilidade."),
                (RED,"Refugo acima da referência","Pressão direta sobre custo variável."),
                (ORANGE,"Horas extras elevadas","Crescimento sem ganho proporcional de volume."),
                (ORANGE,"Custo unitário pressionado","Revisar mix, volume e consumo específico."),
            ]
            for color,title,sub in alerts:
                st.markdown(
                    f"<div class='alert'><div class='alert-icon' style='background:{color}'>!</div>"
                    f"<div><div class='alert-title'>{title}</div><div class='alert-sub'>{sub}</div></div></div>",
                    unsafe_allow_html=True
                )
        if st.button("Abrir diagnóstico", use_container_width=True):
            nav("Diagnóstico e Causas")

    st.write("")
    st.markdown("""
    <div class="agent-strip">
      <div>
        <div class="agent-title">✦ Diagnóstico Executivo</div>
        <div class="agent-copy">
        O desempenho do período está sendo pressionado principalmente por disponibilidade,
        refugo e custo de conversão. O foco deve ser recuperar volume sem ampliar a estrutura de custo.
        </div>
      </div>
      <div>
        <div class="agent-title">3 prioridades</div>
        <div class="agent-copy">
        1. Recuperar disponibilidade da Linha 3<br>
        2. Atacar refugo acima da meta<br>
        3. Redimensionar horas extras e turnos
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    if st.button("Conversar com o Agente de Performance", type="primary"):
        nav("Agente de Performance")

elif page == "Performance Operacional":
    page_header("Performance Operacional","Eficiência, capacidade, perdas e drill-down do KPI até a causa.")
    lp = D["line_perf"].copy()

    c1,c2,c3,c4 = st.columns(4, gap="small")
    c1.metric("OEE", fmt_pct(D["oee"]), f"{(D['oee']-D['target_oee'])*100:+.1f} pp".replace(".",","))
    c2.metric("Disponibilidade", fmt_pct(D["availability"]))
    c3.metric("Eficiência MOD", fmt_pct(D["labor_efficiency"]) if pd.notna(D["labor_efficiency"]) else "Padrão ausente", "mix linearizado")
    c4.metric("Qualidade", fmt_pct(D["quality"]))

    st.write("")
    c1, c2 = st.columns(2, gap="small")

    with c1:
        with st.container(border=True, height=375):
            panel_title("OEE por Linha","Comparação com meta no recorte selecionado")
            if not lp.empty:
                colors = [score_color(safe_div(v,D["target_oee"])-1) for v in lp["OEE"]]
                fig = go.Figure(go.Bar(
                    x=lp["Linha"], y=lp["OEE"], marker_color=colors,
                    text=[fmt_pct(x) for x in lp["OEE"]], textposition="outside"
                ))
                fig.add_hline(y=D["target_oee"], line_dash="dot", line_color="#9AAABD", annotation_text="Meta")
                fig.update_layout(height=300, margin=dict(l=0,r=0,t=8,b=0),
                                  paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                  yaxis=dict(tickformat=".0%", gridcolor="#EFF3F7", range=[0,1]),
                                  xaxis=dict(showgrid=False), showlegend=False)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
            else:
                st.info("Sem linhas no recorte selecionado.")

    with c2:
        with st.container(border=True, height=375):
            panel_title("Paradas x Gap de Produção","Localize linhas com perda de capacidade e volume")
            if not lp.empty:
                fig = go.Figure(go.Scatter(
                    x=lp["Paradas h"], y=lp["Gap Produção"], mode="markers+text",
                    text=lp["Linha"], textposition="top center",
                    marker=dict(size=np.clip(lp["Paradas h"],16,42), color=BLUE, opacity=.78, line=dict(width=2,color="white"))
                ))
                fig.update_layout(height=300, margin=dict(l=0,r=0,t=8,b=0),
                                  paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                  xaxis=dict(gridcolor="#EFF3F7"), yaxis=dict(gridcolor="#EFF3F7"))
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
            else:
                st.info("Sem dados para o gráfico no recorte.")

    st.write("")
    with st.container(border=True):
        panel_title("Drill-down de Performance","KPI → Linha → Máquina → Causa, preservando o recorte dos filtros globais")

        kpi_options=["OEE","Disponibilidade","Produção","Refugo","Horas extras","Custo/unidade"]
        line_options=["Todas"] + (lp["Linha"].astype(str).tolist() if not lp.empty else [])
        c1,c2,c3,c4=st.columns([.9,1,1,1.1],gap="small")

        with c1:
            drill_kpi=st.selectbox("KPI",kpi_options,key="an_drill_kpi")
        with c2:
            drill_line=st.selectbox("Linha",line_options,key="an_drill_line")
        selected_line=None if drill_line=="Todas" else drill_line

        machine_df=ae.machine_drilldown(ACTIVE_DATA,D,selected_line)
        machine_options=["Todas"] + (machine_df["Máquina"].astype(str).tolist() if not machine_df.empty else [])
        with c3:
            selected_machine_ui=st.selectbox(
                "Máquina",
                machine_options if drill_kpi in ["OEE","Disponibilidade","Produção"] else ["N/A"],
                key="an_drill_machine",
                disabled=drill_kpi not in ["OEE","Disponibilidade","Produção"]
            )
        selected_machine=None if selected_machine_ui in ["Todas","N/A"] else selected_machine_ui

        cause_df=ae.cause_drilldown(ACTIVE_DATA,D,selected_line,selected_machine)
        cause_options=["Todas"] + (cause_df["Causa"].astype(str).tolist() if not cause_df.empty else [])
        with c4:
            selected_cause_ui=st.selectbox(
                "Causa",
                cause_options if drill_kpi in ["OEE","Disponibilidade","Produção"] else ["N/A"],
                key="an_drill_cause",
                disabled=drill_kpi not in ["OEE","Disponibilidade","Produção"]
            )
        selected_cause=None if selected_cause_ui in ["Todas","N/A"] else selected_cause_ui

        breadcrumb=[drill_kpi]
        if selected_line:
            breadcrumb.append(selected_line)
        if selected_machine:
            breadcrumb.append(selected_machine)
        if selected_cause:
            breadcrumb.append(selected_cause)
        st.markdown(
            "<div class='frontend-note'><b>Drill-down:</b> " + " → ".join(breadcrumb) + "</div>",
            unsafe_allow_html=True
        )

        st.write("")
        if drill_kpi in ["OEE","Disponibilidade","Produção"]:
            a,b=st.columns([1,.95],gap="small")
            with a:
                panel_title("Máquinas — perda de disponibilidade","Horas de parada, eventos, MTTR e impacto estimado")
                if machine_df.empty:
                    st.info("A base não possui máquina + manutenção suficientes para este recorte.")
                else:
                    show_machine=machine_df.copy()
                    show_machine["Paradas h"]=show_machine["Paradas h"].round(1)
                    show_machine["MTTR min"]=show_machine["MTTR min"].round(0)
                    show_machine["Impacto"]=show_machine["Impacto R$"].map(lambda x:fmt_money(x))
                    show_machine=show_machine.drop(columns=["Impacto R$"])
                    st.dataframe(show_machine,use_container_width=True,hide_index=True,height=285)
            with b:
                panel_title("Causas — Pareto do recorte","Causa dominante e impacto econômico estimado")
                if cause_df.empty:
                    st.info("A base não possui causas de manutenção estruturadas neste recorte.")
                else:
                    show_cause=cause_df.copy()
                    show_cause["Paradas h"]=show_cause["Paradas h"].round(1)
                    show_cause["% das horas"]=show_cause["% das horas"].map(lambda x:f"{x:.1%}")
                    show_cause["Impacto"]=show_cause["Impacto R$"].map(lambda x:fmt_money(x))
                    show_cause=show_cause.drop(columns=["Impacto R$"])
                    st.dataframe(show_cause,use_container_width=True,hide_index=True,height=285)

        elif drill_kpi=="Refugo":
            qprod=ae.quality_product_drilldown(ACTIVE_DATA,selected_line)
            if qprod.empty:
                st.info("Sem granularidade de produto na Qualidade para este recorte.")
            else:
                st.caption("Para Refugo, o caminho correto disponível na base atual é KPI → Linha → Produto. Máquina/causa de qualidade só será afirmada quando essa dimensão existir na fonte.")
                qshow=qprod.copy()
                qshow["Taxa Refugo"]=qshow["Taxa Refugo"].map(lambda x:f"{x:.1%}")
                st.dataframe(qshow,use_container_width=True,hide_index=True,height=300)

        elif drill_kpi=="Horas extras":
            if ACTIVE_DATA and "pessoas" in ACTIVE_DATA:
                pe=ACTIVE_DATA["pessoas"].copy()
                if not pe.empty and "horas_extras" in pe.columns:
                    pe["horas_extras"]=pd.to_numeric(pe["horas_extras"],errors="coerce").fillna(0)
                    dims=["linha"] if "linha" in pe.columns else []
                    if "turno" in pe.columns:
                        dims.append("turno")
                    if dims:
                        pshow=pe.groupby(dims,as_index=False)["horas_extras"].sum().sort_values("horas_extras",ascending=False)
                        pshow=pshow.rename(columns={"linha":"Linha","turno":"Turno","horas_extras":"Horas extras"})
                        st.dataframe(pshow,use_container_width=True,hide_index=True,height=300)
                    else:
                        st.info("A base de Pessoas não possui Linha/Turno para drill-down.")
                else:
                    st.info("Sem dados de horas extras no recorte.")
            else:
                st.info("Drill-down de Pessoas disponível após importação.")

        elif drill_kpi=="Custo/unidade":
            if ACTIVE_DATA and "custos" in ACTIVE_DATA:
                cc=ACTIVE_DATA["custos"].copy()
                if not cc.empty:
                    cost_cols=[c for c in ["custo_mp","custo_mod","custo_energia","custo_manutencao","custo_frete","ggf_outros","custo_fixo"] if c in cc.columns]
                    for col in cost_cols+["receita"]:
                        if col in cc.columns:
                            cc[col]=pd.to_numeric(cc[col],errors="coerce").fillna(0)
                    dims=[c for c in ["linha","produto"] if c in cc.columns]
                    if dims and cost_cols:
                        cc["_custo"]=cc[cost_cols].sum(axis=1)
                        cshow=cc.groupby(dims,as_index=False).agg(Custo=("_custo","sum"),Receita=("receita","sum"))
                        cshow["Custo / Receita"]=cshow.apply(lambda r:safe_div(r["Custo"],r["Receita"]),axis=1)
                        cshow=cshow.sort_values("Custo / Receita",ascending=False)
                        cshow["Custo"]=cshow["Custo"].map(lambda x:fmt_money(x))
                        cshow["Receita"]=cshow["Receita"].map(lambda x:fmt_money(x))
                        cshow["Custo / Receita"]=cshow["Custo / Receita"].map(lambda x:f"{x:.1%}")
                        st.dataframe(cshow,use_container_width=True,hide_index=True,height=300)
                    else:
                        st.info("Custos não possuem granularidade de Linha/Produto suficiente.")
                else:
                    st.info("Sem custos no recorte.")
            else:
                st.info("Drill-down de custos disponível após importação.")

    st.write("")
    with st.expander("Cobertura dos filtros no modelo de dados"):
        coverage=st.session_state.get("analytics_filter_meta",{}).get("coverage")
        if isinstance(coverage,pd.DataFrame) and not coverage.empty:
            st.dataframe(coverage,use_container_width=True,hide_index=True)
        else:
            st.caption("Carregue dados reais para visualizar a cobertura dimensional de cada entidade.")

    st.write("")
    st.dataframe(lp, use_container_width=True, hide_index=True)

elif page == "Diagnóstico e Causas":
    page_header("Diagnóstico e Causas","Raio-X da performance: desvio, causa, impacto financeiro e ação.")

    diag=D["diagnostic"].copy()
    causes=D["causes"].copy()
    engine=ae.performance_engine(ACTIVE_DATA,D,st.session_state.get("analytics_filter_meta"))
    worst=D["line_perf"].sort_values("OEE").iloc[0] if not D["line_perf"].empty else None
    top_lever=diag.iloc[0] if not diag.empty else None
    top_cause=causes.iloc[0] if not causes.empty else None

    # Executive X-ray
    c1,c2,c3,c4=st.columns(4,gap="small")
    c1.metric("Saúde Geral",f"{D['health_score']:.0f}/100",f"Financeira {D['financial_health']:.0f}/100")
    c2.metric("Maior Alavanca",top_lever["Alavanca"] if top_lever is not None else "—",
              fmt_money(top_lever["Impacto_R$"]) if top_lever is not None else "")
    c3.metric("Linha Crítica",worst["Linha"] if worst is not None else "—",
              f"OEE {fmt_pct(worst['OEE'])}" if worst is not None else "")
    c4.metric("Causa Dominante",top_cause["Causa"] if top_cause is not None else "—",
              f"{top_cause['Horas']:.0f} h" if top_cause is not None else "")

    st.write("")
    with st.container(border=True):
        panel_title("Conclusão Executiva","Leitura automática dos principais sinais do período")
        st.markdown(f"<div style='font-size:.76rem;line-height:1.6;color:#34465C'>{D['diagnostic_conclusion']}</div>",unsafe_allow_html=True)
        if D.get("standards_missing"):
            st.warning("Há produtos sem padrão cadastrado: " + ", ".join(D["standards_missing"]) + ". A eficiência MOD não deve ser usada até completar o cadastro.")

    st.write("")
    with st.container(border=True):
        panel_title("Performance Engine","Desvio → local → causa/evidência → impacto financeiro → alavanca → ação")
        if engine.empty:
            st.success("Nenhum desvio material foi identificado pelas regras determinísticas no recorte atual.")
        else:
            c1,c2,c3,c4=st.columns(4,gap="small")
            top_engine=engine.iloc[0]
            c1.metric("Desvios ativos",len(engine))
            c2.metric("Maior impacto",fmt_money(float(top_engine["Impacto_R$"])))
            c3.metric("KPI prioritário",str(top_engine["KPI"]))
            c4.metric("Confiança",str(top_engine["Confiança"]))

            st.write("")
            view_engine=engine.copy()
            view_engine["Impacto"]=view_engine["Impacto_R$"].map(lambda x:fmt_money(x))
            view_engine=view_engine[[
                "KPI","Desvio","Local","Causa / hipótese","Evidência",
                "Alavanca","Ação recomendada","Impacto","Confiança","Fonte"
            ]]
            st.dataframe(
                view_engine,use_container_width=True,hide_index=True,height=min(390,90+55*len(view_engine)),
                column_config={
                    "KPI":st.column_config.TextColumn("KPI",width="small"),
                    "Desvio":st.column_config.TextColumn("Desvio",width="small"),
                    "Local":st.column_config.TextColumn("Onde",width="medium"),
                    "Causa / hipótese":st.column_config.TextColumn("Causa / hipótese",width="medium"),
                    "Evidência":st.column_config.TextColumn("Evidência",width="large"),
                    "Alavanca":st.column_config.TextColumn("Alavanca",width="medium"),
                    "Ação recomendada":st.column_config.TextColumn("Ação recomendada",width="large"),
                    "Impacto":st.column_config.TextColumn("Impacto",width="medium"),
                    "Confiança":st.column_config.TextColumn("Confiança",width="small"),
                    "Fonte":st.column_config.TextColumn("Fonte",width="medium"),
                }
            )
            st.caption("O motor só afirma causa específica quando existe evidência na base. Quando a granularidade não existe, a coluna é tratada explicitamente como hipótese ou lacuna de dados.")

    st.write("")
    c1,c2=st.columns([1.10,.90],gap="small")

    with c1:
        with st.container(border=True, height=430):
            panel_title("Matriz Esforço x Resultado","Priorize impacto financeiro alto com menor esforço")
            if not diag.empty:
                plot=diag.sort_values("Indice_Prioridade",ascending=False).copy()
                labels=[str(v) if i < 6 else "" for i,v in enumerate(plot["Alavanca"].tolist())]
                colors_plot=[GREEN if p=="Prioridade 1" else ORANGE if p=="Prioridade 2" else "#AAB7C4" for p in plot["Prioridade"]]
                med=float(plot["Impacto_R$"].median())
                fig=go.Figure(go.Scatter(
                    x=plot["Esforco"], y=plot["Impacto_R$"],
                    mode="markers+text",
                    text=labels,
                    textposition=["top center","bottom center","top right","bottom left","top left","bottom right"] + ["top center"]*max(0,len(plot)-6),
                    textfont=dict(size=10,color=TEXT),
                    marker=dict(
                        size=np.clip(plot["Resultado_0a100"]/2+18,18,50),
                        color=colors_plot, opacity=.86,
                        line=dict(width=1.5,color="white")
                    ),
                    customdata=np.stack([plot["Horizonte_dias"],plot["Responsavel"],plot["Prioridade"],plot["Impacto_R$"]],axis=-1),
                    hovertemplate="<b>%{text}</b><br>Esforço: %{x}/5<br>Impacto: R$ %{customdata[3]:,.0f}<br>Horizonte: %{customdata[0]} dias<br>%{customdata[2]}<extra></extra>",
                    cliponaxis=False
                ))
                fig.add_vline(x=3,line_dash="dot",line_color="#C8D4DE",line_width=1)
                fig.add_hline(y=med,line_dash="dot",line_color="#C8D4DE",line_width=1)
                fig.add_annotation(x=1.1,y=max(plot["Impacto_R$"])*1.08,text="<b>QUICK WINS</b>",showarrow=False,font=dict(size=9,color=GREEN))
                fig.update_xaxes(range=[0.6,5.4],dtick=1,title="Esforço (1 = baixo | 5 = alto)",gridcolor="#EFF3F7",automargin=True)
                fig.update_yaxes(range=[0,max(plot["Impacto_R$"])*1.22],title="Impacto potencial (R$)",gridcolor="#EFF3F7",tickformat=",.0f",automargin=True)
                fig.update_layout(height=350,margin=dict(l=15,r=25,t=30,b=45),
                                  paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                                  showlegend=False)
                st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

    with c2:
        with st.container(border=True, height=430):
            panel_title("Prioridades Recomendadas","Ranking por impacto financeiro versus esforço")
            show=diag.head(7)[["Alavanca","Impacto_R$","Esforco","Horizonte_dias","Prioridade"]].copy()
            show["Impacto"]=show["Impacto_R$"].map(lambda x:fmt_money(x))
            show=show.drop(columns=["Impacto_R$"])
            st.dataframe(
                show,use_container_width=True,hide_index=True,height=350,
                column_config={
                    "Alavanca":st.column_config.TextColumn("Alavanca",width="medium"),
                    "Esforco":st.column_config.NumberColumn("Esforço",format="%d/5",width="small"),
                    "Horizonte_dias":st.column_config.NumberColumn("Horizonte",format="%d dias",width="small"),
                    "Prioridade":st.column_config.TextColumn("Prioridade",width="medium"),
                    "Impacto":st.column_config.TextColumn("Impacto",width="medium"),
                }
            )

    st.write("")
    c1,c2=st.columns(2,gap="small")
    with c1:
        with st.container(border=True, height=390):
            panel_title("Pareto de Causas","Horas perdidas e concentração")
            if not causes.empty:
                df=causes.sort_values("Horas")
                fig=go.Figure(go.Bar(
                    x=df["Horas"],y=df["Causa"],orientation="h",
                    marker_color=BLUE,
                    text=[f"{x:.0f} h" for x in df["Horas"]],textposition="outside",
                    cliponaxis=False
                ))
                xmax=max(df["Horas"])*1.22
                fig.update_layout(height=320,margin=dict(l=5,r=55,t=8,b=10),
                                  paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                                  xaxis=dict(showgrid=False,showticklabels=False,range=[0,xmax]),
                                  yaxis=dict(showgrid=False,automargin=True,tickfont=dict(size=10,color=TEXT)),
                                  showlegend=False)
                st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

    with c2:
        with st.container(border=True, height=390):
            panel_title("Impacto Financeiro","Buckets sem dupla contagem")
            imp=D["impacts"].sort_values("R$")
            fig=go.Figure(go.Bar(
                x=imp["R$"],y=imp["Impacto"],orientation="h",
                marker_color="#E85B55",
                text=[fmt_money(v,0) for v in imp["R$"]],textposition="outside",
                cliponaxis=False
            ))
            xmax=max(imp["R$"])*1.34 if len(imp) else 1
            fig.update_layout(height=275,margin=dict(l=5,r=110,t=8,b=0),
                              paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                              xaxis=dict(showgrid=False,showticklabels=False,range=[0,xmax]),
                              yaxis=dict(showgrid=False,automargin=True,tickfont=dict(size=10,color=TEXT)),
                              showlegend=False)
            st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
            with st.expander("Racional do impacto financeiro"):
                st.caption("Volume perdido é valorizado pela margem industrial unitária; refugo considera custo consumido nas unidades perdidas; eficiência MOD considera HH reais acima das HH padrão ganhas; horas extras consideram custo incremental; custo/consumo compara real versus referência. Causa e efeito não são somados duas vezes.")

    st.write("")
    with st.container(border=True):
        panel_title("Plano de Ações Proposto","Ações sugeridas a partir das alavancas priorizadas")
        actions_view=diag.head(6)[["Prioridade","Alavanca","Acao","Responsavel","Horizonte_dias","Impacto_R$"]].copy()
        actions_view["Impacto esperado"]=actions_view["Impacto_R$"].map(lambda x:fmt_money(x))
        actions_view=actions_view.drop(columns=["Impacto_R$"])
        actions_view=actions_view.rename(columns={"Acao":"Ação proposta","Responsavel":"Responsável","Horizonte_dias":"Horizonte"})
        st.dataframe(
            actions_view,use_container_width=True,hide_index=True,height=280,
            column_config={
                "Prioridade":st.column_config.TextColumn("Prioridade",width="small"),
                "Alavanca":st.column_config.TextColumn("Alavanca",width="medium"),
                "Ação proposta":st.column_config.TextColumn("Ação proposta",width="large"),
                "Responsável":st.column_config.TextColumn("Responsável",width="medium"),
                "Horizonte":st.column_config.NumberColumn("Horizonte",format="%d dias",width="small"),
                "Impacto esperado":st.column_config.TextColumn("Impacto",width="medium"),
            }
        )

    st.write("")
    c1,c2,c3=st.columns([1,.30,.32])
    with c1:
        st.caption("A matriz usa o esforço configurado em Parametros_Diagnostico. O impacto será calibrado por cliente/planta com histórico real.")
    with c2:
        pdf_bytes=build_diagnostic_pdf(D,diag,causes)
        st.download_button(
            "Baixar relatório PDF",data=pdf_bytes,
            file_name="Relatorio_Diagnostico_Industrial_Performance.pdf",
            mime="application/pdf",use_container_width=True
        )
    with c3:
        if st.button("Adicionar Top 3 ao Plano",type="primary",use_container_width=True):
            rows=[]
            for _,r in diag.head(3).iterrows():
                rows.append([
                    "Alta" if r["Prioridade"]=="Prioridade 1" else "Média",
                    r["Alavanca"],r["Acao"],r["Responsavel"],owner_email(r["Responsavel"]),
                    f"{int(r['Horizonte_dias'])} dias",fmt_money(r["Impacto_R$"]),"Planejado"
                ])
            new=pd.DataFrame(rows,columns=st.session_state.actions.columns)
            st.session_state.actions=pd.concat([st.session_state.actions,new],ignore_index=True)
            nav("Plano de Ação")


elif page == "Finanças / DRE":
    page_header("Finanças / DRE","DRE gerencial industrial: receita, insumos, MOD, GGF, estrutura, despesas e EBITDA.")

    ggf_total=float(D.get("cost_freight",0))+float(D.get("cost_energy",0))+float(D.get("cost_maintenance",0))+float(D.get("cost_contracts",0))+float(D.get("cost_ggf_other",0))
    c1,c2,c3,c4,c5 = st.columns(5, gap="small")
    c1.metric("Receita Líquida", fmt_money(D["revenue"]))
    c2.metric("Margem Industrial", fmt_pct(D["margin"]))
    c3.metric("EBITDA", fmt_money(D["ebitda"]))
    c4.metric("GGF", fmt_money(ggf_total))
    c5.metric("Despesas", fmt_money(D.get("expenses_total",0)))

    st.write("")
    c1, c2 = st.columns([1.22,.78], gap="small")
    with c1:
        with st.container(border=True):
            panel_title("DRE Gerencial","Frete classificado em GGF; despesas segregadas do custo industrial.")
            view = D["dre"].copy()
            view["Realizado"] = view["Realizado"].map(lambda x: fmt_money(x))
            st.dataframe(
                view, use_container_width=True, hide_index=True, height=585,
                column_config={
                    "Linha":st.column_config.TextColumn("DRE Gerencial",width="large"),
                    "Realizado":st.column_config.TextColumn("Realizado",width="medium"),
                }
            )
    with c2:
        with st.container(border=True):
            panel_title("Composição do Custo","Insumos, mão de obra, GGF, estrutura e despesas")
            vals={
                "Insumos / MP":float(D.get("cost_mp",0)),
                "MOD":float(D.get("cost_mod",0)),
                "GGF":ggf_total,
                "Custos Fixos Industriais":float(D.get("fixed_industrial",0)),
                "Despesas":float(D.get("expenses_total",0)),
            }
            vals={k:v for k,v in vals.items() if v>0}
            fig = go.Figure(go.Pie(
                labels=list(vals.keys()), values=list(vals.values()), hole=.68,
                textinfo="percent", textfont=dict(size=10)
            ))
            fig.update_layout(
                height=325, margin=dict(l=0,r=0,t=0,b=15),
                legend=dict(orientation="h",y=-.08,font=dict(size=9)),
                paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

            st.markdown(
                f"<div class='lever-shell'>"
                f"<div class='lever-kicker'>GGF — GASTOS GERAIS DE FABRICAÇÃO</div>"
                f"<div class='lever-title'>Frete {fmt_money(D.get('cost_freight',0))}</div>"
                f"<div class='lever-meta'>Energia {fmt_money(D.get('cost_energy',0))} · "
                f"Manutenção {fmt_money(D.get('cost_maintenance',0))} · "
                f"Contratos {fmt_money(D.get('cost_contracts',0))} · "
                f"Outros {fmt_money(D.get('cost_ggf_other',0))}</div></div>",
                unsafe_allow_html=True
            )
            st.write("")
            st.markdown(
                "<div class='frontend-note'><b>Regra gerencial:</b> o frete está em GGF. "
                "Despesas administrativas, comerciais e logísticas ficam separadas. "
                "A camada de dados mantém a classificação para que uma conta possa ser reclassificada sem alterar o motor.</div>",
                unsafe_allow_html=True
            )

    st.write("")
    c1,c2,c3,c4=st.columns(4,gap="small")
    c1.metric("GGF — Frete",fmt_money(D.get("cost_freight",0)))
    c2.metric("Custos Fixos Industriais",fmt_money(D.get("fixed_industrial",0)))
    c3.metric("Desp. Administrativas",fmt_money(D.get("exp_admin",0)))
    c4.metric("Desp. Comerciais + Logísticas",fmt_money(D.get("exp_commercial",0)+D.get("exp_logistics",0)))


elif page == "Alavancas de Valor":
    page_header("Alavancas de Valor","Simule as 26 alavancas por valor atual → valor meta e veja o efeito na DRE gerencial.")

    B=simulator_baselines(D)

    target_defaults={
        "oee":78.0,
        "availability":82.0,
        "performance":97.0,
        "capacity":80.0,
        "scrap":2.5,
        "rework":2.0,
        "setup":35.0,
        "unplanned_hours":max(0.0,B["unplanned_hours"]*0.80),
        "mttr":70.0,
        "overtime_hours":max(0.0,B["overtime_hours"]*0.75),
        "productivity":20.0 if B["productivity"]<20 else B["productivity"]*1.05,
        "headcount":B["headcount"],
        "mp_specific":1.0 if B["mp_specific_unit"]=="índice" else B["mp_specific"]*0.96,
        "mp_price":0.97 if B["mp_price_unit"]=="índice" else B["mp_price"]*0.97,
        "material_loss_pct":max(0.0,B["material_loss_pct"]*0.85),
        "energy_intensity":B["energy_intensity"]*0.92,
        "freight_per_unit":B["freight_per_unit"]*0.95,
        "otif":95.0,
        "price_per_unit":B["price_per_unit"]*1.02,
        "mix_pp":1.0,
        "volume_units":B["volume_units"]*1.05,
        "fixed_industrial":B["fixed_industrial"]*0.95,
        "contracts_services":B["contracts_services"]*0.90,
        "inventory_days":max(0.0,B["inventory_days"]-10),
        "dpo_days":B["dpo_days"]+5,
        "dso_days":max(0.0,B["dso_days"]-5),
    }

    lever_names=[
        "oee","availability","performance","capacity","scrap","rework","setup","unplanned_hours","mttr",
        "overtime_hours","productivity","headcount","mp_specific","mp_price","material_loss_pct",
        "energy_intensity","freight_per_unit","otif","price_per_unit","mix_pp","volume_units",
        "fixed_industrial","contracts_services","inventory_days","dpo_days","dso_days"
    ]
    for name in lever_names:
        key=f"simt_{name}"
        if key not in st.session_state:
            st.session_state[key]=float(target_defaults[name])

    if "sim_prod_mode" not in st.session_state:
        st.session_state.sim_prod_mode="OEE direto"
    if "sim_group" not in st.session_state:
        st.session_state.sim_group="Produção"

    with st.container(border=True):
        c1,c2,c3=st.columns([1,.34,.34],gap="small")
        with c1:
            st.markdown(
                "<div class='sim-header'><div>"
                "<div class='sim-header-title'>Simulador Atual → Meta</div>"
                "<div class='sim-header-sub'>O usuário informa onde quer chegar; o motor calcula variação, dependências e impacto financeiro.</div>"
                "</div><div><span class='sim-scope-chip'>26 ALAVANCAS · DRE GERENCIAL</span></div></div>",
                unsafe_allow_html=True
            )
        with c2:
            if st.button("Cenário exemplo",use_container_width=True):
                for name in lever_names:
                    st.session_state[f"simt_{name}"]=float(target_defaults[name])
                st.rerun()
        with c3:
            if st.button("Resetar para atual",use_container_width=True):
                for name in lever_names:
                    st.session_state[f"simt_{name}"]=float(B[name])
                st.rerun()

    def target_input(label,name,current,unit="",step=0.1,min_value=0.0,max_value=None,fmt="%.2f",help_text=None):
        kwargs={"label":label,"key":f"simt_{name}","step":float(step),"format":fmt}
        if min_value is not None:
            kwargs["min_value"]=float(min_value)
        if max_value is not None:
            kwargs["max_value"]=float(max_value)
        if help_text:
            kwargs["help"]=help_text
        st.number_input(**kwargs)
        target=float(st.session_state[f"simt_{name}"])
        delta=target-current
        if unit=="%":
            d=f"{delta:+.1f} pp"
            current_txt=f"{current:.1f}%"
            target_txt=f"{target:.1f}%"
        elif unit=="R$":
            d=fmt_money(delta,2)
            current_txt=fmt_money(current,2)
            target_txt=fmt_money(target,2)
        elif unit=="R$/un":
            d=f"R$ {delta:+,.2f}".replace(",",".")
            current_txt=f"R$ {current:,.2f}".replace(",",".")
            target_txt=f"R$ {target:,.2f}".replace(",",".")
        else:
            d=f"{delta:+,.2f}".replace(",",".")
            current_txt=f"{current:,.2f}".replace(",",".")
            target_txt=f"{target:,.2f}".replace(",",".")
            if unit:
                current_txt+=f" {unit}"
                target_txt+=f" {unit}"
                d+=f" {unit}"
        st.caption(f"Atual {current_txt} → Meta {target_txt} · Δ {d}")
        return target

    left,right=st.columns([1.32,.68],gap="small")
    with left:
        with st.container(border=True):
            top1,top2=st.columns([.58,.42],gap="small")
            groups=["Produção","Qualidade","Processo","Pessoas","Materiais","Energia","Logística","Financeiro","Estrutura","Capital"]
            with top1:
                group=st.selectbox("Grupo de alavancas",groups,key="sim_group")
            with top2:
                prod_mode=st.radio(
                    "Motor de Produção",["OEE direto","Drivers de OEE"],
                    horizontal=True,key="sim_prod_mode",
                    help="OEE direto usa a meta de OEE. Drivers recalcula OEE com disponibilidade e performance. Os caminhos não são somados."
                )
            st.markdown("---")

            if group=="Produção":
                st.markdown("<div class='lever-kicker'>PRODUÇÃO</div><div class='lever-title'>Capacidade e eficiência — sempre Atual → Meta</div>",unsafe_allow_html=True)
                a,b=st.columns(2,gap="medium")
                with a:
                    target_input("Meta simulada — OEE","oee",B["oee"],"%",.5,20,100,"%.1f")
                    target_input("Meta simulada — Disponibilidade","availability",B["availability"],"%",.5,20,100,"%.1f")
                with b:
                    target_input("Meta simulada — Performance","performance",B["performance"],"%",.5,20,105,"%.1f")
                    target_input("Meta simulada — Capacidade utilizada","capacity",B["capacity"],"%",.5,1,100,"%.1f")
                st.markdown("<div class='frontend-note'>No modo OEE direto, a meta de OEE define a capacidade potencial. No modo Drivers, disponibilidade e performance formam o OEE. Capacidade habilitada só vira EBITDA quando o volume é vendido.</div>",unsafe_allow_html=True)

            elif group=="Qualidade":
                st.markdown("<div class='lever-kicker'>QUALIDADE</div><div class='lever-title'>Yield, desperdício e retrabalho</div>",unsafe_allow_html=True)
                a,b=st.columns(2,gap="medium")
                with a:
                    target_input("Meta simulada — Refugo","scrap",B["scrap"],"%",.1,0,30,"%.1f")
                with b:
                    target_input("Meta simulada — Retrabalho","rework",B["rework"],"%",.1,0,30,"%.1f")
                st.markdown("<div class='frontend-note'>Refugo atua no consumo de insumos; retrabalho atua em MOD e energia. Os efeitos são encadeados para reduzir dupla contagem.</div>",unsafe_allow_html=True)

            elif group=="Processo":
                st.markdown("<div class='lever-kicker'>PROCESSO</div><div class='lever-title'>Tempo disponível e confiabilidade</div>",unsafe_allow_html=True)
                a,b=st.columns(2,gap="medium")
                with a:
                    target_input("Meta simulada — Setup médio","setup",B["setup"],"min",1,0,max(240,B["setup"]*2),"%.0f")
                    target_input("Meta simulada — MTTR","mttr",B["mttr"],"min",1,0,max(300,B["mttr"]*2),"%.0f")
                with b:
                    target_input("Meta simulada — Paradas não planejadas","unplanned_hours",B["unplanned_hours"],"h",1,0,max(1,B["unplanned_hours"]*2),"%.0f")
                    st.markdown("<div class='frontend-note'>Setup, paradas e MTTR são drivers de disponibilidade. Eles habilitam capacidade e não são somados novamente como EBITDA se o volume já monetiza essa capacidade.</div>",unsafe_allow_html=True)

            elif group=="Pessoas":
                st.markdown("<div class='lever-kicker'>PESSOAS</div><div class='lever-title'>Horas, produtividade e dimensionamento</div>",unsafe_allow_html=True)
                a,b=st.columns(2,gap="medium")
                with a:
                    target_input("Meta simulada — Horas extras","overtime_hours",B["overtime_hours"],"h",10,0,max(100,B["overtime_hours"]*2),"%.0f")
                    target_input("Meta simulada — Produtividade","productivity",B["productivity"],"un/h eq.",.1,.1,max(50,B["productivity"]*2),"%.1f",
                                 "No consolidado multiproduto o ganho deve ser linearizado por HH padrão.")
                with b:
                    target_input("Meta simulada — Headcount","headcount",B["headcount"],"pessoas",1,0,max(10,B["headcount"]*2),"%.0f")
                    st.markdown("<div class='frontend-note'>Hora extra usa o custo/hora real da MOD e somente o adicional configurado. Headcount é tratado como driver da estrutura; se Custo Fixo também for alterado, o motor evita somar os dois.</div>",unsafe_allow_html=True)

            elif group=="Materiais":
                st.markdown("<div class='lever-kicker'>MATERIAIS</div><div class='lever-title'>Consumo, preço e perdas de insumos</div>",unsafe_allow_html=True)
                a,b=st.columns(2,gap="medium")
                with a:
                    target_input(f"Meta simulada — Consumo específico MP ({B['mp_specific_unit']})","mp_specific",B["mp_specific"],B["mp_specific_unit"],.01,0,max(B["mp_specific"]*2,2),"%.3f")
                    target_input("Meta simulada — Perdas de material","material_loss_pct",B["material_loss_pct"],"%",.1,0,30,"%.1f")
                with b:
                    target_input(f"Meta simulada — Preço de MP ({B['mp_price_unit']})","mp_price",B["mp_price"],B["mp_price_unit"],.01,0,max(B["mp_price"]*2,2),"%.3f")
                    st.markdown("<div class='frontend-note'>Quando a base trouxer kg e R$/kg, o simulador usa valores físicos. Se não houver, trabalha com índice 1,00 até o DE/PARA receber os dados reais.</div>",unsafe_allow_html=True)

            elif group=="Energia":
                st.markdown("<div class='lever-kicker'>ENERGIA</div><div class='lever-title'>Intensidade energética da operação</div>",unsafe_allow_html=True)
                target_input(f"Meta simulada — kWh/unidade ({B['energy_unit']})","energy_intensity",B["energy_intensity"],B["energy_unit"],.01,0,max(B["energy_intensity"]*2,2),"%.3f")
                st.markdown("<div class='frontend-note'>O custo de energia acompanha o volume e a intensidade energética simulada. Retrabalho também afeta o consumo.</div>",unsafe_allow_html=True)

            elif group=="Logística":
                st.markdown("<div class='lever-kicker'>LOGÍSTICA</div><div class='lever-title'>Frete em GGF e proteção de receita</div>",unsafe_allow_html=True)
                a,b=st.columns(2,gap="medium")
                with a:
                    target_input("Meta simulada — Frete/unidade","freight_per_unit",B["freight_per_unit"],"R$/un",.01,0,max(1,B["freight_per_unit"]*3),"%.2f")
                with b:
                    target_input("Meta simulada — OTIF","otif",B["otif"],"%",.5,0,100,"%.1f")
                st.markdown("<div class='frontend-note'><b>Frete:</b> entra em GGF na DRE Gerencial. <b>OTIF:</b> gera receita protegida / risco evitado e não é somado automaticamente à receita ou ao EBITDA.</div>",unsafe_allow_html=True)

            elif group=="Financeiro":
                st.markdown("<div class='lever-kicker'>FINANCEIRO</div><div class='lever-title'>Preço, mix e volume — cálculo encadeado</div>",unsafe_allow_html=True)
                a,b=st.columns(2,gap="medium")
                with a:
                    target_input("Meta simulada — Preço médio líquido","price_per_unit",B["price_per_unit"],"R$/un",.1,0,max(B["price_per_unit"]*3,1),"%.2f")
                    target_input("Meta simulada — Volume vendido","volume_units",B["volume_units"],"un",100,0,max(B["volume_units"]*3,1000),"%.0f")
                with b:
                    target_input("Meta simulada — Efeito de mix na margem","mix_pp",B["mix_pp"],"pp",.1,-20,20,"%.1f")
                    st.markdown("<div class='frontend-note'><b>Regra:</b> Receita simulada = Volume simulado × Preço simulado. O efeito de preço incide sobre o volume do cenário, eliminando o erro de somar percentuais independentes sobre a mesma receita base.</div>",unsafe_allow_html=True)

            elif group=="Estrutura":
                st.markdown("<div class='lever-kicker'>ESTRUTURA</div><div class='lever-title'>Custos estruturais em valor absoluto</div>",unsafe_allow_html=True)
                a,b=st.columns(2,gap="medium")
                with a:
                    target_input("Meta simulada — Custos Fixos Industriais","fixed_industrial",B["fixed_industrial"],"R$",1000,0,max(B["fixed_industrial"]*3,1000),"%.0f")
                with b:
                    target_input("Meta simulada — GGF Contratos/Serviços","contracts_services",B["contracts_services"],"R$",1000,0,max(B["contracts_services"]*3,1000),"%.0f")
                st.markdown("<div class='frontend-note'>Contratos/serviços ficam dentro de GGF. Custo fixo industrial é uma linha separada da DRE. Headcount não é somado duas vezes se a meta de custo fixo já incorporar esse efeito.</div>",unsafe_allow_html=True)

            elif group=="Capital":
                st.markdown("<div class='lever-kicker'>CAPITAL</div><div class='lever-title'>Dias de capital de giro</div>",unsafe_allow_html=True)
                a,b=st.columns(2,gap="medium")
                with a:
                    target_input("Meta simulada — Estoque","inventory_days",B["inventory_days"],"dias",1,0,365,"%.0f")
                    target_input("Meta simulada — Prazo cliente","dso_days",B["dso_days"],"dias",1,0,365,"%.0f")
                with b:
                    target_input("Meta simulada — Prazo fornecedor","dpo_days",B["dpo_days"],"dias",1,0,365,"%.0f")
                    st.markdown("<div class='frontend-note'>Capital de giro é calculado em caixa e permanece fora do EBITDA.</div>",unsafe_allow_html=True)

    targets={name:float(st.session_state[f"simt_{name}"]) for name in lever_names}
    R=calculate_simulator_scenario(D,targets,st.session_state.sim_prod_mode)

    active_count=sum(1 for name in lever_names if abs(targets[name]-float(B[name]))>1e-8)

    with right:
        with st.container(border=True):
            panel_title("Impacto do Cenário",f"{active_count} alavancas alteradas em relação ao atual")
            c1,c2=st.columns(2,gap="small")
            with c1:
                st.markdown(
                    f"<div class='sim-card'><div class='sim-card-label'>Receita simulada</div>"
                    f"<div class='sim-card-value'>{fmt_money(R['simulated_revenue'])}</div>"
                    f"<div class='sim-card-delta' style='color:{GREEN if R['revenue_gain']>=0 else RED}'>Δ {fmt_money(R['revenue_gain'])}</div></div>",
                    unsafe_allow_html=True
                )
            with c2:
                st.markdown(
                    f"<div class='sim-card'><div class='sim-card-label'>EBITDA simulado</div>"
                    f"<div class='sim-card-value'>{fmt_money(R['simulated_ebitda'])}</div>"
                    f"<div class='sim-card-delta' style='color:{GREEN if R['ebitda_gain']>=0 else RED}'>Δ {fmt_money(R['ebitda_gain'])}</div></div>",
                    unsafe_allow_html=True
                )
            st.write("")
            c1,c2=st.columns(2,gap="small")
            with c1:
                st.markdown(
                    f"<div class='sim-card'><div class='sim-card-label'>Margem Industrial</div>"
                    f"<div class='sim-card-value'>{fmt_pct(R['simulated_margin'])}</div>"
                    f"<div class='sim-card-delta' style='color:{GREEN if R['simulated_margin']>=D['margin'] else RED}'>base {fmt_pct(D['margin'])}</div></div>",
                    unsafe_allow_html=True
                )
            with c2:
                st.markdown(
                    f"<div class='sim-card'><div class='sim-card-label'>Capital de giro</div>"
                    f"<div class='sim-card-value'>{fmt_money(R['working_capital_release'])}</div>"
                    f"<div class='sim-card-delta' style='color:{BLUE}'>efeito caixa, fora EBITDA</div></div>",
                    unsafe_allow_html=True
                )
            st.write("")
            st.markdown(
                f"<div class='lever-shell'><div class='lever-kicker'>OTIF</div>"
                f"<div class='lever-title'>{'Receita protegida' if R['otif_protected_value']>=0 else 'Receita adicional em risco'}: {fmt_money(abs(R['otif_protected_value']))}</div>"
                f"<div class='lever-meta'>Não entra automaticamente na Receita simulada ou EBITDA. Confiança: Média.</div></div>",
                unsafe_allow_html=True
            )
            st.write("")
            volume_note=""
            if R["requested_volume"]>R["realized_volume"]+1:
                volume_note=f" · demanda solicitada limitada pela capacidade a {R['realized_volume']:,.0f} un".replace(",",".")
            st.markdown(
                f"<div class='lever-shell'><div class='lever-kicker'>CAPACIDADE</div>"
                f"<div class='lever-title'>Valor potencial habilitado: {fmt_money(R['capacity_value'])}</div>"
                f"<div class='lever-meta'>OEE efetivo {R['effective_oee']:.1%} · potencial {R['potential_units']:,.0f} un{volume_note}. "
                f"Capacidade não é somada novamente ao EBITDA.</div></div>".replace(",","."),
                unsafe_allow_html=True
            )

    st.write("")
    c1,c2=st.columns([1.08,.92],gap="small")
    with c1:
        with st.container(border=True):
            panel_title("Bridge de EBITDA","Reconciliado com a DRE simulada")
            bridge=R["bridge"]
            if bridge:
                x=["EBITDA Atual"]+list(bridge.keys())+["EBITDA Simulado"]
                measures=["absolute"]+["relative"]*len(bridge)+["total"]
                y=[D["ebitda"]]+list(bridge.values())+[0]
                fig=go.Figure(go.Waterfall(
                    x=x,measure=measures,y=y,
                    increasing={"marker":{"color":GREEN}},
                    decreasing={"marker":{"color":RED}},
                    totals={"marker":{"color":BLUE}},
                    connector={"line":{"color":"#BBC8D3","width":1}}
                ))
                fig.update_layout(
                    height=385,margin=dict(l=5,r=5,t=10,b=80),
                    paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                    yaxis=dict(gridcolor="#EFF3F7",tickfont=dict(size=9)),
                    xaxis=dict(tickfont=dict(size=9),tickangle=-25,automargin=True),
                    showlegend=False
                )
                st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
            else:
                st.info("O cenário está igual ao atual.")

    with c2:
        with st.container(border=True):
            panel_title("Mapa de Valor","Impacto por alavanca e natureza do valor")
            show=R["breakdown"].copy()
            if not show.empty:
                show=show[show["Impacto_R$"].abs()>0.5].head(12)
                show["Impacto"]=show["Impacto_R$"].map(lambda x:fmt_money(x))
                show=show[["Alavanca","Tipo","Impacto","Confiança"]]
                st.dataframe(show,use_container_width=True,hide_index=True,height=385)
            else:
                st.info("Nenhuma alavanca alterada.")

    st.write("")
    with st.container(border=True):
        panel_title("DRE — Base x Simulado","O cenário conversa diretamente com a DRE Gerencial")
        dre_sim=R["simulated_dre"].copy()
        dre_sim["Δ"]=dre_sim["Simulado"]-dre_sim["Base"]
        for col in ["Base","Simulado","Δ"]:
            dre_sim[col]=dre_sim[col].map(lambda x:fmt_money(x))
        st.dataframe(dre_sim,use_container_width=True,hide_index=True,height=500)

    st.write("")
    with st.container(border=True):
        c1,c2=st.columns([1,.34],gap="small")
        with c1:
            st.markdown(
                "<div class='frontend-note'><b>Regras do motor:</b> preço e volume são encadeados; frete está em GGF; "
                "OTIF é receita protegida; custos e despesas vêm da DRE gerencial; OEE/capacidade são habilitadores; "
                "capital de giro fica fora do EBITDA; Atual → Meta é a única forma de entrada do cenário.</div>",
                unsafe_allow_html=True
            )
        with c2:
            if st.button("Transformar cenário em Plano de Captura",type="primary",use_container_width=True):
                bd=R["breakdown"].copy()
                if not bd.empty:
                    top_actions=bd[
                        (bd["Impacto_R$"]>1) &
                        (bd["Tipo"].str.contains("EBITDA|Valor habilitado|GGF",regex=True))
                    ].head(5)
                else:
                    top_actions=pd.DataFrame()

                owner_map={
                    "OEE":"Ger. Industrial","Disponibilidade":"Ger. Manutenção","Performance":"Ger. Produção",
                    "Capacidade utilizada":"Ger. Industrial","Setup médio":"Engenharia de Processos",
                    "Paradas não planejadas":"Ger. Manutenção","MTTR":"Ger. Manutenção",
                    "Refugo":"Ger. Qualidade","Retrabalho":"Ger. Qualidade",
                    "Horas extras":"Ger. Produção","Produtividade":"Ger. Produção","Headcount":"Ger. Industrial",
                    "Consumo específico MP":"Engenharia de Processos","Preço de MP":"Suprimentos",
                    "Perdas de material":"Ger. Qualidade","kWh/unidade":"Ger. Industrial",
                    "Frete/unidade":"Logística / Suprimentos","OTIF":"PCP / Logística",
                    "Preço médio":"Comercial / CFO","Mix de produtos":"Comercial / CFO",
                    "Volume vendido":"Comercial / Industrial","Custo fixo":"Diretor Industrial / CFO",
                    "Contratos/serviços":"Suprimentos / CFO"
                }
                action_map={
                    "OEE":"Executar plano para atingir a meta de OEE simulada.",
                    "Disponibilidade":"Atacar perdas de disponibilidade e equipamentos críticos.",
                    "Performance":"Eliminar perdas de velocidade e microparadas versus padrão.",
                    "Capacidade utilizada":"Converter capacidade disponível em volume vendável sem aumentar estrutura desnecessária.",
                    "Setup médio":"Aplicar SMED e preparação externa para atingir o setup meta.",
                    "Paradas não planejadas":"Reduzir horas de paradas não planejadas com plano de confiabilidade.",
                    "MTTR":"Reduzir tempo médio de reparo nas falhas críticas.",
                    "Refugo":"Atacar causas de refugo até a meta simulada.",
                    "Retrabalho":"Eliminar causas de retrabalho e estabilizar o processo.",
                    "Horas extras":"Redimensionar escala e gargalos para atingir a meta de horas extras.",
                    "Produtividade":"Rebalancear operação usando HH padrão e mix de produtos.",
                    "Headcount":"Redesenhar capacidade e estrutura para o headcount simulado.",
                    "Consumo específico MP":"Reduzir consumo real por unidade versus padrão.",
                    "Preço de MP":"Renegociar/compor sourcing para atingir o preço-meta de insumo.",
                    "Perdas de material":"Atacar perdas físicas fora do refugo de produto.",
                    "kWh/unidade":"Reduzir intensidade energética por unidade.",
                    "Frete/unidade":"Redesenhar malha/contratação para atingir o frete por unidade meta.",
                    "Preço médio":"Executar estratégia comercial compatível com o preço médio meta.",
                    "Mix de produtos":"Alterar mix para capturar a margem incremental simulada.",
                    "Volume vendido":"Conectar capacidade disponível à demanda e ao volume vendido meta.",
                    "Custo fixo":"Executar plano estrutural para atingir o custo fixo industrial meta.",
                    "Contratos/serviços":"Revisar contratos e serviços classificados em GGF."
                }
                new_rows=[]
                for _,r in top_actions.iterrows():
                    lever=str(r["Alavanca"])
                    owner=owner_map.get(lever,"Gestão")
                    new_rows.append([
                        "Alta" if float(r["Impacto_R$"])>=100000 else "Média",
                        lever,action_map.get(lever,f"Executar plano para atingir a meta simulada de {lever}."),
                        owner,owner_email(owner),"30 dias",fmt_money(float(r["Impacto_R$"])),"Não iniciado"
                    ])
                if new_rows:
                    new=pd.DataFrame(new_rows,columns=st.session_state.actions.columns)
                    st.session_state.actions=pd.concat([st.session_state.actions,new],ignore_index=True)
                    nav("Plano de Ação")
                else:
                    st.warning("Altere pelo menos uma alavanca com impacto econômico antes de criar o plano.")


elif page == "Plano de Ação":
    page_header("Plano de Ação","Responsabilidade, prazo, comunicação e captura de valor.")

    with st.container(border=True):
        panel_title("Ações em acompanhamento","Edite responsável, e-mail, prazo e status diretamente na tabela")
        edited=st.data_editor(
            st.session_state.actions,
            use_container_width=True,hide_index=True,num_rows="dynamic",
            height=320,key="actions_editor",
            column_config={
                "Prioridade":st.column_config.SelectboxColumn("Prioridade",options=["Alta","Média","Baixa"],width="small"),
                "Problema":st.column_config.TextColumn("Problema / oportunidade",width="medium"),
                "Ação":st.column_config.TextColumn("Ação",width="large"),
                "Responsável":st.column_config.TextColumn("Responsável",width="medium"),
                "E-mail":st.column_config.TextColumn("E-mail",width="medium"),
                "Prazo":st.column_config.TextColumn("Prazo",width="small"),
                "Impacto":st.column_config.TextColumn("Impacto",width="medium"),
                "Status":st.column_config.SelectboxColumn("Status",options=["Não iniciado","Planejado","Em andamento","Concluído","Bloqueado"],width="medium"),
            }
        )
        st.session_state.actions=edited

    st.write("")
    c1,c2=st.columns([1.15,.85],gap="small")

    with c1:
        with st.container(border=True):
            panel_title("Adicionar nova ação","Cadastre a ação e o e-mail do responsável")
            with st.form("action_form", clear_on_submit=True):
                a,b=st.columns(2)
                problema=a.text_input("Problema / oportunidade")
                responsavel=b.text_input("Responsável")
                email=st.text_input("E-mail do responsável",placeholder="nome@empresa.com")
                acao=st.text_area("Ação recomendada")
                c,d,e=st.columns(3)
                prazo=c.text_input("Prazo",placeholder="dd/mm/aaaa")
                prioridade=d.selectbox("Prioridade",["Alta","Média","Baixa"])
                impacto=e.text_input("Impacto esperado",placeholder="R$ 100 mil")
                ok=st.form_submit_button("Adicionar ação",type="primary")
                if ok and problema and acao:
                    new=pd.DataFrame(
                        [[prioridade,problema,acao,responsavel,email,prazo,impacto,"Planejado"]],
                        columns=st.session_state.actions.columns
                    )
                    st.session_state.actions=pd.concat([st.session_state.actions,new],ignore_index=True)
                    st.success("Ação adicionada ao plano.")
                    st.rerun()

    with c2:
        with st.container(border=True):
            panel_title("Comunicar responsável","Prepare o e-mail da ação selecionada")
            if len(st.session_state.actions):
                labels=[
                    f"{i+1}. {row['Problema']} - {row['Responsável']}"
                    for i,(_,row) in enumerate(st.session_state.actions.iterrows())
                ]
                selected=st.selectbox("Ação",options=list(range(len(labels))),format_func=lambda i:labels[i])
                row=st.session_state.actions.iloc[selected]
                st.markdown(
                    f"<div class='email-note'><b>Responsável:</b> {row['Responsável']}<br>"
                    f"<b>E-mail:</b> {row['E-mail'] if str(row['E-mail']).strip() else 'não cadastrado'}<br>"
                    f"<b>Prazo:</b> {row['Prazo']}<br><b>Impacto:</b> {row['Impacto']}</div>",
                    unsafe_allow_html=True
                )
                st.write("")
                email_ok="@" in str(row["E-mail"])
                if email_ok:
                    st.link_button("Preparar e-mail no Outlook",action_mailto(row),use_container_width=True)
                else:
                    st.button("Cadastre o e-mail para enviar",disabled=True,use_container_width=True)
                st.markdown(
                    "<div class='report-note'>Nesta versão o botão abre a mensagem pronta no Outlook/cliente de e-mail. "
                    "Para envio automático pelo sistema, a integração recomendada é Microsoft Graph com autenticação segura.</div>",
                    unsafe_allow_html=True
                )


elif page == "Agente de Performance":
    page_header("Agente de Performance","Pergunte aos dados e transforme análise em decisão.")
    if "chat" not in st.session_state:
        st.session_state.chat = []

    st.markdown(f"""
    <div class="agent-strip">
      <div>
        <div class="agent-title">Resumo do período</div>
        <div class="agent-copy">
        Produção em <b>{D["attainment"]:.1%}</b> do plano, OEE em <b>{D["oee"]:.1%}</b>,
        refugo em <b>{D["scrap"]:.1%}</b> e margem industrial em <b>{D["margin"]:.1%}</b>.
        </div>
      </div>
      <div>
        <div class="agent-title">Perguntas úteis</div>
        <div class="agent-copy">O que mais destruiu margem? · Qual linha priorizar? · Quanto ganho elevando o OEE?</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    for role,msg in st.session_state.chat:
        st.chat_message(role).write(msg)

    q = st.chat_input("Ex.: Qual o impacto de elevar o OEE para 80%?")
    if q:
        st.session_state.chat.append(("user", q))
        ql = q.lower()
        if "oee" in ql:
            ans = f"O OEE atual é {fmt_pct(D['oee'])}. O maior potencial está na recuperação de disponibilidade. Use o Simulador de Alavancas para testar metas de OEE, disponibilidade e performance."
        elif "linha" in ql:
            worst = D["line_perf"].sort_values("OEE").iloc[0]
            ans = f"A prioridade é {worst['Linha']}, com OEE de {fmt_pct(worst['OEE'])} e {worst['Paradas h']:.0f} horas de parada no período."
        elif "margem" in ql or "ebitda" in ql:
            top = D["impacts"].sort_values("R$",ascending=False).iloc[0]
            ans = f"A maior pressão estimada sobre o resultado vem de {top['Impacto']}, com impacto indicativo de {fmt_money(top['R$'])}."
        else:
            ans = "As prioridades são disponibilidade, refugo e horas extras. Use Diagnóstico e Alavancas para abrir as causas e simular o efeito financeiro."
        st.session_state.chat.append(("assistant", ans))
        st.rerun()

elif page == "Relatórios":
    page_header("Relatórios","Resumo executivo e materiais para rotina de gestão.")
    summary = f"""INDUSTRIAL PERFORMANCE — RESUMO EXECUTIVO
Produção: {D["actual"]:,.0f} un
Plano: {D["planned"]:,.0f} un
Atingimento: {D["attainment"]:.1%}
OEE: {D["oee"]:.1%}
Refugo: {D["scrap"]:.1%}
Margem industrial: {D["margin"]:.1%}
EBITDA industrial: {fmt_money(D["ebitda"])}

Prioridades:
1. Recuperar disponibilidade
2. Reduzir perdas de qualidade
3. Ajustar horas extras / capacidade
"""
    with st.container(border=True):
        panel_title("Resumo Executivo","Versão simples para validação do fluxo")
        st.write(summary)
    st.write("")
    st.download_button("Baixar resumo executivo", summary, file_name="industrial_performance_resumo.txt", type="primary")

elif page == "Central de Dados":
    admin_header("Central de Dados", "Entrada governada: RAW → DE/PARA → Standard → Data Quality → Semantic / Gold.")
    tabs = st.tabs(["Nova importação", "Histórico", "Arquitetura"])

    with tabs[0]:
        render_data_layer_import()

    with tabs[1]:
        st.markdown("### Histórico de ingestões")
        st.caption("No MVP v0.6.3 este histórico usa persistência local temporária. A arquitetura já está separada para migrar para Object Storage + PostgreSQL na v0.8.")
        hist = idl.list_ingestions()
        if hist.empty:
            st.info("Nenhuma ingestão persistida neste ambiente ainda.")
        else:
            h = hist.copy()
            keep = [c for c in ["timestamp", "company", "source", "filename", "rows", "quality_score", "quality_status", "ingestion_id"] if c in h.columns]
            st.dataframe(h[keep].sort_values("timestamp", ascending=False), use_container_width=True, hide_index=True)

    with tabs[2]:
        st.markdown("### Industrial Data Layer")
        arch = pd.DataFrame([
            ["RAW", "Preserva o arquivo original e metadados", "Ativo no MVP"],
            ["MAPPING", "DE/PARA de abas, colunas, dimensões e unidades", "Ativo no MVP"],
            ["STANDARD", "Industrial Performance Data Model canônico", "Ativo no MVP"],
            ["DATA QUALITY", "Score, bloqueios e alertas de consistência", "Ativo no MVP"],
            ["SEMANTIC / GOLD", "Dados governados para Cockpit e Performance Engine", "Ativo no MVP"],
            ["LINEAGE", "Origem → aba → coluna → campo padrão → transformação", "Ativo no MVP"],
            ["OBJECT STORAGE + POSTGRESQL", "Persistência empresarial e multiempresa", "v0.8"],
        ], columns=["Camada", "Função", "Status"])
        st.dataframe(arch, use_container_width=True, hide_index=True)
        st.info("O valor proprietário está no Industrial Performance Data Model e nas regras de transformação. A infraestrutura de armazenamento pode evoluir sem refazer o Performance Engine.")

elif page == "Mapeamentos":
    admin_header("Mapeamentos", "DE/PARA reutilizável por empresa e fonte de dados.")
    _idl_init_state()

    saved = idl.list_saved_mappings()
    with st.container(border=True):
        panel_title("Mappings salvos", "Perfis gravados no ambiente piloto")
        if saved.empty:
            st.info("Ainda não há mappings persistidos neste ambiente. Eles são gravados quando uma ingestão é aplicada.")
        else:
            st.dataframe(saved, use_container_width=True, hide_index=True)

    st.write("")
    with st.container(border=True):
        panel_title("Mapping em uso", "Origem, campo padrão, unidade e confiança")
        if not st.session_state.idl_mapping:
            st.info("Nenhum mapping ativo nesta sessão. Crie uma importação na Central de Dados.")
            if st.button("Abrir Central de Dados", type="primary", key="mapping_open_central"):
                nav("Central de Dados")
        else:
            rows = []
            for sh, cols_map in st.session_state.idl_mapping.get("column_map", {}).items():
                entity = st.session_state.idl_mapping.get("sheet_map", {}).get(sh, {}).get("entity")
                for source_col, meta in cols_map.items():
                    field = meta.get("field")
                    if not field:
                        continue
                    units = st.session_state.idl_mapping.get("unit_map", {}).get(sh, {}).get(source_col, {})
                    rows.append({
                        "Aba origem": sh,
                        "Entidade": idl.ENTITY_LABELS.get(entity, entity),
                        "Coluna origem": source_col,
                        "Campo padrão": field,
                        "Confiança": f"{float(meta.get('confidence',0))*100:.0f}%",
                        "Unidade origem": units.get("source", "—"),
                        "Unidade padrão": units.get("target") or "—",
                    })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            mapping_json = idl.mapping_to_json(st.session_state.idl_mapping, st.session_state.idl_company, st.session_state.idl_source)
            st.download_button(
                "Exportar perfil DE/PARA",
                mapping_json,
                file_name=f"mapping_{idl.safe_slug(st.session_state.idl_company)}_{idl.safe_slug(st.session_state.idl_source)}.json",
                mime="application/json",
            )

    st.write("")
    st.caption("Importante: no Streamlit Cloud o armazenamento local não é a persistência definitiva. Por isso o perfil pode ser exportado e, na v0.8, será armazenado em PostgreSQL/Object Storage.")

elif page == "Qualidade dos Dados":
    admin_header("Qualidade dos Dados", "Governança antes do cálculo: completude, estrutura, tipos, padrões, metas e consistência.")
    _idl_init_state()

    data_for_quality = st.session_state.idl_standard or st.session_state.real_data
    if data_for_quality:
        q = idl.evaluate_data_quality(data_for_quality, st.session_state.idl_mapping)
        _idl_render_quality_summary(q)
        if not q.checks.empty:
            st.dataframe(q.checks[["Categoria", "Item", "Severidade", "Resultado", "Detalhe", "Penalidade"]], use_container_width=True, hide_index=True)

        st.write("")
        with st.container(border=True):
            panel_title("Regra de governança", "O sistema não trata ausência de meta ou de padrão como ausência de problema")
            st.markdown(
                "**KPI sem meta é risco de gestão.** Bases multiproduto sem padrões perdem confiabilidade na leitura de produtividade. "
                "Falhas estruturais críticas bloqueiam a aplicação; alertas não críticos reduzem o score e permanecem explícitos."
            )
    else:
        st.info("Ainda não há uma base importada para avaliar. Use a Central de Dados para iniciar uma ingestão.")
        if st.button("Abrir Central de Dados", type="primary", key="quality_open_central"):
            nav("Central de Dados")

elif page == "Configurações":
    admin_header("Configurações", "Modelo padrão, dados ativos e evolução de integrações.")
    tabs = st.tabs(["Modelo padrão", "Dados ativos", "Integrações", "Infraestrutura"])

    with tabs[0]:
        st.markdown("### Industrial Performance Data Model")
        st.caption("O modelo padrão continua disponível como acelerador, mas o cliente não precisa mais adaptar seu Excel a ele: o DE/PARA faz a tradução.")
        template = Path(__file__).parent / "Industrial_Performance_Input_Padrao_v063.xlsx"
        if not template.exists():
            template = Path(__file__).parent / "Industrial_Performance_Input_Padrao_v062.xlsx"
        if template.exists():
            st.download_button(
                "Baixar modelo padrão de referência",
                template.read_bytes(),
                file_name="Industrial_Performance_Input_Padrao_v063.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
            )
        st.write("")
        st.markdown("**Fluxo oficial v0.6.3:** RAW → Mapping / DE-PARA → Standard → Data Quality → Semantic / Gold → Performance Engine")

    with tabs[1]:
        if st.session_state.real_data is not None:
            st.success("O Performance Engine está usando dados importados e padronizados.")
            if st.session_state.get("idl_last_record"):
                rec = st.session_state.idl_last_record
                st.json({k: rec.get(k) for k in ["company", "source", "filename", "quality_score", "quality_status", "storage_mode"]})
            if st.button("Voltar para dados demo", key="config_demo"):
                st.session_state.real_data = None
                st.rerun()
        else:
            st.info("O Performance Engine está usando dados demo.")
        if st.button("Abrir nova importação", key="config_open_central"):
            nav("Central de Dados")

    with tabs[2]:
        st.markdown("### Roadmap de conectores")
        integrations = pd.DataFrame([
            ["Excel", "Disponível", "Upload + DE/PARA"],
            ["ERP / SQL", "v0.8", "Conector → mesmo Standard Model"],
            ["MES", "v0.8", "Conector → mesmo Standard Model"],
            ["WMS / CMMS", "v0.8", "Conector → mesmo Standard Model"],
            ["APIs", "v0.8", "Ingestão programática e incremental"],
        ], columns=["Fonte", "Status", "Estratégia"])
        st.dataframe(integrations, use_container_width=True, hide_index=True)

    with tabs[3]:
        st.markdown("### Persistência")
        st.info("v0.6.3 usa DuckDB + Parquet e uma camada de abstração local para validar o produto. No Streamlit Cloud, o disco local é temporário e não deve guardar o histórico empresarial definitivo.")
        st.markdown("**v0.8:** Object Storage (S3 / Azure Blob / R2) + PostgreSQL + engine analítico. O Industrial Performance Data Model e o Performance Engine permanecem os mesmos.")

