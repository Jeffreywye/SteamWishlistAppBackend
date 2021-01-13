from datetime import datetime
from Steam.SteamAPI import SteamAPI
from Models.models import User, Game

# must put list of games on hold since, can't add the games to db atm
# class SteamQueries:
#     def __init__(self, db):
#         self._db = db
#         self._steam = SteamAPI()

#     def initSteamDB(self):
#         data = self._steam.getGames()
#         for app in data:
#             game = Game(app_id=app['appid'],
#                         name=app['name'])
#             try:
#                 self._db.session.add(game)
#                 self._db.session.commit()
#             except Exception as e:
#                 print("Error at ")
#                 print(app)
#                 print(e)


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
            res = None
            # check if game is already added to the users list
            if self.checkGameInList(user,appID):
                # if game is in user's list
                # then failed to add game into list
                res = False
                print("game in list already")
            else:
                # game not in user's list
                try:
                    user.games.append(game)
                    self._db.session.commit()
                    # successfully added game
                    res = True
                except:
                    # anything goes wrong commiting, then failed to add game
                    res = False

            # check if it is up to data
            last_updated = game.last_updated
            if (86400 < (datetime.utcnow()-last_updated).total_seconds()):
                # if the game hasn't been updated in 24 hour update it
                res = self.updateWishlistGame(game, appID)
            return res

        else:
            # if game doesnt exist in db 
            # then add it in
            game = self.createGameObj(appID)
            if game:
                try:
                    self._db.session.add(game)
                    user.games.append(game)
                    self._db.session.commit()
                    return True
                except:
                    return False
        return False

    def checkGameInList(self, userObj, appID):
        try:
            check = userObj.games.filter_by(app_id=appID).all()
            if check:
                return True
            else:
                return False
        except:
            return False

    def updateWishlistGame(self, sqlGameObj, appID):
        app = self._steam.requestGameData(appID)
        ret = False
        if app:
            sqlGameObj.app_id = app['appid']
            sqlGameObj.name = app['name']
            if app['is_free']:
                sqlGameObj.init_price = 0
                sqlGameObj.final_price = 0
                sqlGameObj.discount_percent = 0
            else:
                sqlGameObj.init_price=app['init_price']
                sqlGameObj.final_price=app['final_price']
                sqlGameObj.discount_percent=app['discount']
            sqlGameObj.last_updated = datetime.utcnow()
            try:
                self._db.session.commit()
                ret = True
            except:
                ret = False
        return ret

    def removeFromWishlist(self, id, appID):
        pass

    def createGameObj(self, appID):
        app = self._steam.requestGameData(appID)
        game = None
        if app:
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
        return game