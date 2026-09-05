
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from ui.styles import page_header, card_html, status_color, CYAN, BLUE, NAVY, RED, ORANGE, GREEN, MUTED
from ui.components import top_filters, kpi_table_html, alert_html, priority_badge

def render(d):
    top_filters()
    page_header("Cockpit Executivo","Visão integrada da performance da operação e do impacto no resultado.")

    cols = st.columns(6)
    for c, item in zip(cols, d["cards"]):
        with c:
            st.markdown(card_html(item["label"],item["value"],item["delta"],item["delta_txt"]), unsafe_allow_html=True)

    c1,c2,c3 = st.columns([1.05,1.25,.68])
    with c1:
        st.markdown(kpi_table_html(d["kpis"]), unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="section"><div class="section-title">Evolução da Performance</div>', unsafe_allow_html=True)
        p=d["perf"]
        fig=go.Figure()
        fig.add_bar(x=p["Mês"],y=p["Produção"],name="Realizado",marker_color=BLUE)
        fig.add_bar(x=p["Mês"],y=p["Meta Produção"],name="Meta",marker_color="#DCE6F0")
        fig.add_trace(go.Scatter(x=p["Mês"],y=p["OEE"]*60000,mode="lines+markers",name="OEE",line=dict(color=ORANGE,width=3)))
        fig.update_layout(height=330,margin=dict(l=10,r=10,t=10,b=10),barmode="group",
                          paper_bgcolor="white",plot_bgcolor="white",legend=dict(orientation="h",y=1.08),
                          yaxis=dict(gridcolor="#EEF2F6"))
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="section"><div class="section-title">Status da Fábrica</div>', unsafe_allow_html=True)
        fig=go.Figure(go.Pie(labels=["Em linha","Atenção","Fora da meta"],values=[5,2,1],hole=.62,
                             marker=dict(colors=[GREEN,ORANGE,RED]),textinfo="none"))
        fig.update_layout(height=190,margin=dict(l=0,r=0,t=0,b=0),showlegend=False,
                          annotations=[dict(text="<b>62%</b><br><span style='font-size:10px'>indicadores<br>em linha</span>",x=.5,y=.5,showarrow=False)])
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        st.markdown('<div class="small-muted">● <span style="color:#12A866">Em linha</span> &nbsp; 5</div>'
                    '<div class="small-muted">● <span style="color:#FF7A00">Atenção</span> &nbsp; 2</div>'
                    '<div class="small-muted">● <span style="color:#E53935">Fora da meta</span> &nbsp; 1</div>',
                    unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section"><div class="section-title">Estrutura de Custos</div>'
                    '<div style="height:14px;border-radius:8px;overflow:hidden;display:flex">'
                    '<div style="width:63%;background:#0B5EA8"></div><div style="width:37%;background:#B9D8F2"></div></div>'
                    '<div style="display:flex;justify-content:space-between;margin-top:9px">'
                    '<div><div class="small-muted">Custo Variável</div><b>63%</b></div>'
                    '<div><div class="small-muted">Custo Fixo</div><b>37%</b></div></div></div>',
                    unsafe_allow_html=True)

    c1,c2,c3=st.columns([1.05,1.1,.75])
    with c1:
        st.markdown('<div class="section"><div class="section-title">Top 5 Impactos no DRE (Mês)</div>', unsafe_allow_html=True)
        df=d["dre_impacts"].sort_values("R$ mil")
        fig=px.bar(df,x="R$ mil",y="Impacto",orientation="h")
        fig.update_traces(marker_color="#F04444")
        fig.update_layout(height=260,margin=dict(l=0,r=10,t=10,b=30),paper_bgcolor="white",plot_bgcolor="white",
                          xaxis_title="Impacto no EBITDA (R$ mil)",yaxis_title=None,xaxis=dict(gridcolor="#EEF2F6"))
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="section"><div class="section-title">Alavancas com Maior Potencial</div>', unsafe_allow_html=True)
        for _,r in d["levers"].iterrows():
            st.markdown(
                f"<div style='display:grid;grid-template-columns:2.1fr 1fr 1.3fr .8fr;gap:8px;"
                f"padding:8px 0;border-bottom:1px solid #EEF2F6;font-size:.77rem;align-items:center'>"
                f"<div>{r['Alavanca']}</div><div>{r['Gap Atual']}</div><div>{r['Impacto Potencial']}</div>"
                f"<div>{priority_badge(r['Prioridade'])}</div></div>",
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="section"><div class="section-title">Principais Alertas do Mês</div>', unsafe_allow_html=True)
        for a in d["alerts"]:
            st.markdown(alert_html(*a),unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    c1,c2=st.columns([1.45,.65])
    with c1:
        st.markdown("""
        <div class="agent-box">
          <div style="font-weight:850;color:#10233F;margin-bottom:6px">✦ Diagnóstico Executivo (IA)</div>
          <div style="font-size:.82rem;color:#25364C">
          A fábrica fechou agosto com <b>8,3% abaixo da meta de produção</b>, impactando aproximadamente
          <b>R$ 500 mil no EBITDA</b>. O principal fator foi a menor disponibilidade da Linha 3,
          seguido pelo aumento de refugo e horas extras.
          </div>
          <div style="margin-top:10px;font-size:.8rem">
          <b>Principais recomendações:</b><br>
          1. Atacar paradas não planejadas da Linha 3<br>
          2. Implementar plano de redução de refugo no Produto A<br>
          3. Revisar dimensionamento de turnos e horas extras
          </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="section" style="background:#071E36"><div style="color:white;font-weight:850;margin-bottom:8px">Pergunte ao Agente de Performance</div>', unsafe_allow_html=True)
        st.text_input("agent_home",placeholder="Ex.: Qual o impacto de aumentar o OEE para 85%?",label_visibility="collapsed")
        st.markdown('<div style="color:#73DFFF;font-size:.72rem">Ver exemplos de perguntas</div></div>', unsafe_allow_html=True)
