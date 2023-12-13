import dash
from dash import dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import datetime as dt
import os
from pyairtable import Api
import requests
from datetime import datetime
import pandas as pd
from dash import html
from dash.dependencies import Input, Output
from dash import Dash, callback, ctx, callback_context
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate

app = Dash(__name__, suppress_callback_exceptions=True)
monitor = pd.read_csv("dati.csv")
opzioni_prog = [{'label': value, 'value': value} for value in sorted(monitor["Programma"].unique())]

layout = html.Div([
    html.H3("Non un altro Gantt: visualizza solo gli indicatori che ti servono"),
    html.P("Planned Value, Earned Value e Actual Cost per programmi, progetti e work packages"),
    html.Div([
        html.Div([
            html.Label("Programmi:", style={'fontSize': 30, 'textAlign': 'center'}),
            html.P("Controlla tutti i progetti di un Programma"),
            dcc.Dropdown(
                id='programma',
                options=opzioni_prog,
                value='5 CoastPredict',
                clearable=False,
                placeholder="Seleziona un programma",
                style={"margin-bottom": "2px"}
            ),
            dcc.Graph(
                id='display-map',
                figure={},
                style={'width': '100%', 'display': 'inline-block', 'margin-right': '2%'}
            )
        ], style={'width': '100%', 'display': 'inline-block', 'margin-right': '2%', 'margin-bottom': '20px'}),

        html.Div([
            html.Label("Progetti del Programma selezionato:", style={'fontSize': 30, 'textAlign': 'center'}),
            html.P("Osserva i Work Package di Progetto nel tempo"),
            dcc.Dropdown(id='progetto', options=[], value="16. AI ensemble engine for coastal hazard predictions")
        ], style={'width': '100%', 'margin-bottom': '2px','display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='wpdiprogetto', figure={}, style={'width': '49%',
                                                           'display': 'inline-block',
                                                           "margin-right": "18px"}),
            dcc.Graph(id='grafprogetti', figure={}, style={'width': '49%',
                                                           'display': 'inline-block'})
        ], style={'width': '100%', 'display': 'inline-block'})
])])

# Populate the options of Progetto dropdown based on Programma dropdown
@callback(
    Output('progetto', 'options'),
    Input('programma', 'value')
)
def imp_opzioni_progetti(programma_scelto):
    monitoraggio = pd.read_csv("dati.csv")
    monitoraggio["Data rilevazione"] = pd.to_datetime(monitoraggio["Data rilevazione"], format='%d/%m/%Y', errors='coerce')
    monitoraggio["KPI"] = monitoraggio["KPI"].astype("category")
    monitoraggio["Work Package"] = monitoraggio["Work Package"].astype("string")
    monitoraggio["Programma"] = monitoraggio["Programma"].astype("string")
    monitoraggio["Attività"] = monitoraggio["Attività"].astype("string")
    monitoraggio["Progetto"] = monitoraggio["Progetto"].astype("string")
    monitoraggio["Peso Attività (%)"] = pd.to_numeric(monitoraggio["Peso Attività (%)"].str.replace(',', '.'), errors="coerce", downcast="float")
    monitoraggio["Peso Attività (%)"] = monitoraggio["Peso Attività (%)"].astype("float")
    filtered_progetti = monitoraggio[monitoraggio['Programma'] == programma_scelto]

    return [{'label': c, 'value': c} for c in sorted(filtered_progetti["Progetto"].unique())]

# populate initial values of Progetti dropdown
@app.callback(
    Output('progetto', 'value'),
    Input('progetto', 'options')
)
def valore_progetto(available_options):
    return available_options[0]['value']

@callback(
    Output('display-map', 'figure'),
    Input('progetto', 'value'),
    Input('programma', 'value') 
)

def update_graph(proj_selezionato, progr_selezionato):
    if len(progr_selezionato) == 0:
        return dash.no_update
    else:
        monitor = pd.read_csv("dati.csv")
        monitor["Data rilevazione"] = pd.to_datetime(monitor["Data rilevazione"], format='%d/%m/%Y', errors='coerce')
        monitor["KPI"] = monitor["KPI"].astype("category")
        monitor["Work Package"] = monitor["Work Package"].astype("string")
        monitor["Programma"] = monitor["Programma"].astype("string")
        monitor["Attività"] = monitor["Attività"].astype("string")
        monitor["Progetto"] = monitor["Progetto"].astype("string")
        monitor["Peso Attività (%)"] = pd.to_numeric(monitor["Peso Attività (%)"].str.replace(',', '.'), errors="coerce", downcast="float")
        monitor["Peso Attività (%)"] = monitor["Peso Attività (%)"].astype("float")
        prog = monitor[monitor["Programma"] == progr_selezionato]
        planned_value = prog[prog['KPI'] == 'Planned Value']
        earned_value = prog[prog['KPI'] == 'Earned Value']
        actual_cost = prog[prog['KPI'] == 'Actual Cost']

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=planned_value.groupby('Progetto')['Valore (PV) (€)'].sum().reset_index()['Progetto'],
            y=planned_value.groupby('Progetto')['Valore (PV) (€)'].sum().reset_index()['Valore (PV) (€)'],
            name='Planned Value',
            marker=dict(color='blue',
            opacity = 0.5)
        ))

        fig.add_trace(go.Scatter(
            x=earned_value.groupby('Progetto')['Valore (PV) (€)'].sum().reset_index()['Progetto'],
            y=earned_value.groupby('Progetto')['Valore (PV) (€)'].sum().reset_index()['Valore (PV) (€)'],
            name='Earned Value',
            mode='markers',
            marker=dict(color='lightgreen')
        ))

        fig.add_trace(go.Scatter(
            x=actual_cost.groupby('Progetto')['Valore (PV) (€)'].sum().reset_index()['Progetto'],
            y=actual_cost.groupby('Progetto')['Valore (PV) (€)'].sum().reset_index()['Valore (PV) (€)'],
            name='Actual Cost',
            mode='markers',
            marker=dict(color='red')
        ))
        
        fig.update_layout(
            legend=dict(
                x=0.5,
                y=-0.05,         # Center the legend horizontally
                xanchor='center',
                orientation='h',
                font=dict(
                    color="#9FB4C7"
                )
            ),
            xaxis=dict(showticklabels=False),
            showlegend=True,
            hovermode="x unified",
            hoverlabel=dict(
                font=dict(
                size=10,
                color="#9FB4C7"  # Set the font size for hover labels
            )
            )
        )

        return fig
    
@callback(
    Output('wpdiprogetto', 'figure'),
    Input('progetto', 'value'),
)

def update_graph_due(proj_selezionato):
    if len(proj_selezionato) == 0:
        return dash.no_update
    else:
        monitor = pd.read_csv("dati.csv")
        monitor["Data rilevazione"] = pd.to_datetime(monitor["Data rilevazione"], format='%d/%m/%Y', errors='coerce')
        monitor["KPI"] = monitor["KPI"].astype("category")
        monitor["Work Package"] = monitor["Work Package"].astype("string")
        monitor["Programma"] = monitor["Programma"].astype("string")
        monitor["Attività"] = monitor["Attività"].astype("string")
        monitor["Progetto"] = monitor["Progetto"].astype("string")
        monitor["Peso Attività (%)"] = pd.to_numeric(monitor["Peso Attività (%)"].str.replace(',', '.'), errors="coerce", downcast="float")
        monitor["Peso Attività (%)"] = monitor["Peso Attività (%)"].astype("float")
        prog = monitor[monitor["Progetto"] == proj_selezionato]
        planned_value = prog[prog['KPI'] == 'Planned Value']
        earned_value = prog[prog['KPI'] == 'Earned Value']
        actual_cost = prog[prog['KPI'] == 'Actual Cost']

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=planned_value.groupby('Work Package')['Valore (PV) (€)'].sum().reset_index()['Work Package'],
            y=planned_value.groupby('Work Package')['Valore (PV) (€)'].sum().reset_index()['Valore (PV) (€)'],
            name='Planned Value',
            marker=dict(color='blue',
            opacity = 0.5)
        ))

        fig.add_trace(go.Scatter(
            x=earned_value.groupby('Work Package')['Valore (PV) (€)'].sum().reset_index()['Work Package'],
            y=earned_value.groupby('Work Package')['Valore (PV) (€)'].sum().reset_index()['Valore (PV) (€)'],
            name='Earned Value',
            mode='markers',
            marker=dict(color='lightgreen')
        ))

        fig.add_trace(go.Scatter(
            x=actual_cost.groupby('Work Package')['Valore (PV) (€)'].sum().reset_index()['Work Package'],
            y=actual_cost.groupby('Work Package')['Valore (PV) (€)'].sum().reset_index()['Valore (PV) (€)'],
            name='Actual Cost',
            mode='markers',
            marker=dict(color='red')
        ))
        
        fig.update_layout(
            legend=dict(
                x=0.4,
                y=-0.1,         # Center the legend horizontally
                xanchor='center',
                orientation='h',
                font=dict(
                    size=10,
                    color="#9FB4C7"
                )
            ),
        xaxis=dict(showticklabels=False),
        showlegend=True,
        hovermode="x unified",
        hoverlabel=dict(
            font=dict(
                size=10,
                color="#9FB4C7"  # Set the font size for hover labels
            )
        )
        )
        return fig

@callback(
    Output('grafprogetti', 'figure'),
    Input('progetto', 'value') 
)

def ritornagraf(proj_selezionato):
    if len(proj_selezionato) == 0:
        return dash.no_update
    else:
        monitor = pd.read_csv("dati.csv")
        monitor["Data rilevazione"] = pd.to_datetime(monitor["Data rilevazione"], format='%d/%m/%Y', errors='coerce')
        monitor["KPI"] = monitor["KPI"].astype("category")
        monitor["Work Package"] = monitor["Work Package"].astype("string")
        monitor["Programma"] = monitor["Programma"].astype("string")
        monitor["Attività"] = monitor["Attività"].astype("string")
        monitor["Progetto"] = monitor["Progetto"].astype("string")
        monitor["Peso Attività (%)"] = pd.to_numeric(monitor["Peso Attività (%)"].str.replace(',', '.'), errors="coerce", downcast="float")
        monitor["Peso Attività (%)"] = monitor["Peso Attività (%)"].astype("float")
        prog = monitor[monitor["Progetto"] == proj_selezionato]
        planned_value = prog[prog['KPI'] == 'Planned Value']
        earned_value = prog[prog['KPI'] == 'Earned Value']
        actual_cost = prog[prog['KPI'] == 'Actual Cost']

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=prog["Data rilevazione"].unique(),
            y=planned_value.groupby("Data rilevazione")['Valore (PV) (€)'].sum().reset_index()['Valore (PV) (€)'],
            name='Planned Value',
            mode='lines+markers',  # Set the mode for the entire trace
            marker=dict(
                color='blue'
            )
        ))

        fig.add_trace(go.Scatter(
            x=prog["Data rilevazione"].unique(),
            y=earned_value.groupby("Data rilevazione")['Valore (PV) (€)'].sum().reset_index()['Valore (PV) (€)'],
            name='Earned Value',
            mode='lines+markers',
            marker=dict(color='lightgreen')
        ))

        fig.add_trace(go.Scatter(
            x=prog["Data rilevazione"].unique(),
            y=actual_cost.groupby("Data rilevazione")['Valore (PV) (€)'].sum().reset_index()['Valore (PV) (€)'],
            name='Actual Cost',
            mode='lines+markers',
            marker=dict(color='red')
        ))
        
        fig.update_layout(
            legend=dict(
                x=0.5,
                y=-0.1,         # Center the legend horizontally
                xanchor='center',
                orientation='h',
                font=dict(
                    size=10,
                    color="#9FB4C7")
            ),
            xaxis=dict(
            showticklabels=True,  # Set to True to show tick labels
            tickvals=prog["Data rilevazione"].unique(),  # Specify tick positions
            ticktext=prog["Data rilevazione"].unique().strftime('%d/%m/%Y'),  # Specify corresponding tick labels
            ),
            showlegend=True,
            hovermode="x unified",
            hoverlabel=dict(
            font=dict(
                size=10,
                color="#9FB4C7"  # Set the font size for hover labels
            )
        )
        )
        return fig
