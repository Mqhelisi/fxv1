from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import json

def breakbreak(d):
    lastkey = 1
    intarr =  list()
    finarr = list()
    for index in range(len(d)):
        for key in d[index]:

                
            if key==lastkey:

                intarr.append(d[index][key])
       
            else:

                finarr.append({lastkey:json.dumps(intarr)})
                intarr = list()
                intarr.append(d[index][key])
                
            if index == len(d) - 1:
                if key==lastkey:
                    finarr.append({key:json.dumps(intarr)})
                else:
                    intarr = list()
                    intarr.append(d[index][key])
                    finarr.append({key:json.dumps(intarr)})

                
                break
            
            lastkey=key
    return finarr

def breakdown(a,b):
    d=list()
    e=0
    f=1
    for g in a:
        for index in range(g):
            # print(b[e])
            d.append({f:[b[e],'=']})
            e+=1
        f+=1
    # print(d)
    return breakbreak(d)
    
def make_elems(xx):
    z = list()
    for y in xx:
        z.append({'label':y,'value':y})

    return z

def topModel(idd,options,name=None,hdn=False):


    topDrop = dcc.Dropdown(
    id=idd,
            options = options,
            optionHeight=50,                    #height/space between dropdown options
            value='None',                    #dropdown value selected automatically when page loads
            disabled=hdn,                     #disable dropdown value selection
            multi=False,                        #allow multiple dropdown values to be selected
            searchable=True,                    #allow user-searching of dropdown values
            search_value='',                    #remembers the value searched in dropdown
            placeholder='Please select...',     #gray, default text shown when no option is selected
            clearable=True,                     #allow user to removes the selected value
            style={'width':"100%"}             #use dictionary to define CSS styles of your dropdown
            # className='select_box',           #activate separate CSS document in assets folder
            # persistence=True,                 #remembers dropdown value. Used with persistence_type
            # persistence_type='memory'         #remembers dropdown value selected until...
)       
    if name is not None:
        return dcc.Dropdown(
    id=idd,
            options = options,
            optionHeight=50,                    #height/space between dropdown options
            value=name,                    #dropdown value selected automatically when page loads
            disabled=hdn,                     #disable dropdown value selection
            multi=False,                        #allow multiple dropdown values to be selected
            searchable=True,                    #allow user-searching of dropdown values
            search_value='',                    #remembers the value searched in dropdown
            placeholder='Please select...',     #gray, default text shown when no option is selected
            clearable=True,                     #allow user to removes the selected value
            style={'width':"100%"}             #use dictionary to define CSS styles of your dropdown
            # className='select_box',           #activate separate CSS document in assets folder
            # persistence=True,                 #remembers dropdown value. Used with persistence_type
            # persistence_type='memory'         #remembers dropdown value selected until...
)
    return dbc.Row(style={'width':'100%'},children=topDrop), 

def header1(name):
    bottomLine = html.H4(style={'color':'black','margin-top':'2px'},children=name)
    return dbc.Row(dbc.Col(bottomLine))

def make_one_pr(indi,values,indicfrm):
#     value = [5, 3, 3, None]
    records2 = indicfrm[indicfrm['value'] == indi].to_dict('records')
    g = dict()
    z=0
    for i in values:
        # print(indi)
        if i != None:
            varval = 'default'+str(z+1)
            varname = varval + 'Name'
            g[records2[0][varname]] = i
            z+=1
            # print(varname)

    return g

def make_two_pr(params,whcwch,indics,indicfrm):
    cnt=btch=0
    param1 = dict()
    param2 = dict()
    for a in whcwch:
        indic8 = indicfrm[indicfrm['value'] == indics[btch]].to_dict('records')[0]        
        z=0

        for i in range(a):

            varval = 'default'+str(z+1)
            varname = varval + 'Name'
            z+=1

            if btch==0:
                param1[indic8[varname]] = params[cnt]
            else:
                param2[indic8[varname]] = params[cnt]

            cnt+=1
        btch+=1
    return param1, param2

def make_params(amt,pname):
    z=list()
    options = ['>','<','=']

    if amt == None:
        return None
    for x in range(int(amt)):
        idn = {"type": "variable-val", "index": x}
        idd = {"type": "comparison-dropdown", "index": x}
        varval = 'default'+str(x+1)
        varname = varval + 'Name'
        # print(varname)
        parname = pname[varname]
        parval = pname[varval]

        z.append(
            dbc.Row(
            [
            dbc.Col(html.H6(str(parname)+ ':'), width={'size':3,'offset':1}, style = {'text':'black'}),
        dbc.Col(dbc.Input(id=idn, value=parval, type="text"), width=3),
        dbc.Col(topModel(idd,options,name='='), width=3)

                         ]
                         ))

    return z
# ////////////////////////////COMPONENTS//////
def getvars(dframe,var):
    if var == 'None':
        # print(var)
        return None
    dfm = dframe.loc[dframe['value'] == var]['variables'].to_numpy()[0]
    return dfm
