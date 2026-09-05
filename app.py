
import streamlit as st
from pathlib import Path

from styles import inject_css
from demo import get_demo
import cockpit, operations, diagnostics, finance, levers, actions, agent, reports, settings

st.set_page_config(
    page_title="Industrial Performance | H2M",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)
inject_css()
d = get_demo()

with st.sidebar:
    logo = Path(__file__).parent / "logo_h2m_white.jpeg"
    if logo.exists():
        st.image(str(logo), width=150)
    st.markdown(
        '<div style="font-size:.8rem;color:#BBD1E5;margin:-6px 0 14px 2px">Da operação ao resultado.</div>',
        unsafe_allow_html=True
    )

    nav = st.radio(
        "Navegação",
        [
            "Cockpit Executivo",
            "Performance Operacional",
            "Diagnóstico e Causas",
            "Finanças / DRE",
            "Alavancas de Valor",
            "Plano de Ação",
            "Agente de Performance",
            "Relatórios",
            "Configurações",
        ],
        label_visibility="collapsed",
    )

    st.markdown("<br><br>",unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:1.15rem;font-weight:850">Indústrias mais eficientes.<br>Resultados mais fortes.</div>'
        '<div style="margin-top:12px;color:#76DFFF;font-size:.68rem;letter-spacing:.08em">PESSOAS &nbsp;&nbsp; DADOS &nbsp;&nbsp; AÇÃO</div>',
        unsafe_allow_html=True
    )

routes = {
    "Cockpit Executivo": cockpit.render,
    "Performance Operacional": operations.render,
    "Diagnóstico e Causas": diagnostics.render,
    "Finanças / DRE": finance.render,
    "Alavancas de Valor": levers.render,
    "Plano de Ação": actions.render,
    "Agente de Performance": agent.render,
    "Relatórios": reports.render,
    "Configurações": settings.render,
}
routes[nav](d)
