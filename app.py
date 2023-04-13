from dash import Dash, html, dcc, Patch, ALL, no_update, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd 
from things import topModel, header1, make_two_pr, make_one_pr, make_params, getvars, breakdown
from mtlogic import start_mt5, getChart, resampling
from datetime import datetime
from styles import SIDEBAR_STYLE, CENTER_STYLE
import os
from flask_sqlalchemy import SQLAlchemy
import talib

app = Dash(__name__, suppress_callback_exceptions=True)
app.server.config['SECRET_KEY'] = 'mysecret'
app.server.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:Mqhe23@localhost/fx"
app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app.server)


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

param_ids_1 = list()
param_ids_2 = list()
# /////////////////GATHER DATA ////////////////////
rdf = pd.read_excel('testgold.xlsx')
rdf = rdf.drop('Unnamed: 0', axis=1)
rdf = rdf.set_index('date')
# print(rdf)

rdf = rdf.resample('15Min').agg(
{
    'open':'first',
    'high':'max', 
    'low':'min',
    'close':'last',
    
}
)

# pricenw = rdf.iloc[-1].to_dict()['open']
username = '30585595'
password = 'TestBotApp1'
server2 = 'Deriv-Demo'
path = 'C:/Program Files/Deriv MT5 Terminal/terminal64.exe'

isNet = start_mt5(username, password, server2,path)

candelist = pd.read_excel('CANDLE PATTERNS LIST.xlsx').to_dict('records')
assetList = pd.read_excel('Assets List.xlsx').to_dict('records')

indlist1v = pd.read_excel('allind.xlsx')

indlist1 = indlist1v.drop(['variables','default1Name','default1','default2Name','default2','default3','default3Name','output'], axis=1).to_dict('records')
# indlist2 = indlist2v.drop(['variables','default1Name','default1','default2Name','default2','default3','default3Name','output'], axis=1).to_dict('records')

# /////////////////LEFT SIDE COMPONENTS//////////////////


timeframes = ['5Min','15Min','30Min','1H','2H','4H','12H']

leftBox = html.Div(children=[
    # header1('asset'),
    dbc.Row(header1('Asset:')),
dbc.Row(topModel('asst',assetList)),
html.Hr(),
    dbc.Row(header1('First Indicator'),           
            ),

dbc.Row(topModel('idnt2',indlist1)),  
    dbc.Row(id='param1'),
html.Hr(),

    dbc.Row(header1('Second Indicator')),
dbc.Row(topModel('idnt3',indlist1,hdn=True)),
    dbc.Row(id='param2'),

html.Hr(),
    dbc.Row(header1('Candlestick Patterns')),
        
dbc.Row(topModel('pttrn',candelist)),  
html.Hr(),
  
        dbc.Row(
        dbc.Button('show on chart: ', id='show1')
       ),

       dbc.Row(
    dbc.Col(html.H6(id='show2'))
       )
]
)














# ///////////////////////GRAPH///////////
candles = go.Figure(

    data = [
    go.Candlestick(
    x = rdf.index,
    open = rdf.open,
    high = rdf.high,
    low = rdf.low,
    close = rdf.close
    )
    ]
)

# candles.add_vline(x=datetime(2023,1,3,20,30),line_width=3)
csticks = dcc.Graph(id='candles',figure = candles, style={'height':'80vh', 'width' : '100%'})

graphs = html.Div([
    dcc.Loading(
    csticks
    
    ), 
    # dcc.Interval(id='interval',
    #                     interval=4000)
])

footerData = [
    
        dbc.ModalFooter(
[    dbc.Button('update',id='closeM',className='ms-auto',n_clicks=0),
            dbc.Col(html.H5(id = 'params1', hidden = True),width = 0),
        dbc.Col(html.H5(id = 'params2', hidden = True),width = 0),
        dbc.Col(html.H5(id = 'pryz', hidden = True),width = 0),

        dbc.Col(html.H5(id = 'notif'),width = 7),
        
        ]

    )
]

# /////////////////////RIGHT SIDE COMPONENTS......

rightRow = html.Div(
    [
    dbc.Row(
    dbc.Col(header1('Time Frame:')
            ,width = {"size": 4, "offset": 4})
        ),
    dbc.Row(
    dbc.Col(topModel('tmfrm',timeframes,name='5Min')
            ,width = {"size": 4, "offset": 4})
        ),
        dbc.Row(
            [
    dbc.Col(html.Div(graphs, 
                     style = {'margin':'auto', 'width' : '90%' 
                                   ,'border':'3px solid green'
                                   }), width = 12),
            ]
            , justify="center", align="center"
        )
    ]
)

# fig.add_trace(px.scatter(df,y='indval',x='depval'))
# //////////////////////MODALL
modal = html.Div([
    dbc.Modal(
  children = footerData,
        id='modal',
    centered = True,
    is_open = False
    )
]
)

cdlist = [{'value': 100, 'label': 'Bullish'}, {'value': -100, 'label': 'Bearish'}]

# ////////////////////EVERYTHING TOGETHER
wholeContainer = html.Div(
    [
    dbc.Row([
    dbc.Col(
    leftBox, width=2,style = {
        # 'background':'gray',
        'border-radius':'5%'
    ,'height':'100vw'}
    ),
dbc.Col( 
    html.Div(
    style = CENTER_STYLE,
                children = [
    html.Div(
    rightRow, 
            style = {'align-items':'center'}
                )
    ]
        ), width = 10
    )], justify="end"
    ),
    # html.Div(id='modal1')
    modal,
], style=SIDEBAR_STYLE,)
candlecomps = list()
candlecomps.append({'label':'Bullish','value':100})
candlecomps.append({'label':'Bearish','value':-100})


# /////////////////////////CALLLBACKS

@app.callback(
            Output('idnt3','disabled'),
    Input('idnt2','value'),
)

def update(inits):
    if inits != 'None':
        return False
    return True

@app.callback(
    Output('modal','is_open'), 
    Output('modal','children'),
Output('params1','children'), 
Output('params2','children'), 
    
    Input('show1','n_clicks'),
    State('tmfrm','value'),
    State('asst','value'),
    State('idnt2','value'),

    State('idnt3','value'),
    State('pttrn','value'),
    State('modal','is_open'),
    State('modal','children'),
    State('pryz','children'),
        prevent_initial_call=True
)

def upd_fig(n1,tfrm,idn1,indic1,indic2,idn4,is_open,mbod,pricenw):

    comparison = topModel('p_range',[0.1,0.25,0.5,0.75,1,1.25,1.5],name='1')
    num_params1 = getvars(indlist1v,indic1)
    num_params2 = getvars(indlist1v,indic2)
    indi1 = indlist1v[indlist1v['value'] == indic1].to_dict('records')[0]
    indi2 = indlist1v[indlist1v['value'] == indic2].to_dict('records')[0]
    mbod = footerData


    if indic1 == "None" and indic2 == "None":
        modbod = [  
    dbc.ModalHeader(dbc.ModalTitle("Notifications"), close_button=True),
    dbc.ModalBody([
    dbc.Row([dbc.Col(html.H6('Asset')),dbc.Col(html.H4(idn1))]),
html.Hr(),

    dbc.Row([dbc.Col(html.H6('Price Range'), width=3),
             dbc.Col(dcc.Input(id='price', 
                            placeholder="Price",value=pricenw, type="text"),
                             width={"size": 5, "offset": 1}),
                            dbc.Col(comparison, width={"size": 2, "offset": 1})]),
html.Hr(),

    dbc.Row([dbc.Col(html.H6('Indicator 1')),dbc.Col(html.H5(indic1, style={'text':'brown'})),
             dbc.Col(dbc.Input(id='ind1val', type="text"), width=2),
        dbc.Col(topModel('ind1comp',['>','<','='],name='='), width=2)
             
             ,],style={'display':'none'}),
    dbc.Row(
            [
            
                    dbc.Col(dbc.Input(id={"type": "variable-val", "index": 0}, type="text"), width=3),
        dbc.Col(dbc.Input(id={"type": "comparison-dropdown", "index": 0}), width=3)


            ]
            
            
            
            ,style={'display':'none'}),
html.Hr(),

    dbc.Row([dbc.Col(html.H6('Indicator 2')),dbc.Col(html.H5(indic2)),
             dbc.Col(dbc.Input(id='ind2val', type="text"), width=2),
        dbc.Col(topModel('ind2comp',['>','<','='],name='='), width=3)

             ],style={'display':'none'}),
    dbc.Row(
            [
            

        dbc.Col(dbc.Input(id={"type": "variable-val", "index": 0}, type="text"), width=3),
        dbc.Col(dbc.Input(id={"type": "comparison-dropdown", "index": 0}), width=3)


            ]
            
            
            ,style={'display':'none'}),
html.Hr(),

    dbc.Row(
        [dbc.Col(html.H6('Candle Pattern')),dbc.Col(html.H5(idn4))
        ,
    dbc.Col(
        topModel(
        'cdcomp',cdlist,name=100), width=3
        )]
        )
    ,
html.Hr(),
    dbc.Row([dbc.Col(html.H6('Time Frame:')),
    dbc.Col(topModel('modal_price',timeframes,name=tfrm))]),
            ])]

    elif indic1 == "None":

        param2 = make_params(num_params2, indi1)


        patch2 = Patch()

        patch2.append(param2)
    

        modbod = [  
    dbc.ModalHeader(dbc.ModalTitle("Notifications"), close_button=True),
    dbc.ModalBody([
    dbc.Row([dbc.Col(html.H6('Asset')),dbc.Col(html.H4(idn1))]),
html.Hr(),

    dbc.Row([dbc.Col(html.H6('Price Range'), width=3),
             dbc.Col(dcc.Input(id='price', 
                            placeholder="Price",value=pricenw, type="text"),
                             width={"size": 5, "offset": 1}),
                            dbc.Col(comparison, width={"size": 2, "offset": 1})]),
html.Hr(),

    dbc.Row([dbc.Col(html.H6('Indicator 1')),dbc.Col(html.H5(indic1, style={'text':'brown'})),
             dbc.Col(dbc.Input(id='ind1val', type="text"), width=2),
        dbc.Col(topModel('ind1comp',['>','<','='],name='='), width=2)
             
             ,],style={'display':'none'}),
    dbc.Row(
            [
            
        dbc.Col(dbc.Input(id={"type": "variable-val", "index": 0}, type="text"), width=3),
        dbc.Col(dbc.Input(id={"type": "comparison-dropdown", "index": 0}), width=3)


            ]
            
            ,style={'display':'none'}),
html.Hr(),

    dbc.Row([dbc.Col(html.H6('Indicator 2')),dbc.Col(html.H5(indic2)),
             dbc.Col(dbc.Input(id='ind2val', type="text"), width=2),
        dbc.Col(topModel('ind2comp',['>','<','='],name='='), width=3)

             ],style={'display':'none'}),
    dbc.Row(param2,style={'display':'none'}),
html.Hr(),

    dbc.Row(
        [dbc.Col(html.H6('Candle Pattern')),dbc.Col(html.H5(idn4))
        ,
    dbc.Col(
        topModel(
        'cdcomp',cdlist,name=100), width=3
        )]
        )
    ,
html.Hr(),
    dbc.Row([dbc.Col(html.H6('Time Frame:')),
    dbc.Col(topModel('modal_price',timeframes,name=tfrm))]),
            ])]
        

    elif indic2 == "None":
        param1 = make_params(num_params1, indi1)


        patch1 = Patch()

        patch1.append(param1)

        modbod = [  
    dbc.ModalHeader(dbc.ModalTitle("Notifications"), close_button=True),
    dbc.ModalBody([
    dbc.Row([dbc.Col(html.H6('Asset')),dbc.Col(html.H4(idn1))]),
html.Hr(),

    dbc.Row([dbc.Col(html.H6('Price Range'), width=3),
             dbc.Col(dcc.Input(id='price', 
                            placeholder="Price",value=pricenw, type="text"),
                             width={"size": 5, "offset": 1}),
                            dbc.Col(comparison, width={"size": 2, "offset": 1})]),
html.Hr(),

    dbc.Row([dbc.Col(html.H6('Indicator 1')),dbc.Col(html.H5(indic1, style={'text':'brown'})),
             dbc.Col(dbc.Input(id='ind1val', type="text"), width=2),
        dbc.Col(topModel('ind1comp',['>','<','='],name='='), width=2)
             
             ,]),
    dbc.Row(param1),
html.Hr(),

    dbc.Row([
            
            dbc.Col(html.H6('Indicator 2')),dbc.Col(html.H5(indic2)),
             dbc.Col(dbc.Input(id='ind2val', type="text"), width=2),
        dbc.Col(topModel('ind2comp',['>','<','='],name='='), width=3)

             ],style={'display':'none'}),
    dbc.Row(
            
            [
            
        dbc.Col(dbc.Input(id={"type": "variable-val", "index": 0}, type="text"), width=3),
        dbc.Col(dbc.Input(id={"type": "comparison-dropdown", "index": 0}), width=3)


            ]
            
            ,style={'display':'none'}

    ),
html.Hr(),

    dbc.Row(
        [dbc.Col(html.H6('Candle Pattern')),dbc.Col(html.H5(idn4))
        ,
    dbc.Col(
        topModel(
        'cdcomp',cdlist,name=100), width=3
        )]
        )
    ,
html.Hr(),
    dbc.Row([dbc.Col(html.H6('Time Frame:')),
    dbc.Col(topModel('modal_price',timeframes,name=tfrm))]),
            ])]
    else:

        param1 = make_params(num_params1, indi1)
        param2 = make_params(num_params2, indi2)

        mbod = footerData

        patch1 = patch2 = Patch()

        patch1.append(param1)
        patch2.append(param2)

        modbod = [  
    dbc.ModalHeader(dbc.ModalTitle("Notifications"), close_button=True),
    dbc.ModalBody([
    dbc.Row([dbc.Col(html.H6('Asset')),dbc.Col(html.H4(idn1))]),
html.Hr(),

    dbc.Row([dbc.Col(html.H6('Price Range'), width=3),
             dbc.Col(dcc.Input(id='price', 
                            placeholder="Price",value=pricenw, type="text"),
                             width={"size": 5, "offset": 1}),
                            dbc.Col(comparison, width={"size": 2, "offset": 1})]),
html.Hr(),

    dbc.Row([dbc.Col(html.H6('Indicator 1')),dbc.Col(html.H5(indic1, style={'text':'brown'})),
             dbc.Col(dbc.Input(id='ind1val', type="text"), width=2),
        dbc.Col(topModel('ind1comp',['>','<','='],name='='), width=2)
             
             ,]),
    dbc.Row(param1),
html.Hr(),

    dbc.Row([dbc.Col(html.H6('Indicator 2')),dbc.Col(html.H5(indic2)),
             dbc.Col(dbc.Input(id='ind2val', type="text"), width=2),
        dbc.Col(topModel('ind2comp',['>','<','='],name='='), width=3)

             ]),
    dbc.Row(param2),
html.Hr(),

    dbc.Row(
        [dbc.Col(html.H6('Candle Pattern')),dbc.Col(html.H5(idn4))
        ,
    dbc.Col(
        topModel(
        'cdcomp',cdlist,name=100), width=3
        )]
        )
    ,
html.Hr(),
    dbc.Row([dbc.Col(html.H6('Time Frame:')),
    dbc.Col(topModel('modal_price',timeframes,name=tfrm))]),
            ])]
    
    modbod.append(mbod[0])
    if n1:
        return not is_open,modbod, num_params1, num_params2
    return is_open, modbod, num_params1, num_params2
    
@app.callback(
    Output('closeM','children'),
    Output("notif", "children"), 
    Input('closeM','n_clicks'),
    State('tmfrm','value'),
    State('asst','value'),
    State('idnt2','value'),
    State('idnt3','value'),
    State('pttrn','value'),
    State('modal','is_open'),
    State({"type": "variable-val", "index": ALL}, "value"),
    State({"type": "comparison-dropdown", "index": ALL}, "value"),
    State('params1','children'), 
    State('params2','children'),
    State('ind1val','value'),
    State('ind2val','value'),
    State('ind1comp','value'),
    State('ind2comp','value'),
    State('price','value'),
    State('cdcomp','value'),
    State('p_range','value'),
        prevent_initial_call=True)

def upd_fig2(n1,tfrm,idn1,indic1,indic2,idn4,is_open,v1,v2,p1,p2,i1v,i2v,i1c,i2c,prx,cmp,prnge):
    # print(v1,v2)
    print(p1,p2)
    if p2 == None:
        if p1 == None:
            setup = Setting(idn1,prx,prnge,
                            None,None,None,None,
                            idn4,tfrm,datetime(2023,5,4),i1v,i2v,i1c,i2c,cmp,True,'+263712989466')
            
            db.session.add(setup)
            db.session.commit()
            return 'done', 'notification updated..no indics'
        else:

            params = make_one_pr(indic1,v1,indlist1v)
        
            setup = Setting(idn1,prx,prnge,
                            indic1,None,params,None,
                            idn4,tfrm,datetime(2023,5,4),i1v,i2v,i1c,i2c,cmp,True,'+263712989466')
              
            db.session.add(setup)
            db.session.commit()
            return 'done', 'notif updated, one indic'
    # print(p1)
    # print(v1)

    params2 = [5, 3, 3, 14]
    whcwch2 = [1,3]
    indics2 = [indic1,indic2]

    pr1,pr2 = make_two_pr(v1,[p1,p2],indics2,indlist1v)
    # params = breakdown([p1,p2],v1)
    # print(params)
    # print(tfrm,idn1,indic1,indic2,idn4,is_open)
    setup = Setting(idn1,prx,prnge,indic1,indic2,pr1,pr2,idn4,
                    tfrm,datetime(2023,5,4),i1v,i2v,i1c,i2c,cmp,True,'+263712989466')
    db.session.add(setup)
    db.session.commit()
    return 'done', 'notification updated'
# //////////////////////////////LAYOUTTT

@app.callback(
    Output("candles", "figure"),
    Output('pryz','children'),

    Input("asst", "value"),
    Input("tmfrm", "value"),

        prevent_initial_call=True
)
def scaleYaxis(rng,tfmr):
    # if rng and "xaxis.range" in rng.keys():
    #     try:
    #         d = rdf.loc[
    #             rng["xaxis.range"][0] : rng["xaxis.range"][1],
    #             ["High", "Low", "Open", "Close"],
    #         ]
    #         if len(d) > 0:
    #             csticks["layout"]["yaxis"]["range"] = [d.min().min(), d.max().max()]
    #     except KeyError:
    #         pass
    #     finally:
    #         csticks["layout"]["xaxis"]["range"] = rng["xaxis.range"]
    redo_frame = rdf.copy()
    ctx = callback_context
    # if ctx.triggered[0]['prop_id'] == 'dp1.start_date' or ctx.triggered[0]['prop_id'] == 'dp1.end_date':

    if isNet == True:

        redo_frame = getChart(tfmr,rng)
        candles = go.Figure(

        data = [
        go.Candlestick(
        x = redo_frame.index,
        open = redo_frame.open,
        high = redo_frame.high,
        low = redo_frame.low,
        close = redo_frame.close
        )
        ]
    )
        zryp = redo_frame.iloc[-1].to_dict()['open']
        return candles, zryp
        
    else:
        candles = go.Figure(

        data = [
        go.Candlestick(
        x = redo_frame.index,
        open = redo_frame.open,
        high = redo_frame.high,
        low = redo_frame.low,
        close = redo_frame.close
        )
        ]
    )
        return candles, zryp  

app.layout = wholeContainer

if __name__ == '__main__':
    # app.run_server(debug=True,port=8056)
    app.run_server(host='0.0.0.0', port=1234)
