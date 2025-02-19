import json
from pathlib import Path
import os
from dataclasses import dataclass
from pprint import pprint

@dataclass
class ITMsg:  # only for IT, since sectioned into two (groups don't reflect sections in the case of IT)
    # IT sections with usernames 
    _support = [] 
    _sysadmins = []

    @property
    def support(self):
        return self._support
    
    @property
    def sysadmins(self):
        return self._sysadmins


class Team:
    def __init__(self, id, name, boss, dn, header, category):
        self._id = id
        self._name = name
        self._boss = boss
        self._dn = dn
        self._header = header
        self._category = category

    def __str__(self):
        return str(self._name)

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def boss(self):
        return self._boss

    @property
    def dn(self):
        return self._dn

    @property
    def category(self):
        return self._category

    @property
    def header(self):
        return self._header
    

class Teams:
    def __init__(self):
        teams_file_path = f'{str(os.path.dirname(os.path.realpath(__file__)))}/teams_data.json'
        self._teams = self.load_teams(teams_file_path)
    
    def get_team_by_id(self, id):
        for team in self._teams:
            if team.id == id:
                return team

    def load_teams(self, file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                teams_data = json.load(file)
                teams = [Team(**team) for team in teams_data]
            pprint(f'Loading {len(teams)} teams')
            return teams

    @property
    def teams(self):
        return self._teams

    
            

teams_file_path = Path(__file__).parent / 'teams_data.json'

itmsg = ITMsg()
