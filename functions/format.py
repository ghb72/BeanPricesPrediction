import pandas as pd

prices = pd.read_csv('References/Precios Urea.csv')
prices['Date'] = prices['Date'].str.slice(5,8) +'-' + prices['Date'].str.slice(0,4) + '-15'
prices.replace({
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
    })
prices['Price'] = prices['Price'].replace({',':'.','.':'', '"':''})#.astype(float)
prices.to_csv('prices_data/urea_prices.csv')