# Industrial Performance — v0.6.2 Front-end Premium

## Escopo desta versão
Esta versão preserva o escopo oficial do Simulador:
10 grupos e 26 alavancas.

Grupos:
- Produção
- Qualidade
- Processo
- Pessoas
- Materiais
- Energia
- Logística
- Financeiro
- Estrutura
- Capital

## Front-end
- Grid mais rígido no Cockpit.
- Painéis de mesma linha com alturas equivalentes.
- Sidebar mais compacta.
- Cards e containers com visual mais clean.
- Tabelas com larguras controladas.
- Diagnóstico mantém matriz Esforço x Resultado, Pareto, impacto financeiro, ações e PDF.
- Simulador redesenhado com seleção de grupo, menos poluição visual e painel de impacto fixo ao lado.

## Simulador
- 26 alavancas acordadas.
- OEE direto ou Drivers de OEE.
- Setup, paradas e MTTR alimentam disponibilidade sem dupla contagem.
- Produtividade permanece no escopo, mas o consolidado deve ser linearizado pelo mix.
- Capacidade habilita valor; volume vendido monetiza capacidade.
- OTIF trabalha como receita protegida, não receita automática.
- Custo fixo e contratos/serviços são separados para evitar dupla contagem.
- Capital de giro fica separado do EBITDA.
- Mapa de Valor diferencia "Valor habilitado", EBITDA e Caixa.
- Cenário pode ser transformado em Plano de Captura.

## Planilha padrão
Use:
Industrial_Performance_Input_Padrao_v062.xlsx

Novas abas:
- Alavancas_Simulador
- Premissas_Simulador

A planilha registra o escopo oficial, dependências, confiança e premissas do motor.

## GitHub
Substitua na raiz:
- app.py
- requirements.txt
- README.md

Mantenha:
- logo_h2m_white.jpeg
- logo_h2m_blue.jpeg

Opcionalmente suba também:
- Industrial_Performance_Input_Padrao_v062.xlsx

Main file path:
app.py
