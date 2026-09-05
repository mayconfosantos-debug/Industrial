
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from styles import page_header, BLUE, RED, GREEN, ORANGE
from components import top_filters

def render(d):
    top_filters()
    page_header("Finanças / DRE","Conexão entre performance operacional, estrutura de custos e resultado.")
    dre=d["dre"].copy()
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Receita Líquida","R$ 12,4 mi","-6,8%")
    c2.metric("Margem Contribuição","R$ 3,45 mi","-R$ 670 mil")
    c3.metric("Custos Fixos","R$ 1,55 mi","+R$ 170 mil melhor")
    c4.metric("EBITDA Industrial","R$ 1,90 mi","-R$ 500 mil")

    c1,c2=st.columns([1.1,.9])
    with c1:
        st.subheader("DRE Gerencial — Realizado x Meta")
        view=dre.copy()
        view["Realizado"]=view["Realizado"].map(lambda x:f"R$ {x:.2f} mi".replace(".",","))
        view["Meta"]=view["Meta"].map(lambda x:f"R$ {x:.2f} mi".replace(".",","))
        st.dataframe(view,use_container_width=True,hide_index=True)
    with c2:
        st.subheader("Estrutura de Custos")
        costs=d["costs"].groupby("Tipo")["Realizado R$ mil"].sum().reset_index()
        fig=px.pie(costs,names="Tipo",values="Realizado R$ mil",hole=.58)
        fig.update_layout(height=300,margin=dict(l=0,r=0,t=10,b=10))
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

    st.subheader("Bridge do EBITDA")
    fig=go.Figure(go.Waterfall(
        x=["Meta EBITDA","Volume","Refugo","Horas extras","Manutenção","Consumo MP","Realizado"],
        measure=["absolute","relative","relative","relative","relative","relative","total"],
        y=[2400,-220,-110,-95,-75,-48,0],
        connector={"line":{"color":"#A8B4C1"}}
    ))
    fig.update_layout(height=350,margin=dict(l=10,r=10,t=20,b=20),yaxis_title="R$ mil")
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

    st.subheader("Custo Fixo x Variável por Categoria")
    costs=d["costs"].copy()
    costs["Desvio R$ mil"]=costs["Realizado R$ mil"]-costs["Orçamento R$ mil"]
    st.dataframe(costs,use_container_width=True,hide_index=True)
