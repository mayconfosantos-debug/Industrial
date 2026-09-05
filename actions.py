
import streamlit as st
from ui.styles import page_header
from ui.components import top_filters

def render(d):
    top_filters()
    page_header("Plano de Ação","Transforme diagnóstico em execução, responsabilidade e captura de valor.")
    st.dataframe(d["actions"],use_container_width=True,hide_index=True)
    st.subheader("Nova ação")
    c1,c2=st.columns(2)
    c1.text_input("Problema / oportunidade")
    c2.text_input("Responsável")
    st.text_area("Ação recomendada")
    c3,c4,c5=st.columns(3)
    c3.date_input("Prazo")
    c4.selectbox("Prioridade",["Alta","Média","Baixa"])
    c5.text_input("Impacto esperado (R$)")
    st.button("Adicionar ação",type="primary")
