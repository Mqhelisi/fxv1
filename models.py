import json
from datetime import datetime
import json
from app import db

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
    
    indvars = db.Column(db.JSON, nullable=True)

    candle = db.Column(db.Text, nullable=True)
    timeframe = db.Column(db.Text, nullable=True)
    
    dateLog = db.Column(db.Date, nullable=False,default=datetime.now())
    dateExp = db.Column(db.Date, nullable=False)
    
    def __init__(self, asset,price,prange,ind1,ind2,indvars,
                 candle,timeframe,dateExp,ind1v,ind2v):
        self.asset = asset
        self.price = price
        self.prange = prange
        self.ind1 = ind1
        self.ind2 = ind2
        self.ind1v = ind1v
        self.ind2v = ind2v
        self.indvars = indvars
        self.candle = candle
        self.timeframe = timeframe
        self.dateLog = datetime.now()
        self.dateExp = dateExp
        
        
        
    def json(self):
        return {
            'asset':self.asset,
            'ind1v': self.ind1v,
            'ind2v': self.ind2v,            
            'price':self.price,
            'range': self.prange,
            'indicator1': self.ind1,
            'indicator2': self.ind2,
            'params':self.indvars,
            'candlepattern': self.candle,
            'TimeFrame':self.timeframe,
            'Expiry': self.dateExp.strftime("%d/%m %Y %H:%M"),
            'SetDate': self.dateLog.strftime("%d/%m %Y %H:%M")
        } 
    