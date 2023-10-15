import telegram_send
import json

def send_txt(resrow,setuppp):
    a2 = resrow
    # a2['date'] = a2['date'].strftime("%d/%m %Y %H:%M:%S")
    # print(a2)

    result = json.dumps(a2)
    asst = "FROM THE INTERNET WORKAROUND: " + str(setuppp['id'])
    asst2 = "Indicator INTERNEt for asset: " + setuppp['asset']
    # tyme = "Found at time: " + str(a2['date'])
    openn = "Open Price at: " + str(a2['open'])
    tickvol = "Tick Volume of: " + str(a2['tick_volume'])
    textt = asst + '\n' + asst2 +  '\n' + openn + '\n' + tickvol

    res = telegram_send.send(messages=[textt],conf='./tg.config')
    # print(res)    
    return True

ress = {'id':1,'asset':'word11'}

res2 = {'open':123123,'tick_volume':394023}

send_txt(res2,ress)