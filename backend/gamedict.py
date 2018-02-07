import re
from urllib.request import urlopen
from bs4 import BeautifulSoup as BS

def get_games(page):
    """Get all game names and IDs from a page of BGG website.

    Description:
        Scrapes Board Game Geek website games in order of rank.
        Returns a dictionary of games titles:BGG ID, given a page number
        Games are listed in increments of 50

    inputs:
        page (int): Page number (starts at 1)

    returns:
        game_list (dict): {Name:ID}
    """
    url = 'https://boardgamegeek.com/browse/boardgame/page/{}'.format(page)
    bgg_page = urlopen(url)
    my_bytes = bgg_page.read()
    url_text = my_bytes.decode("utf8")
    bgg_page.close()
    url_text = BS(url_text, 'html.parser')

    games = url_text.find_all("td", class_="collection_objectname")

    def get_game_name(item):
        game_name = item.findNext('a').text
        return game_name

    def get_game_ID(item):
        game_link_id = str(item.findNext('a'))
        game_link_id = re.search('[0-9]{1,7}', game_link_id).group(0)
        return int(game_link_id)

    # game_list = {get_game_name(ii):get_game_ID(ii) for ii in games}
    game_list = {get_game_ID(ii):get_game_name(ii) for ii in games}
    return game_list
