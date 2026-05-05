import streamlit as st
from datetime import date


def render():
    mode = st.session_state.get("form_mode", "new")
    data = st.session_state.get("edit_data", None)
    is_view = mode == "view"
    is_edit  = mode == "edit"
    is_new   = mode == "new"

    title_map = {
        "new":  ("Cadastro de Equipamento", "Preencha os dados técnicos do novo ativo"),
        "edit": ("Editar Equipamento", f"Editando: {data['tag'] if data else ''}"),
        "view": ("Ficha Técnica", f"TAG: {data['tag'] if data else ''}"),
    }
    h1, sub = title_map[mode]

    st.markdown(
        '<div class="topbar-strip">'
        '<div class="strip-seg s3"></div><div class="strip-seg s1"></div>'
        '<div class="strip-seg s2"></div><div class="strip-seg s1"></div>'
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="page-header"><h1>{h1}</h1><p>{sub}</p></div>',
        unsafe_allow_html=True,
    )

    if is_view and data:
        _render_ficha(data)
        return

    _render_form(data, is_new)


def _render_ficha(eq):
    """Read-only technical spec card."""
    st.markdown(
        f"""
        <div class="forzy-card">
          <h3>⚙️ Identificação</h3>
          <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:20px;">
            {_field("TAG", eq['tag'])}
            {_field("Nome", eq['nome'])}
            {_field("Modelo", eq['modelo'])}
            {_field("Fabricante", eq['fabricante'])}
            {_field("Tipo", eq['tipo'])}
            {_field("Local", eq['local_instalacao'])}
            {_field("Data Cadastro", eq['data_cadastro'])}
            {_field("Status", eq['status'])}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="forzy-card">
          <h3>⚡ Dados Elétricos</h3>
          <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:20px;">
            {_field("Potência (kW)", f"{eq['potencia_kw']} kW")}
            {_field("Potência (cv)", f"{eq['potencia_cv']} cv")}
            {_field("Tensão Nominal", f"{eq['tensao_v']} V")}
            {_field("Corrente Nominal", f"{eq['corrente_nominal_a']} A")}
            {_field("Frequência", f"{eq['frequencia_hz']} Hz")}
            {_field("Fator de Potência (cos φ)", str(eq['fator_potencia']))}
            {_field("Rotação Nominal", f"{eq['rotacao_nominal_rpm']} RPM")}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="forzy-card">
          <h3>🛡️ Proteção & Isolamento</h3>
          <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:20px;">
            {_field("Classe de Isolamento", eq['classe_isolamento'])}
            {_field("Grau de Proteção (IP)", eq['grau_protecao'])}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if eq.get("observacoes"):
        st.markdown(
            f'<div class="forzy-card"><h3>📝 Observações</h3>'
            f'<p style="font-size:14px;color:#444;line-height:1.7">{eq["observacoes"]}</p></div>',
            unsafe_allow_html=True,
        )

    c1, c2, c3 = st.columns([1, 1, 5])
    with c1:
        if st.button("✏️ Editar"):
            st.session_state.form_mode = "edit"
            st.rerun()
    with c2:
        if st.button("📊 Dados Brutos"):
            st.session_state.selected_equipment_id = st.session_state.edit_data["id"]
            st.session_state.active_page = "raw_data"
            st.rerun()


def _field(label, value):
    return (
        f"<div>"
        f'<div style="font-size:11px;font-weight:700;text-transform:uppercase;'
        f'letter-spacing:1px;color:#888;margin-bottom:4px;">{label}</div>'
        f'<div style="font-size:15px;font-weight:600;color:#111;">{value}</div>'
        f"</div>"
    )


def _render_form(data, is_new):
    """Create / Edit form."""

    def v(field, default=""):
        if data and field in data:
            return data[field]
        return default

    # ── Section: Identificação ─────────────────────────────────
    st.markdown('<div class="section-divider"><span>Identificação</span></div>', unsafe_allow_html=True)
    r1c1, r1c2, r1c3 = st.columns(3)
    with r1c1:
        tag = st.text_input("TAG do Equipamento *", value=v("tag"), placeholder="ex: MTR-001")
    with r1c2:
        nome = st.text_input("Nome do Equipamento *", value=v("nome"), placeholder="ex: Motor Bomba Principal")
    with r1c3:
        status = st.selectbox(
            "Status *",
            ["Ativo", "Manutenção", "Inativo"],
            index=["Ativo", "Manutenção", "Inativo"].index(v("status", "Ativo")),
        )

    r2c1, r2c2, r2c3 = st.columns(3)
    with r2c1:
        modelo = st.text_input("Modelo *", value=v("modelo"), placeholder="ex: WEG W22 100L")
    with r2c2:
        fabricante = st.text_input("Fabricante *", value=v("fabricante"), placeholder="ex: WEG")
    with r2c3:
        tipo = st.selectbox(
            "Tipo de Motor",
            ["Trifásico", "Monofásico", "CC", "Síncrono", "Outro"],
            index=["Trifásico", "Monofásico", "CC", "Síncrono", "Outro"].index(v("tipo", "Trifásico")),
        )

    local = st.text_input("Local de Instalação", value=v("local_instalacao"), placeholder="ex: Casa de Bombas — Bloco A")

    # ── Section: Dados Elétricos ───────────────────────────────
    st.markdown('<div class="section-divider"><span>Dados Elétricos</span></div>', unsafe_allow_html=True)

    e1, e2, e3, e4 = st.columns(4)
    with e1:
        potencia_kw = st.number_input("Potência (kW) *", min_value=0.0, value=float(v("potencia_kw", 0.0)), step=0.1, format="%.1f")
    with e2:
        potencia_cv = st.number_input("Potência (cv) *", min_value=0.0, value=float(v("potencia_cv", 0.0)), step=0.1, format="%.1f")
    with e3:
        tensao = st.number_input("Tensão (V) *", min_value=0, value=int(v("tensao_v", 380)), step=1)
    with e4:
        corrente = st.number_input("Corrente Nominal (A) *", min_value=0.0, value=float(v("corrente_nominal_a", 0.0)), step=0.1, format="%.1f")

    e5, e6, e7 = st.columns(3)
    with e5:
        frequencia = st.number_input("Frequência (Hz)", min_value=0, value=int(v("frequencia_hz", 60)), step=1)
    with e6:
        rotacao = st.number_input("Rotação Nominal (RPM)", min_value=0, value=int(v("rotacao_nominal_rpm", 1760)), step=10)
    with e7:
        fp = st.number_input("Fator de Potência (cos φ)", min_value=0.0, max_value=1.0, value=float(v("fator_potencia", 0.85)), step=0.01, format="%.2f")

    # ── Section: Proteção ──────────────────────────────────────
    st.markdown('<div class="section-divider"><span>Proteção & Isolamento</span></div>', unsafe_allow_html=True)

    p1, p2 = st.columns(2)
    with p1:
        classe = st.selectbox(
            "Classe de Isolamento",
            ["A", "B", "E", "F", "H"],
            index=["A", "B", "E", "F", "H"].index(v("classe_isolamento", "F")),
        )
    with p2:
        ip = st.selectbox(
            "Grau de Proteção (IP)",
            ["IP21", "IP44", "IP54", "IP55", "IP65", "IP66"],
            index=["IP21", "IP44", "IP54", "IP55", "IP65", "IP66"].index(v("grau_protecao", "IP55")),
        )

    # ── Observações ────────────────────────────────────────────
    st.markdown('<div class="section-divider"><span>Observações</span></div>', unsafe_allow_html=True)
    obs = st.text_area("Observações", value=v("observacoes"), height=100, placeholder="Informações adicionais sobre o equipamento...")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Validation & Save ──────────────────────────────────────
    required_ok = all([tag, nome, modelo, fabricante, potencia_kw > 0, tensao > 0])

    sb1, sb2, sb3 = st.columns([1, 1, 5])
    with sb1:
        save = st.button("💾  Salvar", use_container_width=True)
    with sb2:
        if st.button("↩️  Cancelar", use_container_width=True):
            st.session_state.active_page = "equipment_list"
            st.rerun()

    if save:
        if not required_ok:
            st.error("⚠️  Preencha todos os campos obrigatórios (marcados com *).")
            return

        # Check for duplicate TAG on new
        existing_tags = [e["tag"] for e in st.session_state.equipment_list]
        if is_new and tag in existing_tags:
            st.error(f"Já existe um equipamento com a TAG **{tag}**.")
            return

        new_eq = {
            "id": tag,
            "tag": tag,
            "nome": nome,
            "modelo": modelo,
            "fabricante": fabricante,
            "tipo": tipo,
            "potencia_cv": potencia_cv,
            "potencia_kw": potencia_kw,
            "tensao_v": tensao,
            "corrente_nominal_a": corrente,
            "frequencia_hz": frequencia,
            "rotacao_nominal_rpm": rotacao,
            "fator_potencia": fp,
            "classe_isolamento": classe,
            "grau_protecao": ip,
            "local_instalacao": local,
            "status": status,
            "data_cadastro": str(date.today()),
            "observacoes": obs,
        }

        eq_list = st.session_state.equipment_list
        if is_new:
            eq_list.append(new_eq)
            st.success(f"✅  Equipamento **{tag}** cadastrado com sucesso!")
        else:
            idx = next((i for i, e in enumerate(eq_list) if e["id"] == data["id"]), None)
            if idx is not None:
                eq_list[idx] = new_eq
            st.success(f"✅  Equipamento **{tag}** atualizado com sucesso!")

        st.session_state.equipment_list = eq_list
        st.session_state.form_mode = "view"
        st.session_state.edit_data = new_eq
        st.rerun()
