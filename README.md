# Industrial Performance — v0.6.4 Analytics Engine

## Objetivo
A v0.6.3 cria a camada de entrada de dados do Industrial Performance:

**RAW → Mapping / DE-PARA → Standard Industrial Model → Data Quality → Semantic / Gold → Performance Engine**

O cliente não precisa mais renomear manualmente abas e colunas para aderir ao modelo H2M.

## O que foi implementado

### Central de Dados
Fluxo guiado em 5 etapas:
1. Carregar
2. Identificar
3. Mapear
4. Validar
5. Aplicar

### Reconhecimento automático
- Identificação de abas por nome e estrutura das colunas.
- Sugestão de entidade: Produção, Qualidade, Manutenção, Pessoas, Custos, Metas, Padrões etc.
- Confiança do reconhecimento para orientar o que precisa ser confirmado.

### DE/PARA visual
- Coluna do cliente → campo canônico H2M.
- Campos obrigatórios, recomendados e opcionais.
- Detecção de tipo de dado.
- Confiança por mapeamento.
- Bloqueio de duplicidade de destino na mesma aba.

### Unidades
- Detecção e conversão de minutos ↔ horas.
- kg ↔ toneladas.
- R$ mil → R$.
- % ↔ decimal quando aplicável.
- Unidade original e unidade padrão ficam registradas no lineage.

### Dimensões
Padronização opcional de valores como:
- fábrica;
- linha;
- máquina;
- produto;
- turno;
- causa;
- tipo de parada.

Exemplo: `L01`, `Linha-01` e `Célula A` podem convergir para `Linha 1`.

### Industrial Performance Data Model
Os dados são transformados para entidades canônicas usadas pelo produto:
- producao
- qualidade
- manutencao
- pessoas
- custos
- metas
- padroes_produto
- parametros_diagnostico
- responsaveis
- alavancas_simulador
- premissas_simulador

### Data Quality
Score de 0 a 100 com verificações de:
- entidades e campos obrigatórios;
- completude;
- duplicidade;
- tipos de dados;
- metas;
- padrões de produto;
- mix multiproduto;
- confiança do mapping.

Falhas estruturais críticas bloqueiam a aplicação ao Performance Engine. Alertas não críticos permanecem explícitos e reduzem o score.

### Mapping reutilizável
- Mapping salvo por empresa + fonte no ambiente piloto.
- Exportação do DE/PARA em JSON.
- Importação de perfil JSON para reaplicar o mapping em outro upload.

### RAW + Standard + Lineage
Quando a ingestão é aplicada, a camada piloto tenta registrar:
- arquivo RAW original;
- tabelas Standard em Parquet;
- mapping JSON;
- metadata de ingestão;
- lineage origem → aba → coluna → campo padrão → transformação.

O armazenamento analítico usa **DuckDB + Parquet**.

## Novas páginas
Na seção Administração:
- Central de Dados
- Mapeamentos
- Qualidade dos Dados
- Configurações

## Importante sobre Streamlit Cloud
Na v0.6.3, a persistência local serve para validar a arquitetura e o produto. O disco local do Streamlit Cloud não deve ser considerado armazenamento empresarial definitivo.

Na v0.8, a persistência pode migrar para:
- Object Storage (S3 / Azure Blob / Cloudflare R2)
- PostgreSQL
- DuckDB / camada analítica

O Industrial Performance Data Model e o Performance Engine permanecem os mesmos.

## Compatibilidade funcional preservada
A v0.6.3 mantém:
- Cockpit Executivo;
- Diagnóstico e Causas;
- saúde operacional/financeira ponderada;
- produtividade linearizada por HH padrão em ambiente multiproduto;
- PDF executivo;
- Plano de Ação com responsável e e-mail;
- Simulador oficial com 10 grupos e 26 alavancas;
- regras de não dupla contagem entre causa e efeito;
- logo H2M transparente e clicável.

Também foi corrigido um problema no processamento de dados reais em Manutenção: a coluna canônica `causa` agora é corretamente apresentada ao motor como `Causa` no Pareto e no diagnóstico.

## Arquivos para o GitHub
Suba/substitua na raiz do repositório:
- `app.py`
- `industrial_data_layer.py`
- `requirements.txt`
- `README.md`
- `logo_h2m_transparent.png`
- `logo_h2m_white.jpeg`
- `logo_h2m_blue.jpeg`
- `Industrial_Performance_Input_Padrao_v063.xlsx`

Arquivo principal do Streamlit:
`app.py`


## v0.6.3.1 — Simulador Atual → Meta + DRE Gerencial

### Simulador
- As 26 alavancas agora são informadas como valor **Atual → Meta**.
- O usuário não informa mais “+X%” ou “-X% de melhoria” como lógica principal.
- Preço médio é R$/un e Volume vendido é unidades.
- Receita simulada = **volume simulado × preço simulado**.
- O efeito de preço é calculado sobre o volume do cenário.
- OTIF é mostrado como **receita protegida / receita adicional em risco** e não entra automaticamente na DRE.
- Horas extras usam custo/hora real da MOD + premissa configurável de adicional, removendo o R$ 30/h hardcoded.
- Frete/unidade é valor R$/un e está classificado em GGF.
- Custo fixo e contratos/serviços passam a usar valores absolutos em R$.
- Estoque, DPO e DSO usam dias atuais → dias meta.

### DRE Gerencial
Nova estrutura:
Receita Bruta
(-) Impostos e deduções
= Receita Líquida
(-) Insumos / MP
(-) MOD
(-) GGF — Frete
(-) GGF — Energia
(-) GGF — Manutenção
(-) GGF — Contratos e Serviços
(-) GGF — Outros
= Margem Industrial
(-) Custos Fixos Industriais
= Resultado Industrial
(-) Despesas Administrativas
(-) Despesas Comerciais
(-) Despesas Logísticas
(-) Outros OPEX
= EBITDA

O arquivo padrão v0.6.3.1 adiciona as abas **DRE_Gerencial** e **Plano_Contas_DRE**.


## v0.6.4 — Analytics Engine

### Filtros reais
Os filtros do cabeçalho deixaram de ser ilustrativos. Em bases importadas, Grupo, Planta, Período, Linha e Produto recalculam o modelo quando a dimensão existe na entidade.

O motor registra a cobertura de filtros por entidade. Quando uma dimensão não existe, o sistema não finge precisão:
- a limitação aparece na cobertura;
- a causalidade é rebaixada quando a fonte não suporta o recorte;
- a DRE gerencial recebe tratamento específico para drill-down.

### DRE gerencial em Linha / Produto
Se a DRE_Gerencial estiver consolidada e o usuário filtrar Linha ou Produto, o Analytics Engine faz uma **alocação gerencial reconciliada** usando a participação do recorte na base detalhada de Custos/Produção.

Custos fixos e despesas são rateados pelo peso do recorte e a interface avisa que se trata de uma visão analítica, não de uma DRE contábil legal.

### Drill-down
A tela Performance Operacional agora possui:
- KPI → Linha → Máquina → Causa para OEE, Disponibilidade e Produção;
- Linha → Produto para Refugo quando a base de qualidade não possui máquina/causa;
- detalhamento de horas extras por Linha/Turno;
- detalhamento de custos por Linha/Produto;
- impacto financeiro estimado das perdas de manutenção.

### Performance Engine
Novo módulo `analytics_engine.py` com cadeia determinística:

`KPI → Desvio → Local → Causa/Evidência → Impacto financeiro → Alavanca → Ação`

O motor só afirma uma causa quando a granularidade da fonte suporta a afirmação. Caso contrário, mostra a lacuna de dados ou hipótese explicitamente.

### Modelo padrão v0.6.4
O Excel de exemplo foi atualizado para permitir testar:
- Grupo;
- Planta;
- Período;
- Linha;
- Produto;
- DRE Gerencial alinhada com a operação.

`Plano_Contas_DRE` é tratado como entidade de referência própria e não contamina mais a DRE Gerencial no reconhecimento automático.
