# This code is based on the following example:
# https://discordpy.readthedocs.io/en/stable/quickstart.html#a-minimal-bot

# Token: 
"""
import discord
import os

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

try:
    client.run(os.getenv("TOKEN"))
except discord.HTTPException as e:
    if e.status == 429:
        print("The Discord servers denied the connection for making too many requests")
        print("Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests")
    else:
        raise e
"""
import discord    #導入 Discord.py
from discord.ext import commands #導入 commands 雖然目前不會用到
import os    #導入os模組
import asyncio
import pandas as pd
from datetime import datetime
from discord import app_commands
from discord.app_commands import Choice
import time
import random
import string # 有與文字相關的語法
import requests

# client是跟discord連接，intents是要求機器人的權限
#intents = discord.Intents.default()
#intents.message_content = True
#client = discord.Client(intents = intents)

intents = discord.Intents.all()
#bot = commands.Bot(command_prefix='你想要的指令前綴', intents = intents) 
bot = commands.Bot(command_prefix='/', intents = intents) 
intents.members = True
#透過bot與dicord連結，並設定command的前綴(但還不會用到)

def youbike_search(form, keyword): #建立函式
  pd.options.mode.chained_assignment = None #避免顯示錯誤訊息
  original = pd.read_json('https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json') #引入資料
  rename = original.rename(columns = {'sno':'站點代號', 'sna':'場站中文名稱','total':'場站總停車格','available_rent_bikes':'場站目前車輛數量','sarea':'場站區域',
  'mday':'資料更新時間','latitude':'緯度','longitude':'經度','ar':'地點','sareaen':'場站區域英文','snaen':'場站名稱英文','aren':'地址英文','available_return_bikes':'空位數量',
  'act':'全站禁用狀態'}) #更改欄位名稱

  '''
  2024/5/9更新
  此為舊版程式碼
  rename = original.rename(columns = {'sno':'站點代號', 'sna':'場站中文名稱','tot':'場站總停車格','sbi':'場站目前車輛數量','sarea':'場站區域',
  'mday':'資料更新時間','lat':'緯度','lng':'經度','ar':'地點','sareaen':'場站區域英文','snaen':'場站名稱英文','aren':'地址英文','bemp':'空位數量',
  'act':'全站禁用狀態'})
  '''

  #'srcUpdateTime':'YouBike2.0系統發布資料更新的時間','updateTime':'大數據平台經過處理後將資料存入DB的時間','infoTime':'各場站來源資料更新時間'
  #'infoDate':'各場站來源資料更新時間'
  df_bike = rename.drop(['場站區域英文','場站名稱英文','地址英文','infoDate','srcUpdateTime','updateTime','infoTime'], axis = 'columns') #將用不到的欄位刪除
  df_bike = df_bike.rename(columns = {'場站區域':'場站區域1','地點':'地點1'}) #複製欄位前先更名，準備將區域、地點欄位移到後面
  df_bike['場站區域'] = '0' 
  df_bike['地點'] = '0'
  for i in range(len(df_bike)):
    df_bike.loc[i, '場站中文名稱'] = df_bike.loc[i, '場站中文名稱'].replace('YouBike2.0_','') #將站點名稱簡化
    df_bike.loc[i, '場站區域'] = df_bike.loc[i, '場站區域1'] #複製欄位
    df_bike.loc[i, '地點'] = df_bike.loc[i, '地點1']
  bike = df_bike.drop(['站點代號','場站總停車格','資料更新時間','緯度','經度','全站禁用狀態','場站區域1','地點1'], axis = 'columns') #刪除欄位
  if form == '地點':
    name = keyword
    name1 = keyword
    if name == '建中' or name == '建國中學': #特殊功能：查詢建中附近YouBike站點資料
        CK = ['泉州寧波西街口', '郵政博物館', '植物園', '南海和平路口西南側', '捷運中正紀念堂站(2號出口)', '捷運中正紀念堂站(3號出口)', 
              '羅斯福寧波東街口', '立法院台北會館'] #以建中同學平時常前往的站點篩選資料
        filter = bike['場站中文名稱'].isin(CK)
    else:
        if '台' in name: #通同字轉換
            name = name.replace('台', '臺')
        elif '臺' in name:
            name = name.replace('臺', '台')
        filter = bike['地點'].str.contains(f'{name1}|{name}') #篩選符合關鍵字的站點
  elif form == '無車':
    filter = (bike['場站目前車輛數量'] == 0) #篩選目前無空車的站點
  else:
    name = keyword
    name1 = keyword
    if '台' in name:
      name = name.replace('台', '臺')
    elif '臺' in name:
      name = name.replace('臺', '台')
    filter = bike['場站中文名稱'].str.contains(f'{name1}|{name}')
  bike_result = bike[filter]
  return bike_result

def youbike_zero():
    pd.options.mode.chained_assignment = None
    original = pd.read_json('https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json')
    rename = original.rename(columns = {'sno':'站點代號', 'sna':'場站中文名稱','total':'場站總停車格','available_rent_bikes':'場站目前車輛數量','sarea':'場站區域',
    'mday':'資料更新時間','latitude':'緯度','longitude':'經度','ar':'地點','sareaen':'場站區域英文','snaen':'場站名稱英文','aren':'地址英文','available_return_bikes':'空位數量',
    'act':'全站禁用狀態'})
    """
    rename = original.rename(columns = {'sno':'站點代號', 'sna':'場站中文名稱','tot':'場站總停車格','sbi':'場站目前車輛數量','sarea':'場站區域',
    'mday':'資料更新時間','lat':'緯度','lng':'經度','ar':'地點','sareaen':'場站區域英文','snaen':'場站名稱英文','aren':'地址英文','bemp':'空位數量',
    'act':'全站禁用狀態'})
    """
    #'srcUpdateTime':'YouBike2.0系統發布資料更新的時間','updateTime':'大數據平台經過處理後將資料存入DB的時間','infoTime':'各場站來源資料更新時間'
    #'infoDate':'各場站來源資料更新時間'
    df_bike = rename.drop(['場站區域英文','場站名稱英文','地址英文','infoDate','srcUpdateTime','updateTime','infoTime'], axis = 'columns')
    df_bike = df_bike.rename(columns = {'場站區域':'場站區域1','地點':'地點1'})
    df_bike['場站區域'] = '0'
    df_bike['地點'] = '0'
    for i in range(len(df_bike)):
        df_bike.loc[i, '場站中文名稱'] = df_bike.loc[i, '場站中文名稱'].replace('YouBike2.0_','')
        df_bike.loc[i, '場站區域'] = df_bike.loc[i, '場站區域1']
        df_bike.loc[i, '地點'] = df_bike.loc[i, '地點1']
    bike = df_bike.drop(['站點代號','場站總停車格','資料更新時間','緯度','經度','全站禁用狀態','場站區域1','地點1'], axis = 'columns')
    filter = bike['場站目前車輛數量'] == 0
    bike_result = bike[filter]
    return bike_result

def railway_train_time(day, train_no):
    import pandas as pd
    #day = int(input('請輸入日期：(格式：yyyymmdd，例：20240101，目前可提供查詢資料之日期僅限於2020/11/6至查詢當日後90天)'))
    pd.options.mode.chained_assignment = None
    try:
        day = str(day)
        if day == '20240212':
            original = pd.read_json('https://drive.google.com/uc?id=18sRcFpVWl_RdMtONk2qS3ZBfT2ZuMCto&export=download')
        elif day == '20240726':
            original = pd.read_json('https://drive.google.com/uc?id=1Rwd8tcXPCdVERSTKUotS7OC23PecTB8k&export=download')
        elif day == '20220402':
            original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/2ecc206ae6c06b2118ebeb80473774e897310e49/json%20format/20220402.json')
        elif day == '20240819':
            original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/83d998c9d9facb041ec1cc5573d2f887f81567b7/json%20format/20240819.json')
        elif day == '20240824':
            original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/440b8069abef3c17574e42ddda468941e38b3aa0/json%20format/20240824.json')
        elif day == '20240913':
            original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/b9242da565999d8093fe6bbb0f307b576c07b433/json%20format/20240913.json')
        elif int(day) >= 20241122:
            original = pd.read_json(f'https://raw.githubusercontent.com/Ricky1020/TR-timetable-json/refs/heads/main/{day}.json')
        else:
            original = pd.read_json(f'https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/master/json%20format/{day}.json')
        #train_no = input('請輸入車次：')
        df_copy = original
        for i in range(len(original)):
            df_copy.loc[i, 'TrainInfos'] = str(df_copy['TrainInfos'][i])
        try:
            df_temp = df_copy[df_copy['TrainInfos'].str.contains(f"'Train': '{train_no}'")]
            ind = str(df_temp.index)
            ind = ind.replace('Index([','')
            #ind = ind.replace('Int64Index([','')
            ind = ind.replace("], dtype='int64')",'')
            ind = int(ind)
            if day == '20240212':
                original = pd.read_json('https://drive.google.com/uc?id=18sRcFpVWl_RdMtONk2qS3ZBfT2ZuMCto&export=download')
            elif day == '20240726':
                original = pd.read_json('https://drive.google.com/uc?id=1Rwd8tcXPCdVERSTKUotS7OC23PecTB8k&export=download')
            elif day == '20220402':
                original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/2ecc206ae6c06b2118ebeb80473774e897310e49/json%20format/20220402.json')
            elif day == '20240819':
                original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/83d998c9d9facb041ec1cc5573d2f887f81567b7/json%20format/20240819.json')
            elif day == '20240824':
                original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/440b8069abef3c17574e42ddda468941e38b3aa0/json%20format/20240824.json')
            elif day == '20240913':
                original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/b9242da565999d8093fe6bbb0f307b576c07b433/json%20format/20240913.json')
            elif int(day) >= 20241122:
                original = pd.read_json(f'https://raw.githubusercontent.com/Ricky1020/TR-timetable-json/refs/heads/main/{day}.json')
            else:
                original = pd.read_json(f'https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/master/json%20format/{day}.json')
            #original = pd.read_json('https://ods.railway.gov.tw/tra-ods-web/ods/download/dataResource/exceptionDataResource/8ae4c9818d42839e018d75a9a75564e6')
            df_temp2 = pd.DataFrame(original['TrainInfos'][ind])
            df_time = pd.DataFrame(df_temp2['TimeInfos'][0], index = [0])
            for i in range(1,len(df_temp2)):
                df_temp3 = pd.DataFrame(df_temp2['TimeInfos'][i], index = [i])
                df_time = pd.concat([df_time,df_temp3])
            df_time['站名'] = '0'
            df_time['到站時間'] = df_time['ARRTime']
            df_time['離站時間'] = df_time['DEPTime']
            df_time = df_time.drop(['Route','DEPTime','ARRTime'], axis = 'columns')
            line = {'0':'   ','1':'山線','2':'海線','3':'成追線','4':'山線、海線'}
            for i in range(5):
                if df_temp2['Line'][0] == str(i):
                    via_line = line[str(i)]
                    break
            car_class_list = {'1100':'DR2800/DR2900/DR3000與EMU自強號','1101':'太魯閣號','1102':'PP自強號(附自行車車廂)','1103':'DR3100自強號(含身障座位)','1104':'專列(自強)',
                    '1105':'郵輪式列車(自強)','1106':'商務專列(自強))','1107':'普悠瑪號','1108':'PP自強號','1109':'PP自強號(附親子車廂)',
                    '110A':'PP自強號(附多用途車廂)','110B':'EMU1200自強號','110C':'EMU300自強號','110D':'DR2800自強號','110E':'DR2900自強號','110F':'DR3100自強號',
                    '110G':'EMU3000自強號','110H':'EMU3000自強號(附親子座)','110K':'EMU3000自強號(特仕車)','1110':'莒光號','1111':'莒光號(含身障座位)',
                    '1112':'專列(莒光)','1113':'郵輪式列車(莒光)','1114':'莒光號(附自行車車廂)','1115':'莒光號(附自行車車廂、含身障座位)','1120':'復興號',
                    '1121':'專列(復興)','1122':'郵輪式列車(復興)','1130':'專列(電車)','1131':'區間車','1132':'區間快','1131':'區間車','1133':'郵輪式列車(電車)',
                    '1134':'專列(兩鐵列車)','1135':'區間車(附自行車車廂、含身障座位)','1140':'普快車','1141':'柴快車','1150':'專列(普通車)','1151':'普通車',
                    '1152':'行包專車','1154':'專列(柴客)','1155':'郵輪式列車(柴客)'}
            for i in car_class_list:
                if df_temp2['CarClass'][0] == str(i):
                    car_class = car_class_list[str(i)]
                    break
            sta_info = pd.read_json('https://ods.railway.gov.tw/tra-ods-web/ods/download/dataResource/0518b833e8964d53bfea3f7691aea0ee')
            sta_list = {}
            for i in range(len(sta_info)):
                if sta_info['stationCode'][i] < 1000:
                    code = '0' + str(sta_info['stationCode'][i])
                else:
                    code = str(sta_info['stationCode'][i])
                name = sta_info['stationName'][i]
                sta_list[code] = name
            for i in range(len(df_time)):
                if str(df_time['Station'][i]) in sta_list:
                    df_time.loc[i, '站名'] = sta_list[str(df_time.loc[i, 'Station'])]
            if via_line == '':
                #print(df_temp2['Train'][0]+'次', car_class, df_time['站名'][0], df_time['離站時間'][0], '→',
                    #df_time['站名'][len(df_time)-1], df_time['到站時間'][len(df_time)-1], '\n'+df_temp2['Note'][0])
                info = df_temp2['Train'][0]+'次' + ' ' + car_class + '\n' + df_time['站名'][0] + ' ' + df_time['離站時間'][0] + ' ' + '→' + ' ' + df_time['站名'][len(df_time)-1] + ' ' + df_time['到站時間'][len(df_time)-1] + '\n' + df_temp2['Note'][0]
            else:
                #print(df_temp2['Train'][0]+'次', car_class, df_time['站名'][0], df_time['離站時間'][0], '→',
                    #df_time['站名'][len(df_time)-1], df_time['到站時間'][len(df_time)-1], f'經：{via_line}', '\n'+df_temp2['Note'][0])
                info = df_temp2['Train'][0]+'次' + ' ' + car_class + ' ' + f'經：{via_line}' + '\n' + df_time['站名'][0] + ' ' + df_time['離站時間'][0] + ' ' + '→' + ' ' + df_time['站名'][len(df_time)-1] + ' ' + df_time['到站時間'][len(df_time)-1] + '\n' + df_temp2['Note'][0]
            
            #if len(df_time) >= 60:
            #print(df_time.head(60))
            #print(df_time.tail(len(df_time)-60))
            #else:
            #print(df_time)
        except:
            df_time = ''
            #print('車次輸入錯誤，請確認正確車次後再輸入')
            info = '車次輸入錯誤，請確認正確車次後再輸入'
    except:
        df_time = ''
        info = ('日期輸入錯誤')
    pd.set_option('display.max.rows', None)
    time_list = []
    time = ''
    for i in range(len(df_time)):
        if len(time) <= 1700:
            if len(df_time['站名'][i]) == 5:
                time += df_time['站名'][i] + ' ' + df_time['到站時間'][i] + '   ' + df_time['離站時間'][i]+'\n'
            elif len(df_time['站名'][i]) == 4:
                time += df_time['站名'][i] + '  ' + df_time['到站時間'][i] + '   ' + df_time['離站時間'][i]+'\n'
            elif len(df_time['站名'][i]) == 3:
                time += df_time['站名'][i] + '   ' + df_time['到站時間'][i] + '   ' + df_time['離站時間'][i]+'\n'
            else:
                time += df_time['站名'][i] + '     ' + df_time['到站時間'][i] + '   ' + df_time['離站時間'][i]+'\n'
        else:
            time_list.append(time)
            time = ''
            if len(df_time['站名'][i]) == 5:
                time += df_time['站名'][i] + ' ' + df_time['到站時間'][i] + '   ' + df_time['離站時間'][i]+'\n'
            elif len(df_time['站名'][i]) == 4:
                time += df_time['站名'][i] + '  ' + df_time['到站時間'][i] + '   ' + df_time['離站時間'][i]+'\n'
            elif len(df_time['站名'][i]) == 3:
                time += df_time['站名'][i] + '   ' + df_time['到站時間'][i] + '   ' + df_time['離站時間'][i]+'\n'
            else:
                time += df_time['站名'][i] + '     ' + df_time['到站時間'][i] + '   ' + df_time['離站時間'][i]+'\n'
    time_list.append(time)
    return info, time_list


def tr_train_time_find(day, sta_from, sta_to):
    import pandas as pd
    from datetime import datetime
    pd.options.mode.chained_assignment = None
    #day = int(input('請輸入日期：(格式：yyyymmdd，例：20240101，目前可提供查詢資料之日期僅限於2020/11/6至查詢當日後90天)'))
    info = ''
    info_list = []
    #sign = 0
    #n = 0
    try:
        day = str(day)
        if day == '20240212':
            original = pd.read_json('https://drive.google.com/uc?id=18sRcFpVWl_RdMtONk2qS3ZBfT2ZuMCto&export=download')
        elif day == '20240726':
            original = pd.read_json('https://drive.google.com/uc?id=1Rwd8tcXPCdVERSTKUotS7OC23PecTB8k&export=download')
        elif day == '20220402':
            original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/2ecc206ae6c06b2118ebeb80473774e897310e49/json%20format/20220402.json')
        elif day == '20240819':
            original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/83d998c9d9facb041ec1cc5573d2f887f81567b7/json%20format/20240819.json')
        elif day == '20240824':
            original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/440b8069abef3c17574e42ddda468941e38b3aa0/json%20format/20240824.json')
        elif day == '20240913':
            original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/b9242da565999d8093fe6bbb0f307b576c07b433/json%20format/20240913.json')
        elif int(day) >= 20241122:
            original = pd.read_json(f'https://raw.githubusercontent.com/Ricky1020/TR-timetable-json/refs/heads/main/{day}.json')
        else:
            original = pd.read_json(f'https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/master/json%20format/{day}.json')
        #sta_from = input('請輸入出發站：')
        #sta_to = input('請輸入到達站：')
        if '台' in sta_from:
            sta_from = sta_from.replace('台', '臺')
        if '台' in sta_to:
            sta_to = sta_to.replace('台', '臺')
        k = 0
        sta_info = pd.read_json('https://ods.railway.gov.tw/tra-ods-web/ods/download/dataResource/0518b833e8964d53bfea3f7691aea0ee')
        sta_list = {}
        for i in range(len(sta_info)):
            if sta_info['stationCode'][i] < 1000:
                code = '0' + str(sta_info['stationCode'][i])
            else:
                code = str(sta_info['stationCode'][i])
            name = sta_info['stationName'][i]
            sta_list[code] = name
        train_info = {}
        train_info = pd.DataFrame(train_info, index = [0])
        for i in range(len(original)):
            df_temp4 = pd.DataFrame(original['TrainInfos'][i])
            df_time2 = pd.DataFrame(df_temp4['TimeInfos'][0], index = [0])
            for j in range(1,len(df_temp4)):
                df_temp5 = pd.DataFrame(df_temp4['TimeInfos'][j], index = [j])
                df_time2 = pd.concat([df_time2,df_temp5])
            df_time2['站名'] = '0'
            df_time2['到站時間'] = df_time2['ARRTime']
            df_time2['離站時間'] = df_time2['DEPTime']
            df_time2 = df_time2.drop(['Route','DEPTime','ARRTime'], axis = 'columns')
            for j in range(len(df_time2)):
                if str(df_time2['Station'][j]) in sta_list:
                    df_time2.loc[j, '站名'] = sta_list[str(df_time2['Station'][j])]
            pd.options.mode.chained_assignment = None
            '''car_class_list = {'1100':'DR2800/DR2900/DR3000與EMU自強號','1101':'太魯閣號','1102':'PP自強號(附自行車車廂)','1103':'DR3100自強號(含身障座位)','1104':'專列(自強)',
                    '1105':'郵輪式列車(自強)','1106':'商務專列(自強)','1107':'普悠瑪號','1108':'PP自強號','1109':'PP自強號(附親子車廂)',
                    '110A':'PP自強號(附多用途車廂)','110B':'EMU1200自強號','110C':'EMU300自強號','110D':'DR2800自強號','110E':'DR2900自強號','110F':'DR3100自強號',
                    '110G':'EMU3000自強號','110H':'EMU3000自強號(附親子座)','110K':'EMU3000自強號(特仕車)','1110':'莒光號','1111':'莒光號(含身障座位)',
                    '1112':'專列(莒光)','1113':'郵輪式列車(莒光)','1114':'莒光號(附自行車車廂)','1115':'莒光號(附自行車車廂、含身障座位)','1120':'復興號',
                    '1121':'專列(復興)','1122':'郵輪式列車(復興)','1130':'專列(電車)','1131':'區間車','1132':'區間快','1131':'區間車','1133':'郵輪式列車(電車)',
                    '1134':'專列(兩鐵列車)','1135':'區間車(附自行車車廂、含身障座位)','1140':'普快車','1141':'柴快車','1150':'專列(普通車)','1151':'普通車',
                    '1152':'行包專車','1154':'專列(柴客)','1155':'郵輪式列車(柴客)'}'''
            car_class_list = {'1100':'DR2800/DR2900/DR3000與EMU自強號','1101':'太魯閣號    ','1102':'PP自強號(自)','1103':'柴自強(障)  ','1104':'專列(自強)  ',
                    '1105':'郵輪式(自強)','1106':'商專列(自強)','1107':'普悠瑪號    ','1108':'PP自強號    ','1109':'PP自強號(親)',
                    '110A':'PP自強號(多)','110B':'EMU1200自強號','110C':'EMU300自強號','110D':'DR2800自強號','110E':'DR2900自強號','110F':'柴自強      ',
                    '110G':'自強3000   ','110H':'自強3000(親)','110K':'自強3000(特)','1110':'莒光號      ','1111':'莒光號(障)  ',
                    '1112':'專列(莒光)  ','1113':'郵輪式(莒光)','1114':'莒光號(自)','1115':'莒光號(自障)','1120':'復興號      ',
                    '1121':'專列(復興)  ','1122':'郵輪式(復興)','1130':'專列(電車)  ','1131':'區間車      ','1132':'區間快      ','1131':'區間車      ','1133':'郵輪式(電車)',
                    '1134':'專列(兩鐵)  ','1135':'區間車(自障)','1140':'普快車      ','1141':'柴快車','1150':'專列(普通車)','1151':'普通車',
                    '1152':'行包專車','1154':'專列(柴客)  ','1155':'郵輪式(柴客)'}
            for i in car_class_list:
                if df_temp4['CarClass'][0] == str(i):
                    car_class = car_class_list[str(i)]
                    break
            line = {'0':'    ','1':'山線 ','2':'海線 ','3':'成追線','4':'山線、海線'}
            for i in range(5):
                if df_temp4['Line'][0] == str(i):
                    via_line = line[str(i)]
                    break
            if df_time2['站名'].isin([sta_from]).any():
                if df_time2['站名'].isin([sta_to]).any():
                    df_temp6 = df_time2[df_time2['站名'].str.contains(sta_from)]
                    ind2 = str(df_temp6.index)
                    ind2 = ind2.replace('Index([','')
                    ind2 = ind2.replace("], dtype='int64')",'')
                    try:
                        ind2 = int(ind2)
                    except:
                        ind_temp = ind2.split(',')
                        if int(df_temp4['Train'][0]) % 2 == 1: #逆行
                            if sta_from == '臺中':
                                ind2 = int(ind_temp[1])
                            elif sta_from == '烏日':
                                if via_line == '成追線':
                                    ind2 = int(ind_temp[1])
                                else:
                                    ind2 = int(ind_temp[0])
                            elif sta_from == '左營':
                                ind2 = int(ind_temp[1])
                            elif sta_from == '新竹':
                                ind2 = int(ind_temp[1])
                            else:
                                ind2 = int(ind_temp[0])
                        else:
                            if sta_from == '烏日':
                                if via_line == '山線':
                                    ind2 = int(ind_temp[1])
                                else:
                                    ind2 = int(ind_temp[0])
                            elif sta_from == '樹林':
                                ind2 = int(ind_temp[1])
                            else:
                                ind2 = int(ind_temp[0])
                    df_temp7 = df_time2[df_time2['站名'].str.contains(sta_to)]
                    ind3 = str(df_temp7.index)
                    ind3 = ind3.replace('Index([','')
                    ind3 = ind3.replace("], dtype='int64')",'')
                    try:
                        ind3 = int(ind3)
                    except:
                        ind_temp = ind3.split(',')
                        if int(df_temp4['Train'][0]) % 2 == 1: #逆行
                            if sta_to == '臺中':
                                ind3 = int(ind_temp[1])
                            elif sta_to == '臺北' and str(df_temp4['Train'][0]) == '1':
                                ind3 = int(ind_temp[1])
                            elif sta_to == '烏日':
                                if via_line == '成追線':
                                    ind3 = int(ind_temp[1])
                                else:
                                    ind3 = int(ind_temp[0])
                            elif sta_to == '左營':
                                ind3 = int(ind_temp[1])
                            elif sta_to == '新竹':
                                ind3 = int(ind_temp[1])
                            else:
                                ind3 = int(ind_temp[0])
                        else:
                            if sta_to == '臺北' and str(df_temp4['Train'][0]) == '2':
                                ind3 = int(ind_temp[1])
                            elif sta_to == '烏日':
                                if via_line == '山線':
                                    ind3 = int(ind_temp[1])
                                else:
                                    ind3 = int(ind_temp[0])
                            elif sta_to == '蘇澳':
                                ind3 = int(ind_temp[1])
                            elif sta_to == '樹林':
                                ind3 = int(ind_temp[1])
                            else:
                                ind3 = int(ind_temp[0])
                    now = datetime.now()
                    time_from = now.strptime(df_time2['離站時間'][ind2], '%H:%M:%S')
                    time_from_str = str(time_from)
                    time_from_str = time_from_str.replace('1900-01-01 ','')
                    time_to = now.strptime(df_time2['到站時間'][ind3], '%H:%M:%S')
                    time_to_str = str(time_to)
                    time_to_str = time_to_str.replace('1900-01-01 ','')
                    duration = time_to - time_from
                    #duration = str(duration)
                    duration_str = str(duration)
                    try:
                        #duration = duration.replace('-1 day, ','')
                        duration_str = duration_str.replace('-1 day, ','')
                    except:
                        #duration = str(duration)
                        duration_str = str(duration)
                    if ind2 < ind3:
                        k += 1
                        temp_info = {}
                        temp_info['車次'] = df_temp4['Train'][0]
                        temp_info['車種'] = car_class
                        temp_info['起站'] = df_time2['站名'][0]
                        if df_time2['站名'][len(df_time2)-1] == '臺北-環島':
                            temp_info['終站'] = '臺北'
                        else:
                            temp_info['終站'] = df_time2['站名'][len(df_time2)-1]
                        temp_info['經由'] = via_line
                        temp_info['出發站'] = df_time2['站名'][ind2]
                        temp_info['出發站開車時間1'] = time_from
                        temp_info['出發站開車時間'] = time_from_str
                        temp_info['到達站'] = df_time2['站名'][ind3]
                        temp_info['到達站抵達時間1'] = time_to
                        temp_info['到達站抵達時間'] = time_to_str
                        temp_info['行駛時間1'] = duration
                        temp_info['行駛時間'] = duration_str
                        temp_info = pd.DataFrame(temp_info, index = [k])
                        train_info = pd.concat([train_info,temp_info])
                    train_info = train_info.dropna(axis = 0)
        train_info = train_info.dropna(axis = 0)
        train_info = train_info.sort_values(by = '出發站開車時間1')
        train_info = train_info.drop(['出發站開車時間1','到達站抵達時間1','行駛時間1'], axis = 'columns')
        train_info = train_info.set_index('車次')
        train_info = train_info.reset_index()
        for i in range(len(train_info)):
            if len(info) <= 1700:
                if len(str(train_info.loc[i, '車次'])) == 1:
                    info += str(train_info.loc[i, '車次']) + '    ' 
                elif len(str(train_info.loc[i, '車次'])) == 2:
                    info += str(train_info.loc[i, '車次']) + '   ' 
                elif len(str(train_info.loc[i, '車次'])) == 3:
                    info += str(train_info.loc[i, '車次']) + '  ' 
                else:
                    info += str(train_info.loc[i, '車次']) + ' ' 

                info += str(train_info.loc[i, '車種']) + ' '

                if len(str(train_info.loc[i, '起站'])) == 2:
                    info += str(train_info.loc[i, '起站']) + '   ' 
                elif len(str(train_info.loc[i, '起站'])) == 3:
                    info += str(train_info.loc[i, '起站']) + ' ' 

                if len(str(train_info.loc[i, '終站'])) == 2:
                    info += str(train_info.loc[i, '終站']) + '   ' 
                elif len(str(train_info.loc[i, '終站'])) == 3:
                    info += str(train_info.loc[i, '終站']) + ' ' 
                #info += str(train_info.loc[i, '起站']) + ' ' + str(train_info.loc[i, '終站']) + ' '

                info += str(train_info.loc[i, '經由']) + ' ' + str(train_info.loc[i, '出發站開車時間']) + '  '
                info += str(train_info.loc[i, '到達站抵達時間']) + '  ' + str(train_info.loc[i, '行駛時間']) + '\n'
            
            else:
                info_list.append(info)
                info = ''
                if len(str(train_info.loc[i, '車次'])) == 1:
                    info += str(train_info.loc[i, '車次']) + '    ' 
                elif len(str(train_info.loc[i, '車次'])) == 2:
                    info += str(train_info.loc[i, '車次']) + '   ' 
                elif len(str(train_info.loc[i, '車次'])) == 3:
                    info += str(train_info.loc[i, '車次']) + '  ' 
                else:
                    info += str(train_info.loc[i, '車次']) + ' ' 
                info += str(train_info.loc[i, '車種']) + ' '
                if len(str(train_info.loc[i, '起站'])) == 2:
                    info += str(train_info.loc[i, '起站']) + '   ' 
                elif len(str(train_info.loc[i, '起站'])) == 3:
                    info += str(train_info.loc[i, '起站']) + ' ' 
                if len(str(train_info.loc[i, '終站'])) == 2:
                    info += str(train_info.loc[i, '終站']) + '   ' 
                elif len(str(train_info.loc[i, '終站'])) == 3:
                    info += str(train_info.loc[i, '終站']) + ' ' 
                info += str(train_info.loc[i, '經由']) + ' ' + str(train_info.loc[i, '出發站開車時間']) + '  '
                info += str(train_info.loc[i, '到達站抵達時間']) + '  ' + str(train_info.loc[i, '行駛時間']) + '\n'
        info_list.append(info)    
            #n = i
        """
            if len(info) > 900:
                sign = 1
                break
                return info, sign, n
        """

    except:
        info = ('錯誤，請再試一次')
        info_list.append(info)
    return info_list#, sign, n
    #pd.set_option('display.max.rows', None)
    #train_info
"""
def tr_train_time_find_c(day, sta_from, sta_to, c):
    import pandas as pd
    from datetime import datetime
    pd.options.mode.chained_assignment = None
    #day = int(input('請輸入日期：(格式：yyyymmdd，例：20240101，目前可提供查詢資料之日期僅限於2020/11/6至查詢當日後90天)'))
    info = ''
    sign = 0
    n = c
    try:
        day = str(day)
        if day == '20240212':
            original = pd.read_json('https://drive.google.com/uc?id=18sRcFpVWl_RdMtONk2qS3ZBfT2ZuMCto&export=download')
        elif day == '20240726':
            original = pd.read_json('https://drive.google.com/uc?id=1Rwd8tcXPCdVERSTKUotS7OC23PecTB8k&export=download')
        elif day == '20220402':
            original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/2ecc206ae6c06b2118ebeb80473774e897310e49/json%20format/20220402.json')
        elif day == '20240819':
            original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/83d998c9d9facb041ec1cc5573d2f887f81567b7/json%20format/20240819.json')
        elif day == '20240824':
            original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/440b8069abef3c17574e42ddda468941e38b3aa0/json%20format/20240824.json')
        else:
            original = pd.read_json(f'https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/master/json%20format/{day}.json')
        #sta_from = input('請輸入出發站：')
        #sta_to = input('請輸入到達站：')
        if '台' in sta_from:
            sta_from = sta_from.replace('台', '臺')
        if '台' in sta_to:
            sta_to = sta_to.replace('台', '臺')
        k = 0
        sta_info = pd.read_json('https://ods.railway.gov.tw/tra-ods-web/ods/download/dataResource/0518b833e8964d53bfea3f7691aea0ee')
        sta_list = {}
        for i in range(len(sta_info)):
            if sta_info['stationCode'][i] < 1000:
                code = '0' + str(sta_info['stationCode'][i])
            else:
                code = str(sta_info['stationCode'][i])
            name = sta_info['stationName'][i]
            sta_list[code] = name
        train_info = {}
        train_info = pd.DataFrame(train_info, index = [0])
        for i in range(len(original)):
            df_temp4 = pd.DataFrame(original['TrainInfos'][i])
            df_time2 = pd.DataFrame(df_temp4['TimeInfos'][0], index = [0])
            for j in range(1,len(df_temp4)):
                df_temp5 = pd.DataFrame(df_temp4['TimeInfos'][j], index = [j])
                df_time2 = pd.concat([df_time2,df_temp5])
            df_time2['站名'] = '0'
            df_time2['到站時間'] = df_time2['ARRTime']
            df_time2['離站時間'] = df_time2['DEPTime']
            df_time2 = df_time2.drop(['Route','DEPTime','ARRTime'], axis = 'columns')
            for j in range(len(df_time2)):
                if str(df_time2['Station'][j]) in sta_list:
                    df_time2.loc[j, '站名'] = sta_list[str(df_time2['Station'][j])]
            pd.options.mode.chained_assignment = None
            '''car_class_list = {'1100':'DR2800/DR2900/DR3000與EMU自強號','1101':'太魯閣號','1102':'PP自強號(附自行車車廂)','1103':'DR3100自強號(含身障座位)','1104':'專列(自強)',
                    '1105':'郵輪式列車(自強)','1106':'商務專列(自強)','1107':'普悠瑪號','1108':'PP自強號','1109':'PP自強號(附親子車廂)',
                    '110A':'PP自強號(附多用途車廂)','110B':'EMU1200自強號','110C':'EMU300自強號','110D':'DR2800自強號','110E':'DR2900自強號','110F':'DR3100自強號',
                    '110G':'EMU3000自強號','110H':'EMU3000自強號(附親子座)','110K':'EMU3000自強號(特仕車)','1110':'莒光號','1111':'莒光號(含身障座位)',
                    '1112':'專列(莒光)','1113':'郵輪式列車(莒光)','1114':'莒光號(附自行車車廂)','1115':'莒光號(附自行車車廂、含身障座位)','1120':'復興號',
                    '1121':'專列(復興)','1122':'郵輪式列車(復興)','1130':'專列(電車)','1131':'區間車','1132':'區間快','1131':'區間車','1133':'郵輪式列車(電車)',
                    '1134':'專列(兩鐵列車)','1135':'區間車(附自行車車廂、含身障座位)','1140':'普快車','1141':'柴快車','1150':'專列(普通車)','1151':'普通車',
                    '1152':'行包專車','1154':'專列(柴客)','1155':'郵輪式列車(柴客)'}'''
            car_class_list = {'1100':'DR2800/DR2900/DR3000與EMU自強號','1101':'太魯閣號    ','1102':'PP自強號(自)','1103':'柴自強(障)  ','1104':'專列(自強)  ',
                    '1105':'郵輪式(自強)','1106':'商專列(自強)','1107':'普悠瑪號    ','1108':'PP自強號    ','1109':'PP自強號(親)',
                    '110A':'PP自強號(多)','110B':'EMU1200自強號','110C':'EMU300自強號','110D':'DR2800自強號','110E':'DR2900自強號','110F':'柴自強      ',
                    '110G':'自強3000   ','110H':'自強3000(親)','110K':'自強3000(特)','1110':'莒光號      ','1111':'莒光號(障)  ',
                    '1112':'專列(莒光)  ','1113':'郵輪式(莒光)','1114':'莒光號(自)','1115':'莒光號(自障)','1120':'復興號      ',
                    '1121':'專列(復興)  ','1122':'郵輪式(復興)','1130':'專列(電車)','1131':'區間車      ','1132':'區間快      ','1131':'區間車      ','1133':'郵輪式(電車)',
                    '1134':'專列(兩鐵)  ','1135':'區間車(自障)','1140':'普快車      ','1141':'柴快車','1150':'專列(普通車)','1151':'普通車',
                    '1152':'行包專車','1154':'專列(柴客)','1155':'郵輪式(柴客)'}
            for i in car_class_list:
                if df_temp4['CarClass'][0] == str(i):
                    car_class = car_class_list[str(i)]
                    break
            line = {'0':'    ','1':'山線 ','2':'海線 ','3':'成追線','4':'山線、海線'}
            for i in range(5):
                if df_temp4['Line'][0] == str(i):
                    via_line = line[str(i)]
                    break
            if df_time2['站名'].isin([sta_from]).any():
                if df_time2['站名'].isin([sta_to]).any():
                    df_temp6 = df_time2[df_time2['站名'].str.contains(sta_from)]
                    ind2 = str(df_temp6.index)
                    ind2 = ind2.replace('Index([','')
                    ind2 = ind2.replace("], dtype='int64')",'')
                    try:
                        ind2 = int(ind2)
                    except:
                        ind_temp = ind2.split(',')
                        if int(df_temp4['Train'][0]) % 2 == 1: #逆行
                            if sta_from == '臺中':
                                ind2 = int(ind_temp[1])
                            elif sta_from == '烏日':
                                if via_line == '成追線':
                                    ind2 = int(ind_temp[1])
                                else:
                                    ind2 = int(ind_temp[0])
                            elif sta_from == '左營':
                                ind2 = int(ind_temp[1])
                            elif sta_from == '新竹':
                                ind2 = int(ind_temp[1])
                            else:
                                ind2 = int(ind_temp[0])
                        else:
                            if sta_from == '烏日':
                                if via_line == '山線':
                                    ind2 = int(ind_temp[1])
                                else:
                                    ind2 = int(ind_temp[0])
                            elif sta_from == '樹林':
                                ind2 = int(ind_temp[1])
                            else:
                                ind2 = int(ind_temp[0])
                    df_temp7 = df_time2[df_time2['站名'].str.contains(sta_to)]
                    ind3 = str(df_temp7.index)
                    ind3 = ind3.replace('Index([','')
                    ind3 = ind3.replace("], dtype='int64')",'')
                    try:
                        ind3 = int(ind3)
                    except:
                        ind_temp = ind3.split(',')
                        if int(df_temp4['Train'][0]) % 2 == 1: #逆行
                            if sta_to == '臺中':
                                ind3 = int(ind_temp[1])
                            elif sta_to == '臺北' and str(df_temp4['Train'][0]) == '1':
                                ind3 = int(ind_temp[1])
                            elif sta_to == '烏日':
                                if via_line == '成追線':
                                    ind3 = int(ind_temp[1])
                                else:
                                    ind3 = int(ind_temp[0])
                            elif sta_to == '左營':
                                ind3 = int(ind_temp[1])
                            elif sta_to == '新竹':
                                ind3 = int(ind_temp[1])
                            else:
                                ind3 = int(ind_temp[0])
                        else:
                            if sta_to == '臺北' and str(df_temp4['Train'][0]) == '2':
                                ind3 = int(ind_temp[1])
                            elif sta_to == '烏日':
                                if via_line == '山線':
                                    ind3 = int(ind_temp[1])
                                else:
                                    ind3 = int(ind_temp[0])
                            elif sta_to == '蘇澳':
                                ind3 = int(ind_temp[1])
                            elif sta_to == '樹林':
                                ind3 = int(ind_temp[1])
                            else:
                                ind3 = int(ind_temp[0])
                    now = datetime.now()
                    time_from = now.strptime(df_time2['離站時間'][ind2], '%H:%M:%S')
                    time_from_str = str(time_from)
                    time_from_str = time_from_str.replace('1900-01-01 ','')
                    time_to = now.strptime(df_time2['到站時間'][ind3], '%H:%M:%S')
                    time_to_str = str(time_to)
                    time_to_str = time_to_str.replace('1900-01-01 ','')
                    duration = time_to - time_from
                    #duration = str(duration)
                    duration_str = str(duration)
                    try:
                        #duration = duration.replace('-1 day, ','')
                        duration_str = duration_str.replace('-1 day, ','')
                    except:
                        #duration = str(duration)
                        duration_str = str(duration)
                    if ind2 < ind3:
                        k += 1
                        temp_info = {}
                        temp_info['車次'] = df_temp4['Train'][0]
                        temp_info['車種'] = car_class
                        temp_info['起站'] = df_time2['站名'][0]
                        if df_time2['站名'][len(df_time2)-1] == '臺北-環島':
                            temp_info['終站'] = '臺北'
                        else:
                            temp_info['終站'] = df_time2['站名'][len(df_time2)-1]
                        temp_info['經由'] = via_line
                        temp_info['出發站'] = df_time2['站名'][ind2]
                        temp_info['出發站開車時間1'] = time_from
                        temp_info['出發站開車時間'] = time_from_str
                        temp_info['到達站'] = df_time2['站名'][ind3]
                        temp_info['到達站抵達時間1'] = time_to
                        temp_info['到達站抵達時間'] = time_to_str
                        temp_info['行駛時間1'] = duration
                        temp_info['行駛時間'] = duration_str
                        temp_info = pd.DataFrame(temp_info, index = [k])
                        train_info = pd.concat([train_info,temp_info])
                    train_info = train_info.dropna(axis = 0)
        train_info = train_info.dropna(axis = 0)
        train_info = train_info.sort_values(by = '出發站開車時間1')
        train_info = train_info.drop(['出發站開車時間1','到達站抵達時間1','行駛時間1'], axis = 'columns')
        train_info = train_info.set_index('車次')
        train_info = train_info.reset_index()
        for i in range(c+1, len(train_info)):

            if len(str(train_info.loc[i, '車次'])) == 1:
                info += str(train_info.loc[i, '車次']) + '    ' 
            elif len(str(train_info.loc[i, '車次'])) == 2:
                info += str(train_info.loc[i, '車次']) + '   ' 
            elif len(str(train_info.loc[i, '車次'])) == 3:
                info += str(train_info.loc[i, '車次']) + '  ' 
            else:
                info += str(train_info.loc[i, '車次']) + ' ' 

            info += str(train_info.loc[i, '車種']) + ' '

            if len(str(train_info.loc[i, '起站'])) == 2:
                info += str(train_info.loc[i, '起站']) + '   ' 
            elif len(str(train_info.loc[i, '起站'])) == 3:
                info += str(train_info.loc[i, '起站']) + ' ' 

            if len(str(train_info.loc[i, '終站'])) == 2:
                info += str(train_info.loc[i, '終站']) + '   ' 
            elif len(str(train_info.loc[i, '終站'])) == 3:
                info += str(train_info.loc[i, '終站']) + ' ' 
            #info += str(train_info.loc[i, '起站']) + ' ' + str(train_info.loc[i, '終站']) + ' '
            info += str(train_info.loc[i, '經由']) + ' ' + str(train_info.loc[i, '出發站開車時間']) + '   '
            info += str(train_info.loc[i, '到達站抵達時間']) + '   ' + str(train_info.loc[i, '行駛時間']) + '\n'
            n = i
            if len(info) > 900:
                sign = 1
                break
                return info, sign, n

    except:
        info = ('錯誤，請再試一次')
    return info, sign, n
#"""
def tr_sta_time(date, sta):
    import pandas as pd
    from datetime import datetime
    pd.options.mode.chained_assignment = None
    day = date
    info = ''
    info_list = []
    #sign = 0 
    #n = 0
    try:
        day = str(day)
        option = 2
        if day == '20240212':
            original = pd.read_json('https://drive.google.com/uc?id=18sRcFpVWl_RdMtONk2qS3ZBfT2ZuMCto&export=download')
        elif day == '20240726':
            original = pd.read_json('https://drive.google.com/uc?id=1Rwd8tcXPCdVERSTKUotS7OC23PecTB8k&export=download')
        elif day == '20220402':
            original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/2ecc206ae6c06b2118ebeb80473774e897310e49/json%20format/20220402.json')
        elif day == '20240819':
            original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/83d998c9d9facb041ec1cc5573d2f887f81567b7/json%20format/20240819.json')
        elif day == '20240824':
            original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/440b8069abef3c17574e42ddda468941e38b3aa0/json%20format/20240824.json')
        elif day == '20240913':
            original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/b9242da565999d8093fe6bbb0f307b576c07b433/json%20format/20240913.json')
        elif int(day) >= 20241122:
            original = pd.read_json(f'https://raw.githubusercontent.com/Ricky1020/TR-timetable-json/refs/heads/main/{day}.json')
        else:
            original = pd.read_json(f'https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/master/json%20format/{day}.json')
        station = sta
        if '台' in station:
            station = station.replace('台', '臺')
        k = 0
        train_info = {}
        train_info = pd.DataFrame(train_info, index = [0])
        now = datetime.now()
        sta_info = pd.read_json('https://ods.railway.gov.tw/tra-ods-web/ods/download/dataResource/0518b833e8964d53bfea3f7691aea0ee')
        sta_list = {}
        for i in range(len(sta_info)):
            if sta_info['stationCode'][i] < 1000:
                code = '0' + str(sta_info['stationCode'][i])
            else:
                code = str(sta_info['stationCode'][i])
            name = sta_info['stationName'][i]
            sta_list[code] = name
        for i in range(len(original)):
            df_temp8 = pd.DataFrame(original['TrainInfos'][i])
            line = {'0':'','1':'山線','2':'海線','3':'成追線','4':'山線、海線'}
            for i in range(5):
                if df_temp8['Line'][0] == str(i):
                    via_line = line[str(i)]
                    break
            df_time3 = pd.DataFrame(df_temp8['TimeInfos'][0], index = [0])
            for j in range(1,len(df_temp8)):
                df_temp9 = pd.DataFrame(df_temp8['TimeInfos'][j], index = [j])
                df_time3 = pd.concat([df_time3,df_temp9])
            df_time3['站名'] = ''
            df_time3['到站時間'] = df_time3['ARRTime']
            df_time3['離站時間'] = df_time3['DEPTime']
            df_time3 = df_time3.drop(['Route','DEPTime','ARRTime'], axis = 'columns')
            for j in range(len(df_time3)):
                if str(df_time3['Station'][j]) in sta_list:
                    df_time3.loc[j, '站名'] = sta_list[str(df_time3.loc[j, 'Station'])]
            pd.options.mode.chained_assignment = None
            car_class_list = {'1100':'DR2800/DR2900/DR3000與EMU自強號','1101':'太魯閣號    ','1102':'PP自強號(自)','1103':'柴自強(障)  ','1104':'專列(自強)  ',
                    '1105':'郵輪式(自強)','1106':'商專列(自強)','1107':'普悠瑪號    ','1108':'PP自強號    ','1109':'PP自強號(親)',
                    '110A':'PP自強號(多)','110B':'EMU1200自強號','110C':'EMU300自強號','110D':'DR2800自強號','110E':'DR2900自強號','110F':'柴自強      ',
                    '110G':'自強3000   ','110H':'自強3000(親)','110K':'自強3000(特)','1110':'莒光號      ','1111':'莒光號(障)  ',
                    '1112':'專列(莒光)  ','1113':'郵輪式(莒光)','1114':'莒光號(自)','1115':'莒光號(自障)','1120':'復興號      ',
                    '1121':'專列(復興)  ','1122':'郵輪式(復興)','1130':'專列(電車)','1131':'區間車      ','1132':'區間快      ','1131':'區間車      ','1133':'郵輪式(電車)',
                    '1134':'專列(兩鐵)  ','1135':'區間車(自障)','1140':'普快車      ','1141':'柴快車','1150':'專列(普通車)','1151':'普通車',
                    '1152':'行包專車','1154':'專列(柴客)  ','1155':'郵輪式(柴客)'}
            for i in car_class_list:
                if df_temp8['CarClass'][0] == str(i):
                    car_class = car_class_list[str(i)]
                    break
            if df_time3['站名'].isin([station]).any():
                df_temp9 = df_time3[df_time3['站名'].str.contains(station)]
                ind4 = str(df_temp9.index)
                ind4 = ind4.replace('Index([','')
                ind4 = ind4.replace("], dtype='int64')",'')
                try:
                    ind4 = int(ind4)
                except:
                    ind_temp = ind4.split(',')
                    if int(df_temp8['Train'][0]) % 2 == 1: #逆行
                        if station == '臺中':
                            ind4 = int(ind_temp[1])
                        elif station == '烏日':
                            if via_line == '成追線':
                                ind4 = int(ind_temp[1])
                            else:
                                ind4 = int(ind_temp[0])
                        elif station == '左營':
                            ind4 = int(ind_temp[1])
                        elif station == '新竹':
                            ind4 = int(ind_temp[1])
                        else:
                            ind4 = int(ind_temp[0])
                    else:
                        if station == '烏日':
                            if via_line == '山線':
                                ind4 = int(ind_temp[1])
                            else:
                                ind4 = int(ind_temp[0])
                        elif station == '蘇澳':
                            ind4 = int(ind_temp[1])
                        elif station == '樹林':
                            ind4 = int(ind_temp[1])
                        else:
                            ind4 = int(ind_temp[0])

                #time = now.strptime(df_time3['離站時間'][ind4], '%H:%M:%S')
                #time_str = str(time)
                #time_str = time_str.replace('1900-01-01 ','')
                if station == df_time3['站名'][len(df_time3)-1]:
                    k += 1
                    time = now.strptime(df_time3['到站時間'][ind4], '%H:%M:%S')
                    time_str = str(time)
                    time_str = time_str.replace('1900-01-01 ','')
                    temp_info = {}
                    temp_info['車次'] = df_temp8['Train'][0]
                    temp_info['車種'] = car_class
                    temp_info['起站'] = df_time3['站名'][0]
                    if df_time3['站名'][len(df_time3)-1] == '臺北-環島':
                        temp_info['終站'] = '臺北'
                    else:
                        temp_info['終站'] = df_time3['站名'][len(df_time3)-1]
                    temp_info['經由'] = via_line
                    temp_info['站名'] = df_time3['站名'][ind4]
                    temp_info['開車時間1'] = time
                    temp_info['開車時間'] = time_str
                    #temp_info['抵達時間1'] = time
                    #temp_info['抵達時間'] = time_str
                    temp_info['停靠站'] = '終點站'
                    temp_info = pd.DataFrame(temp_info, index = [k])
                    train_info = pd.concat([train_info,temp_info])
                elif option == 2:
                    if car_class == '區間車      ':
                        if df_temp8['Train'].isin(['4514','4550','4552','4558','4556','4503','4513','4543']).any():
                            k += 1
                            time = now.strptime(df_time3['離站時間'][ind4], '%H:%M:%S')
                            time_str = str(time)
                            time_str = time_str.replace('1900-01-01 ','')
                            temp_info = {}
                            temp_info['車次'] = df_temp8['Train'][0]
                            temp_info['車種'] = car_class
                            temp_info['起站'] = df_time3['站名'][0]
                            if df_time3['站名'][len(df_time3)-1] == '臺北-環島':
                                temp_info['終站'] = '臺北'
                            else:
                                temp_info['終站'] = df_time3['站名'][len(df_time3)-1]
                            temp_info['經由'] = via_line
                            temp_info['站名'] = df_time3['站名'][ind4]
                            temp_info['開車時間1'] = time
                            temp_info['開車時間'] = time_str
                            temp1 = ''
                            m = 0
                            for j in range(ind4+1, len(df_time3)):
                                m += 1
                                temp1 += df_time3['站名'][j]+' '
                            temp_info['停靠站'] = temp1
                            temp_info = pd.DataFrame(temp_info, index = [k])
                            train_info = pd.concat([train_info,temp_info])
                        else:
                            k += 1
                            time = now.strptime(df_time3['離站時間'][ind4], '%H:%M:%S')
                            time_str = str(time)
                            time_str = time_str.replace('1900-01-01 ','')
                            temp_info = {}
                            temp_info['車次'] = df_temp8['Train'][0]
                            temp_info['車種'] = car_class
                            temp_info['起站'] = df_time3['站名'][0]
                            if df_time3['站名'][len(df_time3)-1] == '臺北-環島':
                                temp_info['終站'] = '臺北'
                            else:
                                temp_info['終站'] = df_time3['站名'][len(df_time3)-1]
                            temp_info['經由'] = via_line
                            temp_info['站名'] = df_time3['站名'][ind4]
                            temp_info['開車時間1'] = time
                            temp_info['開車時間'] = time_str
                            temp_info['停靠站'] = '下一站：'+df_time3['站名'][ind4+1]+'(中途各站皆停)'
                            temp_info = pd.DataFrame(temp_info, index = [k])
                            train_info = pd.concat([train_info,temp_info])
                    else:
                        k += 1
                        time = now.strptime(df_time3['離站時間'][ind4], '%H:%M:%S')
                        time_str = str(time)
                        time_str = time_str.replace('1900-01-01 ','')
                        temp_info = {}
                        temp_info['車次'] = df_temp8['Train'][0]
                        temp_info['車種'] = car_class
                        temp_info['起站'] = df_time3['站名'][0]
                        if df_time3['站名'][len(df_time3)-1] == '臺北-環島':
                            temp_info['終站'] = '臺北'
                        else:
                            temp_info['終站'] = df_time3['站名'][len(df_time3)-1]
                        temp_info['經由'] = via_line
                        temp_info['站名'] = df_time3['站名'][ind4]
                        temp_info['開車時間1'] = time
                        temp_info['開車時間'] = time_str
                        temp1 = ''
                        m = 0
                        for j in range(ind4+1, len(df_time3)):
                            m += 1
                            temp1 += df_time3['站名'][j]+' '
                        temp_info['停靠站'] = temp1
                        temp_info = pd.DataFrame(temp_info, index = [k])
                        train_info = pd.concat([train_info,temp_info])
                        #if m >= 1:
                            #print(temp_info['車次'][k], temp_info['車種'][k], '往'+temp_info['終站'][k], temp_info['開車時間'][k], '停靠站：'+temp_info['停靠站'][k])
                
        train_info = train_info.dropna(axis = 0)
        train_info = train_info.sort_values(by = '開車時間1')
        train_info = train_info.drop(['開車時間1'], axis = 'columns')
        train_info = train_info.set_index('車次')
        train_info = train_info.reset_index()
        try:
            for m in range(len(train_info)):
                if len(info) <= 1700:
                    if len(str(train_info.loc[m, '車次'])) == 1:
                        info += str(train_info.loc[m, '車次']) + '    ' 
                    elif len(str(train_info.loc[m, '車次'])) == 2:
                        info += str(train_info.loc[m, '車次']) + '   ' 
                    elif len(str(train_info.loc[m, '車次'])) == 3:
                        info += str(train_info.loc[m, '車次']) + '  ' 
                    else:
                        info += str(train_info.loc[m, '車次']) + ' '

                    info += str(train_info.loc[m, '車種']) + ' '

                    if len(str(train_info.loc[m, '起站'])) == 2:
                        info += str(train_info.loc[m, '起站']) + '   ' 
                    elif len(str(train_info.loc[m, '起站'])) == 3:
                        info += str(train_info.loc[m, '起站']) + ' ' 

                    if len(str(train_info.loc[m, '終站'])) == 2:
                        info += str(train_info.loc[m, '終站']) + '   ' 
                    elif len(str(train_info.loc[m, '終站'])) == 3:
                        info += str(train_info.loc[m, '終站']) + ' '

                    if len(str(train_info.loc[m, '經由'])) == 3:
                        info += str(train_info.loc[m, '經由']) + ' ' 
                    elif len(str(train_info.loc[m, '經由'])) == 2:
                        info += str(train_info.loc[m, '經由']) + '   '
                    else:
                        info += str(train_info.loc[m, '經由']) + '       '    

                    info += str(train_info.loc[m, '開車時間']) + '  ' + '停靠站：' + train_info.loc[m, '停靠站'] + '\n'
                else:
                    info_list.append(info)
                    info = ''
                    if len(str(train_info.loc[m, '車次'])) == 1:
                        info += str(train_info.loc[m, '車次']) + '    ' 
                    elif len(str(train_info.loc[m, '車次'])) == 2:
                        info += str(train_info.loc[m, '車次']) + '   ' 
                    elif len(str(train_info.loc[m, '車次'])) == 3:
                        info += str(train_info.loc[m, '車次']) + '  ' 
                    else:
                        info += str(train_info.loc[m, '車次']) + ' '
                    info += str(train_info.loc[m, '車種']) + ' '
                    if len(str(train_info.loc[m, '起站'])) == 2:
                        info += str(train_info.loc[m, '起站']) + '   ' 
                    elif len(str(train_info.loc[m, '起站'])) == 3:
                        info += str(train_info.loc[m, '起站']) + ' ' 
                    if len(str(train_info.loc[m, '終站'])) == 2:
                        info += str(train_info.loc[m, '終站']) + '   ' 
                    elif len(str(train_info.loc[m, '終站'])) == 3:
                        info += str(train_info.loc[m, '終站']) + ' '
                    if len(str(train_info.loc[m, '經由'])) == 3:
                        info += str(train_info.loc[m, '經由']) + ' ' 
                    elif len(str(train_info.loc[m, '經由'])) == 2:
                        info += str(train_info.loc[m, '經由']) + '   '
                    else:
                        info += str(train_info.loc[m, '經由']) + '       '    
                    info += str(train_info.loc[m, '開車時間']) + '  ' + '停靠站：' + train_info.loc[m, '停靠站'] + '\n'
            info_list.append(info)
            """
                n = m
                if len(info) > 900:
                    sign = 1
                    break
                    return info, sign, n
            """

        except:
            for m in range(len(train_info)):
                if len(info) <= 900:
                    if len(str(train_info.loc[m, '車次'])) == 1:
                        info += str(train_info.loc[m, '車次']) + '    ' 
                    elif len(str(train_info.loc[m, '車次'])) == 2:
                        info += str(train_info.loc[m, '車次']) + '   ' 
                    elif len(str(train_info.loc[m, '車次'])) == 3:
                        info += str(train_info.loc[m, '車次']) + '  ' 
                    else:
                        info += str(train_info.loc[m, '車次']) + ' '

                    info += str(train_info.loc[m, '車種']) + ' '

                    if len(str(train_info.loc[m, '起站'])) == 2:
                        info += str(train_info.loc[m, '起站']) + '   ' 
                    elif len(str(train_info.loc[m, '起站'])) == 3:
                        info += str(train_info.loc[m, '起站']) + ' ' 

                    if len(str(train_info.loc[m, '終站'])) == 2:
                        info += str(train_info.loc[m, '終站']) + '   ' 
                    elif len(str(train_info.loc[m, '終站'])) == 3:
                        info += str(train_info.loc[m, '終站']) + ' '

                    if len(str(train_info.loc[m, '經由'])) == 3:
                        info += str(train_info.loc[m, '經由']) + ' ' 
                    elif len(str(train_info.loc[m, '經由'])) == 2:
                        info += str(train_info.loc[m, '經由']) + '   '
                    else:
                        info += str(train_info.loc[m, '經由']) + '       '    

                    info += str(train_info.loc[m, '開車時間']) + '  ' + '下一站：' + train_info.loc[m, '下一站'] + '\n'
                else:
                    info_list.append(info)
                    info = ''
                    if len(str(train_info.loc[m, '車次'])) == 1:
                        info += str(train_info.loc[m, '車次']) + '    ' 
                    elif len(str(train_info.loc[m, '車次'])) == 2:
                        info += str(train_info.loc[m, '車次']) + '   ' 
                    elif len(str(train_info.loc[m, '車次'])) == 3:
                        info += str(train_info.loc[m, '車次']) + '  ' 
                    else:
                        info += str(train_info.loc[m, '車次']) + ' '
                    info += str(train_info.loc[m, '車種']) + ' '
                    if len(str(train_info.loc[m, '起站'])) == 2:
                        info += str(train_info.loc[m, '起站']) + '   ' 
                    elif len(str(train_info.loc[m, '起站'])) == 3:
                        info += str(train_info.loc[m, '起站']) + ' ' 
                    if len(str(train_info.loc[m, '終站'])) == 2:
                        info += str(train_info.loc[m, '終站']) + '   ' 
                    elif len(str(train_info.loc[m, '終站'])) == 3:
                        info += str(train_info.loc[m, '終站']) + ' '
                    if len(str(train_info.loc[m, '經由'])) == 3:
                        info += str(train_info.loc[m, '經由']) + ' ' 
                    elif len(str(train_info.loc[m, '經由'])) == 2:
                        info += str(train_info.loc[m, '經由']) + '   '
                    else:
                        info += str(train_info.loc[m, '經由']) + '       '    
                    info += str(train_info.loc[m, '開車時間']) + '  ' + '下一站：' + train_info.loc[m, '下一站'] + '\n'
                    #n = m
            """
                    if len(info) > 900:
                        sign = 1
                        break
                        return info, sign, n
            """
    except:
        info = ('錯誤，請再試一次')
        info_list.append(info)
    return info_list#, sign, n

def tr_sta_time_direct(date, sta, direct):
    import pandas as pd
    from datetime import datetime
    pd.options.mode.chained_assignment = None
    day = date
    info = ''
    info_list = []
    try:
        day = str(day)
        option = 2
        if day == '20240212':
            original = pd.read_json('https://drive.google.com/uc?id=18sRcFpVWl_RdMtONk2qS3ZBfT2ZuMCto&export=download')
        elif day == '20240726':
            original = pd.read_json('https://drive.google.com/uc?id=1Rwd8tcXPCdVERSTKUotS7OC23PecTB8k&export=download')
        elif day == '20220402':
            original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/2ecc206ae6c06b2118ebeb80473774e897310e49/json%20format/20220402.json')
        elif day == '20240819':
            original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/83d998c9d9facb041ec1cc5573d2f887f81567b7/json%20format/20240819.json')
        elif day == '20240824':
            original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/440b8069abef3c17574e42ddda468941e38b3aa0/json%20format/20240824.json')
        elif day == '20240913':
            original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/b9242da565999d8093fe6bbb0f307b576c07b433/json%20format/20240913.json')
        elif int(day) >= 20241122:
            original = pd.read_json(f'https://raw.githubusercontent.com/Ricky1020/TR-timetable-json/refs/heads/main/{day}.json')
        else:
            original = pd.read_json(f'https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/master/json%20format/{day}.json')
        station = sta
        if '台' in station:
            station = station.replace('台', '臺')
        k = 0
        train_info = {}
        train_info = pd.DataFrame(train_info, index = [0])
        now = datetime.now()
        sta_info = pd.read_json('https://ods.railway.gov.tw/tra-ods-web/ods/download/dataResource/0518b833e8964d53bfea3f7691aea0ee')
        sta_list = {}
        for i in range(len(sta_info)):
            if sta_info['stationCode'][i] < 1000:
                code = '0' + str(sta_info['stationCode'][i])
            else:
                code = str(sta_info['stationCode'][i])
            name = sta_info['stationName'][i]
            sta_list[code] = name
        for i in range(len(original)):
            df_temp8 = pd.DataFrame(original['TrainInfos'][i])
            line = {'0':'','1':'山線','2':'海線','3':'成追線','4':'山線、海線'}
            for i in range(5):
                if df_temp8['Line'][0] == str(i):
                    via_line = line[str(i)]
                    break
            df_time3 = pd.DataFrame(df_temp8['TimeInfos'][0], index = [0])
            for j in range(1,len(df_temp8)):
                df_temp9 = pd.DataFrame(df_temp8['TimeInfos'][j], index = [j])
                df_time3 = pd.concat([df_time3,df_temp9])
            df_time3['站名'] = ''
            df_time3['到站時間'] = df_time3['ARRTime']
            df_time3['離站時間'] = df_time3['DEPTime']
            df_time3 = df_time3.drop(['Route','DEPTime','ARRTime'], axis = 'columns')
            for j in range(len(df_time3)):
                if str(df_time3['Station'][j]) in sta_list:
                    df_time3.loc[j, '站名'] = sta_list[str(df_time3.loc[j, 'Station'])]
            pd.options.mode.chained_assignment = None
            car_class_list = {'1100':'DR2800/DR2900/DR3000與EMU自強號','1101':'太魯閣號    ','1102':'PP自強號(自)','1103':'柴自強(障)  ','1104':'專列(自強)  ',
                    '1105':'郵輪式(自強)','1106':'商專列(自強)','1107':'普悠瑪號    ','1108':'PP自強號    ','1109':'PP自強號(親)',
                    '110A':'PP自強號(多)','110B':'EMU1200自強號','110C':'EMU300自強號','110D':'DR2800自強號','110E':'DR2900自強號','110F':'柴自強      ',
                    '110G':'自強3000   ','110H':'自強3000(親)','110K':'自強3000(特)','1110':'莒光號      ','1111':'莒光號(障)  ',
                    '1112':'專列(莒光)  ','1113':'郵輪式(莒光)','1114':'莒光號(自)','1115':'莒光號(自障)','1120':'復興號      ',
                    '1121':'專列(復興)  ','1122':'郵輪式(復興)','1130':'專列(電車)','1131':'區間車      ','1132':'區間快      ','1131':'區間車      ','1133':'郵輪式(電車)',
                    '1134':'專列(兩鐵)  ','1135':'區間車(自障)','1140':'普快車      ','1141':'柴快車','1150':'專列(普通車)','1151':'普通車',
                    '1152':'行包專車','1154':'專列(柴客)  ','1155':'郵輪式(柴客)'}
            for i in car_class_list:
                if df_temp8['CarClass'][0] == str(i):
                    car_class = car_class_list[str(i)]
                    break
            if int(df_temp8['Train'][0]) % 2 == direct:
                if df_time3['站名'].isin([station]).any():
                    df_temp9 = df_time3[df_time3['站名'].str.contains(station)]
                    ind4 = str(df_temp9.index)
                    ind4 = ind4.replace('Index([','')
                    ind4 = ind4.replace("], dtype='int64')",'')
                    try:
                        ind4 = int(ind4)
                    except:
                        ind_temp = ind4.split(',')
                        if int(df_temp8['Train'][0]) % 2 == 1: #逆行
                            if station == '臺中':
                                ind4 = int(ind_temp[1])
                            elif station == '烏日':
                                if via_line == '成追線':
                                    ind4 = int(ind_temp[1])
                                else:
                                    ind4 = int(ind_temp[0])
                            elif station == '左營':
                                ind4 = int(ind_temp[1])
                            elif station == '新竹':
                                ind4 = int(ind_temp[1])
                            else:
                                ind4 = int(ind_temp[0])
                        else:
                            if station == '烏日':
                                if via_line == '山線':
                                    ind4 = int(ind_temp[1])
                                else:
                                    ind4 = int(ind_temp[0])
                            elif station == '蘇澳':
                                ind4 = int(ind_temp[1])
                            elif station == '樹林':
                                ind4 = int(ind_temp[1])
                            else:
                                ind4 = int(ind_temp[0])

                    if station == df_time3['站名'][len(df_time3)-1]:
                        k += 1
                        time = now.strptime(df_time3['到站時間'][ind4], '%H:%M:%S')
                        time_str = str(time)
                        time_str = time_str.replace('1900-01-01 ','')
                        temp_info = {}
                        temp_info['車次'] = df_temp8['Train'][0]
                        temp_info['車種'] = car_class
                        temp_info['起站'] = df_time3['站名'][0]
                        if df_time3['站名'][len(df_time3)-1] == '臺北-環島':
                            temp_info['終站'] = '臺北'
                        else:
                            temp_info['終站'] = df_time3['站名'][len(df_time3)-1]
                        temp_info['經由'] = via_line
                        temp_info['站名'] = df_time3['站名'][ind4]
                        temp_info['開車時間1'] = time
                        temp_info['開車時間'] = time_str
                        temp_info['停靠站'] = '終點站'
                        temp_info = pd.DataFrame(temp_info, index = [k])
                        train_info = pd.concat([train_info,temp_info])
                    elif option == 2:
                        if car_class == '區間車      ':
                            if df_temp8['Train'].isin(['4514','4550','4552','4558','4556','4503','4513','4543']).any():
                                k += 1
                                time = now.strptime(df_time3['離站時間'][ind4], '%H:%M:%S')
                                time_str = str(time)
                                time_str = time_str.replace('1900-01-01 ','')
                                temp_info = {}
                                temp_info['車次'] = df_temp8['Train'][0]
                                temp_info['車種'] = car_class
                                temp_info['起站'] = df_time3['站名'][0]
                                if df_time3['站名'][len(df_time3)-1] == '臺北-環島':
                                    temp_info['終站'] = '臺北'
                                else:
                                    temp_info['終站'] = df_time3['站名'][len(df_time3)-1]
                                temp_info['經由'] = via_line
                                temp_info['站名'] = df_time3['站名'][ind4]
                                temp_info['開車時間1'] = time
                                temp_info['開車時間'] = time_str
                                temp1 = ''
                                m = 0
                                for j in range(ind4+1, len(df_time3)):
                                    m += 1
                                    temp1 += df_time3['站名'][j]+' '
                                temp_info['停靠站'] = temp1
                                temp_info = pd.DataFrame(temp_info, index = [k])
                                train_info = pd.concat([train_info,temp_info])
                            else:
                                k += 1
                                time = now.strptime(df_time3['離站時間'][ind4], '%H:%M:%S')
                                time_str = str(time)
                                time_str = time_str.replace('1900-01-01 ','')
                                temp_info = {}
                                temp_info['車次'] = df_temp8['Train'][0]
                                temp_info['車種'] = car_class
                                temp_info['起站'] = df_time3['站名'][0]
                                if df_time3['站名'][len(df_time3)-1] == '臺北-環島':
                                    temp_info['終站'] = '臺北'
                                else:
                                    temp_info['終站'] = df_time3['站名'][len(df_time3)-1]
                                temp_info['經由'] = via_line
                                temp_info['站名'] = df_time3['站名'][ind4]
                                temp_info['開車時間1'] = time
                                temp_info['開車時間'] = time_str
                                temp_info['停靠站'] = '下一站：'+df_time3['站名'][ind4+1]+'(中途各站皆停)'
                                temp_info = pd.DataFrame(temp_info, index = [k])
                                train_info = pd.concat([train_info,temp_info])
                        else:
                            k += 1
                            time = now.strptime(df_time3['離站時間'][ind4], '%H:%M:%S')
                            time_str = str(time)
                            time_str = time_str.replace('1900-01-01 ','')
                            temp_info = {}
                            temp_info['車次'] = df_temp8['Train'][0]
                            temp_info['車種'] = car_class
                            temp_info['起站'] = df_time3['站名'][0]
                            if df_time3['站名'][len(df_time3)-1] == '臺北-環島':
                                temp_info['終站'] = '臺北'
                            else:
                                temp_info['終站'] = df_time3['站名'][len(df_time3)-1]
                            temp_info['經由'] = via_line
                            temp_info['站名'] = df_time3['站名'][ind4]
                            temp_info['開車時間1'] = time
                            temp_info['開車時間'] = time_str
                            temp1 = ''
                            m = 0
                            for j in range(ind4+1, len(df_time3)):
                                m += 1
                                temp1 += df_time3['站名'][j]+' '
                            temp_info['停靠站'] = temp1
                            temp_info = pd.DataFrame(temp_info, index = [k])
                            train_info = pd.concat([train_info,temp_info])
                    
        train_info = train_info.dropna(axis = 0)
        train_info = train_info.sort_values(by = '開車時間1')
        train_info = train_info.drop(['開車時間1'], axis = 'columns')
        train_info = train_info.set_index('車次')
        train_info = train_info.reset_index()
        try:
            for m in range(len(train_info)):
                if len(info) <= 1700:
                    if len(str(train_info.loc[m, '車次'])) == 1:
                        info += str(train_info.loc[m, '車次']) + '    ' 
                    elif len(str(train_info.loc[m, '車次'])) == 2:
                        info += str(train_info.loc[m, '車次']) + '   ' 
                    elif len(str(train_info.loc[m, '車次'])) == 3:
                        info += str(train_info.loc[m, '車次']) + '  ' 
                    else:
                        info += str(train_info.loc[m, '車次']) + ' '

                    info += str(train_info.loc[m, '車種']) + ' '

                    if len(str(train_info.loc[m, '起站'])) == 2:
                        info += str(train_info.loc[m, '起站']) + '   ' 
                    elif len(str(train_info.loc[m, '起站'])) == 3:
                        info += str(train_info.loc[m, '起站']) + ' ' 

                    if len(str(train_info.loc[m, '終站'])) == 2:
                        info += str(train_info.loc[m, '終站']) + '   ' 
                    elif len(str(train_info.loc[m, '終站'])) == 3:
                        info += str(train_info.loc[m, '終站']) + ' '

                    if len(str(train_info.loc[m, '經由'])) == 3:
                        info += str(train_info.loc[m, '經由']) + ' ' 
                    elif len(str(train_info.loc[m, '經由'])) == 2:
                        info += str(train_info.loc[m, '經由']) + '   '
                    else:
                        info += str(train_info.loc[m, '經由']) + '       '    

                    info += str(train_info.loc[m, '開車時間']) + '  ' + '停靠站：' + train_info.loc[m, '停靠站'] + '\n'
                else:
                    info_list.append(info)
                    info = ''
                    if len(str(train_info.loc[m, '車次'])) == 1:
                        info += str(train_info.loc[m, '車次']) + '    ' 
                    elif len(str(train_info.loc[m, '車次'])) == 2:
                        info += str(train_info.loc[m, '車次']) + '   ' 
                    elif len(str(train_info.loc[m, '車次'])) == 3:
                        info += str(train_info.loc[m, '車次']) + '  ' 
                    else:
                        info += str(train_info.loc[m, '車次']) + ' '
                    info += str(train_info.loc[m, '車種']) + ' '
                    if len(str(train_info.loc[m, '起站'])) == 2:
                        info += str(train_info.loc[m, '起站']) + '   ' 
                    elif len(str(train_info.loc[m, '起站'])) == 3:
                        info += str(train_info.loc[m, '起站']) + ' ' 
                    if len(str(train_info.loc[m, '終站'])) == 2:
                        info += str(train_info.loc[m, '終站']) + '   ' 
                    elif len(str(train_info.loc[m, '終站'])) == 3:
                        info += str(train_info.loc[m, '終站']) + ' '
                    if len(str(train_info.loc[m, '經由'])) == 3:
                        info += str(train_info.loc[m, '經由']) + ' ' 
                    elif len(str(train_info.loc[m, '經由'])) == 2:
                        info += str(train_info.loc[m, '經由']) + '   '
                    else:
                        info += str(train_info.loc[m, '經由']) + '       '    
                    info += str(train_info.loc[m, '開車時間']) + '  ' + '停靠站：' + train_info.loc[m, '停靠站'] + '\n'
            info_list.append(info)

        except:
            for m in range(len(train_info)):
                if len(info) <= 900:
                    if len(str(train_info.loc[m, '車次'])) == 1:
                        info += str(train_info.loc[m, '車次']) + '    ' 
                    elif len(str(train_info.loc[m, '車次'])) == 2:
                        info += str(train_info.loc[m, '車次']) + '   ' 
                    elif len(str(train_info.loc[m, '車次'])) == 3:
                        info += str(train_info.loc[m, '車次']) + '  ' 
                    else:
                        info += str(train_info.loc[m, '車次']) + ' '

                    info += str(train_info.loc[m, '車種']) + ' '

                    if len(str(train_info.loc[m, '起站'])) == 2:
                        info += str(train_info.loc[m, '起站']) + '   ' 
                    elif len(str(train_info.loc[m, '起站'])) == 3:
                        info += str(train_info.loc[m, '起站']) + ' ' 

                    if len(str(train_info.loc[m, '終站'])) == 2:
                        info += str(train_info.loc[m, '終站']) + '   ' 
                    elif len(str(train_info.loc[m, '終站'])) == 3:
                        info += str(train_info.loc[m, '終站']) + ' '

                    if len(str(train_info.loc[m, '經由'])) == 3:
                        info += str(train_info.loc[m, '經由']) + ' ' 
                    elif len(str(train_info.loc[m, '經由'])) == 2:
                        info += str(train_info.loc[m, '經由']) + '   '
                    else:
                        info += str(train_info.loc[m, '經由']) + '       '    

                    info += str(train_info.loc[m, '開車時間']) + '  ' + '下一站：' + train_info.loc[m, '下一站'] + '\n'
                else:
                    info_list.append(info)
                    info = ''
                    if len(str(train_info.loc[m, '車次'])) == 1:
                        info += str(train_info.loc[m, '車次']) + '    ' 
                    elif len(str(train_info.loc[m, '車次'])) == 2:
                        info += str(train_info.loc[m, '車次']) + '   ' 
                    elif len(str(train_info.loc[m, '車次'])) == 3:
                        info += str(train_info.loc[m, '車次']) + '  ' 
                    else:
                        info += str(train_info.loc[m, '車次']) + ' '
                    info += str(train_info.loc[m, '車種']) + ' '
                    if len(str(train_info.loc[m, '起站'])) == 2:
                        info += str(train_info.loc[m, '起站']) + '   ' 
                    elif len(str(train_info.loc[m, '起站'])) == 3:
                        info += str(train_info.loc[m, '起站']) + ' ' 
                    if len(str(train_info.loc[m, '終站'])) == 2:
                        info += str(train_info.loc[m, '終站']) + '   ' 
                    elif len(str(train_info.loc[m, '終站'])) == 3:
                        info += str(train_info.loc[m, '終站']) + ' '
                    if len(str(train_info.loc[m, '經由'])) == 3:
                        info += str(train_info.loc[m, '經由']) + ' ' 
                    elif len(str(train_info.loc[m, '經由'])) == 2:
                        info += str(train_info.loc[m, '經由']) + '   '
                    else:
                        info += str(train_info.loc[m, '經由']) + '       '    
                    info += str(train_info.loc[m, '開車時間']) + '  ' + '下一站：' + train_info.loc[m, '下一站'] + '\n'
    except:
        info = ('錯誤，請再試一次')
        info_list.append(info)
    return info_list

"""
def tr_sta_time_c(date, sta, c):
    import pandas as pd
    from datetime import datetime
    pd.options.mode.chained_assignment = None
    day = date
    info = ''
    sign = 0 
    n = c
    try:
        day = str(day)
        option = 2
        if day == '20240212':
            original = pd.read_json('https://drive.google.com/uc?id=18sRcFpVWl_RdMtONk2qS3ZBfT2ZuMCto&export=download')
        elif day == '20240726':
            original = pd.read_json('https://drive.google.com/uc?id=1Rwd8tcXPCdVERSTKUotS7OC23PecTB8k&export=download')
        elif day == '20220402':
            original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/2ecc206ae6c06b2118ebeb80473774e897310e49/json%20format/20220402.json')
        elif day == '20240819':
            original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/83d998c9d9facb041ec1cc5573d2f887f81567b7/json%20format/20240819.json')
        elif day == '20240824':
            original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/440b8069abef3c17574e42ddda468941e38b3aa0/json%20format/20240824.json')
        else:
            original = pd.read_json(f'https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/master/json%20format/{day}.json')
        station = sta
        if '台' in station:
            station = station.replace('台', '臺')
        k = 0
        train_info = {}
        train_info = pd.DataFrame(train_info, index = [0])
        now = datetime.now()
        sta_info = pd.read_json('https://ods.railway.gov.tw/tra-ods-web/ods/download/dataResource/0518b833e8964d53bfea3f7691aea0ee')
        sta_list = {}
        for i in range(len(sta_info)):
            if sta_info['stationCode'][i] < 1000:
                code = '0' + str(sta_info['stationCode'][i])
            else:
                code = str(sta_info['stationCode'][i])
            name = sta_info['stationName'][i]
            sta_list[code] = name
        for i in range(len(original)):
            df_temp8 = pd.DataFrame(original['TrainInfos'][i])
            line = {'0':'','1':'山線','2':'海線','3':'成追線','4':'山線、海線'}
            for i in range(5):
                if df_temp8['Line'][0] == str(i):
                    via_line = line[str(i)]
                    break
            df_time3 = pd.DataFrame(df_temp8['TimeInfos'][0], index = [0])
            for j in range(1,len(df_temp8)):
                df_temp9 = pd.DataFrame(df_temp8['TimeInfos'][j], index = [j])
                df_time3 = pd.concat([df_time3,df_temp9])
            df_time3['站名'] = ''
            df_time3['到站時間'] = df_time3['ARRTime']
            df_time3['離站時間'] = df_time3['DEPTime']
            df_time3 = df_time3.drop(['Route','DEPTime','ARRTime'], axis = 'columns')
            for j in range(len(df_time3)):
                if str(df_time3['Station'][j]) in sta_list:
                    df_time3.loc[j, '站名'] = sta_list[str(df_time3.loc[j, 'Station'])]
            pd.options.mode.chained_assignment = None
            car_class_list = {'1100':'DR2800/DR2900/DR3000與EMU自強號','1101':'太魯閣號    ','1102':'PP自強號(自)','1103':'柴自強(障)  ','1104':'專列(自強)  ',
                    '1105':'郵輪式(自強)','1106':'商專列(自強)','1107':'普悠瑪號    ','1108':'PP自強號    ','1109':'PP自強號(親)',
                    '110A':'PP自強號(多)','110B':'EMU1200自強號','110C':'EMU300自強號','110D':'DR2800自強號','110E':'DR2900自強號','110F':'柴自強      ',
                    '110G':'自強3000   ','110H':'自強3000(親)','110K':'自強3000(特)','1110':'莒光號      ','1111':'莒光號(障)  ',
                    '1112':'專列(莒光)  ','1113':'郵輪式(莒光)','1114':'莒光號(自)','1115':'莒光號(自障)','1120':'復興號      ',
                    '1121':'專列(復興)  ','1122':'郵輪式(復興)','1130':'專列(電車)','1131':'區間車      ','1132':'區間快      ','1131':'區間車      ','1133':'郵輪式(電車)',
                    '1134':'專列(兩鐵)  ','1135':'區間車(自障)','1140':'普快車      ','1141':'柴快車','1150':'專列(普通車)','1151':'普通車',
                    '1152':'行包專車','1154':'專列(柴客)','1155':'郵輪式(柴客)'}
            for i in car_class_list:
                if df_temp8['CarClass'][0] == str(i):
                    car_class = car_class_list[str(i)]
                    break
            if df_time3['站名'].isin([station]).any():
                df_temp9 = df_time3[df_time3['站名'].str.contains(station)]
                ind4 = str(df_temp9.index)
                ind4 = ind4.replace('Index([','')
                ind4 = ind4.replace("], dtype='int64')",'')
                try:
                    ind4 = int(ind4)
                except:
                    ind_temp = ind4.split(',')
                    if int(df_temp8['Train'][0]) % 2 == 1: #逆行
                        if station == '臺中':
                            ind4 = int(ind_temp[1])
                        elif station == '烏日':
                            if via_line == '成追線':
                                ind4 = int(ind_temp[1])
                            else:
                                ind4 = int(ind_temp[0])
                        elif station == '左營':
                            ind4 = int(ind_temp[1])
                        elif station == '新竹':
                            ind4 = int(ind_temp[1])
                        else:
                            ind4 = int(ind_temp[0])
                    else:
                        if station == '烏日':
                            if via_line == '山線':
                                ind4 = int(ind_temp[1])
                            else:
                                ind4 = int(ind_temp[0])
                        elif station == '蘇澳':
                            ind4 = int(ind_temp[1])
                        elif station == '樹林':
                            ind4 = int(ind_temp[1])
                        else:
                            ind4 = int(ind_temp[0])

                #time = now.strptime(df_time3['離站時間'][ind4], '%H:%M:%S')
                #time_str = str(time)
                #time_str = time_str.replace('1900-01-01 ','')
                if station == df_time3['站名'][len(df_time3)-1]:
                    k += 1
                    time = now.strptime(df_time3['到站時間'][ind4], '%H:%M:%S')
                    time_str = str(time)
                    time_str = time_str.replace('1900-01-01 ','')
                    temp_info = {}
                    temp_info['車次'] = df_temp8['Train'][0]
                    temp_info['車種'] = car_class
                    temp_info['起站'] = df_time3['站名'][0]
                    if df_time3['站名'][len(df_time3)-1] == '臺北-環島':
                        temp_info['終站'] = '臺北'
                    else:
                        temp_info['終站'] = df_time3['站名'][len(df_time3)-1]
                    temp_info['經由'] = via_line
                    temp_info['站名'] = df_time3['站名'][ind4]
                    temp_info['開車時間1'] = time
                    temp_info['開車時間'] = time_str
                    #temp_info['抵達時間1'] = time
                    #temp_info['抵達時間'] = time_str
                    temp_info['停靠站'] = '終點站'
                    temp_info = pd.DataFrame(temp_info, index = [k])
                    train_info = pd.concat([train_info,temp_info])
                elif option == 2:
                    if car_class == '區間車      ':
                        if df_temp8['Train'].isin(['4514','4550','4552','4558','4556','4503','4513','4543']).any():
                            k += 1
                            time = now.strptime(df_time3['離站時間'][ind4], '%H:%M:%S')
                            time_str = str(time)
                            time_str = time_str.replace('1900-01-01 ','')
                            temp_info = {}
                            temp_info['車次'] = df_temp8['Train'][0]
                            temp_info['車種'] = car_class
                            temp_info['起站'] = df_time3['站名'][0]
                            if df_time3['站名'][len(df_time3)-1] == '臺北-環島':
                                temp_info['終站'] = '臺北'
                            else:
                                temp_info['終站'] = df_time3['站名'][len(df_time3)-1]
                            temp_info['經由'] = via_line
                            temp_info['站名'] = df_time3['站名'][ind4]
                            temp_info['開車時間1'] = time
                            temp_info['開車時間'] = time_str
                            temp1 = ''
                            m = 0
                            for j in range(ind4+1, len(df_time3)):
                                m += 1
                                temp1 += df_time3['站名'][j]+' '
                            temp_info['停靠站'] = temp1
                            temp_info = pd.DataFrame(temp_info, index = [k])
                            train_info = pd.concat([train_info,temp_info])
                        else:
                            k += 1
                            time = now.strptime(df_time3['離站時間'][ind4], '%H:%M:%S')
                            time_str = str(time)
                            time_str = time_str.replace('1900-01-01 ','')
                            temp_info = {}
                            temp_info['車次'] = df_temp8['Train'][0]
                            temp_info['車種'] = car_class
                            temp_info['起站'] = df_time3['站名'][0]
                            if df_time3['站名'][len(df_time3)-1] == '臺北-環島':
                                temp_info['終站'] = '臺北'
                            else:
                                temp_info['終站'] = df_time3['站名'][len(df_time3)-1]
                            temp_info['經由'] = via_line
                            temp_info['站名'] = df_time3['站名'][ind4]
                            temp_info['開車時間1'] = time
                            temp_info['開車時間'] = time_str
                            temp_info['停靠站'] = '下一站：'+df_time3['站名'][ind4+1]+'(中途各站皆停)'
                            temp_info = pd.DataFrame(temp_info, index = [k])
                            train_info = pd.concat([train_info,temp_info])
                    else:
                        k += 1
                        time = now.strptime(df_time3['離站時間'][ind4], '%H:%M:%S')
                        time_str = str(time)
                        time_str = time_str.replace('1900-01-01 ','')
                        temp_info = {}
                        temp_info['車次'] = df_temp8['Train'][0]
                        temp_info['車種'] = car_class
                        temp_info['起站'] = df_time3['站名'][0]
                        if df_time3['站名'][len(df_time3)-1] == '臺北-環島':
                            temp_info['終站'] = '臺北'
                        else:
                            temp_info['終站'] = df_time3['站名'][len(df_time3)-1]
                        temp_info['經由'] = via_line
                        temp_info['站名'] = df_time3['站名'][ind4]
                        temp_info['開車時間1'] = time
                        temp_info['開車時間'] = time_str
                        temp1 = ''
                        m = 0
                        for j in range(ind4+1, len(df_time3)):
                            m += 1
                            temp1 += df_time3['站名'][j]+' '
                        temp_info['停靠站'] = temp1
                        temp_info = pd.DataFrame(temp_info, index = [k])
                        train_info = pd.concat([train_info,temp_info])
                        #if m >= 1:
                            #print(temp_info['車次'][k], temp_info['車種'][k], '往'+temp_info['終站'][k], temp_info['開車時間'][k], '停靠站：'+temp_info['停靠站'][k])
                
        train_info = train_info.dropna(axis = 0)
        train_info = train_info.sort_values(by = '開車時間1')
        train_info = train_info.drop(['開車時間1'], axis = 'columns')
        train_info = train_info.set_index('車次')
        train_info = train_info.reset_index()
        try:
            for m in range(n+1, len(train_info)):
                if len(str(train_info.loc[m, '車次'])) == 1:
                    info += str(train_info.loc[m, '車次']) + '    ' 
                elif len(str(train_info.loc[m, '車次'])) == 2:
                    info += str(train_info.loc[m, '車次']) + '   ' 
                elif len(str(train_info.loc[m, '車次'])) == 3:
                    info += str(train_info.loc[m, '車次']) + '  ' 
                else:
                    info += str(train_info.loc[m, '車次']) + ' '

                info += str(train_info.loc[m, '車種']) + ' '

                if len(str(train_info.loc[m, '起站'])) == 2:
                    info += str(train_info.loc[m, '起站']) + '   ' 
                elif len(str(train_info.loc[m, '起站'])) == 3:
                    info += str(train_info.loc[m, '起站']) + ' ' 

                if len(str(train_info.loc[m, '終站'])) == 2:
                    info += str(train_info.loc[m, '終站']) + '   ' 
                elif len(str(train_info.loc[m, '終站'])) == 3:
                    info += str(train_info.loc[m, '終站']) + ' '

                if len(str(train_info.loc[m, '經由'])) == 3:
                    info += str(train_info.loc[m, '經由']) + ' ' 
                elif len(str(train_info.loc[m, '經由'])) == 2:
                    info += str(train_info.loc[m, '經由']) + '   '
                else:
                    info += str(train_info.loc[m, '經由']) + '       '    

                info += str(train_info.loc[m, '開車時間']) + '  ' + train_info.loc[m, '停靠站'] + '\n'
                n = m
                if len(info) > 900:
                    sign = 1
                    break
                    return info, sign, n

        except:
                for m in range(n+1, len(train_info)):
                    if len(str(train_info.loc[m, '車次'])) == 1:
                        info += str(train_info.loc[m, '車次']) + '    ' 
                    elif len(str(train_info.loc[m, '車次'])) == 2:
                        info += str(train_info.loc[m, '車次']) + '   ' 
                    elif len(str(train_info.loc[m, '車次'])) == 3:
                        info += str(train_info.loc[m, '車次']) + '  ' 
                    else:
                        info += str(train_info.loc[m, '車次']) + ' '

                    info += str(train_info.loc[m, '車種']) + ' '

                    if len(str(train_info.loc[m, '起站'])) == 2:
                        info += str(train_info.loc[m, '起站']) + '   ' 
                    elif len(str(train_info.loc[m, '起站'])) == 3:
                        info += str(train_info.loc[m, '起站']) + ' ' 

                    if len(str(train_info.loc[m, '終站'])) == 2:
                        info += str(train_info.loc[m, '終站']) + '   ' 
                    elif len(str(train_info.loc[m, '終站'])) == 3:
                        info += str(train_info.loc[m, '終站']) + ' '

                    if len(str(train_info.loc[m, '經由'])) == 3:
                        info += str(train_info.loc[m, '經由']) + ' ' 
                    elif len(str(train_info.loc[m, '經由'])) == 2:
                        info += str(train_info.loc[m, '經由']) + '   '
                    else:
                        info += str(train_info.loc[m, '經由']) + '       '    

                    info += str(train_info.loc[m, '開車時間']) + '  ' + '下一站：' + train_info.loc[m, '下一站'] + '\n'
                    n = m
                    if len(info) > 900:
                        sign = 1
                        break
                        return info, sign, n
    except:
        info = ('錯誤，請再試一次')
    return info, sign, n
"""
def weather(city):
    import pandas as pd
    weather1 = pd.read_json('https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0003-001?Authorization=rdec-key-123-45678-011121314&format=JSON')
    weather2 = pd.read_json('https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0001-001?Authorization=rdec-key-123-45678-011121314&format=JSON')
    rain1 = pd.read_json('https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0002-001?Authorization=rdec-key-123-45678-011121314&format=JSON')


    weather1a = pd.DataFrame(weather1['cwaopendata']['dataset'])
    weather1b = pd.DataFrame(weather1a['Station'][0]['WeatherElement'], index = [0]) #把'TimeInfos'欄位變成DataFrame(要加index)
    weather1b['站點'] = weather1a['Station'][0]['StationName']
    weather1b['縣市1'] = weather1a['Station'][0]['GeoInfo']['CountyName']
    weather1b['鄉鎮市區1'] = weather1a['Station'][0]['GeoInfo']['TownName']
    time = weather1a['Station'][0]['ObsTime']['DateTime']
    #time = time[11:19]
    weather1b['時間1'] = weather1a['Station'][0]['ObsTime']['DateTime']
    #weather1b['時間'] = weather1a['Station'][0]['ObsTime']
    pd.options.mode.chained_assignment = None
    for i in range(1,len(weather1a)):
        df_temp = pd.DataFrame(weather1a['Station'][i]['WeatherElement'], index = [i])
        weather1b = pd.concat([weather1b,df_temp]) #合併DataFrame
        weather1b.loc[i, '站點'] = weather1a['Station'][i]['StationName']
        weather1b.loc[i, '縣市1'] = weather1a['Station'][i]['GeoInfo']['CountyName']
        weather1b.loc[i, '鄉鎮市區1'] = weather1a['Station'][i]['GeoInfo']['TownName']
        time = weather1a['Station'][i]['ObsTime']['DateTime']
        time = time[:4] + '/'+ time[5:7] + '/' + time[8:10] + ' ' + time[11:19]
        weather1b['時間1'] = time #weather1a['Station'][i]['ObsTime']['DateTime']
    #weather1b = weather1b.set_index('站點')
    weather1b = weather1b.dropna(axis = 'columns')
    weather1b = weather1b.rename(columns = {'Weather':'天氣', 'VisibilityDescription':'可見度(km)','SunshineDuration':'日照時數',
    'WindDirection':'風向','WindSpeed':'風速','AirTemperature':'氣溫','RelativeHumidity':'相對溼度(%)','AirPressure':'氣壓','UVIndex':'紫外線指數'})


    weather2a = pd.DataFrame(weather2['cwaopendata']['dataset'])
    weather2b = pd.DataFrame(weather2a['Station'][0]['WeatherElement'], index = [0]) #把'TimeInfos'欄位變成DataFrame(要加index)
    weather2b['站點'] = weather2a['Station'][0]['StationName']
    weather2b['縣市1'] = weather2a['Station'][0]['GeoInfo']['CountyName']
    weather2b['鄉鎮市區1'] = weather2a['Station'][0]['GeoInfo']['TownName']
    time = weather2a['Station'][0]['ObsTime']['DateTime']
    #time = time[11:19]
    weather2b['時間1'] = weather2a['Station'][0]['ObsTime']['DateTime']
    #weather2b['時間'] = weather2a['Station'][0]['ObsTime']
    pd.options.mode.chained_assignment = None
    for i in range(1,len(weather2a)):
        df_temp = pd.DataFrame(weather2a['Station'][i]['WeatherElement'], index = [i])
        weather2b = pd.concat([weather2b,df_temp]) #合併DataFrame
        weather2b.loc[i, '站點'] = weather2a['Station'][i]['StationName']
        weather2b.loc[i, '縣市1'] = weather2a['Station'][i]['GeoInfo']['CountyName']
        weather2b.loc[i, '鄉鎮市區1'] = weather2a['Station'][i]['GeoInfo']['TownName']
        time = weather2a['Station'][i]['ObsTime']['DateTime']
        time = time[:4] + '/'+ time[5:7] + '/' + time[8:10] + ' ' + time[11:19]
    weather2b['時間1'] = time #weather2a['Station'][i]['ObsTime']['DateTime']
    #weather2b = weather2b.set_index('站點')
    weather2b = weather2b.dropna(axis = 'columns')
    weather2b = weather2b.rename(columns = {'Weather':'天氣', 'VisibilityDescription':'可見度(km)','SunshineDuration':'日照時數',
    'WindDirection':'風向','WindSpeed':'風速','AirTemperature':'氣溫','RelativeHumidity':'相對溼度(%)','AirPressure':'氣壓','UVIndex':'紫外線指數'})


    rain1a = pd.DataFrame(rain1['cwaopendata']['dataset'])
    rain1b = pd.DataFrame(rain1a['Station'][0]['RainfallElement'], index = [0]) #把'TimeInfos'欄位變成DataFrame(要加index)
    column = rain1b.columns
    for i in column:
        rain1b.loc[0, i] = float(rain1a['Station'][0]['RainfallElement'][i]['Precipitation'])
    rain1b['站點'] = rain1a['Station'][0]['StationName']
    rain1b['縣市1'] = rain1a['Station'][0]['GeoInfo']['CountyName']
    rain1b['鄉鎮市區1'] = rain1a['Station'][0]['GeoInfo']['TownName']
    #rain1b['時間'] = rain1a['Station'][0]['ObsTime']
    pd.options.mode.chained_assignment = None
    for i in range(1,len(rain1a)):
        df_temp = pd.DataFrame(rain1a['Station'][i]['RainfallElement'], index = [i])
        for j in column:
            df_temp.loc[i, j] = float(rain1a['Station'][i]['RainfallElement'][j]['Precipitation'])
        rain1b = pd.concat([rain1b,df_temp]) #合併DataFrame
        rain1b.loc[i, '站點'] = rain1a['Station'][i]['StationName']
        rain1b.loc[i, '縣市1'] = rain1a['Station'][i]['GeoInfo']['CountyName']
        rain1b.loc[i, '鄉鎮市區1'] = rain1a['Station'][i]['GeoInfo']['TownName']
    rain1c = rain1b.drop(['Past10Min','Past1hr','Past3hr','Past6hr','Past12hr','Past24hr','Past2days','Past3days','縣市1','鄉鎮市區1'], axis = 'columns')
    rain1c = rain1c.rename(columns = {'Now':'累積雨量(mm)'})


    weather3 = pd.concat([weather1b,weather2b]) #合併DataFrame
    weather3 = weather3.set_index('站點')
    weather3 = weather3.reset_index()
    column = weather3.columns
    for i in range(len(weather3)):
        for j in column:
            if ('-99' in str(weather3[j][i])) or ('nan' in str(weather3[j][i])):
                weather3.loc[i, j] = '-'
    #weather3 = weather3.set_index('站點')

    weather4 = pd.merge(weather3, rain1c, how = 'left', left_on = '站點', right_on = '站點')
    weather4 = weather4.set_index('站點')
    weather4 = weather4.reset_index()
    weather4['縣市'] = ''
    weather4['鄉鎮市區'] = ''
    weather4['時間'] = ''
    for i in range(len(weather4)):
        weather4.loc[i, '縣市'] = weather4.loc[i, '縣市1']
        weather4.loc[i, '鄉鎮市區'] = weather4.loc[i, '鄉鎮市區1']
        weather4.loc[i, '時間'] = weather4.loc[i, '時間1']
    weather4 = weather4.drop(['縣市1','鄉鎮市區1','時間1'], axis = 'columns')
    column = weather4.columns
    for i in range(len(weather4)):
        for j in column:
            if ('-99' in str(weather4[j][i])) or ('nan' in str(weather4[j][i])):
                weather4.loc[i, j] = '-'

    if '台' in city:
        city = city.replace('台', '臺')
    filter = weather4['縣市'].str.contains(city)
    df_weather = weather4[filter]
    df_weather = df_weather.set_index('站點')
    df_weather = df_weather.reset_index()
    info = ''
    for i in range(len(df_weather)):
        sta = df_weather['站點'][i]
        weather5 = df_weather['天氣'][i]
        temperature = df_weather['氣溫'][i]
        rain = df_weather['累積雨量(mm)'][i]
        #windspeed = df_weather['風速'][i]
        info += str(sta) + ' ' + str(weather5) + ' ' + str(temperature) + ' ' + str(rain) + '\n'
    return info

def C(n,k):
    a=1
    b=1
    for i in range(n,n-k,-1):
        a=a*i
    for j in range(1,k+1):
        b=b*j
    a=a//b
    return a

def P(n,k):
    a=1
    for i in range(n,n-k,-1):
        a=a*i
    return a

def seat(day, train_no, car, seat_no):
    import pandas as pd
    try:
        if day == 20240819:
            original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/83d998c9d9facb041ec1cc5573d2f887f81567b7/json%20format/20240819.json')
        elif day == 20240726:
            original = pd.read_json('https://drive.google.com/uc?id=1Rwd8tcXPCdVERSTKUotS7OC23PecTB8k&export=download')
        elif day == 20220402:
            original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/2ecc206ae6c06b2118ebeb80473774e897310e49/json%20format/20220402.json')
        elif day == 20240824:
            original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/440b8069abef3c17574e42ddda468941e38b3aa0/json%20format/20240824.json')
        elif day == 20240913:
            original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/b9242da565999d8093fe6bbb0f307b576c07b433/json%20format/20240913.json')
        elif int(day) >= 20241122:
            original = pd.read_json(f'https://raw.githubusercontent.com/Ricky1020/TR-timetable-json/refs/heads/main/{day}.json')
        else:
            original = pd.read_json(f'https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/master/json%20format/{day}.json') #爬蟲
        df_copy = original
        for i in range(len(original)):
            df_copy.loc[i, 'TrainInfos'] = str(df_copy['TrainInfos'][i])
        df_temp = df_copy[df_copy['TrainInfos'].str.contains(f"'Train': '{train_no}'")]
        ind = str(df_temp.index)
        ind = ind.replace('Index([','')
        ind = ind.replace("], dtype='int64')",'')
        ind = int(ind)
        if day == 20240819:
            original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/83d998c9d9facb041ec1cc5573d2f887f81567b7/json%20format/20240819.json')
        elif day == 20240726:
            original = pd.read_json('https://drive.google.com/uc?id=1Rwd8tcXPCdVERSTKUotS7OC23PecTB8k&export=download')
        elif day == 20220402:
            original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/2ecc206ae6c06b2118ebeb80473774e897310e49/json%20format/20220402.json')
        elif day == 20240824:
            original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/440b8069abef3c17574e42ddda468941e38b3aa0/json%20format/20240824.json')
        elif day == 20240913:
            original = pd.read_json('https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/b9242da565999d8093fe6bbb0f307b576c07b433/json%20format/20240913.json')
        elif int(day) >= 20241122:
            original = pd.read_json(f'https://raw.githubusercontent.com/Ricky1020/TR-timetable-json/refs/heads/main/{day}.json')
        else:
            original = pd.read_json(f'https://raw.githubusercontent.com/Taiwan-Railway-Route-Planner/TRAOriginalTimeTable/master/json%20format/{day}.json') #爬蟲
        df_temp2 = pd.DataFrame(original['TrainInfos'][ind])
        sea_mt = ''
        window_aisle = ''
        table = ''
        PPT1000 = ' '
        PPT2000 = ' '
        info = ''
        if (seat_no % 4 == 1) or (seat_no % 4 == 2):
            window_aisle = '靠窗'
        else:
            window_aisle = '靠走道'
        if df_temp2['CarClass'][0] == '1103' or df_temp2['CarClass'][0] == '110F': #DR3100
            if (((car % 3 != 0) and (seat_no % 2 == 0)) or ((car % 3 == 0) and (seat_no % 2 == 1))):
                sea_mt = '靠海'
            else:
                sea_mt = '靠山'
        elif df_temp2['CarClass'][0] == '1101': #TEMU1000
            if (((car <= 4) and (seat_no % 2 == 0)) or ((car > 4) and (seat_no % 2 == 1))):
                sea_mt = '靠海'
            else:
                sea_mt = '靠山'
        elif df_temp2['CarClass'][0] == '1107': #TEMU2000
            if (((car <= 4) and (seat_no % 2 == 0)) or ((car > 4) and (seat_no % 2 == 1))):
                sea_mt = '靠海'
            else:
                sea_mt = '靠山'
            if (((car==4) | (car==5)) & (seat_no>=22) & (((28-seat_no)%2==0) | ((35-seat_no)%2==0) | ((42-seat_no)%2==0) | ((51-seat_no)%2==0))):
                table = '桌型座'
        elif df_temp2['CarClass'][0] == '110G' or df_temp2['CarClass'][0] == '110H' or df_temp2['CarClass'][0] == '110K': #EMU3000
            if (((car <= 8) and (seat_no % 2 == 0)) or ((car > 8) and (seat_no % 2 == 1))):
                sea_mt = '靠海'
            else:
                sea_mt = '靠山'
        elif df_temp2['CarClass'][0] == '1102' or df_temp2['CarClass'][0] == '1108' or df_temp2['CarClass'][0] == '1109' or df_temp2['CarClass'][0] == '110A': #PP
            if (car == 1 | car == 7) & (seat_no % 2 == 1):
                sea_mt = '靠海'
            elif (car == 3 | car == 8) & (seat_no % 2 == 0):
                sea_mt = '靠海'
            elif (car == 2 or car == 4 or car == 5 or car == 6 or car == 9 or car == 10 or car == 11):
                if (seat_no % 2 == 0):
                    sea_mt = '靠海'
                    PPT1000 = ' PPT1000:'
                    PPT2000 = ' PPT2000:靠山'
                else:
                    sea_mt = '靠山'
                    PPT1000 = ' PPT1000:'
                    PPT2000 = ' PPT2000:靠海'
            else:
                sea_mt = '靠山'
        elif df_temp2['CarClass'][0] == '1110' or df_temp2['CarClass'][0] == '1111' or df_temp2['CarClass'][0] == '1114' or df_temp2['CarClass'][0] == '1115' or df_temp2['CarClass'][0] == '1112': #莒光
            if car == 1:
                if seat_no == 4:
                    window_aisle = '靠走道(FPK11500、FPK11600:靠窗)'
                    sea_mt = '靠山'
                elif seat_no == 3:
                    sea_mt = '靠海(FPK11500、FPK11600:靠山)'
                elif seat_no % 2 == 1:
                    sea_mt = '靠海'
                else:
                    sea_mt = '靠山'
            elif (seat_no % 2 == 1):
                sea_mt = '靠海'
            else:
                sea_mt = '靠山'
        else:
            info = '輸入錯誤'
        info = f'{day} 第 {train_no} 次 \n{car} 車 {seat_no} 號 {window_aisle}{PPT1000}{sea_mt}{PPT2000}{table}'
    except:
        info = '日期輸入錯誤'
    return info

def wide_earthquake():
    earthquake_data = pd.read_json('https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/E-A0015-005?Authorization=rdec-key-123-45678-011121314&downloadType=WEB&format=JSON')
    earthquake1 = pd.DataFrame(earthquake_data['cwaopendata']['Earthquake'])
    earthquake2 = pd.DataFrame(earthquake1['Intensity']['County'])
    info_list = [] 
    info = earthquake1['OriginTime']['MagnitudeValue'][:19] + ' ' + earthquake1['Description']['MagnitudeValue'][11:21]
    info = info.replace('T', ' ')
    info += '\n震央位於東經 ' + earthquake1['EpicenterLongitude']['MagnitudeValue'] + ' 度，北緯 ' + earthquake1['EpicenterLatitude']['MagnitudeValue'] + ' 度'
    info += '\n芮氏規模 ' + earthquake1['Magnitude']['MagnitudeValue'] + '\n震源深度 ' + earthquake1['FocalDepth']['MagnitudeValue'] + ' 公里'
    #print(info)
    earthquake3 = pd.DataFrame(earthquake2['Town'][0])
    earthquake3['縣市'] = earthquake2['CountyName'][0]
    for i in range(1,len(earthquake2)):
        earthquake4 = pd.DataFrame(earthquake2['Town'][i]) 
        earthquake4['縣市'] = earthquake2['CountyName'][i]
        earthquake3 = pd.concat([earthquake3,earthquake4])
    earthquake3 = earthquake3.rename(columns = {'StationIntensity':'震度','TownName':'行政區'})
    earthquake3 = earthquake3.drop(['TownCode'], axis = 'columns')
    earthquake3 = earthquake3.sort_values(by = '震度')[::-1]
    filter = (earthquake3['震度'] != '0級')
    earthquake5 = earthquake3[filter].set_index('縣市')
    earthquake5 = earthquake5.reset_index()
    info += '\n \n 縣市  行政區 震度 縣市  行政區 震度'
    for i in range(0, len(earthquake5)-1, 2):
        if len(info) <= 970:
            info += '\n' + earthquake5['縣市'][i] + ' ' + earthquake5['行政區'][i] + ' ' + earthquake5['震度'][i] + ' ' + earthquake5['縣市'][i+1] + ' ' + earthquake5['行政區'][i+1] + ' ' +  earthquake5['震度'][i+1]
        else:
            info_list.append(info)
            info = ''
            info += '\n' + earthquake5['縣市'][i] + ' ' + earthquake5['行政區'][i] + ' ' + earthquake5['震度'][i] + ' ' + earthquake5['縣市'][i+1] + ' ' + earthquake5['行政區'][i+1] + ' ' +  earthquake5['震度'][i+1]
    info_list.append(info)        
    return info_list

@bot.event #這是裝飾器
async def on_ready(): #當機器人完成啟動時
  #slash = await bot.tree.sync()
  print('目前登入身份：', bot.user)
  s = await bot.tree.sync()
  print(f'有{len(s)}個指令')
  #print(f"載入 {len(slash)} 個斜線指令")

@bot.tree.command(name = 'load', description = '載入程式檔案')
#通常使用於撰寫好新的程式檔案要上線，或者要將之前載出的程式檔案再次上線。
async def load(interaction: discord.Interaction, extension: str):
    await bot.load_extension(f"cogs.{extension}")
    await interaction.channel.send(f"Loaded {extension} done.")

@bot.tree.command(name = 'plus', description = '加法')
async def plus(interaction: discord.Interaction, a: int, b: int):
    await interaction.response.send_message(a+b)

@bot.tree.command(name = 'minus', description = '減法')
async def minus(interaction: discord.Interaction, a: int, b: int):
    await interaction.response.send_message(a-b)

@bot.tree.command(name = 'times', description = '乘法')
async def times(interaction: discord.Interaction, a: int, b: int):
    await interaction.response.send_message(a*b)

@bot.tree.command(name = 'divide', description = '除法')
async def divide(interaction: discord.Interaction, a: int, b: int):
    await interaction.response.send_message(a/b)

@bot.tree.command(name = 'ping', description = 'ping')
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f'{round(bot.latency*1000, 2)}ms')
    #bot.latency 機器人延遲

@bot.tree.command(name = 'hello', description = '打招呼')
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hi {interaction.user.mention}")

"""
#@app_commands.command(name = "order", description = "點餐機")
@app_commands.describe(meal = "選擇餐點", size = "選擇份量")
@app_commands.choices(
    meal = [
        Choice(name = "漢堡", value = "hamburger"),
        Choice(name = "薯條", value = "fries"),
        Choice(name = "雞塊", value = "chicken_nuggets"),
    ],
    size = [
        Choice(name = "大", value = 0),
        Choice(name = "中", value = 1),
        Choice(name = "小", value = 2),
    ]
)
@bot.tree.command(name = 'order')
async def order(interaction: discord.Interaction, meal: Choice[str], size: Choice[int]):
    # 獲取使用指令的使用者名稱
    customer = interaction.user.name
    # 使用者選擇的選項資料，可以使用name或value取值
    meal = meal.value
    size = size.value
    await interaction.response.send_message(f"{customer} 點了 {size} 號 {meal} 餐")
"""

#@app_commands.command(name = 'youbike', description = '查詢YouBike')
@app_commands.describe(form = "選擇關鍵字類別")
@app_commands.choices(
    form = [
        Choice(name = "地點(路名)", value = "地點"),
        Choice(name = "名稱(站點名稱)", value = "名稱"),
    ]
)

@bot.tree.command(name = 'youbike', description = '查詢YouBike')
async def youbike(interaction: discord.Interaction, form: Choice[str], keyword:str):
    form_a = str(form)
    if form_a == "Choice(name='地點(路名)', value='地點')":
        form_a = form_a.replace("Choice(name='地點(路名)', value='地點')", '地點')
    else:
        form_a = form_a.replace("Choice(name='名稱(站點名稱)', value='名稱')", '名稱')
    await interaction.response.send_message(f"正在查詢**{form_a}**包含 **{keyword}** 的結果")
    df = youbike_search(form_a, keyword)
    df = df.reset_index(drop = True)
    #s1 = '場站名稱 , 空車數量 , 空位數量'
    s1 = '空 空\n車 位  場站名稱'
    s2 = ''
    for i in range(len(df)): 
      #await ctx.send(df['場站目前車輛數量'][i], df['空位數量'][i], df['場站中文名稱'][i])
      #print(df['場站中文名稱'][i] + ' , ' + str(df['場站目前車輛數量'][i]) + ' , ' + str(df['空位數量'][i]))
        if len(str(df['場站目前車輛數量'][i])) == 1:
            if len(str(df['空位數量'][i])) == 1:
                s2 += str(df['場站目前車輛數量'][i]) + '  ' + str(df['空位數量'][i]) + '  ' + df['場站中文名稱'][i] + '\n'
            else:
                s2 += str(df['場站目前車輛數量'][i]) + '  ' + str(df['空位數量'][i]) + ' ' + df['場站中文名稱'][i] + '\n'
        else:
            if len(str(df['空位數量'][i])) == 1:
                s2 += str(df['場站目前車輛數量'][i]) + ' ' + str(df['空位數量'][i]) + '  ' + df['場站中文名稱'][i] + '\n'
            else:
                s2 += str(df['場站目前車輛數量'][i]) + ' ' + str(df['空位數量'][i]) + ' ' + df['場站中文名稱'][i] + '\n'
    await interaction.channel.send(f'```{s1}\n{s2}```')



@bot.tree.command(name = 'youbike_zero', description = '查詢沒有YouBike的站點')
async def youbike(interaction: discord.Interaction):
    #await interaction.response.send_message(f"正在查詢 {form} 包含 {keyword} 的結果")
    df = youbike_zero()
    df = df.reset_index(drop = True)
    #s1 = '場站名稱 , 空車數量 , 空位數量'
    s1 = '場站名稱，地點'
    s2 = ''
    for i in range(len(df)): 
        s2 += df['場站中文名稱'][i] + '   ' + df['地點'][i] +'\n'
    await interaction.response.send_message(f'```{s1}\n{s2}```')

@bot.tree.command(name = 'tr_train_no', description = '查詢台鐵車次時刻表')
async def train_no(interaction: discord.Interaction, date:int, number:str):
    await interaction.response.send_message(f"正在查詢 **{date}** 車次 **{number}** 的時刻表")
    info, time_list = railway_train_time(date, number)
    time = time_list[0]
    await interaction.channel.send(f'```{info}\n\n站名     到站時間    離站時間 \n{time}```')
    for i in range(1, len(time_list)):
        time = time_list[i]
        await interaction.channel.send(f'```{time}```')

@bot.tree.command(name = 'tr_train_time', description = '查詢台鐵時刻表')
async def train_no(interaction: discord.Interaction, date:int, sta_from:str, sta_to:str):

    await interaction.response.send_message(f"正在查詢 **{date}** 從 **{sta_from}** 到 **{sta_to}** 的時刻表")
    info_list = tr_train_time_find(date, sta_from, sta_to)
    for i in info_list:
        info = i
        await interaction.channel.send(f'```車次  車種        起站   終站   經由  出發時間   抵達時間   行駛時間\n{info}```')
    """
    info, sign, n = tr_train_time_find(date, sta_from, sta_to)
    if sign == 1:
        await interaction.channel.send(f'```車次  車種        起站   終站   經由  出發時間    抵達時間    行駛時間\n{info}```')
        while sign == 1:
            info, sign, n = tr_train_time_find_c(date, sta_from, sta_to, n)
            await interaction.channel.send(f'```車次  車種        起站   終站   經由  出發時間    抵達時間    行駛時間\n{info}```')
    else:
        await interaction.channel.send(f'```車次  車種        起站   終站   經由  出發時間    抵達時間    行駛時間\n{info}```')
    """

@bot.tree.command(name = 'tr_sta_time', description = '查詢台鐵站別時刻表')
async def train_no(interaction: discord.Interaction, date:int, sta:str):
    await interaction.response.send_message(f"正在查詢**{date}** **{sta}**站的時刻表")
    info_list = tr_sta_time(date, sta)
    for i in info_list:
        info = i
        await interaction.channel.send(f'```車次  車種        起站   終站   經由   出發時間   停靠站\n{info}```')
    """
    info, sign, n = tr_sta_time(date, sta)
    if sign == 1:
        await interaction.channel.send(f'```車次  車種        起站   終站   經由   出發時間   停靠站\n{info}```')
        while sign == 1:
            info, sign, n = tr_sta_time_c(date, sta, n)
            await interaction.channel.send(f'```車次  車種        起站   終站   經由   出發時間   停靠站\n{info}```')
    else:
        await interaction.channel.send(f'```車次  車種        起站   終站   經由   出發時間   停靠站\n{info}```')
    """

@app_commands.describe(direct = "選擇順行/逆行")
@app_commands.choices(
    direct = [
        Choice(name = "順行", value = 0), Choice(name = "逆行", value = 1),
    ]
)

@bot.tree.command(name = 'tr_sta_time_direct', description = '查詢台鐵站別時刻表')
async def train_no(interaction: discord.Interaction, date:int, sta:str, direct:int):
    direct_str = '順行'
    if direct == 1:
        direct_str = '逆行'
    else:
        direct_str = '順行'
    await interaction.response.send_message(f"正在查詢**{date}** **{sta}**站 **{direct_str}**的時刻表")
    info_list = tr_sta_time_direct(date, sta, direct)
    for i in info_list:
        info = i
        await interaction.channel.send(f'```車次  車種        起站   終站   經由   出發時間   停靠站\n{info}```')

@app_commands.describe(city_name = "選擇縣市")
@app_commands.choices(
    city_name = [
        Choice(name = "基隆市", value = "基隆市"), Choice(name = "臺北市", value = "臺北市"),
        Choice(name = "新北市", value = "新北市"), Choice(name = "桃園市", value = "桃園市"),
        Choice(name = "新竹縣", value = "新竹縣"), Choice(name = "新竹市", value = "新竹市"),
        Choice(name = "苗栗縣", value = "苗栗縣"), Choice(name = "臺中市", value = "臺中市"),
        Choice(name = "彰化縣", value = "彰化縣"), Choice(name = "南投縣", value = "南投縣"),
        Choice(name = "雲林縣", value = "雲林縣"), Choice(name = "嘉義縣", value = "嘉義縣"),
        Choice(name = "嘉義市", value = "嘉義市"), Choice(name = "臺南市", value = "臺南市"),
        Choice(name = "高雄市", value = "高雄市"), Choice(name = "屏東縣", value = "屏東縣"),
        Choice(name = "宜蘭縣", value = "宜蘭縣"), Choice(name = "花蓮縣", value = "花蓮縣"),
        Choice(name = "臺東縣", value = "臺東縣"), Choice(name = "澎湖縣", value = "澎湖縣"),
        Choice(name = "金門縣", value = "金門縣"), Choice(name = "連江縣", value = "連江縣"),
    ]
)

@bot.tree.command(name = 'weather_now', description = '查詢即時天氣資料')
async def weather_now(interaction: discord.Interaction, city_name:str):
    await interaction.response.send_message(f"正在查詢 **{city_name}** 的即時天氣")
    info = weather(city_name)
    await interaction.channel.send(f'```站點  天氣   氣溫 累積雨量(mm)\n{info}```')

@bot.tree.command(name = 'temperature_c_to_f', description = '攝氏溫標轉華氏溫標')
async def temperature_c_to_f(interaction: discord.Interaction, celsius:float):
    c = celsius
    f = c * 9 / 5 + 32
    await interaction.response.send_message(f"攝氏溫度：{c}℃ = 華氏溫度：{f}℉")

@bot.tree.command(name = 'temperature_f_to_c', description = '華氏溫標轉攝氏溫標')
async def temperature_f_to_c(interaction: discord.Interaction, fahrenheit:float):
    f = fahrenheit
    c = (f - 32) * 5 / 9
    await interaction.response.send_message(f"華氏溫度：{f}℉ = 攝氏溫度：{c}℃")

@app_commands.describe(symbol = "加減乘除")
@app_commands.choices(
    symbol = [
        Choice(name = "+", value = "+"),
        Choice(name = "-", value = "-"),
        Choice(name = "*", value = "*"),
        Choice(name = "/", value = "/"),
    ]
)

@bot.tree.command(name = 'calculator', description = '計算機')
async def calculator(interaction: discord.Interaction, a:float, symbol:'str', b:float):
    ans = 0
    if symbol == '+':
        ans = a + b
    elif symbol == '-':
        ans = a - b
    elif symbol == '*':
        ans = a * b
    elif symbol == '/':
        ans = a / b
    await interaction.response.send_message(f'{a} {symbol} {b} = {ans}')

@bot.tree.command(name = 'bmi', description = 'BMI值計算')
async def bmi(interaction: discord.Interaction, height_cm:float, weight_kg:float):
    height = height_cm / 100
    weight = weight_kg
    bmi = weight / (height ** 2)
    await interaction.response.send_message(f'身高：**{height_cm}**cm \n體重：**{weight_kg}**kg')
    if bmi < 18.5:  
        await interaction.channel.send(f'您的BMI值是：{bmi}，過輕')
    elif bmi>24:
        await interaction.channel.send(f'您的BMI值是：{bmi}，過胖')
    else:
        await interaction.channel.send(f'您的BMI值是：{bmi}，正常')

@bot.tree.command(name = 'leap_year', description = '閏年判斷')
async def leap_year(interaction: discord.Interaction, year:int):
    await interaction.response.send_message(f'查詢年份：{year}年')
    if year % 4 == 0:
        if year % 100 == 0:
            if year % 400 == 0:
                await interaction.channel.send(f"{year}年是閏年")
            elif year % 400 != 0:
                await interaction.channel.send(f"{year}年是平年")
            else:
                await interaction.channel.send("資料有誤")
        elif year % 100 != 0:
            await interaction.channel.send(f"{year}年是閏年")
        else:
            await interaction.channel.send("資料有誤")
    elif year % 4 != 0:
        await interaction.channel.send(f"{year}年是平年")
    else:
        await interaction.channel.send("資料有誤")

@bot.tree.command(name = 'draw_straw', description = '抽籤')
async def draw_straw(interaction: discord.Interaction, start:int, end:int, how_many:int):
    numbers = []
    for i in range(how_many):
        number = random.randrange(start,end) # 隨機取整數(含最小值，不含最大值)
        numbers.append(number)
    await interaction.response.send_message(f'號碼範圍：{start}~{end}\n抽出數量：{how_many}\n抽出號碼：')
    for j in range(len(numbers)):
        await interaction.channel.send(numbers[j])
    
@bot.tree.command(name = 'password_generation', description = '密碼產生器')
async def password_generation(interaction: discord.Interaction, length:int):
    number = string.digits # 可以產生0~9的數字
    letter = string.ascii_letters # 可產生英文大小寫的字母
    passwordlist = number + letter # 0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
    number = list(number) # 由於字串無法shuffle，因此將字串換成清單
    letter = list(letter)
    passwordlist = number + letter
    random.shuffle(passwordlist)
    passwords = passwordlist[:length]
    password = ""
    for i in range(length):
        password += passwords[i]
    await interaction.response.send_message(f'您的密碼是：{password}')

@bot.tree.command(name = 'permutation_combination', description = '排列組合計算機')
async def permutation_combination(interaction: discord.Interaction, n:int, k:int):
    p = P(n, k)
    c = C(n, k)
    await interaction.response.send_message(f'P({n},{k})={p}')
    await interaction.channel.send(f'C({n},{k})={c}')

@bot.tree.command(name = 'world_weather', description = '城市天氣查詢程式 with Open Weather')
async def world_weather(interaction: discord.Interaction, city_name:str):
    API_key = "811b0dec8af25d7a3c469ae6d7fbdfeb" # API
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_key}' # 語法、網址
    information = requests.get(url) # 查詢資料
    kelvin = information.json()['main']['temp'] # 克氏溫標，轉為字典型式以方便查詢
    celsius = kelvin-273.15 # 攝氏溫標
    celsius = round(celsius,1) # 四捨五入
    await interaction.response.send_message(f'{city_name} 目前溫度：{celsius}℃') 

@bot.tree.command(name = 'what_to_eat_for_dinner', description = '晚餐吃什麼')
async def hello(interaction: discord.Interaction):
    dinner_list = ['土托魚羹', '老翁家', '伊田雞肉', '鐵板燒', '蕭家牛雜湯', '三源', '八方雲集', '一品', '泰廚', '根本', '大排檔', '櫻桃小鎮', '吃大餐！']
    random.shuffle(dinner_list)
    dinner = dinner_list[0]
    await interaction.response.send_message(dinner)

@bot.tree.command(name = 'quadratic_equation', description = '一元二次方程式求解')
async def quadratic_equation(interaction: discord.Interaction, a:int, b:int, c:int):
    d = b ** 2 - 4 * a * c
    await interaction.response.send_message(f'({a})x^2 + ({b})x + ({c})')
    if d > 0:
        root1 = (b * (-1) + d ** 0.5) / (2 * a)
        root2 = int((b * (-1) - d ** 0.5) / (2 * a))
        await interaction.channel.send(f'Two different roots x1 = {root1} , x2 = {root2}')
    elif d == 0:
        root1 = int((b * (-1) / (2 * a)))
        await interaction.channel.send(f'Two same roots x={root1}')
    elif d < 0:
        await interaction.channel.send('No real root')

@bot.tree.command(name = 'check_id_card_no', description = '查驗身分證字號')
async def check_id_card_no(interaction: discord.Interaction, id_card_no:str):
    character_list = {'A':10, 'B':11, 'C':12, 'D':13, 'E':14, 'F':15, 'G':16, 'H':17, 'J':18, 'K':19, 'L':20, 'M':21, 'N':22,
            'P':23, 'Q':24, 'R':25, 'S':26, 'T':27, 'U':28, 'V':29, 'X':30, 'Y':31, 'W':32, 'Z':33, 'I':34, 'O':35}
    list1 = []
    for i in id_card_no:
        list1.append(i)
    list1[0] = character_list[list1[0]]
    for i in range(len(list1)):
        list1[i] = int(list1[i])
    character_no = (list1[0] // 10) + (list1[0] % 10) * 9
    no_sum = 0
    for i in range(1,9):
        no_sum += list1[i] * (9-i)
    no_sum += list1[9]
    total_no = character_no + no_sum
    if total_no % 10 == 0:
        await interaction.response.send_message(f'身分證字號 {id_card_no} 符合規則')
    else:
        await interaction.response.send_message(f'身分證字號 {id_card_no} 不符合規則')

@bot.tree.command(name = 'id_card_character', description = '回推身分證字號首字母')
async def check_id_card_no(interaction: discord.Interaction, id_card_no:str):
    char = {'A':10, 'B':11, 'C':12, 'D':13, 'E':14, 'F':15, 'G':16, 'H':17, 'I':34, 'J':18, 'K':19, 'L':20, 'M':21, 'N':22, 'O':35,
        'P':23, 'Q':24, 'R':25, 'S':26, 'T':27, 'U':28, 'V':29, 'W':32, 'X':30, 'Y':31, 'Z':33}
    letter = ''
    for i in char:
        c = (char[i]//10) + (char[i]%10)*9
        c = c%10
        char[i] = c
    b = [int(i) for i in id_card_no]
    d = 0
    for i in range(8):
        d += b[i] * (8-i)
    d += b[8]
    if d % 10 == 0:
        e = 0
    else:
        e = 10 - (d % 10)
    for i in char:
        if char[i] == e:
            letter += i
    await interaction.response.send_message(f'身份證字號數字部分 {id_card_no} 回推字母為 {letter}')

@bot.tree.command(name = 'id_card_check_no', description = '身分證字號檢查碼')
async def check_id_card_no(interaction: discord.Interaction, id_card_no:str):
    char = {'A':10, 'B':11, 'C':12, 'D':13, 'E':14, 'F':15, 'G':16, 'H':17, 'J':18, 'K':19, 'L':20, 'M':21, 'N':22,
        'P':23, 'Q':24, 'R':25, 'S':26, 'T':27, 'U':28, 'V':29, 'X':30, 'Y':31, 'W':32, 'Z':33, 'I':34, 'O':35}
    b = [str(i) for i in id_card_no]
    b[0] = char[b[0]]
    for i in range(len(b)):
        b[i] = int(b[i])
    c = (b[0] // 10) + (b[0] % 10) * 9
    d = 0
    for i in range(1,9):
        d += b[i] * (9-i)
    e = c + d
    m = 10 - (e % 10)
    await interaction.response.send_message(f'身份證字號 {id_card_no} 檢查碼為 {m}')

@bot.tree.command(name = 'demical_to_binary', description = '十進制轉二進制')
async def demical_to_binary(interaction: discord.Interaction, num:int):
    temp_str = ''
    while num > 0:
        temp = num % 2
        num = num // 2
        temp_str = str(temp) + temp_str
    await interaction.response.send_message(num,'=',int(temp_str))

@bot.tree.command(name = 'binary_to_demical', description = '二進制轉十進制')
async def binary_to_demical(interaction: discord.Interaction, num:str):
    demical = 0
    for i in range(1, len(num)+1):
        demical += int(num[-i]) * (2 ** (i-1))
    await interaction.response.send_message(num,'=',demical)

@bot.tree.command(name = 'train_seat', description = '查詢台鐵列車座位靠窗/走道與靠山/海')
async def tra_seat(interaction: discord.Interaction, day:int, train_no:int, car:int, seat_no:int):
    await interaction.response.send_message('正在查詢中...')
    info = seat(day, train_no, car, seat_no)
    await interaction.channel.send(info)

@bot.tree.command(name = 'wide_earthquake', description = '查詢顯著有感地震報告')
async def tra_seat(interaction: discord.Interaction):
    await interaction.response.send_message('正在查詢中...')
    info_list = wide_earthquake()
    for i in info_list:
        info = i
        await interaction.channel.send(f'```{info}```')

'''
@bot.command()
#通常使用於撰寫好新的程式檔案要上線，或者要將之前載出的程式檔案再次上線。
async def load(ctx, extension):
    await bot.load_extension(f"cogs.{extension}")
    await ctx.send(f"Loaded {extension} done.")

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hi <@{ctx.author.id}>")

@bot.command()
async def youbike(ctx, form, keyword):
    await ctx.send(f"正在查詢 {form} 包含 {keyword} 的結果")
    #await ctx.send('請稍候，這可能需要一點時間...')
    df = youbike_search(form, keyword)
    df = df.reset_index(drop = True)
    await ctx.send('場站名稱 , 空車數量 , 空位數量')
    #await ctx.send('空車數量')
    #await ctx.send('| 空位數量')
    #await ctx.send('|  | 場站名稱')
    for i in range(len(df)): 
      #await ctx.send(df['場站目前車輛數量'][i], df['空位數量'][i], df['場站中文名稱'][i])
      print(df['場站中文名稱'][i] + ' , ' + str(df['場站目前車輛數量'][i]) + ' , ' + str(df['空位數量'][i]))
      await ctx.send(df['場站中文名稱'][i] + ' , ' + str(df['場站目前車輛數量'][i]) + ' , ' + str(df['空位數量'][i]))

@bot.command()
async def ping(ctx):
    await ctx.send(f'{round(bot.latency*1000, 2)}ms')
    #bot.latency 機器人延遲
'''

@bot.event #這是裝飾器

async def on_message(msg): #當偵測到訊息
  await bot.process_commands(msg)
  if msg.author == bot.user:  #避免無限循環
      return
  if msg.content.startswith("say"):  #偵測msg的開頭
      tmp = msg.content.split(" ", 1)  #將msg切開
      if len(tmp)==1:  #如果長度只有1，代表後面沒東西
          await msg.channel.send("Pardon me?")
      else:
          await msg.channel.send(tmp[1])
  if bot.user.mentioned_in(msg): #當Bot被提及
    #delmsg = await message.channel.send(message.author.mention+"幹嘛啦!?") 
        #將訊息存入delmsg方便之後刪除
    #await asyncio.sleep(3) #停止3秒
    #await delmsg.delete() #刪除訊息
    #await message.channel.send(message.author.name+"對不起我不該這麼兇\n")
    delmsg = await msg.channel.send("怎麼了？")

bot.run('') #就是你剛剛拿到的TOKEN
