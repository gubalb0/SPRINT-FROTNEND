# ⚡ Forzy Motor Intelligence

> Interface de monitoramento e apoio à decisão para motores elétricos industriais.
> Desenvolvido com **Streamlit + pandas + Plotly** e identidade visual **Forzy / Promon**.
> Challenge Forzy — disciplina de Front-End — FIAP, turma 2TIAPY.

📄 **Documentação final (Sprint 4):** [`docs/DOCUMENTACAO_FINAL.md`](docs/DOCUMENTACAO_FINAL.md) · [PDF](docs/DOCUMENTACAO_FINAL.pdf)
🎬 **Vídeo de demonstração (Sprint 3):** [`docs/video/sprint3_demo.mp4`](docs/video/sprint3_demo.mp4)

| Integrante | RM |
|---|---|
| Gustavo Balbo Saraiva | 561711 |
| Henry Gimenez | 563217 |
| Ian Nobres | 561681 |
| Matheus Mikio | 561864 |
| Vinícius Araújo | 564504 |

---

## 🚀 Como rodar

```bash
pip install -r requirements.txt
streamlit run app.py          # abre em http://localhost:8501
```

Testes dos serviços:

```bash
pip install pytest
python -m pytest -q
```

Demonstração do tratamento de erro (o modelo "cai" a partir do 2º ciclo):

```bash
FORZY_SIMULAR_FALHA=1 streamlit run app.py
```

---

## 🧭 Jornada do usuário

1. **Monitorar** — o app abre no *Painel de Alertas e Estados* (KPIs, resumo executivo por NLP, estado de cada ativo).
2. **Receber alerta** — *Atualizar Análise* (ou modo Auto, 15 s) executa um ciclo do modelo; novos alertas e mudanças de estado são notificados.
3. **Agir** — o card traz resumo em linguagem natural e plano de ação (prazo, equipe, passos); o operador abre Telemetria/Ficha, clica em **✔ Reconhecer** e avalia o resumo da IA (👍/👎). Tudo fica no *Histórico* com `trace_id` e pode ser exportado em CSV.

Use **♻️ Reiniciar Simulação** na barra lateral para recomeçar o cenário de demonstração.

---

## 🗂️ Estrutura

```
app.py                     # entry point: sidebar, badges e roteador de páginas
pages/
  operations_panel.py      # Painel de Alertas e Estados (página inicial)
  alerts.py                # Histórico de eventos (filtros, CSV, trace_id)
  dashboard.py             # Visão geral do parque
  plant_nav.py             # Plantas → Áreas → Ativos
  telemetry.py             # Séries temporais e leitura de placa
  equipment_list.py        # Lista de equipamentos
  equipment_form.py        # Cadastro / edição / ficha técnica
  raw_data.py              # Dados brutos ADC → unidades de engenharia
components/
  cards.py                 # Componentes visuais reutilizáveis + paleta semântica
services/
  monitoring.py            # Orquestração do ciclo, trace_id, reconhecimento, feedback
  alert_engine.py          # Modelo analítico (simulado) + contrato e validação
  nlp_service.py           # Resumos e recomendações (templates, substituível por LLM)
utils/
  session.py               # Estado da sessão e dados de exemplo
  theme.py                 # CSS / identidade Forzy
tests/
  test_services.py         # Testes automatizados (pytest)
docs/
  DOCUMENTACAO_FINAL.md    # Documentação da Sprint 4 (+ PDF e imagens)
```

---

## 📈 Evolução por sprint

| Sprint | Entregável |
|---|---|
| 1 | Cadastro técnico do ativo, lista, ficha técnica, dados brutos |
| 2 | Dashboards de telemetria, séries temporais, navegação por plantas |
| 3 | Painel de Alertas e Estados com modelo analítico simulado + NLP e apoio à decisão |
| 4 | Consolidação: fonte única de alertas, página inicial correta, reconhecimento de alertas, feedback de IA, `trace_id`, erro amigável, testes e documentação final |

---

## 🎨 Design system

| Token | Valor | Uso |
|---|---|---|
| `--orange` | `#FF6B00` | Cor primária, CTAs, TAGs |
| `--purple` | `#3D1A6E` | Sidebar, títulos |
| `--yellow` | `#F5C400` | Destaques |
| `critico` | `#DC3545` | Estado crítico |
| `atencao` | `#FFC107` | Estado de atenção |
| `normal` | `#28A745` | Estado normal |

Fontes: **Barlow Condensed** (títulos) + **Inter** (corpo).

---

*Desenvolvido para o desafio Forzy — uma empresa Promon. "for an easy tomorrow"*
