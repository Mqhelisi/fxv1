import json
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pandas as pd
import os
import talib
from twilio.rest import Client

account_sid = 'AC4cc6677cf885aab5e8d744f456178499'
auth_token = 'fb4f18abfe1ef68d2c6981c5709add03'
client = Client(account_sid, auth_token)
# Function to start Meta Trader 5 (MT5)

def send_txt(to,resrow):
    message = client.messages \
                    .create(
                         body="Join Earth's mightiest heroes. Like Kevin Bacon.",
                         from_='+15855601661',
                         to=to
                     )
    return message.sid
    # print(message.sid)

indlist1v = pd.read_excel('allind.xlsx')

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

            return True
        else:
            print("Login Fail")
            quit()
            return PermissionError
    else:
        print("MT5 Initialization Failed")
        quit()
        return ConnectionAbortedError

def getChart(setup):
    res = {'5Min': 5,'15Min': 15, '30Min': 30, '1H': 60, '2H': 120, '4H': 360, '12H': 720}    
    timeframe = res[setup['TimeFrame']] # integer value representing minutes
    start_bar = 0 # initial position of first bar
    num_bars = 50000 # number of bars

    bars = mt5.copy_rates_from_pos(setup['asset'], timeframe, start_bar, num_bars)
    ticks_frame = pd.DataFrame(bars)
    ticks_frame['date'] = pd.to_datetime(ticks_frame['time'],unit='s')
    ticks_frame = ticks_frame.drop('time', axis=1)
    return ticks_frame

def getCh2(val):
    money = pd.read_excel('Gold.xlsx')
    money = money.drop(['Unnamed: 0'], axis=1)
    return money

def getcandle(df,setup):

    openn = "tstdf['open']"
    high = "tstdf['high']"
    low = "tstdf['low']"
    close = "tstdf['close']"

    a = "tstdf['"+setup['candlepattern']+"']" + " = talib." + setup['candlepattern'] + "(" + openn + "," + high + ","+ low + ","+ close +")"
    # print(a)
    return a

def inRange(row,setup):
    val = setup['range']*0.01
    if row['close']*(1-val) <= setupp['price'] <= row['close']*(1+val):
        return True
    else:
        return False

def paRange(inp,val,trgt):
    val = val*0.01
    if trgt*(1-val) <= inp <= trgt*(1+val):
        return True
    else:
        return False
  
def are_we_in(row,setup):
    chck=dict()
    val = setup['range']*0.01
    if setup['ind1v'] != None:
        if paRange(row[setup['indicator1']],4,setup['ind1v']):
    #         print('param1True')
            chck[setup['indicator1']] = True
        else:
            chck[setup['indicator1']] = False
        
    if setup['ind2v'] != None:

        if paRange(row[setup['indicator2']],4,setup['ind2v']):
    #         print('param2True')

            chck[setup['indicator2']] = True
        else:
            chck[setup['indicator2']] = False
        
        
    if(row[setup['candlepattern']] == setup['cdlval']):
        chck[setup['candlepattern']] = True
    else:
        chck[setup['candlepattern']] = False
        
    if(all(value == True for value in chck.values())):
        print('true' + row['date'].strftime("%d/%m %Y %H:%M:%S"))
        return True
    else:
        return False  
    
def getIndicFxn(df,setup,indcnt):
    if indcnt == 1:

        indic = indlist1v[indlist1v['value'] == setup['indicator1']].to_dict('records')[0]
        indicc = setup['indicator1']
    elif indcnt == 2:
     
        indic = indlist1v[indlist1v['value'] == setup['indicator2']].to_dict('records')[0]  
        indicc = setup['indicator2']
        

    a = ""
    prm = 'params'+str(indcnt)
    for each in setup[prm]:
        a=a + ","+each+"="+str(setup[prm][each])

    a=a+")"
    

    high = "tstdf['high']"
    low = "tstdf['low']"
    close = "tstdf['close']"
    if 'MA' in indicc or indicc == 'APO':
        a = "tstdf['"+indicc+"']" + " = talib." + indicc + "(" + close + a
#         print(a)
        return a
    if indicc == "STOCH":
        a = "tstdf['"+indicc+"']" + ","+"tstdf['"+indicc+"2']" +","+ " = talib." + indicc + "(" + high + ","+ low + ","+ close +a
        return a
    a = "tstdf['"+indicc+"']" + " = talib." + indicc + "(" + high + ","+ low + ","+ close +a
    # print(a)
    return a

def controlIndicators(tstdf,setupp):
# get the chart, MAKE IT DESCENDING ORDER OF DATE?? get last price isolated??
    tstdf = getCh2(setupp).copy() 
    # search chart for indicator 1
    if setupp['ind1v'] != None:
    #     print('found ind1')
        exec(getIndicFxn(tstdf,setupp,1))
    # search for indicator 2
    if setupp['ind2v'] != None:
    #     print('found ind2')
        exec(getIndicFxn(tstdf,setupp,2))
    # search for candlestick
    if setupp['candlepattern'] != 'None':

        exec(getcandle(tstdf,setupp))
    # search if in range
    tstdf['inRange'] = tstdf.apply(lambda x: inRange(x,setupp), axis=1)
    # search records for if they fit the required params

    return tstdf

def siphakthi(tstdf,setp):
    tstdf['WEIN?'] = tstdf.apply(lambda x: are_we_in(x,setp), axis=1)

    return tstdf

def historialsigs(tstdf, setupp):
    tstdf = controlIndicators(tstdf,setupp)
    tstdf = siphakthi(tstdf,setupp)


    fnldf = tstdf[tstdf['WEIN?'] == True]
    if fnldf.empty:
        return "no value", fnldf
    else:
        return "results found!", fnldf

setupp = {'asset': 'Volatility 100 Index',
 'ind1v': None,
 'ind2v': None,
 'ind1c': None,
 'ind2c': None,
 'price': 7960.0,
 'range': 1.0,
 'cdlval': 100,
 'indicator1': 'MA',
 'indicator2': None,
 'params1': None,
 'params2': None,
 'candlepattern': 'CDLDOJI',
 'TimeFrame': '5Min',
 'Expiry': '04/05 2023 00:00',
 'SetDate': '01/04 2023 00:00'}

def is_recent(tstdf):

    latestdiff = datetime.now()-tstdf[tstdf['WEIN?'] == True].iloc[-1].name.to_pydatetime()
    return latestdiff < timedelta(minutes=30)

def make_check(instrct):
    chart = getChart(instrct)

    resp,trupts = historialsigs(chart,instrct)

    if not trupts.empty:
        print(resp)

        if is_recent(trupts,30):
            print('recent find')
            return trupts[trupts['WEIN?'] == True].iloc[-1]
        else:
            print('old find')
            return trupts[trupts['WEIN?'] == True].iloc[-1]
    else:
        print(resp)
        return None
