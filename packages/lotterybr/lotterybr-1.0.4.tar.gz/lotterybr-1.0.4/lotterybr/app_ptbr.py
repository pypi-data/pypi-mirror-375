from shiny import App, render, ui, reactive
from shinywidgets import output_widget, register_widget
import plotly.express as px
import pandas as pd
import numpy as np

from .get_data import get_data

descriptions = {
    'maismilionaria' : "Para ganhar na MaisMilionaria, e necessario acertar pelo menos quatro dos seis numeros sorteados.",
    'megasena' : "Na Mega-Sena, ha diversas faixas de premiacao. Para ganhar o premio maximo (Sena), e preciso acertar todos os seis numeros sorteados. Ha tambem premiacoes para quem acerta cinco numeros (Quina) e quatro numeros (Quadra).",
    'lotofacil' : "Na Lotofacil, existem diferentes faixas de premiacao. Para ganhar o premio maximo, e necessario acertar os quinze numeros sorteados. Ha tambem premiacoes para quem acerta onze, doze, treze ou quatorze numeros.",
    'quina' : "Na Quina, existem diferentes faixas de premiacao. Para ganhar o premio maximo, e necessario acertar os cinco numeros sorteados. Ha tambem premiacoes para quem acerta dois, tres ou quatro numeros.",
    'lotomania' : "Na Lotomania, ha diversas faixas de premiacao. Para ganhar o premio maximo, e necessario acertar todos os vinte numeros sorteados. Alem disso, ha premiacoes para quem acerta dezesseis, dezessete, dezoito ou dezenove numeros.",
    'duplasena' : "Na Dupla Sena, existem diferentes faixas de premiacao. Para ganhar o premio maximo (Sena), e necessario acertar os seis numeros sorteados no primeiro ou no segundo sorteio. Ha tambem premiacoes para quem acerta cinco (Quina) ou quatro (Quadra) numeros em um dos sorteios.",
    'diadesorte' : "No Dia de Sorte, e preciso acertar sete numeros sorteados mais o mes para ganhar o premio maximo. Ha tambem premiacoes para quem acerta seis, cinco, quatro ou tres numeros, independente do mes."
}

app_ui = ui.page_fluid(
    ui.tags.style(
        """
        .data-table-container {
            max-height: 300px;
            overflow-y: auto;
        }
        """
    ),
    ui.h2("Aplicativo Lotterybr"),
    ui.layout_sidebar(
        # Sidebar
        ui.sidebar(
            ui.input_select(
                "jogo", "Escolha o Jogo:",
                {
                    "maismilionaria": "MaisMilionária",
                    "megasena": "Mega-Sena",
                    "lotofacil": "Lotofácil",
                    "quina": "Quina",
                    "lotomania": "Lotomania",
                    "duplasena": "Dupla Sena",
                    "diadesorte": "Dia de Sorte"
                }
            ),
            ui.input_select(
                "tipo", "Escolha o tipo de dados",
                {"numbers": "Números", "winners": "Ganhadores"}
            ),
            ui.input_select(
                "grafico", "Escolha o tipo de gráfico",
                {"bar_chart": "Gráfico de Barras"}
            ),
            ui.panel_conditional(
                "input.tipo == 'winners'",
                ui.input_checkbox("log_scale", "Usar escala logarítmica", False)
            ),
            ui.output_text_verbatim("summary_table")
        ),
        # Conteúdo principal
        output_widget("plot"),
        ui.h5("Descrição:"),
        ui.output_text("dynamic_text"),
        ui.h3("Tabela de Dados"),
        ui.div(
            ui.output_table("data_table"),
            class_="data-table-container"
        )
    )
)


def server(input, output, session):

    @reactive.Effect
    @reactive.event(input.jogo, input.tipo, input.grafico)
    def _():
        game = input.jogo()
        tipo = input.tipo()
        dados = get_data(game, tipo, language= "en")

        if tipo == "numbers":
            if game == "maismilionaria":
                resultado = [x for x in dados['numbers_clovers'] if x.isdigit()]
                df = pd.DataFrame({'Número': resultado}).value_counts().reset_index(name='Frequência')
                fig = px.bar(df, x='Número', y='Frequência', title="Frequência de Números da MaisMilionária")
            else:
                df = pd.DataFrame({'Número': dados['numbers']}).value_counts().reset_index(name='Frequência')
                fig = px.bar(df, x='Número', y='Frequência', title=f"Frequência de Números da {game.capitalize()}")
                
        elif tipo == "winners":
            df = pd.DataFrame(dados)
            if input.log_scale():
                df['winners'] = df['winners'].apply(lambda x: np.log1p(x))
            fig = px.bar(df, x='match', y='winners', title=f"Frequência de Ganhadores da {game.capitalize()}")

        register_widget("plot", fig)

    @output
    @render.text
    def dynamic_text():
        return descriptions[input.jogo()]

    @output
    @render.table
    def data_table():
        game = input.jogo()
        tipo = input.tipo()
        dados = get_data(game, tipo, language="eng")
        return pd.DataFrame(dados)

    @output
    @render.text
    def summary_table():
        game = input.jogo()
        tipo = input.tipo()
        dados = get_data(game, tipo, language="eng")
        return pd.DataFrame(dados).describe().to_string()

app_br = App(app_ui, server)
