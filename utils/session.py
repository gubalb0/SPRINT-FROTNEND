import streamlit as st
from datetime import datetime

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
        "status": "Ativo",
        "data_cadastro": "2024-10-15",
        "observacoes": "Motor principal do circuito de resfriamento.",
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
        "status": "Manutenção",
        "data_cadastro": "2024-11-02",
        "observacoes": "Em manutenção preventiva programada.",
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
        "status": "Ativo",
        "data_cadastro": "2025-01-20",
        "observacoes": "",
    },
]


def init_session():
    if "equipment_list" not in st.session_state:
        st.session_state.equipment_list = SAMPLE_EQUIPMENT.copy()
    if "selected_equipment_id" not in st.session_state:
        st.session_state.selected_equipment_id = None
    if "active_page" not in st.session_state:
        st.session_state.active_page = "dashboard"
    if "form_mode" not in st.session_state:
        st.session_state.form_mode = "new"   # 'new' or 'edit'
    if "edit_data" not in st.session_state:
        st.session_state.edit_data = None
