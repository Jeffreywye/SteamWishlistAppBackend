from Steam.SteamAPI import SteamAPI
from Models.models import Game

# this file will hold all sql queries related to steam
# must test if db object/instance can be passed 
# when this file is imported to apps

# must put list of games on hold since, can't add the games to db atm
class SteamQueries:
    def __init__(self, db):
        self._db = db
        self._steam = SteamAPI()

    def initSteamDB(self):
        data = self._steam.getGames()
        for app in data:
            game = Game(app_id=app['appid'],
                        name=app['name'])
            try:
                self._db.session.add(game)
                self._db.session.commit()
            except Exception as e:
                print("Error at ")
                print(app)
                print(e)


class Queries:
    def __init__(self, db):
        self._db = db
        self._steam = SteamAPI()

    def getWishlist(self, id):
        pass

    def addToWishlist(self, id, appID):
        data = self._steam.requestGameData(appID)
        if data:
            if 'free' in data:
                pass
            else:
                pass
            # game = Game(app_id=,
            #             name=,
            #             init_price=,
            #             final_price=,
            #             discount_percent=, 
            #             )
   
        return False

    def updateWishlistGame(self, id):
        pass

    def removeFromWishlist(self, id, appID):
        pass
