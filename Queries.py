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
        ret = []
        outdatedGames = []
        try:
            games = User.query.get(id).games
            for game in games:
                last_up = game.last_updated
                if (86400 < (datetime.utcnow()-last_up).total_seconds()):
                    outdatedGames.append(game)
                else:
                    item = {}
                    item['name'] = game.name
                    item['appID'] = game.app_id
                    item['init_price'] = game.init_price
                    item['final_price'] = game.final_price
                    item['discount'] = game.discount_percent
                    ret.append(item)
            
            for game in outdatedGames:
                item = self.updateWishlistGame(game,game.app_id)
                ret.append(item)

        except Exception:
            pass

        return ret

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
                obj = self.updateWishlistGame(game, appID)
                res = True if obj else False
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
        ret = {}
        if app:
            sqlGameObj.app_id = app['appid']
            sqlGameObj.name = app['name']
            ret = {}
            ret['name'] = app['name']
            ret['appID'] = app['appid']
            if app['is_free']:
                sqlGameObj.init_price = 0
                sqlGameObj.final_price = 0
                sqlGameObj.discount_percent = 0
                ret['init_price'] = 0
                ret['final_price'] = 0
                ret['discount'] = 0 
            else:
                sqlGameObj.init_price = app['init_price']
                sqlGameObj.final_price = app['final_price']
                sqlGameObj.discount_percent = app['discount']
                ret['init_price'] = app['init_price']
                ret['final_price'] = app['final_price']
                ret['discount'] = app['discount'] 
            sqlGameObj.last_updated = datetime.utcnow()
            try:
                self._db.session.commit()
            except:
                ret = {}
        return ret

    def removeFromWishlist(self, id, appID):
        user = User.query.get(id)
        game = Game.query.get(appID)
        try:
            user.games.remove(game)
            self._db.session.commit()
            return True
        except:
            return False
        return False

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