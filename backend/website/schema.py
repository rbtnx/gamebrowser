import graphene
from graphene import relay
from graphql_relay.node.node import to_global_id
from boardgamegeek import BGGClient

bgg = BGGClient(retries=10, retry_delay=4)

def create_game_list(username):
    collection = bgg.collection(username, exclude_subtype='boardgameexpansion', own=True, wishlist=None)
    game_list = []
    for game in collection:
        g = Game(id=game.id, gid=game.id, collection_name=game.name, rating=game.rating,
                 maxplayers=game.maxplayers, minplayers=game.minplayers)
        game_list.append(g)
    return game_list


def get_collection(username):
    game_list = create_game_list(username)
    c = Collection(id=username, numgames=len(game_list), username=username,
                   games=[game.gid for game in game_list])
    return c

def get_game(owner, id_):
    game_list = create_game_list(owner)
    for game in game_list:
        if game.gid == id_:
            return game


class Game(graphene.ObjectType):

    class Meta:
        interfaces = (relay.Node, )

    gid = graphene.Int(required=True)
    collection_name = graphene.String()
    rating = graphene.Float()
    maxplayers = graphene.Int()
    minplayers = graphene.Int()
    owner = graphene.String()

    @classmethod
    def get_node(cls, info, id):
        return get_game(cls.owner, id)

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
    def resolve_games(self, info, **args):
        return create_game_list(self.username)

    @classmethod
    def get_node(cls, info, id):
        return get_collection(cls.username)


class QueryType(graphene.ObjectType):
    collection = graphene.Field(Collection, username=graphene.String())
    node = relay.Node.Field()

    def resolve_collection(self, info, username):
        return get_collection(username)


schema = graphene.Schema(query=QueryType)