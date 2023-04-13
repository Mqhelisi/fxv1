
import MetaTrader5 as mt5
from datetime import datetime
import pandas as pd
import os
# Function to start Meta Trader 5 (MT5)
def start_mt5(username, password, server, path):
    # Ensure that all variables are the correct type
    uname = int(username) # Username must be an int
    pword = str(password) # Password must be a string
    trading_server = str(server) # Server must be a string
    filepath = str(path) # Filepath must be a string

    # Attempt to start MT5
    if mt5.initialize(login=uname, password=pword, server=trading_server, path=filepath):
        # Login to MT5
        print('initialized, attempting login')
        if mt5.login(login=uname, password=pword, server=trading_server):
            print('login success')

            v10_ticks = mt5.copy_ticks_from("Volatility 10 Index",
            datetime(2020,1,28,13), 1000,
            mt5.COPY_TICKS_ALL)
            # path = os.getcwd()
            # ticks_frame = pd.DataFrame(v10_ticks)
            # writer = pd.ExcelWriter()
            # ticks_frame.to_excel(writer)
            # # df2.to_excel(writer, sheet_name = 'x2')
            # writer.close()
            return True
        else:
            print("Login Fail")
            quit()
            return False
    else:
        print("MT5 Initialization Failed")
        quit()
        return False
    

def getChart(tmfrm,asset):
    res = {'5Min': 5,'15Min': 15, '30Min': 30, '1H': 60, '2H': 120, '4H': 360, '12H': 720}  
    print(res[tmfrm])
    timeframe = res[tmfrm] # integer value representing minutes
    start_bar = 0 # initial position of first bar
    num_bars = 30000 # number of bars

    bars = mt5.copy_rates_from_pos(asset, timeframe, start_bar, num_bars)
    ticks_frame = pd.DataFrame(bars)
#     print(ticks_frame)
    ticks_frame['date'] = pd.to_datetime(ticks_frame['time'],unit='s')
    ticks_frame = ticks_frame.drop('time', axis=1)

    ticks_frame = ticks_frame.set_index('date')

    ticks_frame = resampling(ticks_frame,tmfrm)
    return ticks_frame

def resampling(df,tf):
    df = df.resample(tf).agg(
    {
        'open':'first',
        'high':'max', 
        'low':'min',
        'close':'last',
        
    }
    )
    return df