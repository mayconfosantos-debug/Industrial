
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from io import BytesIO
import unicodedata
from urllib.parse import quote

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
div[data-testid="stVerticalBlockBorderWrapper"] {
    min-width:0;
}
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    min-width:0;
}
div[data-testid="stDataFrame"] {
    width:100%;
}
[data-testid="stMetric"] label {
    min-height:18px;
}
[data-testid="stMetricValue"] {
    white-space:nowrap;
}
.email-note {
    font-size:.62rem;
    color:#6E7C90;
    line-height:1.45;
}
.report-note {
    border-left:3px solid #00B7E8;
    padding:8px 10px;
    background:#F7FCFF;
    border-radius:6px;
    color:#34465C;
    font-size:.65rem;
}


/* =========================================================
   v0.6.2 — FRONT-END PREMIUM
   ========================================================= */
.block-container {
    max-width: 1540px;
    padding: .55rem 1.35rem 2.25rem 1.35rem;
}
[data-testid="stSidebar"] {
    width:258px !important;
}
[data-testid="stSidebar"] > div:first-child {
    width:258px !important;
}
[data-testid="stSidebar"] .block-container {
    padding: .9rem .72rem 1rem .72rem;
}
[data-testid="stHorizontalBlock"] {
    align-items: stretch;
}
[data-testid="stHorizontalBlock"] > div {
    min-width:0;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    background:#FFFFFF;
    border:1px solid #DFE7EF !important;
    border-radius:14px;
    box-shadow:0 4px 16px rgba(10,35,60,.035);
    overflow:hidden;
}
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    min-width:0;
}
div[data-testid="stMetric"] {
    height:104px;
    display:flex;
    flex-direction:column;
    justify-content:center;
    background:#FFFFFF;
    border:1px solid #DFE7EF;
    border-radius:12px;
    box-shadow:0 3px 12px rgba(10,35,60,.03);
}
div[data-testid="stMetricValue"] {
    font-size:1.34rem;
    line-height:1.05;
    color:#10233F;
}
div[data-testid="stDataFrame"] {
    border:1px solid #E3EAF1;
    border-radius:10px;
    overflow:hidden;
}
[data-testid="stDataFrame"] [role="columnheader"] {
    font-weight:700;
}
.stTabs [data-baseweb="tab-list"] {
    background:#F4F7FA;
    border:1px solid #E1E8EF;
    border-radius:10px;
    padding:3px;
}
.stTabs [data-baseweb="tab"] {
    border-radius:7px;
}
.stTabs [aria-selected="true"] {
    background:white !important;
    box-shadow:0 1px 4px rgba(10,35,60,.08);
}
[data-baseweb="select"] > div {
    border-color:#DCE5ED !important;
}
.stSlider [data-baseweb="slider"] {
    padding-top: .2rem;
}
.lever-shell {
    background:linear-gradient(180deg,#FFFFFF 0%,#FAFCFE 100%);
    border:1px solid #DDE6EF;
    border-radius:14px;
    padding:14px 15px;
    min-height:96px;
}
.lever-kicker {
    font-size:.55rem;
    font-weight:850;
    letter-spacing:.08em;
    color:#0B5FA5;
    text-transform:uppercase;
}
.lever-title {
    font-size:.78rem;
    font-weight:850;
    color:#10233F;
    margin-top:3px;
}
.lever-meta {
    font-size:.58rem;
    color:#6E7C90;
    margin-top:4px;
    line-height:1.35;
}
.sim-header {
    display:flex;
    align-items:flex-start;
    justify-content:space-between;
    gap:12px;
    margin-bottom:5px;
}
.sim-header-title {
    font-size:1rem;
    font-weight:850;
    color:#10233F;
}
.sim-header-sub {
    font-size:.63rem;
    color:#6E7C90;
    margin-top:3px;
}
.sim-scope-chip {
    display:inline-block;
    background:#EAF6FE;
    color:#0B5FA5;
    border:1px solid #CDE6F8;
    padding:4px 8px;
    border-radius:999px;
    font-size:.55rem;
    font-weight:850;
}
.sim-card {
    background:#FFFFFF;
    border:1px solid #DFE7EF;
    border-radius:12px;
    padding:12px 13px;
    min-height:92px;
}
.sim-card-label {
    color:#6E7C90;
    font-size:.58rem;
    font-weight:760;
}
.sim-card-value {
    color:#10233F;
    font-size:1.20rem;
    font-weight:850;
    margin-top:5px;
    white-space:nowrap;
}
.sim-card-delta {
    font-size:.59rem;
    font-weight:800;
    margin-top:3px;
}
.sim-mini {
    font-size:.58rem;
    color:#6E7C90;
    line-height:1.4;
}
.conf-high {color:#12805C;font-weight:800;}
.conf-mid {color:#C76A15;font-weight:800;}
.conf-low {color:#7C8795;font-weight:800;}
.frontend-note {
    background:#F7FBFE;
    border-left:3px solid #00B7E8;
    border-radius:8px;
    padding:9px 11px;
    color:#40576B;
    font-size:.62rem;
    line-height:1.45;
}

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
        c[col]=nseries(c[col])
    c["custo_fixo"]=nseries(c["custo_fixo"]) if "custo_fixo" in c.columns else 0

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

    # ---------------- Finance ----------------
    var_cost=c[["custo_mp","custo_mod","custo_energia","custo_manutencao"]].sum().sum()
    fixed_cost=c["custo_fixo"].sum()
    revenue=c["receita"].sum()
    total_cost=var_cost+fixed_cost
    contrib=revenue-var_cost
    ebitda=revenue-total_cost
    margin_contrib=safe_div(contrib,revenue)
    cost_unit=safe_div(total_cost,actual)

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
    t_margin=target_from(data,["Margem","Margem Contribuição"],0.31)
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

    causes=m.groupby("causa",as_index=False)["duracao_horas"].sum().rename(columns={"duracao_horas":"Horas"})
    if not causes.empty:
        margin_unit=safe_div(contrib,actual)
        units_h=safe_div(actual,max(1,actual_hh))
        causes["Impacto R$ mil"]=causes["Horas"]*units_h*margin_unit/1000
        causes=causes.sort_values("Horas",ascending=False).head(8)

    # ---------------- Unique financial impact buckets (avoid double count) ----------------
    margin_unit=safe_div(contrib,max(1,actual))
    loss_prod=max(0,planned-actual)*margin_unit
    loss_scrap=q["refugo"].sum()*safe_div(total_cost,max(1,actual))
    overtime_premium=max(0,overtime-(t_overtime if pd.notna(t_overtime) else 0))*30 if pd.notna(t_overtime) else overtime*30
    cost_gap=max(0,cost_unit-t_cost)*actual if pd.notna(t_cost) else max(0,total_cost*0.015)
    energy_gap=max(0,c["custo_energia"].sum()*0.05)
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
        ("Margem contribuição",fmt_pct(margin_contrib),fmt_pct(t_margin),safe_div(margin_contrib,t_margin)-1,f"{(margin_contrib-t_margin)*100:+.1f} pp".replace(".",","),"↓" if margin_contrib<t_margin else "↑"),
    ]

    margin_score=safe_div(margin_contrib,t_margin)-1
    cards=[
        ("Receita Líquida",fmt_money(revenue),attainment-1,f"{attainment-1:+.1%} vs. plano".replace(".",",")),
        ("Margem Contrib.",fmt_pct(margin_contrib),margin_score,f"{(margin_contrib-t_margin)*100:+.1f} pp vs. meta".replace(".",",")),
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
        "Margem contribuição":max(0,(t_margin-margin_contrib)*revenue)
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

    financial_names=["Produção","Refugo","Custo/unidade","Horas extras","Margem contribuição","Eficiência MOD"]
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
        f"A operação fechou em {attainment:.1%} do plano, com OEE de {oee:.1%} e margem de contribuição de {margin_contrib:.1%}. "
        f"A saúde consolidada está em {health_score:.0f}/100 e a saúde financeira em {financial_health:.0f}/100. "
    )
    if worst_line is not None:
        conclusion += f"A linha mais crítica é {worst_line['Linha']} (OEE {worst_line['OEE']:.1%}). "
    if top_cause is not None:
        conclusion += f"A principal causa de parada é {top_cause['Causa']} ({top_cause['Horas']:.0f} h). "
    if top2:
        conclusion += "As alavancas a priorizar são " + " e ".join(top2) + "."

    dre=pd.DataFrame({
        "Linha":["Receita Líquida","(-) Custos Variáveis","Margem de Contribuição","(-) Custos Fixos","EBITDA Industrial"],
        "Realizado":[revenue,-var_cost,contrib,-fixed_cost,ebitda]
    })

    return {
        "cards":cards,"kpis":kpis,"trend":trend,"line_perf":line_perf,"causes":causes,
        "impacts":impacts,"dre":dre,"cost_structure":{"Variável":var_cost,"Fixo":fixed_cost},
        "oee":oee,"target_oee":t_oee,"scrap":scrap,"target_scrap":t_scrap,
        "attainment":attainment,"margin":margin_contrib,"target_margin":t_margin,
        "ebitda":ebitda,"revenue":revenue,"actual":actual,"planned":planned,
        "availability":availability,"performance":performance,"quality":quality,
        "cost_unit":cost_unit,"overtime":overtime,"productivity":productivity_raw,
        "rework_rate":rework_rate,"mttr_min":mttr_min,"setup_avg_min":setup_avg_min,
        "avg_headcount":avg_headcount,
        "cost_mp":float(c["custo_mp"].sum()),"cost_mod":float(c["custo_mod"].sum()),
        "cost_energy":float(c["custo_energia"].sum()),"cost_maintenance":float(c["custo_manutencao"].sum()),
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
        ("Margem Contrib.","27,8%",-0.103,"-3,2 pp vs. meta"),
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
        ("Margem contribuição","27,8%","31%",-0.103,"-3,2 pp","↓"),
    ]
    impacts=pd.DataFrame({
        "Impacto":["Gap de volume","Refugo","Eficiência MOD","Horas extras","Custo / consumo"],
        "R$":[220000,110000,84000,75000,48000]
    })
    dre=pd.DataFrame({
        "Linha":["Receita Líquida","(-) Custos Variáveis","Margem de Contribuição","(-) Custos Fixos","EBITDA Industrial"],
        "Realizado":[12400000,-8950000,3450000,-1550000,1900000]
    })
    health_details=pd.DataFrame([
        ["Produção",72,3.0,220000,True,True],
        ["OEE",67,2.4,154000,True,True],
        ["Eficiência MOD",72,1.8,84000,True,True],
        ["Refugo",20,2.0,110000,True,True],
        ["OTIF",70,1.2,50000,True,True],
        ["Custo/unidade",68,1.6,95000,True,True],
        ["Horas extras",0,1.5,75000,True,True],
        ["Margem contribuição",50,2.2,397000,True,True],
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
        "oee":.714,"target_oee":.78,"scrap":.038,"target_scrap":.025,
        "attainment":.917,"margin":.278,"target_margin":.31,
        "ebitda":1900000,"revenue":12400000,"actual":41250,"planned":45000,
        "availability":.748,"performance":.945,"quality":.981,
        "cost_unit":18.42,"overtime":1280,"productivity":18.2,
        "rework_rate":.042,"mttr_min":95.0,"setup_avg_min":48.0,"avg_headcount":118,
        "cost_mp":5191000.0,"cost_mod":1611000.0,"cost_energy":895000.0,"cost_maintenance":1253000.0,
        "labor_efficiency":.898,"std_hours_earned":12120,"actual_hh":13497,
        "standards_missing":[],
        "health_score":55,"financial_health":49,"operational_health":61,
        "health_details":health_details,
        "diagnostic":diagnostic,
        "diagnostic_conclusion":"A fábrica fechou em 91,7% do plano, com OEE de 71,4% e margem de contribuição de 27,8%. A saúde consolidada está em 55/100 e a saúde financeira em 49/100. A Linha 3 é a mais crítica (OEE 64%). A principal causa de parada é Falha mecânica (58 h). As alavancas a priorizar são Disponibilidade e Refugo."
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

def page_header(title, subtitle):
    c1,c2,c3,c4 = st.columns([1.05,1.05,.8,1.4], gap="small")
    c1.selectbox("Grupo",["Grupo Industrial S.A."],label_visibility="collapsed",key=f"g_{title}")
    c2.selectbox("Planta",["Planta São Paulo","Todas as plantas"],label_visibility="collapsed",key=f"p_{title}")
    c3.selectbox("Período",["Ago/2026","Jul/2026","Jun/2026"],label_visibility="collapsed",key=f"d_{title}")
    mode = "Dados importados" if st.session_state.real_data else "Dados demo"
    c4.markdown(f'<div style="text-align:right;padding-top:.2rem"><span class="data-badge">{mode}</span></div>',unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">EXECUÇÃO HOJE. COMPETITIVIDADE AMANHÃ.</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="page-title">{title}</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{subtitle}</div>',unsafe_allow_html=True)

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

D = calculate_real(st.session_state.real_data) if st.session_state.real_data else demo_dataset()

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    c1, c2 = st.columns([.20, .80], gap="small")
    logo = Path(__file__).parent / "logo_h2m_white.jpeg"
    with c1:
        if logo.exists():
            st.image(str(logo), width=46)
    with c2:
        st.markdown('<div class="brand-title">Industrial Performance</div><div class="brand-sub">by H2M Consulting</div>', unsafe_allow_html=True)

    groups = [
        ("VISÃO", ["Cockpit Executivo","Performance Operacional","Diagnóstico e Causas"]),
        ("RESULTADO", ["Finanças / DRE","Alavancas de Valor","Plano de Ação"]),
        ("INTELIGÊNCIA", ["Agente de Performance","Relatórios"]),
        ("ADMINISTRAÇÃO", ["Configurações"]),
    ]
    for group, items in groups:
        st.markdown(f'<div class="menu-group">{group}</div>', unsafe_allow_html=True)
        for p in items:
            if st.button(p, key=f"nav_{p}", type="primary" if st.session_state.page == p else "secondary", use_container_width=True):
                nav(p)

    st.markdown('<div class="sidebar-footer"><b>Da operação ao resultado.</b><br><small>PESSOAS &nbsp;&nbsp; DADOS &nbsp;&nbsp; AÇÃO</small></div>', unsafe_allow_html=True)

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
                f"<span>Variável <b>{vp:.0f}%</b></span><span>Fixo <b>{fp:.0f}%</b></span></div>",
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
    page_header("Performance Operacional","Eficiência, capacidade e perdas por linha.")
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
            panel_title("OEE por Linha","Comparação com meta")
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

    with c2:
        with st.container(border=True, height=375):
            panel_title("Paradas x Gap de Produção","Quanto mais à direita e abaixo, pior")
            fig = go.Figure(go.Scatter(
                x=lp["Paradas h"], y=lp["Gap Produção"], mode="markers+text",
                text=lp["Linha"], textposition="top center",
                marker=dict(size=np.clip(lp["Paradas h"],16,42), color=BLUE, opacity=.78, line=dict(width=2,color="white"))
            ))
            fig.update_layout(height=300, margin=dict(l=0,r=0,t=8,b=0),
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              xaxis=dict(gridcolor="#EFF3F7"), yaxis=dict(gridcolor="#EFF3F7"))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    st.write("")
    st.dataframe(lp, use_container_width=True, hide_index=True)

elif page == "Diagnóstico e Causas":
    page_header("Diagnóstico e Causas","Raio-X da performance: desvio, causa, impacto financeiro e ação.")

    diag=D["diagnostic"].copy()
    causes=D["causes"].copy()
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
                st.caption("Volume perdido é valorizado pela margem de contribuição unitária; refugo considera custo consumido nas unidades perdidas; eficiência MOD considera HH reais acima das HH padrão ganhas; horas extras consideram custo incremental; custo/consumo compara real versus referência. Causa e efeito não são somados duas vezes.")

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
    page_header("Finanças / DRE","A operação traduzida em margem, custo fixo, variável e EBITDA.")

    c1,c2,c3,c4 = st.columns(4, gap="small")
    c1.metric("Receita Líquida", fmt_money(D["revenue"]))
    c2.metric("Margem Contrib.", fmt_pct(D["margin"]))
    c3.metric("EBITDA Industrial", fmt_money(D["ebitda"]))
    c4.metric("Custo Fixo", fmt_money(D["cost_structure"]["Fixo"]))

    st.write("")
    c1, c2 = st.columns([1.15,.85], gap="small")
    with c1:
        with st.container(border=True, height=340):
            panel_title("DRE Gerencial","Visão resumida do resultado")
            view = D["dre"].copy()
            view["Realizado"] = view["Realizado"].map(lambda x: fmt_money(x))
            st.dataframe(view, use_container_width=True, hide_index=True)
    with c2:
        with st.container(border=True, height=340):
            panel_title("Custo Fixo x Variável","Estrutura econômica da operação")
            vals = D["cost_structure"]
            fig = go.Figure(go.Pie(labels=list(vals.keys()), values=list(vals.values()), hole=.72,
                                   marker=dict(colors=[BLUE,"#BBD8EC"]), textinfo="percent",
                                   textfont=dict(size=11)))
            fig.update_layout(height=260, margin=dict(l=0,r=0,t=0,b=0),
                              legend=dict(orientation="h",y=-.05),
                              paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

elif page == "Alavancas de Valor":
    page_header("Alavancas de Valor","Simule as 26 alavancas acordadas e traduza performance em receita, margem, EBITDA e caixa.")

    # ------------------------------------------------------------------
    # Baselines / configurable assumptions
    # ------------------------------------------------------------------
    base_revenue=float(D["revenue"])
    base_margin=float(D["margin"])
    base_ebitda=float(D["ebitda"])
    base_fixed=float(D["cost_structure"]["Fixo"])
    base_var=float(D["cost_structure"]["Variável"])
    base_mp=float(D.get("cost_mp",base_var*sim_assumption("participacao_mp_custo_variavel",0.58)))
    base_energy=float(D.get("cost_energy",base_var*sim_assumption("participacao_energia_custo_variavel",0.10)))
    base_mod=float(D.get("cost_mod",base_var*0.18))

    capacity_base=sim_assumption("capacidade_utilizada_base",72.0)
    setup_base=float(D.get("setup_avg_min",np.nan))
    if pd.isna(setup_base):
        setup_base=sim_assumption("setup_medio_base",48.0)
    mttr_base=float(D.get("mttr_min",np.nan))
    if pd.isna(mttr_base):
        mttr_base=sim_assumption("mttr_base",95.0)
    rework_base=float(D.get("rework_rate",np.nan))*100
    if pd.isna(rework_base):
        rework_base=sim_assumption("retrabalho_base",4.2)
    otif_base=sim_assumption("otif_base",89.0)
    mp_specific_base=sim_assumption("consumo_mp_indice_base",1.04)
    avg_monthly_person_cost=sim_assumption("custo_medio_mensal_pessoa",8500.0)
    mp_share=sim_assumption("participacao_mp_custo_variavel",0.58)
    freight_share=sim_assumption("participacao_frete_custo_variavel",0.07)
    contracts_share=sim_assumption("participacao_contratos_custo_fixo",0.22)
    otif_risk_share=sim_assumption("receita_em_risco_otif",0.12)
    period_days=max(1.0,sim_assumption("dias_periodo",30.0))

    base_productivity=float(D.get("productivity",18.2))
    base_headcount=float(D.get("avg_headcount",np.nan))
    if pd.isna(base_headcount):
        base_headcount=118.0

    # ------------------------------------------------------------------
    # Scope defaults — exactly the agreed simulator scope
    # ------------------------------------------------------------------
    scope_targets={
        "sim_oee":78.0,
        "sim_availability":82.0,
        "sim_performance":97.0,
        "sim_capacity":80.0,
        "sim_scrap":2.5,
        "sim_rework":2.0,
        "sim_setup":35.0,
        "sim_unplanned":20,
        "sim_mttr":70.0,
        "sim_overtime":25,
        "sim_productivity":20.0,
        "sim_headcount":0,
        "sim_mp_specific":1.00,
        "sim_mp_price":3.0,
        "sim_material_loss":15,
        "sim_energy":8.0,
        "sim_freight":5.0,
        "sim_otif":95.0,
        "sim_price":2.0,
        "sim_mix":1.0,
        "sim_volume":5.0,
        "sim_fixed":5.0,
        "sim_contracts":10.0,
        "sim_inventory":10,
        "sim_dpo":5,
        "sim_dso":5,
    }
    base_targets={
        "sim_oee":float(np.clip(D["oee"]*100,40.0,95.0)),
        "sim_availability":float(np.clip(D["availability"]*100,50.0,99.0)),
        "sim_performance":float(np.clip(D["performance"]*100,60.0,105.0)),
        "sim_capacity":float(np.clip(capacity_base,40.0,100.0)),
        "sim_scrap":float(np.clip(D["scrap"]*100,0.0,10.0)),
        "sim_rework":float(np.clip(rework_base,0.0,10.0)),
        "sim_setup":float(np.clip(setup_base,5.0,max(120.0,setup_base*1.25))),
        "sim_unplanned":0,
        "sim_mttr":float(np.clip(mttr_base,10.0,max(180.0,mttr_base*1.25))),
        "sim_overtime":0,
        "sim_productivity":float(np.clip(base_productivity,5.0,35.0)),
        "sim_headcount":0,
        "sim_mp_specific":float(np.clip(mp_specific_base,0.80,1.20)),
        "sim_mp_price":0.0,
        "sim_material_loss":0,
        "sim_energy":0.0,
        "sim_freight":0.0,
        "sim_otif":float(np.clip(otif_base,50.0,100.0)),
        "sim_price":0.0,
        "sim_mix":0.0,
        "sim_volume":0.0,
        "sim_fixed":0.0,
        "sim_contracts":0.0,
        "sim_inventory":0,
        "sim_dpo":0,
        "sim_dso":0,
    }
    for k,v in scope_targets.items():
        if k not in st.session_state:
            st.session_state[k]=v
    if "sim_prod_mode" not in st.session_state:
        st.session_state.sim_prod_mode="OEE direto"
    if "sim_group" not in st.session_state:
        st.session_state.sim_group="Produção"

    # Header / controls
    with st.container(border=True):
        c1,c2,c3=st.columns([1,.33,.33],gap="small")
        with c1:
            st.markdown(
                "<div class='sim-header'><div>"
                "<div class='sim-header-title'>Simulador de Performance & Valor</div>"
                "<div class='sim-header-sub'>Escopo oficial: 10 grupos · 26 alavancas · cálculo com dependências para evitar dupla contagem.</div>"
                "</div><div><span class='sim-scope-chip'>MODELO v0.6.2</span></div></div>",
                unsafe_allow_html=True
            )
        with c2:
            if st.button("Cenário exemplo",use_container_width=True):
                for k,v in scope_targets.items():
                    st.session_state[k]=v
                st.rerun()
        with c3:
            if st.button("Resetar para base",use_container_width=True):
                for k,v in base_targets.items():
                    st.session_state[k]=v
                st.rerun()

    # ------------------------------------------------------------------
    # Input panel
    # ------------------------------------------------------------------
    left,right=st.columns([1.32,.68],gap="small")

    with left:
        with st.container(border=True, height=585):
            top1,top2=st.columns([.58,.42],gap="small")
            groups=["Produção","Qualidade","Processo","Pessoas","Materiais","Energia","Logística","Financeiro","Estrutura","Capital"]
            with top1:
                group=st.selectbox("Grupo de alavancas",groups,key="sim_group")
            with top2:
                prod_mode=st.radio(
                    "Motor de Produção",
                    ["OEE direto","Drivers de OEE"],
                    horizontal=True,
                    key="sim_prod_mode",
                    help="OEE direto usa o alvo de OEE como capacidade potencial. Drivers de OEE recalcula o OEE a partir de disponibilidade e performance. Os dois caminhos não são somados."
                )

            st.markdown("---")

            if group=="Produção":
                st.markdown("<div class='lever-kicker'>PRODUÇÃO</div><div class='lever-title'>Capacidade, eficiência e volume potencial</div>",unsafe_allow_html=True)
                a,b=st.columns(2,gap="medium")
                with a:
                    st.slider("OEE (%)",40.0,95.0,key="sim_oee",step=.5,disabled=(prod_mode!="OEE direto"),
                              help="Impacto: volume, receita potencial, margem e EBITDA. No modo Drivers de OEE o resultado é calculado por disponibilidade × performance × qualidade base.")
                    st.caption("Impacto: volume / receita / margem / EBITDA · Confiança: Alta")
                    st.slider("Performance (%)",60.0,105.0,key="sim_performance",step=.5,disabled=(prod_mode=="OEE direto"),
                              help="Driver do OEE. Não é somado novamente ao OEE direto.")
                    st.caption("Impacto: produção adicional · Confiança: Alta")
                with b:
                    st.slider("Disponibilidade (%)",50.0,99.0,key="sim_availability",step=.5,disabled=(prod_mode=="OEE direto"),
                              help="Driver do OEE. Processo (setup, paradas e MTTR) pode elevar a disponibilidade técnica estimada.")
                    st.caption("Impacto: capacidade recuperada · Confiança: Alta")
                    st.slider("Capacidade utilizada (%)",40.0,100.0,key="sim_capacity",step=.5,
                              help="Aumentar utilização reduz custo fixo por unidade, mas não reduz automaticamente o custo fixo total. A monetização depende de volume vendido.")
                    st.caption("Impacto: volume / absorção de custo fixo · Confiança: Média")

            elif group=="Qualidade":
                st.markdown("<div class='lever-kicker'>QUALIDADE</div><div class='lever-title'>Yield, desperdício e capacidade consumida</div>",unsafe_allow_html=True)
                a,b=st.columns(2,gap="medium")
                with a:
                    st.slider("Refugo (%)",0.0,10.0,key="sim_scrap",step=.1,
                              help="Economia de matéria-prima/custo consumido nas unidades perdidas. Não duplica a margem do volume recuperado.")
                    st.caption("Impacto: MP / margem / EBITDA · Confiança: Alta")
                with b:
                    st.slider("Retrabalho (%)",0.0,10.0,key="sim_rework",step=.1,
                              help="Reduz MOD, energia e capacidade consumida por retrabalho.")
                    st.caption("Impacto: MOD / energia / capacidade · Confiança: Alta")

            elif group=="Processo":
                st.markdown("<div class='lever-kicker'>PROCESSO</div><div class='lever-title'>Tempo disponível, confiabilidade e recuperação de capacidade</div>",unsafe_allow_html=True)
                a,b=st.columns(2,gap="medium")
                with a:
                    st.slider("Setup médio (min)",5.0,max(120.0,setup_base*1.25),key="sim_setup",step=1.0)
                    st.caption("Impacto: horas disponíveis + volume · Confiança: Alta")
                    st.slider("MTTR (min)",10.0,max(180.0,mttr_base*1.25),key="sim_mttr",step=1.0)
                    st.caption("Impacto: tempo recuperado / disponibilidade · Confiança: Alta")
                with b:
                    st.slider("Redução de paradas não planejadas (%)",0,60,key="sim_unplanned",step=1)
                    st.caption("Impacto: disponibilidade + produção · Confiança: Alta")
                    st.markdown(
                        "<div class='frontend-note'>Setup, paradas e MTTR alimentam a disponibilidade técnica. "
                        "Quando Disponibilidade já foi elevada manualmente, o motor usa o maior efeito — não soma duas vezes.</div>",
                        unsafe_allow_html=True
                    )

            elif group=="Pessoas":
                st.markdown("<div class='lever-kicker'>PESSOAS</div><div class='lever-title'>Mão de obra, produtividade e dimensionamento</div>",unsafe_allow_html=True)
                a,b=st.columns(2,gap="medium")
                with a:
                    st.slider("Redução de horas extras (%)",0,70,key="sim_overtime",step=1)
                    st.caption("Impacto: MOD + EBITDA · Confiança: Alta")
                    st.slider("Produtividade (un/h equivalente)",5.0,35.0,key="sim_productivity",step=.1,
                              help="Antes de impactar o consolidado, o ganho é linearizado pelo mix usando HH padrão por produto.")
                    st.caption("Impacto: capacidade / MOD · mix linearizado · Confiança: Alta")
                with b:
                    st.slider("Variação de headcount (pessoas)",-30,30,key="sim_headcount",step=1)
                    st.caption(f"Impacto: custo de pessoal · premissa R$ {avg_monthly_person_cost:,.0f}/pessoa".replace(",","."))
                    st.markdown(
                        "<div class='frontend-note'>Headcount positivo aumenta custo; negativo gera economia. "
                        "O modelo não recomenda corte automaticamente — apenas simula o efeito econômico.</div>",
                        unsafe_allow_html=True
                    )

            elif group=="Materiais":
                st.markdown("<div class='lever-kicker'>MATERIAIS</div><div class='lever-title'>Consumo, preço e perdas de matéria-prima</div>",unsafe_allow_html=True)
                a,b=st.columns(2,gap="medium")
                with a:
                    st.slider("Consumo específico MP (índice)",0.80,1.20,key="sim_mp_specific",step=.01,
                              help="1,00 representa o padrão. Valores acima de 1,00 indicam sobreconsumo.")
                    st.caption("Impacto: custo variável · Confiança: Alta")
                    st.slider("Redução de perdas de material (%)",0,50,key="sim_material_loss",step=1)
                    st.caption("Impacto: custo variável · Confiança: Alta")
                with b:
                    st.slider("Redução do preço de MP (%)",0.0,15.0,key="sim_mp_price",step=.5)
                    st.caption("Impacto: CMV / margem · Confiança: Alta")

            elif group=="Energia":
                st.markdown("<div class='lever-kicker'>ENERGIA</div><div class='lever-title'>Consumo específico e custo de transformação</div>",unsafe_allow_html=True)
                st.slider("Redução de kWh/unidade (%)",0.0,30.0,key="sim_energy",step=.5)
                st.caption("Impacto: custo de transformação / EBITDA · Confiança: Média")
                st.markdown(
                    "<div class='frontend-note'>O modelo usa o custo de energia real da base quando disponível. "
                    "A evolução futura pode usar kWh/unidade equivalente por produto/linha.</div>",
                    unsafe_allow_html=True
                )

            elif group=="Logística":
                st.markdown("<div class='lever-kicker'>LOGÍSTICA</div><div class='lever-title'>Custo de entrega e proteção de receita</div>",unsafe_allow_html=True)
                a,b=st.columns(2,gap="medium")
                with a:
                    st.slider("Redução do frete/unidade (%)",0.0,20.0,key="sim_freight",step=.5)
                    st.caption("Impacto: margem / EBITDA · Confiança: Alta")
                with b:
                    st.slider("OTIF (%)",50.0,100.0,key="sim_otif",step=.5)
                    st.caption("Impacto: receita protegida / pedidos · Confiança: Média")
                st.markdown(
                    "<div class='frontend-note'>OTIF não é tratado como receita automática. O motor estima receita em risco e reconhece apenas uma parcela conservadora do valor protegido.</div>",
                    unsafe_allow_html=True
                )

            elif group=="Financeiro":
                st.markdown("<div class='lever-kicker'>FINANCEIRO</div><div class='lever-title'>Preço, mix e volume vendido</div>",unsafe_allow_html=True)
                a,b=st.columns(2,gap="medium")
                with a:
                    st.slider("Variação do preço médio (%)",-10.0,15.0,key="sim_price",step=.5)
                    st.caption("Impacto: receita / EBITDA · Confiança: Alta")
                    st.slider("Variação do volume vendido (%)",-20.0,40.0,key="sim_volume",step=.5)
                    st.caption("Impacto: receita / contribuição · limitado à capacidade")
                with b:
                    st.slider("Efeito de mix na margem (pp)",-5.0,8.0,key="sim_mix",step=.1)
                    st.caption("Impacto: margem / EBITDA · Confiança: Média")
                    st.markdown(
                        "<div class='frontend-note'>O volume vendido monetiza a capacidade criada pelas alavancas operacionais. "
                        "Por isso, capacidade e volume não são somados como dois EBITDAs independentes.</div>",
                        unsafe_allow_html=True
                    )

            elif group=="Estrutura":
                st.markdown("<div class='lever-kicker'>ESTRUTURA</div><div class='lever-title'>Custo fixo e contratos/serviços</div>",unsafe_allow_html=True)
                a,b=st.columns(2,gap="medium")
                with a:
                    st.slider("Redução de custo fixo (%)",0.0,20.0,key="sim_fixed",step=.5)
                    st.caption("Impacto: EBITDA direto · Confiança: Alta")
                with b:
                    st.slider("Redução de contratos/serviços (%)",0.0,30.0,key="sim_contracts",step=.5)
                    st.caption("Impacto: SG&A / custo fabril · Confiança: Alta")
                st.markdown(
                    "<div class='frontend-note'>Contratos/serviços são tratados como um subconjunto da estrutura. "
                    "A redução de custo fixo é aplicada à parcela restante para evitar dupla contagem.</div>",
                    unsafe_allow_html=True
                )

            elif group=="Capital":
                st.markdown("<div class='lever-kicker'>CAPITAL</div><div class='lever-title'>Capital de giro e geração de caixa</div>",unsafe_allow_html=True)
                a,b=st.columns(2,gap="medium")
                with a:
                    st.slider("Redução de estoque (dias)",0,45,key="sim_inventory",step=1)
                    st.caption("Impacto: capital de giro / caixa · Confiança: Alta")
                    st.slider("Redução do prazo cliente (dias)",0,30,key="sim_dso",step=1)
                    st.caption("Impacto: caixa · Confiança: Alta")
                with b:
                    st.slider("Aumento do prazo fornecedor (dias)",0,30,key="sim_dpo",step=1)
                    st.caption("Impacto: caixa · Confiança: Alta")
                    st.markdown(
                        "<div class='frontend-note'>Capital de giro é exibido separado do EBITDA. "
                        "Estoque usa custo diário; cliente usa receita diária; fornecedor usa compras/MP diária.</div>",
                        unsafe_allow_html=True
                    )

    # ------------------------------------------------------------------
    # Causal calculation engine — conservative / no double counting
    # ------------------------------------------------------------------
    # Process levers -> technical availability recovery
    setup_red=max(0.0,(setup_base-st.session_state.sim_setup)/max(setup_base,1))
    unplanned_red=max(0.0,st.session_state.sim_unplanned/100)
    mttr_red=max(0.0,(mttr_base-st.session_state.sim_mttr)/max(mttr_base,1))
    downtime_share=max(0.0,1-D["availability"])
    process_recovery=downtime_share*(0.25*setup_red+0.45*unplanned_red+0.30*mttr_red)
    derived_availability=min(0.99,D["availability"]+process_recovery)

    if st.session_state.sim_prod_mode=="OEE direto":
        oee_target=max(0.01,st.session_state.sim_oee/100)
        process_oee=derived_availability*min(D["performance"],1.0)*D["quality"]
        effective_oee=max(oee_target,process_oee)
        efficiency_growth=max(0.0,safe_div(effective_oee,D["oee"])-1)
        effective_availability=max(D["availability"],derived_availability)
        effective_performance=D["performance"]
    else:
        manual_avail=st.session_state.sim_availability/100
        effective_availability=max(manual_avail,derived_availability)
        effective_performance=st.session_state.sim_performance/100
        # Keep quality base here; scrap/rework value is monetized separately to avoid double count
        effective_oee=effective_availability*min(effective_performance,1.0)*D["quality"]
        efficiency_growth=max(0.0,safe_div(effective_oee,D["oee"])-1)

    utilization_growth=max(0.0,safe_div(st.session_state.sim_capacity,capacity_base)-1)
    output_potential_growth=max(0.0,(1+efficiency_growth)*(1+utilization_growth)-1)
    capacity_revenue_potential=base_revenue*output_potential_growth
    capacity_ebitda_potential=capacity_revenue_potential*base_margin

    # Finance/demand: monetize only capacity that can be sold
    requested_volume_growth=st.session_state.sim_volume/100
    if requested_volume_growth>=0:
        realized_volume_growth=min(requested_volume_growth,output_potential_growth if output_potential_growth>0 else requested_volume_growth)
    else:
        realized_volume_growth=requested_volume_growth
    volume_revenue=base_revenue*realized_volume_growth
    volume_ebitda=volume_revenue*base_margin

    price_revenue=base_revenue*(st.session_state.sim_price/100)
    price_ebitda=price_revenue  # price effect with constant unit variable cost
    mix_ebitda=base_revenue*(st.session_state.sim_mix/100)

    # Quality
    scrap_reduction=max(0.0,(D["scrap"]*100-st.session_state.sim_scrap)/100)
    scrap_saving=scrap_reduction*base_mp
    rework_reduction=max(0.0,(rework_base-st.session_state.sim_rework)/100)
    rework_cost_pool=base_mod+base_energy
    rework_saving=rework_reduction*rework_cost_pool

    # People
    overtime_base_cost=max(0.0,D["overtime"]*30.0)
    overtime_saving=overtime_base_cost*(st.session_state.sim_overtime/100)
    prod_gain=max(0.0,safe_div(st.session_state.sim_productivity,base_productivity)-1)
    productivity_saving=base_mod*prod_gain*0.45
    headcount_effect=-st.session_state.sim_headcount*avg_monthly_person_cost  # negative HC => positive EBITDA

    # Materials
    mp_specific_reduction=max(0.0,(mp_specific_base-st.session_state.sim_mp_specific)/max(mp_specific_base,0.01))
    mp_specific_saving=base_mp*mp_specific_reduction
    mp_price_saving=base_mp*(st.session_state.sim_mp_price/100)
    material_loss_pool=base_mp*0.04
    material_loss_saving=material_loss_pool*(st.session_state.sim_material_loss/100)

    # Energy / logistics
    energy_saving=base_energy*(st.session_state.sim_energy/100)
    freight_base=base_var*freight_share
    freight_saving=freight_base*(st.session_state.sim_freight/100)

    otif_gap=max(1.0,100-otif_base)
    otif_improvement=max(0.0,st.session_state.sim_otif-otif_base)
    protected_revenue=base_revenue*otif_risk_share*min(1.0,otif_improvement/otif_gap)
    recognized_otif_revenue=protected_revenue*0.70
    otif_ebitda=recognized_otif_revenue*base_margin

    # Structure — contracts separated from remainder
    contracts_base=base_fixed*contracts_share
    fixed_ex_contracts=max(0.0,base_fixed-contracts_base)
    contracts_saving=contracts_base*(st.session_state.sim_contracts/100)
    fixed_saving=fixed_ex_contracts*(st.session_state.sim_fixed/100)

    # Capital / cash
    inventory_release=(base_var/period_days)*st.session_state.sim_inventory
    supplier_release=(base_mp/period_days)*st.session_state.sim_dpo
    customer_release=(base_revenue/period_days)*st.session_state.sim_dso
    working_capital_release=inventory_release+supplier_release+customer_release

    # Additive EBITDA — no duplicate capacity attribution
    cost_savings=(
        scrap_saving+rework_saving+overtime_saving+productivity_saving+headcount_effect+
        mp_specific_saving+mp_price_saving+material_loss_saving+energy_saving+
        freight_saving+contracts_saving+fixed_saving
    )
    revenue_add=volume_revenue+price_revenue+recognized_otif_revenue
    ebitda_gain=volume_ebitda+price_ebitda+mix_ebitda+otif_ebitda+cost_savings
    simulated_revenue=base_revenue+revenue_add
    simulated_ebitda=base_ebitda+ebitda_gain
    contribution_gain=(
        volume_ebitda+price_ebitda+mix_ebitda+otif_ebitda+
        scrap_saving+rework_saving+mp_specific_saving+mp_price_saving+
        material_loss_saving+energy_saving+freight_saving
    )
    simulated_contribution=base_revenue*base_margin+contribution_gain
    simulated_margin=safe_div(simulated_contribution,simulated_revenue)

    # Simulated fixed-cost absorption: same fixed cost divided by higher sold output, net of explicit structural savings
    base_fixed_per_unit=safe_div(base_fixed,D["actual"])
    simulated_units=max(1,D["actual"]*(1+realized_volume_growth))
    simulated_fixed_total=max(0,base_fixed-contracts_saving-fixed_saving)
    simulated_fixed_per_unit=safe_div(simulated_fixed_total,simulated_units)
    absorption_gain=max(0,base_fixed_per_unit-simulated_fixed_per_unit)

    # ------------------------------------------------------------------
    # Value attribution table
    # Production/process levers = enabling value; additive lines = bridge value
    # ------------------------------------------------------------------
    enable_pool=capacity_ebitda_potential
    enable_weights={}
    if st.session_state.sim_prod_mode=="OEE direto":
        enable_weights["OEE"]=max(0,efficiency_growth)
    else:
        avail_gain=max(0,effective_availability-D["availability"])
        perf_gain=max(0,effective_performance-D["performance"])
        enable_weights["Disponibilidade"]=avail_gain
        enable_weights["Performance"]=perf_gain
        # Attribute the process-derived part within availability
        if process_recovery>0:
            enable_weights["Setup médio"]=process_recovery*0.25*setup_red
            enable_weights["Paradas não planejadas"]=process_recovery*0.45*unplanned_red
            enable_weights["MTTR"]=process_recovery*0.30*mttr_red
    enable_weights["Capacidade utilizada"]=max(0,utilization_growth)
    total_enable_weight=sum(enable_weights.values()) or 1.0

    breakdown=[]
    for lever,w in enable_weights.items():
        breakdown.append([lever,enable_pool*w/total_enable_weight,"Valor habilitado","Alta" if lever!="Capacidade utilizada" else "Média"])

    additive_lines=[
        ("Refugo",scrap_saving,"EBITDA","Alta"),
        ("Retrabalho",rework_saving,"EBITDA","Alta"),
        ("Horas extras",overtime_saving,"EBITDA","Alta"),
        ("Produtividade",productivity_saving,"EBITDA","Alta"),
        ("Headcount",headcount_effect,"EBITDA","Alta"),
        ("Consumo específico MP",mp_specific_saving,"EBITDA","Alta"),
        ("Preço de MP",mp_price_saving,"EBITDA","Alta"),
        ("Perdas de material",material_loss_saving,"EBITDA","Alta"),
        ("kWh/unidade",energy_saving,"EBITDA","Média"),
        ("Frete/unidade",freight_saving,"EBITDA","Alta"),
        ("OTIF",otif_ebitda,"EBITDA / Receita protegida","Média"),
        ("Preço médio",price_ebitda,"EBITDA","Alta"),
        ("Mix de produtos",mix_ebitda,"EBITDA","Média"),
        ("Volume vendido",volume_ebitda,"EBITDA","Alta"),
        ("Custo fixo",fixed_saving,"EBITDA","Alta"),
        ("Contratos/serviços",contracts_saving,"EBITDA","Alta"),
        ("Estoque",inventory_release,"Caixa","Alta"),
        ("Prazo fornecedor",supplier_release,"Caixa","Alta"),
        ("Prazo cliente",customer_release,"Caixa","Alta"),
    ]
    breakdown.extend(additive_lines)
    breakdown_df=pd.DataFrame(breakdown,columns=["Alavanca","Impacto_R$","Tipo","Confiança"])
    breakdown_df["AbsImpact"]=breakdown_df["Impacto_R$"].abs()
    breakdown_df=breakdown_df.sort_values("AbsImpact",ascending=False).drop(columns=["AbsImpact"])

    active_count=int((breakdown_df["Impacto_R$"].abs()>1).sum())

    # ------------------------------------------------------------------
    # Impact panel
    # ------------------------------------------------------------------
    with right:
        with st.container(border=True, height=585):
            panel_title("Impacto do Cenário",f"{active_count} alavancas com efeito econômico no cenário")
            c1,c2=st.columns(2,gap="small")
            with c1:
                st.markdown(
                    f"<div class='sim-card'><div class='sim-card-label'>Receita simulada</div>"
                    f"<div class='sim-card-value'>{fmt_money(simulated_revenue)}</div>"
                    f"<div class='sim-card-delta' style='color:{GREEN if revenue_add>=0 else RED}'>Δ {fmt_money(revenue_add)}</div></div>",
                    unsafe_allow_html=True
                )
            with c2:
                st.markdown(
                    f"<div class='sim-card'><div class='sim-card-label'>EBITDA simulado</div>"
                    f"<div class='sim-card-value'>{fmt_money(simulated_ebitda)}</div>"
                    f"<div class='sim-card-delta' style='color:{GREEN if ebitda_gain>=0 else RED}'>Δ {fmt_money(ebitda_gain)}</div></div>",
                    unsafe_allow_html=True
                )
            st.write("")
            c1,c2=st.columns(2,gap="small")
            with c1:
                st.markdown(
                    f"<div class='sim-card'><div class='sim-card-label'>Margem estimada</div>"
                    f"<div class='sim-card-value'>{fmt_pct(simulated_margin)}</div>"
                    f"<div class='sim-card-delta' style='color:{GREEN if simulated_margin>=base_margin else RED}'>base {fmt_pct(base_margin)}</div></div>",
                    unsafe_allow_html=True
                )
            with c2:
                st.markdown(
                    f"<div class='sim-card'><div class='sim-card-label'>Capital de giro liberado</div>"
                    f"<div class='sim-card-value'>{fmt_money(working_capital_release)}</div>"
                    f"<div class='sim-card-delta' style='color:{BLUE}'>efeito caixa</div></div>",
                    unsafe_allow_html=True
                )

            st.write("")
            st.markdown(
                f"<div class='lever-shell'>"
                f"<div class='lever-kicker'>CAPACIDADE</div>"
                f"<div class='lever-title'>Valor potencial habilitado: {fmt_money(capacity_ebitda_potential)}</div>"
                f"<div class='lever-meta'>OEE efetivo {effective_oee:.1%} · utilização {st.session_state.sim_capacity:.1f}% · "
                f"potencial de volume {output_potential_growth:.1%}. Esse valor não é somado novamente ao EBITDA se o volume vendido já o monetiza.</div>"
                f"</div>",
                unsafe_allow_html=True
            )
            st.write("")
            st.markdown(
                f"<div class='lever-shell'>"
                f"<div class='lever-kicker'>ABSORÇÃO</div>"
                f"<div class='lever-title'>Custo fixo/un: {fmt_money(base_fixed_per_unit,2)} → {fmt_money(simulated_fixed_per_unit,2)}</div>"
                f"<div class='lever-meta'>Ganho de absorção: {fmt_money(absorption_gain,2)}/un. A utilização maior não reduz o custo fixo total por si só.</div>"
                f"</div>",
                unsafe_allow_html=True
            )

    # ------------------------------------------------------------------
    # Bridge + value map
    # ------------------------------------------------------------------
    st.write("")
    c1,c2=st.columns([1.08,.92],gap="small")
    with c1:
        with st.container(border=True, height=410):
            panel_title("Bridge de EBITDA","Somente impactos aditivos — sem dupla contagem")
            bridge={
                "Volume vendido":volume_ebitda,
                "Preço":price_ebitda,
                "Mix":mix_ebitda,
                "Qualidade":scrap_saving+rework_saving,
                "Pessoas":overtime_saving+productivity_saving+headcount_effect,
                "Materiais":mp_specific_saving+mp_price_saving+material_loss_saving,
                "Energia/Logística":energy_saving+freight_saving+otif_ebitda,
                "Estrutura":fixed_saving+contracts_saving,
            }
            bridge={k:v for k,v in bridge.items() if abs(v)>1}
            x=["EBITDA Atual"]+list(bridge.keys())+["EBITDA Simulado"]
            measures=["absolute"]+["relative"]*len(bridge)+["total"]
            y=[base_ebitda]+list(bridge.values())+[0]
            fig=go.Figure(go.Waterfall(
                x=x,measure=measures,y=y,
                increasing={"marker":{"color":GREEN}},
                decreasing={"marker":{"color":RED}},
                totals={"marker":{"color":BLUE}},
                connector={"line":{"color":"#BBC8D3","width":1}}
            ))
            fig.update_layout(
                height=335,margin=dict(l=5,r=5,t=10,b=55),
                paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(gridcolor="#EFF3F7",tickfont=dict(size=9)),
                xaxis=dict(tickfont=dict(size=9),tickangle=-20,automargin=True),
                showlegend=False
            )
            st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

    with c2:
        with st.container(border=True, height=410):
            panel_title("Mapa de Valor","Impacto por alavanca e natureza do valor")
            show=breakdown_df[breakdown_df["Impacto_R$"].abs()>1].head(10).copy()
            show["Impacto"]=show["Impacto_R$"].map(lambda x:fmt_money(x))
            show=show[["Alavanca","Tipo","Impacto","Confiança"]]
            st.dataframe(
                show,use_container_width=True,hide_index=True,height=335,
                column_config={
                    "Alavanca":st.column_config.TextColumn("Alavanca",width="medium"),
                    "Tipo":st.column_config.TextColumn("Natureza",width="medium"),
                    "Impacto":st.column_config.TextColumn("Impacto",width="medium"),
                    "Confiança":st.column_config.TextColumn("Confiança",width="small"),
                }
            )

    st.write("")
    with st.container(border=True):
        c1,c2=st.columns([1,.33],gap="small")
        with c1:
            st.markdown(
                "<div class='frontend-note'><b>Regra do motor:</b> capacidade operacional pode habilitar receita, mas só entra no EBITDA quando existe volume vendido para monetizá-la. "
                "OEE não é somado com seus drivers; setup/paradas/MTTR alimentam disponibilidade; contratos são separados do restante do custo fixo; capital de giro fica fora do EBITDA.</div>",
                unsafe_allow_html=True
            )
        with c2:
            if st.button("Transformar cenário em Plano de Captura",type="primary",use_container_width=True):
                top_actions=breakdown_df[
                    (breakdown_df["Impacto_R$"]>1) &
                    (breakdown_df["Tipo"].str.contains("EBITDA|Valor habilitado",regex=True))
                ].head(5)

                owner_map={
                    "OEE":"Ger. Industrial","Disponibilidade":"Ger. Manutenção","Performance":"Ger. Produção",
                    "Capacidade utilizada":"Ger. Industrial","Setup médio":"Engenharia de Processos",
                    "Paradas não planejadas":"Ger. Manutenção","MTTR":"Ger. Manutenção",
                    "Refugo":"Ger. Qualidade","Retrabalho":"Ger. Qualidade",
                    "Horas extras":"Ger. Produção","Produtividade":"Ger. Produção","Headcount":"Ger. Industrial",
                    "Consumo específico MP":"Engenharia de Processos","Preço de MP":"Controller / Operações",
                    "Perdas de material":"Ger. Qualidade","kWh/unidade":"Ger. Industrial",
                    "Frete/unidade":"Controller / Operações","OTIF":"Ger. Produção",
                    "Preço médio":"Controller / Operações","Mix de produtos":"Controller / Operações",
                    "Volume vendido":"Ger. Industrial","Custo fixo":"Controller / Operações",
                    "Contratos/serviços":"Controller / Operações"
                }
                action_map={
                    "OEE":"Executar plano para atingir o OEE simulado, detalhando perdas de disponibilidade, performance e qualidade.",
                    "Disponibilidade":"Atacar as maiores perdas de disponibilidade e equipamentos críticos.",
                    "Performance":"Eliminar perdas de velocidade e microparadas versus padrão.",
                    "Capacidade utilizada":"Converter capacidade disponível em volume vendável sem aumentar estrutura fixa.",
                    "Setup médio":"Aplicar SMED e preparação externa nos setups prioritários.",
                    "Paradas não planejadas":"Plano de confiabilidade para reduzir paradas não planejadas.",
                    "MTTR":"Reduzir tempo de reparo com padrão de atendimento, sobressalentes e troubleshooting.",
                    "Refugo":"Pareto de refugo por produto/causa e ajuste de parâmetros de processo.",
                    "Retrabalho":"Eliminar causas de retrabalho e recuperar MOD/energia/capacidade.",
                    "Horas extras":"Rebalancear escala e capacidade para reduzir hora extra sem perder volume.",
                    "Produtividade":"Atacar perdas de HH usando produtividade linearizada pelo mix.",
                    "Headcount":"Revisar dimensionamento e capacidade antes de qualquer alteração de quadro.",
                    "Consumo específico MP":"Comparar consumo real x padrão e atacar sobreconsumo por SKU/processo.",
                    "Preço de MP":"Executar sourcing/negociação para capturar redução de preço de matéria-prima.",
                    "Perdas de material":"Reduzir perdas de processo fora do refugo já contabilizado.",
                    "kWh/unidade":"Atacar consumo específico de energia por linha/produto.",
                    "Frete/unidade":"Rever malha, ocupação, frequência e contratação para reduzir frete/unidade.",
                    "OTIF":"Atacar restrições de PCP, material e expedição que comprometem entrega.",
                    "Preço médio":"Executar plano de preço preservando elasticidade e volume.",
                    "Mix de produtos":"Aumentar participação de produtos/famílias de maior margem.",
                    "Volume vendido":"Converter capacidade em vendas adicionais respeitando demanda e margem.",
                    "Custo fixo":"Revisar estrutura e capacidade ociosa para capturar redução sustentável.",
                    "Contratos/serviços":"Renegociar, redimensionar ou eliminar contratos sem retorno adequado."
                }
                rows=[]
                for _,r in top_actions.iterrows():
                    lever=r["Alavanca"]
                    owner=owner_map.get(lever,"Ger. Industrial")
                    rows.append([
                        "Alta" if r["Impacto_R$"]>=top_actions["Impacto_R$"].median() else "Média",
                        f"Cenário: {lever}",
                        action_map.get(lever,f"Executar plano de captura da alavanca {lever}."),
                        owner,owner_email(owner),"45 dias",fmt_money(r["Impacto_R$"]),"Planejado"
                    ])
                if rows:
                    new_actions=pd.DataFrame(rows,columns=st.session_state.actions.columns)
                    st.session_state.actions=pd.concat([st.session_state.actions,new_actions],ignore_index=True)
                nav("Plano de Ação")


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
        refugo em <b>{D["scrap"]:.1%}</b> e margem de contribuição em <b>{D["margin"]:.1%}</b>.
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
Margem de contribuição: {D["margin"]:.1%}
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

elif page == "Configurações":
    page_header("Configurações","Importe dados, valide o modelo e atualize o cockpit.")
    tabs = st.tabs(["Importação de Dados","Metas","Estrutura de Custos","Integrações"])

    with tabs[0]:
        st.markdown("#### Importar Excel")
        st.caption("Fluxo: carregar → validar → revisar padrões de produto → aplicar ao cockpit. Para ambiente multiproduto, Padroes_Produto é obrigatório para linearizar o mix.")
        uploaded = st.file_uploader("Arquivo Excel", type=["xlsx","xls"], accept_multiple_files=False)

        if uploaded is not None:
            data,issues = parse_excel(uploaded.getvalue())
            if issues:
                st.error("O arquivo foi carregado, mas ainda não está compatível com o modelo.")
                for issue in issues:
                    st.write("•", issue)
            else:
                st.success("Estrutura validada com sucesso.")
                st.write("Abas reconhecidas:")
                st.write(", ".join([k.title() for k in data.keys()]))
                preview_sheet = st.selectbox("Prévia da aba", list(data.keys()))
                st.dataframe(data[preview_sheet].head(20), use_container_width=True, hide_index=True)
                if st.button("Aplicar dados ao cockpit", type="primary"):
                    st.session_state.real_data = data
                    st.session_state.page = "Cockpit Executivo"
                    st.rerun()

        if st.session_state.real_data is not None:
            st.write("")
            if st.button("Voltar para dados demo"):
                st.session_state.real_data = None
                st.rerun()

    with tabs[1]:
        st.info("Próxima evolução: metas persistentes por indicador, linha e período.")
    with tabs[2]:
        st.info("Próxima evolução: plano de contas gerencial + classificação fixo/variável + DE/PARA.")
    with tabs[3]:
        st.info("Roadmap: ERP, MES, WMS, CMMS, SQL e APIs.")
