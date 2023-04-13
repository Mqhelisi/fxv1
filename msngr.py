import json
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pandas as pd
import os
import talib
from twilio.rest import Client
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
import apscheduler
import pandas as pd

from msgthings import start_mt5,make_check,send_txt
account_sid = 'AC4cc6677cf885aab5e8d744f456178499'
auth_token = 'fb4f18abfe1ef68d2c6981c5709add03'
client = Client(account_sid, auth_token)
# Function to start Meta Trader 5 (MT5)
username = '30585595'
password = 'TestBotApp1'
server2 = 'Deriv-Demo'
path = 'C:/Program Files/Deriv MT5 Terminal/terminal64.exe'
uname = int(username) # Username must be an int
pword = str(password) # Password must be a string
trading_server = str(server2) # Server must be a string
filepath = str(path) # Filepath must be a string

# FLASK INITS
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:Mqhe23@localhost/fx"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
scheduler = APScheduler()


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
    active = db.Column(db.Boolean, nullable=False)
    contacts = db.Column(db.Text, nullable=False)
    
    dateLog = db.Column(db.Date, nullable=False,default=datetime.now())
    dateExp = db.Column(db.Date, nullable=False)
    
    def __init__(self, asset,price,prange,ind1,ind2,indvars1,indvars2,
                 candle,timeframe,dateExp,ind1v,ind2v,ind1c,ind2c,cdlval,active,contacts):
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
        self.active = active  
        self.contacts = contacts        
        


        
        
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
            'active': self.active,
            'contacts':self.contacts,
            'Expiry': self.dateExp.strftime("%d/%m %Y %H:%M"),
            'SetDate': self.dateLog.strftime("%d/%m %Y %H:%M")
        } 
    




def mke_inspxn(setup):
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


def job1():
    print('doing job 1')
    with app.app_context():

        stp = Setting.query.filter_by(active=True)
        setups = [st.json() for st in stp]
    print('total units' + str(len(setups)))

    for each in setups:
        print('checking itm of val')
        print(each)
        mke_inspxn(each)
    print('done job 1')


if __name__ =='__main__':

    if(start_mt5(uname,pword,trading_server,filepath)):
        scheduler.add_job(id='jpb1',
    func=job1,
    trigger=apscheduler.triggers.cron.CronTrigger.from_crontab('* * * * *')
    )
        # scheduler.add_job(id='jpb1',func=job1,trigger='interval',seconds=10)

        scheduler.start()
        app.run(host='0.0.0.0', port=12345)
    else:
        print('no')