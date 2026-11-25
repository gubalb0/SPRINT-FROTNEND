# Governança na aplicação — Sprint 4 (GBA)

Onde cada item do documento de governança está implementado no app.

| Item do documento | Onde está no código | Como ver no app |
|---|---|---|
| Metric Contracts (Tabelas 12–14) e diferencial YAML (7.9) | `contracts/*.yaml`, `services/contracts.py` | Telemetria: legenda "Limiares … (contracts/*.yaml)" e faixas 75/85/95 °C e 4,5/7,1/11,0 mm/s |
| Acesso por perfil (Tabelas 2, 11 e 19) | `services/access.py` | Trocar o perfil na barra lateral; Gestor vê telemetria em resumo, Auditor não vê telemetria |
| Autorização no back-end (6.2) | roteador do `app.py` + `access.exigir` nos serviços | Abrir Dados Brutos como Técnico e trocar para Gestor: acesso negado |
| Filtro pré-recuperação e citação de fonte (6.1, 6.4) | `services/assistant.py` | Assistente → "O que devo fazer com o MTR-002?" |
| Sem fonte → revisão humana (Tabela 22) | `assistant.perguntar` | Assistente → "Como calibrar o inversor de frequência do MTR-002?" |
| Acesso negado (6.1) | `PEDIDOS_RESTRITOS` | Como Gestor → "Qual o valor bruto do ADC do MTR-002?" |
| Log de auditoria (Tabela 21) | `assistant._anexar_log` (append-only, HMAC, pseudônimo) | 🧾 Log de Auditoria (Gestor, Auditor, MLOps, Admin) |
| Logs sem segredos e credenciais fora do código (6.2) | `assistant.sanitizar`, variáveis `FORZY_AUDIT_KEY` e `FORZY_PSEUDO_SALT` | Aviso de chave de desenvolvimento no Log de Auditoria |
| Gestão de mudanças (7.7) | `utils/version.py` | Cabeçalho com versões, Changelog e Banner de Ruptura com "Li e entendi" |
| Gates de promoção (7.2) | `tests/test_governanca.py` (MAT, regressão do assistente) | `python -m pytest -q` |

Capturas em [`img/`](img/).

> A base de conhecimento (`services/knowledge_base.py`) contém resumos simulados escritos pelo grupo; não reproduz os manuais dos fabricantes.
