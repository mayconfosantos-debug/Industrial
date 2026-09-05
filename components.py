
import streamlit as st
import pandas as pd
from .styles import RED, ORANGE, GREEN, CYAN, BLUE, NAVY, TEXT, MUTED, BORDER, status_color

def top_filters():
    c1,c2,c3,c4 = st.columns([1.15,1.15,.9,2.8])
    with c1:
        st.selectbox("Grupo", ["Grupo Industrial S.A."], label_visibility="collapsed")
    with c2:
        st.selectbox("Planta", ["Planta São Paulo","Todas as plantas"], label_visibility="collapsed")
    with c3:
        st.selectbox("Período", ["Ago/2026","Jul/2026","Jun/2026"], label_visibility="collapsed")
    with c4:
        st.markdown(
            '<div style="text-align:right;color:#10233F;font-weight:750;padding-top:.45rem;">'
            '“Transformar dados em decisões que geram mais margem.”</div>',
            unsafe_allow_html=True
        )

def kpi_table_html(kpis):
    rows = []
    for r in kpis:
        c = status_color(r["desvio"])
        rows.append(
            f"<tr><td>{r['indicador']}</td><td>{r['mes']}</td><td>{r['meta']}</td>"
            f"<td style='color:{c};font-weight:800'>{r['desvio_txt']}</td>"
            f"<td style='color:{c};font-size:1.1rem'>{r['tend']}</td></tr>"
        )
    return f"""
    <div class="section">
      <div class="section-title">Principais Indicadores</div>
      <table style="width:100%;border-collapse:collapse;font-size:.82rem">
        <thead><tr style="text-align:left;color:{MUTED};border-bottom:1px solid {BORDER}">
          <th style="padding:7px 4px">Indicador</th><th>Mês</th><th>Meta</th><th>Desvio</th><th>Tendência</th>
        </tr></thead>
        <tbody>
          {''.join(rows)}
        </tbody>
      </table>
      <style>
        tbody td {{padding:7px 4px;border-bottom:1px solid #EEF2F6;}}
      </style>
    </div>
    """

def alert_html(level, title, subtitle):
    color = RED if level=="crítico" else ORANGE if level=="atenção" else BLUE
    symbol = "!" if level!="info" else "i"
    return f"""
    <div style="display:flex;gap:10px;padding:9px 0;border-bottom:1px solid #EDF1F5;">
      <div style="width:26px;height:26px;border-radius:50%;background:{color};color:white;
                  display:flex;align-items:center;justify-content:center;font-weight:850;">{symbol}</div>
      <div><div style="font-size:.82rem;font-weight:800;color:{TEXT};">{title}</div>
      <div style="font-size:.72rem;color:{MUTED};">{subtitle}</div></div>
    </div>
    """

def priority_badge(x):
    if x == "Alta":
        return f"<span class='status-pill' style='background:#FFF0EF;color:{RED};border:1px solid #FFC7C4'>Alta</span>"
    if x == "Média":
        return f"<span class='status-pill' style='background:#FFF5E8;color:{ORANGE};border:1px solid #FFD7A8'>Média</span>"
    return f"<span class='status-pill' style='background:#EAF8F1;color:{GREEN};border:1px solid #BFE9D3'>Baixa</span>"
