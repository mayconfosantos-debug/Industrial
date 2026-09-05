
import streamlit as st
from ui.styles import page_header

def render(d):
    page_header("Configurações","Cadastros, metas, estrutura de custos, importação e regras do modelo.")
    tabs=st.tabs(["Dados","Metas","DRE / Custos","Usuários","Integrações"])
    with tabs[0]:
        st.file_uploader("Carregar Excel / CSV",type=["xlsx","xls","csv"],accept_multiple_files=True)
        st.info("Próxima evolução: mapeador DE/PARA visual de colunas.")
    with tabs[1]:
        st.dataframe(d["kpis"],use_container_width=True,hide_index=True)
    with tabs[2]:
        st.dataframe(d["costs"],use_container_width=True,hide_index=True)
    with tabs[3]:
        st.write("Perfis previstos: CEO, COO, CFO, Diretor Industrial, Gerente, Controller, Analista.")
    with tabs[4]:
        st.write("Roadmap: ERP, MES, WMS, CMMS, SQL e APIs.")
