import streamlit as st
from datetime import datetime, timedelta
import random
import math

PLANTS = {
    "Planta A — Utilidades": {
        "areas": ["Casa de Bombas", "Sala de Compressores", "Torre de Resfriamento"],
        "cor": "#FF6B00",
    },
    "Planta B — Produção": {
        "areas": ["Linha de Produção — Setor 1", "Linha de Produção — Setor 2", "Linha de Produção — Setor 3"],
        "cor": "#3D1A6E",
    },
    "Planta C — Manutenção": {
        "areas": ["Oficina Mecânica", "Almoxarifado", "Área de Testes"],
        "cor": "#F5C400",
    },
}

SAMPLE_EQUIPMENT = [
    {
        "id": "MTR-001",
        "tag": "MTR-001",
        "nome": "Motor Bomba Principal",
        "modelo": "WEG W22 100L",
        "fabricante": "WEG",
        "tipo": "Trifásico",
        "potencia_cv": 15.0,
        "potencia_kw": 11.0,
        "tensao_v": 380,
        "corrente_nominal_a": 22.5,
        "frequencia_hz": 60,
        "rotacao_nominal_rpm": 1760,
        "fator_potencia": 0.87,
        "classe_isolamento": "F",
        "grau_protecao": "IP55",
        "local_instalacao": "Casa de Bombas — Bloco A",
        "planta": "Planta A — Utilidades",
        "area": "Casa de Bombas",
        "status": "Ativo",
        "saude": "normal",
        "data_cadastro": "2024-10-15",
        "observacoes": "Motor principal do circuito de resfriamento.",
        "imagem_placa": "WEG_W22_nameplate.jpg",
    },
    {
        "id": "MTR-002",
        "tag": "MTR-002",
        "nome": "Motor Compressor 1",
        "modelo": "WEG W21 132M",
        "fabricante": "WEG",
        "tipo": "Trifásico",
        "potencia_cv": 25.0,
        "potencia_kw": 18.5,
        "tensao_v": 440,
        "corrente_nominal_a": 34.0,
        "frequencia_hz": 60,
        "rotacao_nominal_rpm": 1770,
        "fator_potencia": 0.88,
        "classe_isolamento": "F",
        "grau_protecao": "IP54",
        "local_instalacao": "Sala de Compressores",
        "planta": "Planta A — Utilidades",
        "area": "Sala de Compressores",
        "status": "Manutenção",
        "saude": "critico",
        "data_cadastro": "2024-11-02",
        "observacoes": "Em manutenção preventiva programada.",
        "imagem_placa": "WEG_W21_nameplate.jpg",
    },
    {
        "id": "MTR-003",
        "tag": "MTR-003",
        "nome": "Motor Esteira Transportadora",
        "modelo": "Siemens SIMOTICS GP 112M",
        "fabricante": "Siemens",
        "tipo": "Trifásico",
        "potencia_cv": 10.0,
        "potencia_kw": 7.5,
        "tensao_v": 380,
        "corrente_nominal_a": 16.0,
        "frequencia_hz": 60,
        "rotacao_nominal_rpm": 1740,
        "fator_potencia": 0.84,
        "classe_isolamento": "B",
        "grau_protecao": "IP55",
        "local_instalacao": "Linha de Produção — Setor 3",
        "planta": "Planta B — Produção",
        "area": "Linha de Produção — Setor 3",
        "status": "Ativo",
        "saude": "atencao",
        "data_cadastro": "2025-01-20",
        "observacoes": "",
        "imagem_placa": "Siemens_SIMOTICS_nameplate.jpg",
    },
]


def gerar_historico(eq, horas=24, intervalo_min=10):
    """Gera série temporal simulada realista para um equipamento."""
    agora = datetime.now()
    n_pontos = int(horas * 60 / intervalo_min)
    historico = []

    rpm_nom = eq.get("rotacao_nominal_rpm", 1760)
    v_nom   = eq.get("tensao_v", 380)
    i_nom   = eq.get("corrente_nominal_a", 22.5)
    fp      = eq.get("fator_potencia", 0.87)
    saude   = eq.get("saude", "normal")

    # Simula degradação para equipamentos críticos
    for i in range(n_pontos):
        ts = agora - timedelta(minutes=(n_pontos - i) * intervalo_min)
        pct = i / n_pontos  # progresso no tempo (0 → 1)

        # Tendência de degradação para críticos
        drift = 1.0
        if saude == "critico":
            drift = 1.0 + pct * 0.18   # sobe 18% ao longo do histórico
        elif saude == "atencao":
            drift = 1.0 + pct * 0.07

        noise = lambda v, p: v * (1 + random.gauss(0, p))

        temp   = noise(68 * drift, 0.03)
        vibracao = noise(1.2 * drift, 0.08)
        corrente = noise(i_nom * (0.75 + 0.1 * drift), 0.04)
        rpm    = noise(rpm_nom * (1 - 0.02 * (drift - 1)), 0.01)
        tensao = noise(v_nom, 0.02)
        pot_kw = round(tensao * corrente * math.sqrt(3) * fp / 1000, 2)

        historico.append({
            "timestamp": ts,
            "temperatura_c": round(temp, 1),
            "vibracao_mms": round(vibracao, 3),
            "corrente_a": round(corrente, 2),
            "rotacao_rpm": round(rpm),
            "tensao_v": round(tensao, 1),
            "potencia_kw": pot_kw,
        })

    return historico


def init_session():
    if "equipment_list" not in st.session_state:
        st.session_state.equipment_list = SAMPLE_EQUIPMENT.copy()
    if "historicos" not in st.session_state:
        st.session_state.historicos = {
            eq["id"]: gerar_historico(eq) for eq in SAMPLE_EQUIPMENT
        }
    if "selected_equipment_id" not in st.session_state:
        st.session_state.selected_equipment_id = None
    if "active_page" not in st.session_state:
        st.session_state.active_page = "dashboard"
    if "form_mode" not in st.session_state:
        st.session_state.form_mode = "new"
    if "edit_data" not in st.session_state:
        st.session_state.edit_data = None
    if "planta_selecionada" not in st.session_state:
        st.session_state.planta_selecionada = None
    if "area_selecionada" not in st.session_state:
        st.session_state.area_selecionada = None
    if "alertas" not in st.session_state:
        # Gera alertas iniciais baseados nos equipamentos críticos
        st.session_state.alertas = [
            {
                "tag": "MTR-002",
                "tipo": "critico",
                "mensagem": "Temperatura acima do limite operacional (82°C > 80°C)",
                "timestamp": (datetime.now() - timedelta(minutes=23)).strftime("%H:%M"),
            },
            {
                "tag": "MTR-003",
                "tipo": "atencao",
                "mensagem": "Vibração em tendência crescente nas últimas 2h",
                "timestamp": (datetime.now() - timedelta(minutes=47)).strftime("%H:%M"),
            },
            {
                "tag": "MTR-001",
                "tipo": "normal",
                "mensagem": "Todos os parâmetros dentro do limite nominal",
                "timestamp": (datetime.now() - timedelta(minutes=5)).strftime("%H:%M"),
            },
        ]
