"""
COMPONENTES REUTILIZÁVEIS DE INTERFACE.

Cada função renderiza um bloco visual isolado, podendo ser reaproveitada em
qualquer página. Nenhum componente conhece a origem dos dados — todos recebem
dicionários prontos, garantindo o desacoplamento em relação aos modelos.
"""

import streamlit as st

# ── Paleta semântica (consistente em todo o sistema) ────────────────────────
CORES = {
    "critico": {"cor": "#DC3545", "bg": "#fff0f0", "icon": "🔴", "label": "CRÍTICO"},
    "atencao": {"cor": "#FFC107", "bg": "#fffbf0", "icon": "🟡", "label": "ATENÇÃO"},
    "normal":  {"cor": "#28A745", "bg": "#f0fff4", "icon": "🟢", "label": "NORMAL"},
}


def _sem(severidade):
    return CORES.get(severidade, CORES["normal"])


# ═══════════════════════════════════════════════════════════════════════════
# CARD DE ALERTA
# ═══════════════════════════════════════════════════════════════════════════
def card_alerta(evento, nome_equipamento, resumo_nlp, novo=False):
    """Renderiza um card de alerta com resumo textual gerado por NLP."""
    s = _sem(evento["severidade"])
    hora = evento["timestamp"].strftime("%H:%M:%S") if hasattr(evento["timestamp"], "strftime") else evento["timestamp"]
    score = evento.get("score_anomalia", 0) * 100
    badge_novo = (
        '<span style="background:#FF6B00;color:#fff;padding:2px 9px;border-radius:50px;'
        'font-size:10px;font-weight:800;letter-spacing:1px;margin-left:6px;">NOVO</span>'
        if novo else ""
    )

    st.markdown(
        f"""
        <div style="background:{s['bg']};border-radius:12px;padding:18px 22px;
                    border-left:6px solid {s['cor']};margin-bottom:12px;color:#111;
                    box-shadow:0 3px 14px rgba(0,0,0,0.06);">
          <div style="display:flex;justify-content:space-between;align-items:center;
                      flex-wrap:wrap;gap:8px;margin-bottom:10px;">
            <div style="display:flex;align-items:center;gap:9px;flex-wrap:wrap;">
              <span style="font-size:19px;">{s['icon']}</span>
              <span style="background:{s['cor']};color:#fff;padding:3px 11px;
                           border-radius:50px;font-size:11px;font-weight:800;">{s['label']}</span>
              <span style="background:#FF6B00;color:#fff;padding:3px 11px;
                           border-radius:50px;font-size:11px;font-weight:700;">{evento['tag']}</span>
              <span style="font-family:'Barlow Condensed',sans-serif;font-size:19px;
                           font-weight:700;color:#3D1A6E;">{nome_equipamento}</span>
              {badge_novo}
            </div>
            <span style="font-size:11px;color:#888;">🕐 {hora}</span>
          </div>

          <div style="background:rgba(255,255,255,0.75);border-radius:8px;padding:12px 14px;
                      border:1px solid rgba(0,0,0,0.05);margin-bottom:10px;">
            <div style="font-size:10px;font-weight:800;letter-spacing:1.5px;
                        color:#3D1A6E;text-transform:uppercase;margin-bottom:6px;">
              🧠 Resumo gerado por NLP
            </div>
            <div style="font-size:13px;line-height:1.65;color:#333;">{resumo_nlp}</div>
          </div>

          <div style="display:flex;gap:18px;flex-wrap:wrap;font-size:11px;color:#666;">
            <span><b>Sensor:</b> {evento.get('metrica_label','—')}</span>
            <span><b>Medido:</b> <b style="color:{s['cor']}">{evento['valor']} {evento.get('unidade','')}</b></span>
            <span><b>Limite:</b> {evento['limite']} {evento.get('unidade','')}</span>
            <span><b>Score anomalia:</b> {score:.0f}%</span>
            <span><b>Modelo:</b> {evento.get('modelo','—')}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════
# CARD DE RECOMENDAÇÃO / APOIO À DECISÃO
# ═══════════════════════════════════════════════════════════════════════════
def card_recomendacao(rec):
    """Renderiza um card de apoio à decisão com plano de ação."""
    s = _sem(rec["severidade"])
    passos_html = "".join(
        f'<li style="margin-bottom:5px;font-size:12.5px;color:#333;">{p}</li>'
        for p in rec["passos"]
    )

    st.markdown(
        f"""
        <div style="background:#fff;border-radius:12px;padding:18px 20px;
                    border-top:4px solid {s['cor']};margin-bottom:12px;color:#111;
                    box-shadow:0 3px 14px rgba(0,0,0,0.07);height:100%;">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;flex-wrap:wrap;">
            <span style="background:#FF6B00;color:#fff;padding:2px 10px;
                         border-radius:50px;font-size:10px;font-weight:800;">{rec['tag']}</span>
            <span style="background:{s['bg']};color:{s['cor']};padding:2px 10px;
                         border-radius:50px;font-size:10px;font-weight:800;">{s['icon']} {s['label']}</span>
          </div>
          <div style="font-family:'Barlow Condensed',sans-serif;font-size:19px;
                      font-weight:800;color:#3D1A6E;margin:8px 0 12px 0;
                      text-transform:uppercase;letter-spacing:0.4px;">{rec['titulo']}</div>

          <div style="display:flex;gap:10px;margin-bottom:12px;flex-wrap:wrap;">
            <div style="background:#f6f6f8;border-radius:7px;padding:7px 12px;flex:1;min-width:110px;">
              <div style="font-size:9px;font-weight:800;letter-spacing:1px;color:#888;">PRAZO</div>
              <div style="font-size:13px;font-weight:700;color:{s['cor']};">{rec['prazo']}</div>
            </div>
            <div style="background:#f6f6f8;border-radius:7px;padding:7px 12px;flex:1;min-width:130px;">
              <div style="font-size:9px;font-weight:800;letter-spacing:1px;color:#888;">RESPONSÁVEL</div>
              <div style="font-size:13px;font-weight:700;color:#3D1A6E;">{rec['equipe']}</div>
            </div>
          </div>

          <div style="font-size:9px;font-weight:800;letter-spacing:1.3px;
                      color:#888;margin-bottom:6px;">PLANO DE AÇÃO</div>
          <ol style="margin:0;padding-left:18px;">{passos_html}</ol>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════
# PAINEL DE ESTADO DO EQUIPAMENTO
# ═══════════════════════════════════════════════════════════════════════════
def painel_estado(equipamento, severidade, descricao_nlp, mudou=False):
    """Renderiza o painel de estado operacional de um ativo."""
    s = _sem(severidade)
    pulse = (
        "animation:pulseState 1.4s ease-in-out 3;" if mudou else ""
    )
    badge_mudou = (
        '<span style="background:#FF6B00;color:#fff;padding:2px 8px;border-radius:50px;'
        'font-size:9px;font-weight:800;letter-spacing:1px;">ESTADO ALTERADO</span>'
        if mudou else ""
    )

    st.markdown(
        f"""
        <style>
        @keyframes pulseState {{
          0%,100% {{ box-shadow:0 3px 14px rgba(0,0,0,0.07); }}
          50%     {{ box-shadow:0 0 0 5px {s['cor']}44; }}
        }}
        </style>
        <div style="background:#fff;border-radius:12px;padding:18px 20px;
                    border-left:6px solid {s['cor']};margin-bottom:12px;color:#111;
                    box-shadow:0 3px 14px rgba(0,0,0,0.07);{pulse}">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;
                      flex-wrap:wrap;gap:8px;">
            <div style="display:flex;align-items:center;gap:9px;flex-wrap:wrap;">
              <span style="background:#FF6B00;color:#fff;padding:3px 11px;
                           border-radius:50px;font-size:11px;font-weight:700;">{equipamento['tag']}</span>
              <span style="font-family:'Barlow Condensed',sans-serif;font-size:20px;
                           font-weight:700;color:#3D1A6E;">{equipamento['nome']}</span>
              {badge_mudou}
            </div>
            <span style="background:{s['bg']};color:{s['cor']};padding:4px 14px;
                         border-radius:50px;font-size:12px;font-weight:800;">
              {s['icon']} {s['label']}</span>
          </div>

          <div style="font-size:11px;color:#888;margin-top:6px;">
            📍 {equipamento.get('local_instalacao','—')} &nbsp;|&nbsp;
            ⚙️ {equipamento.get('modelo','—')} &nbsp;|&nbsp;
            ⚡ {equipamento.get('potencia_kw','—')} kW
          </div>

          <div style="background:#f8f8fa;border-radius:8px;padding:11px 13px;margin-top:11px;
                      border-left:3px solid {s['cor']};">
            <div style="font-size:9px;font-weight:800;letter-spacing:1.3px;
                        color:#3D1A6E;margin-bottom:5px;">🧠 DESCRIÇÃO DO ESTADO (NLP)</div>
            <div style="font-size:12.5px;line-height:1.6;color:#444;">{descricao_nlp}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════
# TIMELINE DE EVENTOS
# ═══════════════════════════════════════════════════════════════════════════
def timeline_eventos(historico):
    """Renderiza o histórico cronológico de eventos."""
    if not historico:
        st.markdown(
            '<div style="background:#fff;border-radius:12px;padding:24px;text-align:center;'
            'color:#888;font-size:13px;box-shadow:0 3px 14px rgba(0,0,0,0.06);">'
            'Nenhum evento registrado ainda. Clique em <b>Atualizar</b> para executar '
            'um ciclo de análise.</div>',
            unsafe_allow_html=True,
        )
        return

    itens = ""
    for ev in reversed(historico[-15:]):
        s = _sem(ev["severidade"])
        hora = ev["timestamp"].strftime("%H:%M:%S") if hasattr(ev["timestamp"], "strftime") else ev["timestamp"]
        itens += f"""
        <div style="display:flex;gap:14px;padding:11px 0;border-bottom:1px solid #f0f0f0;">
          <div style="min-width:62px;font-size:11px;color:#888;font-weight:600;padding-top:2px;">{hora}</div>
          <div style="width:11px;display:flex;flex-direction:column;align-items:center;">
            <div style="width:11px;height:11px;border-radius:50%;background:{s['cor']};
                        margin-top:4px;flex-shrink:0;"></div>
            <div style="width:2px;flex:1;background:#eee;margin-top:3px;"></div>
          </div>
          <div style="flex:1;">
            <div style="display:flex;align-items:center;gap:7px;flex-wrap:wrap;">
              <span style="background:{s['bg']};color:{s['cor']};padding:1px 9px;
                           border-radius:50px;font-size:10px;font-weight:800;">{s['label']}</span>
              <span style="background:#FF6B00;color:#fff;padding:1px 9px;
                           border-radius:50px;font-size:10px;font-weight:700;">{ev['tag']}</span>
            </div>
            <div style="font-size:12.5px;color:#333;margin-top:4px;">
              {ev.get('metrica_label','—')} atingiu
              <b style="color:{s['cor']}">{ev['valor']} {ev.get('unidade','')}</b>
              (limite: {ev['limite']} {ev.get('unidade','')})
            </div>
          </div>
        </div>"""

    st.markdown(
        f'<div style="background:#fff;border-radius:12px;padding:8px 20px;color:#111;'
        f'box-shadow:0 3px 14px rgba(0,0,0,0.06);">{itens}</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════
# BLOCO DE RESUMO EXECUTIVO
# ═══════════════════════════════════════════════════════════════════════════
def bloco_resumo_executivo(texto, motor_nlp, ciclo, total_ciclos):
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#3D1A6E 0%,#5B2DA0 100%);
                    border-radius:12px;padding:20px 24px;margin-bottom:18px;
                    box-shadow:0 5px 22px rgba(61,26,110,0.28);">
          <div style="display:flex;justify-content:space-between;align-items:center;
                      flex-wrap:wrap;gap:8px;margin-bottom:10px;">
            <div style="font-size:10px;font-weight:800;letter-spacing:2px;color:#FF6B00;">
              🧠 RESUMO EXECUTIVO — GERADO POR NLP
            </div>
            <div style="font-size:10px;color:rgba(255,255,255,0.55);">
              Ciclo {ciclo} de {total_ciclos - 1} &nbsp;•&nbsp; {motor_nlp}
            </div>
          </div>
          <div style="font-size:14.5px;line-height:1.75;color:#fff;">{texto}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
