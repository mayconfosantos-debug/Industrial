
# Industrial Performance SaaS — H2M | v0.1

Estrutura navegável do SaaS de performance industrial.

## Telas incluídas
1. Cockpit Executivo
2. Performance Operacional
3. Diagnóstico e Causas
4. Finanças / DRE
5. Alavancas de Valor
6. Plano de Ação
7. Agente de Performance
8. Relatórios
9. Configurações

## Identidade
- Logo original H2M preservado em arquivo de imagem, sem distorção.
- Paleta inspirada na ZeroBaseTrack: navy, azul, cyan e branco.
- Regra dos KPIs:
  - Vermelho: desvio < -10%
  - Laranja: -10% até < 0%
  - Verde: >= 0%

## Como rodar
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Como publicar no Streamlit Community Cloud
Suba toda a pasta para o GitHub mantendo a estrutura e aponte o "Main file path" para:

`app.py`

## Próximas evoluções
- Substituir dados-demo pelo Excel real.
- DE/PARA visual de colunas.
- Persistência PostgreSQL.
- Autenticação e multiempresa.
- Motor real de KPIs.
- Árvore causal automatizada.
- Motor de impacto financeiro / DRE.
- Agente LLM com evidências e simulações.
