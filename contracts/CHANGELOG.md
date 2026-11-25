# Changelog — Metric Contracts Forzy

Formato baseado em Keep a Changelog; versões seguem SemVer.

## [MTC-TMP-001 1.1.0] — 2026-11-23
### Adicionado
- Bloco `plausibility`: leitura abaixo de 5 °C, 5 °C abaixo da temperatura ambiente
  ou variância zero por 10 minutos passa a ser amostra inválida.
- Origem: ação corretiva do postmortem PM-2026-001 (sensor de temperatura do MTR-002 enviando zeros).
### Inalterado
- Faixas normal/atenção/alerta/crítico, janela de 300 s e amostras mínimas (sem ruptura, por isso MINOR).

## [MTC-VIB-001 1.0.0] / [MTC-TMP-001 1.0.0] / [MTC-ACC-001 1.0.0] — 2026-10
### Adicionado
- Versão inicial dos contratos definidos na Sprint 3 (Tabelas 12, 13 e 14 do documento).
