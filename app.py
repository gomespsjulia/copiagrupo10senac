import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração visual da página
st.set_page_config(page_title="Saúde Mental - Universitários", layout="wide")

st.title("🧠 Dashboard: Saúde Mental e Hábitos de Universitários")
st.markdown("Análise detalhada de amostras representativas (100 estudantes por visualização).")

# Paleta de cores de alto contraste padrão
CORES_ALTO_CONTRASTE = px.colors.qualitative.Bold

# Carrega a base de dados
@st.cache_data
def carregar_dados():
    df = pd.read_csv("base_tratada.csv")
    
    if "Depression" in df.columns:
        df["Depression"] = df["Depression"].replace({True: "Sim", False: "Não", "True": "Sim", "False": "Não"})
    
    if "genero" in df.columns:
        df["genero"] = df["genero"].replace({"Female": "Feminino", "Male": "Masculino", "Other": "Outros"})
        
    return df

try:
    df = carregar_dados()

    # --- FILTROS (BARRA LATERAL) ---
    st.sidebar.header("⚙️ Filtros do Painel")
    
    opcoes_genero_disponiveis = [g for g in ["Masculino", "Feminino"] if g in df["genero"].dropna().unique()]
    if not opcoes_genero_disponiveis:
        opcoes_genero_disponiveis = list(df["genero"].dropna().unique())

    genero_selecionado = st.sidebar.multiselect(
        "Selecione o Gênero:",
        options=opcoes_genero_disponiveis,
        default=opcoes_genero_disponiveis
    )

    sono_min = float(df["Sleep_Duration"].min())
    sono_max = float(df["Sleep_Duration"].max())
    sono_selecionado = st.sidebar.slider(
        "Faixa de Tempo de Sono (horas):",
        min_value=sono_min,
        max_value=sono_max,
        value=(sono_min, sono_max)
    )

    estudo_min = float(df["Study_Hours"].min())
    estudo_max = float(df["Study_Hours"].max())
    estudo_selecionado = st.sidebar.slider(
        "Faixa de Horas de Estudo (diárias):",
        min_value=estudo_min,
        max_value=estudo_max,
        value=(estudo_min, estudo_max)
    )

    redes_min = float(df["Social_Media_Hours"].min())
    redes_max = float(df["Social_Media_Hours"].max())
    redes_selecionado = st.sidebar.slider(
        "Faixa de Horas em Redes Sociais:",
        min_value=redes_min,
        max_value=redes_max,
        value=(redes_min, redes_max)
    )

    # Aplica TODOS os filtros na tabela
    df_filtrado = df[
        (df["genero"].isin(genero_selecionado)) &
        (df["Sleep_Duration"] >= sono_selecionado[0]) & 
        (df["Sleep_Duration"] <= sono_selecionado[1]) &
        (df["Study_Hours"] >= estudo_selecionado[0]) & 
        (df["Study_Hours"] <= estudo_selecionado[1]) &
        (df["Social_Media_Hours"] >= redes_selecionado[0]) & 
        (df["Social_Media_Hours"] <= redes_selecionado[1])
    ]

    # Função auxiliar para extrair no máximo 100 amostras limpas
    def obter_amostra_100(dataframe):
        if len(dataframe) > 100:
            return dataframe.sample(n=100, random_state=42)
        return dataframe

    # --- MÉTRICAS RÁPIDAS (KPIs) ---
    st.subheader("Visão Geral da Amostra")
    col1, col2, col3 = st.columns(3)
    col1.metric("Estudantes Analisados (Total Base Filtrada)", f"{len(df_filtrado):,}")
    
    if not df_filtrado.empty:
        col2.metric("Nível Médio de Estresse", f"{df_filtrado['nivel_estresse'].mean():.0f}")
        col3.metric("Média de Horas de Sono", f"{df_filtrado['Sleep_Duration'].mean():.0f} h")
    else:
        col2.metric("Nível Médio de Estresse", "0")
        col3.metric("Média de Horas de Sono", "0 h")

    st.divider()

    if not df_filtrado.empty:
        # --- PRIMEIRA LINHA DE GRÁFICOS (1 e 2) ---
        c1, c2 = st.columns(2)

        with c1:
            st.subheader("1. Notas x Estresse")
            df_amostra_1 = obter_amostra_100(df_filtrado)
            fig1 = px.scatter(
                df_amostra_1,
                x="CGPA",
                y="nivel_estresse",
                opacity=0.6,
                color_discrete_sequence=CORES_ALTO_CONTRASTE,
                labels={
                    "CGPA": "Nota (CGPA)", 
                    "nivel_estresse": "Nível de Estresse"
                }
            )
            st.plotly_chart(fig1, use_container_width=True)

        with c2:
            st.subheader("2. Sono x Estresse")
            df_amostra_2 = obter_amostra_100(df_filtrado)
            df_g2 = df_amostra_2.copy()
            df_g2["Sono_Group"] = df_g2["Sleep_Duration"].round(0)
            df_g2 = df_g2.groupby("Sono_Group")["nivel_estresse"].mean().reset_index()
            df_g2["nivel_estresse"] = df_g2["nivel_estresse"].round(0)
            
            fig2 = px.line(
                df_g2,
                x="Sono_Group",
                y="nivel_estresse",
                markers=True,
                color_discrete_sequence=CORES_ALTO_CONTRASTE,
                labels={
                    "Sono_Group": "Horas de Sono",
                    "nivel_estresse": "Nível Médio de Estresse"
                }
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.divider()

        # --- SEGUNDA LINHA DE GRÁFICOS (3 e 4) ---
        c3, c4 = st.columns(2)

        with c3:
            st.subheader("3. Depressão x Estresse")
            df_amostra_3 = obter_amostra_100(df_filtrado)
            fig3 = px.box(
                df_amostra_3,
                x="Depression",
                y="nivel_estresse",
                color="Depression",
                color_discrete_sequence=CORES_ALTO_CONTRASTE,
                labels={
                    "Depression": "Sintomas Depressivos",
                    "nivel_estresse": "Nível de Estresse"
                }
            )
            st.plotly_chart(fig3, use_container_width=True)

        with c4:
            st.subheader("4. Atividade Física x Estresse")
            df_amostra_4 = obter_amostra_100(df_filtrado)
            coluna_ativ = "Physical_Activity_Minutes" if "Physical_Activity_Minutes" in df_amostra_4.columns else "atividade_fisica"
            
            fig4 = px.scatter(
                df_amostra_4,
                x=coluna_ativ,
                y="nivel_estresse",
                opacity=0.6,
                color_discrete_sequence=CORES_ALTO_CONTRASTE,
                labels={
                    coluna_ativ: "Atividade Física (Minutos/Prática)",
                    "nivel_estresse": "Nível de Estresse"
                }
            )
            st.plotly_chart(fig4, use_container_width=True)

        st.divider()

        # --- TERCEIRA LINHA DE GRÁFICOS (5 e 6) ---
        c5, c6 = st.columns(2)

        with c5:
            st.subheader("5. Redes Sociais x Estresse")
            df_amostra_5 = obter_amostra_100(df_filtrado)
            df_g5 = df_amostra_5.copy()
            df_g5["Social_Group"] = df_g5["Social_Media_Hours"].round(0)
            df_g5 = df_g5.groupby("Social_Group")["nivel_estresse"].mean().reset_index()
            df_g5["nivel_estresse"] = df_g5["nivel_estresse"].round(0)
            
            fig5 = px.line(
                df_g5,
                x="Social_Group",
                y="nivel_estresse",
                markers=True,
                color_discrete_sequence=CORES_ALTO_CONTRASTE,
                labels={
                    "Social_Group": "Horas em Redes Sociais",
                    "nivel_estresse": "Nível Médio de Estresse"
                }
            )
            st.plotly_chart(fig5, use_container_width=True)

        with c6:
            st.subheader("6. Redes Sociais x Depressão")
            df_amostra_6 = obter_amostra_100(df_filtrado)
            fig6 = px.box(
                df_amostra_6,
                x="Depression",
                y="Social_Media_Hours",
                color="Depression",
                color_discrete_sequence=CORES_ALTO_CONTRASTE,
                labels={
                    "Depression": "Sintomas Depressivos",
                    "Social_Media_Hours": "Horas em Redes Sociais"
                }
            )
            st.plotly_chart(fig6, use_container_width=True)

    else:
        st.warning("Nenhum dado encontrado para os filtros selecionados. Ajuste os filtros na barra lateral.")

except FileNotFoundError:
    st.error("⚠️ ERRO: O arquivo 'base_tratada.csv' não foi encontrado.")
