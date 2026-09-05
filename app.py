
import streamlit as st
import pandas as pd
import numpy as np
import unicodedata
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Industrial Performance Agent",
    page_icon="🏭",
    layout="wide"
)

# ---------- Visual ----------
st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 3rem;}
.big-title {font-size: 2.15rem; font-weight: 800; margin-bottom: .1rem;}
.subtle {color:#6b7280; font-size:.95rem;}
.kpi-card {
    border:1px solid #E5E7EB; border-radius:14px; padding:16px 18px;
    background:white; min-height:132px; box-shadow:0 1px 2px rgba(0,0,0,.03);
}
.kpi-label {font-size:.82rem; color:#6B7280; text-transform:uppercase; letter-spacing:.04em;}
.kpi-value {font-size:1.75rem; font-weight:800; margin:.15rem 0;}
.kpi-meta {font-size:.9rem; color:#4B5563;}
.insight {
    border-left:4px solid #F59E0B; background:#FFF7ED; padding:14px 16px;
    border-radius:8px; margin:.4rem 0;
}
.agent-answer {
    border:1px solid #D1D5DB; background:#F9FAFB; border-radius:12px;
    padding:16px 18px; margin-top:.5rem;
}
</style>
""", unsafe_allow_html=True)

# ---------- Helpers ----------
def norm_txt(x):
    x = str(x).strip().lower()
    x = ''.join(c for c in unicodedata.normalize('NFKD', x) if not unicodedata.combining(c))
    return ''.join(ch if ch.isalnum() else '_' for ch in x).strip('_')

SHEET_ALIASES = {
    "producao": ["producao","produção","production"],
    "qualidade": ["qualidade","quality"],
    "manutencao": ["manutencao","manutenção","maintenance"],
    "pessoas": ["pessoas","people","mao_de_obra","mão de obra","rh"],
    "custos": ["custos","costs","financeiro"],
    "metas": ["metas","targets","goals"]
}

COL_ALIASES = {
    "producao": {
        "data":["data","date"],
        "fabrica":["fabrica","planta","site","factory"],
        "linha":["linha","line"],
        "produto":["produto","sku","product"],
        "planejado":["planejado","plano","meta_producao","planned"],
        "realizado":["realizado","producao_real","qtd_produzida","volume","actual"],
        "horas_disponiveis":["horas_disponiveis","horas_planejadas","available_hours"],
        "horas_paradas":["horas_paradas","paradas_horas","downtime_hours"],
        "velocidade_real":["velocidade_real","performance_real","actual_speed"],
        "velocidade_nominal":["velocidade_nominal","velocidade_padrao","nominal_speed"]
    },
    "qualidade": {
        "data":["data","date"],
        "linha":["linha","line"],
        "produto":["produto","sku","product"],
        "produzido":["produzido","producao","produced"],
        "aprovado":["aprovado","bons","good_units"],
        "refugo":["refugo","scrap"],
        "retrabalho":["retrabalho","rework"]
    },
    "manutencao": {
        "data":["data","date"],
        "linha":["linha","line"],
        "maquina":["maquina","equipamento","machine"],
        "tipo_parada":["tipo_parada","tipo","downtime_type"],
        "duracao_horas":["duracao_horas","horas","duracao","duration_hours"],
        "causa":["causa","motivo","cause"]
    },
    "pessoas": {
        "data":["data","date"],
        "linha":["linha","line"],
        "turno":["turno","shift"],
        "operadores":["operadores","headcount","pessoas"],
        "horas_normais":["horas_normais","regular_hours"],
        "horas_extras":["horas_extras","overtime","overtime_hours"]
    },
    "custos": {
        "data":["data","date"],
        "linha":["linha","line"],
        "produto":["produto","sku","product"],
        "custo_mp":["custo_mp","materia_prima","raw_material_cost"],
        "custo_mod":["custo_mod","mao_de_obra_direta","direct_labor_cost"],
        "custo_energia":["custo_energia","energia","energy_cost"],
        "custo_manutencao":["custo_manutencao","manutencao","maintenance_cost"],
        "receita":["receita","faturamento","revenue"]
    },
    "metas": {
        "indicador":["indicador","kpi","metric"],
        "meta":["meta","target","goal"]
    }
}

REQUIRED = {
    "producao":["data","linha","planejado","realizado","horas_disponiveis","horas_paradas","velocidade_real","velocidade_nominal"],
    "qualidade":["data","linha","produzido","aprovado","refugo"],
    "manutencao":["data","linha","maquina","duracao_horas","causa"],
    "pessoas":["data","linha","horas_normais","horas_extras"],
    "custos":["data","linha","custo_mp","custo_mod","custo_energia","custo_manutencao","receita"],
    "metas":["indicador","meta"]
}

def canonical_sheet(name):
    n = norm_txt(name)
    for canon, aliases in SHEET_ALIASES.items():
        if n in [norm_txt(a) for a in aliases]:
            return canon
    return None

def rename_columns(df, sheet):
    alias_map = {}
    for canon, aliases in COL_ALIASES[sheet].items():
        for a in aliases + [canon]:
            alias_map[norm_txt(a)] = canon
    new_cols = {}
    for c in df.columns:
        nc = norm_txt(c)
        if nc in alias_map:
            new_cols[c] = alias_map[nc]
    return df.rename(columns=new_cols)

@st.cache_data(show_spinner=False)
def read_workbooks(file_bytes_list):
    bag = {k: [] for k in SHEET_ALIASES}
    warnings = []
    for name, raw in file_bytes_list:
        try:
            xls = pd.ExcelFile(BytesIO(raw))
            for sh in xls.sheet_names:
                canon = canonical_sheet(sh)
                if canon:
                    df = pd.read_excel(BytesIO(raw), sheet_name=sh)
                    df = rename_columns(df, canon)
                    df["_arquivo_origem"] = name
                    bag[canon].append(df)
        except Exception as e:
            warnings.append(f"{name}: {e}")
    result = {}
    for k, dfs in bag.items():
        if dfs:
            result[k] = pd.concat(dfs, ignore_index=True)
    return result, warnings

def validate_data(data):
    issues = []
    for sheet, reqs in REQUIRED.items():
        if sheet not in data:
            issues.append(f"Aba ausente: {sheet.title()}")
            continue
        miss = [c for c in reqs if c not in data[sheet].columns]
        if miss:
            issues.append(f"{sheet.title()}: faltam colunas {', '.join(miss)}")
    return issues

def prep_dates(data):
    for k, df in data.items():
        if "data" in df.columns:
            data[k] = df.copy()
            data[k]["data"] = pd.to_datetime(data[k]["data"], errors="coerce")
    return data

def apply_filters(data, start, end, factories, lines):
    out = {}
    for k, df in data.items():
        d = df.copy()
        if "data" in d.columns:
            d = d[(d["data"].dt.date >= start) & (d["data"].dt.date <= end)]
        if "fabrica" in d.columns and factories:
            d = d[d["fabrica"].astype(str).isin(factories)]
        if "linha" in d.columns and lines:
            d = d[d["linha"].astype(str).isin(lines)]
        out[k] = d
    return out

def num(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)

def safe_div(a,b):
    return float(a/b) if b not in [0,0.0] and pd.notna(b) else 0.0

def get_target(metas, names, default):
    if metas is None or metas.empty:
        return default
    m = metas.copy()
    m["_ind"] = m["indicador"].map(norm_txt)
    candidates = [norm_txt(x) for x in names]
    hit = m[m["_ind"].isin(candidates)]
    if hit.empty:
        return default
    return float(pd.to_numeric(hit.iloc[0]["meta"], errors="coerce"))

def compute_kpis(data):
    p = data["producao"].copy()
    q = data["qualidade"].copy()
    c = data["custos"].copy()
    pe = data["pessoas"].copy()

    for col in ["planejado","realizado","horas_disponiveis","horas_paradas","velocidade_real","velocidade_nominal"]:
        p[col] = num(p[col])
    for col in ["produzido","aprovado","refugo","retrabalho"]:
        if col in q: q[col] = num(q[col])
    for col in ["custo_mp","custo_mod","custo_energia","custo_manutencao","receita"]:
        c[col] = num(c[col])
    for col in ["horas_normais","horas_extras","operadores"]:
        if col in pe: pe[col] = num(pe[col])

    planned = p["planejado"].sum()
    actual = p["realizado"].sum()
    gap = actual - planned
    attainment = safe_div(actual, planned)

    avail_hours = p["horas_disponiveis"].sum()
    downtime = p["horas_paradas"].sum()
    availability = max(0, min(1, 1 - safe_div(downtime, avail_hours)))

    weights = p["realizado"].replace(0, np.nan)
    perf_ratio = (p["velocidade_real"] / p["velocidade_nominal"].replace(0,np.nan)).clip(lower=0, upper=1.5)
    performance = np.average(perf_ratio.fillna(0), weights=weights.fillna(1)) if len(p) else 0
    performance = max(0, min(1.2, float(performance)))

    produced_q = q["produzido"].sum()
    approved_q = q["aprovado"].sum()
    quality = max(0, min(1, safe_div(approved_q, produced_q)))
    scrap_rate = safe_div(q["refugo"].sum(), produced_q)

    oee = availability * min(performance,1) * quality

    total_cost = c[["custo_mp","custo_mod","custo_energia","custo_manutencao"]].sum().sum()
    revenue = c["receita"].sum()
    cost_unit = safe_div(total_cost, actual)
    margin = safe_div(revenue-total_cost, revenue)
    margin_unit = safe_div(revenue-total_cost, actual)

    overtime = pe["horas_extras"].sum()
    regular = pe["horas_normais"].sum()
    productivity = safe_div(actual, regular + overtime)

    targets = data.get("metas", pd.DataFrame())
    target_oee = get_target(targets, ["OEE"], .80)
    target_scrap = get_target(targets, ["Refugo","Taxa Refugo"], .025)
    target_attainment = get_target(targets, ["Atingimento Produção","Produção"], 1.0)
    target_margin = get_target(targets, ["Margem","Margem Contribuição"], .30)

    return {
        "planned":planned,"actual":actual,"gap":gap,"attainment":attainment,
        "availability":availability,"performance":performance,"quality":quality,"oee":oee,
        "scrap_rate":scrap_rate,"total_cost":total_cost,"revenue":revenue,
        "cost_unit":cost_unit,"margin":margin,"margin_unit":margin_unit,
        "overtime":overtime,"regular_hours":regular,"productivity":productivity,
        "target_oee":target_oee,"target_scrap":target_scrap,
        "target_attainment":target_attainment,"target_margin":target_margin
    }

def line_table(data):
    p = data["producao"].copy()
    q = data["qualidade"].copy()
    c = data["custos"].copy()
    m = data["manutencao"].copy()

    for col in ["planejado","realizado","horas_disponiveis","horas_paradas","velocidade_real","velocidade_nominal"]:
        p[col]=num(p[col])
    for col in ["produzido","aprovado","refugo"]:
        q[col]=num(q[col])
    for col in ["custo_mp","custo_mod","custo_energia","custo_manutencao","receita"]:
        c[col]=num(c[col])
    m["duracao_horas"]=num(m["duracao_horas"])

    rows=[]
    for line in sorted(set(p["linha"].astype(str))):
        pp=p[p["linha"].astype(str)==line]
        qq=q[q["linha"].astype(str)==line]
        cc=c[c["linha"].astype(str)==line]
        mm=m[m["linha"].astype(str)==line]
        planned=pp["planejado"].sum()
        actual=pp["realizado"].sum()
        avail=max(0,min(1,1-safe_div(pp["horas_paradas"].sum(),pp["horas_disponiveis"].sum())))
        pr=(pp["velocidade_real"]/pp["velocidade_nominal"].replace(0,np.nan)).clip(0,1.5)
        perf=float(pr.mean()) if len(pr) else 0
        qual=safe_div(qq["aprovado"].sum(),qq["produzido"].sum())
        oee=avail*min(perf,1)*qual
        cost=cc[["custo_mp","custo_mod","custo_energia","custo_manutencao"]].sum().sum()
        rev=cc["receita"].sum()
        rows.append({
            "Linha":line,"Planejado":planned,"Realizado":actual,"Gap":actual-planned,
            "Atingimento":safe_div(actual,planned),"OEE":oee,
            "Refugo":safe_div(qq["refugo"].sum(),qq["produzido"].sum()),
            "Paradas_h":mm["duracao_horas"].sum(),
            "Margem":safe_div(rev-cost,rev)
        })
    return pd.DataFrame(rows)

def generate_insights(data, kpis, lt):
    insights=[]
    if kpis["attainment"] < 1:
        deficit = kpis["planned"]-kpis["actual"]
        worst = lt.sort_values("Gap").iloc[0] if not lt.empty else None
        if worst is not None:
            contrib = safe_div(abs(min(worst["Gap"],0)), deficit)
            insights.append(
                f"A produção está {abs(1-kpis['attainment']):.1%} abaixo do plano. "
                f"A {worst['Linha']} concentra aproximadamente {contrib:.0%} do déficit de volume."
            )
    if kpis["oee"] < kpis["target_oee"]:
        comp = {"Disponibilidade":kpis["availability"],"Performance":kpis["performance"],"Qualidade":kpis["quality"]}
        bottleneck=min(comp,key=comp.get)
        insights.append(
            f"O OEE está em {kpis['oee']:.1%}, abaixo da meta de {kpis['target_oee']:.1%}. "
            f"O componente mais fraco é {bottleneck.lower()} ({comp[bottleneck]:.1%})."
        )
    if kpis["scrap_rate"] > kpis["target_scrap"]:
        q=data["qualidade"].copy()
        q["refugo"]=num(q["refugo"]); q["produzido"]=num(q["produzido"])
        prod=q.groupby("produto",dropna=False).agg(refugo=("refugo","sum"),produzido=("produzido","sum")).reset_index() if "produto" in q else pd.DataFrame()
        if not prod.empty:
            prod["taxa"]=prod["refugo"]/prod["produzido"].replace(0,np.nan)
            wp=prod.sort_values("taxa",ascending=False).iloc[0]
            insights.append(
                f"O refugo está em {kpis['scrap_rate']:.1%}, acima da meta de {kpis['target_scrap']:.1%}. "
                f"O produto com maior taxa de refugo é {wp['produto']} ({wp['taxa']:.1%})."
            )
    m=data["manutencao"].copy()
    m["duracao_horas"]=num(m["duracao_horas"])
    if not m.empty:
        causes=m.groupby("causa")["duracao_horas"].sum().sort_values(ascending=False)
        if len(causes):
            insights.append(
                f"A principal causa registrada de parada é '{causes.index[0]}', com {causes.iloc[0]:.1f} h no período."
            )
    if kpis["margin"] < kpis["target_margin"]:
        insights.append(
            f"A margem está em {kpis['margin']:.1%}, abaixo da referência de {kpis['target_margin']:.1%}. "
            f"O custo industrial médio calculado é R$ {kpis['cost_unit']:,.2f} por unidade."
        )
    return insights[:5]

def loss_table(data,kpis,lt):
    items=[]
    vol_gap=max(0,kpis["planned"]-kpis["actual"])
    items.append(("Gap de produção", vol_gap*kpis["margin_unit"], "Margem potencial associada ao volume não produzido"))
    scrap_units=data["qualidade"]["refugo"].pipe(num).sum()
    items.append(("Refugo", scrap_units*kpis["cost_unit"], "Custo industrial aproximado das unidades refugadas"))
    # downtime opportunity
    runtime=max(1,kpis["regular_hours"]+kpis["overtime"])
    units_per_h=safe_div(kpis["actual"],runtime)
    downtime=data["manutencao"]["duracao_horas"].pipe(num).sum()
    items.append(("Paradas", downtime*units_per_h*kpis["margin_unit"], "Oportunidade indicativa de margem associada às horas paradas"))
    return pd.DataFrame(items,columns=["Perda/Alavanca","Impacto_R$","Critério"]).sort_values("Impacto_R$",ascending=False)

def answer_agent(question,data,kpis,lt):
    q=norm_txt(question)
    if not q:
        return "Digite uma pergunta sobre a performance da operação."
    if "meta" in q or "planej" in q or "produc" in q:
        worst=lt.sort_values("Gap").iloc[0]
        return (
            f"O realizado é {kpis['actual']:,.0f} unidades contra {kpis['planned']:,.0f} planejadas "
            f"({kpis['attainment']:.1%} de atingimento). A maior contribuição negativa está na "
            f"{worst['Linha']}, com gap de {worst['Gap']:,.0f} unidades. "
            f"O OEE geral está em {kpis['oee']:.1%}, e o principal componente limitante é "
            f"{min({'disponibilidade':kpis['availability'],'performance':kpis['performance'],'qualidade':kpis['quality']}, key=lambda x: {'disponibilidade':kpis['availability'],'performance':kpis['performance'],'qualidade':kpis['quality']}[x])}."
        )
    if "perda" in q or "impact" in q or "financeir" in q:
        losses=loss_table(data,kpis,lt)
        parts=[f"{r['Perda/Alavanca']}: R$ {r['Impacto_R$']:,.0f}" for _,r in losses.head(3).iterrows()]
        return "As maiores perdas/alavancas estimadas são: " + "; ".join(parts) + ". Os valores são indicativos e não devem ser somados sem ajuste para evitar dupla contagem."
    if "oee" in q:
        import re
        nums=re.findall(r"\d+(?:[.,]\d+)?", question)
        target=(float(nums[0].replace(",","."))/100) if nums else kpis["target_oee"]
        if kpis["oee"]<=0:
            return "Não há dados suficientes para projetar o impacto de OEE."
        add_units=max(0,kpis["actual"]*(target/kpis["oee"]-1))
        impact=add_units*kpis["margin_unit"]
        return (
            f"Se o OEE subir de {kpis['oee']:.1%} para {target:.1%}, mantendo as demais relações atuais, "
            f"o potencial indicativo é de aproximadamente {add_units:,.0f} unidades adicionais e "
            f"R$ {impact:,.0f} de margem de contribuição. É uma simulação de capacidade, não uma garantia de resultado."
        )
    if "linha" in q or "pior" in q or "gargalo" in q:
        worst=lt.sort_values(["Atingimento","OEE"]).iloc[0]
        return (
            f"A linha que mais exige atenção é {worst['Linha']}: atingimento de {worst['Atingimento']:.1%}, "
            f"OEE de {worst['OEE']:.1%}, refugo de {worst['Refugo']:.1%} e {worst['Paradas_h']:.1f} h de parada."
        )
    if "qualidade" in q or "refugo" in q:
        qd=data["qualidade"].copy()
        qd["refugo"]=num(qd["refugo"]); qd["produzido"]=num(qd["produzido"])
        gp=qd.groupby("produto").agg(refugo=("refugo","sum"),produzido=("produzido","sum")).reset_index()
        gp["taxa"]=gp["refugo"]/gp["produzido"].replace(0,np.nan)
        wp=gp.sort_values("taxa",ascending=False).iloc[0]
        return f"A taxa de refugo geral é {kpis['scrap_rate']:.1%}. O pior produto é {wp['produto']}, com {wp['taxa']:.1%}."
    if "hora_extra" in q or "hora extra" in question.lower():
        return (
            f"Foram registradas {kpis['overtime']:,.1f} horas extras no período. "
            f"A produtividade combinada foi de {kpis['productivity']:,.2f} unidades por hora trabalhada."
        )
    return (
        f"Resumo do período: produção em {kpis['attainment']:.1%} do plano, OEE {kpis['oee']:.1%}, "
        f"refugo {kpis['scrap_rate']:.1%}, margem {kpis['margin']:.1%} e custo unitário R$ {kpis['cost_unit']:,.2f}. "
        "Pergunte, por exemplo: 'Por que não bati a meta?', 'Quais são as maiores perdas?', "
        "'Qual a pior linha?', 'Como está a qualidade?' ou 'Qual o impacto de elevar o OEE para 80%?'."
    )

def fmt_int(x): return f"{x:,.0f}".replace(",","X").replace(".",",").replace("X",".")
def fmt_money(x): return "R$ " + f"{x:,.2f}".replace(",","X").replace(".",",").replace("X",".")
def fmt_pct(x): return f"{x:.1%}".replace(".",",")

def kpi_card(label,value,meta):
    st.markdown(f"""<div class="kpi-card">
    <div class="kpi-label">{label}</div>
    <div class="kpi-value">{value}</div>
    <div class="kpi-meta">{meta}</div>
    </div>""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown('<div class="big-title">Industrial Performance Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="subtle">MVP • Excel → KPIs → diagnóstico → impacto financeiro → decisão</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Dados")
    uploaded = st.file_uploader(
        "Carregue um ou mais arquivos Excel",
        type=["xlsx","xls"],
        accept_multiple_files=True
    )
    st.caption("Abas reconhecidas: Produção, Qualidade, Manutenção, Pessoas, Custos e Metas.")

if not uploaded:
    st.info("Carregue o arquivo **industrial_performance_exemplo.xlsx** para testar o MVP.")
    st.markdown("""
    ### O que este MVP já faz
    - Consolida múltiplos arquivos Excel.
    - Calcula produção, OEE, disponibilidade, performance, qualidade, refugo, produtividade, custo e margem.
    - Identifica linhas, produtos e causas de parada que mais pressionam o resultado.
    - Traduz perdas operacionais em impacto financeiro indicativo.
    - Responde perguntas executivas com base nos dados carregados.
    """)
    st.stop()

file_bytes_list=[(f.name,f.getvalue()) for f in uploaded]
data,warnings=read_workbooks(file_bytes_list)
if warnings:
    for w in warnings: st.warning(w)

issues=validate_data(data)
if issues:
    st.error("O arquivo ainda não está compatível com o modelo do MVP.")
    for i in issues: st.write("•",i)
    st.caption("Use o Excel de exemplo como referência. Na próxima versão podemos adicionar um mapeador DE/PARA visual.")
    st.stop()

data=prep_dates(data)
all_dates=pd.concat([df["data"] for df in data.values() if "data" in df.columns]).dropna()
min_d,max_d=all_dates.min().date(),all_dates.max().date()

prod=data["producao"]
factories=sorted(prod["fabrica"].dropna().astype(str).unique()) if "fabrica" in prod else []
lines=sorted(prod["linha"].dropna().astype(str).unique())

with st.sidebar:
    st.divider()
    st.header("Filtros")
    date_range=st.date_input("Período", value=(min_d,max_d), min_value=min_d, max_value=max_d)
    if isinstance(date_range,tuple) and len(date_range)==2:
        start,end=date_range
    else:
        start=end=date_range
    sel_factories=st.multiselect("Fábrica",factories,default=factories)
    sel_lines=st.multiselect("Linha",lines,default=lines)

fdata=apply_filters(data,start,end,sel_factories,sel_lines)
if fdata["producao"].empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
    st.stop()

kpis=compute_kpis(fdata)
lt=line_table(fdata)
insights=generate_insights(fdata,kpis,lt)

# ---------- KPIs ----------
st.subheader("Cockpit executivo")
cols=st.columns(4)
with cols[0]: kpi_card("Produção",fmt_int(kpis["actual"]),f"Plano {fmt_int(kpis['planned'])} • {fmt_pct(kpis['attainment'])}")
with cols[1]: kpi_card("OEE",fmt_pct(kpis["oee"]),f"Meta {fmt_pct(kpis['target_oee'])}")
with cols[2]: kpi_card("Refugo",fmt_pct(kpis["scrap_rate"]),f"Meta {fmt_pct(kpis['target_scrap'])}")
with cols[3]: kpi_card("Margem",fmt_pct(kpis["margin"]),f"Referência {fmt_pct(kpis['target_margin'])}")

cols=st.columns(4)
with cols[0]: kpi_card("Disponibilidade",fmt_pct(kpis["availability"]),"Componente do OEE")
with cols[1]: kpi_card("Performance",fmt_pct(kpis["performance"]),"Componente do OEE")
with cols[2]: kpi_card("Custo / unidade",fmt_money(kpis["cost_unit"]),"Custo industrial calculado")
with cols[3]: kpi_card("Horas extras",f"{kpis['overtime']:,.1f} h".replace(".",","),f"Produtividade {kpis['productivity']:.2f} un/h".replace(".",","))

# ---------- Charts ----------
st.subheader("Onde está o desvio")
c1,c2=st.columns(2)

with c1:
    chart=lt.sort_values("Gap")
    fig=px.bar(chart,x="Linha",y="Gap",title="Gap de produção por linha")
    fig.update_layout(margin=dict(l=10,r=10,t=50,b=10))
    st.plotly_chart(fig,use_container_width=True)

with c2:
    chart=lt.sort_values("OEE")
    fig=px.bar(chart,x="Linha",y="OEE",title="OEE por linha")
    fig.update_yaxes(tickformat=".0%")
    fig.update_layout(margin=dict(l=10,r=10,t=50,b=10))
    st.plotly_chart(fig,use_container_width=True)

# trend
p=fdata["producao"].copy()
p["planejado"]=num(p["planejado"]); p["realizado"]=num(p["realizado"])
trend=p.groupby("data")[["planejado","realizado"]].sum().reset_index()
fig=go.Figure()
fig.add_trace(go.Scatter(x=trend["data"],y=trend["planejado"],mode="lines",name="Planejado"))
fig.add_trace(go.Scatter(x=trend["data"],y=trend["realizado"],mode="lines",name="Realizado"))
fig.update_layout(title="Produção diária: planejado × realizado",margin=dict(l=10,r=10,t=50,b=10))
st.plotly_chart(fig,use_container_width=True)

# ---------- Insights ----------
st.subheader("Diagnóstico automático")
if insights:
    for x in insights:
        st.markdown(f'<div class="insight">{x}</div>',unsafe_allow_html=True)
else:
    st.success("Nenhum desvio relevante foi identificado pelas regras atuais.")

# ---------- Financial losses ----------
st.subheader("Impacto financeiro indicativo")
losses=loss_table(fdata,kpis,lt).copy()
losses["Impacto estimado"]=losses["Impacto_R$"].map(fmt_money)
st.dataframe(losses[["Perda/Alavanca","Impacto estimado","Critério"]],hide_index=True,use_container_width=True)
st.caption("Estimativas gerenciais. Algumas perdas podem se sobrepor e não devem ser somadas automaticamente.")

# ---------- Detail ----------
with st.expander("Detalhamento por linha"):
    show=lt.copy()
    show["Atingimento"]=show["Atingimento"].map(fmt_pct)
    show["OEE"]=show["OEE"].map(fmt_pct)
    show["Refugo"]=show["Refugo"].map(fmt_pct)
    show["Margem"]=show["Margem"].map(fmt_pct)
    st.dataframe(show,use_container_width=True,hide_index=True)

with st.expander("Principais causas de parada"):
    m=fdata["manutencao"].copy()
    m["duracao_horas"]=num(m["duracao_horas"])
    causes=m.groupby(["linha","causa"],as_index=False)["duracao_horas"].sum().sort_values("duracao_horas",ascending=False)
    st.dataframe(causes.rename(columns={"linha":"Linha","causa":"Causa","duracao_horas":"Horas"}),use_container_width=True,hide_index=True)

# ---------- Agent ----------
st.subheader("Agente de Performance")
st.caption("Faça perguntas executivas sobre os dados carregados.")
question=st.text_input("Pergunta",placeholder="Ex.: Qual o impacto de elevar o OEE para 80%?")
if question:
    ans=answer_agent(question,fdata,kpis,lt)
    st.markdown(f'<div class="agent-answer">{ans}</div>',unsafe_allow_html=True)

with st.expander("Perguntas sugeridas"):
    st.write("• Por que não estamos atingindo a meta?")
    st.write("• Quais são as maiores perdas financeiras?")
    st.write("• Qual é a pior linha?")
    st.write("• Como está a qualidade?")
    st.write("• Qual o impacto de elevar o OEE para 80%?")
