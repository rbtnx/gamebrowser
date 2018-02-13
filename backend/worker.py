import re
from datetime import datetime
import requests
import requests_cache
from bs4 import BeautifulSoup as BS
from boardgamegeek import BGGClient
from website.models import Game, db
from website.app import create_app
import website.config as config


config.Config.SQLALCHEMY_DATABASE_URI = 'postgresql://kathrin:password@localhost:5433/gamebrowser'
app = create_app(config.DevelopmentConfig)
app.app_context().push()
db.init_app(app)
requests_cache.install_cache()

def collection_from_website(username, pagenum=1):
    url = 'https://boardgamegeek.com/collection/user/{}?own=1&subtype=boardgame&excludesubtype=boardgameexpansion&pageID={}'.format(username, pagenum)
    bgg_page = requests.get(url)
    url_text = BS(bgg_page.content, 'html.parser')
    numgames_text = url_text.find('span', attrs={'class':'geekpages'})
    numgames = int(re.search('(?<=of )[0-9]{1,5}', str(numgames_text)).group(0))
    game_list = games_from_html(url_text)
    if pagenum < ((numgames // 300) + 1):
        pagenum += 1
        game_list.update(collection_from_website(username, pagenum))
    return game_list

def games_from_html(url_text):
    """Get all game names and IDs from a page of BGG website.

    Description:
        Scrapes Board Game Geek website games in order of rank.
        Returns a dictionary of games titles:BGG ID, given a page number
        Games are listed in increments of 50

    inputs:
        url_text (soup): Parsed website (with Beautiful soup)

    returns:
        game_list (dict): {Name:ID}
    """
    # url = 'https://boardgamegeek.com/browse/boardgame/page/{}'.format(page)
    games = url_text.find_all("td", class_="collection_objectname")
    plays = url_text.find_all("td", class_="collection_plays")
    rating = url_text.find_all("td", class_="collection_rating")

    def get_game_name(item):
        game_name = item.findNext('a').text
        return game_name

    def get_game_ID(item):
        game_link_id = str(item.findNext('a'))
        game_link_id = re.search('[0-9]{1,7}', game_link_id).group(0)
        return int(game_link_id)

    def get_plays(item):
        if item.a:
            return int(item.a.text)
        return 0

    def get_user_rating(item):
        user_rating = item.findNext("div", class_="rating")
        if user_rating.div:
            return float(user_rating.div.text)
        return float(0)

    game_list = {}
    zipped = zip(games, plays, rating)
    for item in zipped:
        dict_item = {
            get_game_name(item[0]): {
                'id': get_game_ID(item[0]),
                'plays': get_plays(item[1]),
                'rating': get_user_rating(item[2])
            }
        }
        game_list.update(dict_item)
    return game_list

def collect_gamedata(game_list):
    """ Get game data from BGG.

    Description:
        Get game data in chunks of 50 games per api call

    inputs:
        game_list (list): List of ids

    returns:
        games (list): List of game objects """

    bgg = BGGClient(retries=6, retry_delay=4)

    chunksize = 50
    if len(game_list) < chunksize:
        games = bgg.game_list(game_list)
        return games

    games = []
    id_chunks = [game_list[i:i+chunksize] for i in range(0, len(game_list), chunksize)]
    for i in id_chunks:
        games = games + bgg.game_list(i)
    return games

def _suggest_playernum(total_votes, results, minplayers, maxplayers):
    """ Calculate suggestion for player number

    Description:
        private function to determine, if the game is really playable with the given
        number of players. Should only be executed from inside db_update
        returns a 2-dimensional list with 2 entries: list of bestplaynums and list of
        not recommended playnums

    inputs:
        total_votes(int), results (dict), minplayers (int), maxplayers(int)

    returns:
        suggestion (dict): 2 keys, values are lists """

    GOOD_THRESH = 0.15
    BAD_THRESH = 0.15

    if total_votes < 20:
        return {'best with': sorted(list(range(minplayers, maxplayers+1))),
                'not recommended': []}
    good_num = []
    bad_num = []
    for key in results:
        if key[-1:] == '+':
            continue
        if int(results[key]['not_recommended'])/total_votes > BAD_THRESH:
            bad_num.append(int(key))
        if int(results[key]['best'])/total_votes > GOOD_THRESH:
            good_num.append(int(key))
    return {'best with': sorted(good_num), 'not recommended': sorted(bad_num)}


def object_to_model(obj):
    """ Converts bgg BoardGame object to db model """

    numfit = _suggest_playernum(int(obj.suggested_numplayers['total_votes']),
                                obj.suggested_numplayers['results'],
                                obj.max_players, obj.min_players)
    game = Game(gid=obj.id, name_en=obj.name, authors=obj.designers, maxplayers=obj.max_players,
                minplayers=obj.min_players, max_playing_time=obj.max_playing_time,
                min_playing_time=obj.min_playing_time, best_playnum=numfit['best with'],
                not_recom_playnum=numfit['not recommended'], description=obj.description,
                imageurl=obj.image, thumburl=obj.thumbnail, mechanics=obj.mechanics,
                average_weight=obj.rating_average_weight, bgg_rank=obj.stats['ranks'][0]['value'],
                last_updated=datetime.now())
    return game

def update_db(session, game):
    q = Game.query.filter(Game.gid == game.gid)
    if session.query(q.exists()).scalar() is False:
        session.add(game)
        return
    hit = q.first()
    if hit == game:
        return
    hit.bgg_rank = game.bgg_rank
    hit.best_playnum = game.best_playnum
    hit.not_recom_playnum = game.not_recom_playnum
    hit.average_weight = game.average_weight
    hit.imageurl = game.imageurl
    hit.thumburl = game.thumburl
    hit.last_updated = game.last_updated
    return
