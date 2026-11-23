"""Testes dos serviços (Sprint 4). Rodar com: python -m pytest -q"""
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import alert_engine, monitoring, nlp_service  # noqa: E402

EQUIPS = [
    {"tag": "MTR-001", "nome": "Motor Bomba Principal", "saude": "normal", "local_instalacao": "Casa de Bombas"},
    {"tag": "MTR-002", "nome": "Motor Compressor 1", "saude": "critico", "local_instalacao": "Sala de Compressores"},
    {"tag": "MTR-003", "nome": "Motor Esteira", "saude": "atencao", "local_instalacao": "Setor 3"},
]


def _state():
    return {"equipment_list": copy.deepcopy(EQUIPS)}


def test_todos_eventos_do_cenario_respeitam_contrato():
    for ciclo in range(alert_engine.total_ciclos()):
        eventos, _ = alert_engine.detectar_anomalias(ciclo)
        for ev in eventos:
            assert alert_engine.validar_evento(ev) == []


def test_validar_evento_aponta_problemas():
    problemas = alert_engine.validar_evento({"severidade": "grave", "score_anomalia": 1.7})
    assert any("campo ausente: tag" in p for p in problemas)
    assert any("severidade inválida" in p for p in problemas)
    assert any("score_anomalia" in p for p in problemas)


def test_ids_de_evento_nao_colidem_no_mesmo_segundo():
    ids = set()
    for _ in range(20):
        eventos, _ = alert_engine.detectar_anomalias(2)
        ids.update(e["id"] for e in eventos)
    assert len(ids) == 20


def test_ciclo_propaga_estado_e_gera_trace_id():
    st = _state()
    monitoring.garantir_inicializado(st)   # ciclo 0
    monitoring.executar_ciclo(st)          # ciclo 1
    monitoring.executar_ciclo(st)          # ciclo 2 → MTR-002 crítico
    saude = {e["tag"]: e["saude"] for e in st["equipment_list"]}
    assert saude["MTR-002"] == "critico"
    assert st["mudancas_estado"] == {"MTR-002": "critico"}
    assert len(st["trace_id"]) == 12
    assert all(e["trace_id"] for e in st["historico_eventos"])


def test_evento_fora_do_contrato_e_descartado(monkeypatch):
    def quebrado(ciclo):
        return [{"id": "x", "severidade": "critico"}], {"MTR-001": "normal"}
    monkeypatch.setattr(alert_engine, "detectar_anomalias", quebrado)
    st = _state()
    resumo = monitoring.executar_ciclo(st)
    assert resumo["descartados"] == 1 and st["historico_eventos"] == []


def test_reconhecer_remove_dos_pendentes():
    st = _state()
    monitoring.garantir_inicializado(st)
    for _ in range(3):
        monitoring.executar_ciclo(st)
    pend = monitoring.pendentes(st)
    assert pend
    monitoring.reconhecer_alerta(st, pend[0]["id"])
    assert len(monitoring.pendentes(st)) == len(pend) - 1


def test_alertas_ativos_mantem_um_por_tag_e_metrica_criticos_primeiro():
    st = _state()
    monitoring.garantir_inicializado(st)
    for _ in range(6):  # passa do fim do cenário: repete o último ciclo
        monitoring.executar_ciclo(st)
    ativos = monitoring.alertas_ativos(st)
    chaves = [(e["tag"], e["metrica"]) for e in ativos]
    assert len(chaves) == len(set(chaves))
    assert ativos[0]["severidade"] == "critico"


def test_feedback_guarda_trace_id():
    st = _state()
    monitoring.garantir_inicializado(st)
    monitoring.executar_ciclo(st)
    ev = st["historico_eventos"][-1]
    monitoring.registrar_feedback(st, ev["id"], util=False)
    assert monitoring.feedback(st, ev["id"])["trace_id"] == ev["trace_id"]


def test_reiniciar_limpa_simulacao():
    st = _state()
    monitoring.garantir_inicializado(st)
    monitoring.reiniciar(st)
    assert "historico_eventos" not in st and "ciclo_analise" not in st


def test_nlp_resumo_cita_tag_valor_e_confianca():
    eventos, _ = alert_engine.detectar_anomalias(2)
    texto = nlp_service.resumir_evento(eventos[0], EQUIPS[1])
    assert "MTR-002" in texto and "84.3" in texto and "94%" in texto
