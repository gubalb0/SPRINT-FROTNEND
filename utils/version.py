"""Versões do produto exibidas no cabeçalho (gestão de mudanças, seção 7.7 da documentação)."""

from services import contracts

PRODUTO = "5.0.0"
BASE_CONHECIMENTO = "1.3.0"
MODELO_PREDITIVO = "4.1.0"
ATUALIZADO_EM = "25/11/2026"

# Mudanças MAJOR recentes -> Banner de Ruptura (7 dias antes, 14 dias depois)
BANNER_RUPTURA = (
    "Mudança de interpretação em 25/11/2026: os limiares de temperatura e vibração da tela "
    "passaram a seguir os Metric Contracts (temperatura 75/85/95 °C; vibração 4,5/7,1/11,0 mm/s). "
    "Valores anteriores a essa data foram avaliados pela versão 4.0.0 (70/80 °C e 2,8/4,5 mm/s)."
)

CHANGELOG = [
    ("5.0.0", "MAJOR", "Sprint 4 (Governança): limiares da interface passam a ser lidos dos Metric Contracts "
              "em YAML (muda a interpretação de temperatura e vibração); assistente de troubleshooting com "
              "citação de fonte e log de auditoria; seleção de perfil com autorização na camada de serviço."),
    ("4.0.0", "MAJOR", "Sprint 4 (Front-end): Painel de Alertas como página inicial e fonte única de alertas; "
              "reconhecimento de alertas, feedback de IA, erro amigável, trace_id e testes."),
    ("3.0.1", "PATCH", "Correção dos cards que exibiam código na tela."),
    ("3.0.0", "MAJOR", "Sprint 3: Painel de Alertas e Estados com camada de inteligência."),
]


def linha_versao() -> str:
    return (f"Forzy Motor Intelligence v{PRODUTO} · Metric Contracts v{contracts.versao_conjunto()} · "
            f"Base de conhecimento v{BASE_CONHECIMENTO} · Modelo v{MODELO_PREDITIVO} · "
            f"atualizado em {ATUALIZADO_EM}")
