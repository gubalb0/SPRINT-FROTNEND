"""
METRIC CONTRACTS (Sprint 4 — Governança).

Fonte única dos limiares exibidos na interface e usados pelo motor de alertas.
Os arquivos YAML em `contracts/` são versionados (SemVer + CHANGELOG.md) e
correspondem às Tabelas 12, 13 e 14 da documentação de governança.

Nenhuma página deve ter limiar "hardcoded": todas chamam `faixas(metrica)`.
"""

from functools import lru_cache
from pathlib import Path

import yaml

PASTA = Path(__file__).resolve().parent.parent / "contracts"

# métrica da aplicação -> arquivo do contrato
ARQUIVOS = {
    "vibracao_mms": "MTC-VIB-001.yaml",
    "temperatura_c": "MTC-TMP-001.yaml",
    "aceleracao_g": "MTC-ACC-001.yaml",
}


@lru_cache(maxsize=None)
def carregar(metrica: str) -> dict:
    """Lê o contrato YAML da métrica. Lança KeyError se a métrica não tem contrato."""
    with open(PASTA / ARQUIVOS[metrica], encoding="utf-8") as f:
        return yaml.safe_load(f)


def tem_contrato(metrica: str) -> bool:
    return metrica in ARQUIVOS


def faixas(metrica: str) -> dict:
    """
    Limiares absolutos da métrica:
        {"atencao": 75, "alerta": 85, "critico": 95, "unit": "°C",
         "id": "MTC-TMP-001", "version": "1.1.0"}
    """
    c = carregar(metrica)
    b = c["bands"]
    return {
        "atencao": b["atencao"]["min"],
        "alerta": b["alerta"]["min"],
        "critico": b["critico"]["min"],
        "unit": c["metric"]["unit"],
        "id": c["id"],
        "version": c["version"],
    }


def classificar(metrica: str, valor: float) -> str:
    """Faixa do contrato em que o valor cai: normal | atencao | alerta | critico."""
    f = faixas(metrica)
    if valor >= f["critico"]:
        return "critico"
    if valor >= f["alerta"]:
        return "alerta"
    if valor >= f["atencao"]:
        return "atencao"
    return "normal"


def referencia(metrica: str) -> str:
    """Texto curto para citação: 'MTC-TMP-001 v1.1.0'."""
    f = faixas(metrica)
    return f"{f['id']} v{f['version']}"


def versao_conjunto() -> str:
    """Maior versão entre os contratos vigentes (exibida no cabeçalho)."""
    versoes = [tuple(int(x) for x in carregar(m)["version"].split(".")) for m in ARQUIVOS]
    return ".".join(str(x) for x in max(versoes))
