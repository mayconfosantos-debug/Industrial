# Industrial Performance Agent — MVP

Este MVP transforma arquivos Excel industriais em um cockpit executivo com análise automática.

## O que já faz
- Upload de um ou mais arquivos Excel.
- Consolidação automática das abas.
- Filtros por período, fábrica e linha.
- KPIs: produção, atingimento, OEE, disponibilidade, performance, qualidade, refugo, margem, custo por unidade, horas extras e produtividade.
- Diagnóstico automático dos principais desvios.
- Estimativas de impacto financeiro.
- Perguntas executivas ao Agente de Performance.

## Estrutura esperada do Excel
Use `industrial_performance_exemplo.xlsx` como modelo.

Abas:
- Producao
- Qualidade
- Manutencao
- Pessoas
- Custos
- Metas

O aplicativo já reconhece alguns nomes alternativos de abas e colunas.

## Como rodar localmente

1. Instale Python 3.11+.
2. Abra o terminal nesta pasta.
3. Crie um ambiente virtual (opcional, recomendado).
4. Instale as dependências:

```bash
pip install -r requirements.txt
```

5. Rode:

```bash
streamlit run app.py
```

6. O navegador abrirá o aplicativo.

## Como testar
Faça upload do arquivo:

`industrial_performance_exemplo.xlsx`

## Próximas evoluções recomendadas
1. Mapeador DE/PARA visual de colunas.
2. Banco PostgreSQL para histórico por cliente.
3. Login e segregação por empresa.
4. Integração ERP/MES.
5. Motor de alertas e Morning Industrial Brief.
6. Agente LLM com contexto controlado e trilha de evidências.
7. Árvore financeira EBITDA / margem / perdas.
