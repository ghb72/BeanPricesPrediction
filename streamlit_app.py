import streamlit as st
from app_constants import EXPLAINER
from skforecast.utils import load_forecaster
import pandas as pd
import plotly.graph_objects as go

forecaster = load_forecaster('models/forecaster_101_12_0.005_na_0.019.joblib', verbose=False)
prices_data = pd.read_csv('clean_data/clean_monthly_w_urea.csv', index_col='date')

last_24month_taken = prices_data.tail(24)
last_24month_taken.index = pd.to_datetime(last_24month_taken.index)
last_24month_taken.index = pd.date_range(start=last_24month_taken.index[0], periods=len(last_24month_taken), freq='ME')

# price plots and predictions
def forecast(predict:bool):
    # plotly figure objects PRICE:
    trace_1 = go.Scatter(
        x=last_24month_taken.index, 
        y=last_24month_taken['bayo_price'], 
        mode='lines',
        name='Tendency of real prices'
    )
    trace_3 = go.Scatter(
        x=[last_24month_taken.index[-1]],
        y=[last_24month_taken['bayo_price'].iloc[-1]],
        mode='markers',
        name='Last Price Taken'
    )
    layout_prices = go.Layout(
        title='Bayo Bean Prices Tendency',
        xaxis=dict(title='Date'),
        yaxis=dict(title='Price (MXN)'),
    #     template='simple_white'
    )

    if predict:
        predictions = forecaster.predict(steps=2, last_window=last_24month_taken)

        predictions.loc[last_24month_taken.index[-1]] = last_24month_taken['bayo_price'].iloc[-1]
        predictions.sort_index(inplace=True)

        
        trace_2 = go.Scatter(
            x=predictions.index, 
            y=predictions['bayo_price'], 
            mode='lines', 
            name = 'Forecasting by Month',
            line = {'color':'orange'}
        )
        prices = go.Figure(
            data=[trace_1, trace_2, trace_3],
            layout=layout_prices,
        )
        return prices
    else:
        prices = go.Figure(
            data=[trace_1, trace_3],
            layout=layout_prices,
        )
        return prices

    
def historic_prices_plot():
    return go.Figure(
        data=go.Scatter(
            x=prices_data.index,
            y=prices_data['bayo_price']
        ),
        layout = go.Layout(
            title = 'Historic Prices of Bayo Bean',
            xaxis=dict(title = 'Date'),
            yaxis=dict(title = 'Price (MXN)'),
            # template='simple_white'
        )
    )

def weather_plots():
    rain = go.Figure(
        data = [go.Scatter(x=prices_data.index, y=prices_data['rain'], mode='lines', name='Rain')],
        layout=go.Layout(
            title='Historic Average Rain in the Region',
            xaxis=dict(title='Date'),
            yaxis=dict(title='Average Rain (mm)'),
            # template='simple_white'
        )
    )
    temp = go.Figure(
        data = [
            go.Scatter(x=prices_data.index, y=prices_data['t_min'], mode='lines', name='T min'),
            go.Scatter(x=prices_data.index, y=prices_data['t_max'], mode='lines', name='T max', line ={'color':'orange'}),
        ],
        layout=go.Layout(
            title='Historic Average Temperatures in the Region',
            xaxis=dict(title='Date'),
            yaxis=dict(title='T (ºC)'),
            # template='simple_white'
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
            # template='simple_white'
        )
    )
    urea = go.Figure(
        data=[
            go.Scatter(
                x=prices_data.index,
                y=prices_data['urea_price'],
                mode = 'lines',
                name = 'Urea Prices'
            ),
        ],
        layout=go.Layout(
            title = 'Historic Prices of Urea in Zacatecas',
            xaxis=dict(title='Date'),
            yaxis=dict(title='Price (MXN)')
        )
    )
    return rain, temp, evap, urea



# PAGE STRUCTURE
st.title('Bayo Bean Prices Forecasting' )
st.header('Second Version with better models')
st.text('''
        This is a ML learning app to predict the prices of the Bayo Bean for the principal
        production zone in Mexico, the principal zone is located in Zacatecas State, and 
        it has over 40% production of this variety of Bean. The predicted variable is at 
        2 months in future, and is evaluated each month. The input features of this model are 
        the past prices of bean, urea, and the climatic history of the production region.

        The prices are taken from the Sistema Nacional de Información e Integración de 
        Mercados 
        ''')

prices_tab, weather_tab = st.tabs(['Prices','Weather'])

# prices tab
prices_tab.warning("In the case the graph doesn't charge, please reload the predictions or page")
if prices_tab.form('My form'):
    prices_tab.write('form')
if prices_tab.button('Forecast'):
    prices = forecast(True)
    prices_tab.plotly_chart(prices)
else:
    prices = forecast(False)
    prices_tab.plotly_chart(prices)

historic_prices = historic_prices_plot()
prices_tab.plotly_chart(historic_prices)

# weather tab
weather_tab.header('Weather Variables along time')
# plotly figure objects
rain, temp, evap, urea = weather_plots()
# weather plots in streamlit
weather_tab.plotly_chart(rain)
weather_tab.plotly_chart(temp)
weather_tab.plotly_chart(evap)
weather_tab.plotly_chart(urea)