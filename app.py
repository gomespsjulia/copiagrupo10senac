import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.colors import sample_colorscale
CORES_ALTO_CONTRASTE = px.colors.qualitative.Bold

st.set_page_config(layout="wide")

st.title("Rede Social x Estresse")

df = pd.read_csv("base_tratada.csv")

df["Social_Media_Hours"] = df["Social_Media_Hours"].round()

df_grafico = df.drop_duplicates(subset=["Social_Media_Hours"]).sample(10, random_state=42)
df_grafico = df_grafico.sort_values(by="Social_Media_Hours")

def formata_hora(valor):
    h = int(valor)
    return f"{h}:00"

df_grafico["Tempo de Uso"] = df_grafico["Social_Media_Hours"].apply(formata_hora)

df_grafico["Tempo de Uso"] = pd.Categorical(
    df_grafico["Tempo de Uso"], 
    categories=[f"{int(h)}:00" for h in sorted(df_grafico["Social_Media_Hours"].unique())], 
    ordered=True
)

df_grafico = df_grafico.sort_values(by="Social_Media_Hours")
df_grafico = df_grafico.set_index("Tempo de Uso")

st.bar_chart(
    df_grafico["nivel_estresse"],
    x_label="Tempo de uso de Redes Sociais",
    y_label="Nível de Estresse"
)

sem_depressão = df[df["Depression"] == False]
com_depressão = df[df["Depression"] == True]
quantidade = df["Depression"].value_counts()
quantidade.index = ["Sem depressão", "Com depressão"]

col1, col2 = st.columns(2)

with col1:
	st.subheader("Distribuição de estudantes por depressão")
	fig, ax = plt.subplots(figsize=(8, 6))
	total = quantidade.sum()

	ax.pie(
		quantidade,
		labels=quantidade.index,
		autopct=lambda pct: f"{pct:.1f}%\n({int(pct * total / 100):,})"
	)

	st.pyplot(fig)

media = df.groupby("Depression")["Social_Media_Hours"].mean()
media.index = ["Sem depressão", "Com depressão"]

with col2:
	st.subheader("Social Media x Depression")
	fig, ax = plt.subplots(figsize=(8, 6))
	media.plot.bar(ax=ax, color=["#1f77b4", "#ff7f0e"])
	ax.bar_label(
        ax.containers[0],
        labels=[f"{valor:.2f} h" for valor in media],
        padding=3,
		fontsize=14
    )

	ax.set_title("Média de uso de redes sociais")
	ax.set_ylabel("Horas")
	ax.tick_params(axis="x", labelrotation=0)
	ax.set_ylim(0, 4)

	ax.plot(
		[0, 1],
		[media.iloc[0], media.iloc[0]],
		linestyle="--",
		color="#1f77b4"
	)

	st.pyplot(fig)
	
c3, c4 = st.columns(2)

with c3:
    st.subheader("3. Nível de Estresse x Depressão")
        
    # Usa todos os estudantes após os filtros
    df_amostra_3 = df.copy()
        
    # Cria grupos de nível de estresse
    df_amostra_3["Grupo_Estresse"] = pd.cut(
        df_amostra_3["nivel_estresse"],
        bins=[0, 3, 6, 10],
        labels=["Baixo (1–3)", "Moderado (4–6)", "Alto (7–10)"],
        include_lowest=True
    )
        
    # Conta estudantes por nível de estresse e depressão
    df_g3 = (
        df_amostra_3
        .groupby(["Grupo_Estresse", "Depression"], observed=False)
        .size()
        .reset_index(name="Quantidade")
    )
        
    fig3 = px.bar(
        df_g3,
        x="Grupo_Estresse",
        y="Quantidade",
        color="Depression",
        barmode="group",
        text="Quantidade",
        color_discrete_sequence=CORES_ALTO_CONTRASTE,
        labels={
            "Grupo_Estresse": "Nível de Estresse",
            "Quantidade": "Quantidade de Estudantes",
            "Depression": "Sintomas Depressivos"
        }
    )
        
    # Formata os números nas barras
    fig3.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside"
    )
        
    # Configura o eixo Y de 0 até 70.000, com linhas a cada 10.000
    fig3.update_yaxes(
        range=[0, 70000],
        dtick=10000,
        tickformat=","
    )
        
    st.plotly_chart(fig3, use_container_width=True)
# ==========================================
# GRÁFICO 4 - RICHARD
# SONO X ESTRESSE
# ==========================================

st.divider()

st.subheader("4. Relação entre Duração do Sono e Nível de Estresse")


# Calcula a média de horas de sono
# para cada nível de estresse
sono_estresse = (
    df
    .groupby("nivel_estresse", as_index=False)["Sleep_Duration"]
    .mean()
    .sort_values("nivel_estresse")
)


# Cria o gráfico
grafico_estresse = go.Figure()


# Valores mínimo e máximo do estresse
stress_min = sono_estresse["nivel_estresse"].min()
stress_max = sono_estresse["nivel_estresse"].max()


# ==========================================
# LINHA COM TRANSIÇÃO SUAVE DE CORES
# ==========================================

for i in range(len(sono_estresse) - 1):

    stress_medio = (
        sono_estresse["nivel_estresse"].iloc[i]
        + sono_estresse["nivel_estresse"].iloc[i + 1]
    ) / 2


    stress_normalizado = (
        (stress_medio - stress_min)
        / (stress_max - stress_min)
    )


    cor = sample_colorscale(
        "YlOrRd",
        stress_normalizado
    )[0]


    # Cria cada segmento da linha
    grafico_estresse.add_trace(
        go.Scatter(
            x=[
                sono_estresse["nivel_estresse"].iloc[i],
                sono_estresse["nivel_estresse"].iloc[i + 1]
            ],

            y=[
                sono_estresse["Sleep_Duration"].iloc[i],
                sono_estresse["Sleep_Duration"].iloc[i + 1]
            ],

            mode="lines",

            line=dict(
                color=cor,
                width=3
            ),

            showlegend=False
        )
    )


# ==========================================
# PONTOS COLORIDOS
# ==========================================

grafico_estresse.add_trace(
    go.Scatter(
        x=sono_estresse["nivel_estresse"],

        y=sono_estresse["Sleep_Duration"],

        mode="markers",

        marker=dict(
            size=9,

            color=sono_estresse["nivel_estresse"],

            colorscale="YlOrRd",

            cmin=stress_min,
            cmax=stress_max,

            showscale=True,

            colorbar=dict(
                title=dict(
                    text="Nível de<br>Estresse",
                    font=dict(size=20)
                ),

                tickfont=dict(size=16),

                thickness=25,

                len=1
            )
        ),

        showlegend=False
    )
)


# ==========================================
# CONFIGURAÇÃO VISUAL
# ==========================================

grafico_estresse.update_layout(
    template="plotly_dark",

    height=450,

    font=dict(size=16),

    xaxis=dict(
        title=dict(
            text="Nível de Estresse",
            font=dict(size=20)
        ),

        tickfont=dict(size=16)
    ),

    yaxis=dict(
        title=dict(
            text="Média da Duração do Sono (horas)",
            font=dict(size=20)
        ),

        tickfont=dict(size=16)
    ),

    margin=dict(
        l=80,
        r=110,
        t=30,
        b=80
    )
)


# ==========================================
# EXIBE O GRÁFICO
# ==========================================

st.plotly_chart(
    grafico_estresse,
    use_container_width=True
)
