import json
# import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pandas as pd
import talib
import pandas as pd
import telegram_send
import os
import asyncio
from metaapi_cloud_sdk import MetaApi
from metaapi_cloud_sdk.clients.metaApi.tradeException import TradeException

# Note: for information on how to use this example code please read https://metaapi.cloud/docs/client/usingCodeExamples
loop2 = asyncio.get_event_loop()

async def test_meta_api_synchronization():


    token = os.getenv('TOKEN') or 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiIwNTRkMzYxZjkzODVkM2Y5ZTM5ZjM0YTNmN2VjZjI2ZiIsInBlcm1pc3Npb25zIjpbXSwidG9rZW5JZCI6IjIwMjEwMjEzIiwiaW1wZXJzb25hdGVkIjpmYWxzZSwicmVhbFVzZXJJZCI6IjA1NGQzNjFmOTM4NWQzZjllMzlmMzRhM2Y3ZWNmMjZmIiwiaWF0IjoxNjk2NzY2NTM0fQ.aHlfg_mY0s1_eY8RSODMfZIE1WUfsmZ3ciDpdPTV-MUuAkTDcvz79iBaXeTRSFytzn5rCrx_gnvudP146uXjx5sn_iOviUOU6st-xnvudOjC4LEC2x_WPVkFzCYPmezWkq13RhLs0BTkcrXifEp0hjxW1pI52usmI0xi2weVf7Hwxx0rp60_gQMS87L45qkY_azUTUqeqTsuIP6gcuM45XYVjxo0w_eFirHNbNG93c4w0jxW9VlgOzFj5ehJB5cz8ttSMwdHxvOKZAqixLLD94p2vf_l-rthnaf3F6ssOmst1iVXl_FRLpSzB6i3W-FpscOAsq4KOAbAQf1_ISk-qVH2DiOwLkN2TCTQa_SrEvv86m87krDZtSfSSjoq_CTWzM5s3NTn-Fq8wSx4pWJUEe0J9odS5lX5tC15Ag0tYXvrBiWqAJ_OTiXBiIDpFvFJc8M_8jZEnbJUXCJQy5xlbbgI3lZ1CyGUQzf-gZHt64vi1r7VsyMVpNSimzvrDfTrgObikf2VTsh4McJh6Ohh0btRTazThz750GD1pLyWVBR4TwRw4ZpDSKv5yW9o60xc-0Acv89syqohLBQYihJA2YMnEIjA391leT-B2CJCFjn8spdtsbrtFASjK173hVKdNrrWyh8uuUYoqt0PF-zKQ34XhF9FZSz1gAeJ3z2eKkU'
    accountId = os.getenv('ACCOUNT_ID') or 'c7134157-6e22-4920-abf1-59e474c6d8a4'

    api = MetaApi(token)
    
    account = await api.metatrader_account_api.get_account(accountId)
    initial_state = account.state
    deployed_states = ['DEPLOYING', 'DEPLOYED']

    if initial_state not in deployed_states:
        #  wait until account is deployed and connected to broker
        print('Deploying account')
        await account.deploy()

    print('Waiting for API server to connect to broker (may take couple of minutes)')
    await account.wait_connected()

    # connect to MetaApi API
    connection = account.get_rpc_connection()
    await connection.connect()

    # wait until terminal state synchronized to the local state
    print('Waiting for SDK to synchronize to terminal state (may take some time depending on your history size)')
    await connection.wait_synchronized()


#         symbol = os.getenv('SYMBOL') or 'EURUSD'
    if initial_state not in deployed_states:
        # undeploy account if it was undeployed
        print('Undeploying account')
        await connection.close()
        await account.undeploy() 


    return account

def send_txt(resrow,setuppp):
    a2 = resrow.to_dict()
    print(a2)

    a2['date'] = a2['date'].strftime("%d/%m %Y %H:%M:%S")

    result = json.dumps(a2)
    asst = "Indicator ID: " + str(setuppp['id'])
    asst1 = "Indicator for asset: " + setuppp['asset']
    tyme = "Found at time: " + str(a2['date'])
    openn = "Open Price at: " + str(a2['open'])
    tickvol = "Tick Volume of: " + str(a2['tick_volume'])
    textt = asst + '\n' + asst1 + '\n' + tyme + '\n' + openn + '\n' + tickvol
    res = telegram_send.send(messages=[textt])
    # print(res)    
    return True


def getChart(setup):
    res = {'5Min': 5,'15Min': 15, '30Min': 30, '1H': 60, '2H': 120, '4H': 360, '12H': 720}    
    timeframe = res[setup['TimeFrame']] # integer value representing minutes
    start_bar = 0 # initial position of first bar
    num_bars = 10000 # number of bars

    # bars = mt5.cop    `y_rates_from_pos(setup['asset'], timeframe, start_bar, num_bars)
#     print(bars)
    ticks_frame = pd.DataFrame(bars)
    ticks_frame['date'] = pd.to_datetime(ticks_frame['time'],unit='s')
    ticks_frame = ticks_frame.drop('time', axis=1)

    return ticks_frame


async def anotherChart(asst,account):
        
    # retrieve last 10K 1m candles
    pages = 2
    print(f'Downloading {pages}K latest candles for {asst}')
    started_at = datetime.now().timestamp()
    start_time = None
    candles = None
    prcDf = pd.DataFrame()
    for i in range(pages):
        # the API to retrieve historical market data is currently available for G1 and MT4 G2 only
        new_candles = await account.get_historical_candles(asst, '5m', start_time)

        print(f'Downloaded {len(new_candles) if new_candles else 0} historical candles for {asst}')
        newDf = pd.DataFrame(new_candles)
        prcDf = pd.concat([prcDf,newDf])    
        if new_candles and len(new_candles):
            candles = new_candles
        if candles and len(candles):
            start_time = candles[0]['time'] 
            print(start_time.minute)
            if(start_time.minute == 0):
                start_time.replace(minute=59)
            else:
                start_time.replace(minute=start_time.minute - 1)

            print(f'First candle time is {start_time}')
    if candles:
        print(f'First candle is', candles[0])
    print(f'Took {(datetime.now().timestamp() - started_at) * 1000}ms')
    prcDf['brokerTime'] = pd.to_datetime(prcDf['brokerTime'])
    prcDf = prcDf.drop(columns=['time','timeframe','symbol','volume']).rename(columns={"brokerTime": "date"})
    return prcDf







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
    # print(setup['candlepattern'])
    if(setup['candlepattern'] == None):
        chck[setup['candlepattern']] = True

    elif(row[setup['candlepattern']] != setup['cdlval']):
        chck[setup['candlepattern']] = False
    else:
        chck[setup['candlepattern']] = True
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
    if setupp['candlepattern'] != None:

        exec(getcandle(tstdf,setupp))
    # search if in range
    tstdf['inRange'] = tstdf.apply(lambda x: inRange(x,setupp), axis=1)
    # search records for if they fit the required params

    return tstdf

def siphakthi(tstdf,setp):
    tstdf['WEIN?'] = tstdf.apply(lambda x: are_we_in(x,setp), axis=1)

    return tstdf
def historialsigs(tstdf, setupp):
    print(setupp)
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
    tz_corrected_mins = in_minutes-120
    return latestdiff < timedelta(minutes=mins), tz_corrected_mins


def make_check(chart,instrct):
    # chart = loop2.run_until_complete(anotherChart(instrct,acc))
    
    # chart = await anotherChart(instrct,acc)
    resp,trupts = historialsigs(chart,instrct)

    if not trupts.empty:
        print(trupts)
        truth, howrecent = is_recent(trupts,30)
        if(int(howrecent) < 16):
            print('recent find, ' + str(int(howrecent)) +'mins ago')
            # print(trupts[trupts['WEIN?'] == True].iloc[-1])

            res = send_txt(trupts[trupts['WEIN?'] == True].iloc[-1],instrct)

            if res == True:
                print("sent message")
            else:
                print("no message sent")
            
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



