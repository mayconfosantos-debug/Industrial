
import streamlit as st
import plotly.express as px
from ui.styles import page_header, RED, ORANGE, BLUE
from ui.components import top_filters

def render(d):
    top_filters()
    page_header("Diagnóstico e Causas","Do desvio executivo à causa-raiz operacional.")
    c1,c2=st.columns([1,1])
    with c1:
        st.subheader("Pareto de Causas")
        df=d["causes"].sort_values("Horas")
        fig=px.bar(df,x="Horas",y="Causa",orientation="h",text="Horas")
        fig.update_traces(marker_color=BLUE)
        fig.update_layout(height=350,margin=dict(l=0,r=10,t=10,b=30),xaxis_title="Horas perdidas",yaxis_title=None)
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    with c2:
        st.subheader("Impacto Financeiro por Causa")
        df=d["causes"].sort_values("Impacto R$ mil")
        fig=px.bar(df,x="Impacto R$ mil",y="Causa",orientation="h",text="Impacto R$ mil")
        fig.update_traces(marker_color=RED)
        fig.update_layout(height=350,margin=dict(l=0,r=10,t=10,b=30),yaxis_title=None)
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

    st.subheader("Árvore de Diagnóstico")
    st.markdown("""
    <div class="section">
    <b>Produção abaixo da meta (-8,3%)</b><br>
    &nbsp;&nbsp;↳ <b>Linha 3</b> concentra 58% do gap<br>
    &nbsp;&nbsp;&nbsp;&nbsp;↳ <b>Disponibilidade</b> é o componente mais fraco<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↳ <b>MX-04</b> concentrou 37 h de parada corretiva<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↳ <b>Falha mecânica</b> é a principal causa<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↳ <b>Impacto estimado: R$ 164 mil</b>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Hipóteses e Evidências")
    st.dataframe(d["causes"],use_container_width=True,hide_index=True)
