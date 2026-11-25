"""
Testes da Sprint 4 (Governança). Servem de base para os gates de promoção:
MAT (limiares da tela = contratos) e regressão do assistente (citação e acesso por perfil).
Rodar com: python -m pytest -q
"""
import copy
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import access, assistant, contracts, monitoring  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EQUIPS = [
    {"tag": "MTR-001", "nome": "Motor Bomba Principal", "fabricante": "WEG", "saude": "normal"},
    {"tag": "MTR-002", "nome": "Motor Compressor 1", "fabricante": "WEG", "saude": "critico"},
    {"tag": "MTR-003", "nome": "Motor Esteira Transportadora", "fabricante": "Siemens", "saude": "atencao"},
]
HIST = {"MTR-002": [{"temperatura_c": 96.0, "vibracao_mms": 11.8, "corrente_a": 38.0}]}


@pytest.fixture
def state():
    s = {"equipment_list": copy.deepcopy(EQUIPS), "historicos": copy.deepcopy(HIST)}
    for _ in range(5):
        monitoring.executar_ciclo(s)
    return s


# ── MAT: Metric Contracts ───────────────────────────────────────────────────
def test_contratos_tem_faixas_da_documentacao():
    assert (contracts.faixas("temperatura_c")["atencao"], contracts.faixas("temperatura_c")["alerta"],
            contracts.faixas("temperatura_c")["critico"]) == (75, 85, 95)
    assert (contracts.faixas("vibracao_mms")["atencao"], contracts.faixas("vibracao_mms")["alerta"],
            contracts.faixas("vibracao_mms")["critico"]) == (4.5, 7.1, 11.0)
    assert contracts.faixas("aceleracao_g")["critico"] == 6.5


@pytest.mark.parametrize("valor,faixa", [(60, "normal"), (75, "atencao"), (88, "alerta"), (96.8, "critico")])
def test_classificacao_temperatura(valor, faixa):
    assert contracts.classificar("temperatura_c", valor) == faixa


def test_nenhum_limiar_antigo_hardcoded_nas_paginas():
    """Os limiares da Sprint 3 (70/80 °C e 2,8/4,5 mm/s) não podem voltar à interface."""
    for nome in ("telemetry.py", "raw_data.py"):
        codigo = open(os.path.join(RAIZ, "pages", nome), encoding="utf-8").read()
        assert not re.search(r'"warn":\s*(70|2\.8)\b', codigo)
        assert "70, 80" not in codigo and "2.8, 4.5" not in codigo


def test_eventos_do_motor_de_alertas_usam_limites_dos_contratos(state):
    for ev in state["historico_eventos"]:
        if contracts.tem_contrato(ev["metrica"]):
            f = contracts.faixas(ev["metrica"])
            assert ev["limite"] in (f["atencao"], f["alerta"], f["critico"])


# ── Acesso por perfil ───────────────────────────────────────────────────────
def test_back_end_nega_dados_brutos_ao_gestor():
    with pytest.raises(access.AcessoNegado):
        access.exigir("GESTOR", "dados_brutos")


def test_tecnico_nao_le_log_de_auditoria(state):
    with pytest.raises(access.AcessoNegado):
        assistant.log_auditoria(state, "TECNICO")


def test_filtro_pre_recuperacao_esconde_model_card_do_tecnico():
    trechos, filtro = assistant.recuperar("TECNICO", {"model", "card", "limitacao"}, set())
    assert "kb_model_card" not in filtro
    assert all(t["access_class"] != "kb_model_card" for t in trechos)


def test_versao_substituida_nunca_e_recuperada():
    trechos, _ = assistant.recuperar("ADMIN", {"rolamento", "mancal"}, set())
    assert all(t["vigente"] for t in trechos)


# ── Regra de citação (Tabela 22) ────────────────────────────────────────────
def test_recomendacao_com_fonte_e_dado_operacional(state):
    r = assistant.perguntar(state, "TECNICO", "tec.joao", "O que devo fazer com o MTR-002?")
    assert r["citation_status"] == "COM_FONTE"
    assert r["recommendation_type"] == "TROCA_ROLAMENTO"
    assert r["citacoes"][0]["doc_id"] == "DOC-WEG-W21-MIM" and r["citacoes"][0]["doc_version"] == "3.2"
    assert any("MTC-VIB-001" in d for d in r["dado_operacional"])
    assert "24 horas" in r["texto"]


def test_sem_fonte_vai_para_revisao_humana(state):
    r = assistant.perguntar(state, "TECNICO", "tec.joao", "Como calibrar o inversor de frequência do MTR-002?")
    assert r["citation_status"] == "SEM_FONTE_REVISAO" and r["handoff_level"] == "H2"
    assert r["citacoes"] == [] and r["recommendation_type"] == "INFORMATIVA"


def test_gestor_recebe_acesso_negado_para_dado_bruto(state):
    r = assistant.perguntar(state, "GESTOR", "gestor.ana", "Qual o valor bruto do ADC do MTR-002?")
    assert r["citation_status"] == "ACESSO_NEGADO"
    assert "11.8" not in r["texto"] and "96" not in r["texto"]


def test_credenciais_nunca_sao_recuperadas_nem_pelo_admin(state):
    r = assistant.perguntar(state, "ADMIN", "admin.carla", "Qual a senha do usuário gestor?")
    assert r["citation_status"] == "ACESSO_NEGADO"


def test_gestor_ve_telemetria_so_em_resumo(state):
    ctx = assistant.contexto_operacional(state, "GESTOR", "MTR-002")
    assert ctx["telemetria"] == {"temperatura_c": "critico", "vibracao_mms": "critico"}


def test_verificador_bloqueia_citacao_que_nao_foi_recuperada():
    recuperados, _ = assistant.recuperar("TECNICO", {"rolamento"}, set())
    falsa = [{"chunk_id": "DOC-INVENTADO-c99"}]
    assert assistant.verificar_citacoes(falsa, recuperados) is False


# ── Log de auditoria (Tabela 21) ────────────────────────────────────────────
def test_log_tem_campos_obrigatorios_e_assinatura(state):
    assistant.perguntar(state, "TECNICO", "tec.joao", "O que devo fazer com o MTR-002?")
    reg = state[assistant.LOG_KEY][-1]
    for campo in ("trace_id", "user_pseudo_id", "user_role", "request_timestamp", "retrieved_sources",
                  "llm_model_version", "knowledge_base_version", "prediction_model_version",
                  "citation_status", "operator_decision", "digital_signature"):
        assert campo in reg
    assert reg["user_pseudo_id"] != "tec.joao"
    assert assistant.verificar_assinatura(reg)
    reg["citation_status"] = "ALTERADO"
    assert not assistant.verificar_assinatura(reg)


def test_log_nao_guarda_token_nem_senha(state):
    assistant.perguntar(state, "TECNICO", "tec.joao",
                        "MTR-002 rolamento Bearer abc.def.ghi senha=123456 joao@forzy.com")
    texto = str(state[assistant.LOG_KEY][-1])
    assert "abc.def.ghi" not in texto and "123456" not in texto and "joao@forzy.com" not in texto


def test_decisao_exige_justificativa_e_e_append_only(state):
    r = assistant.perguntar(state, "TECNICO", "tec.joao", "O que devo fazer com o MTR-002?")
    with pytest.raises(ValueError):
        assistant.registrar_decisao(state, "TECNICO", "tec.joao", r["trace_id"], "REJEITOU", "")
    antes = len(state[assistant.LOG_KEY])
    assistant.registrar_decisao(state, "TECNICO", "tec.joao", r["trace_id"], "ESCALOU", "ruído diferente no mancal")
    log = state[assistant.LOG_KEY]
    assert len(log) == antes + 1
    assert log[-1]["previous_event_id"] == log[-2]["event_id"]
    assert assistant.decisao_atual(state, r["trace_id"]) == "ESCALOU"
    assert log[-1]["handoff_level"] == "H3"
