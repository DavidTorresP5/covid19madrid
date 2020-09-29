import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd


# App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.JOURNAL])

server = app.server

# Read the file from CAM official website

df = pd.read_json(
    "http://datos.comunidad.madrid/catalogo/dataset/7da43feb-8d4d-47e0-abd5-3d022d29d09e/resource/877fa8f5-cd6c-4e44-9df5-0fb60944a841/download/covid19_tia_muni_y_distritos_s.json",
    orient="split",
)
"""

df = pd.read_json(
    "data/covid19_tia_muni_y_distritos_s.json",
    orient="split",
)
"""

df = df[
    [
        "municipio_distrito",
        "fecha_informe",
        "tasa_incidencia_acumulada_ultimos_14dias",
        "casos_confirmados_totales",
        "casos_confirmados_ultimos_14dias",
    ]
]
df["fecha_informe"] = pd.to_datetime(df["fecha_informe"])
df["tasa_incidencia_acumulada_ultimos_14dias"] = (
    df["tasa_incidencia_acumulada_ultimos_14dias"].round(0).astype(int)
)
df = df.rename(
    columns={
        "municipio_distrito": "Municipio/Distrito",
        "fecha_informe": "Fecha",
        "tasa_incidencia_acumulada_ultimos_14dias": "IA 14 días",
    }
)

# Create a list of different choices

opciones_municipios = []
for municipio in df["Municipio/Distrito"].unique():
    opciones_municipios.append({"label": municipio, "value": municipio})


# Choices
controls = dbc.Card(
    [
        dbc.FormGroup(
            [
                html.H3("Incidencia acumulada por municipio o distrito"),
                html.P(
                    "Busca uno o varios municipios o distritos de la Comunidad de Madrid para ver la evolución de su Incidencia Acumulada de casos de covid-19 en los últimos 14 días."
                ),
                html.P(
                    "La incidencia acumulada (IA) se define como la proporción de individuos sanos que desarrollan la enfermedad a lo largo de un periodo determinado. La incidencia acumulada proporciona una estimación de la probabilidad o el riesgo de que un individuo libre de una determinada enfermedad la desarrolle durante un período especificado de tiempo."
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Elige municipio o distrito:"),
                dcc.Dropdown(
                    id="in-municipio",
                    options=opciones_municipios,
                    value=["Fuenlabrada", "Getafe", "Alcobendas"],
                    multi=True,
                ),
            ]
        ),
    ],
    body=True,
)

# Layout
app.layout = dbc.Container(
    [
        html.H1("Incidencia acumulada Covid-19 CAM"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(controls, md=4),
                dbc.Col(
                    dcc.Graph(id="out-lineplot", config={"displaylogo": False}), md=8
                ),
            ],
            align="center",
        ),
    ],
    fluid=True,
)

# Callbacks


@app.callback(
    Output("out-lineplot", "figure"),
    [Input("in-municipio", "value")],
)

# Update functions


def update_figure(municipios):

    df_filtr = df[df["Municipio/Distrito"].isin(municipios)]

    fig = px.line(
        df_filtr,
        x="Fecha",
        y="IA 14 días",
        color="Municipio/Distrito",
        template="plotly_white",
        title="Incidencia acumulada en Municipios o Distritos de la Comunidad de Madrid",
    )

    fig.update_traces(mode="lines+markers")

    fig.add_shape(
        type="line",
        x0=min(df_filtr["Fecha"]),
        y0=500,
        x1=max(df_filtr["Fecha"]),
        y1=500,
        line=dict(color="red", width=1, dash="dash"),
    )
    fig.add_shape(
        type="line",
        x0=min(df_filtr["Fecha"]),
        y0=150,
        x1=max(df_filtr["Fecha"]),
        y1=150,
        line=dict(color="orangered", width=1, dash="dash"),
    )

    fig.add_annotation(
        x=df_filtr["Fecha"].drop_duplicates().nsmallest(4).iloc[-1],
        y=520,
        text="IA límite Ministerio de Sanidad",
    )
    fig.add_annotation(
        x=df_filtr["Fecha"].drop_duplicates().nsmallest(4).iloc[-1],
        y=170,
        text="Transmisión comunitaria",
    )
    fig.update_annotations(dict(xref="x", yref="y"))

    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(
            showspikes=True,
            showline=True,
            showgrid=True,
            spikedash="solid",
        ),
        xaxis_tickformat="%Y-%m-%d",
        yaxis=dict(showspikes=True, showline=True, showgrid=True, spikedash="solid"),
    )

    return fig


if __name__ == "__main__":
    app.run_server(debug=False)
