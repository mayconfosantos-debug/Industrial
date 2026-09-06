
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import unicodedata
import re

import numpy as np
import pandas as pd

ANALYTICS_VERSION = "0.6.4"

DIMENSION_ALIASES = {
    "grupo": ["grupo", "grupo_empresa", "grupo_industrial", "business_group"],
    "planta": ["fabrica", "planta", "unidade", "site", "factory"],
    "linha": ["linha", "line", "workcenter", "centro_trabalho"],
    "produto": ["produto", "sku", "product", "material", "item"],
}
DATE_FIELDS = ["data", "competencia", "date", "periodo"]


def _norm(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))
    return "_".join(filter(None, re.split(r"[^a-z0-9]+", text)))


def _find_column(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    if df is None or df.empty:
        return None
    by_norm = {_norm(c): c for c in df.columns}
    for c in candidates:
        if _norm(c) in by_norm:
            return by_norm[_norm(c)]
    return None


def _safe_div(a: float, b: float) -> float:
    try:
        return float(a / b) if b not in (0, 0.0) and pd.notna(b) else 0.0
    except Exception:
        return 0.0


def filter_options(data: Optional[Dict[str, pd.DataFrame]]) -> Dict[str, Any]:
    """Collect real filter options from all canonical entities."""
    out: Dict[str, Any] = {
        "grupo": [],
        "planta": [],
        "linha": [],
        "produto": [],
        "date_min": None,
        "date_max": None,
    }
    if not data:
        return out

    dims = {k: set() for k in ["grupo", "planta", "linha", "produto"]}
    dates: List[pd.Timestamp] = []

    fact_entities={"producao","qualidade","manutencao","pessoas","custos","dre_gerencial"}
    for entity, df in data.items():
        if entity not in fact_entities:
            continue
        if df is None or not isinstance(df, pd.DataFrame) or df.empty:
            continue
        for dim, aliases in DIMENSION_ALIASES.items():
            col = _find_column(df, aliases)
            if col:
                vals = df[col].dropna().astype(str).str.strip()
                dims[dim].update(v for v in vals if v and v.lower() not in {"nan", "none", "<na>"})
        dcol = _find_column(df, DATE_FIELDS)
        if dcol:
            ds = pd.to_datetime(df[dcol], errors="coerce").dropna()
            if not ds.empty:
                dates.extend([ds.min(), ds.max()])

    for dim in dims:
        out[dim] = sorted(dims[dim], key=lambda x: _norm(x))
    if dates:
        out["date_min"] = min(dates).normalize()
        out["date_max"] = max(dates).normalize()
    return out


def apply_filters(
    data: Optional[Dict[str, pd.DataFrame]],
    filters: Optional[Dict[str, Any]] = None,
) -> Tuple[Optional[Dict[str, pd.DataFrame]], Dict[str, Any]]:
    """
    Apply Group / Plant / Period / Line / Product filters to every canonical
    entity that carries the dimension. Returns filtered data plus coverage metadata.

    If a detailed line/product filter is active but DRE_Gerencial does not have that
    dimension, the managerial DRE is removed so the app falls back to detailed Custos
    rather than mixing plant-level finance with line-level operations.
    """
    if not data:
        return data, {"active": False, "coverage": pd.DataFrame(), "warnings": [], "empty": False}

    filters = filters or {}
    start = filters.get("start")
    end = filters.get("end")
    active_dims = {
        "grupo": filters.get("grupo"),
        "planta": filters.get("planta"),
        "linha": filters.get("linha"),
        "produto": filters.get("produto"),
    }
    active_dims = {k: v for k, v in active_dims.items() if v not in (None, "", "Todos", "Todas")}

    result: Dict[str, pd.DataFrame] = {}
    coverage_rows: List[Dict[str, Any]] = []
    warnings: List[str] = []

    for entity, original in data.items():
        if original is None or not isinstance(original, pd.DataFrame):
            result[entity] = original
            continue
        df = original.copy()
        applied = []
        missing = []

        dcol = _find_column(df, DATE_FIELDS)
        if (start is not None or end is not None):
            if dcol:
                dser = pd.to_datetime(df[dcol], errors="coerce")
                mask = pd.Series(True, index=df.index)
                if start is not None:
                    mask &= dser >= pd.Timestamp(start)
                if end is not None:
                    # Include the whole selected final date.
                    mask &= dser < (pd.Timestamp(end) + pd.Timedelta(days=1))
                df = df.loc[mask].copy()
                applied.append("período")
            else:
                missing.append("período")

        for dim, value in active_dims.items():
            col = _find_column(df, DIMENSION_ALIASES[dim])
            if col:
                df = df.loc[df[col].astype(str).str.strip() == str(value).strip()].copy()
                applied.append(dim)
            else:
                missing.append(dim)

        result[entity] = df.reset_index(drop=True)
        coverage_rows.append({
            "Entidade": entity,
            "Linhas origem": int(len(original)),
            "Linhas filtradas": int(len(df)),
            "Filtros aplicados": ", ".join(applied) if applied else "—",
            "Dimensões ausentes": ", ".join(missing) if missing else "—",
        })

    # Prevent financial dimensional mismatch.
    # If DRE is aggregated and a line/product filter is active, allocate the managerial
    # DRE to the selected slice using detailed Custos/Produção shares. This keeps totals
    # reconciled while making the allocation explicit.
    dre = result.get("dre_gerencial")
    original_dre = data.get("dre_gerencial")
    financial_allocation = False

    if (
        original_dre is not None and isinstance(original_dre, pd.DataFrame) and not original_dre.empty
        and isinstance(dre, pd.DataFrame) and dre.empty
    ):
        result.pop("dre_gerencial", None)
        warnings.append(
            "A DRE Gerencial não possui registros para o recorte selecionado. "
            "O resultado financeiro usa a base detalhada de Custos neste recorte para evitar cruzar períodos/unidades diferentes."
        )
        dre = None

    if (
        original_dre is not None and isinstance(original_dre, pd.DataFrame) and not original_dre.empty
        and isinstance(dre, pd.DataFrame) and not dre.empty
    ):
        missing_detail_dims = [
            dim for dim in ["linha","produto"]
            if dim in active_dims and _find_column(original_dre, DIMENSION_ALIASES[dim]) is None
        ]
        if missing_detail_dims:
            selected_costs = result.get("custos")
            base_costs = data.get("custos")

            def _filter_base_costs(df):
                if df is None or not isinstance(df,pd.DataFrame) or df.empty:
                    return pd.DataFrame()
                out=df.copy()
                dcol=_find_column(out,DATE_FIELDS)
                if dcol and (start is not None or end is not None):
                    ds=pd.to_datetime(out[dcol],errors="coerce")
                    mask=pd.Series(True,index=out.index)
                    if start is not None:
                        mask &= ds >= pd.Timestamp(start)
                    if end is not None:
                        mask &= ds < (pd.Timestamp(end)+pd.Timedelta(days=1))
                    out=out.loc[mask].copy()
                for dim in ["grupo","planta"]:
                    value=active_dims.get(dim)
                    if value is not None:
                        col=_find_column(out,DIMENSION_ALIASES[dim])
                        if col:
                            out=out.loc[out[col].astype(str).str.strip()==str(value).strip()].copy()
                return out

            base_costs=_filter_base_costs(base_costs)

            def _sum(df,col):
                if df is None or not isinstance(df,pd.DataFrame) or df.empty or col not in df.columns:
                    return 0.0
                return float(pd.to_numeric(df[col],errors="coerce").fillna(0).sum())

            def _ratio(col, fallback):
                den=_sum(base_costs,col)
                num=_sum(selected_costs,col)
                return max(0.0,min(1.0,_safe_div(num,den))) if den>0 else fallback

            revenue_share=_ratio("receita",0.0)
            if revenue_share<=0:
                # fall back to production volume share
                base_prod=data.get("producao")
                selected_prod=result.get("producao")
                if isinstance(base_prod,pd.DataFrame) and not base_prod.empty and "realizado" in base_prod.columns:
                    bp=_filter_base_costs(base_prod)
                    den=_sum(bp,"realizado")
                    num=_sum(selected_prod,"realizado")
                    revenue_share=max(0.0,min(1.0,_safe_div(num,den))) if den>0 else 0.0
            if revenue_share<=0:
                revenue_share=1.0

            allocation_map={
                "receita_bruta":revenue_share,
                "impostos_deducoes":revenue_share,
                "receita_liquida":revenue_share,
                "insumos_mp":_ratio("custo_mp",revenue_share),
                "mod":_ratio("custo_mod",revenue_share),
                "ggf_frete":_ratio("custo_frete",revenue_share),
                "ggf_energia":_ratio("custo_energia",revenue_share),
                "ggf_manutencao":_ratio("custo_manutencao",revenue_share),
                "ggf_contratos_servicos":revenue_share,
                "ggf_outros":_ratio("ggf_outros",revenue_share),
                "custos_fixos_industriais":revenue_share,
                "desp_administrativas":revenue_share,
                "desp_comerciais":revenue_share,
                "desp_logisticas":revenue_share,
                "outros_opex":revenue_share,
                "volume_vendido":revenue_share,
                "consumo_mp_kg":_ratio("custo_mp",revenue_share),
                "preco_medio_mp_kg":1.0,
                "consumo_energia_kwh":_ratio("custo_energia",revenue_share),
                "estoque_dias":1.0,
                "prazo_fornecedor_dias":1.0,
                "prazo_cliente_dias":1.0,
            }
            allocated=dre.copy()
            for col,factor in allocation_map.items():
                if col in allocated.columns and factor != 1.0:
                    allocated[col]=pd.to_numeric(allocated[col],errors="coerce").fillna(0)*factor
            allocated["_alocacao_gerencial"]=True
            allocated["_base_alocacao"]=f"participação do recorte em Custos/Produção ({revenue_share:.1%})"
            result["dre_gerencial"]=allocated
            financial_allocation=True
            warnings.append(
                "A DRE Gerencial não possui " + " e ".join(missing_detail_dims) + ". "
                f"Para este drill-down, custos fixos e despesas foram alocados gerencialmente pelo peso do recorte "
                f"({revenue_share:.1%} da base detalhada). O recorte é analítico, não uma DRE contábil legal."
            )

    prod = result.get("producao")
    empty = bool(prod is not None and isinstance(prod, pd.DataFrame) and prod.empty)
    return result, {
        "active": bool(active_dims or start is not None or end is not None),
        "coverage": pd.DataFrame(coverage_rows),
        "warnings": warnings,
        "empty": empty,
        "financial_allocation": financial_allocation,
        "filters": {**active_dims, "start": start, "end": end},
    }


def filter_context_label(filters: Optional[Dict[str, Any]]) -> str:
    if not filters:
        return "Todos os dados"
    parts = []
    for key, label in [("grupo", "Grupo"), ("planta", "Planta"), ("linha", "Linha"), ("produto", "Produto")]:
        val = filters.get(key)
        if val not in (None, "", "Todos", "Todas"):
            parts.append(f"{label}: {val}")
    if filters.get("start") is not None and filters.get("end") is not None:
        a = pd.Timestamp(filters["start"]).strftime("%d/%m/%Y")
        b = pd.Timestamp(filters["end"]).strftime("%d/%m/%Y")
        parts.append(f"{a}–{b}")
    return " · ".join(parts) if parts else "Todos os dados"


def machine_drilldown(
    data: Optional[Dict[str, pd.DataFrame]],
    D: Dict[str, Any],
    line: Optional[str] = None,
) -> pd.DataFrame:
    """Machine-level downtime view for the selected line."""
    if not data or "manutencao" not in data:
        return pd.DataFrame(columns=["Máquina","Paradas h","Eventos","MTTR min","Causa dominante","Impacto R$"])
    m = data["manutencao"].copy()
    if m.empty or "maquina" not in m.columns or "duracao_horas" not in m.columns:
        return pd.DataFrame(columns=["Máquina","Paradas h","Eventos","MTTR min","Causa dominante","Impacto R$"])
    m["duracao_horas"] = pd.to_numeric(m["duracao_horas"], errors="coerce").fillna(0)
    if line and "linha" in m.columns:
        m = m[m["linha"].astype(str) == str(line)].copy()
    if m.empty:
        return pd.DataFrame(columns=["Máquina","Paradas h","Eventos","MTTR min","Causa dominante","Impacto R$"])

    margin_unit = _safe_div(float(D.get("revenue",0)) * float(D.get("margin",0)), max(1.0,float(D.get("actual",1))))
    units_h = _safe_div(float(D.get("actual",0)), max(1.0,float(D.get("actual_hh",1))))

    rows = []
    for machine, g in m.groupby("maquina", dropna=False):
        hours = float(g["duracao_horas"].sum())
        events = int(len(g))
        mttr = float(g["duracao_horas"].mean()*60) if events else 0.0
        if "causa" in g.columns and g["causa"].notna().any():
            cause = str(g.groupby("causa")["duracao_horas"].sum().sort_values(ascending=False).index[0])
        else:
            cause = "Não classificada"
        impact = hours * units_h * margin_unit
        rows.append([str(machine), hours, events, mttr, cause, impact])
    out = pd.DataFrame(rows, columns=["Máquina","Paradas h","Eventos","MTTR min","Causa dominante","Impacto R$"])
    return out.sort_values(["Paradas h","Impacto R$"], ascending=False).reset_index(drop=True)


def cause_drilldown(
    data: Optional[Dict[str, pd.DataFrame]],
    D: Dict[str, Any],
    line: Optional[str] = None,
    machine: Optional[str] = None,
) -> pd.DataFrame:
    """Cause-level downtime view for selected line/machine."""
    if not data or "manutencao" not in data:
        return pd.DataFrame(columns=["Causa","Paradas h","Eventos","% das horas","Impacto R$"])
    m = data["manutencao"].copy()
    if m.empty or "causa" not in m.columns or "duracao_horas" not in m.columns:
        return pd.DataFrame(columns=["Causa","Paradas h","Eventos","% das horas","Impacto R$"])
    m["duracao_horas"] = pd.to_numeric(m["duracao_horas"], errors="coerce").fillna(0)
    if line and "linha" in m.columns:
        m = m[m["linha"].astype(str) == str(line)].copy()
    if machine and "maquina" in m.columns:
        m = m[m["maquina"].astype(str) == str(machine)].copy()
    if m.empty:
        return pd.DataFrame(columns=["Causa","Paradas h","Eventos","% das horas","Impacto R$"])

    total_h = max(1e-9, float(m["duracao_horas"].sum()))
    margin_unit = _safe_div(float(D.get("revenue",0)) * float(D.get("margin",0)), max(1.0,float(D.get("actual",1))))
    units_h = _safe_div(float(D.get("actual",0)), max(1.0,float(D.get("actual_hh",1))))

    rows = []
    for cause, g in m.groupby("causa", dropna=False):
        hours = float(g["duracao_horas"].sum())
        rows.append([
            str(cause), hours, int(len(g)), hours/total_h, hours*units_h*margin_unit
        ])
    out = pd.DataFrame(rows, columns=["Causa","Paradas h","Eventos","% das horas","Impacto R$"])
    return out.sort_values(["Paradas h","Impacto R$"], ascending=False).reset_index(drop=True)


def quality_product_drilldown(
    data: Optional[Dict[str, pd.DataFrame]],
    line: Optional[str] = None,
) -> pd.DataFrame:
    if not data or "qualidade" not in data:
        return pd.DataFrame(columns=["Produto","Produzido","Refugo","Taxa Refugo","Retrabalho"])
    q = data["qualidade"].copy()
    if q.empty or "produto" not in q.columns:
        return pd.DataFrame(columns=["Produto","Produzido","Refugo","Taxa Refugo","Retrabalho"])
    if line and "linha" in q.columns:
        q = q[q["linha"].astype(str) == str(line)].copy()
    for col in ["produzido","refugo","retrabalho"]:
        if col not in q.columns:
            q[col]=0
        q[col]=pd.to_numeric(q[col], errors="coerce").fillna(0)
    rows=[]
    for product,g in q.groupby("produto",dropna=False):
        produced=float(g["produzido"].sum())
        scrap=float(g["refugo"].sum())
        rework=float(g["retrabalho"].sum())
        rows.append([str(product),produced,scrap,_safe_div(scrap,produced),rework])
    return pd.DataFrame(rows,columns=["Produto","Produzido","Refugo","Taxa Refugo","Retrabalho"]).sort_values("Taxa Refugo",ascending=False)


def _target(data: Optional[Dict[str,pd.DataFrame]], names: List[str]) -> float:
    if not data:
        return np.nan
    m=data.get("metas")
    if m is None or m.empty or "indicador" not in m.columns or "meta" not in m.columns:
        return np.nan
    targets={_norm(x) for x in names}
    for _,r in m.iterrows():
        if _norm(r.get("indicador","")) in targets:
            v=pd.to_numeric(r.get("meta"),errors="coerce")
            return float(v) if pd.notna(v) else np.nan
    return np.nan


def _impact(D: Dict[str,Any], label: str) -> float:
    imp=D.get("impacts")
    if imp is None or not isinstance(imp,pd.DataFrame) or imp.empty:
        return 0.0
    hit=imp[imp["Impacto"].astype(str).map(_norm)==_norm(label)]
    return float(hit.iloc[0]["R$"]) if not hit.empty else 0.0


def _diag_impact(D: Dict[str,Any], lever: str) -> float:
    diag=D.get("diagnostic")
    if diag is None or not isinstance(diag,pd.DataFrame) or diag.empty:
        return 0.0
    hit=diag[diag["Alavanca"].astype(str).map(_norm)==_norm(lever)]
    return float(hit.iloc[0]["Impacto_R$"]) if not hit.empty else 0.0


def performance_engine(
    data: Optional[Dict[str,pd.DataFrame]],
    D: Dict[str,Any],
    filter_meta: Optional[Dict[str,Any]] = None,
) -> pd.DataFrame:
    """
    Deterministic diagnostic chain:
    KPI -> deviation -> location -> evidence/cause -> financial impact -> lever -> action.
    It only asserts causes when the source contains evidence.
    """
    rows: List[List[Any]] = []
    lp=D.get("line_perf",pd.DataFrame())
    causes_all=D.get("causes",pd.DataFrame())

    coverage=(filter_meta or {}).get("coverage")
    active_filter_dims=set((filter_meta or {}).get("filters",{}).keys()) if filter_meta else set()

    def source_respects(entity: str) -> Tuple[bool,str]:
        if not isinstance(coverage,pd.DataFrame) or coverage.empty:
            return True,""
        hit=coverage[coverage["Entidade"].astype(str)==entity]
        if hit.empty:
            return True,""
        missing=str(hit.iloc[0].get("Dimensões ausentes","—"))
        if missing in {"—","","nan"}:
            return True,""
        active=(filter_meta or {}).get("filters",{})
        relevant=[d for d in ["grupo","planta","linha","produto"] if active.get(d) not in (None,"","Todos","Todas")]
        violated=[d for d in relevant if d in missing]
        return (len(violated)==0, ", ".join(violated))

    worst_line = None
    if isinstance(lp,pd.DataFrame) and not lp.empty:
        worst_line=str(lp.sort_values("OEE").iloc[0]["Linha"])

    def top_maintenance_cause(line: Optional[str]) -> Tuple[str,float,str]:
        respects,missing_dims=source_respects("manutencao")
        if not respects:
            return "Causa não atribuída",0.0,f"Manutenção sem granularidade para: {missing_dims}"
        if not data or "manutencao" not in data:
            return "Causa não disponível",0.0,"Sem dados de manutenção"
        m=data["manutencao"].copy()
        if m.empty or "causa" not in m.columns or "duracao_horas" not in m.columns:
            return "Causa não disponível",0.0,"Sem causa estruturada"
        if line and "linha" in m.columns:
            m=m[m["linha"].astype(str)==str(line)]
        if m.empty:
            return "Causa não disponível",0.0,"Sem registros no recorte"
        m["duracao_horas"]=pd.to_numeric(m["duracao_horas"],errors="coerce").fillna(0)
        g=m.groupby("causa")["duracao_horas"].sum().sort_values(ascending=False)
        if g.empty:
            return "Causa não disponível",0.0,"Sem causa estruturada"
        return str(g.index[0]),float(g.iloc[0]),f"{float(g.iloc[0]):.1f} h de parada"

    # 1) Production attainment
    attainment=float(D.get("attainment",0))
    if attainment < 1:
        if isinstance(lp,pd.DataFrame) and not lp.empty:
            wr=lp.sort_values("Gap Produção").iloc[0]
            local=str(wr["Linha"])
            local_evidence=f"Gap {float(wr['Gap Produção']):,.0f} un; OEE {float(wr['OEE']):.1%}".replace(",",".")
        else:
            local="Operação"
            local_evidence=f"Atingimento {attainment:.1%}"
        cause,hours,cause_ev=top_maintenance_cause(local)
        impact=_impact(D,"Gap de volume")
        rows.append([
            "Produção",f"{attainment-1:+.1%}",local,cause,
            f"{local_evidence}; {cause_ev}",impact,
            "Disponibilidade","Atacar a principal restrição da linha e recuperar volume vendável.",
            "Alta" if not cause.startswith("Causa não") else "Média","Produção + Manutenção + DRE"
        ])

    # 2) OEE
    oee=float(D.get("oee",0))
    target_oee=float(D.get("target_oee",np.nan))
    if pd.notna(target_oee) and oee < target_oee:
        local=worst_line or "Operação"
        cause,hours,cause_ev=top_maintenance_cause(local)
        impact=max(_diag_impact(D,"Disponibilidade"),_diag_impact(D,"Performance"))
        rows.append([
            "OEE",f"{(oee-target_oee)*100:+.1f} pp",local,cause,
            f"OEE {oee:.1%} vs meta {target_oee:.1%}; {cause_ev}",impact,
            "Disponibilidade","Priorizar disponibilidade/performance na linha crítica e remover a causa dominante.",
            "Alta" if not cause.startswith("Causa não") else "Média","Produção + Manutenção"
        ])

    # 3) Scrap
    scrap=float(D.get("scrap",0))
    target_scrap=float(D.get("target_scrap",np.nan))
    if pd.notna(target_scrap) and scrap > target_scrap:
        local="Operação"
        evidence=f"Refugo {scrap:.1%} vs meta {target_scrap:.1%}"
        if isinstance(lp,pd.DataFrame) and not lp.empty and "Refugo" in lp.columns:
            wr=lp.sort_values("Refugo",ascending=False).iloc[0]
            local=str(wr["Linha"])
            evidence+=f"; maior taxa em {local}: {float(wr['Refugo']):.1%}"
        qprod=quality_product_drilldown(data,local if local!="Operação" else None)
        cause="Produto/causa de qualidade não estruturada"
        if not qprod.empty:
            p=qprod.iloc[0]
            cause=f"Refugo concentrado no produto {p['Produto']}"
            evidence+=f"; produto {p['Produto']} com {float(p['Taxa Refugo']):.1%}"
        rows.append([
            "Refugo",f"{(scrap-target_scrap)*100:+.1f} pp",local,cause,evidence,
            _impact(D,"Refugo"),"Refugo",
            "Abrir Pareto de refugo por produto/causa e estabilizar parâmetros do processo.",
            "Média","Qualidade + Custos"
        ])

    # 4) Labor efficiency
    labor=float(D.get("labor_efficiency",np.nan))
    labor_target=_target(data,["Eficiência MOD","Eficiencia MOD"])
    people_respects,people_missing=source_respects("pessoas")
    if people_respects and pd.notna(labor) and pd.notna(labor_target) and labor < labor_target:
        local="Operação"
        if data and "pessoas" in data:
            pe=data["pessoas"].copy()
            if not pe.empty and "linha" in pe.columns and "horas_extras" in pe.columns:
                pe["horas_extras"]=pd.to_numeric(pe["horas_extras"],errors="coerce").fillna(0)
                by=pe.groupby("linha")["horas_extras"].sum().sort_values(ascending=False)
                if not by.empty:
                    local=str(by.index[0])
        rows.append([
            "Eficiência MOD",f"{(labor-labor_target)*100:+.1f} pp",local,
            "HH reais acima das HH padrão ganhas",
            f"Eficiência {labor:.1%} vs meta {labor_target:.1%}; produtividade mix-linearizada",
            _impact(D,"Eficiência MOD"),"Eficiência MOD",
            "Rebalancear operação por HH padrão, produto e turno; atacar esperas e desequilíbrio.",
            "Alta","Pessoas + Padrões de Produto + Custos"
        ])

    # 5) Overtime
    overtime=float(D.get("overtime",0))
    overtime_target=_target(data,["Horas extras"])
    if people_respects and pd.notna(overtime_target) and overtime > overtime_target:
        local="Operação"
        evidence=f"{overtime:,.0f} h vs meta {overtime_target:,.0f} h".replace(",",".")
        if data and "pessoas" in data:
            pe=data["pessoas"].copy()
            if not pe.empty and "linha" in pe.columns and "horas_extras" in pe.columns:
                pe["horas_extras"]=pd.to_numeric(pe["horas_extras"],errors="coerce").fillna(0)
                by=pe.groupby("linha")["horas_extras"].sum().sort_values(ascending=False)
                if not by.empty:
                    local=str(by.index[0])
                    evidence+=f"; {local}: {float(by.iloc[0]):,.0f} h".replace(",",".")
        rows.append([
            "Horas extras",f"{overtime-overtime_target:+,.0f} h".replace(",","."),
            local,"Carga/escala acima do padrão",evidence,_impact(D,"Horas extras"),
            "Horas extras","Revisar escala, gargalos e relação hora extra × volume incremental.",
            "Alta","Pessoas + Custos"
        ])

    # 6) Cost / unit
    cost=float(D.get("cost_unit",0))
    cost_target=_target(data,["Custo/unidade","Custo por unidade"])
    if pd.notna(cost_target) and cost_target>0 and cost > cost_target:
        rows.append([
            "Custo/unidade",f"{_safe_div(cost,cost_target)-1:+.1%}","DRE / Custos",
            "Estrutura de custo acima da referência",
            f"Custo/un {cost:.2f} vs meta {cost_target:.2f}",_impact(D,"Custo / consumo"),
            "Consumo MP","Abrir custos por linha/produto e atacar os maiores desvios de consumo e GGF.",
            "Média","Custos + DRE Gerencial"
        ])

    # 7) Industrial margin
    margin=float(D.get("margin",0))
    margin_target=_target(data,["Margem","Margem Industrial","Margem Contribuição"])
    if pd.notna(margin_target) and margin < margin_target:
        impact=max(0.0,(margin_target-margin)*float(D.get("revenue",0)))
        top_causes=", ".join([str(x) for x in (pd.DataFrame(rows)["Alavanca"].head(3).tolist() if rows else [])])
        rows.append([
            "Margem Industrial",f"{(margin-margin_target)*100:+.1f} pp","DRE Gerencial",
            top_causes or "Drivers operacionais e de custo",
            f"Margem {margin:.1%} vs meta {margin_target:.1%}",impact,
            "Portfólio de alavancas","Atacar primeiro as alavancas operacionais/custos já evidenciadas; não somar este gap como impacto adicional.",
            "Média","DRE Gerencial + Performance Engine"
        ])

    cols=["KPI","Desvio","Local","Causa / hipótese","Evidência","Impacto_R$","Alavanca","Ação recomendada","Confiança","Fonte"]
    out=pd.DataFrame(rows,columns=cols)
    if not out.empty:
        out["Prioridade_Score"]=out["Impacto_R$"].abs()
        out=out.sort_values("Prioridade_Score",ascending=False).drop(columns=["Prioridade_Score"]).reset_index(drop=True)
    return out
