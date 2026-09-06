from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import hashlib
import json
import os
import re
import unicodedata
import warnings

import numpy as np
import pandas as pd

try:
    import duckdb  # type: ignore
except Exception:  # pragma: no cover - fallback for static/offline validation
    duckdb = None


DATA_LAYER_VERSION = "0.6.5"
IGNORE_ENTITY = "Ignorar"
AUTO_UNIT = "Auto"
NO_CONVERSION = "Sem conversão"


def norm(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))
    return "_".join(filter(None, re.split(r"[^a-z0-9]+", text)))


def safe_slug(value: Any) -> str:
    return norm(value) or "nao_informado"


ENTITY_LABELS: Dict[str, str] = {
    "producao": "Produção",
    "qualidade": "Qualidade",
    "manutencao": "Manutenção",
    "pessoas": "Pessoas",
    "custos": "Custos / Financeiro",
    "dre_gerencial": "DRE Gerencial",
    "plano_contas_dre": "Plano de Contas DRE",
    "metas": "Metas",
    "padroes_produto": "Padrões de Produto",
    "parametros_diagnostico": "Parâmetros de Diagnóstico",
    "responsaveis": "Responsáveis",
    "alavancas_simulador": "Alavancas do Simulador",
    "premissas_simulador": "Premissas do Simulador",
    "cadastro_dimensoes": "Cadastro de Dimensões",
}

LABEL_TO_ENTITY = {v: k for k, v in ENTITY_LABELS.items()}

SHEET_ALIASES: Dict[str, List[str]] = {
    "producao": ["producao", "produção", "production", "prod", "ordens_producao", "apontamento_producao"],
    "qualidade": ["qualidade", "quality", "qc", "scrap", "refugo", "inspecao"],
    "manutencao": ["manutencao", "manutenção", "maintenance", "downtime", "paradas", "falhas"],
    "pessoas": ["pessoas", "people", "mao_de_obra", "mão de obra", "labor", "horas", "headcount"],
    "custos": ["custos", "costs", "financeiro", "cost"],
    "dre_gerencial": ["dre_gerencial", "dre gerencial", "management_pnl", "pnl_gerencial", "resultado_gerencial", "dre", "pl", "resultado"],
    "plano_contas_dre": ["plano_contas_dre", "plano contas dre", "plano_contas", "chart_of_accounts", "management_chart_of_accounts"],
    "metas": ["metas", "targets", "goals", "objetivos"],
    "padroes_produto": ["padroes_produto", "padrões_produto", "padroes", "standards", "product_standards", "roteiro"],
    "parametros_diagnostico": ["parametros_diagnostico", "diagnostico_parametros", "diagnostic_parameters"],
    "responsaveis": ["responsaveis", "responsáveis", "owners", "responsibles"],
    "alavancas_simulador": ["alavancas_simulador", "simulator_levers", "alavancas"],
    "premissas_simulador": ["premissas_simulador", "simulator_assumptions", "premissas"],
    "cadastro_dimensoes": ["cadastro_dimensoes", "cadastro dimensoes", "cadastro_linhas", "cadastro maquinas", "master_data", "master data", "hierarquia_industrial", "dimensoes", "dimensões"],
}

# Canonical schema. priority: required | recommended | optional
# unit is the internal expected unit for normalization.
FIELD_SPECS: Dict[str, Dict[str, Dict[str, Any]]] = {
    "producao": {
        "grupo": {"label": "Grupo", "priority": "optional", "dtype": "text", "aliases": ["grupo", "grupo_empresa", "grupo_industrial", "business_group"]},
        "data": {"label": "Data", "priority": "required", "dtype": "date", "aliases": ["data", "date", "dt", "dt_producao", "data_ref", "data_producao"]},
        "fabrica": {"label": "Fábrica / Planta", "priority": "recommended", "dtype": "text", "aliases": ["fabrica", "planta", "site", "factory", "unidade_fabril", "unidade_industrial", "plant"]},
        "linha": {"label": "Linha", "priority": "required", "dtype": "text", "aliases": ["linha", "line", "workcenter", "work_center", "centro_trabalho", "celula", "célula", "recurso"]},
        "produto": {"label": "Produto / SKU", "priority": "required", "dtype": "text", "aliases": ["produto", "sku", "product", "material", "item", "codigo_produto", "cod_produto"]},
        "planejado": {"label": "Produção Planejada", "priority": "required", "dtype": "number", "unit": "unidades", "aliases": ["planejado", "plano", "meta_producao", "planned", "qtd_prevista", "quantidade_planejada", "target_qty", "planned_qty"]},
        "realizado": {"label": "Produção Realizada", "priority": "required", "dtype": "number", "unit": "unidades", "aliases": ["realizado", "producao_real", "qtd_produzida", "quantidade_produzida", "volume", "actual", "production_qty", "actual_qty"]},
        "horas_disponiveis": {"label": "Horas Disponíveis", "priority": "required", "dtype": "number", "unit": "horas", "aliases": ["horas_disponiveis", "horas_planejadas", "available_hours", "tempo_disponivel", "tempo_disponivel_h", "available_time"]},
        "horas_paradas": {"label": "Horas Paradas", "priority": "required", "dtype": "number", "unit": "horas", "aliases": ["horas_paradas", "paradas_horas", "downtime_hours", "downtime", "tempo_parada", "tempo_parado"]},
        "velocidade_real": {"label": "Velocidade Real", "priority": "required", "dtype": "number", "aliases": ["velocidade_real", "performance_real", "actual_speed", "vel_real", "rate_actual"]},
        "velocidade_nominal": {"label": "Velocidade Nominal", "priority": "required", "dtype": "number", "aliases": ["velocidade_nominal", "velocidade_padrao", "nominal_speed", "standard_speed", "vel_nominal"]},
    },
    "qualidade": {
        "grupo": {"label": "Grupo", "priority": "optional", "dtype": "text", "aliases": ["grupo", "grupo_empresa", "grupo_industrial", "business_group"]},
        "fabrica": {"label": "Fábrica / Planta", "priority": "optional", "dtype": "text", "aliases": ["fabrica", "planta", "site", "factory", "unidade_fabril", "unidade_industrial", "plant"]},
        "data": {"label": "Data", "priority": "required", "dtype": "date", "aliases": ["data", "date", "dt", "data_qualidade"]},
        "linha": {"label": "Linha", "priority": "required", "dtype": "text", "aliases": ["linha", "line", "workcenter", "centro_trabalho", "celula"]},
        "produto": {"label": "Produto / SKU", "priority": "required", "dtype": "text", "aliases": ["produto", "sku", "product", "material", "item"]},
        "produzido": {"label": "Quantidade Produzida", "priority": "required", "dtype": "number", "unit": "unidades", "aliases": ["produzido", "producao", "produced", "qtd_produzida", "total_produzido", "production_qty"]},
        "aprovado": {"label": "Quantidade Boa / Aprovada", "priority": "required", "dtype": "number", "unit": "unidades", "aliases": ["aprovado", "bons", "good_units", "qtd_boa", "good_qty", "approved_qty"]},
        "refugo": {"label": "Refugo", "priority": "required", "dtype": "number", "unit": "unidades", "aliases": ["refugo", "scrap", "scrap_qty", "qtd_refugo", "sucata"]},
        "retrabalho": {"label": "Retrabalho", "priority": "recommended", "dtype": "number", "unit": "unidades", "aliases": ["retrabalho", "rework", "rework_qty", "qtd_retrabalho"]},
    },
    "manutencao": {
        "grupo": {"label": "Grupo", "priority": "optional", "dtype": "text", "aliases": ["grupo", "grupo_empresa", "grupo_industrial", "business_group"]},
        "fabrica": {"label": "Fábrica / Planta", "priority": "optional", "dtype": "text", "aliases": ["fabrica", "planta", "site", "factory", "unidade_fabril", "unidade_industrial", "plant"]},
        "data": {"label": "Data", "priority": "required", "dtype": "date", "aliases": ["data", "date", "dt", "data_parada"]},
        "linha": {"label": "Linha", "priority": "required", "dtype": "text", "aliases": ["linha", "line", "workcenter", "centro_trabalho"]},
        "maquina": {"label": "Máquina / Equipamento", "priority": "required", "dtype": "text", "aliases": ["maquina", "equipamento", "machine", "equipment", "asset", "recurso"]},
        "tipo_parada": {"label": "Tipo de Parada", "priority": "recommended", "dtype": "text", "aliases": ["tipo_parada", "tipo", "downtime_type", "categoria_parada", "classificacao"]},
        "duracao_horas": {"label": "Duração da Parada", "priority": "required", "dtype": "number", "unit": "horas", "aliases": ["duracao_horas", "horas", "duracao", "duration_hours", "downtime", "tempo_parada", "duracao_min", "downtime_min"]},
        "causa": {"label": "Causa", "priority": "required", "dtype": "text", "aliases": ["causa", "motivo", "cause", "failure_cause", "raiz", "reason"]},
    },
    "pessoas": {
        "grupo": {"label": "Grupo", "priority": "optional", "dtype": "text", "aliases": ["grupo", "grupo_empresa", "grupo_industrial", "business_group"]},
        "fabrica": {"label": "Fábrica / Planta", "priority": "optional", "dtype": "text", "aliases": ["fabrica", "planta", "site", "factory", "unidade_fabril", "unidade_industrial", "plant"]},
        "data": {"label": "Data", "priority": "required", "dtype": "date", "aliases": ["data", "date", "dt"]},
        "linha": {"label": "Linha", "priority": "required", "dtype": "text", "aliases": ["linha", "line", "workcenter", "centro_trabalho"]},
        "turno": {"label": "Turno", "priority": "recommended", "dtype": "text", "aliases": ["turno", "shift", "turma"]},
        "operadores": {"label": "Operadores / Headcount", "priority": "recommended", "dtype": "number", "unit": "pessoas", "aliases": ["operadores", "headcount", "pessoas", "fte", "hc"]},
        "horas_normais": {"label": "Horas Normais", "priority": "required", "dtype": "number", "unit": "horas", "aliases": ["horas_normais", "regular_hours", "horas_regulares", "hh_normal"]},
        "horas_extras": {"label": "Horas Extras", "priority": "required", "dtype": "number", "unit": "horas", "aliases": ["horas_extras", "overtime", "overtime_hours", "he", "hh_extra"]},
    },
    "custos": {
        "grupo": {"label": "Grupo", "priority": "optional", "dtype": "text", "aliases": ["grupo", "grupo_empresa", "grupo_industrial", "business_group"]},
        "fabrica": {"label": "Fábrica / Planta", "priority": "optional", "dtype": "text", "aliases": ["fabrica", "planta", "site", "factory", "unidade_fabril", "unidade_industrial", "plant"]},
        "data": {"label": "Data", "priority": "required", "dtype": "date", "aliases": ["data", "date", "dt", "competencia"]},
        "linha": {"label": "Linha", "priority": "required", "dtype": "text", "aliases": ["linha", "line", "workcenter", "centro_custo", "cost_center"]},
        "produto": {"label": "Produto / SKU", "priority": "recommended", "dtype": "text", "aliases": ["produto", "sku", "product", "material", "item"]},
        "custo_mp": {"label": "Custo MP", "priority": "required", "dtype": "number", "unit": "R$", "aliases": ["custo_mp", "materia_prima", "raw_material_cost", "mp", "material_cost"]},
        "custo_mod": {"label": "Custo MOD", "priority": "required", "dtype": "number", "unit": "R$", "aliases": ["custo_mod", "mao_de_obra_direta", "direct_labor_cost", "mod", "labor_cost"]},
        "custo_energia": {"label": "Custo Energia", "priority": "required", "dtype": "number", "unit": "R$", "aliases": ["custo_energia", "energia", "energy_cost", "utilities_energy"]},
        "custo_manutencao": {"label": "Custo Manutenção", "priority": "required", "dtype": "number", "unit": "R$", "aliases": ["custo_manutencao", "manutencao", "maintenance_cost", "maintenance"]},
        "custo_fixo": {"label": "Custo Fixo", "priority": "recommended", "dtype": "number", "unit": "R$", "aliases": ["custo_fixo", "fixed_cost", "custos_fixos", "factory_fixed_cost"]},
        "receita": {"label": "Receita", "priority": "required", "dtype": "number", "unit": "R$", "aliases": ["receita", "faturamento", "revenue", "sales", "net_revenue"]},
    },
    "dre_gerencial": {
        "grupo": {"label": "Grupo", "priority": "optional", "dtype": "text", "aliases": ["grupo", "grupo_empresa", "grupo_industrial", "business_group"]},
        "linha": {"label": "Linha", "priority": "optional", "dtype": "text", "aliases": ["linha", "line", "workcenter", "centro_trabalho"]},
        "produto": {"label": "Produto / SKU", "priority": "optional", "dtype": "text", "aliases": ["produto", "sku", "product", "material", "item"]},
        "competencia": {"label": "Competência", "priority": "required", "dtype": "date", "aliases": ["competencia", "data", "date", "periodo", "period"]},
        "planta": {"label": "Planta / Unidade", "priority": "recommended", "dtype": "text", "aliases": ["planta", "fabrica", "unidade", "site", "factory"]},
        "receita_bruta": {"label": "Receita Bruta", "priority": "recommended", "dtype": "number", "unit": "R$", "aliases": ["receita_bruta", "gross_revenue", "faturamento_bruto"]},
        "impostos_deducoes": {"label": "Impostos e Deduções", "priority": "recommended", "dtype": "number", "unit": "R$", "aliases": ["impostos_deducoes", "impostos", "deducoes", "taxes_deductions"]},
        "receita_liquida": {"label": "Receita Líquida", "priority": "required", "dtype": "number", "unit": "R$", "aliases": ["receita_liquida", "receita", "net_revenue", "revenue"]},
        "insumos_mp": {"label": "Insumos / Matéria-prima", "priority": "required", "dtype": "number", "unit": "R$", "aliases": ["insumos_mp", "custo_mp", "materia_prima", "raw_material"]},
        "mod": {"label": "MOD", "priority": "required", "dtype": "number", "unit": "R$", "aliases": ["mod", "custo_mod", "mao_de_obra_direta", "direct_labor"]},
        "ggf_frete": {"label": "GGF — Frete", "priority": "recommended", "dtype": "number", "unit": "R$", "aliases": ["ggf_frete", "frete", "freight", "freight_cost"]},
        "ggf_energia": {"label": "GGF — Energia", "priority": "recommended", "dtype": "number", "unit": "R$", "aliases": ["ggf_energia", "custo_energia", "energia", "energy"]},
        "ggf_manutencao": {"label": "GGF — Manutenção", "priority": "recommended", "dtype": "number", "unit": "R$", "aliases": ["ggf_manutencao", "custo_manutencao", "manutencao", "maintenance"]},
        "ggf_contratos_servicos": {"label": "GGF — Contratos e Serviços", "priority": "recommended", "dtype": "number", "unit": "R$", "aliases": ["ggf_contratos_servicos", "contratos_servicos", "contracts_services"]},
        "ggf_outros": {"label": "GGF — Outros", "priority": "recommended", "dtype": "number", "unit": "R$", "aliases": ["ggf_outros", "outros_ggf", "other_factory_overhead"]},
        "custos_fixos_industriais": {"label": "Custos Fixos Industriais", "priority": "recommended", "dtype": "number", "unit": "R$", "aliases": ["custos_fixos_industriais", "custo_fixo_industrial", "fixed_industrial_cost"]},
        "desp_administrativas": {"label": "Despesas Administrativas", "priority": "recommended", "dtype": "number", "unit": "R$", "aliases": ["desp_administrativas", "despesas_administrativas", "admin_expenses"]},
        "desp_comerciais": {"label": "Despesas Comerciais", "priority": "recommended", "dtype": "number", "unit": "R$", "aliases": ["desp_comerciais", "despesas_comerciais", "selling_expenses"]},
        "desp_logisticas": {"label": "Despesas Logísticas (sem frete)", "priority": "recommended", "dtype": "number", "unit": "R$", "aliases": ["desp_logisticas", "despesas_logisticas", "logistics_expenses"]},
        "outros_opex": {"label": "Outros OPEX", "priority": "recommended", "dtype": "number", "unit": "R$", "aliases": ["outros_opex", "other_opex"]},
        "volume_vendido": {"label": "Volume Vendido", "priority": "recommended", "dtype": "number", "unit": "unidades", "aliases": ["volume_vendido", "sold_volume", "qtd_vendida"]},
        "consumo_mp_kg": {"label": "Consumo MP", "priority": "optional", "dtype": "number", "unit": "kg", "aliases": ["consumo_mp_kg", "material_consumption_kg"]},
        "preco_medio_mp_kg": {"label": "Preço Médio MP", "priority": "optional", "dtype": "number", "unit": "R$", "aliases": ["preco_medio_mp_kg", "preco_mp_kg", "material_price_kg"]},
        "consumo_energia_kwh": {"label": "Consumo de Energia", "priority": "optional", "dtype": "number", "unit": "kWh", "aliases": ["consumo_energia_kwh", "energy_consumption_kwh"]},
        "estoque_dias": {"label": "Estoque (dias)", "priority": "optional", "dtype": "number", "unit": "dias", "aliases": ["estoque_dias", "inventory_days"]},
        "prazo_fornecedor_dias": {"label": "Prazo Fornecedor (dias)", "priority": "optional", "dtype": "number", "unit": "dias", "aliases": ["prazo_fornecedor_dias", "dpo", "supplier_days"]},
        "prazo_cliente_dias": {"label": "Prazo Cliente (dias)", "priority": "optional", "dtype": "number", "unit": "dias", "aliases": ["prazo_cliente_dias", "dso", "customer_days"]},
    },
    "plano_contas_dre": {
        "campo_canonico": {"label": "Campo Canônico", "priority": "required", "dtype": "text", "aliases": ["campo_canonico", "canonical_field"]},
        "grupo_dre": {"label": "Grupo DRE", "priority": "required", "dtype": "text", "aliases": ["grupo_dre", "dre_group"]},
        "subgrupo": {"label": "Subgrupo", "priority": "recommended", "dtype": "text", "aliases": ["subgrupo", "subgroup"]},
        "natureza": {"label": "Natureza", "priority": "recommended", "dtype": "text", "aliases": ["natureza", "nature"]},
        "comportamento_default": {"label": "Comportamento Default", "priority": "recommended", "dtype": "text", "aliases": ["comportamento_default", "default_behavior"]},
        "inclui_ebitda": {"label": "Inclui EBITDA", "priority": "recommended", "dtype": "text", "aliases": ["inclui_ebitda", "included_in_ebitda"]},
        "observacao": {"label": "Observação", "priority": "optional", "dtype": "text", "aliases": ["observacao", "observação", "notes"]},
    },
    "cadastro_dimensoes": {
        "grupo": {"label": "Grupo", "priority": "optional", "dtype": "text", "aliases": ["grupo", "grupo_empresa", "grupo_industrial", "business_group"]},
        "fabrica": {"label": "Fábrica / Planta", "priority": "recommended", "dtype": "text", "aliases": ["fabrica", "planta", "site", "factory", "unidade_fabril", "unidade_industrial", "plant"]},
        "linha": {"label": "Linha", "priority": "recommended", "dtype": "text", "aliases": ["linha", "line", "workcenter", "centro_trabalho", "celula", "célula"]},
        "maquina": {"label": "Máquina / Equipamento", "priority": "optional", "dtype": "text", "aliases": ["maquina", "equipamento", "machine", "equipment", "asset"]},
        "produto": {"label": "Produto / SKU", "priority": "optional", "dtype": "text", "aliases": ["produto", "sku", "product", "material", "item"]},
        "familia": {"label": "Família de Produto", "priority": "optional", "dtype": "text", "aliases": ["familia", "família", "product_family", "family"]},
        "centro_custo": {"label": "Centro de Custo", "priority": "optional", "dtype": "text", "aliases": ["centro_custo", "cost_center", "ccusto", "cc"]},
    },
    "metas": {
        "indicador": {"label": "Indicador", "priority": "required", "dtype": "text", "aliases": ["indicador", "kpi", "metric"]},
        "meta": {"label": "Meta", "priority": "required", "dtype": "number", "aliases": ["meta", "target", "goal"]},
        "direcao": {"label": "Direção", "priority": "recommended", "dtype": "text", "aliases": ["direcao", "direção", "direction"]},
        "unidade": {"label": "Unidade", "priority": "recommended", "dtype": "text", "aliases": ["unidade", "unit"]},
        "obrigatoria": {"label": "Obrigatória", "priority": "optional", "dtype": "text", "aliases": ["obrigatoria", "obrigatória", "mandatory"]},
        "referencia_financeira": {"label": "Referência Financeira", "priority": "optional", "dtype": "text", "aliases": ["referencia_financeira", "referência_financeira", "financial_reference"]},
    },
    "padroes_produto": {
        "produto": {"label": "Produto / SKU", "priority": "required", "dtype": "text", "aliases": ["produto", "sku", "product", "material"]},
        "familia": {"label": "Família", "priority": "recommended", "dtype": "text", "aliases": ["familia", "família", "family"]},
        "linha_padrao": {"label": "Linha Padrão", "priority": "recommended", "dtype": "text", "aliases": ["linha_padrao", "linha_padrão", "standard_line"]},
        "tempo_ciclo_padrao_min_un": {"label": "Ciclo padrão (min/un)", "priority": "recommended", "dtype": "number", "unit": "minutos", "aliases": ["tempo_ciclo_padrao_min_un", "tempo_ciclo_padrão_min_un", "standard_cycle_min_unit", "tempo_ciclo", "cycle_time"]},
        "operadores_padrao": {"label": "Operadores padrão", "priority": "recommended", "dtype": "number", "unit": "pessoas", "aliases": ["operadores_padrao", "operadores_padrão", "standard_operators"]},
        "hh_padrao_un": {"label": "HH padrão / un", "priority": "recommended", "dtype": "number", "unit": "horas", "aliases": ["hh_padrao_un", "hh_padrão_un", "standard_labor_hours_unit"]},
        "tempo_setup_padrao_min_lote": {"label": "Setup padrão (min/lote)", "priority": "optional", "dtype": "number", "unit": "minutos", "aliases": ["tempo_setup_padrao_min_lote", "tempo_setup_padrão_min_lote", "standard_setup_min_batch", "setup_padrao"]},
        "lote_padrao_un": {"label": "Lote padrão", "priority": "optional", "dtype": "number", "unit": "unidades", "aliases": ["lote_padrao_un", "lote_padrão_un", "standard_batch"]},
        "mp_padrao_kg_un": {"label": "MP padrão (kg/un)", "priority": "optional", "dtype": "number", "unit": "kg", "aliases": ["mp_padrao_kg_un", "mp_padrão_kg_un", "standard_material_kg_unit"]},
        "energia_padrao_kwh_un": {"label": "Energia padrão (kWh/un)", "priority": "optional", "dtype": "number", "unit": "kWh", "aliases": ["energia_padrao_kwh_un", "energia_padrão_kwh_un", "standard_energy_kwh_unit"]},
        "custo_hh_mod": {"label": "Custo HH MOD", "priority": "optional", "dtype": "number", "unit": "R$", "aliases": ["custo_hh_mod", "labor_hour_cost"]},
        "preco_liquido_padrao": {"label": "Preço líquido padrão", "priority": "optional", "dtype": "number", "unit": "R$", "aliases": ["preco_liquido_padrao", "preço_liquido_padrão", "standard_net_price"]},
        "custo_variavel_padrao": {"label": "Custo variável padrão", "priority": "optional", "dtype": "number", "unit": "R$", "aliases": ["custo_variavel_padrao", "custo_variável_padrão", "standard_variable_cost"]},
        "margem_contrib_padrao": {"label": "Margem contribuição padrão", "priority": "optional", "dtype": "number", "unit": "R$", "aliases": ["margem_contrib_padrao", "margem_contrib_padrão", "standard_contribution_margin"]},
    },
    "parametros_diagnostico": {
        "alavanca": {"label": "Alavanca", "priority": "required", "dtype": "text", "aliases": ["alavanca", "lever"]},
        "esforco_1a5": {"label": "Esforço 1–5", "priority": "recommended", "dtype": "number", "aliases": ["esforco_1a5", "esforço_1a5", "effort"]},
        "horizonte_dias": {"label": "Horizonte (dias)", "priority": "recommended", "dtype": "number", "aliases": ["horizonte_dias", "horizon_days"]},
        "responsavel_tipico": {"label": "Responsável típico", "priority": "recommended", "dtype": "text", "aliases": ["responsavel_tipico", "responsável_típico", "typical_owner"]},
        "tipo_impacto": {"label": "Tipo de impacto", "priority": "optional", "dtype": "text", "aliases": ["tipo_impacto", "impact_type"]},
        "peso_minimo_gestao": {"label": "Peso mínimo de gestão", "priority": "optional", "dtype": "number", "aliases": ["peso_minimo_gestao", "peso_mínimo_gestão", "minimum_management_weight"]},
    },
    "responsaveis": {
        "responsavel": {"label": "Responsável", "priority": "required", "dtype": "text", "aliases": ["responsavel", "responsável", "name"]},
        "cargo_funcao": {"label": "Cargo / Função", "priority": "recommended", "dtype": "text", "aliases": ["cargo_funcao", "cargo_função", "role"]},
        "area": {"label": "Área", "priority": "recommended", "dtype": "text", "aliases": ["area", "área"]},
        "email": {"label": "E-mail", "priority": "recommended", "dtype": "text", "aliases": ["email", "e_mail", "e-mail"]},
        "observacao": {"label": "Observação", "priority": "optional", "dtype": "text", "aliases": ["observacao", "observação", "notes"]},
    },
    "alavancas_simulador": {
        "grupo": {"label": "Grupo", "priority": "required", "dtype": "text", "aliases": ["grupo", "group"]},
        "alavanca": {"label": "Alavanca", "priority": "required", "dtype": "text", "aliases": ["alavanca", "lever"]},
        "formato": {"label": "Formato", "priority": "recommended", "dtype": "text", "aliases": ["formato", "format"]},
        "atual_exemplo": {"label": "Atual exemplo", "priority": "optional", "dtype": "number", "aliases": ["atual_exemplo", "current_example"]},
        "meta_exemplo": {"label": "Meta exemplo", "priority": "optional", "dtype": "number", "aliases": ["meta_exemplo", "target_example"]},
        "unidade": {"label": "Unidade", "priority": "optional", "dtype": "text", "aliases": ["unidade", "unit"]},
        "impacto_principal": {"label": "Impacto principal", "priority": "optional", "dtype": "text", "aliases": ["impacto_principal", "primary_impact"]},
        "impacto_secundario": {"label": "Impacto secundário", "priority": "optional", "dtype": "text", "aliases": ["impacto_secundario", "secondary_impact"]},
        "dependencia": {"label": "Dependência", "priority": "optional", "dtype": "text", "aliases": ["dependencia", "dependência", "dependency"]},
        "confianca": {"label": "Confiança", "priority": "optional", "dtype": "text", "aliases": ["confianca", "confiança", "confidence"]},
        "ativa": {"label": "Ativa", "priority": "optional", "dtype": "text", "aliases": ["ativa", "active"]},
        "observacao": {"label": "Observação", "priority": "optional", "dtype": "text", "aliases": ["observacao", "observação", "notes"]},
    },
    "premissas_simulador": {
        "chave": {"label": "Chave", "priority": "required", "dtype": "text", "aliases": ["chave", "key"]},
        "valor": {"label": "Valor", "priority": "required", "dtype": "number", "aliases": ["valor", "value"]},
        "unidade": {"label": "Unidade", "priority": "optional", "dtype": "text", "aliases": ["unidade", "unit"]},
        "uso_no_motor": {"label": "Uso no motor", "priority": "optional", "dtype": "text", "aliases": ["uso_no_motor", "engine_use"]},
        "observacao": {"label": "Observação", "priority": "optional", "dtype": "text", "aliases": ["observacao", "observação", "notes"]},
    },
}

CORE_APPLY_REQUIREMENTS: Dict[str, List[str]] = {
    "producao": ["data", "linha", "produto", "planejado", "realizado", "horas_disponiveis", "horas_paradas", "velocidade_real", "velocidade_nominal"],
    "qualidade": ["data", "linha", "produto", "produzido", "aprovado", "refugo"],
    "manutencao": ["data", "linha", "maquina", "duracao_horas", "causa"],
    "pessoas": ["data", "linha", "horas_normais", "horas_extras"],
    "custos": ["data", "linha", "custo_mp", "custo_mod", "custo_energia", "custo_manutencao", "receita"],
}

DIMENSION_FIELDS = {
    "grupo", "fabrica", "planta", "linha", "produto", "maquina", "turno", "causa", "tipo_parada", "familia", "linha_padrao", "indicador", "area", "responsavel", "centro_custo"
}

UNIT_OPTIONS = [AUTO_UNIT, NO_CONVERSION, "segundos", "minutos", "horas", "kg", "toneladas", "unidades", "R$", "R$ mil", "% (0-100)", "decimal (0-1)"]


@dataclass
class QualityResult:
    score: float
    status: str
    blocking: bool
    checks: pd.DataFrame
    summary: Dict[str, Any]


def _similarity(a: str, b: str) -> float:
    aa, bb = norm(a), norm(b)
    if not aa or not bb:
        return 0.0
    if aa == bb:
        return 1.0
    if aa in bb or bb in aa:
        return 0.90
    seq = SequenceMatcher(None, aa, bb).ratio()
    at, bt = set(aa.split("_")), set(bb.split("_"))
    token = len(at & bt) / max(1, len(at | bt))
    return max(seq, token)


def _type_hint(series: pd.Series) -> str:
    sample = series.dropna().head(200)
    if sample.empty:
        return "empty"
    if pd.api.types.is_datetime64_any_dtype(sample):
        return "date"
    numeric = pd.to_numeric(sample.astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False), errors="coerce")
    numeric_ratio = float(numeric.notna().mean())
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        date_parsed = pd.to_datetime(sample, errors="coerce", dayfirst=True)
    date_ratio = float(date_parsed.notna().mean())
    if date_ratio >= 0.90 and numeric_ratio < 0.90:
        return "date"
    if numeric_ratio >= 0.90:
        return "number"
    return "text"


def infer_unit(column_name: str, canonical_field: Optional[str] = None) -> str:
    n = norm(column_name)
    if re.search(r"(^|_)min($|_)", n) or "minuto" in n:
        return "minutos"
    if re.search(r"(^|_)(hr|hrs|hora|horas|h)($|_)", n):
        return "horas"
    if "seg" in n or "second" in n:
        return "segundos"
    if "kg" in n:
        return "kg"
    if "ton" in n:
        return "toneladas"
    if "pct" in n or "percent" in n or "porcent" in n or "%" in str(column_name):
        return "% (0-100)"
    if "mil_r" in n or "r_mil" in n or "mil_reais" in n:
        return "R$ mil"
    if "custo" in n or "receita" in n or "valor" in n or "revenue" in n:
        return "R$"
    target = get_target_unit(canonical_field)
    return target if target in {"horas", "minutos", "kg", "unidades", "R$"} else AUTO_UNIT


def get_target_unit(field: Optional[str]) -> Optional[str]:
    if not field:
        return None
    for fields in FIELD_SPECS.values():
        if field in fields:
            return fields[field].get("unit")
    return None


def entity_options() -> List[str]:
    return [IGNORE_ENTITY] + [ENTITY_LABELS[k] for k in ENTITY_LABELS]


def field_options(entity: str) -> List[str]:
    return ["Não mapear"] + list(FIELD_SPECS.get(entity, {}).keys())


def field_display(entity: str, field: str) -> str:
    if field == "Não mapear":
        return field
    spec = FIELD_SPECS.get(entity, {}).get(field, {})
    label = spec.get("label", field)
    priority = spec.get("priority", "optional")
    suffix = {"required": "Obrigatório", "recommended": "Recomendado", "optional": "Opcional"}.get(priority, priority)
    return f"{label} · {suffix}"


def field_label_to_name(entity: str, display: str) -> str:
    if display == "Não mapear":
        return display
    for field in FIELD_SPECS.get(entity, {}):
        if field_display(entity, field) == display:
            return field
    return display


def workbook_fingerprint(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()



# ---------------------------------------------------------------------------
# v0.6.5 — Smart sheet reading + semantic context
# ---------------------------------------------------------------------------

HEADER_SCAN_ROWS = 18

def _all_alias_keys() -> set[str]:
    keys=set()
    for entity,fields in FIELD_SPECS.items():
        for field,spec in fields.items():
            keys.add(norm(field))
            keys.add(norm(spec.get("label","")))
            for alias in spec.get("aliases",[]):
                keys.add(norm(alias))
    for entity,aliases in SHEET_ALIASES.items():
        keys.add(norm(entity))
        for alias in aliases:
            keys.add(norm(alias))
    return {k for k in keys if k}

_HEADER_ALIAS_KEYS=_all_alias_keys()


def _header_row_score(values: List[Any]) -> float:
    cleaned=[str(v).strip() for v in values if pd.notna(v) and str(v).strip() and str(v).strip().lower()!="nan"]
    if len(cleaned)<2:
        return -10.0
    norms=[norm(v) for v in cleaned]
    alias_hits=sum(1 for v in norms if v in _HEADER_ALIAS_KEYS)
    fuzzy_hits=0
    for v in norms:
        if v in _HEADER_ALIAS_KEYS:
            continue
        if any(_similarity(v,a)>=0.90 for a in _HEADER_ALIAS_KEYS):
            fuzzy_hits+=1
    numericish=sum(1 for v in cleaned if re.fullmatch(r"[-+]?[\d.,%$Rr\s]+",v) is not None)
    long_text=sum(1 for v in cleaned if len(v)>55)
    unique_ratio=len(set(norms))/max(1,len(norms))
    return (
        alias_hits*5.0 + fuzzy_hits*2.5 + min(len(cleaned),14)*0.25 +
        unique_ratio*1.4 - numericish*0.35 - long_text*0.45
    )


def smart_read_sheet(raw: bytes, sheet_name: str, max_header_rows: int = HEADER_SCAN_ROWS) -> Tuple[pd.DataFrame, Dict[str,Any]]:
    """
    Read semi-structured Excel sheets without assuming row 1 is the header.
    Returns a clean DataFrame and metadata describing the detected header/context.
    """
    preview=pd.read_excel(BytesIO(raw),sheet_name=sheet_name,header=None,nrows=max_header_rows)
    if preview.empty:
        return pd.DataFrame(), {"header_row":0,"confidence":0.0,"context_lines":[],"context_text":""}

    scores=[]
    for idx,row in preview.iterrows():
        scores.append((int(idx),_header_row_score(row.tolist())))
    best_idx,best_score=max(scores,key=lambda x:x[1])
    row0_score=dict(scores).get(0,-10.0)

    # Prefer row 0 when it is already a strong header; otherwise accept later row.
    header_idx=0 if row0_score>=best_score-1.0 and row0_score>=5.0 else best_idx
    confidence=float(np.clip((dict(scores).get(header_idx,0)+2)/18,0.35,0.99))

    df=pd.read_excel(BytesIO(raw),sheet_name=sheet_name,header=header_idx)
    df=df.dropna(axis=1,how="all").dropna(axis=0,how="all").reset_index(drop=True)
    df.columns=[
        str(c).strip() if str(c).strip() and not str(c).lower().startswith("unnamed") else f"coluna_{i+1}"
        for i,c in enumerate(df.columns)
    ]

    context_lines=[]
    if header_idx>0:
        raw_context=pd.read_excel(BytesIO(raw),sheet_name=sheet_name,header=None,nrows=header_idx)
        for _,r in raw_context.iterrows():
            vals=[str(v).strip() for v in r.tolist() if pd.notna(v) and str(v).strip() and str(v).strip().lower()!="nan"]
            if vals:
                context_lines.append(" | ".join(vals))
    return df,{
        "header_row":int(header_idx),
        "confidence":round(confidence,4),
        "context_lines":context_lines,
        "context_text":" ; ".join(context_lines),
        "header_score":round(float(dict(scores).get(header_idx,0)),3),
    }


_MONTH_WORDS={
    "jan","janeiro","feb","fev","fevereiro","mar","marco","março","apr","abr","abril",
    "may","mai","maio","jun","junho","jul","julho","aug","ago","agosto","sep","set","setembro",
    "oct","out","outubro","nov","novembro","dec","dez","dezembro"
}


def _clean_context_value(value: str, dimension: str) -> str:
    s=str(value or "").strip(" _-–—:;|")
    s=re.sub(r"\.(xlsx|xls|csv)$","",s,flags=re.I)
    # Remove obvious period/file descriptors.
    parts=[p for p in re.split(r"[\s_\-]+",s) if p]
    parts=[p for p in parts if norm(p) not in _MONTH_WORDS and not re.fullmatch(r"20\d{2}",p)]
    s=" ".join(parts).strip()
    if dimension=="fabrica":
        s=re.sub(r"^(planta|fabrica|fábrica|factory|site|unidade\s+(fabril|industrial))\s*[:\-]?\s*","",s,flags=re.I).strip()
        if s and not norm(s).startswith(("planta_","fabrica_")):
            s=f"Planta {s}"
    return s


def infer_context_from_text(text: str, dimension: str) -> Optional[str]:
    text=str(text or "").strip()
    if not text:
        return None
    if dimension=="fabrica":
        patterns=[
            r"(?:planta|f[aá]brica|factory|site|unidade\s+(?:fabril|industrial))\s*[:=\-–|]\s*([A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9 ._/\\-]{1,45})",
        ]
    elif dimension=="grupo":
        patterns=[
            r"(?:grupo|group|holding)\s*[:=\-–|]\s*([A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9 ._/\\-]{1,55})",
        ]
    else:
        return None
    for pat in patterns:
        m=re.search(pat,text,flags=re.I)
        if m:
            val=_clean_context_value(m.group(1),dimension)
            if val:
                return val
    return None


def infer_sheet_semantic_context(filename: str, sheet_name: str, context_text: str, entity: Optional[str]) -> Dict[str,Any]:
    """Infer contextual dimensions from preamble, sheet name and file name."""
    candidates={}
    evidences=[
        ("cabeçalho/contexto",context_text,0.94),
        ("nome da aba",sheet_name,0.80),
        ("nome do arquivo",filename,0.74),
    ]
    for dim in ["grupo","fabrica"]:
        for source,text,conf in evidences:
            value=infer_context_from_text(text,dim)
            if value:
                candidates[dim]={"value":value,"confidence":conf,"source":source}
                break

    # If sheet contains entity + a remaining location token, use as low-confidence plant context.
    if "fabrica" not in candidates and entity:
        n=norm(sheet_name)
        aliases=[norm(entity)]+[norm(a) for a in SHEET_ALIASES.get(entity,[])]
        remainder=n
        for alias in sorted(aliases,key=len,reverse=True):
            if alias and alias in remainder:
                remainder=remainder.replace(alias,"_")
        tokens=[t for t in remainder.split("_") if t and t not in _MONTH_WORDS and not re.fullmatch(r"20\d{2}",t)]
        if tokens:
            raw=" ".join(tokens)
            if len(raw)>=3:
                candidates["fabrica"]={"value":_clean_context_value(raw,"fabrica"),"confidence":0.68,"source":"nome da aba (inferido)"}
    return candidates


def _dimension_key(value: Any, dimension: str) -> str:
    n=norm(value)
    if not n:
        return ""
    prefixes={
        "fabrica":["planta","fabrica","factory","site","unidade_fabril","unidade_industrial"],
        "linha":["linha","line","celula","cell"],
        "maquina":["maquina","machine","equipamento","equipment"],
        "produto":["produto","product","sku","item"],
        "grupo":["grupo","group","holding"],
    }
    parts=n.split("_")
    while parts and "_".join(parts[:2]) in prefixes.get(dimension,[]):
        parts=parts[2:]
    if parts and parts[0] in prefixes.get(dimension,[]):
        parts=parts[1:]
    key="_".join(parts)
    if dimension=="linha":
        key=re.sub(r"^l(?=\d)","",key)
        key=re.sub(r"^0+(?=\d)","",key)
    return key or n


def _canonical_display(values: List[str], dimension: str) -> str:
    vals=[str(v).strip() for v in values if pd.notna(v) and str(v).strip()]
    if not vals:
        return ""
    # Prefer most frequent; for plants prefer explicit "Planta ..." naming.
    counts=pd.Series(vals).value_counts()
    if dimension=="fabrica":
        plant_vals=[v for v in counts.index if norm(v).startswith("planta_")]
        if plant_vals:
            return str(max(plant_vals,key=lambda v:(counts[v],len(v))))
    return str(max(counts.index,key=lambda v:(counts[v],len(v))))


def canonicalize_dimensions(standard: Dict[str,pd.DataFrame], mapping: Dict[str,Any]) -> Tuple[Dict[str,pd.DataFrame],List[Dict[str,Any]]]:
    """Unify synonymous dimension values across entities (e.g. Fábrica SP / Planta SP)."""
    lineage=[]
    dim_fields={
        "grupo":["grupo"],
        "fabrica":["fabrica","planta"],
        "linha":["linha"],
        "maquina":["maquina"],
        "produto":["produto"],
    }
    buckets={d:{} for d in dim_fields}
    for entity,df in standard.items():
        if df is None or df.empty:
            continue
        for dim,fields in dim_fields.items():
            for field in fields:
                if field not in df.columns:
                    continue
                for v in df[field].dropna().astype(str):
                    if not v.strip():
                        continue
                    key=_dimension_key(v,dim)
                    if key:
                        buckets[dim].setdefault(key,[]).append(v)

    canonical={}
    for dim,groups in buckets.items():
        canonical[dim]={k:_canonical_display(vals,dim) for k,vals in groups.items()}

    for entity,df in standard.items():
        if df is None or df.empty:
            continue
        out=df.copy()
        for dim,fields in dim_fields.items():
            for field in fields:
                if field not in out.columns:
                    continue
                before=out[field].copy()
                out[field]=out[field].map(
                    lambda v: (
                        _clean_context_value(canonical[dim].get(_dimension_key(v,dim),v),"fabrica")
                        if dim=="fabrica"
                        else canonical[dim].get(_dimension_key(v,dim),v)
                    ) if pd.notna(v) and str(v).strip() else v
                )
                changed=((before.astype(str)!=out[field].astype(str)) & before.notna()).sum()
                if changed:
                    lineage.append({
                        "entidade":entity,"campo_padrao":field,"aba_origem":"semantic",
                        "coluna_origem":field,"unidade_origem":None,"unidade_destino":None,
                        "confianca":0.96,"transformacao":f"canonicalização semântica de {dim}: {int(changed)} valor(es)"
                    })
        standard[entity]=out
    mapping["semantic_canonical_values"]=canonical
    return standard,lineage


def _unique_relationship(df: pd.DataFrame, key_col: str, value_col: str) -> Dict[str,str]:
    if df is None or df.empty or key_col not in df.columns or value_col not in df.columns:
        return {}
    tmp=df[[key_col,value_col]].dropna().copy()
    tmp=tmp[(tmp[key_col].astype(str).str.strip()!="") & (tmp[value_col].astype(str).str.strip()!="")]
    if tmp.empty:
        return {}
    rel={}
    for key,g in tmp.groupby(key_col):
        vals=g[value_col].astype(str).drop_duplicates().tolist()
        if len(vals)==1:
            rel[str(key)]=vals[0]
    return rel


def build_relationship_catalog(standard: Dict[str,pd.DataFrame]) -> Dict[str,Dict[str,str]]:
    """Build only unambiguous relationships; never guess many-to-many relationships."""
    combined=[]
    for entity,df in standard.items():
        if df is None or df.empty:
            continue
        temp=df.copy()
        if "planta" in temp.columns and "fabrica" not in temp.columns:
            temp["fabrica"]=temp["planta"]
        cols=[c for c in ["grupo","fabrica","linha","maquina","produto"] if c in temp.columns]
        if cols:
            combined.append(temp[cols])
    all_df=pd.concat(combined,ignore_index=True,sort=False) if combined else pd.DataFrame()

    rel={
        "linha_to_fabrica":_unique_relationship(all_df,"linha","fabrica"),
        "maquina_to_linha":_unique_relationship(all_df,"maquina","linha"),
        "maquina_to_fabrica":_unique_relationship(all_df,"maquina","fabrica"),
        "produto_to_fabrica":_unique_relationship(all_df,"produto","fabrica"),
        "fabrica_to_grupo":_unique_relationship(all_df,"fabrica","grupo"),
        "linha_to_grupo":_unique_relationship(all_df,"linha","grupo"),
    }
    return rel


def semantic_enrich_standard(
    standard: Dict[str,pd.DataFrame],
    mapping: Dict[str,Any],
) -> Tuple[Dict[str,pd.DataFrame],List[Dict[str,Any]],pd.DataFrame]:
    """
    Resolve missing Group/Plant/Line using explicit data, sheet/file context and
    cross-table relationships. It never fills a dimension when the relationship is ambiguous.
    """
    standard,canon_lineage=canonicalize_dimensions(standard,mapping)
    lineage=list(canon_lineage)
    report_rows=[]

    learned_relationships=mapping.get("semantic_relationships",{}) if isinstance(mapping.get("semantic_relationships",{}),dict) else {}

    def _merged_relationships(current):
        merged={k:dict(v) for k,v in current.items()}
        for rel_name,rel_map in learned_relationships.items():
            if not isinstance(rel_map,dict):
                continue
            merged.setdefault(rel_name,{})
            # Current-file evidence wins; learned mapping only fills missing keys.
            for key,value in rel_map.items():
                merged[rel_name].setdefault(str(key),value)
        return merged

    relationships=_merged_relationships(build_relationship_catalog(standard))

    # Two passes allow master data / explicit relationships to propagate.
    for pass_no in [1,2]:
        for entity,df in list(standard.items()):
            if df is None or df.empty:
                continue
            out=df.copy()
            source_sheet=out["_source_sheet"] if "_source_sheet" in out.columns else pd.Series([""]*len(out),index=out.index)

            plant_field="planta" if entity=="dre_gerencial" else ("fabrica" if "fabrica" in FIELD_SPECS.get(entity,{}) else None)
            if plant_field and plant_field not in out.columns:
                out[plant_field]=pd.Series(pd.NA,index=out.index,dtype="string")
            if "grupo" in FIELD_SPECS.get(entity,{}) and "grupo" not in out.columns:
                out["grupo"]=pd.Series(pd.NA,index=out.index,dtype="string")
            if "linha" in FIELD_SPECS.get(entity,{}) and "linha" not in out.columns:
                out["linha"]=pd.Series(pd.NA,index=out.index,dtype="string")

            # Line from machine relationship.
            if "linha" in out.columns and "maquina" in out.columns:
                missing=out["linha"].isna() | out["linha"].astype(str).str.strip().isin(["","<NA>","nan"])
                inferred=out["maquina"].astype(str).map(relationships.get("maquina_to_linha",{}))
                fill=missing & inferred.notna()
                if fill.any():
                    out.loc[fill,"linha"]=inferred[fill]
                    report_rows.append([entity,"Linha",int(fill.sum()),"relação Máquina → Linha",0.98,"Resolvido"])

            # Plant from line, machine, product, then sheet context.
            if plant_field:
                missing=out[plant_field].isna() | out[plant_field].astype(str).str.strip().isin(["","<NA>","nan"])
                candidates=[
                    ("relação Linha → Planta","linha",relationships.get("linha_to_fabrica",{}),0.98),
                    ("relação Máquina → Planta","maquina",relationships.get("maquina_to_fabrica",{}),0.98),
                    ("relação Produto → Planta","produto",relationships.get("produto_to_fabrica",{}),0.90),
                ]
                for method,keycol,relmap,conf in candidates:
                    if keycol in out.columns and missing.any():
                        inferred=out[keycol].astype(str).map(relmap)
                        fill=missing & inferred.notna()
                        if fill.any():
                            out.loc[fill,plant_field]=inferred[fill]
                            report_rows.append([entity,"Planta",int(fill.sum()),method,conf,"Resolvido"])
                            missing=out[plant_field].isna() | out[plant_field].astype(str).str.strip().isin(["","<NA>","nan"])
                if missing.any():
                    context_map=mapping.get("semantic_context",{})
                    ctx=source_sheet.map(
                        lambda sh: (context_map.get(str(sh),{}).get("fabrica") or {}).get("value")
                    )
                    ctx_conf=source_sheet.map(
                        lambda sh: (context_map.get(str(sh),{}).get("fabrica") or {}).get("confidence",0.0)
                    )
                    fill=missing & ctx.notna() & (ctx.astype(str).str.strip()!="") & (ctx_conf>=0.68)
                    if fill.any():
                        out.loc[fill,plant_field]=ctx[fill]
                        report_rows.append([entity,"Planta",int(fill.sum()),"contexto de arquivo/aba/cabeçalho",float(ctx_conf[fill].mean()),"Resolvido"])

            # Group from plant/line, then context.
            if "grupo" in out.columns:
                missing=out["grupo"].isna() | out["grupo"].astype(str).str.strip().isin(["","<NA>","nan"])
                if plant_field and plant_field in out.columns and missing.any():
                    inferred=out[plant_field].astype(str).map(relationships.get("fabrica_to_grupo",{}))
                    fill=missing & inferred.notna()
                    if fill.any():
                        out.loc[fill,"grupo"]=inferred[fill]
                        report_rows.append([entity,"Grupo",int(fill.sum()),"relação Planta → Grupo",0.98,"Resolvido"])
                        missing=out["grupo"].isna() | out["grupo"].astype(str).str.strip().isin(["","<NA>","nan"])
                if "linha" in out.columns and missing.any():
                    inferred=out["linha"].astype(str).map(relationships.get("linha_to_grupo",{}))
                    fill=missing & inferred.notna()
                    if fill.any():
                        out.loc[fill,"grupo"]=inferred[fill]
                        report_rows.append([entity,"Grupo",int(fill.sum()),"relação Linha → Grupo",0.96,"Resolvido"])
                        missing=out["grupo"].isna() | out["grupo"].astype(str).str.strip().isin(["","<NA>","nan"])
                if missing.any():
                    context_map=mapping.get("semantic_context",{})
                    ctx=source_sheet.map(lambda sh:(context_map.get(str(sh),{}).get("grupo") or {}).get("value"))
                    ctx_conf=source_sheet.map(lambda sh:(context_map.get(str(sh),{}).get("grupo") or {}).get("confidence",0.0))
                    fill=missing & ctx.notna() & (ctx.astype(str).str.strip()!="") & (ctx_conf>=0.68)
                    if fill.any():
                        out.loc[fill,"grupo"]=ctx[fill]
                        report_rows.append([entity,"Grupo",int(fill.sum()),"contexto de arquivo/aba/cabeçalho",float(ctx_conf[fill].mean()),"Resolvido"])

            standard[entity]=out
        relationships=_merged_relationships(build_relationship_catalog(standard))

    # Final unresolved report.
    for entity,df in standard.items():
        if df is None or df.empty:
            continue
        checks=[]
        if "grupo" in FIELD_SPECS.get(entity,{}):
            checks.append(("Grupo","grupo"))
        if entity=="dre_gerencial" and "planta" in FIELD_SPECS.get(entity,{}):
            checks.append(("Planta","planta"))
        elif "fabrica" in FIELD_SPECS.get(entity,{}):
            checks.append(("Planta","fabrica"))
        for label,field in checks:
            if field not in df.columns:
                unresolved=len(df)
            else:
                unresolved=int((df[field].isna() | df[field].astype(str).str.strip().isin(["","<NA>","nan"])).sum())
            if unresolved:
                report_rows.append([entity,label,unresolved,"sem evidência suficiente",0.0,"Não resolvido"])

    # Drop internal provenance columns before the application layer.
    for entity,df in list(standard.items()):
        if df is not None and not df.empty:
            standard[entity]=df.drop(columns=[c for c in ["_source_sheet","_source_row"] if c in df.columns],errors="ignore")

    report=pd.DataFrame(report_rows,columns=["Entidade","Dimensão","Registros","Método","Confiança","Status"])
    if not report.empty:
        report["Confiança"]=pd.to_numeric(report["Confiança"],errors="coerce").fillna(0.0)
    mapping["semantic_relationships"]=relationships
    mapping["semantic_resolution"]={
        "resolved_rows":int(report.loc[report["Status"]=="Resolvido","Registros"].sum()) if not report.empty else 0,
        "unresolved_rows":int(report.loc[report["Status"]=="Não resolvido","Registros"].sum()) if not report.empty else 0,
        "report":report.to_dict(orient="records") if not report.empty else [],
    }
    for _,r in report[report["Status"]=="Resolvido"].iterrows() if not report.empty else []:
        lineage.append({
            "entidade":r["Entidade"],"campo_padrao":r["Dimensão"].lower(),
            "aba_origem":"semantic","coluna_origem":"relacionamentos/contexto",
            "unidade_origem":None,"unidade_destino":None,"confianca":float(r["Confiança"]),
            "transformacao":f"resolução semântica: {r['Método']} ({int(r['Registros'])} registros)"
        })
    return standard,lineage,report

def inspect_workbook(raw: bytes, filename: str = "arquivo.xlsx") -> Dict[str, Any]:
    xls = pd.ExcelFile(BytesIO(raw))
    sheets: Dict[str, Any] = {}
    total_rows = 0
    for sh in xls.sheet_names:
        df,read_meta = smart_read_sheet(raw,sh)
        total_rows += len(df)
        sheets[sh] = {
            "rows": int(len(df)),
            "cols": int(len(df.columns)),
            "columns": [str(c) for c in df.columns],
            "types": {str(c): _type_hint(df[c]) for c in df.columns},
            "preview": df.head(20),
            "header_row": int(read_meta.get("header_row",0)),
            "header_confidence": float(read_meta.get("confidence",0)),
            "context_lines": read_meta.get("context_lines",[]),
            "context_text": read_meta.get("context_text",""),
        }
    return {
        "filename": filename,
        "hash": workbook_fingerprint(raw),
        "size_bytes": len(raw),
        "sheet_count": len(sheets),
        "total_rows": total_rows,
        "sheets": sheets,
    }


def suggest_entity(sheet_name: str, columns: List[str]) -> Tuple[Optional[str], float, str]:
    best_entity, best_score, best_reason = None, 0.0, ""
    n_sheet = norm(sheet_name)
    if n_sheet in {"leia_me", "leia", "readme", "instructions", "instrucoes", "info", "informacoes"}:
        return None, 0.99, "aba informativa detectada"
    unnamed_ratio = (sum(1 for c in columns if norm(c).startswith("unnamed")) / max(1, len(columns))) if columns else 0.0
    if unnamed_ratio >= 0.60:
        return None, 0.90, "estrutura informativa / cabeçalho não tabular"
    for entity in ENTITY_LABELS:
        sheet_score = max((_similarity(n_sheet, a) for a in SHEET_ALIASES.get(entity, [])), default=0.0)
        field_specs = FIELD_SPECS.get(entity, {})
        if columns and field_specs:
            column_hits = []
            for col in columns:
                best_col = 0.0
                for field, spec in field_specs.items():
                    for alias in spec.get("aliases", []) + [field]:
                        best_col = max(best_col, _similarity(col, alias))
                column_hits.append(best_col)
            strong = sum(1 for x in column_hits if x >= 0.84)
            coverage = strong / max(1, min(len(columns), max(4, len(field_specs))))
            col_score = min(1.0, coverage * 1.35)
        else:
            col_score = 0.0
        score = 0.58 * sheet_score + 0.42 * col_score
        if sheet_score >= 0.98:
            score = max(score, 0.94)
        if score > best_score:
            best_entity, best_score = entity, score
            best_reason = f"nome da aba {sheet_score:.0%} · colunas {col_score:.0%}"
    if best_score < 0.42:
        return None, best_score, "baixa confiança"
    return best_entity, min(best_score, 0.99), best_reason


def suggest_column(entity: str, column_name: str, series: Optional[pd.Series] = None) -> Tuple[Optional[str], float, str]:
    specs = FIELD_SPECS.get(entity, {})
    best_field, best_score, best_sim = None, 0.0, 0.0
    detected_type = _type_hint(series) if series is not None else None
    for field, spec in specs.items():
        sim = max((_similarity(column_name, a) for a in spec.get("aliases", []) + [field]), default=0.0)
        dtype_score = 0.0
        if detected_type and detected_type != "empty":
            dtype_score = 1.0 if detected_type == spec.get("dtype") else 0.0
        score = 0.84 * sim + 0.16 * dtype_score
        if sim >= 0.99:
            score = max(score, 0.98)
        if score > best_score:
            best_field, best_score, best_sim = field, score, sim

    # "Unidade" is ambiguous in industrial files: it can mean unit of measure
    # or business/plant unit. Use values to decide and never map UOMs to Planta.
    if norm(column_name) in {"unidade","unit"} and best_field in {"fabrica","planta"} and series is not None:
        vals=[norm(v) for v in series.dropna().astype(str).head(80) if str(v).strip()]
        uom_tokens={
            "kg","g","t","ton","tonelada","toneladas","un","und","unidade","unidades",
            "pct","percentual","porcentagem","r","rs","r_mil","h","hora","horas",
            "min","minuto","minutos","kwh","mwh","litro","litros","l"
        }
        if vals and sum(v in uom_tokens for v in vals)/len(vals) >= 0.45:
            return None, min(best_score,0.69), "coluna 'Unidade' interpretada como unidade de medida, não Planta"
        # Text-like repeated labels are plausible plants, but remain confirmable.
        if vals and len(set(vals)) <= 30:
            best_score=max(best_score,0.76)
            best_sim=max(best_sim,0.60)

    # Semantic dimensions must have lexical evidence. Type alone cannot turn
    # an arbitrary text column ("Observação", "Status", etc.) into Planta/Linha.
    if best_field in DIMENSION_FIELDS and best_sim < 0.58:
        return None, best_score, f"sem evidência semântica suficiente · tipo: {detected_type or 'n/d'}"
    if best_score < 0.56:
        return None, best_score, f"baixa confiança · tipo detectado: {detected_type or 'n/d'}"
    return best_field, min(best_score, 0.99), f"tipo detectado: {detected_type or 'n/d'}"


def build_initial_mapping(raw: bytes, filename: str = "arquivo.xlsx") -> Dict[str, Any]:
    profile = inspect_workbook(raw, filename)
    xls = pd.ExcelFile(BytesIO(raw))
    sheet_map: Dict[str, Any] = {}
    column_map: Dict[str, Dict[str, Any]] = {}
    unit_map: Dict[str, Dict[str, Any]] = {}
    dimension_map: Dict[str, Dict[str, Dict[str, str]]] = {}
    semantic_context: Dict[str, Dict[str, Any]] = {}

    for sh, info in profile["sheets"].items():
        entity, conf, reason = suggest_entity(sh, info["columns"])
        sheet_map[sh] = {"entity": entity, "confidence": round(conf, 4), "reason": reason}
        semantic_context[sh] = infer_sheet_semantic_context(
            filename, sh, info.get("context_text",""), entity
        )
        if entity:
            df, _ = smart_read_sheet(raw, sh)
            column_map[sh] = {}
            unit_map[sh] = {}
            dimension_map[sh] = {}
            used_fields: set[str] = set()
            for col in df.columns:
                field, cconf, creason = suggest_column(entity, str(col), df[col])
                if field in used_fields and cconf < 0.97:
                    field = None
                if field:
                    used_fields.add(field)
                column_map[sh][str(col)] = {
                    "field": field,
                    "confidence": round(cconf, 4),
                    "reason": creason,
                }
                if field:
                    unit_map[sh][str(col)] = {
                        "source": infer_unit(str(col), field),
                        "target": FIELD_SPECS.get(entity, {}).get(field, {}).get("unit"),
                    }
                    if field in DIMENSION_FIELDS:
                        vals = df[col].dropna().astype(str).str.strip()
                        uniques = vals[vals.ne("")].drop_duplicates().head(80).tolist()
                        dimension_map[sh][field] = {v: v for v in uniques}
    return {
        "version": DATA_LAYER_VERSION,
        "workbook": {k: v for k, v in profile.items() if k != "sheets"},
        "sheet_map": sheet_map,
        "column_map": column_map,
        "unit_map": unit_map,
        "dimension_map": dimension_map,
        "semantic_context": semantic_context,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def refresh_column_mapping(raw: bytes, mapping: Dict[str, Any]) -> Dict[str, Any]:
    """Rebuild suggestions after sheet/entity classification while preserving explicit matches when possible."""
    xls = pd.ExcelFile(BytesIO(raw))
    mapping.setdefault("column_map", {})
    mapping.setdefault("unit_map", {})
    mapping.setdefault("dimension_map", {})
    for sh in xls.sheet_names:
        sm = mapping.get("sheet_map", {}).get(sh, {})
        entity = sm.get("entity")
        if not entity:
            continue
        df,read_meta = smart_read_sheet(raw, sh)
        mapping.setdefault("semantic_context", {})[sh] = infer_sheet_semantic_context(
            mapping.get("workbook",{}).get("filename","arquivo.xlsx"),
            sh, read_meta.get("context_text",""), entity
        )
        old = mapping["column_map"].get(sh, {})
        mapping["column_map"][sh] = {}
        mapping["unit_map"].setdefault(sh, {})
        mapping["dimension_map"].setdefault(sh, {})
        used_fields: set[str] = set()
        for col in df.columns:
            col_s = str(col)
            old_field = old.get(col_s, {}).get("field")
            if old_field in FIELD_SPECS.get(entity, {}) and old_field not in used_fields:
                field = old_field
                cconf = old.get(col_s, {}).get("confidence", 1.0)
                creason = old.get(col_s, {}).get("reason", "mapeamento preservado")
            else:
                field, cconf, creason = suggest_column(entity, col_s, df[col])
                if field in used_fields and cconf < 0.97:
                    field = None
            if field:
                used_fields.add(field)
            mapping["column_map"][sh][col_s] = {"field": field, "confidence": round(float(cconf), 4), "reason": creason}
            if field:
                mapping["unit_map"][sh].setdefault(col_s, {"source": infer_unit(col_s, field), "target": FIELD_SPECS[entity][field].get("unit")})
                mapping["unit_map"][sh][col_s]["target"] = FIELD_SPECS[entity][field].get("unit")
                if field in DIMENSION_FIELDS:
                    vals = df[col].dropna().astype(str).str.strip()
                    uniques = vals[vals.ne("")].drop_duplicates().head(80).tolist()
                    current = mapping["dimension_map"][sh].setdefault(field, {})
                    for val in uniques:
                        current.setdefault(val, val)
    return mapping


def _convert_numeric(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")
    cleaned = series.astype(str).str.strip()
    # Brazilian/European number handling: 1.234,56 -> 1234.56; plain 1234.56 remains valid.
    has_comma = cleaned.str.contains(",", regex=False).mean() > 0.20
    if has_comma:
        cleaned = cleaned.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    return pd.to_numeric(cleaned, errors="coerce")


def _convert_date_series(series: pd.Series) -> pd.Series:
    """Handle both true Excel dates and numeric Excel serial dates."""
    numeric=pd.to_numeric(series,errors="coerce")
    valid=numeric.dropna()
    if len(valid) and float(valid.median())>=20000 and float(valid.median())<=80000:
        return pd.to_datetime(numeric,unit="D",origin="1899-12-30",errors="coerce")
    return pd.to_datetime(series,errors="coerce",dayfirst=True)


def apply_unit_conversion(series: pd.Series, source_unit: Optional[str], target_unit: Optional[str]) -> pd.Series:
    if not target_unit or not source_unit or source_unit in {AUTO_UNIT, NO_CONVERSION} or source_unit == target_unit:
        return series
    s = _convert_numeric(series)
    key = (source_unit, target_unit)
    factors = {
        ("segundos", "horas"): 1 / 3600,
        ("minutos", "horas"): 1 / 60,
        ("horas", "minutos"): 60,
        ("toneladas", "kg"): 1000,
        ("kg", "toneladas"): 1 / 1000,
        ("R$ mil", "R$"): 1000,
        ("% (0-100)", "decimal (0-1)"): 1 / 100,
        ("decimal (0-1)", "% (0-100)"): 100,
    }
    factor = factors.get(key)
    return s * factor if factor is not None else series


def transform_to_standard(raw: bytes, mapping: Dict[str, Any]) -> Tuple[Dict[str, pd.DataFrame], List[Dict[str, Any]]]:
    xls = pd.ExcelFile(BytesIO(raw))
    standard: Dict[str, pd.DataFrame] = {}
    lineage: List[Dict[str, Any]] = []

    for sh in xls.sheet_names:
        entity = mapping.get("sheet_map", {}).get(sh, {}).get("entity")
        if not entity:
            continue
        df,read_meta = smart_read_sheet(raw, sh)
        mapping.setdefault("semantic_context", {}).setdefault(
            sh, infer_sheet_semantic_context(mapping.get("workbook",{}).get("filename","arquivo.xlsx"),sh,read_meta.get("context_text",""),entity)
        )
        out = pd.DataFrame(index=df.index)
        out["_source_sheet"]=sh
        out["_source_row"]=np.arange(len(df))
        for source_col, cmeta in mapping.get("column_map", {}).get(sh, {}).items():
            field = cmeta.get("field")
            if not field or field == "Não mapear" or source_col not in df.columns:
                continue
            ser = df[source_col].copy()
            spec = FIELD_SPECS.get(entity, {}).get(field, {})
            source_unit = mapping.get("unit_map", {}).get(sh, {}).get(source_col, {}).get("source", AUTO_UNIT)
            target_unit = spec.get("unit")
            if spec.get("dtype") == "date":
                ser = _convert_date_series(ser)
            elif spec.get("dtype") == "number":
                ser = _convert_numeric(ser)
                ser = apply_unit_conversion(ser, source_unit, target_unit)
            else:
                ser = ser.astype("string").str.strip()

            dmap = mapping.get("dimension_map", {}).get(sh, {}).get(field, {})
            if dmap:
                ser = ser.astype("string").map(lambda x: dmap.get(str(x), x) if pd.notna(x) else x)
            out[field] = ser
            lineage.append({
                "entidade": entity,
                "campo_padrao": field,
                "aba_origem": sh,
                "coluna_origem": source_col,
                "unidade_origem": source_unit,
                "unidade_destino": target_unit,
                "confianca": cmeta.get("confidence"),
                "transformacao": "DE/PARA + normalização de tipo/unidade" if source_unit not in {AUTO_UNIT, NO_CONVERSION, target_unit} else "DE/PARA + normalização de tipo",
            })
        if entity in standard and not out.empty:
            standard[entity] = pd.concat([standard[entity], out], ignore_index=True)
        else:
            standard[entity] = out.reset_index(drop=True)

    standard, semantic_lineage, _ = semantic_enrich_standard(standard, mapping)
    lineage.extend(semantic_lineage)
    return standard, lineage


def _check_row(checks: List[Dict[str, Any]], category: str, item: str, severity: str, result: str, detail: str, penalty: float) -> None:
    checks.append({"Categoria": category, "Item": item, "Severidade": severity, "Resultado": result, "Detalhe": detail, "Penalidade": penalty})


def evaluate_data_quality(standard: Dict[str, pd.DataFrame], mapping: Optional[Dict[str, Any]] = None) -> QualityResult:
    checks: List[Dict[str, Any]] = []
    score = 100.0
    blocking = False

    # Core entities and fields
    for entity, fields in CORE_APPLY_REQUIREMENTS.items():
        label = ENTITY_LABELS.get(entity, entity)
        if entity not in standard or standard[entity].empty:
            penalty = 12.0
            score -= penalty
            blocking = True
            _check_row(checks, "Estrutura", label, "Crítica", "Falha", "Entidade obrigatória ausente ou vazia.", penalty)
            continue
        df = standard[entity]
        missing = [f for f in fields if f not in df.columns]
        if missing:
            penalty = min(12.0, 2.0 * len(missing))
            score -= penalty
            blocking = True
            _check_row(checks, "Estrutura", label, "Crítica", "Falha", "Campos obrigatórios ausentes: " + ", ".join(missing), penalty)
        else:
            _check_row(checks, "Estrutura", label, "Crítica", "OK", "Campos obrigatórios presentes.", 0.0)

    # Completeness, type, duplicates
    for entity, df in standard.items():
        if df is None or df.empty:
            continue
        specs = FIELD_SPECS.get(entity, {})
        required = [f for f, s in specs.items() if s.get("priority") == "required" and f in df.columns]
        if required:
            null_rate = float(df[required].isna().mean().mean())
            if null_rate > 0.10:
                penalty = min(10.0, null_rate * 30)
                score -= penalty
                _check_row(checks, "Completude", ENTITY_LABELS.get(entity, entity), "Alta", "Atenção", f"{null_rate:.1%} de nulos em campos obrigatórios.", penalty)
            elif null_rate > 0:
                penalty = min(3.0, null_rate * 10)
                score -= penalty
                _check_row(checks, "Completude", ENTITY_LABELS.get(entity, entity), "Média", "Atenção", f"{null_rate:.1%} de nulos em campos obrigatórios.", penalty)
            else:
                _check_row(checks, "Completude", ENTITY_LABELS.get(entity, entity), "Média", "OK", "Sem nulos nos campos obrigatórios mapeados.", 0.0)

        dup_rate = float(df.duplicated().mean()) if len(df) else 0.0
        if dup_rate > 0:
            penalty = min(5.0, dup_rate * 20)
            score -= penalty
            _check_row(checks, "Duplicidade", ENTITY_LABELS.get(entity, entity), "Média", "Atenção", f"{dup_rate:.1%} das linhas são duplicadas.", penalty)

        for field, spec in specs.items():
            if field not in df.columns:
                continue
            if spec.get("dtype") == "date":
                invalid = float(pd.to_datetime(df[field], errors="coerce").isna().mean()) if len(df) else 0
                if invalid > 0.05:
                    penalty = min(4.0, invalid * 8)
                    score -= penalty
                    _check_row(checks, "Tipo", f"{ENTITY_LABELS.get(entity, entity)} · {field}", "Alta", "Atenção", f"{invalid:.1%} não reconhecido como data.", penalty)
            if spec.get("dtype") == "number":
                invalid = float(pd.to_numeric(df[field], errors="coerce").isna().mean()) if len(df) else 0
                if invalid > 0.05:
                    penalty = min(4.0, invalid * 8)
                    score -= penalty
                    _check_row(checks, "Tipo", f"{ENTITY_LABELS.get(entity, entity)} · {field}", "Alta", "Atenção", f"{invalid:.1%} não reconhecido como número.", penalty)

    # Governance: targets
    metas = standard.get("metas")
    if metas is None or metas.empty or "indicador" not in metas.columns or "meta" not in metas.columns:
        score -= 4.0
        _check_row(checks, "Governança", "Metas", "Alta", "Atenção", "Metas não carregadas. KPIs sem meta serão tratados como risco de gestão.", 4.0)
    else:
        missing_targets = int(metas["meta"].isna().sum())
        if missing_targets:
            penalty = min(4.0, 0.5 * missing_targets)
            score -= penalty
            _check_row(checks, "Governança", "Metas", "Alta", "Atenção", f"{missing_targets} metas sem valor.", penalty)
        else:
            _check_row(checks, "Governança", "Metas", "Alta", "OK", "Metas carregadas.", 0.0)

    # Product standards & mix linearization
    prod = standard.get("producao")
    std = standard.get("padroes_produto")
    if prod is not None and not prod.empty and "produto" in prod.columns:
        products = set(prod["produto"].dropna().astype(str))
        if len(products) > 1:
            if std is None or std.empty or "produto" not in std.columns:
                score -= 7.0
                _check_row(checks, "Padrões", "Mix multiproduto", "Alta", "Atenção", "Há múltiplos produtos, mas a tabela de padrões não foi carregada; produtividade consolidada ficará limitada.", 7.0)
            else:
                std_products = set(std["produto"].dropna().astype(str))
                missing_products = sorted(products - std_products)
                if missing_products:
                    penalty = min(7.0, 1.0 + 0.5 * len(missing_products))
                    score -= penalty
                    _check_row(checks, "Padrões", "Produtos sem padrão", "Alta", "Atenção", f"{len(missing_products)} produto(s) sem padrão: {', '.join(missing_products[:8])}", penalty)
                else:
                    _check_row(checks, "Padrões", "Mix multiproduto", "Alta", "OK", "Todos os produtos possuem cadastro de padrão.", 0.0)

    # Mapping ambiguity + semantic resolution
    if mapping:
        low = []
        for sh, cols in mapping.get("column_map", {}).items():
            for source, meta in cols.items():
                if meta.get("field") and float(meta.get("confidence", 0)) < 0.70:
                    low.append(f"{sh}.{source}")
        if low:
            penalty = min(4.0, 0.5 * len(low))
            score -= penalty
            _check_row(checks, "Mapeamento", "Confiança", "Média", "Atenção", f"{len(low)} campo(s) com baixa confiança; confirme o DE/PARA.", penalty)

        semantic_records=mapping.get("semantic_resolution",{}).get("report",[])
        unresolved=[r for r in semantic_records if r.get("Status")=="Não resolvido"]
        if unresolved:
            critical_prod=sum(int(r.get("Registros",0)) for r in unresolved if r.get("Entidade")=="producao" and r.get("Dimensão")=="Planta")
            total_unresolved=sum(int(r.get("Registros",0)) for r in unresolved)
            penalty=min(8.0, 5.0 if critical_prod else max(1.0,total_unresolved*0.02))
            score-=penalty
            detail=f"{total_unresolved} registro(s) com dimensão sem evidência suficiente."
            if critical_prod:
                detail+=f" Produção possui {critical_prod} registro(s) sem Planta resolvida."
            _check_row(checks,"Semântica","Entity Resolution","Alta","Atenção",detail,penalty)
        else:
            if semantic_records:
                _check_row(checks,"Semântica","Entity Resolution","Alta","OK","Dimensões semânticas resolvidas sem lacunas relevantes.",0.0)

    score = float(max(0.0, min(100.0, score)))
    if blocking:
        status = "Bloqueado"
    elif score >= 90:
        status = "Excelente"
    elif score >= 80:
        status = "Bom"
    elif score >= 70:
        status = "Atenção"
    else:
        status = "Crítico"

    checks_df = pd.DataFrame(checks)
    if not checks_df.empty:
        checks_df["Penalidade"] = checks_df["Penalidade"].round(1)
    summary = {
        "score": score,
        "status": status,
        "blocking": blocking,
        "critical": int((checks_df.get("Severidade", pd.Series(dtype=str)) == "Crítica").sum()) if not checks_df.empty else 0,
        "warnings": int((checks_df.get("Resultado", pd.Series(dtype=str)) == "Atenção").sum()) if not checks_df.empty else 0,
        "checks": int(len(checks_df)),
    }
    return QualityResult(score=score, status=status, blocking=blocking, checks=checks_df, summary=summary)


def mapping_to_json(mapping: Dict[str, Any], company: str = "", source: str = "") -> bytes:
    obj = dict(mapping)
    obj["company"] = company
    obj["source"] = source
    obj["exported_at"] = datetime.now(timezone.utc).isoformat()
    return json.dumps(obj, ensure_ascii=False, indent=2, default=str).encode("utf-8")


def mapping_from_json(raw: bytes) -> Dict[str, Any]:
    return json.loads(raw.decode("utf-8"))


def data_root(base: Optional[Path] = None) -> Path:
    root = Path(os.getenv("INDUSTRIAL_DATA_ROOT", str(base or (Path.cwd() / ".industrial_data"))))
    root.mkdir(parents=True, exist_ok=True)
    return root


def _write_parquet_duckdb(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if duckdb is None:
        # Development fallback. Production requirements install duckdb.
        df.to_csv(path.with_suffix(".csv"), index=False)
        return
    con = duckdb.connect(database=":memory:")
    try:
        con.register("df_input", df)
        safe_path = str(path).replace("'", "''")
        con.execute(f"COPY df_input TO '{safe_path}' (FORMAT PARQUET, COMPRESSION ZSTD)")
    finally:
        con.close()


def persist_ingestion(
    raw: bytes,
    filename: str,
    company: str,
    source: str,
    mapping: Dict[str, Any],
    standard: Dict[str, pd.DataFrame],
    lineage: List[Dict[str, Any]],
    quality: QualityResult,
    root: Optional[Path] = None,
) -> Dict[str, Any]:
    root = data_root(root)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    digest = workbook_fingerprint(raw)[:10]
    ingestion_id = f"{stamp}_{digest}"
    company_slug, source_slug = safe_slug(company), safe_slug(source)

    raw_dir = root / "raw" / company_slug / source_slug / ingestion_id
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / filename
    raw_path.write_bytes(raw)

    standard_dir = root / "standard" / company_slug / source_slug / ingestion_id
    for entity, df in standard.items():
        _write_parquet_duckdb(df, standard_dir / f"{entity}.parquet")

    mappings_dir = root / "mappings" / company_slug
    mappings_dir.mkdir(parents=True, exist_ok=True)
    mapping_path = mappings_dir / f"{source_slug}.json"
    mapping_path.write_bytes(mapping_to_json(mapping, company, source))

    meta_dir = root / "metadata"
    meta_dir.mkdir(parents=True, exist_ok=True)
    lineage_df = pd.DataFrame(lineage)
    if not lineage_df.empty:
        _write_parquet_duckdb(lineage_df, meta_dir / f"lineage_{ingestion_id}.parquet")

    record = {
        "ingestion_id": ingestion_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "company": company,
        "source": source,
        "filename": filename,
        "file_hash": workbook_fingerprint(raw),
        "rows": int(sum(len(df) for df in standard.values())),
        "entities": list(standard.keys()),
        "quality_score": round(quality.score, 1),
        "quality_status": quality.status,
        "raw_path": str(raw_path),
        "standard_path": str(standard_dir),
        "mapping_path": str(mapping_path),
        "storage_mode": "local_ephemeral_mvp",
        "version": DATA_LAYER_VERSION,
    }
    registry = meta_dir / "ingestions.jsonl"
    with registry.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    semantic_meta={
        "semantic_context":mapping.get("semantic_context",{}),
        "semantic_relationships":mapping.get("semantic_relationships",{}),
        "semantic_resolution":mapping.get("semantic_resolution",{}),
    }
    (meta_dir / f"semantic_{ingestion_id}.json").write_text(
        json.dumps(semantic_meta,ensure_ascii=False,indent=2,default=str),encoding="utf-8"
    )
    # Active pointer for process/app restarts in the MVP environment.
    (meta_dir / "active_ingestion.json").write_text(
        json.dumps(record,ensure_ascii=False,indent=2,default=str),encoding="utf-8"
    )
    return record


def _read_standard_dir(path: Path) -> Dict[str,pd.DataFrame]:
    standard={}
    if not path.exists():
        return standard
    parquet_files=list(path.glob("*.parquet"))
    csv_files=list(path.glob("*.csv"))
    for p in parquet_files:
        try:
            if duckdb is not None:
                con=duckdb.connect(database=":memory:")
                try:
                    safe_path=str(p).replace("'","''")
                    df=con.execute(f"SELECT * FROM read_parquet('{safe_path}')").df()
                finally:
                    con.close()
            else:
                df=pd.read_parquet(p)
            standard[p.stem]=df
        except Exception:
            continue
    for p in csv_files:
        if p.stem in standard:
            continue
        try:
            standard[p.stem]=pd.read_csv(p)
        except Exception:
            continue
    return standard


def load_active_ingestion(root: Optional[Path] = None) -> Tuple[Optional[Dict[str,pd.DataFrame]],Optional[Dict[str,Any]]]:
    """Reload the active Standard layer when the current app process still has its local data directory."""
    root=data_root(root)
    pointer=root / "metadata" / "active_ingestion.json"
    if not pointer.exists():
        return None,None
    try:
        record=json.loads(pointer.read_text(encoding="utf-8"))
        standard=_read_standard_dir(Path(record.get("standard_path","")))
        if standard:
            return standard,record
    except Exception:
        pass
    return None,None


def clear_active_ingestion(root: Optional[Path] = None) -> None:
    root=data_root(root)
    p=root / "metadata" / "active_ingestion.json"
    try:
        if p.exists():
            p.unlink()
    except Exception:
        pass


def list_ingestions(root: Optional[Path] = None) -> pd.DataFrame:
    root = data_root(root)
    registry = root / "metadata" / "ingestions.jsonl"
    if not registry.exists():
        return pd.DataFrame(columns=["timestamp", "company", "source", "filename", "rows", "quality_score", "quality_status", "ingestion_id"])
    rows = []
    for line in registry.read_text(encoding="utf-8").splitlines():
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return pd.DataFrame(rows)


def list_saved_mappings(root: Optional[Path] = None) -> pd.DataFrame:
    root = data_root(root)
    base = root / "mappings"
    rows = []
    if not base.exists():
        return pd.DataFrame(columns=["company", "source", "path", "updated_at"])
    for p in base.rglob("*.json"):
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
            rows.append({
                "company": obj.get("company", p.parent.name),
                "source": obj.get("source", p.stem),
                "path": str(p),
                "updated_at": datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec="seconds"),
            })
        except Exception:
            continue
    return pd.DataFrame(rows)


def load_saved_mapping(company: str, source: str, root: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    root = data_root(root)
    p = root / "mappings" / safe_slug(company) / f"{safe_slug(source)}.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def build_semantic_catalog(standard: Dict[str, pd.DataFrame], lineage: List[Dict[str, Any]]) -> pd.DataFrame:
    rows = []
    lineage_df = pd.DataFrame(lineage)
    for entity, df in standard.items():
        for field in df.columns:
            match = lineage_df[(lineage_df["entidade"] == entity) & (lineage_df["campo_padrao"] == field)] if not lineage_df.empty else pd.DataFrame()
            rows.append({
                "Entidade": ENTITY_LABELS.get(entity, entity),
                "Campo padrão": field,
                "Registros": len(df),
                "Origem": ", ".join(sorted(match["aba_origem"].astype(str).unique())) if not match.empty else "—",
                "Coluna origem": ", ".join(sorted(match["coluna_origem"].astype(str).unique())) if not match.empty else "—",
            })
    return pd.DataFrame(rows)
