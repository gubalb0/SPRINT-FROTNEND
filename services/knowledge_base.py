"""
BASE DE CONHECIMENTO DO ASSISTENTE (Sprint 4) — camada Gold, versão 1.3.0.

ATENÇÃO: os trechos abaixo são RESUMOS SIMULADOS escritos pelo grupo para o
protótipo. Eles NÃO reproduzem o texto dos manuais dos fabricantes; os
identificadores de documento (doc_id) apenas indicam a qual tipo de documento
o trecho corresponderia na base real indexada.

Cada trecho carrega os metadados exigidos pelo QG-1 (seção 7.1 da documentação):
doc_id, doc_version, secao, access_class, vigente. Trechos sem access_class não
podem ser indexados, porque não seriam filtráveis por perfil.
"""

KB_VERSION = "1.3.0"

CHUNKS = [
    {
        "chunk_id": "WEG-W21-MIM-v3.2-c07",
        "doc_id": "DOC-WEG-W21-MIM", "doc_version": "3.2", "vigente": True,
        "titulo": "Manual de instalação e manutenção — motores WEG W21",
        "secao": "Manutenção de mancais e rolamentos",
        "access_class": "kb_manual_fabricante",
        "recomendacao": "TROCA_ROLAMENTO",
        "keywords": {"weg", "rolamento", "mancal", "vibracao", "ruido", "aquecimento", "temperatura", "desgaste", "falha", "substituir", "trocar"},
        "texto": ("Vibração crescente acompanhada de aquecimento do mancal indica desgaste do rolamento. "
                  "Programar a substituição do rolamento com o motor parado e conferir a lubrificação do mancal oposto."),
    },
    {
        "chunk_id": "WEG-W21-MIM-v3.1-c07",
        "doc_id": "DOC-WEG-W21-MIM", "doc_version": "3.1", "vigente": False,   # substituída pela 3.2
        "titulo": "Manual de instalação e manutenção — motores WEG W21",
        "secao": "Manutenção de mancais e rolamentos",
        "access_class": "kb_manual_fabricante",
        "recomendacao": "TROCA_ROLAMENTO",
        "keywords": {"rolamento", "mancal", "vibracao", "aquecimento", "temperatura", "substituir"},
        "texto": "Versão anterior do procedimento de rolamentos (substituída). Não deve ser usada.",
    },
    {
        "chunk_id": "WEG-W21-MIM-v3.2-c08",
        "doc_id": "DOC-WEG-W21-MIM", "doc_version": "3.2", "vigente": True,
        "titulo": "Manual de instalação e manutenção — motores WEG W21",
        "secao": "Lubrificação dos rolamentos",
        "access_class": "kb_manual_fabricante",
        "recomendacao": "LUBRIFICACAO",
        "keywords": {"weg", "lubrificacao", "lubrificar", "graxa", "intervalo", "rolamento", "mancal", "aquecimento"},
        "texto": ("Usar graxa compatível com a indicada na placa do motor e não misturar tipos diferentes. "
                  "Excesso de graxa também provoca aquecimento do mancal."),
    },
    {
        "chunk_id": "WEG-W21-MIM-v3.2-c11",
        "doc_id": "DOC-WEG-W21-MIM", "doc_version": "3.2", "vigente": True,
        "titulo": "Manual de instalação e manutenção — motores WEG W21",
        "secao": "Temperatura de operação e classe de isolamento",
        "access_class": "kb_manual_fabricante",
        "recomendacao": "INSPECAO",
        "keywords": {"weg", "temperatura", "sobreaquecimento", "aquecimento", "isolamento", "classe", "ventilacao", "sobrecarga", "carcaca"},
        "texto": ("Classe de isolamento F com limite de 155 °C. Causas comuns de sobreaquecimento: sobrecarga, "
                  "ventilação obstruída e tensão desequilibrada entre fases. Inspecionar antes de religar."),
    },
    {
        "chunk_id": "SIE-GP-OPI-v2.1-c04",
        "doc_id": "DOC-SIEMENS-SIMOTICS-GP-OPI", "doc_version": "2.1", "vigente": True,
        "titulo": "Instruções de operação — Siemens SIMOTICS GP",
        "secao": "Vibração, alinhamento e fixação",
        "access_class": "kb_manual_fabricante",
        "recomendacao": "INSPECAO",
        "keywords": {"vibracao", "alinhamento", "desalinhamento", "acoplamento", "base", "fixacao", "esteira", "siemens"},
        "texto": ("Vibração elevada sem aquecimento costuma indicar desalinhamento do acoplamento ou base solta. "
                  "Verificar alinhamento e torque dos parafusos de fixação."),
    },
    {
        "chunk_id": "WEG-W22-MIM-v5.0-c03",
        "doc_id": "DOC-WEG-W22-MIM", "doc_version": "5.0", "vigente": True,
        "titulo": "Manual de instalação e manutenção — motores WEG W22",
        "secao": "Corrente acima da nominal",
        "access_class": "kb_manual_fabricante",
        "recomendacao": "INSPECAO",
        "keywords": {"weg", "corrente", "nominal", "sobrecarga", "tensao", "fase", "desequilibrio", "bomba"},
        "texto": ("Corrente acima da nominal indica sobrecarga mecânica ou desequilíbrio de tensão. "
                  "Medir a tensão nas três fases e conferir a carga acionada."),
    },
    {
        "chunk_id": "POP-MAN-014-v1.4-c01",
        "doc_id": "POP-MAN-014", "doc_version": "1.4", "vigente": True,
        "titulo": "Procedimento interno — Parada programada de motor",
        "secao": "Comunicação e bloqueio",
        "access_class": "kb_procedimento_interno",
        "recomendacao": "PARADA_PROGRAMADA",
        "keywords": {"parada", "programada", "parar", "desligar", "bloqueio", "loto", "nr10", "ordem", "servico", "rolamento", "substituir", "trocar"},
        "texto": ("Toda parada programada exige aviso ao Gestor de Planta, ordem de serviço aberta e bloqueio "
                  "e etiquetagem conforme NR-10 antes da intervenção."),
    },
    {
        "chunk_id": "POP-MAN-021-v1.1-c01",
        "doc_id": "POP-MAN-021", "doc_version": "1.1", "vigente": True,
        "titulo": "Procedimento interno — Retorno de manutenção e teste de sensores",
        "secao": "Teste de leitura dos sensores",
        "access_class": "kb_procedimento_interno",
        "recomendacao": "INSPECAO",
        "keywords": {"sensor", "leitura", "zero", "zerado", "conector", "manutencao", "retorno", "temperatura", "adc"},
        "texto": ("Após manutenção, conferir as leituras de todos os canais do sensor. Leitura zerada ou congelada "
                  "indica conector solto (ação do postmortem PM-2026-001)."),
    },
    {
        "chunk_id": "POP-MAN-030-v1.0-c01",
        "doc_id": "POP-MAN-030", "doc_version": "1.0", "vigente": True,
        "titulo": "Procedimento interno — Alteração de limiar",
        "secao": "Mudança de Metric Contract",
        "access_class": "kb_procedimento_interno",
        "recomendacao": "AJUSTE_THRESHOLD",
        "keywords": {"threshold", "limiar", "limite", "ajuste", "ajustar", "alterar", "contrato", "metric"},
        "texto": ("Alterar faixa de limiar é mudança MAJOR do Metric Contract: passa pelos gates de promoção, "
                  "exige aprovação registrada e Banner de Ruptura na interface."),
    },
    {
        "chunk_id": "MODEL-CARD-ANOM-v4.1.0-c02",
        "doc_id": "MODEL-CARD-ANOM", "doc_version": "4.1.0", "vigente": True,
        "titulo": "Model Card — modelo de anomalias",
        "secao": "Limitações conhecidas",
        "access_class": "kb_model_card",
        "recomendacao": "INFORMATIVA",
        "keywords": {"modelo", "model", "card", "limitacao", "vies", "confianca", "treinamento", "drift"},
        "texto": ("Desempenho menor em marcas sub-representadas e ativos com mais de 15 anos. "
                  "Predições com confiança abaixo de 70% acionam o Circuit Breaker."),
    },
]
