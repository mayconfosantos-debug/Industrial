
import streamlit as st
from styles import page_header
from components import top_filters

def render(d):
    top_filters()
    page_header("Agente de Performance","Pergunte aos dados, investigue causas e simule impacto no resultado.")

    st.markdown("""
    <div class="agent-box">
    <b>Resumo executivo do período</b><br><br>
    A operação está abaixo da meta em produção, OEE e margem de contribuição. A Linha 3 concentra
    a maior parcela do gap operacional. O impacto agregado das principais perdas é de aproximadamente
    R$ 548 mil no EBITDA, com maior potencial de recuperação em disponibilidade, refugo e horas extras.
    </div>
    """, unsafe_allow_html=True)

    q=st.chat_input("Pergunte: Qual alavanca tem maior impacto no EBITDA?")
    if q:
        st.chat_message("user").write(q)
        ans = "A alavanca com maior potencial atual é a recuperação de disponibilidade da Linha 3, estimada em R$ 312 mil. Em seguida vem a redução de refugo, com R$ 214 mil. Recomendo priorizar as duas porque combinam alto impacto financeiro e causas operacionais identificadas."
        st.chat_message("assistant").write(ans)

    st.subheader("Perguntas sugeridas")
    st.markdown("""
    - Por que a fábrica ficou abaixo da meta?
    - Qual linha destruiu mais margem?
    - Qual o impacto de elevar o OEE para 80%?
    - Quanto recuperamos reduzindo o refugo para 2,5%?
    - Onde o custo fixo está acima do orçamento?
    - Quais 3 ações devem ser prioridade esta semana?
    """)
