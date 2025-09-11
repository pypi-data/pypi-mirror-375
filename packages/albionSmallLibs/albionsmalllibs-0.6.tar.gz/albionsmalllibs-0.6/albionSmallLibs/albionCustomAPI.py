from albion_api_client import AlbionAPI
import requests
import json
import sqlite3
import pandas as pd

class CustomAlbionAPI(AlbionAPI):
    @staticmethod
    def __customRequest__(url, params):
        response = requests.get(url, params=params)
        try:
            response.raise_for_status()  # détection d'erreurs HTTP (4xx, 5xx)
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error: {e} - {response.text}")
            raise
        except json.decoder.JSONDecodeError as e:
            print(f"JSON decode error: {e} - {response.text}")
            raise
    
    def __init__(self, path:str = ""):
        # Connect to (or create) the database
        self.conn = sqlite3.connect(path + "data/game_stats.db")
        # Create a cursor object
        self.cursor = self.conn.cursor()
        
    def _url(self, endpoint):
        URL = 'https://gameinfo-ams.albiononline.com/api/gameinfo'
        # 'https://gameinfo-ams.albiononline.com/api/gameinfo'
        return URL + endpoint
        
    def search(self, query):
        params = {}
        params['q'] = query
        response = self.__customRequest__(self._url('/search'), params=params)
        if 'code' in response and response['code'] != 200:
            raise Exception(f"Error: API request failed with status code {response['code']}")
        return response
    
    def get_battle(self, battleID:int ,offset:int=0, limit:int=51):
        params = {}
        params['offset'] = offset
        params['limit'] = limit
        response = self.__customRequest__(self._url(f'/events/battle/{battleID}'),
                            params=params)
        return response
    
    def get_recent_events(self, guildID:str, limit:int=50, offset:int=0):
        params = {}
        params['limit'] = limit
        params['offset'] = offset
        params['guildId'] = guildID
        return self.__customRequest__(self._url('/events'), params=params)
    
    def get_battles_guild(self, guildID, offset=0, limit=51, sort='recent'):
        params = {}
        params['guildId'] = guildID
        params['offset'] = offset
        params['limit'] = limit
        if sort and sort in ['recent', 'topfame']:
            params['sort'] = sort

        return self.__customRequest__(self._url('/battles'), params=params)
    
    def save_battles(self,df_battles):
        df_battles.to_sql("game_results", self.conn, if_exists="append", index=False)
        
    def read_battles(self):
        return pd.read_sql_query("SELECT * FROM game_results", self.conn)
    
    def get_existing_battleID(self):
        """Read existing events from the database."""
        try:
            data = self.read_battles()
            return set(int(ele) for ele in data.ID)
        except:
            print("Can't read DB")
            return set()
    
