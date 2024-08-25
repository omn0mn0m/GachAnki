import json
import logging
import os

logging.basicConfig(level=logging.WARNING)

import requests

from ._vendor.supabase import create_client, Client
from ._vendor.gotrue.errors import AuthApiError, AuthInvalidCredentialsError
from .api import ambr

class Database:

    def __init__(self):
        self.pocketbase = PocketBase('https://degeneranki.pockethost.io/')
        self.account_load()
        
        # Load characters and weapons
        self.characters = ambr.get_characters()
        self.weapons = ambr.get_weapons()

    def is_logged_in(self):
        return self.pocketbase.is_logged_in()

    def account_signup(self, email, password):
        try:
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
            })
        except (AuthApiError, AuthInvalidCredentialsError) as e:
            response = ErrorResponse()
            response.error = e
        else:
            # Initial account defaults to 0, so no need to load public database
            self.gacha_points = 0
            self.lifetime_rolls = 0
            self.pity_4_star = 0
            self.pity_5_star = 0
        finally:
            return response

    def account_login(self, email, password):
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })
        except (AuthApiError, AuthInvalidCredentialsError) as e:
            response = ErrorResponse()
            response.error = e
        else:
            self.account_load()
        finally:
            return response

    def account_signout(self):
        response = self.supabase.auth.sign_out()
        return response

    def account_load(self):
        if self.pocketbase.is_logged_in():
            self.gacha_points = self.pocketbase.profile['gachaPoints']
            self.lifetime_rolls = self.pocketbase.profile['lifetimeRolls']
            self.pity_4_star = self.pocketbase.profile['pity4Star']
            self.pity_5_star = self.pocketbase.profile['pity5Star']

    def get_owned_characters(self):
        user_response = self.supabase.auth.get_user()
        
        if user_response:
            response = (
                self.supabase.table('inventory')
                .select('profiles(id), items(lookup_id, icon_url, party_url, franchise, item_type), quantity, xp')
                .eq('profiles.id', user_response.user.id)
                .eq('items.item_type', 'CHARACTER')
                .execute()
            )
            return response.data

        return []
        
    def get_owned_weapons(self):
        user_response = self.supabase.auth.get_user()
        
        if user_response:
            response = (
                self.supabase.table('inventory')
                .select('profiles(id), items(lookup_id, icon_url, party_url, franchise, item_type), quantity, xp')
                .eq('profiles.id', user_response.user.id)
                .eq('items.item_type', 'WEAPON')
                .execute()
            )
            return response.data

        return []

    def add_owned_item(self, item, franchise, item_type) -> None:
        user_response = self.supabase.auth.get_user()
        
        if user_response:
            parameters = {
                'profile_id': user_response.user.id,
                'item_lookup_id': item.id,
                'item_franchise': franchise,
                'item_type': item_type,
                'item_icon_url': item.icon,
                'item_party_url': '',
            }

            self.supabase.rpc('add_item', params=parameters).execute()

    def add_owned_character(self, character, franchise) -> None:
        self.add_owned_item(character, franchise, 'CHARACTER')

    def increment_character_xp(self, character_id, xp):
        pass

    def add_owned_weapon(self, weapon_id):
        self.add_owned_item(character, franchise, 'CHARACTER')

    def save(self):
        data = {
            "gacha_points": self.gacha_points,
            "lifetime_rolls": self.lifetime_rolls,
            "pity_4_star": self.pity_4_star,
            "pity_5_star": self.pity_5_star
        }

        user_response = self.supabase.auth.get_user()
        
        if user_response:
            db_data, count = self.supabase.table('profiles').update(data).eq('id', user_response.user.id).execute()

class ErrorResponse:
    pass


class PocketBase:
    
    def __init__(self, url):
        self.url = url
        self.token = ''

    def login(self, username, password):
        login_url = self.url + '/api/collections/collectionIdOrName/auth-with-password'
        response = requests.post(login_url, data={
            'identity': username,
            'password': password,
        })

        if 'token' in response:
            self.token = response['token']
            self.profile = response['record']

    def register(self, username, password):
        register_url = self.url + '/api/collections/users/records'
        response = requests.post(register_url, data={
            'username': username,
            'password': password,
            'passowrdConfirm': password,
        })

    def is_logged_in(self):
        return self.token != ''

    def log_out(self):
        self.token = ''