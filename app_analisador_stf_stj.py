# ============================================
# Analisador de Sentenças do STF/STJ — Versão 2.1
# Desenvolvido por: Maria Eduarda de Bustamante Fontoura e Nicolly Soares Motta
# ============================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
from basedosdados import read_sql

# ---------- CONFIGURAÇÃO ----------
st.set_page_config(page_title="Analisador de Sentenças do STF/STJ", page_icon="⚖️", layout="wide")
st.title("⚖️ Analisador de Sentenças do STF/STJ — Dados Reais e Simulados")
st.markdown("""
Aplicativo desenvolvido para análise quantitativa de jurisprudência dos tribunais superiores (STF/STJ).  
- Utiliza **dados reais do STF** (dataset Corte Aberta — Base dos Dados).  
- Inclui **simulação de dados do STJ**, representando o consumo da **API pública Datajud**.
""")

# ---------- FUNÇÕES DE EXTRAÇÃO DE DADOS ----------

@st.cache_data(show_spinner=True)
def carregar_dados_stf(linhas=200):
    """Carrega decisões reais do STF (Base dos Dados - Corte Aberta)"""
    query = f"""
    SELECT
      id_decisao AS ID_Decisao,
      orgao_julgador_nome AS Tribunal,
      ementa_texto AS Ementa,
      decisao_texto AS Resultado
    FROM `basedosdados.br_stf.corte_aberta`
    WHERE ementa_texto IS NOT NULL
    LIMIT {linhas}
    """
    df = read_sql(query)
    df["Tribunal"] = df["Tribunal"].fillna("STF")
    df["Resultado"] = df["Resultado"].fillna("Não especificado")
    return df

def carregar_dados_stj_simulado(linhas=200):
    """Simula dados do STJ (como se fossem extraídos via API Datajud)"""
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
            "ID_Decisao": i + 1,
            "Tribunal": "STJ",
            "Ementa": random.choice(ementas),
            "Resultado": random.choice(resultados)
        })
    return pd.DataFrame(dados)

# ---------- INTERFACE ----------
st.sidebar.header("Filtros de Análise")
tribunal = st.sidebar.radio("Selecione o Tribunal:", ["STF", "STJ", "AMBOS"])
linhas = st.sidebar.slider("Quantidade de decisões para análise:", 50, 1000, 200, 50)
termos_input = st.sidebar.text_area(
    "Digite os termos-chave separados por vírgula:",
    "dano moral, repercussão geral, inconstitucionalidade"
)
analisar = st.sidebar.button("Analisar Decisões")

# ---------- PROCESSAMENTO ----------
if analisar:
    st.subheader("🔍 Resultados da Análise")

    # Carregar dados conforme filtro
    if tribunal == "STF":
        st.info("Carregando dados reais do STF (Base dos Dados)... ⏳")
        df = carregar_dados_stf(linhas)
    elif tribunal == "STJ":
        st.info("Carregando dados simulados do STJ (simulação da API Datajud)... ⚙️")
        df = carregar_dados_stj_simulado(linhas)
    else:
        st.info("Carregando dados do STF e STJ... 🏛️")
        df_stf = carregar_dados_stf(linhas // 2)
        df_stj = carregar_dados_stj_simulado(linhas // 2)
        df = pd.concat([df_stf, df_stj], ignore_index=True)

    termos = [t.strip().lower() for t in termos_input.split(",") if t.strip()]
    freq_termos = {t: df["Ementa"].str.lower().str.count(t).sum() for t in termos}

    # ---------- RESULTADOS ----------
    freq_df = pd.DataFrame(freq_termos.items(), columns=["Termo", "Frequência"])
    st.markdown("### 📊 Frequência de Termos nas Ementas")
    st.dataframe(freq_df, use_container_width=True)

    # ---------- GRÁFICOS ----------
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Distribuição de Resultados")
        fig1, ax1 = plt.subplots()
        df["Resultado"].value_counts().plot(kind="bar", ax=ax1)
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

    # ---------- AMOSTRA DE DECISÕES ----------
    st.markdown("### 🧾 Amostra de Decisões")
    st.dataframe(df[["Tribunal", "Ementa", "Resultado"]].sample(min(5, len(df))), use_container_width=True)

# ---------- RODAPÉ ----------
st.markdown("---")
st.markdown("👩‍⚖️ **Desenvolvido por:** Maria Eduarda de Bustamante Fontoura e Nicolly Soares Motta — Versão 2.1")
st.markdown("📚 **Fontes de Dados:**")
st.markdown("- [Base dos Dados — Corte Aberta (STF)](https://basedosdados.org/dataset/br-stf-corte-aberta)")
st.markdown("- [API Pública Datajud (STJ, simulação conceitual)](https://datajud.cnj.jus.br/)")
