from shiny import App, render, ui, reactive
from shinywidgets import output_widget, register_widget
import plotly.express as px
import pandas as pd
import numpy as np

from .get_data import get_data

descriptions = {
    "maismilionaria": "To win in MaisMilionaria, you need to match at least four of the six drawn numbers.",
    "megasena": "In Mega-Sena, there are various prize tiers. To win the top prize (Sena), you must match all six drawn numbers. There are also prizes for matching five numbers (Quina) and four numbers (Quadra).",
    "lotofacil": "In Lotofacil, there are different prize tiers. To win the top prize, you need to match all fifteen drawn numbers. There are also prizes for matching eleven, twelve, thirteen, or fourteen numbers.",
    "quina": "In Quina, there are different prize tiers. To win the top prize, you need to match all five drawn numbers. There are also prizes for matching two, three, or four numbers.",
    "lotomania": "In Lotomania, there are various prize tiers. To win the top prize, you need to match all twenty drawn numbers. Additionally, there are prizes for matching sixteen, seventeen, eighteen, or nineteen numbers.",
    "duplasena": "In Dupla Sena, there are different prize tiers. To win the top prize (Sena), you need to match all six drawn numbers in either the first or the second draw. There are also prizes for matching five (Quina) or four (Quadra) numbers in one of the draws.",
    "diadesorte": "In Dia de Sorte, you need to match seven drawn numbers plus the month to win the top prize. There are also prizes for matching six, five, four, or three numbers, regardless of the month."
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
    ui.h2("Lotterybr App"),
    ui.layout_sidebar(
        # Sidebar correto
        ui.sidebar(
            ui.input_select(
                "jogo", "Choose Game:",
                {
                    "maismilionaria": "MaisMilionaria",
                    "megasena": "Mega-Sena",
                    "lotofacil": "LotoFacil",
                    "quina": "Quina",
                    "lotomania": "LotoMania",
                    "duplasena": "Dupla Sena",
                    "diadesorte": "Dia de Sorte"
                }
            ),
            ui.input_select(
                "tipo", "Choose data type",
                {"numbers": "Numbers", "winners": "Winners"}
            ),
            ui.input_select(
                "grafico", "Choose graph type",
                {"bar_chart": "Bar Chart"}
            ),
            ui.panel_conditional(
                "input.tipo == 'winners'",
                ui.input_checkbox("log_scale", "Use log scale", False)
            ),
            ui.output_text_verbatim("summary_table")
        ),
        # Conteúdo principal direto
        output_widget("plot"),
        ui.h5("Description:"),
        ui.output_text("dynamic_text"),
        ui.h3("Data Table"),
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
        dados = get_data(game, tipo, language= "eng")

        if tipo == "numbers":
            if game == "maismilionaria":
                resultado = [x for x in dados['numbers_clovers'] if x.isdigit()]
                df = pd.DataFrame({'Number': resultado}).value_counts().reset_index(name='Frequency')
                fig = px.bar(df, x='Number', y='Frequency', title="MaisMilionaria Numbers Frequency")
            else:
                df = pd.DataFrame({'Number': dados['numbers']}).value_counts().reset_index(name='Frequency')
                fig = px.bar(df, x='Number', y='Frequency', title=f"{game.capitalize()} Numbers Frequency")
                
        elif tipo == "winners":
            df = pd.DataFrame(dados)
            if input.log_scale():
                df['winners'] = df['winners'].apply(lambda x: np.log1p(x))
            fig = px.bar(df, x='match', y='winners', title=f"{game.capitalize()} Winners Frequency")

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

app_en = App(app_ui, server)
