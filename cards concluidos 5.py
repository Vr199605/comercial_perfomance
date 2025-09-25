# dashboard_google_sheets_completo.py
# 📊 Dashboard de Metas - Streamlit + Google Sheets

import sys
import subprocess

# ----------------------------
# Instalação automática de pacotes se não estiverem presentes
# ----------------------------
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

for pkg in ["streamlit==1.27.0", "pandas==2.1.1", "plotly==5.16.1", "gspread==5.11.0", "google-auth==2.27.0"]:
    try:
        __import__(pkg.split("==")[0])
    except ImportError:
        install(pkg)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import gspread
from google.oauth2.service_account import Credentials

# ----------------------------
# CONFIGURAÇÃO DA PÁGINA
# ----------------------------
st.set_page_config(
    page_title="Dashboard de Metas - Performance Comercial",
    layout="wide",
    page_icon="📊"
)

# ----------------------------
# CONFIGURAÇÃO GOOGLE SHEETS
# ----------------------------
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSlQ9u5x09qR0dAKJsMC-fXTvJWRWPzMrXpaGaojOPblRrJYbx4Q-xalzh2hmf2WtwHRoLVIBOdL_HC/pub?output=csv"

# ----------------------------
# MAPEAMENTO DE NOMES (baseado na planilha)
# ----------------------------
NOME_MAPPING = {
    'Werbet': 'Werbet', 'Werker Alencar': 'Werbet', 'Werbet Alencar': 'Werbet',
    'Pamela': 'Pamela', 'Pamela Crédita': 'Pamela', 'Pamela Cri': 'Pamela', 'Pamela Cristina': 'Pamela',
    'Ana Clara': 'Ana Clara', 'Ana Clara Souza': 'Ana Clara',
    'Danilo': 'Danilo', 'Danilo Neder': 'Danilo',
    'Natalie': 'Natalie', 'Natalie Lopes': 'Natalie',
    'Andressa': 'Andressa',
    'Rafael': 'Rafael', 'Rafael Miguel': 'Rafael',
    'Thaís': 'Thaís', 'Thais Mendonca': 'Thaís', 'Thais': 'Thaís', 'Thaki': 'Thaís'
}

# ----------------------------
# METAS MENSAIS (baseado na estrutura da planilha)
# ----------------------------
META_MENSAL_POR_COMERCIAL = {
    "Janeiro": { "Andressa": 22, "Rafael": 22, "Thaís": 22, "Ana Clara": 44, "Danilo": 44, "Pamela": 44, "Natalie": 44, "Werbet": 44 },
    "Fevereiro": { "Andressa": 20, "Rafael": 20, "Thaís": 20, "Ana Clara": 40, "Danilo": 40, "Pamela": 40, "Natalie": 40, "Werbet": 40 },
    "Março": { "Andressa": 21, "Rafael": 21, "Thaís": 21, "Ana Clara": 42, "Danilo": 42, "Pamela": 42, "Natalie": 42, "Werbet": 42 },
    "Abril": { "Andressa": 22, "Rafael": 22, "Thaís": 22, "Ana Clara": 44, "Danilo": 44, "Pamela": 44, "Natalie": 44, "Werbet": 44 },
    "Maio": { "Andressa": 22, "Rafael": 22, "Thaís": 22, "Ana Clara": 44, "Danilo": 44, "Pamela": 44, "Natalie": 44, "Werbet": 44 },
    "Junho": { "Andressa": 21, "Rafael": 21, "Thaís": 21, "Ana Clara": 42, "Danilo": 42, "Pamela": 42, "Natalie": 42, "Werbet": 42 },
    "Julho": { "Andressa": 23, "Rafael": 23, "Thaís": 23, "Ana Clara": 46, "Danilo": 46, "Pamela": 46, "Natalie": 46, "Werbet": 46 },
    "Agosto": { "Andressa": 21, "Rafael": 21, "Thaís": 21, "Ana Clara": 42, "Danilo": 42, "Pamela": 42, "Natalie": 42, "Werbet": 42 },
    "Setembro": { "Andressa": 22, "Rafael": 22, "Thaís": 22, "Ana Clara": 44, "Danilo": 44, "Pamela": 44, "Natalie": 44, "Werbet": 44 },
    "Outubro": { "Andressa": 23, "Rafael": 23, "Thaís": 23, "Ana Clara": 46, "Danilo": 46, "Pamela": 46, "Natalie": 46, "Werbet": 46 },
    "Novembro": { "Andressa": 21, "Rafael": 21, "Thaís": 21, "Ana Clara": 42, "Danilo": 42, "Pamela": 42, "Natalie": 42, "Werbet": 42 },
    "Dezembro": { "Andressa": 22, "Rafael": 22, "Thaís": 22, "Ana Clara": 44, "Danilo": 44, "Pamela": 44, "Natalie": 44, "Werbet": 44 }
}

# ----------------------------
# FUNÇÃO DE META TOTAL
# ----------------------------
def meta_mensal_total(nome, meses):
    return sum(META_MENSAL_POR_COMERCIAL[m].get(nome, 0) for m in meses)

# ----------------------------
# CARREGAR DADOS DO GOOGLE SHEETS
# ----------------------------
@st.cache_data(ttl=300)  # Cache de 5 minutos
def load_data():
    try:
        # Carregar dados diretamente do CSV público
        df = pd.read_csv(SHEET_URL)
        
        if df.empty:
            st.warning("⚠ A planilha está vazia ou não foi possível carregar os dados.")
            return create_sample_data()
        
        # Verificar e mapear colunas baseado na estrutura da planilha
        required_columns = ['Data de Conclusão', 'Comercial/Capitão']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.warning(f"⚠ Colunas faltantes na planilha: {missing_columns}")
            st.info("Tentando identificar colunas similares...")
            
            # Tentar encontrar colunas similares
            column_mapping = {}
            for required in required_columns:
                for actual in df.columns:
                    if required.lower() in actual.lower() or actual.lower() in required.lower():
                        column_mapping[required] = actual
                        break
            
            if len(column_mapping) == len(required_columns):
                df = df.rename(columns=column_mapping)
                st.success("✅ Colunas mapeadas com sucesso!")
            else:
                st.error("❌ Não foi possível mapear todas as colunas necessárias.")
                return create_sample_data()
        
        # Processar datas
        df['Data de Conclusão'] = pd.to_datetime(df['Data de Conclusão'], dayfirst=True, errors='coerce')
        df.dropna(subset=['Data de Conclusão'], inplace=True)
        
        if df.empty:
            st.warning("⚠ Nenhuma data válida encontrada após processamento.")
            return create_sample_data()
        
        # Extrair ano e mês
        df['Ano'] = df['Data de Conclusão'].dt.year
        df['Mês'] = df['Data de Conclusão'].dt.strftime('%B')
        
        # Traduzir meses para português
        meses_trad = {
            'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março', 'April': 'Abril',
            'May': 'Maio', 'June': 'Junho', 'July': 'Julho', 'August': 'Agosto',
            'September': 'Setembro', 'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
        }
        df['Mês'] = df['Mês'].map(meses_trad).fillna(df['Mês'])

        # Padronizar nomes dos comerciais
        df['Comercial_Padronizado'] = df['Comercial/Capitão'].astype(str)
        for nome_ori, nome_pad in NOME_MAPPING.items():
            df.loc[df['Comercial/Capitão'].str.contains(nome_ori, case=False, na=False), 'Comercial_Padronizado'] = nome_pad

        # Filtrar apenas nomes válidos
        nomes_validos = list(NOME_MAPPING.values())
        df = df[df['Comercial_Padronizado'].isin(nomes_validos)]
        
        st.success(f"✅ Dados carregados com sucesso! {len(df)} registros encontrados.")
        return df

    except Exception as e:
        st.error(f"❌ Erro ao carregar dados da planilha: {str(e)}")
        st.info("📋 Usando dados de exemplo para demonstração.")
        return create_sample_data()

def create_sample_data():
    """Criar dados de exemplo baseado na estrutura da planilha real"""
    sample_data = {
        'Data de Conclusão': pd.to_datetime([
            '2025-01-15', '2025-01-20', '2025-02-10', '2025-02-25', '2025-03-05',
            '2025-03-15', '2025-04-10', '2025-04-20', '2025-05-05', '2025-05-25'
        ]),
        'Comercial/Capitão': [
            'Andressa', 'Rafael', 'Thaís', 'Ana Clara', 'Danilo',
            'Pamela', 'Natalie', 'Werbet', 'Andressa', 'Rafael'
        ]
    }
    df_exemplo = pd.DataFrame(sample_data)
    df_exemplo['Ano'] = df_exemplo['Data de Conclusão'].dt.year
    df_exemplo['Mês'] = df_exemplo['Data de Conclusão'].dt.strftime('%B').map({
        'January':'Janeiro','February':'Fevereiro','March':'Março',
        'April':'Abril','May':'Maio'
    }).fillna('Janeiro')
    df_exemplo['Comercial_Padronizado'] = df_exemplo['Comercial/Capitão']
    return df_exemplo

# ----------------------------
# ESTILO CSS
# ----------------------------
st.markdown("""
<style>
.big-font { 
    font-size:30px !important; 
    font-weight: bold; 
    color: #0d6efd; 
    text-align: center;
    margin-bottom: 20px;
}
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
    border-radius: 10px;
    color: white;
    margin: 10px 0;
}
.metric-value {
    font-size: 2.5em;
    font-weight: bold;
    text-align: center;
}
.metric-label {
    font-size: 1.2em;
    text-align: center;
    opacity: 0.9;
}
.stDataFrame div.row_heading, .stDataFrame div.col_heading { 
    font-weight: bold; 
    font-size: 16px; 
}
.stDataFrame td { 
    padding: 8px; 
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# FUNÇÃO DE COR PARA KPI
# ----------------------------
def color_atingimento(val):
    if val >= 100:
        return 'background-color: #28a745; color: white; font-weight: bold'
    elif val >= 80:
        return 'background-color: #ffc107; color: black; font-weight: bold'
    else:
        return 'background-color: #dc3545; color: white; font-weight: bold'

# ----------------------------
# FUNÇÃO PARA CRIAR CARDS DE MÉTRICA
# ----------------------------
def metric_card(title, value, delta=None, delta_color="normal"):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{title}</div>
            <div class="metric-value">{value}</div>
            {f'<div style="text-align: center; font-size: 1.1em;">{delta}</div>' if delta else ''}
        </div>
        """, unsafe_allow_html=True)

# ----------------------------
# CARREGAR DADOS
# ----------------------------
df = load_data()

# ----------------------------
# DASHBOARD
# ----------------------------
if df.empty:
    st.error("❌ Nenhum dado disponível para exibição.")
else:
    tab_intro, tab_mensal, tab_anual, tab_totais, tab_explicacao = st.tabs([
        "✨ Apresentação", 
        "📊 Performance Mensal", 
        "📈 Consolidado Anual",
        "🏆 Resultados Totais",
        "📘 Como Usar"
    ])

    # ABA INTRO
    with tab_intro:
        st.markdown('<h1 class="big-font">🚀 Dashboard de Performance Comercial</h1>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ## 🌟 Bem-vindo ao nosso painel de performance!
            
            Este dashboard foi desenvolvido para acompanhar o desempenho da equipe comercial com base nos dados da planilha Google Sheets.
            
            **📈 Funcionalidades principais:**
            - ✅ Acompanhamento em tempo real das metas
            - 📊 Análise mensal e anual
            - 🎯 Comparativo entre realizado vs meta
            - 👥 Performance individual por comercial
            - 📱 Visualização responsiva e intuitiva
            
            **🔗 Fonte dos dados:** [Planilha Google Sheets](""" + SHEET_URL + """)
            """)
        
        with col2:
            st.image("https://cdn-icons-png.flaticon.com/512/5968/5968344.png", width=150)
            st.metric("Total de Registros", len(df))
            st.metric("Período Coberto", f"{df['Ano'].min()} - {df['Ano'].max()}")
            st.metric("Comerciais Ativos", df['Comercial_Padronizado'].nunique())
        
        # Mostrar prévia dos dados
        with st.expander("🔍 Visualizar Dados Carregados"):
            st.dataframe(df.head(10), use_container_width=True)

    # ABA PERFORMANCE MENSAL
    with tab_mensal:
        st.header("📊 Performance Mensal")
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            anos_disponiveis = sorted(df['Ano'].unique())
            ano_selecionado = st.selectbox("**Selecione o Ano:**", anos_disponiveis, index=len(anos_disponiveis)-1)
        
        with col2:
            ordem_meses = list(META_MENSAL_POR_COMERCIAL.keys())
            meses_disponiveis = sorted(df['Mês'].unique(), key=lambda x: ordem_meses.index(x) if x in ordem_meses else len(ordem_meses))
            meses_selecionados = st.multiselect("**Selecione os Meses:**", meses_disponiveis, default=meses_disponiveis)
        
        with col3:
            todos_comerciais = sorted(df['Comercial_Padronizado'].unique())
            comerciais_selecionados = st.multiselect("**Filtrar Comerciais:**", todos_comerciais, default=todos_comerciais)
        
        # Aplicar filtros
        df_filtrado = df[
            (df['Ano'] == ano_selecionado) & 
            (df['Mês'].isin(meses_selecionados)) &
            (df['Comercial_Padronizado'].isin(comerciais_selecionados))
        ]
        
        if not df_filtrado.empty and meses_selecionados:
            # Tabela de performance
            tabela_mensal = df_filtrado.groupby('Comercial_Padronizado').size().reset_index(name='Realizado')
            tabela_mensal['Meta'] = tabela_mensal['Comercial_Padronizado'].apply(lambda x: meta_mensal_total(x, meses_selecionados))
            tabela_mensal['Atingimento (%)'] = (tabela_mensal['Realizado'] / tabela_mensal['Meta'] * 100).round(2)
            tabela_mensal['Diferença'] = tabela_mensal['Realizado'] - tabela_mensal['Meta']
            
            # Ordenar por atingimento
            tabela_mensal = tabela_mensal.sort_values('Atingimento (%)', ascending=False)
            
            # Exibir métricas resumidas
            total_realizado = tabela_mensal['Realizado'].sum()
            total_meta = tabela_mensal['Meta'].sum()
            atingimento_geral = (total_realizado / total_meta * 100) if total_meta > 0 else 0
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                metric_card("Total Realizado", total_realizado)
            with col2:
                metric_card("Total Meta", total_meta)
            with col3:
                metric_card("Atingimento", f"{atingimento_geral:.1f}%")
            with col4:
                metric_card("Diferença", total_realizado - total_meta)
            
            # Tabela detalhada
            st.subheader("📋 Detalhamento por Comercial")
            styled_table = tabela_mensal.style.format({
                'Atingimento (%)': '{:.2f}%',
                'Meta': '{:.0f}',
                'Realizado': '{:.0f}',
                'Diferença': '{:.0f}'
            }).applymap(color_atingimento, subset=['Atingimento (%)'])
            
            st.dataframe(styled_table, use_container_width=True)
            
            # Gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de barras comparativo
                fig_barras = px.bar(
                    tabela_mensal, 
                    x='Comercial_Padronizado', 
                    y=['Realizado', 'Meta'],
                    barmode='group',
                    title=f'Realizado vs Meta - {ano_selecionado}',
                    labels={'value': 'Quantidade', 'variable': 'Tipo'},
                    text_auto=True
                )
                fig_barras.update_layout(xaxis_title="Comercial", yaxis_title="Quantidade")
                st.plotly_chart(fig_barras, use_container_width=True)
            
            with col2:
                # Gráfico de pizza do atingimento geral
                fig_pie = px.pie(
                    names=['Atingido', 'Falta Atingir'],
                    values=[total_realizado, max(0, total_meta - total_realizado)],
                    title=f"Atingimento Geral: {atingimento_geral:.1f}%",
                    color=['Atingido', 'Falta Atingir'],
                    color_discrete_map={'Atingido': '#28a745', 'Falta Atingir': '#dc3545'}
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # Gráfico de evolução mensal
            st.subheader("📈 Evolução Mensal")
            evolucao_mensal = df_filtrado.groupby('Mês').size().reset_index(name='Realizado')
            # Ordenar meses corretamente
            evolucao_mensal['Mês'] = pd.Categorical(evolucao_mensal['Mês'], categories=ordem_meses, ordered=True)
            evolucao_mensal = evolucao_mensal.sort_values('Mês')
            
            fig_evolucao = px.line(
                evolucao_mensal,
                x='Mês',
                y='Realizado',
                title='Evolução do Realizado ao Longo dos Meses',
                markers=True
            )
            st.plotly_chart(fig_evolucao, use_container_width=True)
            
        else:
            st.warning("⚠ Selecione pelo menos um mês para visualizar os dados.")

    # ABA CONSOLIDADO ANUAL
    with tab_anual:
        st.header("📈 Consolidado Anual")
        
        col1, col2 = st.columns(2)
        
        with col1:
            ano_anual = st.selectbox("**Ano para Análise:**", anos_disponiveis, index=len(anos_disponiveis)-1, key="ano_anual")
        
        with col2:
            # Opções de períodos
            periodo_opcoes = {
                "Ano Completo": list(META_MENSAL_POR_COMERCIAL.keys()),
                "1º Semestre": ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho"],
                "2º Semestre": ["Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"],
                "Personalizado": None
            }
            periodo_selecionado = st.selectbox("**Período:**", list(periodo_opcoes.keys()))
            
            if periodo_selecionado == "Personalizado":
                meses_personalizado = st.multiselect("**Selecione os Meses:**", list(META_MENSAL_POR_COMERCIAL.keys()))
                meses_analise = meses_personalizado
            else:
                meses_analise = periodo_opcoes[periodo_selecionado]
        
        if meses_analise:
            df_anual = df[(df['Ano'] == ano_anual) & (df['Mês'].isin(meses_analise))]
            
            if not df_anual.empty:
                # Tabela consolidada
                tabela_anual = df_anual.groupby('Comercial_Padronizado').size().reset_index(name='Realizado')
                tabela_anual['Meta'] = tabela_anual['Comercial_Padronizado'].apply(lambda x: meta_mensal_total(x, meses_analise))
                tabela_anual['Atingimento (%)'] = (tabela_anual['Realizado'] / tabela_anual['Meta'] * 100).round(2)
                tabela_anual = tabela_anual.sort_values('Atingimento (%)', ascending=False)
                
                # Métricas gerais
                total_realizado_anual = tabela_anual['Realizado'].sum()
                total_meta_anual = tabela_anual['Meta'].sum()
                atingimento_anual = (total_realizado_anual / total_meta_anual * 100) if total_meta_anual > 0 else 0
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    metric_card("Realizado Anual", total_realizado_anual)
                with col2:
                    metric_card("Meta Anual", total_meta_anual)
                with col3:
                    metric_card("Atingimento", f"{atingimento_anual:.1f}%")
                
                # Visualizações
                col1, col2 = st.columns(2)
                
                with col1:
                    # Gráfico de barras horizontal
                    fig_bar_h = px.bar(
                        tabela_anual.sort_values('Atingimento (%)'),
                        y='Comercial_Padronizado',
                        x='Atingimento (%)',
                        title='Atingimento por Comercial (%)',
                        orientation='h',
                        color='Atingimento (%)',
                        color_continuous_scale='RdYlGn'
                    )
                    st.plotly_chart(fig_bar_h, use_container_width=True)
                
                with col2:
                    # Gráfico de radar
                    fig_radar = go.Figure()
                    
                    for _, row in tabela_anual.iterrows():
                        fig_radar.add_trace(go.Scatterpolar(
                            r=[row['Realizado'], row['Meta'], row['Atingimento (%)']/20],  # Escalar o atingimento
                            theta=['Realizado', 'Meta', 'Atingimento'],
                            fill='toself',
                            name=row['Comercial_Padronizado']
                        ))
                    
                    fig_radar.update_layout(
                        polar=dict(
                            radialaxis=dict(visible=True, range=[0, max(tabela_anual[['Realizado', 'Meta']].max().max(), 50)])
                        ),
                        title="Comparativo por Comercial - Radar"
                    )
                    st.plotly_chart(fig_radar, use_container_width=True)
                
                # Tabela detalhada
                st.subheader("📊 Tabela Consolidada")
                st.dataframe(
                    tabela_anual.style.format({
                        'Atingimento (%)': '{:.2f}%',
                        'Meta': '{:.0f}',
                        'Realizado': '{:.0f}'
                    }).applymap(color_atingimento, subset=['Atingimento (%)']),
                    use_container_width=True
                )
                
            else:
                st.warning(f"⚠ Nenhum dado encontrado para {ano_anual} no período selecionado.")

    # ABA RESULTADOS TOTAIS
    with tab_totais:
        st.header("🏆 Resultados Totais")
        
        # Estatísticas gerais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_geral = len(df)
            metric_card("Total Geral de Vendas", total_geral)
        
        with col2:
            comercial_top = df['Comercial_Padronizado'].value_counts().index[0]
            metric_card("Top Comercial", comercial_top)
        
        with col3:
            mes_top = df['Mês'].value_counts().index[0]
            metric_card("Mês com Mais Vendas", mes_top)
        
        with col4:
            ano_top = df['Ano'].value_counts().index[0]
            metric_card("Ano com Mais Vendas", ano_top)
        
        # Análise temporal
        st.subheader("📈 Tendência Temporal")
        evolucao_anual = df.groupby('Ano').size().reset_index(name='Vendas')
        fig_tendencia = px.line(evolucao_anual, x='Ano', y='Vendas', title='Evolução Anual das Vendas', markers=True)
        st.plotly_chart(fig_tendencia, use_container_width=True)
        
        # Distribuição por comercial
        st.subheader("👥 Distribuição por Comercial")
        dist_comercial = df['Comercial_Padronizado'].value_counts().reset_index()
        dist_comercial.columns = ['Comercial', 'Vendas']
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_dist = px.pie(dist_comercial, values='Vendas', names='Comercial', title='Distribuição de Vendas por Comercial')
            st.plotly_chart(fig_dist, use_container_width=True)
        
        with col2:
            fig_bar_dist = px.bar(dist_comercial, x='Vendas', y='Comercial', orientation='h', title='Vendas por Comercial')
            st.plotly_chart(fig_bar_dist, use_container_width=True)

    # ABA EXPLICAÇÃO
    with tab_explicacao:
        st.header("📘 Como Usar o Dashboard")
        
        st.markdown("""
        ## 🎯 Objetivo do Dashboard
        
        Este dashboard foi criado para acompanhar o desempenho da equipe comercial com base nos dados da planilha Google Sheets.
        
        ## 📊 Abas do Dashboard
        
        ### ✨ Apresentação
        - Visão geral do sistema
        - Estatísticas rápidas
        - Prévia dos dados carregados
        
        ### 📊 Performance Mensal
        - Análise detalhada por mês/ano
        - Filtros por comercial e período
        - Gráficos comparativos
        - Evolução temporal
        
        ### 📈 Consolidado Anual
        - Visão anual e por semestre
        - Gráfico de radar para comparação
        - Análise de atingimento
        
        ### 🏆 Resultados Totais
        - Métricas gerais
        - Tendências temporais
        - Distribuição por comercial
        
        ## 🔧 Funcionalidades
        
        ### Filtros Interativos
        - Selecione anos, meses e comerciais
        - Períodos pré-definidos (semestres)
        - Filtros personalizados
        
        ### Visualizações
        - **Gráficos de Barras**: Comparação realizado vs meta
        - **Gráficos de Pizza**: Distribuição percentual
        - **Gráficos de Linha**: Evolução temporal
        - **Gráficos de Radar**: Comparação multidimensional
        
        ### Cores e Indicadores
        - 🟢 **Verde**: Meta atingida ou superada (≥100%)
        - 🟡 **Amarelo**: Próximo da meta (80-99%)
        - 🔴 **Vermelho**: Abaixo da meta (<80%)
        
        ## 📁 Fonte dos Dados
        
        Os dados são carregados automaticamente da planilha Google Sheets pública:
        - Atualização automática a cada 5 minutos
        - Fallback para dados de exemplo em caso de erro
        - Validação de estrutura de dados
        
        ## 💡 Dicas de Uso
        
        1. **Comece pela aba Mensal** para análises detalhadas
        2. **Use a aba Anual** para visão estratégica
        3. **Consulte a aba Totais** para métricas gerais
        4. **Filtre por períodos específicos** para análises focadas
        5. **Compare comerciais** usando os gráficos de radar
        """)

# ----------------------------
# RODAPÉ
# ----------------------------
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Dashboard de Performance Comercial • Desenvolvido com Streamlit • Dados carregados de Google Sheets</p>
    <p>Última atualização: """ + pd.Timestamp.now().strftime("%d/%m/%Y %H:%M") + """</p>
</div>
""", unsafe_allow_html=True)