# importing libraries
import pandas as pd
import calendar
from os import listdir
import numpy as np

def take_name(file):
    with open(file, 'r', encoding='utf-8') as file_text:
        lines = file_text.readlines()
        for line in lines:
            if line.startswith(' NOMBRE'):
                name_place = line.split(':')[1].strip()
                name_place = name_place.replace(' ','_')
                return name_place

def read_weather_df(folder:str ='weather_data/raw_daily') -> pd.DataFrame:
    """This functionn read all the files in format .txt,
    taken from df/daily folder and prepares it to have
    a raw weather data dataframeframe"""

    df = pd.DataFrame()
    name_files = listdir(folder)
    for file in name_files:
        place = take_name(folder+'/'+file)
        df_place = pd.read_csv(f'{folder}/{file}', skiprows=25, sep=r'\s+', names =['date',f'rain_{place}',f'evap_{place}',f't_max_{place}',f't_min_{place}'], index_col='date')
        df = pd.concat([df, df_place], join='outer', axis=1)
    
    df.index = pd.to_datetime(df.index)
    df.dropna(how='all', inplace=True)
    df.replace('NULO', np.nan, inplace=True)
    df.sort_index(inplace=True)
    df = df.astype(float)
    
    return df

def prepare_mean_df(df:pd.DataFrame, verbose:bool = False) -> pd.DataFrame:
    """Creates a new dfframe to have the means of the
    df in the dfframe with cols ['rain','evap','t_max','t_min']"""

    total = len(df)
    to_drop_columns = []
    for col in df.columns:
        number = df[col].count()
        percent = ((total-number)/total)*100
        if percent > 90:
            to_drop_columns.append(col)
            indicator = '(Column Dropped!)'
        elif percent < 90:
            indicator= ''
        if verbose:
            print(f'Rows in {col}: {number}, Miss Data: {total-number}, % Missed = {percent}, {indicator}')
    df.drop(columns=to_drop_columns, inplace=True)

    df = df.copy()

    df['rain'] = df[[col for col in df.columns if 'rain' in col]].mean(axis=1)
    df['t_max'] = df[[col for col in df.columns if 't_max' in col]].mean(axis=1)
    df['t_min'] = df[[col for col in df.columns if 't_min' in col]].mean(axis=1)
    df['evap'] = df[[col for col in df.columns if 'evap' in col]].mean(axis=1)
    df_mean = df[['rain','evap','t_max','t_min']].copy()

    df_mean['date'] = df_mean.index
    df_mean['month'] = df_mean['date'].dt.month
    df_mean['year'] = df_mean['date'].dt.year
    df_mean.drop(columns='date',inplace=True)
    return df_mean

def read_prices(file:str, dropna=False, daynumber = 15) -> pd.DataFrame:
    """This function read prices from a csv file with format: \n
    Ano,Ene,Feb,Mar,Abr,May,Jun,Jul,Ago,Sep,Oct,Nov,Dic
    1998,4.88,6,6,6,6,6.50,7,8,7.70,7,7.12,6.80
    1999,7,6.50,6.30,6.50,5.75,5.60,6,6.38,6.50,6.50,5.75,4.50
    
    Daynumber will be the day of month in wich price is located"""

    try:
        data = pd.read_csv(file)
        data.replace('\r\n',np.nan, inplace=True)
        data = data.melt(id_vars=['Ano'])
        data.replace({
            'Ene': 1,
            'Feb': 2,
            'Mar': 3,
            'Abr': 4,
            'May': 5,
            'Jun': 6,
            'Jul': 7,
            'Ago': 8,
            'Sep': 9,
            'Oct': 10,
            'Nov': 11,
            'Dic': 12
        }, inplace=True)

        def combinar_año_mes(row):
            return pd.to_datetime(f"{row['year']}-{row['month']}-{15}", format="%Y-%m-%d")
    
        data.columns = ['year','month','price']
        data['date'] = data.apply(combinar_año_mes, axis=1)
        data.drop(columns=['year','month'], inplace=True)
        data.set_index('date',inplace=True)
        data = data.sort_index().astype(float)

        if dropna == True:
            data.dropna(inplace=True)

        return data
    except:
        print('Invalid Format in prices csv File')
        return pd.DataFrame()

def give_all_data(prices_file:str, weather_folder:str = 'weather_data/raw_daily',  cut_date:str='last price', daynumber:int = 15, method:str = 'akima', verbose:bool = False) -> pd.DataFrame:

    """
    To take all processed data from the original downloaded files
    cut_date must be an format like '2024-08-15', if cut_date == 'last',
    cut_date will be the last date of taken prices.
    
    This function interpolates the prices data with akima method.
    to make all the procedure by own, you must do:
    
    prices = read_prices(prices_file,daynumber=daynumber)
    first_day_price = prices.index.values[0]
    last_day_price = prices.index.values[-1]
    weather_data = read_weather_df(folder=weather_folder)
    weather_mean_data = prepare_mean_df(weather_data)

    data = weather_data.loc[first_day_price:].join(prices)

    filled_data = data[['rain','evap','t_max','t_min']].interpolate(method='time')
    filled_data['price']  = data['price'].interpolate(method='akima')

    if cut_date is None:
        cut_date = last_day_price

    filled_data = filled_data.loc[:cut_date]
    """

    prices = read_prices(prices_file,daynumber=daynumber)
    prices.dropna(inplace=True)
    first_day_price = prices.index.values[0]
    last_day_price = prices.index.values[-1]
    weather_data = read_weather_df(folder=weather_folder)
    weather_mean_data = prepare_mean_df(weather_data, verbose=verbose)

    data = weather_mean_data.loc[first_day_price:].join(prices)

    filled_data = data[['rain','evap','t_max','t_min']].interpolate(method='time')
    filled_data['price']  = data['price'].interpolate(method='akima')

    if cut_date == 'last price':
        cut_date = last_day_price

    filled_data = filled_data.loc[:cut_date]
    print(last_day_price)
    return filled_data


