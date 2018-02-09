import graphene
from graphene import relay
from graphql_relay.node.node import to_global_id
from boardgamegeek import BGGClient

bgg = BGGClient(retries=3, retry_delay=8)

def get_collection(username):
    col = bgg.collection(username, exclude_subtype='boardgameexpansion', own=True, wishlist=None)
    game_list = []
    for game in col:
        g = Game(id=game.id, gid=game.id, collection_name=game.name, rating=game.rating, maxplayers=game.maxplayers, minplayers=game.minplayers)
        game_list.append(g)
    c = Collection(id=username, numgames=len(col), username=username, games=game_list)
    return c


class Game(graphene.ObjectType):

    class Meta:
        interfaces = (relay.Node, )

    gid = graphene.Int(required=True)
    collection_name = graphene.String()
    rating = graphene.Float()
    maxplayers = graphene.Int()
    minplayers = graphene.Int()

    @classmethod
    def get_node(cls, info, id):
        pass

class GameConnection(relay.Connection):

    class Meta:
        node = Game


class Collection(graphene.ObjectType):
    """BGG Collection data """
    class Meta:
        interfaces = (relay.Node, )

    username = graphene.String(required=True)
    numgames = graphene.Int()

    games = relay.ConnectionField(GameConnection, description="Games in collection")
    def resolve_games(self, info):
        return self.games

    @classmethod
    def get_node(cls, info, id):
        return get_collection(cls.username)


class QueryType(graphene.ObjectType):
    collection = graphene.Field(Collection, username=graphene.String())
    node = relay.Node.Field()

    def resolve_collection(self, info, username):
        return get_collection(username)

schema = graphene.Schema(query=QueryType)