import json
import os

import requests

from .api import ambr

class Database:

    base_url = 'https://degeneranki.pockethost.io/'
    token = ''
    profile = {}

    def __init__(self):
        self.account_load()
        
        # Load characters and weapons
        self.characters = ambr.get_characters()
        print(self.characters)
        self.weapons = ambr.get_weapons()

    def is_logged_in(self):
        return self.token != ''

    def account_signup(self, username, password):
        url = self.base_url + '/api/collections/users/records'

        payload = {
            'username': username,
            'password': password,
            'passwordConfirm': password,
            # Initial account defaults to 0
            'gacha_points': 0,
            'lifetime_rolls': 0,
            'pity_4_star': 0,
            'pity_5_star': 0,
        }

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            # Pocketbase requires separate auth after creating user
            self.account_login(username, password)
        else:
            print(f"{response.status_code}: {response.json()['message']}.")
        
        return response.status_code

    def account_login(self, username, password):
        url = self.base_url + '/api/collections/users/auth-with-password'

        payload = {
            "identity": username,
            "password": password,
        }
        headers = {
            "Content-Type": "application/json",
        }

        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            response_json = response.json()
            self.token = response_json['token']
            self.profile = response_json['record']

            self.account_load()
        else:
            print(f"{response.status_code}: {response.json()['message']}")
        
        return response.status_code

    def account_signout(self):
        self.token = ''
        self.profile = {}
        
        self.gacha_points = 0
        self.lifetime_rolls = 0
        self.pity_4_star = 0
        self.pity_5_star = 0

    def account_load(self):
        if self.is_logged_in():
            self.gacha_points = self.profile['gachaPoints']
            self.lifetime_rolls = self.profile['lifetimeRolls']
            self.pity_4_star = self.profile['pity4Star']
            self.pity_5_star = self.profile['pity5Star']

    def get_owned_characters(self, franchise):
        character_list = []
        
        if self.is_logged_in():
            url = self.base_url + '/api/collections/character_inventory/records'

            querystring = {"filter":f"(user='{self.profile['id']}' && franchise='{franchise}')"}

            payload = ""
            headers = {}

            response = requests.get(url, data=payload, headers=headers, params=querystring)

            if response.status_code == 200:
                response_json = response.json()
                character_list.extend(response_json['items'])

                while (response_json['page'] < response_json['totalPages']):
                    querystring = {
                        "filter": f"(user='{self.profile['id']}' && franchise='{franchise}')",
                        "page": response_json['page'] + 1
                    }
                    response = requests.get(url, data=payload, headers=headers, params=querystring)
                    
                    response_json = response.json()
                    character_list.extend(response_json['items'])
                    print(character_list)
            else:
                print(f"{response.status_code}: {response.json()['message']}.")  

        return character_list

    def add_owned_character(self, character, franchise) -> None:
        if self.is_logged_in():
            url = self.base_url + '/api/collections/character_inventory/records'

            payload = {
                "user": self.profile['id'],
                "lookup_id": character.id,
                "franchise": franchise,
                "icon_url": character.icon,
                "quantity": 1,
                "xp": 0,
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": self.token,
            }
            
            response = requests.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                pass

    def save(self):
        if self.is_logged_in():
            url = self.base_url + f"/api/collections/users/records/{self.profile['id']}"

            payload = {
                "gachaPoints": self.gacha_points,
                "lifetimeRolls": self.lifetime_rolls,
                "pity4Star": self.pity_4_star,
                "pity5Star": self.pity_5_star,
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": self.token,
            }

            response = requests.patch(url, json=payload, headers=headers)

            if response.status_code == 200:
                pass

