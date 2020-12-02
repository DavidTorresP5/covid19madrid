import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd


# App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.JOURNAL])
app.title = "Madrid Covid-19"


server = app.server

# Read the files from CAM official website (municipios and zonas básicas de salud [ZBS])

df_muni = pd.read_json(
    "http://datos.comunidad.madrid/catalogo/dataset/7da43feb-8d4d-47e0-abd5-3d022d29d09e/resource/877fa8f5-cd6c-4e44-9df5-0fb60944a841/download/covid19_tia_muni_y_distritos_s.json",
    orient="split",
)

df_muni = df_muni[
    [
        "municipio_distrito",
        "fecha_informe",
        "tasa_incidencia_acumulada_ultimos_14dias",
    ]
]

df_muni = df_muni.rename(
    columns={
        "municipio_distrito": "Municipio/Distrito/ZBS",
        "fecha_informe": "Fecha",
        "tasa_incidencia_acumulada_ultimos_14dias": "IA 14 días",
    }
)

df_zbs = pd.read_json(
    "https://datos.comunidad.madrid/catalogo/dataset/b3d55e40-8263-4c0b-827d-2bb23b5e7bab/resource/907a2df0-2334-4ca7-aed6-0fa199c893ad/download/covid19_tia_zonas_basicas_salud_s.json",
    orient="split",
)

df_zbs = df_zbs[
    [
        "zona_basica_salud",
        "fecha_informe",
        "tasa_incidencia_acumulada_ultimos_14dias",
    ]
]

df_zbs = df_zbs.rename(
    columns={
        "zona_basica_salud": "Municipio/Distrito/ZBS",
        "fecha_informe": "Fecha",
        "tasa_incidencia_acumulada_ultimos_14dias": "IA 14 días",
    }
)

df = pd.concat([df_muni, df_zbs])

df["Fecha"] = pd.to_datetime(df["Fecha"])
df["IA 14 días"] = df["IA 14 días"].round(0).astype(int)


# Create a list of different choices

opciones_municipios = []
for municipio in df["Municipio/Distrito/ZBS"].unique():
    opciones_municipios.append({"label": municipio, "value": municipio})


# Choices
controls = dbc.Card(
    [
        dbc.FormGroup(
            [
                html.H3("Incidencia acumulada por municipio y zonas básicas de salud"),
                html.Br(),
                html.P(
                    "Busca uno o varios municipios o distritos de la Comunidad de Madrid para ver la evolución de su Incidencia Acumulada de casos de covid-19 en los últimos 14 días."
                ),
                html.Br(),
                html.P(
                    "La incidencia acumulada (IA) se define como la proporción de individuos sanos que desarrollan la enfermedad a lo largo de un periodo determinado. La incidencia acumulada proporciona una estimación de la probabilidad o el riesgo de que un individuo libre de una determinada enfermedad la desarrolle durante un período especificado de tiempo."
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Elige municipio o zona básica de salud:"),
                dcc.Dropdown(
                    id="in-municipio",
                    options=opciones_municipios,
                    value=["Fuenlabrada", "Getafe", "Alcobendas"],
                    multi=True,
                ),
            ]
        ),
        dbc.FormGroup(
            [
                html.Br(),
                html.P("Desarrollado por:"),
                html.A(
                    "@DavidTweid",
                    href="https://www.twitter.com/DavidTweid",
                    target="_blank",
                ),
                html.Br(),
                html.A(
                    "Github",
                    href="https://github.com/DavidTorresP5/covid19madrid",
                    target="_blank",
                ),
                html.Br(),
                html.A(
                    "Datos Abiertos CAM",
                    href="https://datos.comunidad.madrid/catalogo/organization/comunidad-de-madrid",
                    target="_blank",
                ),
            ]
        ),
    ],
    body=True,
)

# Layout
app.layout = dbc.Container(
    [
        html.H1("Madrid Covid-19. Incidencia Acumulada"),
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

    df_filtr = df[df["Municipio/Distrito/ZBS"].isin(municipios)]

    fig = px.line(
        df_filtr,
        x="Fecha",
        y="IA 14 días",
        color="Municipio/Distrito/ZBS",
        template="plotly_white",
        title="Incidencia acumulada en Municipios y Zonas Básicas de Salud de la Comunidad de Madrid",
    )

    fig.update_traces(mode="lines+markers")

    fig.add_shape(
        type="line",
        x0=min(df_filtr["Fecha"]),
        y0=25,
        x1=max(df_filtr["Fecha"]),
        y1=25,
        line=dict(color="red", width=1, dash="dash"),
    )

    fig.add_annotation(
        x=df_filtr["Fecha"].drop_duplicates().nsmallest(4).iloc[-1],
        y=45,
        text="Objetivo de IA",
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
