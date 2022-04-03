from os.path import exists as file_exists
import sqlite3
import pandas as pd
import requests
import json
from datetime import date, timedelta, datetime

# This code gets historical data for the symbol

def get_hist_data(end_date, token, symbol, period, candle):
    # Get historical data between dates provided
    # This uses 'Get Price History' from td ameritrade api
    
    url = 'https://api.tdameritrade.com/v1/marketdata/{}/pricehistory?periodType=day&period={}&frequencyType=minute&frequency={}&endDate={}&needExtendedHoursData=false'.format(symbol, period, candle, end_date)

    payload = {'Authorization' : 'Bearer '+token}
    r = requests.get(url, headers=payload)
    histData = json.loads(r.content)
    
    return histData

# Data base functions
def get_db_connection():
    databaseFile = 'Historical_Data.db'
    dbExists = file_exists(databaseFile)
    connection = sqlite3.connect(databaseFile)
    if not dbExists:
        create_table(connection)    
    return connection
    
def create_table(connection):
    try:
        c = connection.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS histdata (type TEXT PRIMARY KEY,
                                                          date TEXT,
                                                          time TEXT,
                                                          simpletime_UTC TEXT,
                                                          symbol TEXT,
                                                          candle INTEGER,
                                                          volume INTEGER,
                                                          open REAL,
                                                          high REAL,
                                                          low REAL,
                                                          close REAL,
                                                          datetime INTEGER) """)
    except :
        pass

def find_new_data(totalData, connection):
    uniqValues = pd.read_sql_query("SELECT * FROM histdata", connection)
    remove = pd.merge(totalData, uniqValues, how='inner', on=['type'])['type']
    
    totalData = totalData[~totalData['type'].isin(remove)]
    print("New points found {}".format(len(totalData)))
    
    return totalData

# Use your own access token here
access_token = YOUR_OWN_ACCESS_TOKEN

# Get data in this range
tickerdata = {'symbol' : 'SPY', 'period' : 10, 'candle' : 5}

totalData = pd.DataFrame()
data = pd.DataFrame()

# Get the data for last 6 months, iteratively. 
# Note for 1 minute candles, you can get data for only up to two weeks(10 days).
for i in range(12):
    if len(data) > 0:
        end_date = data['simpletime_UTC'].min() - timedelta(days=1)
        print(end_date)
    else:
        end_date = date.today()
        print(end_date)
    end_date_timestamp = int(datetime.timestamp(datetime.combine(end_date, datetime.min.time())))*1000
    
    print("Fetching data for 10 days before {}".format(datetime.fromtimestamp(end_date_timestamp/1000)))
    
    histData = get_hist_data(end_date=end_date_timestamp, token=access_token, symbol=tickerdata['symbol'], period=tickerdata['period'], candle=tickerdata['candle'])
    
    data = pd.DataFrame(histData['candles'])
    # Do the formatting
    data['symbol'] = tickerdata['symbol']
    data['candle'] = tickerdata['candle']
    data['type'] = data['symbol'] + "_" + data['candle'].astype('str') + "_" + (data['datetime']/1000).astype('int').astype('str')
    
    data['simpletime_UTC'] = [datetime.utcfromtimestamp(t/1000) for t in data['datetime']]
    data['date'] = data['simpletime_UTC'].astype('str').str[:10]
    data['time'] = data['simpletime_UTC'].astype('str').str[11:]
    data = data.sort_values(by=['datetime'], ascending=False)
    totalData = pd.concat([totalData,data])

    print("Found {} records".format(len(data)))

# Save trades to sqlite DB
connection = get_db_connection()
totalData = totalData.drop_duplicates(subset='type')
newData = find_new_data(totalData, connection)

print(newData)
newData.to_sql(name='histdata', con=connection, if_exists='append', index=False)
connection.close()
