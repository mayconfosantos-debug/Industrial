
import streamlit as st
import plotly.express as px
from ui.styles import page_header, BLUE, ORANGE, GREEN, RED
from ui.components import top_filters

def render(d):
    top_filters()
    page_header("Performance Operacional","Abertura da performance por linha, máquina, produto e turno.")
    df=d["line_perf"]

    c1,c2,c3,c4=st.columns(4)
    c1.metric("OEE Médio","71,4%","-6,6 pp")
    c2.metric("Disponibilidade","74,8%","-5,2 pp")
    c3.metric("Performance","94,5%","+0,8 pp")
    c4.metric("Qualidade","98,1%","-0,4 pp")

    c1,c2=st.columns(2)
    with c1:
        st.subheader("OEE por Linha")
        fig=px.bar(df,x="Linha",y="OEE",text_auto=".1%")
        fig.update_traces(marker_color=[GREEN,ORANGE,RED,ORANGE])
        fig.update_yaxes(tickformat=".0%")
        fig.update_layout(height=330,margin=dict(l=10,r=10,t=20,b=10),showlegend=False)
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    with c2:
        st.subheader("Paradas x Gap de Produção")
        fig=px.scatter(df,x="Paradas h",y="Gap Produção",size="Paradas h",text="Linha")
        fig.update_traces(marker_color=BLUE)
        fig.update_layout(height=330,margin=dict(l=10,r=10,t=20,b=10))
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

    st.subheader("Matriz de Performance")
    show=df.copy()
    for col in ["OEE","Disponibilidade","Performance","Qualidade","Refugo"]:
        show[col]=show[col].map(lambda x:f"{x:.1%}".replace(".",","))
    st.dataframe(show,use_container_width=True,hide_index=True)
