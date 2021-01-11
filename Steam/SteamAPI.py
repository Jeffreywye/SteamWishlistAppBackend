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
        # if is success but no price over_view is returned then game is FREE
    
        url = "http://store.steampowered.com/api/appdetails?appids="+str(app_id)+"&cc=us&l=en&filters=price_overview"
        resp = requests.get(url)
        data = resp.json()[str(app_id)]
        ret = {}
        if data['success'] == False :
            ret['msg'] = 'failed'
            return []
        else:
            data = data['data']
            if not data:
                # game/dlc is free
                return ['free']
            else:
                # game/dlc has a price
                return data
        
        
# steam = SteamAPI()
# apps = steam.getGames()
# appPrices = []
# for index in range(20):
#     id = apps[index]['appid']
#     steam.requestGameData(id)