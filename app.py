# importing libraries
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import Dash, html, callback, Input, Output, dcc
from app_constants import EXPLAINER
from skforecast.utils import load_forecaster
import pandas as pd

forecaster = load_forecaster('models/forecaster_32_2_0.0005_na_0.0054.joblib', verbose=False)
prices_data = pd.read_csv('clean_data/clean_data_simple.csv', index_col='date')
last_180days_taken = prices_data.tail(180)
last_180days_taken.index = pd.to_datetime(last_180days_taken.index)
last_180days_taken.index = pd.date_range(start=last_180days_taken.index[0], periods=len(last_180days_taken), freq='D')
onlyday15 = last_180days_taken[last_180days_taken.index.day == 15]

app  = Dash(external_stylesheets=[dbc.themes.JOURNAL])

app.layout = dbc.Container([
    html.H1('Bayo Bean Prices Prediction'),
    dcc.Markdown(EXPLAINER),
    dbc.Button(
        'Regenerate predictions',
        color='primary',
        id='button',
        class_name='mb-1'
        ),
    dbc.Tabs(
        [
            dbc.Tab(label='prices', tab_id='prices'),
            dbc.Tab(label='weather', tab_id='weather'),
        ],
        id='tabs',
        active_tab='prices'
    ),
    dbc.Spinner(
        [
            dcc.Store(id='store'),
            html.Div(id='tab-content', className='p-4')
        ],
        delay_show=100
    )
])

@app.callback(
        Output('tab-content','children'),
        [Input('tabs','active_tab'), Input('store','data')]
)
def refeder_tab_content(active_tab, data):
    """This callbacks renders the active tab taking as imput the active tab variable and the stored data"""
    if active_tab and data is not None:
        if active_tab == 'prices':
            return [
                dbc.Alert("In case the graph don't charge, reload the predictions", color='danger'),
                dbc.Alert("The Predictions are made each month, or when the data is published", color='light'),
                dcc.Graph(figure=data['prices'])
                ]
        elif active_tab == 'weather':
            return [
                dcc.Graph(figure=data['rain']),
                dcc.Graph(figure=data['temp']),
                dcc.Graph(figure=data['evap'])
            ]
    return 'No tab selected'


@app.callback(Output('store','data'),
              [Input('button', 'n_clicks')])
def generate_graphs(n):
    """This callback generates the graphs for prices and weather"""

    if not n:
        # generatiing empty plots for loading page
        return {k:go.Figure(data=[]) for k in ['prices','rain','t_max','temp','evap']}
    
    #making predictions
    predictions = forecaster.predict(steps=30, last_window=last_180days_taken)
    #

    #making traces of plotly go for prices and predictions
    trace_1 = go.Scatter(
        x=last_180days_taken.index, 
        y=last_180days_taken['price'], 
        mode='lines', 
        name='Tendency of real prices'
    )
    trace_2 = go.Scatter(
        x=predictions.index, 
        y=predictions['price'], 
        mode='lines', 
        name = 'Forecasting by Day'
    )
    trace_3 = go.Scatter(
        x=onlyday15.index, 
        y=onlyday15['price'], 
        mode='lines', 
        name='Real Prices taken'
    )
    layout_prices = go.Layout(
        title='Bayo Bean Prices Tendency',
        xaxis=dict(title='Date'),
        yaxis=dict(title='Price (MXN)'),
        template='simple_white'
    )
    prices = go.Figure(
        data=[trace_1, trace_2, trace_3],
        layout=layout_prices,
    )
    rain = go.Figure(
        data = [go.Scatter(x=prices_data.index, y=prices_data['rain'], mode='lines', name='Rain')],
        layout=go.Layout(
            title='Historic Average Rain in the Region',
            xaxis=dict(title='Date'),
            yaxis=dict(title='Average Rain (mm)'),
            template='simple_white'
        )
    )
    temp = go.Figure(
        data = [
            go.Scatter(x=prices_data.index, y=prices_data['t_min'], mode='lines', name='T min'),
            go.Scatter(x=prices_data.index, y=prices_data['t_max'], mode='lines', name='T max'),
        ],
        layout=go.Layout(
            title='Historic Average Temperatures in the Region',
                xaxis=dict(title='Date'),
                yaxis=dict(title='T (ºC)'),
                template='simple_white'
        )
    )
    evap = go.Figure(
        data = [
            go.Scatter(
                x=prices_data.index, 
                y=prices_data['evap'], 
                mode='lines',
                name='Evaporation'
            )
        ],
        layout=go.Layout(
            title='Historic Average Evaporation in the Region',
            xaxis=dict(title='Date'),
            yaxis=dict(title='Evaporation (mm)'),
            template='simple_white'
        )
    )

    return {'prices':prices, 'rain':rain, 'temp':temp, 'evap':evap}

server = app.server

if __name__ == '__main__':
    app.run(jupyter_mode='external', debug=True)