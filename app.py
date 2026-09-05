
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# -------------------------------------------------------
# CONFIG
# -------------------------------------------------------
st.set_page_config(
    page_title="Industrial Performance | H2M",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

NAVY = "#061D34"
NAVY2 = "#0A2C4C"
BLUE = "#0B5EA8"
CYAN = "#00B8F0"
TEXT = "#10233F"
MUTED = "#6D7B8F"
BG = "#F4F7FB"
BORDER = "#E2E8F0"
RED = "#E53935"
ORANGE = "#F47B20"
GREEN = "#13A86B"
INFO = "#3578C6"
WHITE = "#FFFFFF"

# -------------------------------------------------------
# CSS
# -------------------------------------------------------
st.markdown(f"""
<style>
#MainMenu {{visibility:hidden;}}
footer {{visibility:hidden;}}
header[data-testid="stHeader"] {{background:transparent;}}

.stApp {{
    background:{BG};
    color:{TEXT};
}}

.block-container {{
    max-width: 1720px;
    padding-top: 0.8rem;
    padding-bottom: 2rem;
}}

[data-testid="stSidebar"] {{
    background:linear-gradient(180deg,{NAVY} 0%,{NAVY2} 100%);
    border-right:1px solid rgba(255,255,255,.07);
}}

[data-testid="stSidebar"] .block-container {{
    padding-top:1rem;
}}

[data-testid="stSidebar"] .stButton button {{
    width:100%;
    justify-content:flex-start;
    min-height:42px;
    border:none;
    border-radius:9px;
    background:transparent;
    color:#DCE8F4;
    font-weight:650;
    box-shadow:none;
}}

[data-testid="stSidebar"] .stButton button:hover {{
    background:rgba(0,184,240,.10);
    color:white;
}}

[data-testid="stSidebar"] .stButton button[kind="primary"] {{
    background:linear-gradient(90deg,#0B5EA8,#078FC9);
    color:white;
    border-left:3px solid {CYAN};
}}

.brand-sub {{
    color:#ABC0D3;
    font-size:.72rem;
    margin-top:-6px;
    margin-bottom:16px;
}}

.sidebar-footer {{
    margin-top:22px;
    padding:14px 4px 0;
    color:#C4D3DF;
    font-size:.78rem;
    line-height:1.45;
}}

.sidebar-tag {{
    color:#7BE1FF;
    font-size:.61rem;
    letter-spacing:.08em;
    margin-top:10px;
}}

.eyebrow {{
    color:{BLUE};
    font-size:.66rem;
    font-weight:850;
    letter-spacing:.08em;
    text-transform:uppercase;
}}

.page-title {{
    font-size:2rem;
    font-weight:850;
    line-height:1.05;
    letter-spacing:-.03em;
    color:{TEXT};
    margin-top:.15rem;
}}

.page-subtitle {{
    color:{MUTED};
    font-size:.92rem;
    margin-top:.3rem;
    margin-bottom:.9rem;
}}

.top-quote {{
    text-align:right;
    color:{TEXT};
    font-weight:750;
    font-size:.88rem;
    line-height:1.25;
    padding-top:.4rem;
}}

.kpi-card {{
    background:{WHITE};
    border:1px solid {BORDER};
    border-radius:14px;
    padding:14px 14px 13px;
    box-shadow:0 4px 14px rgba(10,35,60,.035);
    min-height:112px;
}}

.kpi-label {{
    font-size:.69rem;
    font-weight:750;
    color:{MUTED};
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
}}

.kpi-value {{
    font-size:1.52rem;
    font-weight:850;
    color:{TEXT};
    letter-spacing:-.025em;
    margin:.22rem 0 .18rem;
}}

.kpi-delta {{
    font-size:.74rem;
    font-weight:850;
}}

.status-dot {{
    display:inline-block;
    width:8px;
    height:8px;
    border-radius:50%;
    margin-right:5px;
}}

.panel {{
    background:{WHITE};
    border:1px solid {BORDER};
    border-radius:14px;
    padding:15px 16px;
    box-shadow:0 4px 14px rgba(10,35,60,.035);
}}

.panel-title {{
    font-size:.98rem;
    font-weight:850;
    color:{TEXT};
    margin-bottom:4px;
}}

.panel-sub {{
    font-size:.68rem;
    color:{MUTED};
    margin-bottom:8px;
}}

.table-wrap table {{
    width:100%;
    border-collapse:collapse;
    font-size:.76rem;
}}

.table-wrap th {{
    text-align:left;
    color:{MUTED};
    text-transform:uppercase;
    letter-spacing:.03em;
    font-size:.64rem;
    padding:7px 4px;
    border-bottom:1px solid {BORDER};
}}

.table-wrap td {{
    padding:8px 4px;
    border-bottom:1px solid #EEF2F6;
}}

.alert-row {{
    display:flex;
    gap:9px;
    padding:9px 0;
    border-bottom:1px solid #EEF2F6;
}}

.alert-icon {{
    min-width:24px;
    height:24px;
    border-radius:50%;
    display:flex;
    align-items:center;
    justify-content:center;
    color:white;
    font-size:.72rem;
    font-weight:850;
}}

.alert-title {{
    font-size:.76rem;
    font-weight:800;
    color:{TEXT};
    line-height:1.2;
}}

.alert-sub {{
    font-size:.66rem;
    color:{MUTED};
    margin-top:2px;
    line-height:1.25;
}}

.agent-box {{
    background:linear-gradient(135deg,#E9F6FF,#F7FCFF);
    border:1px solid #CDE8FA;
    border-radius:14px;
    padding:15px 16px;
}}

.agent-dark {{
    background:linear-gradient(135deg,#071E36,#0A2D4F);
    border-radius:14px;
    padding:15px 16px;
    color:white;
}}

.status-pill {{
    display:inline-block;
    padding:3px 8px;
    border-radius:999px;
    font-size:.65rem;
    font-weight:850;
}}

div[data-testid="stMetric"] {{
    background:white;
    border:1px solid {BORDER};
    border-radius:14px;
    padding:12px 14px;
}}

.stButton>button {{
    border-radius:9px;
    font-weight:750;
}}

.stDownloadButton>button {{
    border-radius:9px;
    font-weight:750;
}}

@media (max-width:1200px) {{
    .page-title {{font-size:1.7rem;}}
    .kpi-value {{font-size:1.25rem;}}
    .kpi-card {{min-height:104px;}}
}}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# DATA
# -------------------------------------------------------
perf = pd.DataFrame({
    "Mês":["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago"],
    "Produção":[39200,40100,41800,40400,40900,40700,42100,41250],
    "Meta Produção":[45000,45500,46000,46500,47000,47000,47500,48000],
    "OEE":[0.64,0.68,0.73,0.66,0.67,0.66,0.70,0.714],
    "Margem":[0.312,0.307,0.301,0.294,0.288,0.284,0.281,0.278],
})

kpis = [
    ("Produção","41.250 un","45.000",-0.083,"-8,3%","↓"),
    ("OEE","71,4%","78%",-0.0846,"-6,6 pp","↓"),
    ("Produtividade","18,2 un/h","19,5",-0.067,"-6,7%","→"),
    ("Refugo","3,8%","2,5%",-0.52,"+1,3 pp","↑"),
    ("OTIF","89%","95%",-0.063,"-6 pp","↓"),
    ("Custo/unidade","R$ 18,42","R$ 17,10",-0.077,"+7,7%","↑"),
    ("Horas extras","1.280 h","900 h",-0.422,"+42%","↑"),
    ("Margem contribuição","27,8%","31%",-0.103,"-3,2 pp","↓"),
]

cards = [
    ("Receita Líquida","R$ 12,4 mi",-0.068,"-6,8% vs. meta"),
    ("Margem de Contribuição","27,8%",-0.103,"-3,2 pp vs. meta"),
    ("EBITDA Industrial","R$ 1,9 mi",-0.208,"-20,8% vs. meta"),
    ("Produção","41.250 un",-0.083,"-8,3% vs. meta"),
    ("OEE","71,4%",-0.0846,"-6,6 pp vs. meta"),
    ("Custo por Unidade","R$ 18,42",-0.077,"+7,7% vs. meta"),
]

dre_impacts = pd.DataFrame({
    "Impacto":["Menor volume produzido","Aumento de refugo","Horas extras","Manutenção corretiva","Maior consumo de MP"],
    "R$ mil":[220,110,95,75,48]
})

levers = pd.DataFrame({
    "Alavanca":["Disponibilidade Linha 3","Redução de refugo","Otimização de setup","Redução de horas extras","Consumo específico de MP"],
    "Gap Atual":["-12,4%","+1,3 pp","+18 h","+42%","+4%"],
    "Impacto Potencial":["R$ 312 mil","R$ 214 mil","R$ 96 mil","R$ 88 mil","R$ 72 mil"],
    "Prioridade":["Alta","Alta","Média","Média","Baixa"]
})

alerts = [
    ("Crítico","OEE da Linha 3 18% abaixo da meta","Impacto estimado: R$ 312 mil na margem"),
    ("Crítico","Refugo 1,3 pp acima da meta","Impacto estimado: R$ 214 mil"),
    ("Atenção","Horas extras 42% acima da meta","Impacto estimado: R$ 95 mil"),
    ("Atenção","Custo por unidade 7,7% acima da meta","Revisar consumo de matéria-prima"),
    ("Info","OTIF abaixo de 90% pelo segundo mês","Risco de perda de pedidos e receita"),
]

line_perf = pd.DataFrame({
    "Linha":["Linha 1","Linha 2","Linha 3","Linha 4"],
    "OEE":[0.81,0.76,0.64,0.74],
    "Disponibilidade":[0.86,0.82,0.69,0.80],
    "Performance":[0.96,0.94,0.95,0.93],
    "Qualidade":[0.98,0.985,0.975,0.99],
    "Refugo":[0.022,0.026,0.041,0.019],
    "Gap Produção":[-1200,-2100,-7200,-1800],
    "Paradas h":[18,31,79,25]
})

causes = pd.DataFrame({
    "Causa":["Falha mecânica","Setup","Falha elétrica","Falta de material","Microparadas","Qualidade"],
    "Horas":[58,41,29,22,18,12],
    "Impacto R$ mil":[164,96,82,61,45,39]
})

dre = pd.DataFrame({
    "Linha":["Receita Líquida","(-) Custos Variáveis","Margem de Contribuição","(-) Custos Fixos","EBITDA Industrial"],
    "Realizado":[12.40,-8.95,3.45,-1.55,1.90],
    "Meta":[13.30,-9.18,4.12,-1.72,2.40]
})

costs = pd.DataFrame({
    "Categoria":["Matéria-prima","Mão de obra direta","Energia variável","Fretes","Manutenção","Estrutura fabril","Supervisão","Depreciação"],
    "Tipo":["Variável","Variável","Variável","Variável","Fixo","Fixo","Fixo","Fixo"],
    "Realizado R$ mil":[5200,1680,730,620,510,430,370,240],
    "Orçamento R$ mil":[4950,1550,680,590,440,410,340,230]
})

actions_df = pd.DataFrame({
    "Prioridade":["Alta","Alta","Média","Média"],
    "Problema":["Disponibilidade Linha 3","Refugo Produto A","Horas extras","Setup Linha 2"],
    "Ação":["Plano de confiabilidade MX-04","Revisar parâmetros de processo","Redimensionar turnos","SMED em família B"],
    "Responsável":["Ger. Manutenção","Ger. Qualidade","Ger. Produção","Eng. Processos"],
    "Prazo":["10/09/2026","12/09/2026","15/09/2026","18/09/2026"],
    "Impacto":["R$ 312 mil","R$ 214 mil","R$ 88 mil","R$ 96 mil"],
    "Status":["Em andamento","Não iniciado","Em andamento","Planejado"]
})

# -------------------------------------------------------
# HELPERS
# -------------------------------------------------------
def status_color(delta):
    if delta < -0.10:
        return RED
    if delta < 0:
        return ORANGE
    return GREEN

def navigate(page):
    st.session_state["page"] = page
    st.rerun()

def header(title, subtitle):
    c1,c2,c3,c4 = st.columns([1.15,1.15,.85,2.2], gap="small")
    with c1:
        st.selectbox("Grupo",["Grupo Industrial S.A."],label_visibility="collapsed",key=f"g_{title}")
    with c2:
        st.selectbox("Planta",["Planta São Paulo","Todas as plantas"],label_visibility="collapsed",key=f"p_{title}")
    with c3:
        st.selectbox("Período",["Ago/2026","Jul/2026","Jun/2026"],label_visibility="collapsed",key=f"d_{title}")
    with c4:
        st.markdown('<div class="top-quote">“Transformar dados em decisões<br>que geram mais margem.”</div>',unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">EXECUÇÃO HOJE. COMPETITIVIDADE AMANHÃ.</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="page-title">{title}</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{subtitle}</div>',unsafe_allow_html=True)

def kpi_card(label,value,delta,delta_txt):
    c=status_color(delta)
    return f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      <div class="kpi-delta" style="color:{c}">
        <span class="status-dot" style="background:{c}"></span>{delta_txt}
      </div>
    </div>
    """

def kpi_table_html():
    rows=[]
    for indicador,mes,meta,delta,desvio_txt,tend in kpis:
        c=status_color(delta)
        rows.append(
            f"<tr><td><b>{indicador}</b></td><td>{mes}</td><td>{meta}</td>"
            f"<td style='color:{c};font-weight:850'>{desvio_txt}</td>"
            f"<td style='color:{c};font-weight:850'>{tend}</td></tr>"
        )
    return f"""
    <div class="panel table-wrap">
      <div class="panel-title">Principais Indicadores</div>
      <table>
        <thead><tr><th>Indicador</th><th>Mês</th><th>Meta</th><th>Desvio</th><th>Tend.</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </div>
    """

def alert_html(level,title,subtitle):
    if level=="Crítico":
        c=RED;symbol="!"
    elif level=="Atenção":
        c=ORANGE;symbol="!"
    else:
        c=INFO;symbol="i"
    return f"""
    <div class="alert-row">
      <div class="alert-icon" style="background:{c}">{symbol}</div>
      <div>
        <div class="alert-title">{title}</div>
        <div class="alert-sub">{subtitle}</div>
      </div>
    </div>
    """

def priority_badge(priority):
    if priority=="Alta":
        return f"<span class='status-pill' style='background:#FFF0EF;color:{RED};border:1px solid #FFC9C6'>Alta</span>"
    if priority=="Média":
        return f"<span class='status-pill' style='background:#FFF5E8;color:{ORANGE};border:1px solid #FFD7AE'>Média</span>"
    return f"<span class='status-pill' style='background:#EAF8F1;color:{GREEN};border:1px solid #C4EAD7'>Baixa</span>"

# -------------------------------------------------------
# SIDEBAR NAVIGATION
# -------------------------------------------------------
if "page" not in st.session_state:
    st.session_state["page"]="Cockpit Executivo"

pages = [
    "Cockpit Executivo",
    "Performance Operacional",
    "Diagnóstico e Causas",
    "Finanças / DRE",
    "Alavancas de Valor",
    "Plano de Ação",
    "Agente de Performance",
    "Relatórios",
    "Configurações"
]

with st.sidebar:
    logo = Path(__file__).parent/"logo_h2m_white.jpeg"
    if logo.exists():
        st.image(str(logo),width=145)
    st.markdown('<div class="brand-sub">Da operação ao resultado.</div>',unsafe_allow_html=True)

    for p in pages:
        active = st.session_state["page"] == p
        if st.button(p, key=f"nav_{p}", type="primary" if active else "secondary", use_container_width=True):
            navigate(p)

    st.markdown("""
    <div class="sidebar-footer">
      <b>Indústrias mais eficientes.<br>Resultados mais fortes.</b>
      <div class="sidebar-tag">PESSOAS &nbsp;&nbsp; DADOS &nbsp;&nbsp; AÇÃO</div>
    </div>
    """,unsafe_allow_html=True)

# -------------------------------------------------------
# PAGES
# -------------------------------------------------------
page = st.session_state["page"]

if page == "Cockpit Executivo":
    header("Cockpit Executivo","Visão integrada da performance da operação e do impacto no resultado.")

    cols=st.columns(6,gap="small")
    for c,item in zip(cols,cards):
        with c:
            st.markdown(kpi_card(*item),unsafe_allow_html=True)

    st.write("")
    c1,c2,c3=st.columns([1.03,1.22,.72],gap="small")

    with c1:
        st.markdown(kpi_table_html(),unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="panel"><div class="panel-title">Evolução da Performance</div><div class="panel-sub">Produção realizada x meta e tendência do OEE</div>',unsafe_allow_html=True)
        fig=go.Figure()
        fig.add_bar(x=perf["Mês"],y=perf["Meta Produção"],name="Meta",marker_color="#DCE6F0")
        fig.add_bar(x=perf["Mês"],y=perf["Produção"],name="Realizado",marker_color=BLUE)
        fig.add_trace(go.Scatter(x=perf["Mês"],y=perf["OEE"]*60000,mode="lines+markers",name="OEE",
                                 line=dict(color=ORANGE,width=3)))
        fig.update_layout(height=300,margin=dict(l=0,r=0,t=5,b=0),barmode="overlay",
                          paper_bgcolor="white",plot_bgcolor="white",
                          legend=dict(orientation="h",y=1.10),
                          xaxis=dict(showgrid=False),yaxis=dict(gridcolor="#EEF2F6"))
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        st.markdown('</div>',unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="panel"><div class="panel-title">Status da Fábrica</div><div class="panel-sub">Saúde consolidada dos indicadores</div>',unsafe_allow_html=True)
        fig=go.Figure(go.Pie(labels=["Em linha","Atenção","Crítico"],values=[5,2,1],hole=.65,
                             marker=dict(colors=[GREEN,ORANGE,RED]),textinfo="none"))
        fig.update_layout(height=165,margin=dict(l=0,r=0,t=0,b=0),showlegend=False,
                          annotations=[dict(text="<b>62%</b><br><span style='font-size:10px'>em linha</span>",
                                            x=.5,y=.5,showarrow=False)])
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        st.markdown(f"""
        <div style="font-size:.69rem;color:{MUTED}">
        <span class='status-dot' style='background:{GREEN}'></span>5 em linha &nbsp;
        <span class='status-dot' style='background:{ORANGE}'></span>2 atenção &nbsp;
        <span class='status-dot' style='background:{RED}'></span>1 crítico
        </div>
        </div>
        """,unsafe_allow_html=True)

        st.write("")
        st.markdown(f"""
        <div class="panel">
          <div class="panel-title">Estrutura de Custos</div>
          <div style="height:12px;border-radius:8px;overflow:hidden;display:flex;margin:8px 0 10px">
            <div style="width:63%;background:{BLUE}"></div>
            <div style="width:37%;background:#B7D8EF"></div>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:.76rem">
            <div><span style="color:{MUTED}">Variável</span><br><b>63%</b></div>
            <div style="text-align:right"><span style="color:{MUTED}">Fixo</span><br><b>37%</b></div>
          </div>
        </div>
        """,unsafe_allow_html=True)

    st.write("")
    c1,c2,c3=st.columns([1.02,1.08,.8],gap="small")

    with c1:
        st.markdown('<div class="panel"><div class="panel-title">Top 5 Impactos no DRE</div><div class="panel-sub">Efeito estimado sobre EBITDA no mês</div>',unsafe_allow_html=True)
        df=dre_impacts.sort_values("R$ mil")
        fig=px.bar(df,x="R$ mil",y="Impacto",orientation="h",text="R$ mil")
        fig.update_traces(marker_color="#F24B4B",texttemplate="R$ %{text} mil",textposition="outside")
        fig.update_layout(height=245,margin=dict(l=0,r=30,t=0,b=0),paper_bgcolor="white",plot_bgcolor="white",
                          yaxis_title=None,xaxis_title=None,xaxis=dict(gridcolor="#EEF2F6"))
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        st.markdown('</div>',unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="panel"><div class="panel-title">Alavancas com Maior Potencial</div><div class="panel-sub">Prioridade por impacto financeiro</div>',unsafe_allow_html=True)
        for _,r in levers.iterrows():
            st.markdown(
                f"<div style='display:grid;grid-template-columns:1.7fr .8fr 1fr .7fr;gap:7px;padding:7px 0;"
                f"border-bottom:1px solid #EEF2F6;font-size:.71rem;align-items:center'>"
                f"<div><b>{r['Alavanca']}</b></div><div>{r['Gap Atual']}</div><div>{r['Impacto Potencial']}</div>"
                f"<div>{priority_badge(r['Prioridade'])}</div></div>",
                unsafe_allow_html=True
            )
        st.write("")
        if st.button("Abrir todas as alavancas",use_container_width=True):
            navigate("Alavancas de Valor")
        st.markdown('</div>',unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="panel"><div class="panel-title">Principais Alertas do Mês</div>',unsafe_allow_html=True)
        for a in alerts:
            st.markdown(alert_html(*a),unsafe_allow_html=True)
        st.write("")
        if st.button("Ver diagnóstico completo",use_container_width=True):
            navigate("Diagnóstico e Causas")
        st.markdown('</div>',unsafe_allow_html=True)

    st.write("")
    c1,c2=st.columns([1.5,.7],gap="small")
    with c1:
        st.markdown("""
        <div class="agent-box">
          <div style="font-weight:850;color:#10233F;margin-bottom:6px">✦ Diagnóstico Executivo</div>
          <div style="font-size:.79rem;color:#304158;line-height:1.45">
          A fábrica fechou agosto <b>8,3% abaixo da meta de produção</b>, com impacto estimado de
          <b>R$ 500 mil no EBITDA</b>. O principal fator foi a menor disponibilidade da Linha 3,
          seguida pelo aumento de refugo e horas extras.
          </div>
          <div style="font-size:.74rem;color:#304158;margin-top:8px">
          <b>Prioridades:</b> paradas não planejadas da Linha 3; redução de refugo; revisão de turnos e horas extras.
          </div>
        </div>
        """,unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="agent-dark">
          <div style="font-weight:850;margin-bottom:5px">Agente de Performance</div>
          <div style="font-size:.71rem;color:#B9CEE0">Investigue causas, simule cenários e priorize ações.</div>
        </div>
        """,unsafe_allow_html=True)
        if st.button("Conversar com o agente",type="primary",use_container_width=True):
            navigate("Agente de Performance")

elif page == "Performance Operacional":
    header("Performance Operacional","Abertura por linha, máquina, produto e turno.")
    c1,c2,c3,c4=st.columns(4,gap="small")
    c1.metric("OEE Médio","71,4%","-6,6 pp")
    c2.metric("Disponibilidade","74,8%","-5,2 pp")
    c3.metric("Performance","94,5%","+0,8 pp")
    c4.metric("Qualidade","98,1%","-0,4 pp")
    st.write("")
    c1,c2=st.columns(2,gap="small")
    with c1:
        st.markdown('<div class="panel"><div class="panel-title">OEE por Linha</div>',unsafe_allow_html=True)
        fig=px.bar(line_perf,x="Linha",y="OEE",text=line_perf["OEE"].map(lambda x:f"{x:.1%}"))
        fig.update_traces(marker_color=[GREEN,ORANGE,RED,ORANGE],textposition="outside")
        fig.update_yaxes(tickformat=".0%",range=[0,1])
        fig.update_layout(height=330,margin=dict(l=0,r=0,t=5,b=0),paper_bgcolor="white",plot_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        st.markdown('</div>',unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="panel"><div class="panel-title">Paradas x Gap de Produção</div>',unsafe_allow_html=True)
        fig=px.scatter(line_perf,x="Paradas h",y="Gap Produção",size="Paradas h",text="Linha")
        fig.update_traces(marker_color=BLUE,textposition="top center")
        fig.update_layout(height=330,margin=dict(l=0,r=0,t=5,b=0),paper_bgcolor="white",plot_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        st.markdown('</div>',unsafe_allow_html=True)
    st.write("")
    st.dataframe(line_perf,use_container_width=True,hide_index=True)

elif page == "Diagnóstico e Causas":
    header("Diagnóstico e Causas","Do desvio executivo à causa-raiz operacional.")
    c1,c2=st.columns(2,gap="small")
    with c1:
        st.markdown('<div class="panel"><div class="panel-title">Pareto de Causas</div>',unsafe_allow_html=True)
        df=causes.sort_values("Horas")
        fig=px.bar(df,x="Horas",y="Causa",orientation="h",text="Horas")
        fig.update_traces(marker_color=BLUE)
        fig.update_layout(height=330,margin=dict(l=0,r=0,t=5,b=0),paper_bgcolor="white",plot_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        st.markdown('</div>',unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="panel"><div class="panel-title">Impacto Financeiro por Causa</div>',unsafe_allow_html=True)
        df=causes.sort_values("Impacto R$ mil")
        fig=px.bar(df,x="Impacto R$ mil",y="Causa",orientation="h",text="Impacto R$ mil")
        fig.update_traces(marker_color=RED)
        fig.update_layout(height=330,margin=dict(l=0,r=0,t=5,b=0),paper_bgcolor="white",plot_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        st.markdown('</div>',unsafe_allow_html=True)
    st.write("")
    st.markdown("""
    <div class="panel">
      <div class="panel-title">Árvore de Diagnóstico</div>
      <div style="font-size:.82rem;line-height:1.8;color:#304158">
      <b>Produção abaixo da meta (-8,3%)</b><br>
      &nbsp;&nbsp;↳ Linha 3 concentra 58% do gap<br>
      &nbsp;&nbsp;&nbsp;&nbsp;↳ Disponibilidade é o componente mais fraco<br>
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↳ MX-04 concentrou 37 h de parada corretiva<br>
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↳ Falha mecânica é a principal causa<br>
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↳ <b>Impacto estimado: R$ 164 mil</b>
      </div>
    </div>
    """,unsafe_allow_html=True)
    st.write("")
    if st.button("Criar plano de ação",type="primary"):
        navigate("Plano de Ação")

elif page == "Finanças / DRE":
    header("Finanças / DRE","Conecte desempenho operacional, estrutura de custos e resultado.")
    c1,c2,c3,c4=st.columns(4,gap="small")
    c1.metric("Receita Líquida","R$ 12,4 mi","-6,8%")
    c2.metric("Margem de Contribuição","R$ 3,45 mi","-R$ 670 mil")
    c3.metric("Custos Fixos","R$ 1,55 mi","R$ 170 mil melhor")
    c4.metric("EBITDA Industrial","R$ 1,90 mi","-R$ 500 mil")
    st.write("")
    c1,c2=st.columns([1.1,.9],gap="small")
    with c1:
        st.markdown('<div class="panel"><div class="panel-title">DRE Gerencial</div>',unsafe_allow_html=True)
        view=dre.copy()
        view["Realizado"]=view["Realizado"].map(lambda x:f"R$ {x:.2f} mi".replace(".",","))
        view["Meta"]=view["Meta"].map(lambda x:f"R$ {x:.2f} mi".replace(".",","))
        st.dataframe(view,use_container_width=True,hide_index=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="panel"><div class="panel-title">Estrutura de Custos</div>',unsafe_allow_html=True)
        cdf=costs.groupby("Tipo")["Realizado R$ mil"].sum().reset_index()
        fig=px.pie(cdf,names="Tipo",values="Realizado R$ mil",hole=.62,
                   color="Tipo",color_discrete_map={"Variável":BLUE,"Fixo":"#B7D8EF"})
        fig.update_layout(height=280,margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        st.markdown('</div>',unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="panel"><div class="panel-title">Bridge do EBITDA</div>',unsafe_allow_html=True)
    fig=go.Figure(go.Waterfall(
        x=["Meta EBITDA","Volume","Refugo","Horas extras","Manutenção","Consumo MP","Realizado"],
        measure=["absolute","relative","relative","relative","relative","relative","total"],
        y=[2400,-220,-110,-95,-75,-48,0],
        decreasing={"marker":{"color":RED}},
        increasing={"marker":{"color":GREEN}},
        totals={"marker":{"color":BLUE}},
    ))
    fig.update_layout(height=330,margin=dict(l=0,r=0,t=10,b=0),paper_bgcolor="white",plot_bgcolor="white")
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    st.markdown('</div>',unsafe_allow_html=True)
    st.write("")
    cc=costs.copy()
    cc["Desvio R$ mil"]=cc["Realizado R$ mil"]-cc["Orçamento R$ mil"]
    st.dataframe(cc,use_container_width=True,hide_index=True)

elif page == "Alavancas de Valor":
    header("Alavancas de Valor","Priorize ações pela capacidade de recuperar margem e EBITDA.")
    st.dataframe(levers,use_container_width=True,hide_index=True)
    st.write("")
    st.markdown('<div class="panel"><div class="panel-title">Simulador de Alavancas</div><div class="panel-sub">Teste cenários e veja o impacto potencial</div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    oee=c1.slider("OEE alvo",65.0,90.0,80.0,.5)
    scrap=c2.slider("Refugo alvo (%)",1.0,5.0,2.5,.1)
    overtime=c3.slider("Redução de horas extras (%)",0,50,20)
    impact=max(0,oee-71.4)*38 + max(0,3.8-scrap)*82 + overtime*2.2
    st.success(f"Impacto potencial indicativo no EBITDA: R$ {impact:,.0f} mil".replace(",","."))
    if st.button("Transformar cenário em plano de ação",type="primary"):
        navigate("Plano de Ação")
    st.markdown('</div>',unsafe_allow_html=True)

elif page == "Plano de Ação":
    header("Plano de Ação","Transforme diagnóstico em execução, responsabilidade e captura de valor.")
    if "actions" not in st.session_state:
        st.session_state["actions"]=actions_df.copy()
    st.dataframe(st.session_state["actions"],use_container_width=True,hide_index=True)
    st.write("")
    with st.form("new_action",clear_on_submit=True):
        c1,c2=st.columns(2)
        problema=c1.text_input("Problema / oportunidade")
        responsavel=c2.text_input("Responsável")
        acao=st.text_area("Ação")
        c3,c4,c5=st.columns(3)
        prazo=c3.text_input("Prazo",placeholder="dd/mm/aaaa")
        prioridade=c4.selectbox("Prioridade",["Alta","Média","Baixa"])
        impacto=c5.text_input("Impacto esperado",placeholder="R$ 100 mil")
        submitted=st.form_submit_button("Adicionar ação",type="primary")
        if submitted and problema and acao:
            new=pd.DataFrame([{
                "Prioridade":prioridade,
                "Problema":problema,
                "Ação":acao,
                "Responsável":responsavel,
                "Prazo":prazo,
                "Impacto":impacto,
                "Status":"Planejado"
            }])
            st.session_state["actions"]=pd.concat([st.session_state["actions"],new],ignore_index=True)
            st.success("Ação adicionada.")
            st.rerun()

elif page == "Agente de Performance":
    header("Agente de Performance","Investigue causas, simule cenários e transforme análise em decisão.")
    st.markdown("""
    <div class="agent-box">
      <div style="font-weight:850;margin-bottom:6px">Resumo executivo do período</div>
      <div style="font-size:.79rem;color:#304158;line-height:1.45">
      A operação está abaixo da meta em produção, OEE e margem de contribuição. A Linha 3 concentra
      a maior parcela do gap operacional. As maiores oportunidades estão em disponibilidade, refugo
      e horas extras.
      </div>
    </div>
    """,unsafe_allow_html=True)
    st.write("")
    if "chat" not in st.session_state:
        st.session_state["chat"]=[]
    for role,msg in st.session_state["chat"]:
        st.chat_message(role).write(msg)
    q=st.chat_input("Ex.: Qual o impacto de elevar o OEE para 80%?")
    if q:
        st.session_state["chat"].append(("user",q))
        ql=q.lower()
        if "oee" in ql:
            ans="Elevar o OEE de 71,4% para 80% representa potencial indicativo de aproximadamente R$ 327 mil em EBITDA, principalmente pela recuperação de disponibilidade da Linha 3."
        elif "refugo" in ql:
            ans="Reduzir o refugo de 3,8% para 2,5% representa potencial indicativo de R$ 107 mil no período, principalmente por menor consumo de matéria-prima e retrabalho."
        elif "linha" in ql:
            ans="A Linha 3 é a principal prioridade: OEE de 64%, maior volume de paradas e maior contribuição para o gap de produção."
        elif "ebitda" in ql or "margem" in ql:
            ans="O principal gap de EBITDA vem de menor volume produzido, seguido por refugo, horas extras e manutenção corretiva."
        else:
            ans="Os três focos prioritários são: recuperar disponibilidade da Linha 3, reduzir refugo e rever horas extras. Juntos, representam o maior potencial de recuperação financeira."
        st.session_state["chat"].append(("assistant",ans))
        st.rerun()

elif page == "Relatórios":
    header("Relatórios","Fechamentos executivos, comitês de performance e materiais de gestão.")
    st.markdown("""
    <div class="panel">
      <div class="panel-title">Relatórios disponíveis</div>
      <div style="font-size:.82rem;line-height:1.8;color:#304158">
      • Morning Industrial Brief<br>
      • Fechamento semanal de performance<br>
      • Comitê mensal de resultado<br>
      • DRE operacional comentado<br>
      • Top perdas e alavancas<br>
      • Plano de ação e captura de valor
      </div>
    </div>
    """,unsafe_allow_html=True)
    st.write("")
    report_text = """INDUSTRIAL PERFORMANCE - RESUMO EXECUTIVO
Produção: 41.250 un | Meta: 45.000
OEE: 71,4% | Meta: 78%
Margem de contribuição: 27,8% | Meta: 31%
EBITDA Industrial: R$ 1,9 mi | Gap estimado: R$ 500 mil

Principais causas:
1. Menor volume produzido
2. Refugo acima da meta
3. Horas extras
4. Manutenção corretiva

Prioridades:
- Recuperar disponibilidade da Linha 3
- Reduzir refugo
- Revisar dimensionamento de turnos
"""
    st.download_button("Baixar resumo executivo (.txt)",report_text,file_name="resumo_executivo.txt",type="primary")

elif page == "Configurações":
    header("Configurações","Cadastros, metas, estrutura de custos e futuras integrações.")
    tabs=st.tabs(["Dados","Metas","DRE / Custos","Usuários","Integrações"])
    with tabs[0]:
        uploaded=st.file_uploader("Carregar Excel / CSV",type=["xlsx","xls","csv"],accept_multiple_files=True)
        if uploaded:
            st.success(f"{len(uploaded)} arquivo(s) carregado(s). Próxima etapa: mapeador DE/PARA.")
    with tabs[1]:
        metas=pd.DataFrame({
            "Indicador":[k[0] for k in kpis],
            "Meta":[k[2] for k in kpis]
        })
        st.data_editor(metas,use_container_width=True,hide_index=True)
    with tabs[2]:
        st.data_editor(costs,use_container_width=True,hide_index=True)
    with tabs[3]:
        st.info("Perfis previstos: CEO, COO, CFO, Diretor Industrial, Gerente, Controller e Analista.")
    with tabs[4]:
        st.info("Roadmap: ERP, MES, WMS, CMMS, SQL e APIs.")
