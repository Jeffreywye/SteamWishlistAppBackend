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

    def requestGameData(self, app_id):
        # if is success but no price over_view is returned then game is FREE
        # maybe shouldnt use filter param, so that response json would have the type key to distinguish dlc from game
    
        url = "http://store.steampowered.com/api/appdetails?appids="+str(app_id)+"&cc=us&l=en&filters=price_overview"
        resp = requests.get(url)
        data = resp.json()[str(app_id)]
        ret = {}
        print(data)
        if data['success'] == False :
            ret['msg'] = 'failed'
            print('failed')
        else:
            data = data['data']
            if not data:
                # game/dlc is free
                print(str(app_id) + " is a free game")
            else:
                # game/dlc has a price
                print(data)
        print()
        
steam = SteamAPI()
apps = steam.getGames()

# print(apps[4])
# print(len(apps))
# appPrices = []
for index in range(20):
    id = apps[index]['appid']
    steam.requestGameData(id)