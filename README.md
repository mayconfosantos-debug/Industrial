# Industrial Performance — v0.6.2.1 Hotfix

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


## Hotfix v0.6.2.1
- Corrigido NameError no carregamento do app.
- Causa: regras CSS da v0.6.1/v0.6.2 estavam com chaves simples dentro de um f-string do Python.
- Todas as chaves CSS foram escapadas corretamente.
- Escopo funcional permanece igual: 10 grupos e 26 alavancas.
- Nenhuma regra de negócio do simulador foi removida.


## Hotfix v0.6.2.2
- Menu lateral totalmente alinhado à esquerda.
- Texto e conteúdo interno dos botões agora usam justify-content:flex-start e text-align:left.
- Mantido o destaque azul/cyan do item ativo.


## Hotfix v0.6.2.3
- Corrigido NameError da linha `width:100%` no CSS do menu lateral.
- Todas as chaves do CSS do hotfix da sidebar foram escapadas corretamente para uso dentro do f-string.
- Auditoria do bloco de tema confirmou que as únicas expressões f-string restantes são as variáveis de tema esperadas.
- Mantido o menu alinhado à esquerda.


## v0.6.2.4 — Logo H2M
- Logo H2M trocado por versão branca com fundo transparente.
- Removido o bloco branco visual do logo na sidebar.
- Logo agora é clicável.
- Clique abre https://h2mconsulting.com.br em nova aba.
- Menu lateral permanece alinhado à esquerda.
