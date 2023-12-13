import dash
from dash import dcc, html
import plotly.express as px
import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from dash import Dash, callback, ctx, callback_context

acqua = pd.read_csv("acqua.csv")
dropdown_options = [{'label': col, 'value': col} for col in ['Disclosure', 'Source', 'Water stress', 'Fresh']]
discl = [{'label': value, 'value': value} for value in sorted(acqua["Disclosure"].unique())]
sourcedf = [{'label': value, 'value': value} for value in sorted(acqua["Source"].unique())]
type = [{'label': value, 'value': value} for value in sorted(acqua["Fresh"].unique())]
waterstress = [{'label': value, 'value': value} for value in sorted(acqua["Water stress"].unique())]

# Define app layout
layout = html.Div([
    html.H3("Valutazione della Materialità con gli standard GRI"),
    html.P("Verifica il contributo in megalitri di una Fonte al Target, e raggruppa per Variabili intermedie. Scorri nel tempo con lo Slider"),
    html.Div([
        html.Div([
            html.Label("Fonte"),
            dcc.Dropdown(
                options=dropdown_options,
                id='discl',
                placeholder="Seleziona una fonte",
                value= "Disclosure"
            )
        ], style={'width': '33%', 'display': 'inline-block'}),
        
        html.Div([
            html.Label("Variabile intermedia"),
            dcc.Dropdown(
                options=dropdown_options,
                id='varinterm',
                placeholder="Seleziona variabile intermedia",
                value= "Water stress"
            )
        ], style={'width': '33%', 'display': 'inline-block'}),
        html.Div([
            html.Label("Target"),
            dcc.Dropdown(
                options=dropdown_options,
                id='target',
                placeholder="Seleziona un target",
                value= "Source"
            )
        ], style={'width': '33%', 'display': 'inline-block'}),
    ]),

    dcc.Graph(figure={}, id='grafacqua1', style={'width': '99%',
                                                 'display': 'inline-block',
                                                 'margin-top': '0.1%'}),

    dcc.Slider(
        min=acqua['Year'].min(),
        max=acqua['Year'].max(),
        step=None,
        id='slider',
        value=acqua['Year'].max(),
        marks={str(year): str(year) for year in acqua['Year'].unique()},
    )
], style={'width': '100%', 'display': 'inline-block', 'margin-right': '2%'})

@callback(
    Output('grafacqua1', 'figure'),
    Input('discl', 'value'),
    Input('varinterm', 'value'),
    Input('target', 'value'),
    Input('slider', 'value')
)

#DA QUI GIUSTO
def grafico_acqua(disclosure, sel_varint, sel_targ, year_value):
    if disclosure is None or sel_targ is None:
        # Handle the case where one or both dropdowns are not yet selected
        return {'data': []}
    
    selected_columns = [disclosure, sel_targ, sel_varint]
        
    if len(selected_columns) == 3:
        source_column = selected_columns[0]
        target_column = selected_columns[1]
        varint_column = selected_columns[2]
        slided = acqua[acqua['Year'] == year_value]
        dfvarint1 = slided.groupby([source_column, varint_column])['Tot'].sum().reset_index()
        dfvarint1.columns = ['source', 'target', 'value']
        dfvarint2 = slided.groupby([varint_column, target_column])['Tot'].sum().reset_index()
        dfvarint2.columns = ['source', 'target', 'value']
        linksdf = pd.concat([dfvarint1, dfvarint2], axis=0)
        uniquedf = list(pd.unique(linksdf[['source', 'target']].values.ravel('K')))
        # Use the filtered DataFrame for unique values
        dictdf = {k: v for v, k in enumerate(uniquedf)}
        linksdf['source'] = linksdf['source'].map(dictdf)
        linksdf['target'] = linksdf['target'].map(dictdf)
        links_dict = linksdf.to_dict(orient='list')
       
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=uniquedf,
                color="#9FB4C7"  
            ),
            link=dict(
                source=links_dict["source"],
                target=links_dict["target"],
                value=links_dict["value"],
                color="blue"
            ))
        ])
        fig.update_layout(
                          font_size=10,
                          showlegend=True,
                          autosize=True,
                          margin=dict(l=20, r=20, t=20, b=20),
                          title_font=dict(family='Arial', size=20, color='blue')
                          )

        return fig
