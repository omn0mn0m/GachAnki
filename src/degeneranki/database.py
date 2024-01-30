import json
import logging
import os
import sqlite3
import sys

from contextlib import closing
from os import path

logging.basicConfig(level=logging.WARNING)

from ._vendor.supabase import create_client, Client
from .api import ambr

class Database:

    def __init__(self):
        root_project_dir = path.abspath(path.dirname(__file__))
        sys.path.insert(1, root_project_dir)
        self.user_files_dir = path.join(root_project_dir, "user_files")

        # Default to public Supabase credentials
        url = os.environ.get('SUPABASE_URL', 
                             'https://fsasczgnagdnyclkdvyk.supabase.co')
        key = os.environ.get('SUPABASE_KEY', 
                             'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZzYXNjemduYWdkbnljbGtkdnlrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDU5ODEyMzYsImV4cCI6MjAyMTU1NzIzNn0.L2A-5o50ikk8PdV1xVseRbth9Rk45HaiwQNebkitBCY')
        self.supabase: Client = create_client(url, key)
        
        if path.isfile(path.join(self.user_files_dir, "data.json")):
            # Load json data
            with open(path.join(self.user_files_dir, "data.json")) as data_file:
                json_data = json.load(data_file)
                self.gacha_points = json_data.get("gacha_points")
                self.lifetime_rolls = json_data.get("lifetime_rolls")
                self.pity_4_star = json_data.get("pity_4_star")
                self.pity_5_star = json_data.get("pity_5_star")
        else:
            default_json = {
                "gacha_points": 0,
                "lifetime_rolls": 0,
                "pity_4_star": 0,
                "pity_5_star": 0,
            }

            with open(path.join(self.user_files_dir, "data.json"), 'w') as data_file:
                json.dump(default_json, data_file)
                
                self.gacha_points = 0
                self.lifetime_rolls = 0
                self.pity_4_star = 0
                self.pity_5_star = 0
        
        # Load characters and weapons
        self.characters = ambr.get_characters()
        self.weapons = ambr.get_weapons()

        # Creates tables if needed
        with closing(sqlite3.connect(path.join(self.user_files_dir, "database.db"))) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS weapons
                (id VARCHAR(32) NOT NULL PRIMARY KEY,
                quantity INT DEFAULT 1);
                """)
                cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS characters
                (id VARCHAR(32) NOT NULL PRIMARY KEY,
                quantity INT DEFAULT 1,
                xp INT DEFAULT 0);
                """)

    def account_signup(self, email, password):
        response = self.supabase.auth.sign_up({
            "email": email,
            "password": password,
        })
        return response

    def account_login(self, email, password):
        data = self.supabase.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })
        return data

    def account_signout(self):
        response = self.supabase.auth.sign_out()
        return response

    def get_owned_characters(self):
        with closing(sqlite3.connect(path.join(self.user_files_dir, "database.db"))) as connection:
            with closing(connection.cursor()) as cursor:
                return cursor.execute("SELECT * FROM characters").fetchall()
        
    def get_owned_weapons(self):
        with closing(sqlite3.connect(path.join(self.user_files_dir, "database.db"))) as connection:
            with closing(connection.cursor()) as cursor:
                return cursor.execute("SELECT * FROM weapons").fetchall()

    def add_owned_character(self, character_id):
        parameters = {
            'id': character_id,
        }
        with closing(sqlite3.connect(path.join(self.user_files_dir, "database.db"))) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute("""INSERT INTO characters (id)
                VALUES (:id)
                ON CONFLICT (id)
                DO UPDATE SET quantity = quantity + 1
                """, parameters)
                connection.commit()

    def increment_character_xp(self, character_id, xp):
        parameters = {
            'xp': xp,
            'id': character_id,
        }
        with closing(sqlite3.connect(path.join(self.user_files_dir, "database.db"))) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute("""UPDATE characters
                SET xp = xp + :xp
                WHERE id = :id
                """, parameters)
                connection.commit()

    def add_owned_weapon(self, weapon_id):
        parameters = {
            'id': weapon_id,
        }
        with closing(sqlite3.connect(path.join(self.user_files_dir, "database.db"))) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute("""INSERT INTO weapons (id)
                VALUES (:id)
                ON CONFLICT (id)
                DO UPDATE SET quantity = quantity + 1
                """, parameters)
                connection.commit()

    def save(self):
        data = {
            "gacha_points": self.gacha_points,
            "lifetime_rolls": self.lifetime_rolls,
            "pity_4_star": self.pity_4_star,
            "pity_5_star": self.pity_5_star
        }

        with open(path.join(self.user_files_dir, "data.json"), 'w') as json_file:
            json.dump(data, json_file, ensure_ascii=False)
