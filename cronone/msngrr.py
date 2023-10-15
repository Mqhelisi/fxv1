import pandas as pd
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json
import talib
from datetime import datetime, timedelta
from msgstory import make_check,anotherChart,send_txt, test_meta_api_synchronization
import asyncio
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Date, Text, Boolean, Float,JSON,create_engine
from sqlalchemy.orm import sessionmaker

whole_start = datetime.now().timestamp()
loop = asyncio.get_event_loop()
# engine = create_engine("postgresql+psycopg2://postgres:Mqhe23@localhost/fx")
engine = create_engine("postgresql+psycopg2://krtl_fx_stp_user:9XWzSV0Qr8kBZa371ZTPoH5Y0AXkeXwf@dpg-ckkpju3j89us73a0a5t0-a.oregon-postgres.render.com/krtl_fx_stp")

Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class Setting(Base):

    __tablename__ = 'settiings'
    
    id = Column(Integer, nullable=False, primary_key=True)
    asset = Column(Text, nullable=False)

    price = Column(Float, nullable=False)
    prange = Column(Float, nullable=False)

    ind1 = Column(Text, nullable=True)
    ind2 = Column(Text, nullable=True)
    
    ind1v = Column(Float, nullable=True)
    ind2v = Column(Float, nullable=True)
    
    ind1c = Column(Text, nullable=True)
    ind2c = Column(Text, nullable=True)
    cdlval = Column(Float, nullable=False)
    

    indvars1 = Column(JSON, nullable=True)
    indvars2 = Column(JSON, nullable=True)

    candle = Column(Text, nullable=True)
    timeframe = Column(Text, nullable=True)
    active = Column(Boolean, nullable=False)
    contacts = Column(Text, nullable=False)
    
    dateLog = Column(Date, nullable=False,default=datetime.now())
    dateExp = Column(Date, nullable=False)
    
    def __init__(self, asset,price,prange,ind1,ind2,indvars1,indvars2,
                 candle,timeframe,dateExp,ind1v,ind2v,ind1c,ind2c,cdlval,active,contacts):
        self.asset = asset
        self.price = pr
        ice
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
            'id':self.id,
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

# async def mke_inspxn(setup,acc):
#     print('doing test for setup with asset: ' + setup['asset'] + ' and timeframe ' + setup['TimeFrame']  )
#     resultfr = loop2.run_until_complete(make_check(setup,acc))
# #  if resultfr is not empty take the last value and send it as a text
#     if resultfr.empty:
#         return 'no result'
#     res = send_txt(resultfr, setuppp=setup)

#     if res == True:
#         return "sent message"
#     else:
#         return "no message sent"
    
print('doing job 1')

stp = session.query(Setting).filter_by(active=True)
setups = [st.json() for st in stp]
print('total units' + str(len(setups)))


ac = loop.run_until_complete(test_meta_api_synchronization())


for each in setups:
    print('checking itm of val')
    print(each)
    print('doing test for setup with asset: ' + each['asset'] + ' and timeframe ' + each['TimeFrame']  )

    chart2 = loop.run_until_complete(anotherChart(each['asset'],ac))

    resfrm = make_check(chart2,each)
    if resfrm.empty:
        print( 'no result')
    else:
        res = send_txt(resfrm, setuppp=each)

        if res == True:
            print( "sent message")
        else:
            print( "no message sent")
    
print('done job 1')
print(f'Took {(datetime.now().timestamp() - whole_start)}s')


