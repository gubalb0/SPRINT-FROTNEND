"""
POLÍTICA DE ACESSO POR PERFIL (Sprint 4 — Governança).

Implementa na camada de serviço as matrizes da documentação:
  - Tabela 2  (RBAC por recurso)
  - Tabela 11 (visibilidade na planta digital)
  - Tabela 19 (fontes recuperáveis pelo assistente)

Segurança by Design: a interface pode esconder botões por conveniência, mas a
decisão de autorizar é sempre tomada aqui (`exigir`), antes de renderizar uma
página ou de recuperar qualquer dado. Em produção o perfil viria da claim
`role` do token OIDC; no protótipo ele é escolhido na barra lateral.
"""

PERFIS = {
    "TECNICO": "Técnico de Operação",
    "GESTOR":  "Gestor de Planta",
    "AUDITOR": "Auditor de Compliance",
    "MLOPS":   "Engenheiro de MLOps",
    "ADMIN":   "Administrador",
}

# Usuários de demonstração (simulam o provedor de identidade).
USUARIOS_DEMO = {
    "TECNICO": "tec.joao",
    "GESTOR":  "gestor.ana",
    "AUDITOR": "auditor.paula",
    "MLOPS":   "mlops.rafael",
    "ADMIN":   "admin.carla",
}

# Níveis: "total", "leitura", "resumo", "validacao" ou ausente (sem acesso).
T, L, R, V = "total", "leitura", "resumo", "validacao"

POLITICA = {
    # ── Páginas / recursos (Tabelas 2 e 11) ───────────────────────────────
    "alertas":                {"TECNICO": T, "GESTOR": T, "AUDITOR": L, "MLOPS": T, "ADMIN": T},
    "dashboard":              {"TECNICO": T, "GESTOR": T, "AUDITOR": T, "MLOPS": T, "ADMIN": T},
    "planta_digital":         {"TECNICO": T, "GESTOR": T, "AUDITOR": T, "MLOPS": T, "ADMIN": T},
    "telemetria_tempo_real":  {"TECNICO": T, "GESTOR": R,               "MLOPS": T, "ADMIN": T},
    "historico":              {"TECNICO": L, "GESTOR": T, "AUDITOR": T, "MLOPS": T, "ADMIN": T},
    "lista_equipamentos":     {"TECNICO": T, "GESTOR": T, "AUDITOR": T, "MLOPS": T, "ADMIN": T},
    "cadastro_ativos":        {              "GESTOR": V,               "MLOPS": T, "ADMIN": T},
    "dados_brutos":           {"TECNICO": T,                            "MLOPS": T, "ADMIN": T},
    "log_auditoria":          {              "GESTOR": L, "AUDITOR": T, "MLOPS": T, "ADMIN": T},
    "assistente":             {"TECNICO": T, "GESTOR": T, "AUDITOR": T, "MLOPS": T, "ADMIN": T},
    "usuarios_permissoes":    {                                                     "ADMIN": T},

    # ── Classes de acesso da base de conhecimento (Tabela 19) ─────────────
    "kb_manual_fabricante":   {"TECNICO": T, "GESTOR": T, "AUDITOR": T, "MLOPS": T, "ADMIN": T},
    "kb_procedimento_interno": {"TECNICO": T, "GESTOR": T, "AUDITOR": L, "MLOPS": T, "ADMIN": T},
    "kb_model_card":          {                                         "MLOPS": T, "ADMIN": T},
}

# Recursos que o assistente NUNCA recupera, para nenhum perfil (Tabela 19).
NUNCA_RECUPERAVEL = {"usuarios_permissoes"}

PAGINA_RECURSO = {
    "operations_panel": "alertas",
    "dashboard":        "dashboard",
    "plant_nav":        "planta_digital",
    "telemetry":        "telemetria_tempo_real",
    "alerts":           "historico",
    "equipment_list":   "lista_equipamentos",
    "equipment_form":   "cadastro_ativos",
    "raw_data":         "dados_brutos",
    "assistant":        "assistente",
    "audit_log":        "log_auditoria",
}


class AcessoNegado(PermissionError):
    pass


def nivel(perfil, recurso):
    """Nível de acesso do perfil ao recurso, ou None."""
    return POLITICA.get(recurso, {}).get(perfil)


def pode(perfil, recurso) -> bool:
    return nivel(perfil, recurso) is not None


def exigir(perfil, recurso) -> str:
    """Autorização no back-end: lança AcessoNegado se o perfil não tem acesso."""
    n = nivel(perfil, recurso)
    if n is None:
        raise AcessoNegado(f"Perfil {PERFIS.get(perfil, perfil)} sem acesso a '{recurso}'.")
    return n


def perfis_com_acesso(recurso) -> list:
    return [PERFIS[p] for p in PERFIS if pode(p, recurso)]
