import json
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pandas as pd
import os
import talib
from twilio.rest import Client

import pandas as pd


account_sid = 'AC4cc6677cf885aab5e8d744f456178499'
auth_token = 'fb4f18abfe1ef68d2c6981c5709add03'
client = Client(account_sid, auth_token)

def send_txt(to,resrow):
    a2 = resrow.to_dict()
    a2['date'] = a2['date'].strftime("%d/%m %Y %H:%M:%S")
    # a3 = json.dumps(a2)
    # msgbdy = 'asset: ' + a2['asset'] + ', TF:' + a2['TimeFrame'] + ', price:' + str(a2['price']) + ', candle:' + a2['TimeFrame']+ ', indic1:' + a2['indicator1'] + ', indic2:' + a2['indicator2']
    # print(msgbdy)
   
    message = client.messages \
                    .create(
                         body='hi',
                         from_='+15855601661',
                         to=to
                     )
    print(message.sid)    
    return message.sid


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
    num_bars = 10000 # number of bars

    bars = mt5.copy_rates_from_pos(setup['asset'], timeframe, start_bar, num_bars)
#     print(bars)
    ticks_frame = pd.DataFrame(bars)
    ticks_frame['date'] = pd.to_datetime(ticks_frame['time'],unit='s')
    ticks_frame = ticks_frame.drop('time', axis=1)
    return ticks_frame

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
    
    if row['close']*(1-val) <= setup['price'] <= row['close']*(1+val):
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
    chck['range'] = row['inRange']


    if(all(value == True for value in chck.values())):
#         print('true' + row['date'].strftime("%d/%m %Y %H:%M:%S"))
        return True
    else:
        return False  
    
def getIndicFxn(df,setup,indcnt):
    indlist1v = pd.read_excel('allind.xlsx')

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
#     tstdf = getChart(setupp).copy() 
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
        # msgbdy = 'asset: ' + setupp['asset'] + ', TF:' + setupp['TimeFrame'] + ', price:' + setupp['price'] + ', candle:' + setupp['TimeFrame']+ ', indic1:' + setupp['indicator1'] + ', indic2:' + setupp['indicator2']

        return "results found!", fnldf
def is_recent(tstdf,mins):
#     print(tstdf)

    latestdiff = datetime.now()-tstdf[tstdf['WEIN?'] == True].iloc[-1].date.to_pydatetime()
    in_minutes = latestdiff.total_seconds() / 60
    return latestdiff < timedelta(minutes=mins), in_minutes

def make_check(instrct):
    chart = getChart(instrct)

    resp,trupts = historialsigs(chart,instrct)

    if not trupts.empty:
        print(resp)
        truth, howrecent = is_recent(trupts,30)
        if(truth):
            print('recent find, ' + str(int(howrecent)) +'mins ago')
            print(trupts[trupts['WEIN?'] == True].iloc[-1])
            
            return trupts[trupts['WEIN?'] == True].iloc[-1]
        else:
            print('old find, ' + str(int(howrecent)) +'mins ago')
            print(trupts[trupts['WEIN?'] == True].iloc[-1])
            # return trupts[trupts['WEIN?'] == True].iloc[-1]
            return pd.DataFrame()
    else:
        print(resp)
        return trupts


def job1(setup):
    print('doing test for setup with asset: ' + setup['asset'] + ' and timeframe ' + setup['TimeFrame']  )
    resultfr = make_check(setup)
#  if resultfr is not empty take the last value and send it as a text
    if resultfr.empty:
        return 'no result'
    res = send_txt(setup['contacts'],resultfr)

    if res == True:
        return "sent message"
    else:
        return "no message sent"


