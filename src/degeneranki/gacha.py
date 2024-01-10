import json
import random
from enum import Enum

from .database import Database
from ._vendor import requests

soft_pity_5_star = 75
hard_pity_5_star = 90
hard_pity_4_star = 10

pull_rarities = (5, 4, 3)
pull_base_weights = (1, 10, 190)
pull_pity_weights = (1, 8, 53)

class GachaMachine:

    def __init__(self):
        self.genshin_5_star_characters = json.loads(requests.get("https://api.genshin.dev/characters/all?rarity=5").content)
        self.genshin_4_star_characters = json.loads(requests.get("https://api.genshin.dev/characters/all?rarity=4").content)
        self.genshin_4_star_weapons = json.loads(requests.get("https://api.genshin.dev/weapons/all?rarity=4").content)
        self.genshin_3_star_weapons = json.loads(requests.get("https://api.genshin.dev/weapons/all?rarity=3").content)

        self.data = Database()

    def roll(self):
        roll = {}

        # Add 1 roll and remove gacha points
        self.data.lifetime_rolls = self.data.lifetime_rolls + 1

        # Decide on rarity pull
        if self.data.pity_5_star >= hard_pity_5_star - 1:
            pull_rarity = 5
        elif self.data.pity_4_star >= hard_pity_4_star - 1:
            pull_rarity = 4
        elif self.data.pity_5_star >= soft_pity_5_star - 1:
            pull_rarity = random.choices(pull_rarities, pull_pity_weights)[0]
        else:
            pull_rarity = random.choices(pull_rarities, pull_base_weights)[0]

        if pull_rarity == 5: # Pull for 5 star character
            pull = random.choice(self.genshin_5_star_characters)
            search_name = pull['name'].lower().replace(' ', '-')
            pull['image_data'] = requests.get("https://api.genshin.dev/characters/{}/gacha-splash".format(search_name)).content
            
            self.data.pity_5_star = 0 # Assuming 4 and 5 star pity are treated separately
        elif pull_rarity == 4: # Decide on 4 star character vs weapon, then pull
            if random.randint(0, 1):  
                pull = random.choice(self.genshin_4_star_characters)
                search_name = pull['name'].lower().replace(' ', '-')
                pull['image_data'] = requests.get("https://api.genshin.dev/characters/{}/gacha-splash".format(search_name)).content
            else:
                pull = random.choice(self.genshin_4_star_weapons)
                search_name = pull['name'].lower().replace(' ', '-')
                pull['image_data'] = requests.get("https://api.genshin.dev/weapons/{}/icon".format(search_name)).content

            self.data.pity_4_star = 0 # Assuming 4 and 5 star pity are treated separately
            self.data.pity_5_star = self.data.pity_5_star + 1
        elif pull_rarity == 3: # Pull for 3 star weapon
            pull = random.choice(self.genshin_3_star_weapons)
            search_name = pull['name'].lower().replace(' ', '-')
            pull['image_data'] = requests.get("https://api.genshin.dev/weapons/{}/icon".format(search_name)).content

            self.data.pity_4_star = self.data.pity_4_star + 1
            self.data.pity_5_star = self.data.pity_5_star + 1
        else:
            pass

        self.data.save()
        
        return pull
