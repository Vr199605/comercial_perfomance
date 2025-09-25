# 📊 Dashboard de Metas - Performance Comercial

Este projeto é um **dashboard interativo em Streamlit** que conecta-se ao **Google Sheets** para exibir a performance da equipe comercial em tempo real.

## 🚀 Funcionalidades
- ✅ Acompanhamento em tempo real das metas
- 📊 Análise mensal e anual
- 🎯 Comparativo entre realizado vs meta
- 👥 Performance individual por comercial
- 📱 Visualização responsiva e intuitiva

## 🛠️ Pré-requisitos
- Python 3.9+ instalado
- Conta Google com acesso ao Google Sheets (se usar credenciais privadas)
- Git (opcional, se for clonar via repositório)

## 📦 Instalação

Clone este repositório (ou baixe o arquivo `.py` diretamente):

```bash
git clone https://github.com/seu-usuario/dashboard-metas.git
cd dashboard-metas
```

Crie e ative um ambiente virtual (recomendado):

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

## ▶️ Como Executar

Na raiz do projeto, rode o comando:

```bash
streamlit run dashboard_google_sheets_completo.py
```

O Streamlit abrirá automaticamente no navegador padrão em `http://localhost:8501`.

## 🔗 Fonte de Dados

Os dados vêm da planilha pública no Google Sheets (CSV exportado):

- [Planilha Google Sheets](https://docs.google.com/spreadsheets/d/e/2PACX-1vSlQ9u5x09qR0dAKJsMC-fXTvJWRWPzMrXpaGaojOPblRrJYbx4Q-xalzh2hmf2WtwHRoLVIBOdL_HC/pub?output=csv)

## 📂 Estrutura do Projeto

```
📊 dashboard-metas/
 ├── dashboard_google_sheets_completo.py   # Código principal do dashboard
 ├── requirements.txt                      # Dependências do projeto
 └── README.md                             # Documentação
```

---

## ✨ Demonstração

![Exemplo de Dashboard](https://cdn-icons-png.flaticon.com/512/5968/5968344.png)

---

👨‍💻 Desenvolvido com ❤️ usando **Python + Streamlit + Google Sheets**
