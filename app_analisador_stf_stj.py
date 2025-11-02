# ============================================
# Analisador de Sentenças do STF/STJ — Versão com fallback para upload
# ============================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
import os

# ---------- CONFIG ----------
st.set_page_config(page_title="Analisador de Sentenças do STF/STJ", page_icon="⚖️", layout="wide")
st.title("⚖️ Analisador de Sentenças do STF/STJ — Base real (Excel)")

# ---------- Função para carregar o arquivo Excel ----------
@st.cache_data(show_spinner=True)
def carregar_dados_stf_excel_local(caminho_local="stf_corte_aberta_sample.xlsx"):
    """
    Tenta carregar o arquivo Excel do caminho local (por exemplo, quando o arquivo
    foi enviado para o repositório GitHub e está presente no app do Streamlit Cloud).
    Se o arquivo não existir, levanta FileNotFoundError.
    """
    if not os.path.exists(caminho_local):
        raise FileNotFoundError(f"Arquivo '{caminho_local}' não encontrado.")
    df = pd.read_excel(caminho_local)
    # Ajustes: criamos colunas usadas pelo app a partir das colunas reais
    # Verifique nomes exatamente iguais aos presentes na sua planilha
    if "Observação do andamento" in df.columns:
        df["Ementa"] = df["Observação do andamento"].astype(str)
    elif "Observacao do andamento" in df.columns:
        df["Ementa"] = df["Observacao do andamento"].astype(str)
    else:
        # fallback: tenta localizar alguma coluna que pareça conter texto
        possible = [c for c in df.columns if "ement" in c.lower() or "andamento" in c.lower() or "observ" in c.lower()]
        if possible:
            df["Ementa"] = df[possible[0]].astype(str)
        else:
            df["Ementa"] = df.iloc[:, 0].astype(str)  # último recurso

    # Resultado (tipo decisão)
    if "Tipo decisão" in df.columns:
        df["Resultado"] = df["Tipo decisão"].astype(str)
    elif "Tipo decisao" in df.columns:
        df["Resultado"] = df["Tipo decisao"].astype(str)
    else:
        possible_res = [c for c in df.columns if "decis" in c.lower() or "resultado" in c.lower()]
        if possible_res:
            df["Resultado"] = df[possible_res[0]].astype(str)
        else:
            df["Resultado"] = "Não especificado"

    df["Tribunal"] = "STF"
    return df

def carregar_dados_stf_do_buffer(uploaded_file):
    """Lê o Excel enviado via st.file_uploader (in-memory)."""
    df = pd.read_excel(uploaded_file)
    # mesmo mapeamento de colunas
    if "Observação do andamento" in df.columns:
        df["Ementa"] = df["Observação do andamento"].astype(str)
    elif "Observacao do andamento" in df.columns:
        df["Ementa"] = df["Observacao do andamento"].astype(str)
    else:
        possible = [c for c in df.columns if "ement" in c.lower() or "andamento" in c.lower() or "observ" in c.lower()]
        if possible:
            df["Ementa"] = df[possible[0]].astype(str)
        else:
            df["Ementa"] = df.iloc[:, 0].astype(str)

    if "Tipo decisão" in df.columns:
        df["Resultado"] = df["Tipo decisão"].astype(str)
    elif "Tipo decisao" in df.columns:
        df["Resultado"] = df["Tipo decisao"].astype(str)
    else:
        possible_res = [c for c in df.columns if "decis" in c.lower() or "resultado" in c.lower()]
        if possible_res:
            df["Resultado"] = df[possible_res[0]].astype(str)
        else:
            df["Resultado"] = "Não especificado"

    df["Tribunal"] = "STF"
    return df

def carregar_dados_stj_simulado(linhas=200):
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
            "idFatoDecisao": i + 1,
            "Tribunal": "STJ",
            "Ementa": random.choice(ementas),
            "Resultado": random.choice(resultados)
        })
    return pd.DataFrame(dados)

# ---------- Interface ----------
st.sidebar.header("Filtros de Análise")
tribunal = st.sidebar.radio("Selecione o Tribunal:", ["STF", "STJ", "AMBOS"])
linhas = st.sidebar.slider("Quantidade de decisões (para STJ simulado):", 50, 1000, 200, 50)
termos_input = st.sidebar.text_area("Digite os termos-chave separados por vírgula:",
                                    "dano moral, repercussão geral, inconstitucionalidade")
analisar = st.sidebar.button("Analisar Decisões")

# ---------- Processamento ----------
if analisar:
    st.subheader("🔍 Resultados da Análise")

    df = None
    # Primeiro: tenta carregar arquivo local (enviado ao repositório)
    caminho_padrao = "stf_corte_aberta_sample.xlsx"  # NOME QUE SUGIRO COLOCAR NO REPO
    try:
        df = carregar_dados_stf_excel_local(caminho_padrao)
        st.success(f"Arquivo carregado do repositório: {caminho_padrao}")
    except FileNotFoundError:
        st.warning(f"Arquivo '{caminho_padrao}' não encontrado no repositório. Faça upload do arquivo .xlsx abaixo ou envie o arquivo para o repositório e reinicie o app.")
        uploaded_file = st.file_uploader("Faça upload da planilha Excel (.xlsx) com os dados do STF", type=["xlsx"])
        if uploaded_file is not None:
            df = carregar_dados_stf_do_buffer(uploaded_file)
            st.success("Arquivo carregado via upload pelo navegador.")

    # Se o usuário escolheu STJ (simulado) ou se não há df real e escolheu "STJ" ou "AMBOS"
    if tribunal == "STJ" and df is None:
        df = carregar_dados_stj_simulado(linhas)
    elif tribunal == "AMBOS" and df is None:
        st.info("Usando apenas STJ simulado porque o arquivo STF não está disponível.")
        df = carregar_dados_stj_simulado(linhas)

    # Caso ainda não haja df (usuário não fez upload), interrompe
    if df is None:
        st.stop()

    # Contagem de termos
    termos = [t.strip().lower() for t in termos_input.split(",") if t.strip()]
    df["Ementa"] = df["Ementa"].astype(str)
    freq_termos = {t: df["Ementa"].str.lower().str.count(t).sum() for t in termos}

    # Resultados
    freq_df = pd.DataFrame(freq_termos.items(), columns=["Termo", "Frequência"])
    st.markdown("### 📊 Frequência de Termos nas Decisões")
    st.dataframe(freq_df, use_container_width=True)

    # Gráficos
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Distribuição de Tipos de Decisão")
        fig1, ax1 = plt.subplots()
        df["Resultado"].value_counts().head(10).plot(kind="bar", ax=ax1)
        plt.xlabel("Tipo de Decisão")
        plt.ylabel("Quantidade")
        plt.title("Distribuição dos Tipos de Decisão (STF)")
        st.pyplot(fig1)

    with col2:
        st.markdown("#### Distribuição por Tribunal")
        fig2, ax2 = plt.subplots()
        df["Tribunal"].value_counts().plot(kind="pie", autopct=\"%1.1f%%\", ax=ax2)
        plt.title("Origem das Decisões")
        st.pyplot(fig2)

    st.markdown("### 🧾 Amostra de Decisões")
    st.dataframe(df[["Tribunal", "Ementa", "Resultado"]].sample(min(5, len(df))), use_container_width=True)

st.markdown("---")
st.markdown("👩‍⚖️ Desenvolvido por: Maria Eduarda de Bustamante Fontoura e Nicolly Soares Motta")
