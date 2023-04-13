from flask import Flask
from flask_apscheduler import APScheduler
import apscheduler
import json
import MetaTrader5 as mt5
from datetime import datetime
import pandas as pd
import os
import talib
from flask_sqlalchemy import SQLAlchemy
from testlogic import start_mt5,send_txt,are_we_in,make_check
# Function to start Meta Trader 5 (MT5)

indlist1v = pd.read_excel('allind.xlsx')


username = '30585595'
password = 'TestBotApp1'
server2 = 'Deriv-Demo'
path = 'C:/Program Files/Deriv MT5 Terminal/terminal64.exe'
uname = int(username) # Username must be an int
pword = str(password) # Password must be a string
trading_server = str(server2) # Server must be a string
filepath = str(path) # Filepath must be a string


def tststuff(tstdf,setupp):
    # get the chart, MAKE IT DESCENDING ORDER OF DATE?? get last price isolated??
   
    # search chart for indicator 1
    if setupp['ind1v'] != None:
    #     print('found ind1')
        exec(getIndicFxn(tstdf,setupp,1))
    # search for indicator 2
    if setupp['ind2v'] != None:
    #     print('found ind2')
        exec(getIndicFxn(tstdf,setupp,2))
    # search for candlestick
    exec(getcandle(tstdf,setupp))
    # search if in range
    tstdf['inRange'] = tstdf.apply(lambda x: inRange(x,setupp), axis=1)
    # search records for if they fit the required params
    return tstdf

# def maketest(df,setupp):
#     df['WEIN?'] = df.apply(lambda x: are_we_in(x,setupp), axis=1)
#     return df[df['WEIN?'] == True]



app = Flask(__name__)
scheduler = APScheduler()
db = SQLAlchemy(app)

mynumber = '+263712989466'

class Setting(db.Model):

    __tablename__ = 'settiings'
    
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    asset = db.Column(db.Text, nullable=False)

    price = db.Column(db.Float, nullable=False)
    prange = db.Column(db.Float, nullable=False)

    ind1 = db.Column(db.Text, nullable=True)
    ind2 = db.Column(db.Text, nullable=True)
    
    ind1v = db.Column(db.Float, nullable=True)
    ind2v = db.Column(db.Float, nullable=True)
    
    ind1c = db.Column(db.Text, nullable=True)
    ind2c = db.Column(db.Text, nullable=True)
    cdlval = db.Column(db.Float, nullable=False)
    

    indvars1 = db.Column(db.JSON, nullable=True)
    indvars2 = db.Column(db.JSON, nullable=True)

    candle = db.Column(db.Text, nullable=True)
    timeframe = db.Column(db.Text, nullable=True)
    
    dateLog = db.Column(db.Date, nullable=False,default=datetime.now())
    dateExp = db.Column(db.Date, nullable=False)
    
    def __init__(self, asset,price,prange,ind1,ind2,indvars1,indvars2,
                 candle,timeframe,dateExp,ind1v,ind2v,ind1c,ind2c,cdlval):
        self.asset = asset
        self.price = price
        self.prange = prange
        self.ind1 = ind1
        self.ind2 = ind2
        self.ind1v = ind1v
        self.ind2v = ind2v
        self.ind1c = ind1c
        self.ind2c = ind2c
        self.indvars1 = indvars1
        self.indvars2 = indvars2
        self.candle = candle
        self.timeframe = timeframe
        self.dateLog = datetime.now()
        self.dateExp = dateExp
        self.cdlval = cdlval        


        
        
    def json(self):
        return {
            'asset':self.asset,
            'ind1v': self.ind1v,
            'ind2v': self.ind2v,          
            'ind1c': self.ind1c,
            'ind2c': self.ind2c,   
            'price':self.price,
            'range': self.prange,
            'cdlval': self.cdlval,
            'indicator1': self.ind1,
            'indicator2': self.ind2,
            'params1':self.indvars1,
            'params2':self.indvars2,
            'candlepattern': self.candle,
            'TimeFrame':self.timeframe,
            'Expiry': self.dateExp.strftime("%d/%m %Y %H:%M"),
            'SetDate': self.dateLog.strftime("%d/%m %Y %H:%M")
        } 
    
setupp = Setting.query.filter_by(id=1).first()

def job2():
    print('summmmmmmmm')

def job1():

    resultfr = make_check(setupp)
#  if resultfr is not empty take the last value and send it as a text
    if resultfr.empty:
        return 'no result'
    res = send_txt(mynumber,resultfr)

    if res == True:
        return "sent message"
    else:
        return "no message sent"

if __name__ =='__main__':
    if(start_mt5(uname,pword,trading_server,filepath)):
        scheduler.add_job(id='jpb1',
            func=job1,trigger=apscheduler.triggers.cron.CronTrigger.from_crontab('* * * * *'))
        # scheduler.add_job(id='jpb1',func=job1,trigger='interval',seconds=10)
        scheduler.add_job(id='jpb2',
            func=job2,trigger=apscheduler.triggers.cron.CronTrigger.from_crontab('30 * * * *'))
        
        scheduler.start()
        app.run(host='0.0.0.0', port=12345)
    else:
        print('no')
        