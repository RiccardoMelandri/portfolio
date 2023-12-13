import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
from pages import home, seconda
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

external_stylesheets = ['assets/header.css']

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server

linkedin_url = "https://www.linkedin.com/in/riccardo-melandri-a583306b/"
cv_filename = "Riccardo Melandri Curriculum Vitae.pdf"
cv_filepath = f"./{cv_filename}"

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# padding for the page content
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H4("Portfolio", className="display-3"),
        html.Hr(),
        html.P(
            "Dati per il project management e per la sostenibilità aziendale", className="lead"
        ),
        html.Hr(),
        html.P("Seleziona"),
        dbc.Nav(
            [
                dbc.NavLink("Project management", href="/", active="exact"),
                dbc.NavLink("Materialità dell'acqua (GRI)", href="/seconda", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
        html.Div([
            html.P("Info e contatti:"),
            html.A("Profilo LinkedIn", href=linkedin_url, target="_blank", style={'color': '#141721'}),
            html.Br(),
            dcc.Download(id="download-cv-link"),
            html.A("Download CV", id="download-cv-button", href="#", n_clicks=0, style={'color': '#141721'})
                        
        ], style={
            'margin-top': '100px',
            'width': '100%',  # Set the width of the dropdown
            'border': '2px solid #000',  # Add a 2px solid black border
            'border-radius': '5px',  # Optional: Add border radius for rounded corners
            'padding': '5px',
            'color': '#141721',
            'background-color': '#9FB4C7'
        }),
        
    ], 
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", children=[], style=CONTENT_STYLE)

app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    content
])

@app.callback(
    Output("download-cv-link", "data"),
    Input("download-cv-button", "n_clicks"),
    prevent_initial_call=True
)
def download_cv(n_clicks):
    if n_clicks is None:
        raise PreventUpdate

    return dcc.send_file(cv_filepath, filename=cv_filename)

@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def render_page_content(pathname):
    if pathname == "/":
        return home.layout,
                
    elif pathname == "/seconda":
        return seconda.layout,
                
if __name__ == '__main__':
    app.run_server(debug=True,port=100)