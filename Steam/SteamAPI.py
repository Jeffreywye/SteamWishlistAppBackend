import requests

class SteamAPI:
    def __init__(self):
        pass
    
    def getGames(self):
        resp = requests.get('https://api.steampowered.com/ISteamApps/GetAppList/v2/')
        data = resp.json()['applist']['apps']
        apps = []
        for app in data:
            apps.append(app)
            # print(app)
        return apps

    # must change format
    def requestGameData(self, app_id):
        url = "http://store.steampowered.com/api/appdetails?appids="+str(app_id)+"&cc=us&l=en"
        resp = requests.get(url)
        data = resp.json()[str(app_id)]
        ret = {}
        if data['success'] == False :
            ret['msg'] = 'failed'
            return []
        else:
            ret = {}
            data = data['data']
            ret['name'] = data['name']
            ret['appid'] = data['steam_appid']
            ret['is_free'] = data['is_free']

            if ret['is_free']:
                return ret
            elif 'price_overview' in data:
                ret['init_price'] = data['price_overview']['initial']
                ret['final_price'] = data['price_overview']['final']
                ret['discount'] = data['price_overview']['discount_percent']
                return ret
            else:
                # unreleased game
                return []
        
        
# steam = SteamAPI()
# apps = steam.getGames()
# appPrices = []
# for index in range(10):
#     id = apps[index]['appid']
#     data = steam.requestGameData(id)
#     print(data)