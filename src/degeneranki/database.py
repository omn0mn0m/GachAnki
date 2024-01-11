import json
import sqlite3
import sys
from os import path

from . import ambr

class Database:

    def __init__(self):
        sys.path.insert(1, path.abspath(path.dirname(__file__)))
        root_project_dir = path.abspath(path.dirname(__file__))
        self.user_files_dir = path.join(root_project_dir, "user_files")
        
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

        # Load sqlite3 database data
        self.conn = sqlite3.connect(path.join(root_project_dir, "user_files", "database.db"))
        self.conn.cursor().execute(f"""
        CREATE TABLE IF NOT EXISTS weapons
        (id VARCHAR(32) NOT NULL PRIMARY KEY,
        quantity INT DEFAULT 1);
        """)
        self.conn.cursor().execute(f"""
        CREATE TABLE IF NOT EXISTS characters
        (id VARCHAR(32) NOT NULL PRIMARY KEY,
        quantity INT DEFAULT 1,
        xp INT DEFAULT 0);
        """)

    def get_owned_characters(self):
        return self.conn.cursor().execute("SELECT * FROM characters").fetchall()
        
    def get_owned_weapons(self):
        return self.conn.cursor().execute("SELECT * FROM weapons").fetchall()

    def add_owned_character(self, character_id):
        parameters = {
            'id': character_id,
        }
        self.conn.cursor().execute("""INSERT INTO characters (id)
        VALUES (:id)
        ON CONFLICT (id)
        DO UPDATE SET quantity = quantity + 1
        """, parameters)
        self.conn.commit()

    def increment_character_xp(self, character_id, xp):
        parameters = {
            'xp': xp,
            'id': character_id,
        }
        self.conn.cursor().execute("""UPDATE characters
        SET xp = xp + :xp
        WHERE id = :id
        """, parameters)
        self.conn.commit()

    def add_owned_weapon(self, weapon_id):
        parameters = {
            'id': weapon_id,
        }
        self.conn.cursor().execute("""INSERT INTO weapons (id)
        VALUES (:id)
        ON CONFLICT (id)
        DO UPDATE SET quantity = quantity + 1
        """, parameters)
        self.conn.commit()
        
    def own_weapons(self, weapon_id):
        pass

    def save(self):
        data = {
            "gacha_points": self.gacha_points,
            "lifetime_rolls": self.lifetime_rolls,
            "pity_4_star": self.pity_4_star,
            "pity_5_star": self.pity_5_star
        }

        with open(path.join(self.user_files_dir, "data.json"), 'w') as json_file:
            json.dump(data, json_file, ensure_ascii=False)
