import json
import random
from enum import Enum

from . import ambr
from .database import Database

soft_pity_5_star = 75
hard_pity_5_star = 90
hard_pity_4_star = 10

pull_rarities = (5, 4, 3)
pull_base_weights = (1, 10, 190)
pull_pity_weights = (1, 8, 53)

class GachaMachine:

    def __init__(self):
        self.data = Database()

        self.rarity_sorted_characters = ambr.sort_by_rarity(self.data.characters)
        print(self.rarity_sorted_characters[4])
        self.rarity_sorted_weapons = ambr.sort_by_rarity(self.data.weapons)
        print(self.rarity_sorted_weapons[3])

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
            pull = random.choice(self.rarity_sorted_characters[5])
            
            self.data.pity_5_star = 0 # Assuming 4 and 5 star pity are treated separately
        elif pull_rarity == 4: # Decide on 4 star character vs weapon, then pull
            if random.randint(0, 1):  
                pull = random.choice(self.rarity_sorted_characters[4])
            else:
                pull = random.choice(self.rarity_sorted_weapons[4])

            self.data.pity_4_star = 0 # Assuming 4 and 5 star pity are treated separately
            self.data.pity_5_star = self.data.pity_5_star + 1
        elif pull_rarity == 3: # Pull for 3 star weapon
            pull = random.choice(self.rarity_sorted_weapons[3])

            self.data.pity_4_star = self.data.pity_4_star + 1
            self.data.pity_5_star = self.data.pity_5_star + 1
        else:
            pass

        self.data.save()
        
        return pull
