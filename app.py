
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from io import BytesIO
import unicodedata

# ============================================================
# CONFIG
# ============================================================
st.set_page_config(
    page_title="Industrial Performance | H2M",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Palette H2M + ZeroBaseTrack
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
SOFT_BLUE = "#EAF6FE"
SOFT_GREEN = "#EAF8F2"
SOFT_ORANGE = "#FFF5E9"
SOFT_RED = "#FFF0EF"

# ============================================================
# GLOBAL CSS / DESIGN SYSTEM
# ============================================================
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
    padding: .35rem 1.35rem 2rem 1.35rem;
}}

[data-testid="stSidebar"] {{
    background:linear-gradient(180deg,{NAVY} 0%,{NAVY_2} 100%);
    border-right:0;
    width:272px !important;
}}
[data-testid="stSidebar"] > div:first-child {{width:272px !important;}}
[data-testid="stSidebar"] .block-container {{padding:1rem .85rem 1.1rem;}}

[data-testid="stSidebar"] .stButton>button {{
    width:100%;
    min-height:38px;
    justify-content:flex-start;
    padding:.42rem .7rem;
    border:0;
    border-radius:8px;
    background:transparent;
    color:#D8E4EE;
    box-shadow:none;
    font-size:.78rem;
    font-weight:650;
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

.brand-wrap {{
    display:flex;
    align-items:center;
    gap:8px;
    margin:0 0 12px 0;
}}
.brand-title {{
    color:white;
    font-weight:850;
    font-size:.82rem;
    line-height:1.1;
}}
.brand-sub {{
    color:#9FB5C7;
    font-size:.60rem;
    margin-top:2px;
}}
.menu-group {{
    color:#77DDF8;
    font-size:.54rem;
    letter-spacing:.11em;
    font-weight:850;
    margin:14px 7px 5px;
}}
.sidebar-footer {{
    margin-top:16px;
    padding:10px 5px 0;
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
    margin:.08rem 0 0 0;
}}
.page-subtitle {{
    font-size:.79rem;
    color:{MUTED};
    margin:.24rem 0 .9rem 0;
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
    height:102px;
    box-sizing:border-box;
    background:{WHITE};
    border:1px solid {BORDER};
    border-radius:12px;
    padding:12px 13px;
    box-shadow:0 3px 12px rgba(10,35,60,.03);
    overflow:hidden;
}}
.kpi-label {{
    height:17px;
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
    color:{MUTED};
    font-size:.64rem;
    font-weight:760;
}}
.kpi-value {{
    color:{TEXT};
    font-size:1.36rem;
    line-height:1.08;
    font-weight:860;
    letter-spacing:-.034em;
    margin:.34rem 0 .20rem;
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

.panel {{
    box-sizing:border-box;
    background:{WHITE};
    border:1px solid {BORDER};
    border-radius:12px;
    padding:13px 14px;
    box-shadow:0 3px 12px rgba(10,35,60,.03);
}}
.panel.h355 {{height:355px;overflow:hidden;}}
.panel.h300 {{height:300px;overflow:hidden;}}
.panel.h270 {{height:270px;overflow:hidden;}}
.panel-title {{
    font-size:.88rem;
    font-weight:850;
    color:{TEXT};
    margin-bottom:2px;
}}
.panel-sub {{
    font-size:.60rem;
    color:{MUTED};
    margin-bottom:7px;
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

.section-tabs {{
    font-size:.62rem;
    color:{MUTED};
}}
.small {{font-size:.59rem;color:{MUTED};}}

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
.stTabs [data-baseweb="tab-list"] {{
    gap:4px;
}}
.stTabs [data-baseweb="tab"] {{
    height:36px;
    border-radius:8px;
    padding:0 12px;
    font-size:.70rem;
    font-weight:750;
}}
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA ENGINE
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
    "metas":["metas","targets","goals"]
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
    "metas":{"indicador":["indicador","kpi","metric"],"meta":["meta","target","goal"]}
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
        "producao":["data","linha","planejado","realizado","horas_disponiveis","horas_paradas","velocidade_real","velocidade_nominal"],
        "qualidade":["data","linha","produzido","aprovado","refugo"],
        "manutencao":["data","linha","maquina","duracao_horas","causa"],
        "pessoas":["data","linha","horas_normais","horas_extras"],
        "custos":["data","linha","custo_mp","custo_mod","custo_energia","custo_manutencao","receita"],
    }
    issues=[]
    for sh, cols in required.items():
        if sh not in data:
            issues.append(f"Aba ausente: {sh.title()}")
        else:
            miss=[c for c in cols if c not in data[sh].columns]
            if miss:
                issues.append(f"{sh.title()}: faltam {', '.join(miss)}")
    if issues:
        return None, issues
    for _,df in data.items():
        if "data" in df.columns:
            df["data"]=pd.to_datetime(df["data"],errors="coerce")
    return data, []

def target_from(data, names, default):
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

def calculate_real(data):
    p=data["producao"].copy()
    q=data["qualidade"].copy()
    m=data["manutencao"].copy()
    pe=data["pessoas"].copy()
    c=data["custos"].copy()

    for col in ["planejado","realizado","horas_disponiveis","horas_paradas","velocidade_real","velocidade_nominal"]:
        p[col]=nseries(p[col])
    for col in ["produzido","aprovado","refugo"]:
        q[col]=nseries(q[col])
    m["duracao_horas"]=nseries(m["duracao_horas"])
    for col in ["horas_normais","horas_extras"]:
        pe[col]=nseries(pe[col])
    for col in ["custo_mp","custo_mod","custo_energia","custo_manutencao","receita"]:
        c[col]=nseries(c[col])
    if "custo_fixo" in c.columns:
        c["custo_fixo"]=nseries(c["custo_fixo"])
    else:
        c["custo_fixo"]=0

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

    var_cost=c[["custo_mp","custo_mod","custo_energia","custo_manutencao"]].sum().sum()
    fixed_cost=c["custo_fixo"].sum()
    revenue=c["receita"].sum()
    total_cost=var_cost+fixed_cost
    contrib=revenue-var_cost
    ebitda=revenue-total_cost
    margin_contrib=safe_div(contrib,revenue)
    cost_unit=safe_div(total_cost,actual)

    overtime=pe["horas_extras"].sum()
    hours=pe["horas_normais"].sum()+overtime
    productivity=safe_div(actual,hours)

    t_oee=target_from(data,["OEE"],0.78)
    t_scrap=target_from(data,["Refugo","Taxa Refugo"],0.025)
    t_margin=target_from(data,["Margem","Margem Contribuição"],0.31)

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

    causes=m.groupby("causa",as_index=False)["duracao_horas"].sum().rename(columns={"duracao_horas":"Horas"})
    if not causes.empty:
        margin_unit=safe_div(contrib,actual)
        units_h=safe_div(actual,max(1,hours))
        causes["Impacto R$ mil"]=causes["Horas"]*units_h*margin_unit/1000
        causes=causes.sort_values("Horas",ascending=False).head(6)

    kpis=[
        ("Produção",f"{actual:,.0f} un".replace(",","."),f"{planned:,.0f}".replace(",","."),attainment-1,f"{attainment-1:+.1%}".replace(".",","),"↑" if attainment>=1 else "↓"),
        ("OEE",fmt_pct(oee),fmt_pct(t_oee),safe_div(oee,t_oee)-1,f"{(oee-t_oee)*100:+.1f} pp".replace(".",","),"↑" if oee>=t_oee else "↓"),
        ("Produtividade",f"{productivity:.1f} un/h".replace(".",","),"—",0,"—","→"),
        ("Refugo",fmt_pct(scrap),fmt_pct(t_scrap),1-safe_div(scrap,t_scrap),f"{(scrap-t_scrap)*100:+.1f} pp".replace(".",","),"↓" if scrap<=t_scrap else "↑"),
        ("OTIF","—","—",0,"—","→"),
        ("Custo/unidade",fmt_money(cost_unit,2),"—",0,"—","→"),
        ("Horas extras",f"{overtime:,.0f} h".replace(",","."),"—",0,"—","→"),
        ("Margem contribuição",fmt_pct(margin_contrib),fmt_pct(t_margin),safe_div(margin_contrib,t_margin)-1,f"{(margin_contrib-t_margin)*100:+.1f} pp".replace(".",","),"↑" if margin_contrib>=t_margin else "↓"),
    ]

    margin_score=safe_div(margin_contrib,t_margin)-1
    cards=[
        ("Receita Líquida",fmt_money(revenue),attainment-1,f"{attainment-1:+.1%} vs. plano".replace(".",",")),
        ("Margem Contrib.",fmt_pct(margin_contrib),margin_score,f"{(margin_contrib-t_margin)*100:+.1f} pp vs. meta".replace(".",",")),
        ("EBITDA Industrial",fmt_money(ebitda),margin_score,f"{margin_score:+.1%} vs. ref.".replace(".",",")),
        ("Produção",f"{actual:,.0f} un".replace(",","."),attainment-1,f"{attainment-1:+.1%} vs. meta".replace(".",",")),
        ("OEE",fmt_pct(oee),safe_div(oee,t_oee)-1,f"{(oee-t_oee)*100:+.1f} pp vs. meta".replace(".",",")),
        ("Custo / un.",fmt_money(cost_unit,2),0,"calculado no período"),
    ]

    loss_prod=max(0,planned-actual)*safe_div(contrib,max(1,actual))
    loss_scrap=q["refugo"].sum()*safe_div(total_cost,max(1,actual))
    loss_down=m["duracao_horas"].sum()*safe_div(actual,max(1,hours))*safe_div(contrib,max(1,actual))
    impacts=pd.DataFrame({
        "Impacto":["Gap de produção","Refugo","Paradas","Horas extras","Consumo / mix"],
        "R$":[loss_prod,loss_scrap,loss_down,overtime*30,max(0,total_cost*0.015)]
    }).sort_values("R$",ascending=False)

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
        "cost_unit":cost_unit,"overtime":overtime,"productivity":productivity
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
        ("Produtividade","18,2 un/h","19,5",-0.067,"-6,7%","→"),
        ("Refugo","3,8%","2,5%",-0.52,"+1,3 pp","↑"),
        ("OTIF","89%","95%",-0.063,"-6 pp","↓"),
        ("Custo/unidade","R$ 18,42","R$ 17,10",-0.077,"+7,7%","↑"),
        ("Horas extras","1.280 h","900 h",-0.422,"+42%","↑"),
        ("Margem contribuição","27,8%","31%",-0.103,"-3,2 pp","↓"),
    ]
    impacts=pd.DataFrame({"Impacto":["Menor volume","Refugo","Horas extras","Manutenção","Consumo MP"],"R$":[220000,110000,95000,75000,48000]})
    dre=pd.DataFrame({
        "Linha":["Receita Líquida","(-) Custos Variáveis","Margem de Contribuição","(-) Custos Fixos","EBITDA Industrial"],
        "Realizado":[12400000,-8950000,3450000,-1550000,1900000]
    })
    return {
        "cards":cards,"kpis":kpis,"trend":trend,"line_perf":line_perf,"causes":causes,"impacts":impacts,
        "dre":dre,"cost_structure":{"Variável":8950000,"Fixo":1550000},
        "oee":.714,"target_oee":.78,"scrap":.038,"target_scrap":.025,
        "attainment":.917,"margin":.278,"target_margin":.31,
        "ebitda":1900000,"revenue":12400000,"actual":41250,"planned":45000,
        "availability":.748,"performance":.945,"quality":.981,
        "cost_unit":18.42,"overtime":1280,"productivity":18.2
    }

# ============================================================
# SESSION
# ============================================================
if "page" not in st.session_state:
    st.session_state.page="Cockpit Executivo"
if "real_data" not in st.session_state:
    st.session_state.real_data=None
if "actions" not in st.session_state:
    st.session_state.actions=pd.DataFrame([
        ["Alta","Disponibilidade Linha 3","Plano de confiabilidade MX-04","Ger. Manutenção","10/09/2026","R$ 312 mil","Em andamento"],
        ["Alta","Refugo Produto A","Revisar parâmetros de processo","Ger. Qualidade","12/09/2026","R$ 214 mil","Não iniciado"],
        ["Média","Horas extras","Redimensionar turnos","Ger. Produção","15/09/2026","R$ 88 mil","Em andamento"],
    ],columns=["Prioridade","Problema","Ação","Responsável","Prazo","Impacto","Status"])

D = calculate_real(st.session_state.real_data) if st.session_state.real_data else demo_dataset()

# ============================================================
# UI HELPERS
# ============================================================
def nav(page):
    st.session_state.page=page
    st.rerun()

def page_header(title,subtitle):
    c1,c2,c3,c4=st.columns([1.05,1.05,.8,1.4],gap="small")
    c1.selectbox("Grupo",["Grupo Industrial S.A."],label_visibility="collapsed",key=f"g_{title}")
    c2.selectbox("Planta",["Planta São Paulo","Todas as plantas"],label_visibility="collapsed",key=f"p_{title}")
    c3.selectbox("Período",["Ago/2026","Jul/2026","Jun/2026"],label_visibility="collapsed",key=f"d_{title}")
    mode="Dados importados" if st.session_state.real_data else "Dados demo"
    c4.markdown(f'<div style="text-align:right;padding-top:.2rem"><span class="data-badge">{mode}</span></div>',unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">EXECUÇÃO HOJE. COMPETITIVIDADE AMANHÃ.</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="page-title">{title}</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{subtitle}</div>',unsafe_allow_html=True)

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

def table_kpis():
    rows=[]
    for ind,mes,meta,score,delta,tend in D["kpis"]:
        c=score_color(score)
        rows.append(f"<tr><td>{ind}</td><td>{mes}</td><td>{meta}</td>"
                    f"<td style='color:{c};font-weight:850'>{delta}</td>"
                    f"<td style='color:{c};font-weight:850'>{tend}</td></tr>")
    return f"""
    <div class="panel h355">
      <div class="panel-title">Principais Indicadores</div>
      <div class="panel-sub">Realizado, meta, desvio e tendência</div>
      <table class="kpi-table">
        <colgroup><col style="width:34%"><col style="width:19%"><col style="width:17%"><col style="width:20%"><col style="width:10%"></colgroup>
        <thead><tr><th>Indicador</th><th>Mês</th><th>Meta</th><th>Desvio</th><th>Tend.</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </div>"""

def panel_title(title,sub=None):
    st.markdown(
        f'<div class="panel-title">{title}</div>' +
        (f'<div class="panel-sub">{sub}</div>' if sub else ''),
        unsafe_allow_html=True
    )

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    # Discreet brand lockup
    c1,c2=st.columns([.33,.67],gap="small")
    logo=Path(__file__).parent/"logo_h2m_white.jpeg"
    with c1:
        if logo.exists():
            st.image(str(logo),width=62)
    with c2:
        st.markdown(
            '<div class="brand-wrap"><div>'
            '<div class="brand-title">Industrial Performance</div>'
            '<div class="brand-sub">by H2M Consulting</div>'
            '</div></div>',
            unsafe_allow_html=True
        )

    groups = [
        ("VISÃO", ["Cockpit Executivo","Performance Operacional","Diagnóstico e Causas"]),
        ("RESULTADO", ["Finanças / DRE","Alavancas de Valor","Plano de Ação"]),
        ("INTELIGÊNCIA", ["Agente de Performance","Relatórios"]),
        ("ADMINISTRAÇÃO", ["Configurações"]),
    ]
    for group, items in groups:
        st.markdown(f'<div class="menu-group">{group}</div>',unsafe_allow_html=True)
        for p in items:
            if st.button(p,key=f"nav_{p}",type="primary" if st.session_state.page==p else "secondary",use_container_width=True):
                nav(p)

    st.markdown(
        '<div class="sidebar-footer"><b>Da operação ao resultado.</b><br>'
        '<small>PESSOAS &nbsp;&nbsp; DADOS &nbsp;&nbsp; AÇÃO</small></div>',
        unsafe_allow_html=True
    )

# ============================================================
# COCKPIT
# ============================================================
page=st.session_state.page

if page=="Cockpit Executivo":
    page_header("Cockpit Executivo","Performance operacional e impacto financeiro em uma única leitura.")

    cols=st.columns(6,gap="small")
    for col,item in zip(cols,D["cards"]):
        with col:
            st.markdown(kpi_card(*item),unsafe_allow_html=True)

    st.write("")
    left,mid,right=st.columns([1.00,1.25,.72],gap="small")

    with left:
        st.markdown(table_kpis(),unsafe_allow_html=True)

    with mid:
        st.markdown('<div class="panel h355">',unsafe_allow_html=True)
        panel_title("Tendência de Produção","Realizado versus plano — leitura contínua")
        trend=D["trend"].copy()
        x=trend["data"] if "data" in trend.columns else np.arange(len(trend))
        fig=go.Figure()
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
            height=292,margin=dict(l=4,r=4,t=10,b=6),
            paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h",y=1.08,x=0,font=dict(size=10)),
            xaxis=dict(showgrid=False,zeroline=False,tickfont=dict(size=9,color=MUTED)),
            yaxis=dict(gridcolor="#EFF3F7",zeroline=False,tickfont=dict(size=9,color=MUTED)),
            hovermode="x unified"
        )
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        st.markdown('</div>',unsafe_allow_html=True)

    with right:
        st.markdown('<div class="panel h355">',unsafe_allow_html=True)
        panel_title("Saúde da Fábrica","Status consolidado dos KPIs")
        scores=[x[3] for x in D["kpis"]]
        green=sum(1 for s in scores if s>=0)
        orange=sum(1 for s in scores if -0.10<=s<0)
        red=sum(1 for s in scores if s<-0.10)
        total=max(1,len(scores))
        fig=go.Figure(go.Pie(
            labels=["Em linha","Atenção","Crítico"],
            values=[green,orange,red],
            hole=.74,
            marker=dict(colors=[GREEN,ORANGE,RED],line=dict(width=0)),
            textinfo="none",
            hovertemplate="%{label}: %{value}<extra></extra>"
        ))
        pct=int(round(green/total*100))
        fig.update_layout(
            height=205,margin=dict(l=0,r=0,t=0,b=0),showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            annotations=[dict(text=f"<b>{pct}%</b><br><span style='font-size:10px'>em linha</span>",
                              x=.5,y=.5,showarrow=False,font=dict(size=16,color=TEXT))]
        )
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        st.markdown(
            f"<div class='small'><span class='dot' style='background:{GREEN}'></span>{green} em linha&nbsp;&nbsp;"
            f"<span class='dot' style='background:{ORANGE}'></span>{orange} atenção&nbsp;&nbsp;"
            f"<span class='dot' style='background:{RED}'></span>{red} crítico</div>",
            unsafe_allow_html=True
        )
        st.write("")
        var=D["cost_structure"]["Variável"]; fixed=D["cost_structure"]["Fixo"]; totalc=max(1,var+fixed)
        vp=var/totalc*100; fp=fixed/totalc*100
        st.markdown(
            f"<div class='panel-sub' style='margin-top:5px'>Estrutura de custos</div>"
            f"<div style='height:8px;border-radius:6px;overflow:hidden;display:flex'>"
            f"<div style='width:{vp:.1f}%;background:{BLUE}'></div>"
            f"<div style='width:{fp:.1f}%;background:#BBD8EC'></div></div>"
            f"<div style='display:flex;justify-content:space-between;margin-top:6px;font-size:.60rem'>"
            f"<span>Variável <b>{vp:.0f}%</b></span><span>Fixo <b>{fp:.0f}%</b></span></div>",
            unsafe_allow_html=True
        )
        st.markdown('</div>',unsafe_allow_html=True)

    st.write("")
    c1,c2,c3=st.columns([1.02,1.05,.88],gap="small")

    with c1:
        st.markdown('<div class="panel h300">',unsafe_allow_html=True)
        panel_title("Impactos no Resultado","Principais perdas traduzidas em R$")
        imp=D["impacts"].sort_values("R$").tail(5)
        fig=go.Figure(go.Bar(
            x=imp["R$"],y=imp["Impacto"],orientation="h",
            marker=dict(color="#E85B55"),
            text=[fmt_money(v,0) for v in imp["R$"]],
            textposition="outside",
            hovertemplate="%{y}<br>%{text}<extra></extra>"
        ))
        fig.update_layout(
            height=236,margin=dict(l=4,r=72,t=6,b=4),
            paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False,showticklabels=False,zeroline=False),
            yaxis=dict(showgrid=False,tickfont=dict(size=9,color=TEXT)),
            showlegend=False
        )
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        st.markdown('</div>',unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="panel h300">',unsafe_allow_html=True)
        panel_title("Alavancas Prioritárias","Onde atacar primeiro para recuperar resultado")
        lev=[
            ("Disponibilidade","Linha 3",312000,"Alta"),
            ("Refugo","Produto A",214000,"Alta"),
            ("Setup","Linha 2",96000,"Média"),
            ("Horas extras","Operação",88000,"Média"),
            ("Consumo MP","Mix",72000,"Baixa"),
        ]
        for name,scope,impact,prio in lev:
            if prio=="Alta": bc,bg=RED,SOFT_RED
            elif prio=="Média": bc,bg=ORANGE,SOFT_ORANGE
            else: bc,bg=GREEN,SOFT_GREEN
            st.markdown(
                f"<div style='display:grid;grid-template-columns:1.35fr .8fr .82fr .58fr;gap:7px;"
                f"align-items:center;padding:7px 0;border-bottom:1px solid #EEF2F6;font-size:.64rem'>"
                f"<div><b>{name}</b><br><span style='color:{MUTED};font-size:.55rem'>{scope}</span></div>"
                f"<div>{fmt_money(impact,0)}</div>"
                f"<div style='color:{MUTED}'>potencial</div>"
                f"<div><span class='priority' style='color:{bc};background:{bg}'>{prio}</span></div></div>",
                unsafe_allow_html=True
            )
        st.markdown('</div>',unsafe_allow_html=True)
        if st.button("Abrir alavancas",use_container_width=True):
            nav("Alavancas de Valor")

    with c3:
        st.markdown('<div class="panel h300">',unsafe_allow_html=True)
        panel_title("Alertas Executivos","Desvios que exigem atenção")
        alerts=[
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
        st.markdown('</div>',unsafe_allow_html=True)
        if st.button("Abrir diagnóstico",use_container_width=True):
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
    """,unsafe_allow_html=True)
    st.write("")
    if st.button("Conversar com o Agente de Performance",type="primary"):
        nav("Agente de Performance")

# ============================================================
# PERFORMANCE
# ============================================================
elif page=="Performance Operacional":
    page_header("Performance Operacional","Eficiência, capacidade e perdas por linha.")
    lp=D["line_perf"].copy()

    c1,c2,c3,c4=st.columns(4,gap="small")
    c1.metric("OEE",fmt_pct(D["oee"]),f"{(D['oee']-D['target_oee'])*100:+.1f} pp".replace(".",","))
    c2.metric("Disponibilidade",fmt_pct(D["availability"]))
    c3.metric("Performance",fmt_pct(D["performance"]))
    c4.metric("Qualidade",fmt_pct(D["quality"]))

    st.write("")
    c1,c2=st.columns(2,gap="small")

    with c1:
        st.markdown('<div class="panel">',unsafe_allow_html=True)
        panel_title("OEE por Linha","Comparação com meta")
        colors=[score_color(safe_div(v,D["target_oee"])-1) for v in lp["OEE"]]
        fig=go.Figure(go.Bar(
            x=lp["Linha"],y=lp["OEE"],marker_color=colors,
            text=[fmt_pct(x) for x in lp["OEE"]],textposition="outside"
        ))
        fig.add_hline(y=D["target_oee"],line_dash="dot",line_color="#9AAABD",annotation_text="Meta")
        fig.update_layout(height=300,margin=dict(l=0,r=0,t=8,b=0),
                          paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                          yaxis=dict(tickformat=".0%",gridcolor="#EFF3F7",range=[0,1]),
                          xaxis=dict(showgrid=False),showlegend=False)
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        st.markdown('</div>',unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="panel">',unsafe_allow_html=True)
        panel_title("Paradas x Gap de Produção","Quanto mais à direita e abaixo, pior")
        fig=go.Figure(go.Scatter(
            x=lp["Paradas h"],y=lp["Gap Produção"],mode="markers+text",
            text=lp["Linha"],textposition="top center",
            marker=dict(size=np.clip(lp["Paradas h"],16,42),color=BLUE,opacity=.78,line=dict(width=2,color="white"))
        ))
        fig.update_layout(height=300,margin=dict(l=0,r=0,t=8,b=0),
                          paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                          xaxis=dict(gridcolor="#EFF3F7"),yaxis=dict(gridcolor="#EFF3F7"))
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        st.markdown('</div>',unsafe_allow_html=True)

    st.write("")
    st.dataframe(lp,use_container_width=True,hide_index=True)

# ============================================================
# DIAGNÓSTICO
# ============================================================
elif page=="Diagnóstico e Causas":
    page_header("Diagnóstico e Causas","Do desvio executivo à causa operacional.")
    causes=D["causes"].copy()
    if causes.empty:
        st.info("Não há dados de causas suficientes para este período.")
    else:
        c1,c2=st.columns(2,gap="small")
        with c1:
            st.markdown('<div class="panel">',unsafe_allow_html=True)
            panel_title("Pareto de Horas Perdidas","Principais causas de parada")
            df=causes.sort_values("Horas")
            fig=go.Figure(go.Bar(x=df["Horas"],y=df["Causa"],orientation="h",marker_color=BLUE,
                                 text=[f"{x:.0f} h" for x in df["Horas"]],textposition="outside"))
            fig.update_layout(height=300,margin=dict(l=0,r=55,t=8,b=0),
                              paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                              xaxis=dict(showgrid=False,showticklabels=False),yaxis=dict(showgrid=False))
            st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
            st.markdown('</div>',unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="panel">',unsafe_allow_html=True)
            panel_title("Impacto Financeiro por Causa","Estimativa gerencial")
            df=causes.sort_values("Impacto R$ mil")
            fig=go.Figure(go.Bar(x=df["Impacto R$ mil"],y=df["Causa"],orientation="h",marker_color="#E85B55",
                                 text=[f"R$ {x:.0f} mil" for x in df["Impacto R$ mil"]],textposition="outside"))
            fig.update_layout(height=300,margin=dict(l=0,r=75,t=8,b=0),
                              paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                              xaxis=dict(showgrid=False,showticklabels=False),yaxis=dict(showgrid=False))
            st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
            st.markdown('</div>',unsafe_allow_html=True)

    st.write("")
    st.markdown("""
    <div class="panel">
      <div class="panel-title">Árvore de Diagnóstico</div>
      <div class="panel-sub">Encadeamento causal da performance</div>
      <div style="font-size:.72rem;line-height:1.85;color:#34465C">
        <b>Produção abaixo da meta</b>
        &nbsp;→&nbsp; linha com maior gap
        &nbsp;→&nbsp; componente OEE mais fraco
        &nbsp;→&nbsp; equipamento / turno
        &nbsp;→&nbsp; causa dominante
        &nbsp;→&nbsp; <b>impacto financeiro</b>
      </div>
    </div>
    """,unsafe_allow_html=True)
    st.write("")
    if st.button("Criar plano de ação",type="primary"):
        nav("Plano de Ação")

# ============================================================
# FINANÇAS / DRE
# ============================================================
elif page=="Finanças / DRE":
    page_header("Finanças / DRE","A operação traduzida em margem, custo fixo, variável e EBITDA.")

    c1,c2,c3,c4=st.columns(4,gap="small")
    c1.metric("Receita Líquida",fmt_money(D["revenue"]))
    c2.metric("Margem Contrib.",fmt_pct(D["margin"]))
    c3.metric("EBITDA Industrial",fmt_money(D["ebitda"]))
    c4.metric("Custo Fixo",fmt_money(D["cost_structure"]["Fixo"]))

    st.write("")
    c1,c2=st.columns([1.15,.85],gap="small")
    with c1:
        st.markdown('<div class="panel">',unsafe_allow_html=True)
        panel_title("DRE Gerencial","Visão resumida do resultado")
        view=D["dre"].copy()
        view["Realizado"]=view["Realizado"].map(lambda x:fmt_money(x))
        st.dataframe(view,use_container_width=True,hide_index=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="panel">',unsafe_allow_html=True)
        panel_title("Custo Fixo x Variável","Estrutura econômica da operação")
        vals=D["cost_structure"]
        fig=go.Figure(go.Pie(labels=list(vals.keys()),values=list(vals.values()),hole=.72,
                             marker=dict(colors=[BLUE,"#BBD8EC"]),textinfo="percent",
                             textfont=dict(size=11)))
        fig.update_layout(height=260,margin=dict(l=0,r=0,t=0,b=0),
                          legend=dict(orientation="h",y=-.05),
                          paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        st.markdown('</div>',unsafe_allow_html=True)

# ============================================================
# ALAVANCAS / SIMULADOR 2.0
# ============================================================
elif page=="Alavancas de Valor":
    page_header("Alavancas de Valor","Simule cenários multi-alavancas e veja o impacto no resultado.")

    base_revenue=D["revenue"]
    base_margin=D["margin"]
    base_ebitda=D["ebitda"]
    base_fixed=D["cost_structure"]["Fixo"]
    base_var=D["cost_structure"]["Variável"]

    left,right=st.columns([1.45,.75],gap="small")

    with left:
        tabs=st.tabs(["Operação","Qualidade","Pessoas","Custos","Comercial","Capital"])

        with tabs[0]:
            a,b=st.columns(2)
            oee=a.slider("OEE alvo (%)",60.0,95.0,max(78.0,D["oee"]*100),.5)
            availability=b.slider("Disponibilidade alvo (%)",60.0,95.0,max(80.0,D["availability"]*100),.5)
            c,d=st.columns(2)
            performance=c.slider("Performance alvo (%)",70.0,105.0,max(97.0,D["performance"]*100),.5)
            setup_reduction=d.slider("Redução de setup (%)",0,50,15)
            e,f=st.columns(2)
            downtime_reduction=e.slider("Redução de paradas não planejadas (%)",0,50,20)
            capacity_util=f.slider("Utilização de capacidade (%)",50.0,95.0,80.0,.5)

        with tabs[1]:
            a,b=st.columns(2)
            scrap=a.slider("Refugo alvo (%)",0.5,8.0,min(2.5,D["scrap"]*100),.1)
            rework=b.slider("Redução de retrabalho (%)",0,50,20)
            c,d=st.columns(2)
            material_loss=c.slider("Redução de perda de material (%)",0,40,15)
            ppm=d.slider("Redução de PPM / defeitos (%)",0,50,20)

        with tabs[2]:
            a,b=st.columns(2)
            overtime=a.slider("Redução de horas extras (%)",0,60,20)
            productivity=b.slider("Ganho de produtividade (%)",0,30,8)
            c,d=st.columns(2)
            headcount=c.slider("Variação de headcount (%)",-20,20,0)
            absenteeism=d.slider("Redução de absenteísmo (%)",0,30,5)

        with tabs[3]:
            a,b=st.columns(2)
            mp_cost=a.slider("Redução no custo de MP (%)",0,15,3)
            mp_consumption=b.slider("Redução no consumo específico de MP (%)",0,15,3)
            c,d=st.columns(2)
            energy=c.slider("Redução de energia / un. (%)",0,20,5)
            fixed_cost=d.slider("Redução de custo fixo (%)",0,15,2)
            e,f=st.columns(2)
            freight=e.slider("Redução de frete / un. (%)",0,15,3)
            contracts=f.slider("Redução em contratos / serviços (%)",0,20,5)

        with tabs[4]:
            a,b=st.columns(2)
            volume=a.slider("Variação de volume vendido (%)",-10,30,5)
            price=b.slider("Variação de preço médio (%)",-5,10,2)
            c,d=st.columns(2)
            mix=c.slider("Ganho de margem por mix (pp)",-3.0,5.0,1.0,.1)
            otif=d.slider("OTIF alvo (%)",70.0,100.0,95.0,.5)

        with tabs[5]:
            a,b=st.columns(2)
            inventory=a.slider("Redução de estoque (%)",0,30,10)
            wip=b.slider("Redução de WIP (%)",0,30,10)
            c,d=st.columns(2)
            dso=c.slider("Redução de prazo cliente (dias)",0,15,5)
            dpo=d.slider("Aumento prazo fornecedor (dias)",0,15,5)

    # Simple driver-based simulation
    # Operations / productivity effect on available output
    oee_gain=max(0,oee-D["oee"]*100)/100
    availability_gain=max(0,availability-D["availability"]*100)/100
    performance_gain=max(0,performance-D["performance"]*100)/100

    op_revenue = base_revenue * (
        oee_gain*0.55 +
        availability_gain*0.30 +
        performance_gain*0.20 +
        setup_reduction/100*0.05 +
        downtime_reduction/100*0.08 +
        max(0,capacity_util-72)/100*0.08
    )

    quality_saving = (
        max(0,D["scrap"]*100-scrap)/100 * base_var * 0.55 +
        rework/100 * base_var * 0.025 +
        material_loss/100 * base_var * 0.035 +
        ppm/100 * base_var * 0.015
    )

    people_saving = (
        overtime/100 * max(1,D["overtime"]*30) +
        productivity/100 * base_var * 0.06 -
        headcount/100 * base_fixed * 0.35 +
        absenteeism/100 * base_var * 0.015
    )

    cost_saving = (
        mp_cost/100 * base_var * 0.58 +
        mp_consumption/100 * base_var * 0.58 +
        energy/100 * base_var * 0.10 +
        fixed_cost/100 * base_fixed +
        freight/100 * base_var * 0.07 +
        contracts/100 * base_fixed * 0.22
    )

    commercial_revenue = base_revenue * (volume/100 + price/100)
    mix_gain = base_revenue * (mix/100)
    otif_gain = base_revenue * max(0,otif-89)/100 * 0.08

    working_capital = (
        inventory/100 * base_var * 0.35 +
        wip/100 * base_var * 0.10 +
        dso/365 * base_revenue +
        dpo/365 * base_var
    )

    simulated_revenue = base_revenue + op_revenue + commercial_revenue + otif_gain
    ebitda_gain = quality_saving + people_saving + cost_saving + mix_gain + op_revenue*base_margin + commercial_revenue*base_margin + otif_gain*base_margin
    simulated_ebitda = base_ebitda + ebitda_gain
    simulated_margin = safe_div(simulated_ebitda, simulated_revenue) if simulated_revenue else 0

    with right:
        st.markdown('<div class="panel">',unsafe_allow_html=True)
        panel_title("Impacto do Cenário","Base x simulado")

        st.markdown(f"""
        <div class="scenario-card">
          <div class="scenario-label">Receita</div>
          <div class="scenario-value">{fmt_money(simulated_revenue)}</div>
          <div class="scenario-delta">Δ {fmt_money(simulated_revenue-base_revenue)}</div>
        </div>
        <div style="height:8px"></div>
        <div class="scenario-card">
          <div class="scenario-label">Margem estimada</div>
          <div class="scenario-value">{fmt_pct(simulated_margin)}</div>
          <div class="scenario-delta">base {fmt_pct(base_margin)}</div>
        </div>
        <div style="height:8px"></div>
        <div class="scenario-card">
          <div class="scenario-label">EBITDA</div>
          <div class="scenario-value">{fmt_money(simulated_ebitda)}</div>
          <div class="scenario-delta">Δ {fmt_money(ebitda_gain)}</div>
        </div>
        <div style="height:8px"></div>
        <div class="scenario-card">
          <div class="scenario-label">Capital de giro liberado</div>
          <div class="scenario-value">{fmt_money(working_capital)}</div>
          <div class="scenario-delta">efeito caixa, não EBITDA</div>
        </div>
        """,unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

    st.write("")
    # Waterfall
    st.markdown('<div class="panel">',unsafe_allow_html=True)
    panel_title("Bridge do Cenário","Contribuição estimada das principais alavancas")
    components = {
        "Operação": op_revenue*base_margin,
        "Qualidade": quality_saving,
        "Pessoas": people_saving,
        "Custos": cost_saving,
        "Comercial": commercial_revenue*base_margin + mix_gain + otif_gain*base_margin,
    }
    x=["EBITDA Atual"]+list(components.keys())+["EBITDA Simulado"]
    measures=["absolute"]+["relative"]*len(components)+["total"]
    y=[base_ebitda]+list(components.values())+[0]
    fig=go.Figure(go.Waterfall(
        x=x,measure=measures,y=y,
        increasing={"marker":{"color":GREEN}},
        decreasing={"marker":{"color":RED}},
        totals={"marker":{"color":BLUE}},
        connector={"line":{"color":"#B8C4CE","width":1}}
    ))
    fig.update_layout(
        height=310,margin=dict(l=0,r=0,t=10,b=5),
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor="#EFF3F7",tickfont=dict(size=9)),
        xaxis=dict(tickfont=dict(size=9)),
        showlegend=False
    )
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    st.markdown('</div>',unsafe_allow_html=True)

    st.write("")
    c1,c2=st.columns([1,.45])
    with c1:
        st.caption("Simulação gerencial. Os coeficientes serão calibrados por cliente/planta quando houver histórico real.")
    with c2:
        if st.button("Transformar cenário em Plano de Captura",type="primary",use_container_width=True):
            new_actions = pd.DataFrame([
                ["Alta","Cenário: Operação","Executar plano de recuperação de OEE/disponibilidade","Ger. Industrial","30 dias",fmt_money(max(0,components["Operação"])),"Planejado"],
                ["Alta","Cenário: Qualidade","Executar plano de redução de perdas e refugo","Ger. Qualidade","45 dias",fmt_money(max(0,components["Qualidade"])),"Planejado"],
                ["Média","Cenário: Custos","Executar plano de eficiência de custos","Controller / Operações","60 dias",fmt_money(max(0,components["Custos"])),"Planejado"],
            ],columns=st.session_state.actions.columns)
            st.session_state.actions=pd.concat([st.session_state.actions,new_actions],ignore_index=True)
            nav("Plano de Ação")

# ============================================================
# PLANO DE AÇÃO
# ============================================================
elif page=="Plano de Ação":
    page_header("Plano de Ação","Responsabilidade, prazo e captura de valor.")

    st.dataframe(st.session_state.actions,use_container_width=True,hide_index=True)

    st.write("")
    with st.form("action_form",clear_on_submit=True):
        a,b=st.columns(2)
        problema=a.text_input("Problema / oportunidade")
        responsavel=b.text_input("Responsável")
        acao=st.text_area("Ação recomendada")
        c,d,e=st.columns(3)
        prazo=c.text_input("Prazo",placeholder="dd/mm/aaaa")
        prioridade=d.selectbox("Prioridade",["Alta","Média","Baixa"])
        impacto=e.text_input("Impacto esperado",placeholder="R$ 100 mil")
        ok=st.form_submit_button("Adicionar ação",type="primary")
        if ok and problema and acao:
            new=pd.DataFrame([[prioridade,problema,acao,responsavel,prazo,impacto,"Planejado"]],
                             columns=st.session_state.actions.columns)
            st.session_state.actions=pd.concat([st.session_state.actions,new],ignore_index=True)
            st.success("Ação adicionada ao plano.")
            st.rerun()

# ============================================================
# AGENTE
# ============================================================
elif page=="Agente de Performance":
    page_header("Agente de Performance","Pergunte aos dados e transforme análise em decisão.")
    if "chat" not in st.session_state:
        st.session_state.chat=[]

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
    """,unsafe_allow_html=True)

    st.write("")
    for role,msg in st.session_state.chat:
        st.chat_message(role).write(msg)

    q=st.chat_input("Ex.: Qual o impacto de elevar o OEE para 80%?")
    if q:
        st.session_state.chat.append(("user",q))
        ql=q.lower()
        if "oee" in ql:
            ans=f"O OEE atual é {fmt_pct(D['oee'])}. O maior potencial está na recuperação de disponibilidade. Use o Simulador de Alavancas para testar metas de OEE, disponibilidade e performance."
        elif "linha" in ql:
            worst=D["line_perf"].sort_values("OEE").iloc[0]
            ans=f"A prioridade é {worst['Linha']}, com OEE de {fmt_pct(worst['OEE'])} e {worst['Paradas h']:.0f} horas de parada no período."
        elif "margem" in ql or "ebitda" in ql:
            top=D["impacts"].sort_values("R$",ascending=False).iloc[0]
            ans=f"A maior pressão estimada sobre o resultado vem de {top['Impacto']}, com impacto indicativo de {fmt_money(top['R$'])}."
        else:
            ans="As prioridades são disponibilidade, refugo e horas extras. Use Diagnóstico e Alavancas para abrir as causas e simular o efeito financeiro."
        st.session_state.chat.append(("assistant",ans))
        st.rerun()

# ============================================================
# RELATÓRIOS
# ============================================================
elif page=="Relatórios":
    page_header("Relatórios","Resumo executivo e materiais para rotina de gestão.")
    summary=f"""INDUSTRIAL PERFORMANCE — RESUMO EXECUTIVO
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
    st.markdown('<div class="panel"><div class="panel-title">Resumo Executivo</div><div class="panel-sub">Versão simples para validação do fluxo</div></div>',unsafe_allow_html=True)
    st.write("")
    st.download_button("Baixar resumo executivo",summary,file_name="industrial_performance_resumo.txt",type="primary")

# ============================================================
# CONFIGURAÇÕES / UPLOAD
# ============================================================
elif page=="Configurações":
    page_header("Configurações","Importe dados, valide o modelo e atualize o cockpit.")

    tabs=st.tabs(["Importação de Dados","Metas","Estrutura de Custos","Integrações"])

    with tabs[0]:
        st.markdown("#### Importar Excel")
        st.caption("Fluxo: carregar → validar → revisar → aplicar ao cockpit.")
        uploaded=st.file_uploader("Arquivo Excel",type=["xlsx","xls"],accept_multiple_files=False)

        if uploaded is not None:
            data,issues=parse_excel(uploaded.getvalue())
            if issues:
                st.error("O arquivo foi carregado, mas ainda não está compatível com o modelo.")
                for issue in issues:
                    st.write("•",issue)
            else:
                st.success("Estrutura validada com sucesso.")
                st.write("Abas reconhecidas:")
                st.write(", ".join([k.title() for k in data.keys()]))

                preview_sheet=st.selectbox("Prévia da aba",list(data.keys()))
                st.dataframe(data[preview_sheet].head(20),use_container_width=True,hide_index=True)

                if st.button("Aplicar dados ao cockpit",type="primary"):
                    st.session_state.real_data=data
                    st.session_state.page="Cockpit Executivo"
                    st.rerun()

        if st.session_state.real_data is not None:
            st.write("")
            if st.button("Voltar para dados demo"):
                st.session_state.real_data=None
                st.rerun()

    with tabs[1]:
        st.info("Próxima evolução: metas persistentes por indicador, linha e período.")
    with tabs[2]:
        st.info("Próxima evolução: plano de contas gerencial + classificação fixo/variável + DE/PARA.")
    with tabs[3]:
        st.info("Roadmap: ERP, MES, WMS, CMMS, SQL e APIs.")
