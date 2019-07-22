"""
models.py

Odds Portal data model for storing stuff that's scraped

"""


import json
import os


class Game(object):
    def __init__(self):
        self.retrieval_url = str()
        self.retrieval_datetime = str()
        self.game_datetime = str()
        self.game_url = str()
        self.num_possible_outcomes = str()
        self.team_home = str()
        self.team_away = str()
        self.odds_home = str()
        self.odds_away = str()
        self.odds_draw = str()
        self.outcome = str()
        self.score_home = str()
        self.score_away = str()


class Season(object):
    def __init__(self,name):
        self.name = name
        self.games = list()
        self.urls = list()
        self.possible_outcomes = int()

    def add_game(self,game):
        self.games.append(game)

    def add_url(self,url):
        self.urls.append(url)


class League(object):
    def __init__(self,name):
        self.name = name
        self.seasons = dict()
        self.root_url = str()

    def __getitem__(self,key):
        return self.seasons[key]

    def __setitem__(self,key,value):
        self.seasons[key] = value


class BasicJsonEncoder(json.JSONEncoder):
        def default(self, o):
            return o.__dict__ 


class Collection(object):
    def __init__(self,name):
        self.name = name
        self.sport = str()
        self.region = str()
        self.output_dir = str()
        self.outcomes = 0
        self.league = None

    def __getitem__(self,key):
        return self.league[key]

    def __setitem__(self,key,value):
        self.league[key] = value


class DataRepository(object):
    def __init__(self):
        self.collections = dict()
        self.output_dir = str()

    def start_new_data_collection(self,target_sport_obj):
        if target_sport_obj['collection_name'] not in self.collections:
            # Most fields from "target sport objects" map to Collection fields
            new_collection = Collection(target_sport_obj['collection_name'])
            new_collection.sport = target_sport_obj['sport']
            new_collection.region = target_sport_obj['region']
            new_collection.output_dir = target_sport_obj['output_dir']
            new_collection.outcomes = target_sport_obj['outcomes']
            # *Some* fields from "target sport objects" map to League fields
            new_league = League(target_sport_obj['league'])
            new_league.root_url = target_sport_obj['root_url']
            new_collection.league = new_league
            # Store this new Collection in this repository, by name
            self.collections[target_sport_obj['collection_name']] = new_collection
        else:
            raise RuntimeError('Target sports JSON file must have unique collection names.')

    def set_output_directory(self,path):
        self.output_dir = path

    def save_all_collections_to_json(self):
        for _, collection in self.collections.items():
            qualified_output_dir = os.path.normpath(self.output_dir + os.sep + collection.output_dir)
            if os.path.isdir(qualified_output_dir):
                filelist = [ f for f in os.listdir(qualified_output_dir) ]
                for f in filelist:
                    os.remove(os.path.join(qualified_output_dir, f))
            else:
                os.makedirs(qualified_output_dir)
            with open(os.path.join(qualified_output_dir, collection.name + '.json'), 'w') as outfile:
                json.dump(collection, outfile, cls=BasicJsonEncoder)

    def __getitem__(self,key):
        return self.collections[key]

    def __setitem__(self,key,value):
        self.collections[key] = value
