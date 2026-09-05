
import streamlit as st
import pandas as pd
from styles import page_header
from components import top_filters

def render(d):
    top_filters()
    page_header("Alavancas de Valor","Onde agir primeiro para recuperar margem e EBITDA.")
    st.subheader("Ranking Executivo")
    st.dataframe(d["levers"],use_container_width=True,hide_index=True)

    st.subheader("Simulador de Alavancas")
    c1,c2,c3=st.columns(3)
    oee=c1.slider("OEE alvo",65,90,80)
    scrap=c2.slider("Refugo alvo (%)",1.0,5.0,2.5,.1)
    overtime=c3.slider("Redução de horas extras (%)",0,50,20)

    oee_gain=max(0,oee-71.4)*38
    scrap_gain=max(0,3.8-scrap)*82
    ot_gain=overtime*2.2
    total=oee_gain+scrap_gain+ot_gain
    st.success(f"Impacto potencial indicativo no EBITDA: R$ {total:,.0f} mil".replace(",","."))
    st.caption("Simulação gerencial para priorização. Na versão conectada, os coeficientes virão do modelo econômico de cada planta.")
