
import streamlit as st
from ui.styles import page_header
from ui.components import top_filters

def render(d):
    top_filters()
    page_header("Relatórios","Fechamentos, comitês de performance e materiais executivos.")
    st.markdown("""
    <div class="section">
      <b>Relatórios previstos</b><br><br>
      • Morning Industrial Brief<br>
      • Fechamento semanal de performance<br>
      • Comitê mensal de resultado<br>
      • DRE operacional comentado<br>
      • Top perdas e alavancas<br>
      • Plano de ação e captura de valor
    </div>
    """, unsafe_allow_html=True)
    st.button("Gerar relatório executivo",type="primary")
