from tests.testconf import *
from website.models import Game

def test_game_model(session):
    game = mixer.blend(Game)
    assert game.gid > 0
