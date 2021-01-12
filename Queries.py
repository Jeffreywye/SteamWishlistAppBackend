from Steam.SteamAPI import SteamAPI
from Models.models import User, Game

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
        user = User.query.get(id)
        game = Game.query.get(appID)

        if game:
            #game exist in db
            # then check if it is up to data
            last_updated = game.last_updated
            return True

        else:
            # if game doesnt exist in db 
            # then add it in
            app = self._steam.requestGameData(appID)
            if app:
                game = None
                if app['is_free']:
                    game = Game(app_id=app['appid'],
                                name=app['name'],
                                init_price=0,
                                final_price=0,
                                discount_percent=0, 
                                )
                else:
                    game = Game(app_id=app['appid'],
                                name=app['name'],
                                init_price=app['init_price'],
                                final_price=app['final_price'],
                                discount_percent=app['discount'], 
                                )
                try:
                    self._db.session.add(game)
                    user.games.append(game)
                    self._db.session.commit()
                    return True
                except:
                    return False
        return False

    def checkGameInList(self, id, appID):
        

    def updateWishlistGame(self, id):
        pass

    def removeFromWishlist(self, id, appID):
        pass
