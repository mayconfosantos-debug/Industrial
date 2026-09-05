
import pandas as pd
import numpy as np

def get_demo():
    months = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago"]
    perf = pd.DataFrame({
        "Mês": months,
        "Produção": [39200,40100,41800,40400,40900,40700,42100,41250],
        "Meta Produção": [45000,45500,46000,46500,47000,47000,47500,48000],
        "OEE": [0.64,0.68,0.73,0.66,0.67,0.66,0.70,0.714],
        "Meta OEE": [0.78]*8,
        "Custo/Un": [17.1,17.3,17.6,17.8,18.0,18.1,18.2,18.42],
        "Margem": [0.312,0.307,0.301,0.294,0.288,0.284,0.281,0.278],
    })

    kpis = [
        {"indicador":"Produção","mes":"41.250 un","meta":"45.000","desvio":-0.083,"desvio_txt":"-8,3%","tend":"↓"},
        {"indicador":"OEE","mes":"71,4%","meta":"78%","desvio":-0.0846,"desvio_txt":"-6,6 pp","tend":"↓"},
        {"indicador":"Produtividade","mes":"18,2 un/h","meta":"19,5","desvio":-0.067,"desvio_txt":"-6,7%","tend":"→"},
        {"indicador":"Refugo","mes":"3,8%","meta":"2,5%","desvio":-0.52,"desvio_txt":"+1,3 pp","tend":"↑"},
        {"indicador":"OTIF","mes":"89%","meta":"95%","desvio":-0.063,"desvio_txt":"-6 pp","tend":"↓"},
        {"indicador":"Custo/unidade","mes":"R$ 18,42","meta":"R$ 17,10","desvio":-0.077,"desvio_txt":"+7,7%","tend":"↑"},
        {"indicador":"Horas extras","mes":"1.280 h","meta":"900 h","desvio":-0.422,"desvio_txt":"+42%","tend":"↑"},
        {"indicador":"Margem contribuição","mes":"27,8%","meta":"31%","desvio":-0.103,"desvio_txt":"-3,2 pp","tend":"↓"},
    ]

    cards = [
        {"label":"Receita Líquida","value":"R$ 12,4 mi","delta":-0.068,"delta_txt":"-6,8% vs. meta"},
        {"label":"Margem de Contribuição","value":"27,8%","delta":-0.103,"delta_txt":"-3,2 pp vs. meta"},
        {"label":"EBITDA Industrial","value":"R$ 1,9 mi","delta":-0.208,"delta_txt":"-20,8% vs. meta"},
        {"label":"Produção","value":"41.250 un","delta":-0.083,"delta_txt":"-8,3% vs. meta"},
        {"label":"OEE","value":"71,4%","delta":-0.0846,"delta_txt":"-6,6 pp vs. meta"},
        {"label":"Custo por Unidade","value":"R$ 18,42","delta":-0.077,"delta_txt":"+7,7% vs. meta"},
    ]

    dre_impacts = pd.DataFrame({
        "Impacto": ["Menor volume produzido","Aumento de refugo","Horas extras","Manutenção corretiva","Maior consumo de MP"],
        "R$ mil": [220,110,95,75,48]
    })

    levers = pd.DataFrame({
        "Alavanca":["Disponibilidade (Linha 3)","Redução de refugo","Otimização de setup","Redução de horas extras","Consumo específico de MP"],
        "Gap Atual":["-12,4%","+1,3 pp","+18 h","+42%","+4%"],
        "Impacto Potencial":["R$ 312 mil","R$ 214 mil","R$ 96 mil","R$ 88 mil","R$ 72 mil"],
        "Prioridade":["Alta","Alta","Média","Média","Baixa"]
    })

    alerts = [
        ("crítico","OEE da Linha 3 18% abaixo da meta","Impacto estimado: R$ 312 mil na margem"),
        ("crítico","Refugo 1,3 pp acima da meta","Impacto estimado: R$ 214 mil"),
        ("atenção","Horas extras 42% acima da meta","Impacto estimado: R$ 95 mil"),
        ("atenção","Custo por unidade 7,7% acima da meta","Revisar consumo de matéria-prima"),
        ("info","OTIF abaixo de 90% pelo segundo mês","Risco de perda de pedidos e receita"),
    ]

    line_perf = pd.DataFrame({
        "Linha":["Linha 1","Linha 2","Linha 3","Linha 4"],
        "OEE":[0.81,0.76,0.64,0.74],
        "Disponibilidade":[0.86,0.82,0.69,0.80],
        "Performance":[0.96,0.94,0.95,0.93],
        "Qualidade":[0.98,0.985,0.975,0.99],
        "Refugo":[0.022,0.026,0.041,0.019],
        "Gap Produção":[-1200,-2100,-7200,-1800],
        "Paradas h":[18,31,79,25]
    })

    causes = pd.DataFrame({
        "Causa":["Falha mecânica","Setup","Falha elétrica","Falta de material","Microparadas","Qualidade"],
        "Horas":[58,41,29,22,18,12],
        "Impacto R$ mil":[164,96,82,61,45,39]
    })

    dre = pd.DataFrame({
        "Linha":["Receita Líquida","(-) Custos Variáveis","Margem de Contribuição","(-) Custos Fixos","EBITDA Industrial"],
        "Realizado":[12.40,-8.95,3.45,-1.55,1.90],
        "Meta":[13.30,-9.18,4.12,-1.72,2.40]
    })

    costs = pd.DataFrame({
        "Categoria":["Matéria-prima","Mão de obra direta","Energia variável","Fretes","Manutenção","Estrutura fabril","Supervisão","Depreciação"],
        "Tipo":["Variável","Variável","Variável","Variável","Fixo","Fixo","Fixo","Fixo"],
        "Realizado R$ mil":[5200,1680,730,620,510,430,370,240],
        "Orçamento R$ mil":[4950,1550,680,590,440,410,340,230]
    })

    actions = pd.DataFrame({
        "Prioridade":["Alta","Alta","Média","Média"],
        "Problema":["Disponibilidade Linha 3","Refugo Produto A","Horas extras","Setup Linha 2"],
        "Ação":["Plano de confiabilidade MX-04","Revisar parâmetros de processo","Redimensionar turnos","SMED em família B"],
        "Responsável":["Ger. Manutenção","Ger. Qualidade","Ger. Produção","Eng. Processos"],
        "Prazo":["10/09/2026","12/09/2026","15/09/2026","18/09/2026"],
        "Impacto":["R$ 312 mil","R$ 214 mil","R$ 88 mil","R$ 96 mil"],
        "Status":["Em andamento","Não iniciado","Em andamento","Planejado"]
    })

    return {
        "perf": perf, "kpis": kpis, "cards": cards, "dre_impacts": dre_impacts,
        "levers": levers, "alerts": alerts, "line_perf": line_perf,
        "causes": causes, "dre": dre, "costs": costs, "actions": actions
    }
