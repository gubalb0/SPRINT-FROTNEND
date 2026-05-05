# ⚡ Forzy Motor Intelligence — Sprint 1

> Interface de cadastro técnico e visualização de dados de motores elétricos.
> Desenvolvido com **Streamlit** e identidade visual **Forzy / Promon**.

---

## 🗂️ Estrutura do Projeto

```
forzy_app/
│
├── app.py                  # Entry point — roteador de páginas + sidebar
│
├── pages/
│   ├── __init__.py
│   ├── dashboard.py        # Visão geral com KPIs e resumo
│   ├── equipment_list.py   # Lista/datatable de equipamentos com filtros
│   ├── equipment_form.py   # Formulário de cadastro, edição e ficha técnica
│   └── raw_data.py         # Visualização de dados brutos com conversão
│
├── utils/
│   ├── __init__.py
│   ├── session.py          # Inicialização do session state e dados de exemplo
│   └── theme.py            # CSS customizado com identidade Forzy (inject_css)
│
├── data/                   # (Futuro) persistência em JSON/SQLite
├── assets/                 # (Futuro) imagens, logos, ícones
│
├── requirements.txt
└── README.md
```

---

## 🚀 Como Rodar Localmente

### 1. Pré-requisitos
- Python 3.9+
- pip

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Executar

```bash
streamlit run app.py
```

A aplicação abrirá em `http://localhost:8501`.

---

## 📋 Funcionalidades — Sprint 1

### 🏠 Dashboard
- KPIs: total de equipamentos, ativos, em manutenção, inativos
- Tabela com últimos equipamentos cadastrados
- Estatísticas de potência total e fabricantes
- Ações rápidas (cadastrar, listar, dados)

### 📋 Lista de Equipamentos
- Datatable responsivo com todos os equipamentos
- Filtros por nome/TAG, fabricante e status
- Cards expansivos com dados principais
- Botões de ação: Ficha Técnica, Editar, Dados Brutos

### ➕ Cadastro / Ficha Técnica
- Formulário com validação de campos obrigatórios
- Seções: Identificação, Dados Elétricos, Proteção & Isolamento, Observações
- Modo Ficha Técnica (read-only) e Edição
- Feedback visual de sucesso/erro

### 📊 Dados Brutos
- Seleção de equipamento
- Cards de sensores com valores convertidos em unidades de engenharia:
  - Tensão (V), Corrente (A), Rotação (RPM), Temperatura (°C), Vibração (mm/s), Potência (kW)
- Indicadores de status semântico (verde/amarelo/vermelho)
- Exposição dos valores RAW de ADC (0–4095)
- Tabela de fatores de conversão por canal
- Gráfico histórico simulado (linha de tendência)

---

## 🎨 Design System

| Token         | Valor     | Uso                        |
|---------------|-----------|----------------------------|
| `--orange`    | `#FF6B00` | Cor primária, CTAs, destaques |
| `--purple`    | `#3D1A6E` | Sidebar, headers, títulos  |
| `--yellow`    | `#F5C400` | Alertas, KPI de atenção    |
| `--success`   | `#28A745` | Status ativo / OK          |
| `--warning`   | `#FFC107` | Status manutenção / alerta |
| `--danger`    | `#DC3545` | Status inativo / crítico   |

Fontes: **Barlow Condensed** (display/títulos) + **Inter** (corpo/labels)

---

## 🔮 Roadmap — Próximas Sprints

| Sprint | Entregável                                               |
|--------|----------------------------------------------------------|
| 2      | Integração com sensores reais (MQTT / API REST)          |
| 2      | Persistência em SQLite ou banco de séries temporais      |
| 3      | Modelo de ML para detecção de anomalias                  |
| 3      | Alertas automáticos (e-mail / webhook)                   |
| 4      | Dashboard preditivo com horizon de manutenção            |

---

## 🏗️ Decisões de Arquitetura

- **Desacoplamento frontend/backend**: as páginas consomem apenas `st.session_state` e funções utilitárias — o modelo de ML pode ser integrado em `utils/model.py` sem alterar nenhuma página.
- **Framework substituível**: todo o CSS vive em `utils/theme.py`. Migrar de Streamlit para Gradio ou FastAPI+React exige apenas reescrever as páginas, sem alterar lógica de negócio.
- **Dados mockados**: `utils/session.py` popula dados de exemplo no `session_state`. Na Sprint 2, basta substituir esse seed por uma chamada ao banco de dados.

---

*Desenvolvido para o desafio Forzy — uma empresa Promon.*
*"for an easy tomorrow"*
