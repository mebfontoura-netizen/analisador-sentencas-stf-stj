# ============================================
# Analisador de Sentenças do STF/STJ — Versão 2.3 (Base real em Excel)
# Desenvolvido por: Maria Eduarda de Bustamante Fontoura e Nicolly Soares Motta
# ============================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random

# ---------- CONFIGURAÇÃO ----------
st.set_page_config(page_title="Analisador de Sentenças do STF/STJ", page_icon="⚖️", layout="wide")
st.title("⚖️ Analisador de Sentenças do STF/STJ — Base real (Excel do STF)")
st.markdown("""
Aplicativo desenvolvido para análise quantitativa de jurisprudência dos tribunais superiores (STF/STJ).  
Esta versão utiliza **dados reais do STF**, extraídos da base pública Corte Aberta e salvos em formato `.xlsx`.
""")

# ---------- FUNÇÕES DE CARREGAMENTO DE DADOS ----------

@st.cache_data(show_spinner=True)
def carregar_dados_stf_excel(caminho="808b2598-6b6e-4df9-9f4a-8d614da3f78d.xlsx"):
    """Carrega decisões reais do STF a partir da planilha Excel enviada."""
    df = pd.read_excel(caminho)
    
    # Renomeia colunas, se necessário (ajuste conforme o nome das colunas da sua planilha)
    df.columns = [col.strip().capitalize() for col in df.columns]
    
    # Garante que as colunas principais existam
    colunas_necessarias = ["Id_decisao", "Ementa", "Resultado"]
    for c in colunas_necessarias:
        if c not in df.columns:
            st.warning(f"⚠️ Coluna '{c}' não encontrada na planilha. Verifique o nome exato no Excel.")
    return df

def carregar_dados_stj_simulado(linhas=200):
    """Simula decisões do STJ (conceito de API Datajud)."""
    resultados = ["Procedente", "Improcedente", "Parcialmente Procedente"]
    ementas = [
        "Recurso especial sobre dano moral julgado improcedente.",
        "Pedido de habeas corpus parcialmente procedente.",
        "Reconhecida a repercussão geral em tema de direito administrativo.",
        "Ação declaratória de inconstitucionalidade julgada procedente.",
        "Pedido improvido por ausência de provas documentais."
    ]
    dados = []
    for i in range(linhas):
        dados.append({
            "Id_decisao": i + 1,
            "Tribunal": "STJ",
            "Ementa": random.choice(ementas),
            "Resultado": random.choice(resultados)
        })
    return pd.DataFrame(dados)

# ---------- INTERFACE ----------
st.sidebar.header("Filtros de Análise")
tribunal = st.sidebar.radio("Selecione o Tribunal:", ["STF", "STJ", "AMBOS"])
linhas = st.sidebar.slider("Quantidade de decisões (para STJ simulado):", 50, 1000, 200, 50)
termos_input = st.sidebar.text_area(
    "Digite os termos-chave separados por vírgula:",
    "dano moral, repercussão geral, inconstitucionalidade"
)
analisar = st.sidebar.button("Analisar Decisões")

# ---------- PROCESSAMENTO ----------
if analisar:
    st.subheader("🔍 Resultados da Análise")

    if tribunal == "STF":
        st.info("Carregando dados reais do STF... ⏳")
        df = carregar_dados_stf_excel()
        df["Tribunal"] = "STF"
    elif tribunal == "STJ":
        st.info("Carregando dados simulados do STJ... ⚙️")
        df = carregar_dados_stj_simulado(linhas)
    else:
        st.info("Carregando dados reais do STF e simulados do STJ... 🏛️")
        df_stf = carregar_dados_stf_excel()
        df_stf["Tribunal"] = "STF"
        df_stj = carregar_dados_stj_simulado(linhas // 2)
        df = pd.concat([df_stf, df_stj], ignore_index=True)

    termos = [t.strip().lower() for t in termos_input.split(",") if t.strip()]
    freq_termos = {t: df["Ementa"].astype(str).str.lower().str.count(t).sum() for t in termos}

    # ---------- RESULTADOS ----------
    freq_df = pd.DataFrame(freq_termos.items(), columns=["Termo", "Frequência"])
    st.markdown("### 📊 Frequência de Termos nas Ementas")
    st.dataframe(freq_df, use_container_width=True)

    # ---------- GRÁFICOS ----------
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Distribuição de Resultados")
        fig1, ax1 = plt.subplots()
        df["Resultado"].value_counts().head(10).plot(kind="bar", ax=ax1)
        plt.xlabel("Resultado")
        plt.ylabel("Quantidade")
        plt.title("Distribuição dos Resultados")
        st.pyplot(fig1)

    with col2:
        st.markdown("#### Distribuição por Tribunal")
        fig2, ax2 = plt.subplots()
        df["Tribunal"].value_counts().plot(kind="pie", autopct="%1.1f%%", ax=ax2)
        plt.title("Origem das Decisões")
        st.pyplot(fig2)

    # ---------- AMOSTRA ----------
    st.markdown("### 🧾 Amostra de Decisões")
    st.dataframe(df[["Tribunal", "Ementa", "Resultado"]].sample(min(5, len(df))), use_container_width=True)

# ---------- RODAPÉ ----------
st.markdown("---")
st.markdown("👩‍⚖️ **Desenvolvido por:** Maria Eduarda de Bustamante Fontoura e Nicolly Soares Motta — Versão 2.3")
st.markdown("📚 **Fonte de Dados Reais:** Base Corte Aberta (STF)")


