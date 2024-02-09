import json
import logging
import os

logging.basicConfig(level=logging.WARNING)

from .vendor.supabase import create_client, Client
from .vendor.gotrue.errors import AuthApiError, AuthInvalidCredentialsError
from .api import ambr

class Database:

    def __init__(self):
        # Default to public Supabase credentials
        url = os.environ.get('SUPABASE_URL', 
                             'https://fsasczgnagdnyclkdvyk.supabase.co')
        key = os.environ.get('SUPABASE_KEY', 
                             'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZzYXNjemduYWdkbnljbGtkdnlrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDU5ODEyMzYsImV4cCI6MjAyMTU1NzIzNn0.L2A-5o50ikk8PdV1xVseRbth9Rk45HaiwQNebkitBCY')
        self.supabase: Client = create_client(url, key)
        
        self.account_load()
        
        # Load characters and weapons
        self.characters = ambr.get_characters()
        self.weapons = ambr.get_weapons()

    def is_logged_in(self):
        return self.supabase.auth.get_user() is not None

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
        user_response = self.supabase.auth.get_user()
        
        if user_response:
            response = self.supabase.table("profiles").select("*").eq("id", user_response.user.id).execute()
        
            if response:
                self.gacha_points = response.data[0]['gacha_points']
                self.lifetime_rolls = response.data[0]['lifetime_rolls']
                self.pity_4_star = response.data[0]['pity_4_star']
                self.pity_5_star = response.data[0]['pity_5_star']

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
