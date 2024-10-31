import streamlit as st
from app_constants import EXPLAINER
from skforecast.utils import load_forecaster
import pandas as pd

forecaster = load_forecaster('models/forecaster_32_2_0.0005_na_0.0054.joblib', verbose=False)
prices_data = pd.read_csv('clean_data/clean_data_simple.csv', index_col='date')
last_180days_taken = prices_data.tail(180)
last_180days_taken.index = pd.to_datetime(last_180days_taken.index)
last_180days_taken.index = pd.date_range(start=last_180days_taken.index[0], periods=len(last_180days_taken), freq='D')
onlyday15 = last_180days_taken[last_180days_taken.index.day == 15]

# predictions
predictions = forecaster.predict(steps=30, last_window=last_180days_taken)
    

# PAGE STRUCTURE
st.title('Bayo Bean Prices Prediction')
st.text('''
        This is a ML learning app to predict the prices of the Bayo Bean for the principal
        production zone in Mexico, the principal zone is located in Zacatecas State, and 
        it has over 40% production of this variety of Bean. The predicted variable is at 
        30 days in future, and is evaluated each month. The dependences of this model are 
        the past prices of bean and the climatic history of the production region.

        The prices are taken from the Sistema Nacional de Información e Integración de 
        Mercados 
        ''')

prices_tab, weather_tab = st.tabs(['Prices','Weather'])

# prices tab
prices_tab.warning("In the case the graph doesn't charge, please reload the predictions or page")
prices_tab.line_chart(predictions)

# weather tab
weather_tab.header('st.p')