import requests

class SteamAPI:
    def __init__(self):
        pass

resp = requests.get('https://api.steampowered.com/ISteamApps/GetAppList/v2/')
data = resp.json()['applist']['apps']
print(len(data))

appIDs = []
for app in data:
    appIDs.append(app['appid'])

print(len(appIDs))

appPrices = []
for id in appIDs:
    # if is success but no price over_view is returned then game is FREE
    url = "http://store.steampowered.com/api/appdetails?appids="+str(id)+"&cc=us&l=en&filters=price_overview"
    resp = requests.get(url)
    print(resp.json())